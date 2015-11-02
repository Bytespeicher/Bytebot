#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json

from urllib import urlopen

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from plugins.plugin import Plugin


class spacestatus(Plugin):
    def registerCommand(self, irc):
        irc.registerCommand(
            '!status',
            'Returns the door status of the hackerspace rooms'
        )
        irc.registerCommand(
            '!users',
            'Returns the current users inside the hackerspace rooms'
        )

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.startswith('!status'):
            try:
                response = urlopen(BYTEBOT_PLUGIN_CONFIG['spacestatus']['url'])
                data = json.loads(response.read())

                irc.msg(channel, 'Space status:')
                if data['state']['open']:
                    irc.msg(channel, '\tDer Space ist offen!')
                else:
                    irc.msg(channel, '\tDer Space ist geschlossen!')
            except Exception:
                irc.msg(channel, '\tFehler beim Abrufen des Status')

        if msg.startswith('!users'):
            try:
                response = urlopen(BYTEBOT_PLUGIN_CONFIG['spacestatus']['url'])
                data = json.loads(response.read())['sensors'][
                    'people_now_present'][0]

                if data['value'] > 0:
                    irc.msg(channel,
                            'Space users: ' + str(', '.join(data['names'])))
                elif data['value'] == 0:
                    irc.msg(channel, 'Scheinbar ist niemand im Space :(')
                else:
                    irc.msg(channel,
                            'Ich bin mir nicht sicher, ob jemand da ist')
            except Exception as e:
                print(e)
                irc.msg(channel, '\tFehler beim Abrufen der User')
