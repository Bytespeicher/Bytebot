#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import re
from urllib import urlopen

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_STATUS_URL, BYTEBOT_TOPIC, BYTEBOT_CHANNEL


class autotopic(Plugin):

    def minuteCron(self, irc):
        try:
            irc.topic(BYTEBOT_CHANNEL)
            old_topic = irc.current_topic

            topic = BYTEBOT_TOPIC
            response = urlopen(BYTEBOT_STATUS_URL)
            data = json.loads(response.read())
            if data['state']['open'] is True:
                topic += u' | Space is open'
                status = 'open'
            else:
                topic += u' | Space is closed'
                status = 'closed'

            try:
                old_status = re.search('Space is (open|closed)', old_topic[2])
                old_status = old_status.group(1)
            except Exception as e:
                old_status = "closed"

            if old_status != status:
                irc.topic(
                    BYTEBOT_CHANNEL,
                    unicode(topic).encode('utf-8', errors='replace')
                )
                irc.topic(BYTEBOT_CHANNEL)
        except Exception as e:
            print(e)
            print("Error while setting topic")
