#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class Plugin:
    """
    This class is a skeleton plugin class defining event hooks on which 
    plugins can be attached.
    """

    def registerCommand(self, irc):
        pass

    def minuteCron(self, irc):
        pass

    def hourCron(self, irc):
        pass

    def dayCron(self, irc):
        pass

    def onSignOn(self, irc, channel):
        pass

    def onJoined(self, irc, channel):
        pass

    def onConnect(self, irc, server):
        pass

    def onDisconnect(self, irc, server, reason):
        pass

    def onMessage(self, irc, message, channel):
        pass

    def onPrivmsg(self, irc, user, channel, msg):
        pass

    def onNotice(self, irc, message, channel):
        pass

    def onAction(self, irc, user, channel, message):
        pass

    def onAlterCollidedNick(self, irc, nickname):
        pass

    def onUserJoined(self, irc, user, channel):
        pass
