#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from plugins.plugin import Plugin
from time import time

class muschi(Plugin):
    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand('!muschi', 'Muschi')

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find('!muschi') == -1:
            return

        self.irc     = irc
        self.channel = channel

        try:
            last_muschi = irc.last_muschi
        except Exception as e: 
            last_muschi = 0

        if last_muschi < (time() - 300):
            irc.msg(channel, "   /),,,/)")
            irc.msg(channel, " =( ' Y ' )=")
            irc.msg(channel, "   ( U U )")
            irc.msg(channel, ',,,("),("),,,')
            irc.last_muschi = time()
        else:
            irc.msg(channel, "Don't overdo it ;)")
