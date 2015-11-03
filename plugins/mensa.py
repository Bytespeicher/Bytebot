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

        data = unicode(data, errors='replace')

        ret = json.loads(data)

        return ret

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find("!mensa") == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_mensa = irc.last_mensa
        except Exception as e:
            last_mensa = 0

        if len(data) == 0:
            irc.msg(channel, "'I'm sorry openmensa has no food data.")
            return

        if last_mensa < (time() - 60):
            try:
                data = self._get_mensa_food()

                irc.msg(channel, 'Mensa Menu FH Erfurt:')

                for x in range(len(data)):

                    name = data[x][u'name'].encode('ascii', 'ignore')
                    price_student = data[x][u'prices']['students']
                    # price_extern = data[x][u'prices']['pupils'].encode('ascii', 'ignore')

                    print_str = '{:70}: '.format(name) + \
                        '{:3.2f}€ / student'.format(price_student)  # + \
                    #'{:3.0f} / extern'.format(price_extern)
                    # irc.msg(channel, print_str)

                    print print_str

                    irc.msg(channel, print_str)

                irc.last_mensa = time()

            except Exception as e:
                print(e)
                irc.msg(channel, 'Error while fetching data.')
        else:
            irc.msg(channel, "Don't overdo it ;)")
