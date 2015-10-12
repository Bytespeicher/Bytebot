#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
import json

from plugins.plugin import Plugin
from time import time

class parken(Plugin):
    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand('!parken', 'Parken')
    
    def getparken(self):
        url = 'http://parken.cjcj.de/erfurt/'
        data = urllib2.urlopen(url, timeout=BYTEBOT_HTTP_TIMEOUT).read(BYTEBOT_HTTP_MAXSIZE)
        data = unicode(data, errors='ignore')
        ret = json.loads(data)

        return ret

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find('!parken') == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_parken = irc.last_parken
        except Exception as e:
            last_parken = 0

        if last_parken < (time() - 300):
            try:
                data = self.getparken();
                irc.msg(channel, 'Freie Parkplätze:')
                for x in range(1, len(ret)):
                    sName = ret[x][u'name'].encode('ascii', 'ignore')
                    iBelegt = int(ret[x][u'belegt'].encode('ascii', 'ignore'))
                    iMaximum = int(ret[x][u'maximal'].encode('ascii', 'ignore'))
                    if(iBelegt<0):
                        iBelegt=0;
                    if(iMaximum<0):
                        iMaximum=0;
                    str = '{:25s}'.format(sName) + ': ' +  '{:3.0f}'.format(iMaximum - iBelegt) + ' P. von ' + '{:3.0f}'.format(iMaximum) + ' P. frei'
                    irc.msg(channel, str)
                
                irc.last_parken = time()
            except Exception as e:
                irc.msg(channel, 'Error while fetching data.')
        else:
            irc.msg(channel, "Don't overdo it ;)")
