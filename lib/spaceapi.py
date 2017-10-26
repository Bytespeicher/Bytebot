import json
import aiohttp
from irc3 import asyncio


@asyncio.coroutine
def spaceapi(bot, target=None):

    """Load configuration"""
    config = bot.config.get(__name__, {})

    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            ret = []
            for space_url in config['url'].split():
                resp = yield from session.get(space_url)
                if resp.status != 200:
                    if target is not None:
                        bot.privmsg(target, "Error while retrieving spaceapi data" + space_url)
                    raise Exception()
                r = yield from resp.read()
                ret.append(json.loads(r.decode('utf-8')))
                    
    return ret
