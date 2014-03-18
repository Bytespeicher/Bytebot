# Plugins
To work with the autoloader, for now all class names MUST be lowercase.

All plugins MUST inherit from plugins.plugin.Plugin.

If a plugin adds chat commands you MAY add those to the list of available
commands via the registerCommand function.

# Dependencies

* Bytebot
 * sys
 * re
 * inspect
 * json
 * resource
 * ssl
 * twisted
 * urllib
 * time
* autotopic
 * urllib
 * json
 * re
* messagelogger
 * time
* shorturl
 * beautifulsoup4
 * urllib2
 * json
 * re
* spacestatus
 * urllib
 * json
