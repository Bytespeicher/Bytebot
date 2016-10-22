#!/usr/bin/env python3
#!python3
# -*- coding: utf-8 -*-

from irc3.plugins.command import command

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
import json
import aiohttp
import datetime
import time

@command(permission="view")
@asyncio.coroutine
def station(bot, mask, target, args):
    """Show current tram and bus station information

        %%station
    """
    url = "https://wla.31384.de:4044/evag/functions/departures"
    payload = {"extId": "151213","useTimestamp": True}
    headers = {"Content-Type": "application/json"}
    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.post(url, data=json.dumps(payload),
                   headers=headers)
            if resp.status != 200:
                bot.privmsg(target, "Error while retrieving traffic data.")
                raise Exception()
            r = yield from resp.read()

    try:
        j = json.loads(r.decode('utf-8'))
        departures = j["result"]["departures"]

        data = []
        count = 0;

        for i in range(len(departures)):
            if(j["result"]["departures"][i]["timestamp"] >= time.time()):
                data.append(
                    {'departure': j["result"]["departures"][i]["timestamp"],
                     'type': j["result"]["departures"][i]["type"],
                     'targetLocation': j["result"]["departures"][i]
                            ["targetLocation"],
                     'line': j["result"]["departures"][i]["line"]})
            if(count>10):
                break
            else:
                count = count + 1

        bot.privmsg(target, "Erfurt, Leipziger Pl.");
        for i in range(len(data)):
            bot.privmsg(target,
                        "%s: %4.4s %s -> %s" % (datetime.datetime.fromtimestamp(
                                    data[i]['departure']).strftime('%H:%M'),
                                            data[i]['type'].upper(),
                                            data[i]['line'],
                                            data[i]['targetLocation'],
                                         ))
                                         
    except KeyError:
        bot.privmsg(target, "Error while retrieving traffic data.")
        raise Exception()
