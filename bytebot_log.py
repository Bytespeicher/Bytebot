#!/usr/bin/env python2
# -*- coding: utf-8 -*-

LOG_DEBUG = 0b0001
LOG_INFO = 0b0010
LOG_WARN = 0b0100
LOG_ERROR = 0b1000

from twisted.python import log

class BytebotLogObserver(log.FileLogObserver):
    def __init__(self, f, level=LOG_ERROR):
        self.level = level
        log.FileLogObserver.__init__(self, f)

    def emit(self, eventDict):
        if eventDict['isError']:
            level = LOG_ERROR
        elif 'level' in eventDict:
            level = eventDict['level']
        else:
            level = LOG_INFO

        if (self.level & level) > 0:
            log.FileLogObserver.emit(self, eventDict)
