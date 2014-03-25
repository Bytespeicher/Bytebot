#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG

class autoop(Plugin):
    def onIrc_JOIN(self, irc, prefix, params):
        channel = params[0]
        user    = prefix.split('!')[0]

        if prefix in BYTEBOT_PLUGIN_CONFIG['autoop']['hostmask'][channel]:
            print("Giving user %s +o on channel %s" % (prefix, channel))
            irc.mode(channel, True, 'o', user=user)
            irc.msg(channel, "Hey, %s, it seems like you're a nice guy. Let me op you hard" % user)
        if user in BYTEBOT_PLUGIN_CONFIG['autoop']['name'][channel]:
            print("Giving user %s +o on channel %s" % (user, channel))
            irc.mode(channel, True, 'o', user=user)
            irc.msg(channel, "Hey, %s, it seems like you're a nice guy. Let me op you hard" % user)
        else:
            print("User %s not in autoop list %s" % (prefix, channel))
