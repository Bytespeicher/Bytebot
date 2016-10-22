from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from dateutil import parser
from irc3 import asyncio
from irc3.plugins.command import command
from irc3.plugins.cron import cron

import aiohttp
import datetime
import feedparser
import os
import pytz
import time


@command(permission="view")
@asyncio.coroutine
def rss(bot, mask, target, args):
    """Show last entries for a rss source

        %%rss [<feed>]
    """

    config = BYTEBOT_PLUGIN_CONFIG['rss']

    if args['<feed>'] is None:
        """No argument was given."""
        bot.privmsg(
            target,
            'Use !rss with one of the following parameters'
        )

        """Output name ordered list of feeds."""
        for feed in sorted(config, key=lambda entry: entry['name']):
            bot.privmsg(
                target,
                "  %s (%s)" % (feed['name'].lower(), feed['url'])
            )

    else:
        """Argument <feed> was set, check if it is a valid one."""
        feeds = filter(lambda entry: entry['name'].lower() == args['<feed>'],
                       config)
        if feeds:
            for feed in feeds:
                bot.log.info('Fetching rss feed for %s' % feed['name'].lower())
                yield from _rss_process_feed(bot, target, feed, 5)
        else:
            bot.privmsg(
                target,
                'Invalid feed name. Use !rss to get a list of valid feeds'
            )


@asyncio.coroutine
def _rss_process_feed(bot, target, config, number_of_entries=-1):
    """Process a rss feed an post numberOfEntries

        feed:            Dictionary with feed informations
        numberOfEntries: Number of entries to post. -1 means to post
                         only new entries based on cached informations
    """

    if number_of_entries == -1 and os.path.isfile(config['cache']):
        """Try to read read cache information about last run"""
        cache = open(config['cache'], "r")
        line = cache.readline()
        cached_etag = ""
        last_entry_timestamp = 0
        if len(line) > 3:
            (cached_etag, last_entry_timestamp) = line.split(" ", 1)
        get_params = {'etag': cached_etag}
    else:
        get_params = {}

    """Request the rss feed content."""
    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.get(config['url'], params=get_params)
            if resp.status == 200:
                """Get text content and etag from http request."""
                r = yield from resp.text()
                r_etag = resp.headers.get('etag')
            elif resp.status == 304:
                """Etag was used in request and noting changed."""
                return
            else:
                bot.privmsg(target, "Error while retrieving rss data")
                raise Exception()

    try:
        """Parse feed."""
        feed = feedparser.parse(r)
        if feed.bozo:
            raise Exception(str(feed.bozo_exception))

        """Remove unneeded entries in feed."""
        if number_of_entries != -1:
            feed.entries = feed.entries[0:number_of_entries]

        """Use local timezone as source for calculations."""
        timezoneEF = pytz.timezone('Europe/Berlin')

        if not os.path.isfile(config['cache']):
            """
            Save new file if none exists and don't post anything. Prevents
            spamming of already posted entries if the cache file was removed.

            See https://github.com/Bytespeicher/Bytebot/issues/46
            """

            dt_now = datetime.datetime.utcnow()
            dt_now = dt_now.replace(tzinfo=pytz.utc)
            dt_now.astimezone(timezoneEF)
            dt_now = time.mktime(dt_now.timetuple())

            _save_cache(filename=config['cache'],
                        etag=r_etag,
                        last_entry=dt_now)
            return

        """Traverses feed entries in reversed order (post oldest first)"""
        for entry in reversed(feed.entries):

            """Parse date of entry dependent on the feedtype and
            convert to timestamp."""
            if config['type'] == 'dokuwiki':
                dt = parser.parse(entry.date)
            elif config['type'] == 'wordpress':
                dt = parser.parse(entry.published)
            elif config['type'] in ('github', 'redmine'):
                dt = parser.parse(entry.updated)

            dt.astimezone(timezoneEF)
            dt_timestamp = dt.strftime('%s')

            """Skip old entries if we would only new entries."""
            if number_of_entries == -1 and \
               last_entry_timestamp >= dt_timestamp:
                continue

            """Create irc message dependent on the feedtype."""
            if config['type'] == 'dokuwiki':
                message = "%s changed %s" % (entry.author,
                                             entry.title.split(" - ", 1)[0])
                message2 = "(%s)" % entry.link.split("?", 1)[0]
                if len(entry.title.split(" - ", 1)) == 2:
                    message += " - comment: %s" % entry.title.split(" - ")[1]
            elif config['type'] == 'wordpress':
                message = "%s added \"%s\"" % (entry.author,
                                               entry.title_detail.value)
                message2 = "(%s)" % entry.link
            elif config['type'] == 'github':
                message = "%s pushed a new commit:" % entry.author
                message2 = entry.title
            elif config['type'] == 'redmine':
                message = "%s: %s" % (entry.author_detail.name, entry.title)
                message2 = entry.link

            """Post messages with named prefix."""
            message = "%s | %s" % (config['name'].upper(), message)
            message2 = "%s   %s" % (" " * len(config['name']), message2)
            bot.privmsg(target, message)
            bot.privmsg(target, message2)

            """Save etag and last entry informations to cache file"""
            if number_of_entries == -1:
                _save_cache(filename=config['cache'],
                            etag=r_etag,
                            last_entry=dt_timestamp)

    except KeyError:
        bot.privmsg(target, "Error while retrieving rss data")
        raise Exception()


def _save_cache(filename='', etag='', last_entry=''):
    """
    Save the cache tags to a file

    Keyword arguments:
    etag -- The etag header checksum
    last_entry -- The timestamp when the latest entry was submitted
    """
    cache = open(filename, "w")
    cache.truncate(0)
    cache.write('%s %s' % (etag, last_entry))
    cache.close()


@cron('*/5 * * * *')
@asyncio.coroutine
def rss_cron(bot):
    """
    Checks RSS feed every 5 minutes and post recent changes
    """

    config = BYTEBOT_PLUGIN_CONFIG['rss']
    for feed in sorted(config, key=lambda entry: entry['name']):
        yield from _rss_process_feed(bot, bot.config.autojoins[0], feed)
