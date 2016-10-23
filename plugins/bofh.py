import random
from os.path import dirname, realpath

import aiofiles
from irc3.plugins.command import command
from irc3 import asyncio


@command(permission="view")
@asyncio.coroutine
def bofh(bot, mask, target, args):
    """Returns a random BOFH excuse

        %%bofh
    """
    try:
        f = yield from aiofiles.open(
            dirname(realpath(__file__)) + '/../data/bofh.txt',
            mode='r'
        )
        try:
            data = yield from f.readlines()
        finally:
            yield from f.close()

        bot.privmsg(target, 'Current excuse: %s' % random.choice(data))
    except Exception as e:
        bot.log.error(e)
        bot.privmsg(target, '\tNo way to get excuse: Temporal anomaly')
