#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from plugins.plugin import Plugin
from time import time

from bytebot_config import BYTEBOT_HTTP_TIMEOUT

class station(Plugin):

    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand('!station', 'Haltestelle')

    def _get_public_traffic(self, station, number_of_results):
        url = "http://vmt.hafas.de/bin/stboard.exe/dn?"

        today = datetime.now()
        tomorrow = datetime.now() + timedelta(hours=24)

        today_formated = '{:%d.%m.%y}'.format(today)
        tomorrow_formated = '{:%d.%m.%y}'.format(tomorrow)
        hour = '{:%H}'.format(today)
        minute = '{:%M}'.format(today)

        data = 'input=' + station + \
            '&selectDate=today&dateBegin=' + str(today_formated) + \
            '&dateEnd=' + str(tomorrow_formated) + \
            '&time=' + str(hour) + '%3A' + str(minute) + \
            '&timeselect=W%E4hlen' +\
            '&boardType=dep' +\
            '&REQProduct_list=1%3A1111111111111111' +\
            '&maxJourneys=' + str(number_of_results) + \
            '&start=Anzeigen'

        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req, timeout=BYTEBOT_HTTP_TIMEOUT)

        soup = BeautifulSoup(response.read(), 'html.parser')

        station_name = soup.find_all('span', {"class": "output"})
        time = soup.find_all('td', {"class": "time"})
        product = soup.find_all('td', {"class": "product"})
        timetable = soup.find_all('td', {"class": "timetable"})

        name = station_name[0].text.encode('utf-8').strip()
        ret = []

        for i in range(number_of_results):
            ret_time = time[i].text.encode('utf-8').strip()
            ret_product = product[i].text.encode('utf-8').strip()
            ret_product = ret_product.replace("    ", " ")
            ret_timetable = timetable[i].find('a').text.encode('utf-8').strip()

            ret.append(
                {'time': ret_time,
                 'product': ret_product,
                 'timetable': ret_timetable})

        return name, ret

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find('!station') == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_station = irc.last_station
        except Exception as e:
            last_station = 0

        if last_station < (time() - 60):
            try:
                name, data = self._get_public_traffic('151213', 10)

                irc.msg(channel, name + ':')

                for i in range(len(data)):
                    irc.msg(channel, '   ' +
                            data[i]['time'] + ': ' +
                            data[i]['product'] + ' -> ' +
                            data[i]['timetable'])

                irc.last_station = time()

            except Exception as e:
                print(e)
                irc.msg(channel, 'Error while fetching data.')
        else:
            irc.msg(channel, "Don't overdo it ;)")
