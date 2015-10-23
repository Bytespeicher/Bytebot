#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from icalendar import Calendar
from icalendar.prop import vDDDTypes
from datetime import date, datetime, timedelta
from pytz import utc, timezone
from urllib import urlopen
from dateutil.rrule import *
from dateutil.parser import *

class dates(Plugin):
    def __init__(self):
        try:
            BYTEBOT_PLUGIN_CONFIG['dates'].keys()
        except Exception:
            raise Exception('ERROR: Plugin "dates" is missing configuration!')

        pass

    def registerCommand(self, irc):
        """Registers the '!dates' command to the global command list

        irc: An instance of the bytebot. Will be passed by the plugin loader
        """

        irc.registerCommand('!dates', 'Shows the next planned dates')

    def onPrivmsg(self, irc, msg, channel, user):
        """Looks for a '!dates' command in messages posted to the channel and
        returns a list of dates within the next week.

        irc: An instance of the bytebot. Will be passed by the plugin loader
        msg: The msg sent to the channel
        channel: The channels name
        user: The user who sent the message
        """

        if msg.find('!dates') == -1:
            return

        f = urlopen(BYTEBOT_PLUGIN_CONFIG['dates']['url'])
        cal = Calendar.from_ical(f.read())
        now = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        then = now + timedelta(
            days=BYTEBOT_PLUGIN_CONFIG['dates']['timedelta'])
        found = 0

        data = []
        timezoneEF = timezone('Europe/Berlin')
        fmt = "%d.%m.%Y %H:%M"

        for ev in cal.walk('VEVENT'):
            start = vDDDTypes.from_ical(ev["DTSTART"])
            
            if isinstance(start, datetime):
                rset = rruleset()
                info = ""
                loc = ""

                if "SUMMARY" in ev:
                    found += 1
                    info =  ev["SUMMARY"].encode("utf-8")
                else:
                    continue # events ohne summary zeigen wir nicht an!

                #--------------------
                # coming soon!
                #if "LOCATION" in ev:
                #    loc = ev["LOCATION"]
                #else:
                #    loc = "Liebknechtstrasse 8"
                #--------------------

                if "RRULE" in ev: #recurrence
                    ical_dtstart = (ev.get("DTSTART")).to_ical()
                    ical_rrule = (ev.get('RRULE')).to_ical()
                    rset.rrule(rrulestr(ical_rrule, dtstart=parse(ical_dtstart)))

                    for e in rset.between(now, then):
                        data.append({
                            'datetime': e.strftime(fmt),
                            'datetime_sort': e.strftime(fmt),
                            'info': info,
                            'loc' : loc,
                        })

                    #TODO handling of EXDATE

                else: #no recurrence
                    if start < utc.localize(now) or start > utc.localize(then):
                        continue

                    data.append({
                        'datetime': start.astimezone(timezoneEF).strftime(fmt),
                        'datetime_sort': start.astimezone(timezoneEF).strftime(fmt),
                        'info': info,
                        'loc' : loc,
                    })

            #TODO handling of whole day events
            #if isinstance(start, date):

        data = sorted(data,
                      key=lambda k: time.mktime(datetime.strptime(
                          k['datetime_sort'], "%d.%m.%Y %H:%M").timetuple()))

        for ev in data:
            irc.msg(channel, "  %s - %s" % (ev['datetime'], ev['info']))

        if found == 0:
            irc.msg(channel, "No dates during the next week")

        f.close()
