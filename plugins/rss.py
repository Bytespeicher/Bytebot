#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import feedparser

from twisted.python import log
from pytz           import timezone
from dateutil       import parser
from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG, BYTEBOT_CHANNEL
from bytebot_log    import LOG_WARN

class rss(Plugin):
    def __init__(self):
        pass

    def registerCommand(self, irc):
        """Registers the '!rss' command to the global command list
        
        irc:        An instance of the bytebot. Will be passed by the plugin loader
        """

        irc.registerCommand('!rss', 'Show the last recent changes')

    def fiveMinuteCron(self, irc):
        """Checks RSS feed every 5 minutes and post recent changes

        irc:        An instance of the bytebot. Will be passed by the plugin loader
        """
        try:

            self.irc     = irc
            self.channel =  BYTEBOT_CHANNEL
            for feed in BYTEBOT_PLUGIN_CONFIG['rss']:
                # process new feed entries
                self.processFeed(feed)

        except Exception as e:
            print(e)
            print("Error while processing rss feed")


    def onPrivmsg(self, irc, msg, channel, user):
        """Looks for a '!rss' command in messages posted to the channel and 
        returns a list of recent changes.

        irc:        An instance of the bytebot. Will be passed by the plugin loader
        msg:        The msg sent to the channel
        channel:    The channels name
        user:       The user who sent the message
        """

        if msg.find('!rss') == -1:
            return

        # Found rss command without source, show details
        if msg.find(' ') == -1:
            irc.msg(channel, "Use !rss with one of the following second parameter to specify source:")
            for feed in BYTEBOT_PLUGIN_CONFIG['rss']:
                irc.msg(channel, "  %s (%s)" % (feed['name'].lower(), feed['url']))
            return

        self.irc     = irc
        self.channel = channel

        # Found source, show last feed entries
        for feed in BYTEBOT_PLUGIN_CONFIG['rss']:
            if msg.split(' ', 1)[1] == feed['name'].lower():
                self.processFeed(feed, 5)

    def processFeed(self, feed, numberOfEntries = -1):
        """Process a rss feed an post numberOfEntries

        feed:            Dictionary with feed informations
        numberOfEntries: Number of entries to post. -1 means to post only new entries based on cached informations
        """

        if numberOfEntries == -1:
            # try to read read cache information about last run
            cache = open(feed['cache'], "ar+")
            line = cache.readline()
            cached_etag = ""
            last_entry_timestamp = 0
            if len(line) > 3:
                (cached_etag, last_entry_timestamp) = line.split(" ", 1)

            request = feedparser.parse(feed['url'], etag=cached_etag)
        else:
            request = feedparser.parse(feed['url'])

        # Nothing changed
        if request.status == 304:
            return

        # Feed not successfull retrieved, so stop with error
        if request.status != 200:
            log.msg("Unknown HTTP status retrieved for feed %s: %d" % (feed['name'], request.status), level=LOG_WARN)

        # local timezone
        timezoneEF = timezone('Europe/Berlin')

        # remove unneeded entries in feed
        if numberOfEntries != -1:
            request.entries = request.entries[0:numberOfEntries]

        # traverse feed entries in reversed order (post oldest first)
        for entry in reversed(request.entries):

            # parse date of entry dependent on the feedtype and convert to timestamp
            if feed['type'] == 'dokuwiki':
                dt = parser.parse(entry.date)
            elif feed['type'] == 'wordpress':
                dt = parser.parse(entry.published)

            dt.astimezone(timezoneEF)
            dt_timestamp = dt.strftime('%s')

            # skip old entries if we would only new entries
            if numberOfEntries == -1 and last_entry_timestamp >= dt_timestamp:
                continue

            # create irc message dependent on the feedtype
            if feed['type'] == 'dokuwiki':
                message = "%s changed %s" % (entry.author, entry.title.split(" - ", 1)[0])
                message2 = "(%s)" % entry.link.split("?", 1)[0]
                if len(entry.title.split(" - ", 1)) == 2:
                     message += " - comment: %s" % entry.title.split(" - ")[1]
            elif feed['type'] == 'wordpress':
                message = "%s added \"%s\"" % (entry.author, entry.title_detail.value)
                message2 = "(%s)" % entry.link

            # post messages with named prefix
            message = "%s | %s" % (feed['name'].upper(), message)
            message2 = "%s   %s" % (" " * len(feed['name']), message2)
            self.irc.say(self.channel, unicode(message).encode('utf-8', errors='replace'))
            self.irc.say(self.channel, unicode(message2).encode('utf-8', errors='replace'))

            # note timestamp for cache
            last_entry_timestamp = dt_timestamp

        # save cache if we only process last entries
        if numberOfEntries == -1:
            cache.truncate(0)
            cache.write('%s %s' % (request.etag, last_entry_timestamp))
            cache.close()
