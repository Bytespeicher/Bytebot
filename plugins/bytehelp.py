from irc3.plugins.command import command


@command(permission="view")
def bytehelp(bot, mask, target, args):
    """Simple Q&A command

    %%bytehelp [<question>]
    """

    config = bot.config.get(__name__, {})

    """Remove default hash key from config and determine commands"""
    if 'hash' in config:
        del config['hash']
    commands = sorted(config.keys())

    if args['<question>'] is None:

        bot.privmsg(
            target,
            "Use !bytehelp with the following commands: " + ', '.join(commands)
        )
        bot.privmsg(target,
                    "Or try !help for a list of all available commands")
        return

    question = args['<question>']
    if question in commands:
        bot.privmsg(target, config[question])
    else:
        bot.privmsg(
            target,
            "Sorry, I did not understand your question, maybe try !bytehelp"
        )
