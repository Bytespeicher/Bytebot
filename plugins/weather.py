#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from time import time

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG
import requests


class weather(Plugin):
    """
    The weather function read the current temperature of the city Erfurt.
    It is necessary to register to get an API key from openweathermap
    http://openweathermap.org/api
    """
    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand('!weather', 'weather in Erfurt')

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find('!weather') == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_weather = irc.last_weather
        except Exception:
            last_weather = 0

        if last_weather < (time() - 5):
            config = BYTEBOT_PLUGIN_CONFIG['weather']

            if msg.find(' ') == -1:
                location = config['location']
            else:
                location = "".join(msg.split(' ')[1:])

            url = config['url'] + location + '&appid=%s' % config['api_key']
            r = requests.get(url)

            if r.status_code != 200:
                irc.msg(channel, 'Error while retrieving weather data')
                return

            try:
                j = r.json()
                temp = j["main"]["temp"]
                location = "%s,%s" % (j["name"].encode('utf-8'),
                                      j["sys"]["country"].encode('utf-8'))
            except KeyError:
                irc.msg(channel, "Error while retrieving weather data")
                return

            irc.msg(channel, "We have now %2.2f °C in %s" % (temp, location))
            irc.last_weather = time()
        else:
            irc.msg(channel, "Don't overdo it ;)")
