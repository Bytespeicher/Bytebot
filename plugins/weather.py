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

        if last_weather < (time() - 300):
            config = BYTEBOT_PLUGIN_CONFIG['weather']
            url = config['url'] + config['location'] + \
                '&appid=%s' % config['api_key']
            r = requests.get(url)

            if r.status_code != 200:
                irc.msg('Error while retrieving weather data')
                return

            temp = r.json()["main"]["temp"]

            irc.msg(channel, "We have now %2.2f °C in Erfurt" % temp)
            irc.last_weather = time()
        else:
            irc.msg(channel, "Don't overdo it ;)")
