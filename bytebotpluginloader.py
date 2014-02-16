#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from sys                import exit

class ByteBotPluginLoader:
    PLUGINS = {} 

    def __init__(self, plugins, plugin_path='plugins'):
        """
        plugins:        tupel with plugins
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
            except Exception as e:
                print("FATAL: Could not import plugin %s.%s" %
                      (path, plugin))
                exit(255)

    def run(self, fn, args={}):
        for key, plugin in self.PLUGINS.iteritems():
            try:
                method = getattr(plugin, fn)
                method(**args)
            except Exception as e:
                print("WARNING: An error occured while executing %s in %s with %s" %
                     (fn, plugin, args))
