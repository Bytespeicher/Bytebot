from irc3.plugins.command import command

from bytebot_config import BYTEBOT_PLUGIN_CONFIG
from irc3 import asyncio
import json
import aiohttp

from geopy.geocoders import Nominatim

@command(permission="view")
@asyncio.coroutine
def fuel(bot, mask, target, args):
    """Show the current fuel for Erfurt

        %%fuel [<city>]...
    """
    config = BYTEBOT_PLUGIN_CONFIG['fuel']

    if config['api_key'] == "your_apikey":
        return "I don't have your api key!"

    if '<city>' not in args or len(args['<city>']) < 1:
        lat = config['lat']
        lng = config['lng']
        bot.log.info('Fetching fuel info for Erfurt')
    else:
        geolocator = Nominatim()
        location = geolocator.geocode(" ".join(args['<city>']))

        lat = location.latitude
        lng = location.longitude
        bot.log.info('Fetching fuel info for ' + str(" ".join(args['<city>'])))
        print((lat, lng))

    try:
        url = "https://creativecommons.tankerkoenig.de/json/list.php?" + \
            "lat=" + str(lat) + \
            "&lng=" + str(lng) + \
            "&rad=" + config['rad'] + \
            "&sort=dist" + \
            "&type=e5&apikey=" + \
            str(config['api_key'])

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

            if brand == '':
                brand = 'GLOBUS'

            print_str = \
                u"   {:20}".format(brand + ', ' + str(postCode) + ': ') + \
                u"{:5}  ".format(e5) + \
                u"{:5}  ".format(e10) + \
                u"{:5}  ".format(diesel)

            messages.append(print_str)

        headline = u"{:23}".format('fuel prices:') + \
            u"{:6} ".format('e5') + \
            u"{:6} ".format('e10') + \
            u"{:6} ".format('diesel')

        bot.privmsg(target, headline)
        for m in messages:
            bot.privmsg(target, m)

    except KeyError:
        bot.privmsg(target, "Error while retrieving fuel data")
        raise Exception()
