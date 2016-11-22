from irc3.plugins.command import command

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
import aiohttp
import json


@command(permission="view")
@asyncio.coroutine
def betterplace(bot, mask, target, args):
    """Show the current betterplace projects

        %%betterplace
    """
    config = BYTEBOT_PLUGIN_CONFIG['betterplace']

    if config['id'] == "betterplace_id":
        return "I don't have your betterplace id!"

    bot.privmsg(target, 'betterplace projects:')

    try:
        url = "https://api.betterplace.org/de/api_v4/organisations/" + \
              str(config['id']) + \
              "/projects.json"

        with aiohttp.Timeout(10):
            with aiohttp.ClientSession(loop=bot.loop) as session:
                resp = yield from session.get(url)
                if resp.status != 200:
                    bot.privmsg(
                        target, "Error while retrieving " + __name__ + " data")
                    raise Exception()
                r = yield from resp.read()

            projects = json.loads(r.decode('utf-8'))

            for d in projects["data"]:
                if(d["closed_at"] is None):
                    bot.privmsg(target,
                                " {name:35}" +
                                " {got:3}€ von {want:3}€ gespendet".format(
                                    name=d["title"],
                                    got=int(
                                        d["donated_amount_in_cents"]) / 100,
                                    want=int(d["donated_amount_in_cents"] +
                                             d["open_amount_in_cents"]) / 100
                                ))

    except KeyError:
        bot.privmsg(target, "Error while retrieving " + __name__ + " data")
        raise Exception()
