#!/usr/bin/env python2

import socket
import sys
import re
import inspect
import json

from urllib         import urlopen
from bytebot_config import *

class Bytebot:
    def __init__(self):
        print("ByteBot loaded")

    def _send(self, message):
        irc.send('PRIVMSG ' + BYTEBOT_CHANNEL + ' :' + message + '\r\n')

    def _lookup_dict_command(self, dict):
	print("lookup dict command: " + dict)
        return BYTEBOT_DICT_COMMANDS[dict]

    def _list_dict_commands(self):
        commands = ''
        for name in sorted(BYTEBOT_DICT_COMMANDS.keys()):
            commands += name + ', '

        self._send("Available dictionary commands: " + commands)

    def ping(self, message):
        if text.find('ping') != -1:
            self._send('pong ' + text.split() [0])

    def dict_commands(self, message):
        dict = re.search('^.*[: ]!([^ ].[^ $]*)', message)
        if dict and dict.group(1) and dict.group(1) != 'help':
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
            print('Sending help..')
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
                print e



def parse_msg(bot, text):
    text = text.split()
    text.pop(0)
    text.pop(0)
    message = " ".join(text)

    for method in dir(bot):
        attr = getattr(bot, method)
        if inspect.ismethod(attr) and not attr.__name__.startswith("_"):
#            print("Executing " + attr.__name__ + " for " + message)
            attr(message)




irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "connecting to:" + BYTEBOT_SERVER
irc.connect((BYTEBOT_SERVER, 6667))
irc.send("USER "+ BYTEBOT_NICK +" "+ BYTEBOT_NICK +" "+ BYTEBOT_NICK +" :bytespeicher bot\n")
irc.send("NICK "+ BYTEBOT_NICK +"\n")
irc.send("PRIVMSG NICKSERV :IDENTIFY " + BYTEBOT_PASSWORD+ "\r\n")
irc.send("JOIN "+ BYTEBOT_CHANNEL +"\n")


bot = Bytebot()

while 1:
    text=irc.recv(2040)
    print text

    if text.find('PING') != -1:
        print("PING REQUEST:\r\n")
        print(text)
        
        print('Reply will be: "PONG ' + text.split() [1] + '"\r\n')
        irc.send('PONG ' + text.split() [1] + '\r\n')

    parse_msg(bot, text)

