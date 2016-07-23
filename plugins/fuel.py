#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
import json
from time import time

from plugins.plugin import Plugin

from bytebot_config import BYTEBOT_HTTP_TIMEOUT, BYTEBOT_HTTP_MAXSIZE
from bytebot_config import BYTEBOT_PLUGIN_CONFIG


class fuel(Plugin):

    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand("!fuel", "Treibstoffpreise")

    def _get_fuel_stations(self):
        url = "https://creativecommons.tankerkoenig.de/json/list.php?" + \
            "lat=50.9827792" + \
            "&lng=11.0394426" + \
            "&rad=15" + \
            "&sort=dist" + \
            "&type=e5&apikey=" + \
            str(BYTEBOT_PLUGIN_CONFIG["fuel"]["apikey"])

        data = urllib2.urlopen(url, timeout=BYTEBOT_HTTP_TIMEOUT).read(
            BYTEBOT_HTTP_MAXSIZE)

        return json.loads(data)

    def _get_fuel_stations_details(self, station_id):
        url = "https://creativecommons.tankerkoenig.de/json/detail.php?" + \
            "id=" + station_id + \
            "&apikey=" + str(BYTEBOT_PLUGIN_CONFIG["fuel"]["apikey"])

        data = urllib2.urlopen(url, timeout=BYTEBOT_HTTP_TIMEOUT).read(
            BYTEBOT_HTTP_MAXSIZE)

        return json.loads(data)

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find("!fuel") == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_fuel = irc.last_fuel
        except Exception:
            last_fuel = 0

        if last_fuel < (time() - 60):
            try:
                data = self._get_fuel_stations()
            except Exception:
                irc.msg(channel, "Error while fetching data.")

            if len(data) == 0:
                irc.msg(channel, "'I'm sorry, no fuel data.")
                return

            messages = []
            for x in range(len(data['stations'])):
                brand = data[u'stations'][x][u"brand"]
                station_id = data['stations'][x][u"id"]
                postCode = data['stations'][x][u"postCode"]

                data_details = self._get_fuel_stations_details(station_id)

                e5 = data_details['station']['e5']
                e10 = data_details['station']['e10']
                diesel = data_details['station']['diesel']

                if brand == '':
                    brand = 'GLOBUS'

                print_str = \
                    u"   {:20}".format(brand + ', ' + str(postCode) + ': ') + \
                    u"{:5}  ".format(e5) + \
                    u"{:5}  ".format(e10) + \
                    u"{:5}  ".format(diesel)

                messages.append(print_str)

            headline = u"{:23}".format('fuel prices:') + \
                u"{:6} ".format('e5') + \
                u"{:6} ".format('e10') + \
                u"{:6} ".format('diesel')

            irc.msg(channel, headline.encode("utf-8", "ignore"))
            for m in messages:
                irc.msg(channel, m.encode("utf-8", "ignore"))

            irc.last_fuel = time()
        else:
            irc.msg(channel, "Don't overdo it ;)")
