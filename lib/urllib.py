#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib2
import json

from bs4 import BeautifulSoup
from twisted.python import log
from clarifai.client import ClarifaiApi

from bytebot_config import BYTEBOT_HTTP_TIMEOUT, BYTEBOT_HTTP_MAXSIZE
from bytebot_config import BYTEBOT_PLUGIN_CONFIG


def googl(url):
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


def krzus(url):
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


def getTitle(url):
    data = urllib2.urlopen(url=url, timeout=BYTEBOT_HTTP_TIMEOUT)
    soup = BeautifulSoup(data, "html.parser")
    return soup.title.getText().encode('utf-8')[:60]


def getTags(url):
    ret = ''
    api = ClarifaiApi(
        BYTEBOT_PLUGIN_CONFIG['shorturl']['clarifai_app_id'],
        BYTEBOT_PLUGIN_CONFIG['shorturl']['clarifai_app_secret']
    )
    tags = api.tag_image_urls(url)

    if(tags[u'status_code'] == "OK"):
        ret = ', '.join(tags[u'results'][0][u'result'][u'tag'][u'classes'])

    return ret
