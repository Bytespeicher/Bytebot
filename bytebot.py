#!/usr/bin/env python2

import socket
import sys
import re
import inspect

from bytebot_config import *

server   = BYTEBOT_SERVER
channel  = BYTEBOT_CHANNEL
botnick  = BYTEBOT_NICK
password = 

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "connecting to:"
irc.connect((BYTEBOT_SERVER, 6667))
irc.send("USER "+ BYTEBOT_NICK +" "+ BYTEBOT_NICK +" "+ BYTEBOT_NICK +" :bytespeicher bot\n")
irc.send("NICK "+ BYTEBOT_NICK +"\n")
irc.send("PRIVMSG NICKSERV :IDENTIFY " + BYTEBOT_PASSWORD+ "\r\n")
irc.send("JOIN "+ BYTEBOT_CHANNEL +"\n")

bot = new Bytebot()

while 1:
    text=irc.recv(2040)
    print text

    if text.find('PING') != -1:
        irc.send('PRIVMSG ' + BYTEBOT_CHANNEL + ' :PONG ' + text.split() [1] + '\r\n')

    parse_msg(bot, message)

def parse_msg(bot, message):
    for method in dir(bot):
        attr = getattr(bot, method):
        if inspect.ismethod(attr) and not attr.startswith("_"):
            print("Executing " + attr + " for " + message)
            attr(message)

class Bytebot:
    def __init__(self):
        print("ByteBot loaded")

    def _send(self, message):
        irc.send('PRIVMSG ' + BYTEBOT_CHANNEL + ' :' + message + '\r\n')

    def _lookup_dict_command(self, dict):
	print("dict " + dict)
        if BYTEBOT_DICT_COMMANDS[dict]:
            send(BYTEBOT_DICT_COMMANDS[dict])

    def _list_dict_commands(self):
        for name in BYTEBOT_DICT_COMMANDS:
            commands += BYTEBOT_DICT_COMMANDS[name]
        self.send("Available dictionary commands: " + commands)

    def ping(self, message):
        if text.find('PING') != -1:
            self.send('pong ' + text.split() [0])

    def dict_commands(self, message):
        dict = re.search('(,,\(.*\))', text)
        if dict.group(0):
            answer = self._lookup_dict(dict.group(0))
            if answer:
                self._send(answer)
            else:
                self._send("Unknown command '" + dict.group(0) + "'")

    def dict_commands_list(self, message):
        if message == ',,(help)'
            self._list_dict_commands()

