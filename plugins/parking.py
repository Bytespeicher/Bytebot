from irc3.plugins.command import command

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
import aiohttp
import xml.etree.ElementTree as ET


@command(permission="view")
@asyncio.coroutine
def parking(bot, mask, target, args):
    """Show the current parking lot status

        %%parking
    """
    config = BYTEBOT_PLUGIN_CONFIG['parking']

    if config['url'] == "parking_url":
        return "I don't have your parking url!"

    bot.privmsg(target, 'Parkhausbelegung:')

    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            resp = yield from session.get(config['url'])
            if resp.status != 200:
                bot.privmsg(target, "Error while retrieving parking data")
                raise Exception()
            r = yield from resp.read()

            root = ET.fromstring(r)
            for lot in root.findall('ph'):
                bot.privmsg(target,
                            "    {name:32}{use:3} von {max:3} frei".format(
                                name=lot.find('longname').text,
                                use=int(lot.find('belegung').text),
                                max=int(lot.find('kapazitaet').text)
                            ))
