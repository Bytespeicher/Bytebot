from irc3 import asyncio
from irc3.plugins.command import command

import io
import re
import json
import aiohttp

from datetime import datetime
from dateutil import tz

from difflib import get_close_matches

URL = "https://evag-live.wla-backend.de/node/v1/departures/{extId}"
RE_FIX = "(,\\s*|\\s*-\\s*){component}|{component}((,\\s*)|\\s*-\\s*)"


def lookup_by_id(extId):
    """
    Lookup station by extId and return the pretty concatenation of name, parent
    """
    with io.open("data/stations.latest.json") as fp:
        for obj in json.load(fp):
            if obj["id"] == extId:
                return "{parent}, {name}".format(**obj)


def lookup_by_name(name, parent):
    """
    Lookup station by (parent, name) and return its extId.
    """
    with io.open("data/stations.latest.json") as fp:
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
    config = bot.config.get(__name__, {})

    city = config.get("city")
    if not city:
        city = "Erfurt"

    # determine extId (VMT internal id) and friendly name
    extid = " ".join(args["<name>"])
    if not extid:
        extid = str(config.get("id", 151213))

    if extid == "help":
        return "Use !station NAME/EXTID to get recent departures"

    name = None
    if extid.isdigit():
        name = lookup_by_id(extid)
    else:
        extid = lookup_by_name(extid, city)
        if extid is not None:
            name = lookup_by_id(extid)

    if extid is None:
        return "Unknown station: " + " ".join(args["<name>"])

    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.get(URL.format(extId=extid))
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

        data = []
        for departure in body.get("departures", []):
            delay = 0  # in seconds
            try:
                timestamp = departure.get("timestamp")
                timestamp_rt = departure.get("timestamp_rt", 0)
                delay = max(0, timestamp_rt - timestamp) // 60
            except ValueError:
                pass

            data.append({
                "type": "Tram" if departure["type"] == "Strab" else "Bus",
                "line": departure["line"],
                "target": remove_component(departure["targetLocation"], city),
                "time": datetime.fromtimestamp(departure["timestamp"], tzinfo),
                "delay": delay
            })

        # limit output to 10 max
        data = data[:10]

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
