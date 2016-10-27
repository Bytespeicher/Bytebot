from irc3.plugins.command import command
from bytebot_config import BYTEBOT_PLUGIN_CONFIG


@command(permission="view")
def bytehelp(bot, mask, target, args):
    """Simple Q&A command

    %%bytehelp [<question>]
    """
    if args['<question>'] is None:
        commands = ''
        for name in sorted(BYTEBOT_PLUGIN_CONFIG['ircquestions'].keys()):
            commands += name + ', '

        bot.privmsg(target,
                    "Use !bytehelp with the following commands: " + commands)
        bot.privmsg(target,
                    "Or try !help for a list of all available commands")
        return

    question = args['<question>']
    if question in BYTEBOT_PLUGIN_CONFIG['ircquestions']:
        bot.privmsg(target, BYTEBOT_PLUGIN_CONFIG['ircquestions'][question])
    else:
        bot.privmsg(
            target,
            "Sorry, I did not understand your question, maybe try !bytehelp"
        )
