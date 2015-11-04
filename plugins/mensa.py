#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
import json
from time import time, strftime

from plugins.plugin import Plugin

from bytebot_config import BYTEBOT_HTTP_TIMEOUT, BYTEBOT_HTTP_MAXSIZE
from bytebot_config import BYTEBOT_PLUGIN_CONFIG


class mensa(Plugin):

    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand("!mensa", "Mensa menu for today")

    def _get_mensa_food(self):
        url = "http://openmensa.org/api/v2/canteens/" + \
            str(BYTEBOT_PLUGIN_CONFIG["mensa"]["canteen"]) + "/days/" + \
            strftime("%Y-%m-%d") + "/meals"

        data = urllib2.urlopen(url, timeout=BYTEBOT_HTTP_TIMEOUT).read(
            BYTEBOT_HTTP_MAXSIZE)

        return json.loads(data)

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find("!mensa") == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_mensa = irc.last_mensa
        except Exception as e:
            last_mensa = 0

        if last_mensa < (time() - 60):
            try:
                data = self._get_mensa_food()
            except Exception:
                irc.msg(channel, "Error while fetching data.")

            if len(data) == 0:
                irc.msg(channel, "'I'm sorry openmensa has no food data.")
                return

            messages = []
            for x in range(len(data)):
                name = data[x][u"name"]
                price_student = data[x][u"prices"]["students"]

                print_str = u"{:70}: ".format(name) + \
                    u"{:3.2f}€ / student".format(price_student)

                messages.append(print_str)

            irc.msg(channel, "Mensa Menu FH Erfurt:")
            for m in messages:
                irc.msg(channel, "  " + m.encode("utf-8", "ignore"))

            irc.last_mensa = time()
        else:
            irc.msg(channel, "Don't overdo it ;)")
