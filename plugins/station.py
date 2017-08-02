from irc3 import asyncio
from irc3.plugins.command import command

import re
import json
import aiohttp

from datetime import datetime
from dateutil import tz

_RE_FIX = "(,\\s*|\\s*-\\s*){component}|{component}((,\\s*)|\\s*-\\s*)"


def remove_component(targetlocation, component="Erfurt"):
    """
    Fix API locations like "Erfurt, Daberstedt" to just "Daberstedt"
    """
    return re.sub(_RE_FIX.format(component=component), "", targetlocation)


@command(permission="view")
@asyncio.coroutine
def station(bot, mask, target, args):
    """
    Show departures for station: 151213 (Leipziger Platz, Erfurt). The service
    URL is consumed by Erfurt Mobil (Android/iOS).

    A list of all known stations in the VMT area can be viewed here:
    https://evag-live.wla-backend.de/stations/latest.json

    %%station
    """
    url = "https://evag-live.wla-backend.de/node/v1/departures/151213"
    headers = {"Content-Type": "application/json"}
    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.get(url, headers=headers)
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
                "target": remove_component(departure["targetLocation"]),
                "time": datetime.fromtimestamp(departure["timestamp"], tzinfo),
                "delay": delay
            })

        # limit output to 10 max
        data = data[:10]

        # add padding to all departures if any is delayed
        delayed = any(map(lambda d: d["delay"] > 0, data))

        bot.privmsg(target, "Erfurt, Leipziger Platz")
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
                    departure["type"], departure["line"],
                    departure["target"]))

    except KeyError:
        bot.privmsg(target, "Error while retrieving traffic data.")
        raise Exception()
