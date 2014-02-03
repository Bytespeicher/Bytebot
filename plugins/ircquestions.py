#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class IRCQuestions:
    def __init__(self):
        pass

    def lookup_dict_command(self, dict):
        return BYTEBOT_DICT_COMMANDS[dict]

    def list_dict_commands(self):
        commands = ''
        for name in sorted(BYTEBOT_DICT_COMMANDS.keys()):
            commands += name + ', '

        self._send("Available dictionary commands: " + commands)

    def dict_commands(self, message):
        dict = re.search('^.*[: ]!([^ ].[^ $]*)', message)
        if dict and dict.group(1) and dict.group(1) not in ['help', 'status']:
            try:
                answer = self.lookup_dict_command(dict.group(1))
                if answer:
                    self._send(answer)
                else:
                    self._send("Unknown command '" + dict.group(1) + "'")
            except Exception, e:
                self._send("Unknown command '" + dict.group(1) + "'")

    def dict_commands_list(self, message):
        if message.find('!help') != -1:
            self._list_dict_commands()

