#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class Plugin:
    """
    This class is a skeleton plugin class defining event hooks on which 
    plugins can be attached.
    """
    def onSignOn(self, channel):
       pass

    def onJoin(self, channel):
        pass

    def onConnect(self, server):
        pass

    def onDisconnect(self, server, reason):
        pass

    def onMessage(self, message, channel):
        pass

    def onNotice(self, message, channel):
        pass

    def onAction(self, user, channel, message):
        pass

    def onAlterCollidedNick(self, nickname):
        pass
