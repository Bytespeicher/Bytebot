from irc3 import asyncio
from irc3.plugins.command import command

from git import Repo
import time


@command(permission="view")
@asyncio.coroutine
def version(bot, mask, target, args):
    """Get current running version information of bot

        %%version
    """

    try:
        repo = Repo()
        bot.privmsg(
            target,
            "Bot is running on commit %s" % repo.head.commit.hexsha
        )
        bot.privmsg(
            target,
            "Commited on %s by %s" % (
                time.strftime(
                    "%d.%m.%Y %H:%M",
                    time.gmtime(repo.head.commit.committed_date)
                ),
                repo.head.commit.author.name
            )
        )

    except Exception:
        bot.privmsg(target, "Error while retrieving git information")
        raise Exception()
