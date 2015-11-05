#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl, task
from twisted.python import logfile, log

from bytebot_config import BYTEBOT_NICK, BYTEBOT_PASSWORD, BYTEBOT_CHANNEL, \
    BYTEBOT_SSL, BYTEBOT_PORT, BYTEBOT_SERVER, BYTEBOT_PLUGINS, \
    BYTEBOT_LOGPATH, BYTEBOT_LOGLEVEL
from bytebotpluginloader import ByteBotPluginLoader
from bytebot_log import BytebotLogObserver, LOG_ERROR, LOG_INFO, LOG_WARN, \
    LOG_DEBUG


class ByteBot(irc.IRCClient):

    nickname = BYTEBOT_NICK
    password = BYTEBOT_PASSWORD
    realname = BYTEBOT_NICK
    username = BYTEBOT_NICK
    channel = BYTEBOT_CHANNEL

    plugins = {}

    def registerCommand(self, name, description=''):
        self.plugins[name] = description

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.factory.plugins.run(
            'registerCommand',
            {'irc': self}
        )

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        log.msg("[sign on]")
        self.join(self.factory.channel)
        self.startCron()

    def joined(self, channel):
        log.msg("[joined channel %s]" % channel)
        self.factory.plugins.run('onJoined',
                                 {
                                     'irc': self,
                                     'channel': channel
                                 })

    def privmsg(self, user, channel, msg):
        self.factory.plugins.run('onPrivmsg',
                                 {
                                     'irc':       self,
                                     'user':      user,
                                     'channel':   channel,
                                     'msg':       msg
                                 })

        user = user.split("!", 1)[0]

        if channel == self.nickname:
            """ User whispering to the bot"""
            self.msg(
                user,
                "I don't usually whisper back. But when I do, it's to you."
            )
            return

        if msg.startswith(self.nickname + ":"):
            msg = "%s: Ich bin ein Bot. Meine Intelligenz ist limitiert" % user
            self.msg(channel, msg)
            log.msg("<%s> %s" % (self.nickname, msg))

        if msg.startswith('!commands'):
            for pid, name in enumerate(self.plugins):
                self.msg(channel, "%s. %s:" % (pid+1, name))
                self.msg(channel, "\t%s" % self.plugins[name])

    def userJoined(self, user, channel):
        self.factory.plugins.run('onUserJoined',
                                 {
                                     'irc':     self,
                                     'user':    user,
                                     'channel': channel
                                 })

    def irc_JOIN(self, prefix, params):
        self.factory.plugins.run('onIrc_JOIN',
                                 {
                                     'irc':     self,
                                     'prefix':  prefix,
                                     'params':  params
                                 })

    def noticed(self, user, channel, message):
        """
        This function is called if a NOTICE is received. According to the RFC
        one MUST NOT send automatic replies in response to a NOTICE to avoid
        loops between clients.
        """
        pass

    def action(self, user, channel, msg):
        user = user.split("!", 1)[0]

    def irc_NICK(self, prefix, params):
        old_nick = prefix.split("!")[0]
        new_nick = params[0]

    def irc_RPL_TOPIC(self, prefix, params):
        self.current_topic = params

    def alterCollidedNick(self, nickname):
        return nickname + "^"

    def startCron(self):
        def runPerMinute():
            log.msg("[running cron - every 60s]")
            self.factory.plugins.run('minuteCron', {'irc': self})

        def runPerFiveMinutes():
            log.msg("[running cron - every 5m]")
            self.factory.plugins.run('fiveMinuteCron', {'irc': self})

        def runPerHour():
            log.msg("[running cron - every 60m]")
            self.factory.plugins.run('hourCron', {'irc': self})

        def runPerDay():
            log.msg("[running cron - every 24h]")
            self.factory.plugins.run('dayCron', {'irc': self})

        self.minuteCron = task.LoopingCall(runPerMinute)
        self.minuteCron.start(60.0)

        self.fiveMinuteCron = task.LoopingCall(runPerFiveMinutes)
        self.fiveMinuteCron.start(300.0)

        self.hourCron = task.LoopingCall(runPerHour)
        self.hourCron.start(3600.0)

        self.dayCron = task.LoopingCall(runPerDay)
        self.dayCron.start(86400.0)


class ByteBotFactory(protocol.ClientFactory):

    def __init__(self, nickname, password, channel):
        self.nickname = nickname
        self.password = password
        self.channel = channel
        self.plugins = ByteBotPluginLoader(BYTEBOT_PLUGINS)

    def buildProtocol(self, addr):
        p = ByteBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        log("FATAL: connection failed: %s" % reason, level=LOG_ERROR)
        reactor.stop()


if __name__ == '__main__':
    # ERROR | WARNING
    log_error = logfile.LogFile("error.log", BYTEBOT_LOGPATH,
                                rotateLength=10000000, maxRotatedFiles=100)

    # INFO | DEBUG
    log_info = logfile.LogFile("bytebot.log", BYTEBOT_LOGPATH,
                               rotateLength=10000000, maxRotatedFiles=100)

    logger_error = BytebotLogObserver(
        log_error,
        (BYTEBOT_LOGLEVEL & ~LOG_INFO & ~LOG_DEBUG & ~LOG_WARN)
    )
    logger_info = BytebotLogObserver(
        log_info,
        (BYTEBOT_LOGLEVEL & ~LOG_ERROR)
    )

    log.addObserver(logger_error.emit)
    log.addObserver(logger_info.emit)

    f = ByteBotFactory(BYTEBOT_NICK, BYTEBOT_PASSWORD, BYTEBOT_CHANNEL)
    if BYTEBOT_SSL is True:
        reactor.connectSSL(
            BYTEBOT_SERVER,
            int(BYTEBOT_PORT),
            f,
            ssl.ClientContextFactory()
        )
    else:
        reactor.connectTCP(BYTEBOT_SERVER, int(BYTEBOT_PORT), f)
    reactor.run()
