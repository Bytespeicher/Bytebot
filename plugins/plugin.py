#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class Plugin:
    """
    This class is a skeleton plugin class defining event hooks on which 
    plugins can be attached.
    """

    def registerCommand(self, irc):
        """Registers an irc command that will be listed when !commands is
        called from a user. This command SHOULD be implemented in the same
        class as it is registered in.

        irc: An instance of the bytebot. Will be passed by the plugin loader
        """
        pass

    def minuteCron(self, irc):
        """Registers a function that will be called every minute. This
        function must not exceed an execution time of more than 30 seconds to
        ensure that, when sequentually executed, no ping timeouts occur.

        irc: An instance of the bytebot. Will be passed by the plugin loader
        """
        pass

    def hourCron(self, irc):
        """Registers a function that will be called every hour. This
        function must not exceed an execution time of more than 30 seconds to
        ensure that, when sequentually executed, no ping timeouts occur.

        irc: An instance of the bytebot. Will be passed by the plugin loader
        """
        pass

    def dayCron(self, irc):
        """Registers a function that will be called every day. This
        function must not exceed an execution time of more than 30 seconds to
        ensure that, when sequentually executed, no ping timeouts occur.

        irc: An instance of the bytebot. Will be passed by the plugin loader
        """
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

    def onIrc_JOIN(self, irc, prefix, params):
        pass
