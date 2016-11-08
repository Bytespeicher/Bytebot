from irc3.plugins.command import command

from irc3 import asyncio


@command(permission="view")
@asyncio.coroutine
def rofl(bot, mask, target, args):
    """Show the current rofl rofl rofl

        %%rofl
    """
    bot.privmsg(target, 'Incoming ROFLCOPTER!')
    bot.privmsg(target, '.')
    bot.privmsg(target, '    ROFL:ROFL:ROFL:ROFL')
    bot.privmsg(target, '         ___^___ _')
    bot.privmsg(target, ' L    __/      [] \\')
    bot.privmsg(target, 'LOL == =__         \\')
    bot.privmsg(target, ' L      \___ ___ ___]')
    bot.privmsg(target, '              I   I')
    bot.privmsg(target, '          ----------/')
