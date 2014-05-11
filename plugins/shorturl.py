#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
import json
import re

from plugins.plugin import Plugin
from bs4            import BeautifulSoup
from twisted.python import log

from bytebot_config import BYTEBOT_HTTP_TIMEOUT, BYTEBOT_HTTP_MAXSIZE

class shorturl(Plugin):
    def googl(self, url):
        log.msg("Shortening URL %s" % url)

        post_url = 'https://www.googleapis.com/urlshortener/v1/url'
        postdata = {'longUrl': url}
        headers = {'Content-Type':'application/json'}

        req = urllib2.Request(
            post_url,
            json.dumps(postdata),
            headers
        )
        data = urllib2.urlopen(url=req, timeout=BYTEBOT_HTTP_TIMEOUT).read(BYTEBOT_HTTP_MAXSIZE)
        ret = json.loads(data)[u'id'].encode('ascii','ignore')

        return ret

    def getTitle(self, url):
	data = urllib2.urlopen(url=url, timeout=BYTEBOT_HTTP_TIMEOUT)
        soup = BeautifulSoup(data)
        return soup.title.string[:60]

    def onPrivmsg(self, irc, msg, channel, user):

        try:
            url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)[0]
            shorturl = self.googl(url)
        except Exception as e:
            return

        try:
            title = self.getTitle(url)
        except Exception as e:
            title = ''

        if title != '':
            irc.msg(channel, title.encode('ascii', 'ignore'))
            irc.msg(channel, '\tURL: %s' % shorturl)
        else:
            irc.msg(channel, "URL: %s" % shorturl)
