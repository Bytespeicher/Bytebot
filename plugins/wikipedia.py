#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG
import requests


class wikipedia(Plugin):
    """
    With this plugin you can search for wikipedia entries.
    """
    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand(
			'!wiki TOPIC',
			'wikipedia article summary for TOPIC'
		)

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find('!wiki') == -1:
            return

        self.irc = irc
        self.channel = channel

        config = BYTEBOT_PLUGIN_CONFIG['wikipedia']

        if msg.find(' ') == -1:
            irc.msg(channel, 'usage: !wiki TOPIC')
            return
        else:
            request = " ".join(msg.split(' ')[1:])

        url = config['url'] + request
        try:
            r = requests.get(url)

            if r.status_code != 200:
                irc.msg(channel, 'Error while retrieving wikipedia data')
                return

            w = r.json()["query"]["pages"]
            text = w[list(w.keys())[0]]["extract"][0:300]
            text = text[0:text.rfind(" ")] + "[. . .]"

        except KeyError:
            irc.msg(channel, "Error while retrieving wikipedia data")
            return

        irc.msg(channel, "%s: %s" % (request, text))
