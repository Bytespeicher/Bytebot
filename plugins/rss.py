#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import feedparser
import os
import datetime
import pytz

from twisted.python import log
from dateutil       import parser
from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG, BYTEBOT_CHANNEL
from bytebot_log    import LOG_WARN

class rss(Plugin):
    def __init__(self):
        pass

    def registerCommand(self, irc):
        """Registers the '!rss' command to the global command list

        irc:        An instance of the bytebot. Will be passed by the plugin loader
        """

        irc.registerCommand('!rss', 'Show the last recent changes')

    def fiveMinuteCron(self, irc):
        """Checks RSS feed every 5 minutes and post recent changes

        irc:        An instance of the bytebot. Will be passed by the plugin loader
        """
        try:

            self.irc = irc
            self.channel = BYTEBOT_CHANNEL
            for feed in BYTEBOT_PLUGIN_CONFIG['rss']:
                # process new feed entries
                self.process_feed(feed)

        except Exception as e:
            print(e)
            print("Error while processing rss feed")


    def onPrivmsg(self, irc, msg, channel, user):
        """Looks for a '!rss' command in messages posted to the channel and
        returns a list of recent changes.

        irc:        An instance of the bytebot. Will be passed by the plugin loader
        msg:        The msg sent to the channel
        channel:    The channels name
        user:       The user who sent the message
        """

        if msg.find('!rss') == -1:
            return

        # Found rss command without source, show details
        if msg.find(' ') == -1:
            irc.msg(channel, "Use !rss with one of the following second parameter to specify source:")
            for feed in BYTEBOT_PLUGIN_CONFIG['rss']:
                irc.msg(channel, "  %s (%s)" % (feed['name'].lower(), feed['url']))
            return

        self.irc = irc
        self.channel = channel

        # Found source, show last feed entries
        for feed in BYTEBOT_PLUGIN_CONFIG['rss']:
            if msg.split(' ', 1)[1] == feed['name'].lower():
                self.process_feed(feed, 5)

    def process_feed(self, feed, numberOfEntries=-1):
        """Process a rss feed an post numberOfEntries

        feed:            Dictionary with feed informations
        numberOfEntries: Number of entries to post. -1 means to post only new entries based on cached informations
        """

        if numberOfEntries == -1 and os.path.isfile(feed['cache']):
            # try to read read cache information about last run
            cache = open(feed['cache'], "r")
            line = cache.readline()
            cached_etag = ""
            last_entry_timestamp = 0
            if len(line) > 3:
                (cached_etag, last_entry_timestamp) = line.split(" ", 1)

            request = feedparser.parse(feed['url'], etag=cached_etag)
        else:
            request = feedparser.parse(feed['url'])

        # Nothing changed
        if request.status == 304:
            return

        # Feed not successfull retrieved, so stop with error
        if request.status != 200:
            log.msg("Unknown HTTP status retrieved for feed %s: %d" % (feed['name'], request.status), level=LOG_WARN)

        # local timezone
        timezoneEF = pytz.timezone('Europe/Berlin')

        # remove unneeded entries in feed
        if numberOfEntries != -1:
            request.entries = request.entries[0:numberOfEntries]

        if not os.path.isfile(feed['cache']):
            """
            Save new file if none exists and don't post anything. Prevents
            spamming of already posted entries if the cache file was removed.

            See https://github.com/Bytespeicher/Bytebot/issues/46
            """
            request = feedparser.parse(feed['url'])

            dt_now = datetime.datetime.utcnow()
            dt_now = dt_now.replace(tzinfo=pytz.utc)
            dt_now.astimezone(timezoneEF)
            dt_now = time.mktime(dt_now.timetuple())

            self.save_cache(filename=feed['cache'],
                            etag=request.etag,
                            last_entry=dt_now)
            return

        # traverse feed entries in reversed order (post oldest first)
        for entry in reversed(request.entries):

            # parse date of entry dependent on the feedtype and convert to timestamp
            if feed['type'] == 'dokuwiki':
                dt = parser.parse(entry.date)
            elif feed['type'] == 'wordpress':
                dt = parser.parse(entry.published)
            elif feed['type'] in ('github', 'redmine'):
                dt = parser.parse(entry.updated)

            dt.astimezone(timezoneEF)
            dt_timestamp = dt.strftime('%s')

            # skip old entries if we would only new entries
            if numberOfEntries == -1 and last_entry_timestamp >= dt_timestamp:
                continue

            # create irc message dependent on the feedtype
            if feed['type'] == 'dokuwiki':
                message = "%s changed %s" % (entry.author, entry.title.split(" - ", 1)[0])
                message2 = "(%s)" % entry.link.split("?", 1)[0]
                if len(entry.title.split(" - ", 1)) == 2:
                     message += " - comment: %s" % entry.title.split(" - ")[1]
            elif feed['type'] == 'wordpress':
                message = "%s added \"%s\"" % (entry.author, entry.title_detail.value)
                message2 = "(%s)" % entry.link
            elif feed['type'] == 'github':
                message = "%s pushed a new commit:" % entry.author
                message2 = entry.title
            elif feed['type'] == 'redmine':
                message = "%s: %s" % (entry.author_detail.name, entry.title)
                message2 = entry.link

            # post messages with named prefix
            message = "%s | %s" % (feed['name'].upper(), message)
            message2 = "%s   %s" % (" " * len(feed['name']), message2)
            self.irc.say(self.channel, unicode(message).encode('utf-8', errors='replace'))
            self.irc.say(self.channel, unicode(message2).encode('utf-8', errors='replace'))

            if numberOfEntries == -1:
                self.save_cache(filename=feed['cache'],
                                etag=request.etag,
                                last_entry=dt_timestamp)

    def save_cache(self, filename='', etag='', last_entry=''):
        """Save the cache tags to a file

        Keyword arguments:
        etag -- The etag header checksum
        last_entry -- The timestamp when the latest entry was submitted
        """
        cache = open(filename, "w")
        cache.truncate(0)
        cache.write('%s %s' % (etag, last_entry))
        cache.close()
