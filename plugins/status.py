from irc3.plugins.command import command

from irc3 import asyncio
from lib.spaceapi import spaceapi


@command(permission="view")
@asyncio.coroutine
def status(bot, mask, target, args):
    """Returns the door status of the hackerspace rooms

        %%status
    """
    try:
        data = yield from spaceapi(bot, target)
        
        for space_data in data:
            bot.privmsg(target, 'Space status of ' + space_data['space'] + ':')
            if space_data['state']['open']:
                bot.privmsg(target, '\tThe space is open!')
            else:
                bot.privmsg(target, '\tThe space is closed!')
                
    except Exception as e:
        bot.log.error(e)
        bot.privmsg(target, '\tError while retrieving space status')


@command(permission="view")
@asyncio.coroutine
def users(bot, mask, target, args):
    """Returns the current users inside the hackerspace rooms

        %%users
    """
    try:
        data = yield from spaceapi(bot, target)
        data = data['sensors']['people_now_present'][0]

        if data['value'] > 0:
            bot.privmsg(target,
                        'Space users: ' + str(', '.join(data['names'])))
        elif data['value'] == 0:
            bot.privmsg(target, 'Nobody is logged into teh space :(')
        else:
            bot.privmsg(target,
                        "I'm not sure if anyone's in the space")
    except Exception as e:
        bot.log.error(e)
        bot.privmsg(target, '\tError while retrieving user data')
