#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from bytebot_config import BYTEBOT_DICT_COMMANDS
from plugins.plugin import Plugin

class Ircquestions(Plugin):
    def __init__(self):
        pass

    def lookup_dict_command(self, dict_name):
        return BYTEBOT_DICT_COMMANDS[dict_name]

    def list_dict_commands(self):
        commands = ''
        for name in sorted(BYTEBOT_DICT_COMMANDS.keys()):
            commands += name + ', '

        self.irc.msg(self.irc.channel, 
                     "Use !help with the following commands: " + commands)

    def onPrivmsg(self, irc, msg, channel, user):
        self.irc     = irc
        self.channel = channel

        if msg.find('!help') == -1:
            return

        if len(msg.split(' ')) == 1:
            self.list_dict_commands()
            return

        try:
            question = msg.split(' ')[1]
        except IndexError as e:
            irc.msg(channel, "Sorry, das habe ich nicht verstanden. Versuch doch mal !help")
            return

        if question in BYTEBOT_CONFIG['ircquestions']:
            irc.msg(channel, BYTEBOT_CONFIG['ircquestions'][question])
