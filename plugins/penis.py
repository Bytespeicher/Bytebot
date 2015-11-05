#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from time import time

from plugins.plugin import Plugin


class penis(Plugin):
    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand('!penis', 'Penis')

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find('!penis') == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_penis = irc.last_penis
        except Exception:
            last_penis = 0

        if last_penis < (time() - 300):
            irc.msg(channel, '  /\)')
            irc.msg(channel, ' / /')
            irc.msg(channel, '( Y)')
            irc.last_penis = time()
        else:
            irc.msg(channel, "Don't overdo it ;)")
