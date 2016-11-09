from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
from irc3.plugins.command import command
from irc3.plugins.cron import cron

import aiohttp
import datetime
import dateutil.parser
import pytz
import os
import json


@command(permission="view")
@asyncio.coroutine
def cccongress(bot, mask, target, args):
    """Show informations about Chaos Communication Congress

        %%cccongress [<command>]
    """

    config = BYTEBOT_PLUGIN_CONFIG['cccongress']

    if not os.path.isfile(config['cache']):
        yield from _update_cache(bot)
        return "Schedule cache is unavailable. " + \
               "Please try again in a few minutes!"

    if args['<command>'] is None:
        yield from _output_talks(0, bot, target)
    elif args['<command>'] == 'halls':
        bot.privmsg(target, "Available halls: %s" % ', '.join(_get_halls()))
    elif args['<command>'] == 'next':
        yield from _output_talks(1, bot, target)
    elif args['<command>'] == 'schedule':
        yield from _scheduleinformations(bot, target)
    elif args['<command>'] == "help":
        yield from _output_help(bot, target)


@cron('1 * 1-26,31 12 *')
@cron('*/15 * 27-30 12 *')
@asyncio.coroutine
def cccongress_update_cron(bot):
    """Update schedule in December"""

    yield from _update_cache(bot)


# @cron('* * 27-30 12 *')
@cron('* * * * *')
@asyncio.coroutine
def cccongress_announce_next_talks(bot):
    """Announce next talks"""

    config = BYTEBOT_PLUGIN_CONFIG['cccongress']

    announcelist = []
    for hall in _get_halls():
        """Get next event for hall"""
        event = _get_talk(hall, 1)
        if event is not None:
            """Check if event starts in a few minutes"""
            event_start = dateutil.parser.parse(event['date'])
            designated_start = \
                datetime.datetime.now(pytz.timezone('Europe/Berlin')) + \
                datetime.timedelta(minutes=config['announce_minutes'])
            if event_start == designated_start:
                """Save hall informations in event and add to announcelist"""
                event['hall'] = hall
                announcelist.append(event)

    """Announce found events"""
    if len(announcelist) > 0:
        bot.privmsg(
            bot.config.autojoins[0],
            "The following talks will start in %d minutes" %
            config['announce_minutes']
        )
        for event in announcelist:
            yield from _output_single_talk(event['hall'],
                                           event,
                                           bot,
                                           bot.config.autojoins[0])


@asyncio.coroutine
def _output_talks(slot, bot, target):
    """Output talks

        slot: Output talks running now (slot = 0) or next (slot = 1)
    """

    eventcounter = 0
    for hall in _get_halls():
        event = _get_talk(hall, slot)
        if event is not None:
            eventcounter += 1
            yield from _output_single_talk(hall, event, bot, target)

    if eventcounter == 0:
        bot.privmsg(target, "No talks found.")


@asyncio.coroutine
def _output_single_talk(hall, event, bot, target):
    """Output single talk

        hall: Name of hall
        event: Event informations
    """

    bot.privmsg(target,
                "[%s] %s %s" % (hall, event['start'], event['title']))
    bot.privmsg(
        target,
        "%s (%s / %s)" %
        ('{:<14}'.format(''), event['language'], _get_persons(event))
    )


@asyncio.coroutine
def _scheduleinformations(bot, target):
    """Output informations about schedule"""

    config = BYTEBOT_PLUGIN_CONFIG['cccongress']
    json_data = _get_json_data()

    bot.privmsg(
        target,
        "%s (%s)" %
        (json_data['schedule']['conference']['title'],
         json_data['schedule']['conference']['acronym'])
    )

    file_mtime = os.path.getmtime(config['cache'])
    file_dtime = datetime.datetime.fromtimestamp(file_mtime)
    bot.privmsg(
        target,
        "Schedule was last updated on %s" %
        file_dtime.strftime('%Y-%m-%d %H:%M:%S')
    )

    bot.privmsg(
        target,
        "Current schedule version is %s" %
        json_data['schedule']['version']
    )


@asyncio.coroutine
def _output_help(bot, target):
    """Output help"""

    bot.privmsg(target, "The following commands are available:")
    bot.privmsg(target, "!cccongress          - Show current talks")
    bot.privmsg(target, "!cccongress halls    - Show available halls")
    bot.privmsg(target, "!cccongress next     - Show next talks")
    bot.privmsg(target, "!cccongress schedule - Show schedule informations")


def _get_json_data():
    """Get json from cached file"""

    with open(BYTEBOT_PLUGIN_CONFIG['cccongress']['cache']) as json_file:
        return json.load(json_file)


def _get_talk(hall, slot=0, bot=None):
    """Get talks for a hall

        hall: Name of hall
        slot: Get talks running now (slot = 0) or next (slot = 1)
    """

    json_data = _get_json_data()
    now = datetime.datetime.now(pytz.timezone('Europe/Berlin'))

    for day in json_data['schedule']['conference']['days']:

        day_start = dateutil.parser.parse(day['day_start'])
        day_end = dateutil.parser.parse(day['day_end'])

        """Ignore days in the past"""
        if day_end < now:
            continue

        for event in day['rooms'][hall]:

            """Get start, duration and calculate end"""
            event_start = dateutil.parser.parse(event['date'])
            event_duration = datetime.timedelta(
                hours=int(event['duration'][:2]),
                minutes=int(event['duration'][3:])
            )
            event_end = event_start + event_duration

            """Find current talk"""
            if slot == 0 and event_start <= now and event_end >= now:
                return event

            """Find next talk"""
            if slot == 1 and event_start >= now:
                return event

    return None


def _get_halls():

    json_data = _get_json_data()

    halls = []
    for day in json_data['schedule']['conference']['days']:
        halls += day['rooms'].keys()

    return sorted(set(halls))


def _get_persons(event):
    """Get string of persons from event"""
    persons = []
    for person in event['persons']:
        persons.append(person['public_name'])

    return ', '.join(persons)


@asyncio.coroutine
def _update_cache(bot):
    """ Update cached schedule """

    config = BYTEBOT_PLUGIN_CONFIG['cccongress']
    config['cache_etag'] = config['cache'] + '.etag'
    config['url'] = config['url'].replace('YEAR',
                                          str(datetime.datetime.now().year))

    if os.path.isfile(config['cache']):
        """Try to read read cache information about last run"""
        cache = open(config['cache_etag'], "r")
        headers = {'If-None-Match': cache.readline().strip().rstrip('\n')}
    else:
        headers = {}

    """Request the schedule content."""
    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.get(config['url'], headers=headers)
            if resp.status == 200:
                """Get text content and etag from http request."""
                r = yield from resp.text()
                r_etag = resp.headers.get('etag')
            elif resp.status == 304:
                """Etag was used in request and noting changed."""
                return
            else:
                bot.privmsg(target, "Error while retrieving schedule data")
                raise Exception()

    try:
        """ Save schedule cache to disk """
        cache = open(config['cache'], "w")
        cache.truncate(0)
        cache.write('%s' % r)
        cache.close()

        """ Save etag cache to disk """
        cache = open(config['cache_etag'], "w")
        cache.truncate(0)
        cache.write('%s' % r_etag)
        cache.close()

    except KeyError:
        bot.privmsg(target, "Error while retrieving schedule data")
        raise Exception()
