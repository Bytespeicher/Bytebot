#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_STATUS_URL, BYTEBOT_TOPIC, BYTEBOT_CHANNEL
from urllib         import urlopen

import json

class autotopic(Plugin):

    def minuteCron(self, irc):
        try:
            topic = BYTEBOT_TOPIC
            response = urlopen(BYTEBOT_STATUS_URL)
            data = json.loads(response.read())
            if data['state']['open']:
                topic += u' | Space is open (' + unicode(data['state']['message']) + ')'
            else:
                topic += u' | Space is closed'

            irc.topic(BYTEBOT_CHANNEL, unicode(topic).encode('utf-8', errors='replace'))
        except Exception as e:
            print("Error while setting topic")
