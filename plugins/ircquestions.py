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

        self._send("Available dictionary commands: " + commands)

    def onMessage(self, message, channel):
        if message.find('!help') != -1:
            self._list_dict_commands()

        dict = re.search('^.*[: ]!([^ ].[^ $]*)', message)
        if dict and dict.group(1) and dict.group(1) not in ['help', 'status']:
            try:
                answer = self.lookup_dict_command(dict.group(1))
                if answer:
                    self.irc.sendMessage(answer)
            except Exception, e:
                self._send("Unknown command '" + dict.group(1) + "'")

