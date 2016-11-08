#!/usr/bin/env python3
#!python3
# -*- coding: utf-8 -*-
from irc3.plugins.command import command

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
import json
import aiohttp
import requests
import xml.etree.ElementTree as ET


@command(permission="view")
@asyncio.coroutine
def parking(bot, mask, target, args):
    """Show the current parking lot status

        %%parking
    """
    config = BYTEBOT_PLUGIN_CONFIG['parking']

    if config['url'] == "parking_url":
        return "I don't have your parking url!"

    bot.privmsg(target, 'Parkhausbelegung:')
    r = requests.get(config['url'])
    if r.status_code == 200:
        root = ET.fromstring(r.text)
        for lot in root.findall('ph'):
            name = lot.find('longname').text.replace("Ăź", "ü")
            use = int(lot.find('belegung').text)
            max = int(lot.find('kapazitaet').text)

            print_str = \
                u"   {:32}".format(name) + \
                u"{:3}".format(max - use) + \
                u" von " + \
                u"{:3}".format(max) + \
                u" frei"

            bot.privmsg(target, print_str)
    else:
        r.raise_for_status()
        return "Service seems offline!"
