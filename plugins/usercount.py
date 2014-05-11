#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from plugins.plugin import Plugin
from twisted.python import log
from bytebot_log    import LOG_WARN

class usercount(Plugin):
    def __init__(self):
        log.msg("Usercount not implemented yet", level=LOG_WARN)
        pass
