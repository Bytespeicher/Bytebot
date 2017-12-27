from irc3 import asyncio
from irc3.plugins.command import command
from irc3.plugins.cron import cron

import io
import re
import json
import aiohttp
import os
import pytz
import datetime

from dateutil import tz

from difflib import get_close_matches

RE_FIX = "(,\\s*|\\s*-\\s*){component}|{component}((,\\s*)|\\s*-\\s*)"


def station_configuration(bot):
    """Load configuration"""
    config = {
        'cache': '/tmp/station.cache',
        'city': 'Erfurt',
        'id': '151213',
        'announce_minutes': 30
    }
    config.update(bot.config.get(__name__, {}))
    return config


def lookup_by_id(bot, extId):
    """
    Lookup station by extId and return the pretty concatenation of name, parent
    """

    # load configuration
    config = station_configuration(bot)

    with io.open(config['cache']) as fp:
        for obj in json.load(fp):
            if obj["id"] == extId:
                return "{parent}, {name}".format(**obj)


def lookup_by_name(bot, name, parent):
    """
    Lookup station by (parent, name) and return its extId.
    """

    # load configuration
    config = station_configuration(bot)

    with io.open(config['cache']) as fp:
        data = json.load(fp)
        candidates = [obj["name"] for obj in data if obj["parent"] == parent]

        match = get_close_matches(name, candidates, 1, 0.3)
        if not match:
            return None

        for obj in data:
            if obj["parent"] == parent and obj["name"] == match[0]:
                return str(obj["id"])


def remove_component(targetlocation, component):
    """
    Fix API locations like "Erfurt, Daberstedt" to just "Daberstedt"
    """
    return re.sub(RE_FIX.format(component=component), "", targetlocation)


@command(permission="view")
@asyncio.coroutine
def station(bot, mask, target, args):
    """
    Show departures for station: 151213 (Leipziger Platz, Erfurt). The service
    URL is consumed by Erfurt Mobil (Android/iOS).

    A list of all known stations in the VMT area can be viewed here:
    https://evag-live.wla-backend.de/stations/latest.json

    %%station
    %%station <name>...
    """

    # load configuration
    config = station_configuration(bot)
    if " ".join(args['<name>']) == "help":
        return \
            "Use !station [minutes] NAME/EXTID to get recent departures " + \
            "for the next minutes (default: %s)" % config['announce_minutes']

    if not os.path.isfile(config['cache']):
        yield from _update_cache(bot)
        return "Station cache is unavailable. " + \
               "Please try again in a few minutes!"

    if 'city' not in config:
        bot.privmsg(target, "No city configured.")
        return

    # determine extId (VMT internal id) and friendly name
    announce_limit_arg = None
    if len(args['<name>']) >= 2 and args['<name>'][0].isdigit():
        announce_limit_arg = int(args['<name>'][0])
        del args['<name>'][0]

    extid = " ".join(args["<name>"])
    if not extid:
        extid = str(config['id'])

    name = None
    if extid.isdigit():
        name = lookup_by_id(bot, extid)
    else:
        extid = lookup_by_name(bot, extid, config['city'])
        if extid is not None:
            name = lookup_by_id(bot, extid)

    if extid is None:
        return "Unknown station: " + " ".join(args["<name>"])

    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.get(
                       config['url_departures'].format(extId=extid)
                   )
            if resp.status != 200:
                bot.privmsg(target, "Error while retrieving traffic data.")
                raise Exception()
            body = yield from resp.read()

    try:
        body = json.loads(body.decode('utf-8'))
    except json.JSONDecodeError:
        bot.privmsg(target, "Error while retrieving traffic data.")

    try:
        # use local timezone
        tzinfo = tz.tzlocal()

        announce_limit = datetime.datetime.now(tzinfo)
        if announce_limit_arg is not None:
            announce_limit += datetime.timedelta(minutes=announce_limit_arg)
        else:
            announce_limit += datetime.timedelta(
                                  minutes=config['announce_minutes'])

        data = []
        for departure in body.get("departures", []):
            delay = 0  # in seconds
            try:
                timestamp = datetime.datetime.fromtimestamp(
                                departure.get("timestamp"), tzinfo)
                timestamp_rt = datetime.datetime.fromtimestamp(
                                   departure.get("timestamp_rt", 0), tzinfo)
                delay = max(0, (timestamp_rt - timestamp).seconds) // 6
            except ValueError:
                pass

            # limit output to announce_minutes
            if timestamp > announce_limit:
                break

            data.append({
                "type": "Tram" if departure["type"] == "Strab" else "Bus",
                "line": departure["line"],
                "target": remove_component(
                    departure["targetLocation"],
                    config['city']
                ),
                "time": timestamp,
                "delay": delay
            })

        # add padding to all departures if any is delayed
        delayed = any(map(lambda d: d["delay"] > 0, data))

        # get max line number
        maxline = max(map(lambda d: len(d["line"]), data))

        bot.privmsg(target, name)
        for departure in data:
            delay = ""
            if departure["delay"]:
                delay = " +{:d}".format(departure["delay"])
            elif delayed:
                delay = "   "

            bot.privmsg(
                target,
                "{:4}{} | {:4} {} -> {}".format(
                    departure["time"].strftime("%H:%M"),
                    delay,
                    departure["type"],
                    departure["line"].rjust(maxline),
                    departure["target"]))

    except KeyError:
        bot.privmsg(target, "Error while retrieving traffic data.")
        raise Exception()


@cron('23 0 * * *')
@asyncio.coroutine
def cccongress_update_cron(bot):
    """Update station list once a day"""

    yield from _update_cache(bot, 1)


@asyncio.coroutine
def _update_cache(bot, cron=0):
    """Update cached station list

        cron: defines whether update was triggered by cron or not
    """

    config = station_configuration(bot)
    config['cache_etag'] = config['cache'] + '.etag'

    if os.path.isfile(config['cache']):
        """Try to read read cache information about last run"""
        cache = open(config['cache_etag'], "r")
        headers = {'If-None-Match': cache.readline().strip().rstrip('\n')}
    else:
        headers = {}

    try:
        """Request the station list"""
        with aiohttp.Timeout(30):
            with aiohttp.ClientSession(loop=bot.loop) as session:
                resp = yield from session.get(
                           config['url_stationlist'],
                           headers=headers
                       )
                if resp.status == 200:
                    """Get text content and etag from http request."""
                    r = yield from resp.text()
                    r_etag = resp.headers.get('etag')
                elif resp.status == 304:
                    """Etag was used in request and noting changed."""
                    return
                else:
                    raise Exception()

    except Exception as e:
        bot.log.error(e)
        if cron == 0:
            bot.privmsg(bot.config.autojoins[0],
                        "Error while retrieving station list")

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

    except OSError as e:
        bot.log.error(e)
