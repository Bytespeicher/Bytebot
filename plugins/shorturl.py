#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re

from twisted.python import log

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from lib import urllib


class shorturl(Plugin):

    def onPrivmsg(self, irc, msg, channel, user):
        try:
            url = re.findall("http[s]?://(?:[^\s]|[0-9]|[$-_@.&+]|[!*\(\),]|" +
                             "(?:%[0-9a-fA-F][0-9a-fA-F]))+", msg)[0]
            try:
                short_function = getattr(urllib, BYTEBOT_PLUGIN_CONFIG[
                                         'shorturl']['shortener'])
                shorturl = short_function(url)
            except NameError:
                log.msg('Could not load shortener function ' +
                        BYTEBOT_PLUGIN_CONFIG)
        except Exception as e:
            log.msg(e)
            return

        desc = ''
        try:
            if url[-4:].lower() in ('.jpg', 'jpeg', '.png', '.gif'):
                desc = 'Tags: ' + urllib.getTags(url)
            else:
                desc = 'Title: ' + urllib.getTitle(url)
        except Exception as e:
            pass

        if desc != '':
            irc.msg(channel, desc.encode('utf-8', 'replace'))
            irc.msg(channel, '\tURL: %s' % shorturl)
        else:
            irc.msg(channel, "URL: %s" % shorturl)
