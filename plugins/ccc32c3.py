#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import datetime
from time import time

from plugins.plugin import Plugin

from bytebot_config import BYTEBOT_HTTP_TIMEOUT, BYTEBOT_HTTP_MAXSIZE
from bytebot_config import BYTEBOT_PLUGIN_CONFIG

with open("events.json") as json_file:
    json_data = json.load(json_file)

class ccc32c3(Plugin):

    def __init__(self):
        pass

    def registerCommand(self, irc):
        irc.registerCommand("!32c3", "32c3")

    def get_plays(self, hall):
        now_playing = json_data['schedule']['conference']['days'][0]['rooms'][hall][0]
        now_playing['date'] = "2099-12-31T23:59:59+01:00"

        next_playing = json_data['schedule']['conference']['days'][0]['rooms'][hall][0]
        next_playing['date'] = "2099-12-31T23:59:59+01:00"

        for x in json_data['schedule']['conference']['days']:

            for event in x['rooms'][hall]:
                z = (datetime.datetime.strptime(event['date'][0:-6], "%Y-%m-%dT%H:%M:%S") - datetime.datetime.now())
                
                if(z.days < 0):
                    now_playing = event



            for event in x['rooms'][hall]:
                z = (datetime.datetime.strptime(event['date'][0:-6], "%Y-%m-%dT%H:%M:%S") - datetime.datetime.now())

                if(z.days >= 0):
                    if(datetime.datetime.strptime(event['date'][0:-6], "%Y-%m-%dT%H:%M:%S") < datetime.datetime.strptime(next_playing['date'][0:-6], "%Y-%m-%dT%H:%M:%S")):
                        next_playing = event

        return now_playing, next_playing

    def conv(self, t):
        x = datetime.datetime.strptime(t[0:-6], "%Y-%m-%dT%H:%M:%S")
        return x.strftime("%H:%M")

    def onPrivmsg(self, irc, msg, channel, user):
        if msg.find("!32c3") == -1:
            return

        self.irc = irc
        self.channel = channel

        try:
            last_ccc32c3 = irc.last_ccc32c3
        except Exception:
            last_ccc32c3 = 0

        if msg.find("now") != -1:
            #if last_ccc32c3 < (time() - 60):
                now, next = self.get_plays("Hall 1")
                irc.msg(channel, ("Hall 1: " + self.conv(now['date']) + " " + now['title']).encode("utf-8", "ignore"))

                now, next = self.get_plays("Hall 2")
                irc.msg(channel, ("Hall 2: " + self.conv(now['date']) + " " + now['title']).encode("utf-8", "ignore"))

                now, next = self.get_plays("Hall G")
                irc.msg(channel, ("Hall G: " + self.conv(now['date']) + " " + now['title']).encode("utf-8", "ignore"))

                now, next = self.get_plays("Hall 6")
                irc.msg(channel, ("Hall 6: " + self.conv(now['date']) + " " + now['title']).encode("utf-8", "ignore"))

                irc.last_ccc32c3 = time()
            #else:
            #    irc.msg(channel, "Don't overdo it ;)")

        if msg.find("next") != -1:
            #if last_ccc32c3 < (time() - 60):
                now, next = self.get_plays("Hall 1")
                irc.msg(channel, ("Hall 1: " + self.conv(next['date']) + " " + next['title']).encode("utf-8", "ignore"))

                now, next = self.get_plays("Hall 2")
                irc.msg(channel, ("Hall 2: " + self.conv(next['date']) + " " + next['title']).encode("utf-8", "ignore"))

                now, next = self.get_plays("Hall G")
                irc.msg(channel, ("Hall G: " + self.conv(next['date']) + " " + next['title']).encode("utf-8", "ignore"))

                now, next = self.get_plays("Hall 6")
                irc.msg(channel, ("Hall 6: " + self.conv(next['date']) + " " + next['title']).encode("utf-8", "ignore"))

                irc.last_ccc32c3 = time()
            #else:
            #    irc.msg(channel, "Don't overdo it ;)")