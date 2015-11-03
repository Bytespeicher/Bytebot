#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
import json
import re

from plugins.plugin import Plugin
from bs4 import BeautifulSoup
from twisted.python import log

from clarifai.client import ClarifaiApi

from bytebot_config import BYTEBOT_HTTP_TIMEOUT, BYTEBOT_HTTP_MAXSIZE
from bytebot_config import BYTEBOT_PLUGIN_CONFIG


class shorturl(Plugin):

    def googl(self, url):
        log.msg("Shortening URL %s" % url)

        post_url = 'https://www.googleapis.com/urlshortener/v1/url'
        postdata = {'longUrl': url}
        headers = {'Content-Type': 'application/json'}

        req = urllib2.Request(
            post_url,
            json.dumps(postdata),
            headers
        )
        data = urllib2.urlopen(url=req, timeout=BYTEBOT_HTTP_TIMEOUT).read(
            BYTEBOT_HTTP_MAXSIZE)
        ret = json.loads(data)[u'id'].encode('ascii', 'ignore')

        return ret

    def krzus(self, url):
        log.msg("Shortening URL %s" % url)

        post_url = 'http://krz.us/api/v1/short'
        postdata = {
            'url': url,
            'key': BYTEBOT_PLUGIN_CONFIG['shorturl']['api_key']
        }
        headers = {'Content-Type': 'application/json'}

        req = urllib2.Request(
            post_url,
            json.dumps(postdata),
            headers
        )
        data = urllib2.urlopen(url=req, timeout=BYTEBOT_HTTP_TIMEOUT).read(
            BYTEBOT_HTTP_MAXSIZE)
        ret = json.loads(data)[u'url_short'].encode('ascii', 'ignore')

        return ret

    def getTitle(self, url):
        data = urllib2.urlopen(url=url, timeout=BYTEBOT_HTTP_TIMEOUT)
        soup = BeautifulSoup(data)
        return soup.title.getText().encode('utf-8')[:60]

    def getTags(self, url):
        ret = ''
        api = ClarifaiApi(
                BYTEBOT_PLUGIN_CONFIG['shorturl']['clarifai_app_id'],
                BYTEBOT_PLUGIN_CONFIG['shorturl']['clarifai_app_secret']
            )
        tags = api.tag_image_urls(url)

        if(tags[u'status_code'] == "OK"):
            ret = ', '.join(tags[u'results'][0][u'result'][u'tag'][u'classes'])

        return ret

    def onPrivmsg(self, irc, msg, channel, user):

        try:
            url = re.findall(
                'http[s]?://(?:[^\s]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)[0]
            try:
                short_function = getattr(self, BYTEBOT_PLUGIN_CONFIG[
                                         'shorturl']['shortener'])
                shorturl = short_function(url)
            except NameError:
                log.msg('Could not load shortener function ' +
                        BYTEBOT_PLUGIN_CONFIG)
        except Exception as e:
            log.msg(e)
            return

        if(url[-4:] == '.jpg'):
            try:
                desc = 'Tags : ' + self.getTags(url)
            except Exception as e:
                desc = ''
        else
            try:
                desc = 'Title : ' + self.getTitle(url)
            except Exception as e:
                desc = ''

        if desc != '':
            irc.msg(channel, desc)
            irc.msg(channel, '\tURL: %s' % shorturl)
        else:
            irc.msg(channel, "URL: %s" % shorturl)
