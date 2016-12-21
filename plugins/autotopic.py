import irc3
from irc3 import asyncio
from irc3.plugins.cron import cron
from lib.spaceapi import spaceapi
import re


@irc3.plugin
class autotopic:

    requires = ['irc3.plugins.async']

    def __init__(self, bot):
        self.bot = bot

        """Load configuration"""
        self.config = {'topic' : ''}
        self.config.update(self.bot.config.get(__name__, {}))

    @cron('* * * * *')
    @asyncio.coroutine
    def cron_topic(self):
        """Change the topic each minute on demand"""
        try:
            data = yield from spaceapi(self.bot)
            current_topic = yield from self.bot.async_cmds.topic(
                self.bot.config.autojoins[0]
            )
            topic = self.config['topic']

            if data['state']['open']:
                topic += u' | Space is open'
                status = 'open'
            else:
                topic += u' | Space is closed'
                status = 'closed'

            try:
                old_status = re.search('Space is (open|closed)',
                                       current_topic['topic'])
                old_status = old_status.group(1)
            except Exception as e:
                old_status = 'closed'

            if old_status != status:
                self.bot.topic(self.bot.config.autojoins[0], topic)

        except Exception as e:
            self.bot.log.error(e)
