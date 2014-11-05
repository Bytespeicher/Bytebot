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
 * ssl (for debian-based systems: this comes with python-openssl package, not as python-module)
 * twisted
 * urllib
 * time
* autotopic
 * urllib
 * json
 * re
* dates
 * icalendar
 * datetime
 * pytz
 * urllib
* messagelogger
 * time
* rss (which also does atom)
 * feedparser
* shorturl
 * beautifulsoup4
 * urllib2
 * json
 * re
* spacestatus
 * urllib
 * json
