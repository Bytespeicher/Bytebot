#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
import json

from plugins.plugin import Plugin
from time import time

from bytebot_config import BYTEBOT_HTTP_TIMEOUT, BYTEBOT_HTTP_MAXSIZE
from bytebot_config import BYTEBOT_PLUGIN_CONFIG


class parking(Plugin):
    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand('!parking', 'Parken')

    def _get_parking_status(self):
        url = BYTEBOT_PLUGIN_CONFIG['parking']['url']

        data = urllib2.urlopen(url, timeout=BYTEBOT_HTTP_TIMEOUT).read(
                BYTEBOT_HTTP_MAXSIZE)

        data = unicode(data, errors='ignore')

        ret = json.loads(data)

        return ret

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find('!parking') == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_parking = irc.last_parking
        except Exception as e:
            last_parking = 0

        if last_parking < (time() - 60):
            try:
                data = self._get_parking_status()

                irc.msg(channel, 'Free parking lots:')

                for x in range(1, len(data)):

                    name = data[x][u'name'].encode('ascii', 'ignore')
                    occupied = int(data[x][u'belegt'].encode('ascii', 'ignore'))
                    spaces = int(data[x][u'maximal'].encode('ascii', 'ignore'))

                    if(occupied < 0):
                        occupied = 0

                    if(spaces <= 0):
                        print_str = '{:25s}: not available'.format(name)
                    else:
                        print_str = '{:25s}: '.format(name) + \
                                    '{:3.0f} / '.format(spaces - occupied) + \
                                    '{:3.0f}'.format(spaces)

                    irc.msg(channel, print_str)

                irc.last_parking = time()

            except Exception as e:
                print(e)
                irc.msg(channel, 'Error while fetching data.')
        else:
            irc.msg(channel, "Don't overdo it ;)")
