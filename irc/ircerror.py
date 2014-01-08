#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class IrcErrorLevel:
    DEBUG = 0b00001
    INFO  = 0b00010
    WARN  = 0b00100
    ERROR = 0b01000
    EMERG = 0b10000

class IrcException(Exception):
    pass
