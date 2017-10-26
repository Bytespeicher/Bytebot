import re
import json

import irc3
import aiohttp

try:
    from clarifai.client import ClarifaiApi
except ImportError:
    ClarifaiApi = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# via http://stackoverflow.com/a/7160778/6729695
__URL_REGEX = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # flake8: noqa
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

__URL_KRZUS = "https://krz.us/api/v1/short"

__IMAGE_EXT = ("jpeg", "jpg", "gif", "png")


@irc3.event(irc3.rfc.PRIVMSG)
@irc3.asyncio.coroutine
def greetings(bot, mask, target, data=None, **kw):
    # log.msg("Shortening URL %s" % url)
    if bot.nick == mask.nick:
        return

    url = None
    for match in __URL_REGEX.finditer(data):
        url = match.group(0)
        break

    if not url:
        return

    """Load configuration"""
    config = bot.config.get(__name__, {})

    with aiohttp.Timeout(10):
        with aiohttp.ClientSession(loop=bot.loop) as session:
            headers = {"Content-Type": "application/json"}
            payload = {"url": url, "key": None}
            resp = yield from session.post(
                    __URL_KRZUS, data=json.dumps(payload), headers=headers)

            if resp.status != 200:
                raise Exception

            r = yield from resp.read()

    data = json.loads(r.decode('utf-8'))

    short = data.get("url_short")
    if not url:
        return

    desc = None
    if url.endswith(__IMAGE_EXT) and ClarifaiApi is not None:
        api = ClarifaiApi(
            config['clarifai_app_id'],
            config['clarifai_app_secret'])
        tags = api.tag_image_urls(url)

        if tags['status_code'] == "OK":
            ret = ', '.join(tags['results'][0]['result']['tag']['classes'])
            desc = "Tags: {}".format(ret)
    elif BeautifulSoup is not None:
        with aiohttp.Timeout(10):
            with aiohttp.ClientSession(loop=bot.loop) as session:
                resp = yield from session.get(url)
                if resp.status == 200:
                    r = yield from resp.read()
                    soup = BeautifulSoup(r, "html.parser")
                    title = soup.title.getText()
                    if len(title) > 60:
                        title = title[:60] + "…"
                    desc = "Title: {}".format(title)

    if desc:
        bot.privmsg(target, desc)
        bot.privmsg(target, "\tURL: {}".format(short))
    else:
        bot.privmsg(target, "URL: {}".format(short))
