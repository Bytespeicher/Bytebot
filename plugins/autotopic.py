import json
import re
import aiohttp
from irc3 import asyncio
from irc3 import rfc
from irc3 import event
from irc3.plugins.cron import cron

from bytebot_config import BYTEBOT_STATUS_URL, BYTEBOT_TOPIC, BYTEBOT_CHANNEL


@cron('* * * * *')
@asyncio.coroutine
def autotopic(bot):
    bot.topic(BYTEBOT_CHANNEL)
    bot.log.info('requested channel topic')


@event(rfc.TOPIC)
def myevent(bot, srv=None, me=None, channel=None, data=None):
    bot.log.info('test')
    try:
        bot.topic(channel, topic="TESTTOPIC")
        topic = BYTEBOT_TOPIC
        with aiohttp.Timeout(10):
            with aiohttp.ClientSession(loop=bot.loop) as session:
                resp = yield from session.get(BYTEBOT_STATUS_URL)
                if resp.status != 200:
                    bot.log.info("Error retrieving status")
                    raise Exception()
                response = yield from resp.read()

        data = json.loads(response.decode('utf-8'))
        if data['state']['open'] is True:
            topic += u' | Space is open'
            status = 'open'
        else:
            topic += u' | Space is closed'
            status = 'closed'

        try:
            old_status = re.search('Space is (open|closed)', old_topic[2])
            old_status = old_status.group(1)
        except Exception as e:
            old_status = "closed"

        if old_status != status:
            bot.log.info(bot.topic(
                channel,
                topic
            ))
    except Exception as e:
        bot.log.error(e)
        bot.log.error("Error while setting topic")
