from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
from irc3.plugins.command import command

import aiohttp
import json
import urllib.parse


@command(permission="view")
@asyncio.coroutine
def wikipedia(bot, mask, target, args):
    """Get short abstract from wikipedia for a given topic

        %%wikipedia <topic>...
    """

    config = BYTEBOT_PLUGIN_CONFIG['wikipedia']

    if ' '.join(args['<topic>']) == 'help':
        return 'Use !wikipedia TOPIC to show wikipedia abstract about topic'

    """Request the wikipedia content."""
    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            url = config['url']
            url += urllib.parse.quote_plus('_'.join(args['<topic>']))
            resp = yield from session.get(url)
            if resp.status == 200:
                """Get text content from http request."""
                r = yield from resp.text()
            else:
                bot.privmsg(
                    target,
                    "Error while retrieving data from wikipedia"
                )
                raise Exception()

    try:
        """Load JSON data from response"""
        json_data = json.loads(r)
        w = json_data["query"]["pages"]
        if ('-1' not in w.keys()):
            """Valid response from wikipedia for existing topic"""
            text = w[list(w.keys())[0]]["extract"]
            """Shorten abstract"""
            text = text[0:config['length_of_abstract']]
            text = text[0:text.rfind(" ")] + " [...]"
            bot.privmsg(target, text)
        else:
            """Topic did not exist"""
            bot.privmsg(target, "Topic not found on wikipedia")

    except KeyError:
        bot.privmsg(target, "Error while retrieving content from wikipedia")
        raise Exception()
