#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from sys                import exit
from twisted.internet   import reactor
from bytebot_log        import *
from twisted.python     import log

class ByteBotPluginLoader:
    """This class enables automatic loading and method calling for plugin 
    classes. 

    The class also catches faulty plugin code so if an exception is thrown 
    that is not handled in the plugin code itself it will be handled here 
    without crashing the whole bot."""

    PLUGINS = {} 

    def __init__(self, plugins, plugin_path='plugins'):
        """
        plugins:        tupel with plugin names to register
        plugin_path:    path to plugins
                        MUST NOT end with a trailing slash
        """
        path = plugin_path.replace('/', '.')
        for plugin in plugins:
            try:
                self.PLUGINS[plugin] = getattr(
                    __import__("%s.%s" % (path, plugin)).__dict__[plugin],
                    plugin
                )()

                log.msg("Loaded plugin '%s'" % plugin)
            except Exception as e:
                log.msg("FATAL: Could not import plugin %s.%s" %
                        (path, plugin),
                        level=LOG_ERROR)
                exit(255)

    def run(self, fn, args={}, threaded=True):
        """Runs a specific function on all registered plugins

        fn              plugin method name to execute
        args            dictionary with arguments to call the method with
        threaded        if set to True, the functions will be run in a thread
        """
        log.msg("Executing function %s on all plugins with args %s" %
                (fn, args),
                level=LOG_DEBUG)
        for key, plugin in self.PLUGINS.iteritems():
            try:
                method = getattr(plugin, fn)
                if not threaded:
                    log.msg("Execute | non-threaded | %s->%s" %
                            (plugin, method.__name__),
                            level=LOG_DEBUG)
                    method(**args)
                else:
                    log.msg("Execute | threaded | %s->%s" %
                            (plugin, method.__name__),
                            level=LOG_DEBUG)
                    reactor.callInThread(method, **args)
            except Exception as e:
                log.msg("WARNING: An error occured while executing %s in %s with %s" %
                        (fn, plugin, args),
                        level=LOG_WARN)
