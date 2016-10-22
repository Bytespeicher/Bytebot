from irc3.plugins.command import command

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
import json
import aiohttp

@command(permission="view")
@asyncio.coroutine
def status(bot, mask, target, args):
    """Returns the door status of the hackerspace rooms

        %%status
    """
    try:
        with aiohttp.Timeout(10):
            with aiohttp.ClientSession(loop=bot.loop) as session:
                resp = yield from session.get(
                    BYTEBOT_PLUGIN_CONFIG['spacestatus']['url'])
                if resp.status != 200:
                    bot.privmsg(target, "Error while retrieving weather data")
                    raise Exception()
                r = yield from resp.read()

        data = json.loads(r.decode('utf-8'))

        bot.privmsg(target, 'Space status:')
        if data['state']['open']:
            bot.privmsg(target, '\tDer Space ist offen!')
        else:
            bot.privmsg(target, '\tDer Space ist geschlossen!')
    except Exception:
        bot.privmsg(target, '\tFehler beim Abrufen des Status')


@command(permission="view")
@asyncio.coroutine
def users(bot, mask, target, args):
    """Returns the current users inside the hackerspace rooms

        %%users
    """
    try:
        with aiohttp.Timeout(10):
            with aiohttp.ClientSession(loop=bot.loop) as session:
                resp = yield from session.get(
                    BYTEBOT_PLUGIN_CONFIG['spacestatus']['url'])
                if resp.status != 200:
                    bot.privmsg(target, "Error while retrieving weather data")
                    raise Exception()
                r = yield from resp.read()

        data = json.loads(r.decode('utf-8'))['sensors']['people_now_present'][0]

        if data['value'] > 0:
            bot.privmsg(target,
                    'Space users: ' + str(', '.join(data['names'])))
        elif data['value'] == 0:
            bot.privmsg(target, 'Scheinbar ist niemand im Space :(')
        else:
            bot.privmsg(target,
                    'Ich bin mir nicht sicher, ob jemand da ist')
    except Exception:
        bot.privmsg(target, '\tFehler beim Abrufen der User')
