import json
import aiohttp
from irc3 import asyncio
from bytebot_config import BYTEBOT_PLUGIN_CONFIG


@asyncio.coroutine
def spaceapi(bot, target=None):
    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.get(
                BYTEBOT_PLUGIN_CONFIG['spacestatus']['url'])
            if resp.status != 200:
                if target is not None:
                    bot.privmsg(target, "Error while retrieving spaceapi data")
                raise Exception()
            r = yield from resp.read()
    return json.loads(r.decode('utf-8'))
