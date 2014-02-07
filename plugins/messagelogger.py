#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from plugin import Plugin

class MessageLogger(Plugin):
    def __init__(self, filename):
        self.file = open(filename, "a")

    def __del__(self):
        self.file.close()

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def onConnectionMade(self):
        self.log("[connected at %s]" %
                 time.asctime(time.localtime(time.time())))

    def onConnectionLost(self, reason):
        self.log("[disconnected at %s]", %
                 time.asctime(time.localtime(time.time())))

    def onSignedOn(self):
        self.log("[signed on at %s]", %
                 time.asctime(time.localtime(time.time())))

    def onPrivMsg(self, user, channel, msg):
        self.log("%s: <%s> %s" % (channel, user, msg))

    def onAction(self, user, channel, msg):
        self.log("%s: * %s %s" % (channel, user, msg))

    def onIrc_Nick():
        self.log("%s is now know as %s" % (old_nick, new_nick))

