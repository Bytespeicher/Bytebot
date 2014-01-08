#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import re
import inspect
import json
import resource
import ssl

from urllib         import urlopen
from bytebot_config import *
from time           import time

class Bytebot:
    def __init__(self):
        print("ByteBot")
        self.debug    = BYTEBOT_DEBUG
        self._warm_up = True
        self._last_status_check = 0

        self._print("connecting to:" + BYTEBOT_SERVER)

        port = 6667
	sock = socket(AF_INET, SOCK_STREAM)

        try:
            self._print("DEBUG: Trying SSL")
            import ssl
            sock = ssl.wrap_socket(sock)
            port = 9999
        except Exception, e:
            self._print("WARNING: Error with SSL: " + e)
	    sock = socket(AF_INET, SOCK_STREAM)
            pass

        self._irc = sock
        self._irc.connect((BYTEBOT_SERVER, port))

        self._login()

    def _send(self, message):
        self._print('DEBUG: Sending MSG - ' + message)
        self._irc.send('PRIVMSG ' + BYTEBOT_CHANNEL + ' :' + message + '\r\n')

    def _print(self, msg):
        if self.debug == True:
            print(msg)

    def _lookup_dict_command(self, dict):
        self._print("DEBUG: lookup dict command: " + dict)
        return BYTEBOT_DICT_COMMANDS[dict]

    def _list_dict_commands(self):
        commands = ''
        for name in sorted(BYTEBOT_DICT_COMMANDS.keys()):
            commands += name + ', '

        self._send("Available dictionary commands: " + commands)

    def _login(self):
        self._irc.send("USER "+ BYTEBOT_NICK +" "+ BYTEBOT_NICK +" "+ BYTEBOT_NICK +" :bytespeicher bot\n")
        self._irc.send("NICK "+ BYTEBOT_NICK +"\n")
        self._irc.send("PRIVMSG NICKSERV :IDENTIFY " + BYTEBOT_PASSWORD+ "\r\n")
        self._irc.send("JOIN "+ BYTEBOT_CHANNEL +"\n")

    def _parse_msg(self, text):
        try:
            self._print('DEBUG: _parse_msg')
            self._print(text)
            text_tmp = text.split()
            text_tmp.pop(0)
            text_tmp.pop(0)
            message = " ".join(text_tmp)
        except IndexError, e:
            self._print("WARNING: Got IndexError. Message was: " + text)
            return

        for method in dir(self):
            attr = getattr(self, method)
            if inspect.ismethod(attr) and not attr.__name__.startswith("_"):
                attr(message)

    def _run_loop(self):
        while 1:
            text = self._irc.recv(2040)

            if text:
                self._print(text)

                if text.find(':You are now identified for'):
                    self._warm_up = False

                if self._warm_up == True:
                    continue

                if int(time()) - 10 > self._last_status_check:
                    self._print('DEBUG2: status check')
                    self._last_status_check = int(time())
                    self._check_status_changed()

                self._parse_msg(text)

    def ident(self, message):
        if message.find(':Register first') != -1:
            self._login()

    def dict_commands(self, message):
        dict = re.search('^.*[: ]!([^ ].[^ $]*)', message)
        if dict and dict.group(1) and dict.group(1) not in ['help', 'status']:
            try:
                answer = self._lookup_dict_command(dict.group(1))
                if answer:
                    self._send(answer)
                else:
                    self._send("Unknown command '" + dict.group(1) + "'")
            except Exception, e:
                self._send("Unknown command '" + dict.group(1) + "'")

    def dict_commands_list(self, message):
        if message.find('!help') != -1:
            self._print('DEBUG: Sending help..')
            self._list_dict_commands()

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
                self._print('ERROR: ' + str(e))

    def _set_topic(self):
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
            self._print('ERROR: ' + str(e))
            self._print('topic: ' + topic)


    def _get_topic(self):
        self._topic = ''
        self._print('DEBUG: Getting topic for channel ' + BYTEBOT_CHANNEL)
        self._print('DEBUG: self._irc.send("TOPIC ' + BYTEBOT_CHANNEL + '")')
        self._irc.send('TOPIC ' + BYTEBOT_CHANNEL + '\r\n')
        while self._topic.find('332 ' + BYTEBOT_NICK + ' ' + BYTEBOT_CHANNEL) == -1:
            self._topic = self._irc.recv(2040)
            self._topic = self._topic.split('\r\n')[0]

        self._topic = self._topic.split(' :')[1]

        self._print('DEBUG: Topic is: "' + self._topic + '"')

    def _check_status_changed(self):
        self._print('DEBUG2: _check_status_changed')
        if self._warm_up != False:
            self._print('WARNING: _check_status_changed called while warm up phase')
            return

        try:
            response = urlopen(BYTEBOT_STATUS_URL)
            data     = json.loads(response.read())
            
            self._get_topic()
            try:
                old_status = re.search('Space is (open|closed)', self._topic)
                old_status = old_status.group(1)
            except Exception, e:
                old_status = 'closed'

            self._print('DEBUG: ' + old_status)

            if old_status == 'open' and data['state']['open'] == False:
                self._set_topic()
                self._send('Space is now closed!')
                self._print('Status changed to closed')
            elif old_status == 'closed' and data['state']['open'] == True:
                self._set_topic()
                self._send('Space is now open!')
                self._print('Status changed to closed')
            else:
                self._print('No change in status')

        except Exception, e:
            self._send('API Error')
            self._print('ERROR: ' + str(e))

    def _check_user_count(self):
        self._print("WARNING: Not implemented")

    def check_memory_usage(self, message):
        self._print('DEBUG2: MEMORY USAGE - ' + str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
