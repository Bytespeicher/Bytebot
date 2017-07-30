from irc3 import asyncio
from irc3.plugins.command import command

import re
import json
import aiohttp

from datetime import datetime


def remove_component(targetlocation, component="Erfurt"):
    """
    Fix API locations like "Erfurt, Daberstedt" to just "Daberstedt"
    """
    return re.sub("(,\\s*|\\s*-\\s*)" + component + "|" + component + "((,\\s*)|\\s*-\\s*)", "", targetlocation)


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
        data = []
        for departure in body.get("departures", []):
            delay = 0  # in seconds
            try:
                delay = max(0, departure.get("timestamp_rt", 0) - departure["timestamp"]) // 60
            except ValueError:
                pass

            data.append({
                "type": "Tram" if departure["type"] == "Strab" else "Bus",
                "line": departure["line"],
                "target": remove_component(departure["targetLocation"]),
                "time": datetime.utcfromtimestamp(departure["timestamp"]), "delay": delay
            })

        bot.privmsg(target, "Erfurt, Leipziger Platz")
        for departure in data[:10]:
            bot.privmsg(
                target,
                "{:4}{} | {:4} {} -> {}".format(
                    departure["time"].strftime("%H:%M"),
                    " +{:d}".format(departure["delay"]) if departure["delay"] else "",
                    departure["type"], departure["line"],
                    departure["target"]))

    except KeyError:
        bot.privmsg(target, "Error while retrieving traffic data.")
        raise Exception()
