#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from plugins.plugin import Plugin

class AutoTopic(Plugin):

    def __init__(self):
        pass

    def status(self,message):
        if message.find('!status') != -1:
            try:
                response = urlopen(BYTEBOT_STATUS_URL)
                data = json.loads(response.read())

                self._send('Space status:')
                if data['state']['open']:
                    self._send('    Space is currently open: ' + data['state']['message'])
                else:
                    self._send('    Space is currently closed ' + data['state']['message'])
            except Exception, e:
                self._send('Error retrieving Space status')

    def set_topic(self):
        try:
            topic = BYTEBOT_TOPIC
            response = urlopen(BYTEBOT_STATUS_URL)
            data = json.loads(response.read())
            if data['state']['open']:
                topic += u' | Space is open (' + unicode(data['state']['message']) + ')'
            else:
                topic += u' | Space is closed'


            self._irc.send(unicode('TOPIC ' + BYTEBOT_CHANNEL + ' :' + topic + '\r\n').encode('utf-8', errors='replace'))
        except Exception, e:
            self._send('API Error - topic::status')

    def get_topic(self):
        self.topic = ''
        self._irc.send('TOPIC ' + BYTEBOT_CHANNEL + '\r\n')
        while self._topic.find('332 ' + BYTEBOT_NICK + ' ' + BYTEBOT_CHANNEL) == -1:
            self.topic = self._irc.recv(2040)
            self.topic = self._topic.split('\r\n')[0]

        self.topic = self._topic.split(' :')[1]

    def everyMinute(self, irc):
        print(self.irc.topic(self.irc.channel))
