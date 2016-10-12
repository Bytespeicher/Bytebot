#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import aiohttp
from irc3 import asyncio
from irc3.plugins.command import command
from bs4 import BeautifulSoup

from bytebot_config import BYTEBOT_HTTP_TIMEOUT


@command(permission="view")
@asyncio.coroutine
def station(bot, mask, target, args):
    """Show current tram and bus station information

        %%station
    """
    url = "http://vmt.hafas.de/bin/stboard.exe/dn?"
    station='151213'
    number_of_results=10
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

    with aiohttp.Timeout(BYTEBOT_HTTP_TIMEOUT):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.post(url, data=data)
            if resp.status != 200:
                raise Exception()

            response = yield from resp.read()

    soup = BeautifulSoup(response, 'html.parser')

    station_name = soup.find_all('span', {"class": "output"})
    time = soup.find_all('td', {"class": "time"})
    product = soup.find_all('td', {"class": "product"})
    timetable = soup.find_all('strong', {"class": "startDestination"})

    name = station_name[0].text.encode('utf-8').strip()
    data = []

    for i in range(number_of_results):
        ret_time = time[i].text.encode('utf-8').strip()
        ret_product = product[i].text.encode('utf-8').strip()
        ret_product = ret_product.replace(b"    ", b" ")
        ret_timetable = timetable[i].find('a').text.encode('utf-8').strip()

        data.append(
            {'time': ret_time,
             'product': ret_product,
             'timetable': ret_timetable})

    bot.privmsg(target, name.decode())

    for i in range(len(data)):
        bot.privmsg(target,
                    "%s: %s -> %s" % (data[i]['time'].decode(),
                                      data[i]['product'].decode(),
                                      data[i]['timetable'].decode()))
