[![Build Status](https://travis-ci.org/Bytespeicher/Bytebot.svg?branch=master)](https://travis-ci.org/Bytespeicher/Bytebot)
[![Codacy](https://img.shields.io/codacy/de9188fbea554501b247e1fac75346c9.svg?style=flat)](https://www.codacy.com/public/info_4/Bytebot)

# Plugins
To work with the autoloader, for now all class names MUST be lowercase.

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

# Contributing
See [CONTRIBUTING](CONTRIBUTING.md) for further information on seting things
up and the general coding style.
