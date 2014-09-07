#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from plugins.plugin import Plugin
from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from icalendar      import Calendar, Event
from icalendar.prop import vDDDTypes
from datetime       import datetime, timedelta
from pytz           import utc, timezone
from urllib         import urlopen

class dates(Plugin):
    def __init__(self):
        try:
            BYTEBOT_PLUGIN_CONFIG['dates'].keys()
        except Exception:
            raise Exception('ERROR: Plugin "dates" is missing configuration!')

        pass

    def registerCommand(self, irc):
        """Registers the '!dates' command to the global command list
        
        irc:        An instance of the bytebot. Will be passed by the plugin loader
        """

        irc.registerCommand('!dates', 'Shows the next planned dates')

    def onPrivmsg(self, irc, msg, channel, user):
        """Looks for a '!dates' command in messages posted to the channel and 
        returns a list of dates within the next week.

        irc:        An instance of the bytebot. Will be passed by the plugin loader
        msg:        The msg sent to the channel
        channel:    The channels name
        user:       The user who sent the message
        """

        if msg.find('!dates') == -1:
            return

        f     = urlopen(BYTEBOT_PLUGIN_CONFIG['dates']['url'])
        cal   = Calendar.from_ical(f.read())
        now   = datetime.now(utc).replace(hour=0, minute=0, second=0, microsecond=0)
        nweek = now + timedelta(weeks=1)
        found = 0

        for ev in cal.walk():
            if ev.name != 'VEVENT':
                continue

            if len(str(vDDDTypes.from_ical(ev.get('dtstart'))).split(' ')) > 1:
                start = vDDDTypes.from_ical(ev.get('dtstart')).replace(tzinfo=utc)
                if start < now or start > nweek: continue
            else:
                start = vDDDTypes.from_ical(ev.get('dtstart'))
                if start < now.date() or start > nweek.date(): continue

            found += 1

            fmt = "%d.%m.%Y %H:%M"
            timezoneEF = timezone('Europe/Berlin')

            #convert utc datetime to local timezone
            dt_utc = ev.get('dtstart').dt
            dt_local = dt_utc.astimezone(timezoneEF)
            dt_str = dt_local.strftime(fmt)

            #encode unicode string in utf8
            ucode_event_str = ev.get('summary')
            utf8_event_str = ucode_event_str.encode("utf-8")

            irc.msg(channel, "  %s - %s" % 
                        (dt_str,
                        utf8_event_str)
                   )

        if found == 0:
            irc.msg(channel, "No dates during the next week")

        f.close()
