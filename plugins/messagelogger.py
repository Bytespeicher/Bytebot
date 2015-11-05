#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG


class messagelogger(Plugin):
    def __init__(self):
        self.file = open(BYTEBOT_PLUGIN_CONFIG['messagelogger']['file'], "a")

    def __del__(self):
        self.file.close()

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def onConnectionMade(self, irc):
        self.log("[connected at %s]" %
                 time.asctime(time.localtime(time.time())))

    def onConnectionLost(self, irc, reason):
        self.log("[disconnected at %s]" %
                 time.asctime(time.localtime(time.time())))

    def onSignedOn(self, irc):
        self.log("[signed on at %s]" %
                 time.asctime(time.localtime(time.time())))

    def onPrivmsg(self, irc, user, channel, msg):
        self.log("%s: <%s> %s" % (channel, user, msg))

    def onAction(self, irc, user, channel, msg):
        self.log("%s: * %s %s" % (channel, user, msg))

    def onIrc_Nick(self, irc):
        self.log("%s is now know as %s" % (old_nick, new_nick))

