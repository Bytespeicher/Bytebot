from irc3.plugins.command import command

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
import json
import aiohttp

from geopy.geocoders import Nominatim
from geopy.distance import vincenty

@command(permission="view")
@asyncio.coroutine
def fuel(bot, mask, target, args):
    """Show the current fuel for Erfurt

        %%fuel [<city> <value> <type>]...
    """
    config = BYTEBOT_PLUGIN_CONFIG['fuel']
    sort_type = 'all'
    sort_value = 'dist'
    lat = config['lat']
    lng = config['lng']
    fuel_types = ['e5','e10', 'diesel', 'all']

    if config['api_key'] == "your_apikey":
        return "I don't have your api key!"

    if '<city>' not in args or len(args['<city>']) < 1:
        bot.log.info('Fetching fuel info for Erfurt')
        lat = config['lat']
        lng = config['lng']

    else:
        if " ".join(args['<city>']) == 'sort':
            bot.log.info('Fetching fuel info for Erfurt')

            lat = config['lat']
            lng = config['lng']

            if '<value>' not in args or len(args['<value>']) < 1:
                sort_type = 'all'
                sort_value = 'dist'
            else:
                sort_type = " ".join(args['<value>'])
                sort_value = 'price'

        else:
            if " ".join(args['<city>']) == 'help':
                bot.log.info('Printing some Help')

                cmd = '!'
                bot.privmsg(target, '( ͡° ͜ʖ ͡°)')
                bot.privmsg(target, 'Example commands:')
                bot.privmsg(target, cmd + 'fuel')
                bot.privmsg(target, cmd + 'fuel help')
                bot.privmsg(target, cmd + 'fuel sort <fuel>')
                bot.privmsg(target, cmd + 'fuel <place>')
                bot.privmsg(target, cmd + 'fuel <place> sort <fuel>')

                return ""

            else:
                bot.log.info('Fetching fuel info for ' + str(" ".join(args['<city>'])))

                geolocator = Nominatim()
                location = geolocator.geocode(" ".join(args['<city>']))
                lat = location.latitude
                lng = location.longitude

                if " ".join(args['<value>']) == 'sort':
                    if '<type>' not in args or len(args['<type>']) < 1:
                        sort_type = 'all'
                        sort_value = 'dist'
                    else:
                        sort_type = " ".join(args['<type>'])
                        sort_value = 'price'

    if not sort_type in fuel_types:
        return "Not supported fuel."

    try:
        url = "https://creativecommons.tankerkoenig.de/json/list.php?" + \
            "lat=" + str(lat) + \
            "&lng=" + str(lng) + \
            "&rad=" + str(config['rad']) + \
            "&sort=" + str(sort_value) + \
            "&type=" + str(sort_type) + \
            "&apikey=" + str(config['api_key'])

        with aiohttp.Timeout(10):
            with aiohttp.ClientSession(loop=bot.loop) as session:
                resp = yield from session.get(url)
                if resp.status != 200:
                    bot.privmsg(target, "Error while retrieving station list")
                    raise Exception()
                r = yield from resp.read()

        data = json.loads(r.decode('utf-8'))

        messages = []
        for x in range(len(data['stations'])):
            brand = data[u'stations'][x][u"brand"]
            station_id = data['stations'][x][u"id"]
            postCode = data['stations'][x][u"postCode"]

            bot.log.info('Fetching fuel info for Erfurt station ' +
                str(station_id))
            url = "https://creativecommons.tankerkoenig.de/json/detail.php?" + \
                "id=" + station_id + \
                "&apikey=" + str(config['api_key'])

            with aiohttp.Timeout(10):
                with aiohttp.ClientSession(loop=bot.loop) as session:
                    resp = yield from session.get(url)
                    if resp.status != 200:
                        bot.privmsg(target, "Error while retrieving fuel data")
                        raise Exception()
                    r = yield from resp.read()

            details = json.loads(r.decode('utf-8'))

            e5 = str(details['station']['e5'])
            e10 = str(details['station']['e10'])
            diesel = str(details['station']['diesel'])

            dist = u"{:0.2} km".format(vincenty((details['station']['lat'], details['station']['lng']),
                (lat, lng)).meters/1000)

            if brand == '':
                brand = 'GLOBUS'

            print_str = \
                u"   {:20}".format(brand + ', ' + str(postCode) + ': ') + \
                u"{:5}  ".format(e5) + \
                u"{:5}  ".format(e10) + \
                u"{:5}  ".format(diesel) + \
                u"{:5}  ".format(dist)

            messages.append(print_str)

        headline = u"{:23}".format('fuel prices:') + \
            u"{:6} ".format('e5') + \
            u"{:6} ".format('e10') + \
            u"{:6} ".format('diesel') + \
            u"{:6} ".format('dist')

        if len(messages) >0:
            bot.privmsg(target, headline)
            for m in messages:
                bot.privmsg(target, m)
        else:
            return "No fuel data found!"

    except KeyError:
        bot.privmsg(target, "Error while retrieving fuel data")
        raise Exception()
