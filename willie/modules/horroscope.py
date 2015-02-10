"""
horroscope.py - Slap Module.

Copyright 2014, KeyserSoze

http://willie.dftba.net

"""

from bs4 import BeautifulSoup
import requests
import re
from willie.module import rule, priority, interval, commands
from willie.modules import unicode as uc

hs = {}

base_url = "http://horoscope.com/"
url = "http://my.horoscope.com/astrology/free-daily-horoscope-{}.html"

sign_list = {1: "Aries",
             2: "Taurus",
             3: "Gemini",
             4: "Cancer",
             5: "Leo",
             6: "Virgo",
             7: "Libra",
             8: "Scorpio",
             9: "Sagittarius",
             10: "Capricorn",
             11: "Aquarius",
             12: "Pisces"}


def horoscoper(sign):
    """Return horoscope info."""
    r = requests.get(url.format(sign_list[sign]))
    soup = BeautifulSoup(r.content)

    # data extraction
    reading = soup.find_all("div", {"class": "fontdef1"})[0].text
    date = soup.find_all(id="advert")[1].text
    lucky_numbers = soup.find_all("div", {"class": "fontultrasma10"})[2].text
    numbers = re.sub("[^0-9, ]", "", (soup.find_all("b")[12].text))

    return {
        "read": reading,
        "date": date,
        "lucky": lucky_numbers,
        "numbers": numbers}


@rule('(.*)')
@priority('low')
def horroscope(bot, trigger):
    """ Get horroscopes."""

    result = unicode()
    text = trigger.group().split()
    try:
        if not (text[0][0] == '.' or text[0][0] == '!'):
            return
        word = text[0][1:]
    except:
        return

    if len(hs.keys()) == 0:
        update_hs(bot)

    if word.lower() in hs.keys():
        result = hs[word.lower()]

    if result == '':
        return

    for line in result:
        bot.say(uc.encode(line))


@commands('hs')
def hs_expanded(bot, trigger):
    """ Offer extended horoscope functionality.

    Ex:
    .hs view libra (show's libra horroscope)
    .hs info libra ('show's libra info)

    """

    text = trigger.group().split()

    word = ''
    sign = ''
    result = unicode()

    if len(text) < 2:
        return

    if len(text) == 2:
        word = 'view'
        sign = text[1]
    else:
        word = text[1]
        sign = text[2]

    if len(hs.keys()) == 0:
        update_hs(bot)

    if sign.lower() in hs.keys():
        if word == 'info':
            result = ''
            #result = format_sign(sign)
        elif word == 'view':
            result = hs[sign.lower()]
        else:
            return

    if result == '':
        return

    for line in result:
        bot.say(uc.encode(line))


@interval(60 * 60 * 6)
def update_hs(bot):
    """ internal function to update horroscopes every 6 hours."""

    hs['aries'] = format_hs(horoscoper(1))
    hs['taurus'] = format_hs(horoscoper(2))
    hs['gemini'] = format_hs(horoscoper(3))
    hs['cancer'] = format_hs(horoscoper(4))
    hs['leo'] = format_hs(horoscoper(5))
    hs['virgo'] = format_hs(horoscoper(6))
    hs['libra'] = format_hs(horoscoper(7))
    hs['scorpio'] = format_hs(horoscoper(8))
    hs['sagittarius'] = format_hs(horoscoper(9))
    hs['capricorn'] = format_hs(horoscoper(10))
    hs['aquarius'] = format_hs(horoscoper(11))
    hs['pisces'] = format_hs(horoscoper(12))


def splitmsg(msg):
    """Split the message. Returns array."""

    words = msg.split()
    length = 0
    msg = words[0]
    lines = []
    for word in words[1:]:
        if len(word) + length > 300:
            lines.append(msg)
            msg = ''
            length = 0
            msg = word
        else:
            msg = msg + ' ' + word
            length = length + len(word)

    lines.append(msg)
    return lines


def format_hs(horo):
    "Format the horoscope."

    lines = []
#    lines.append(horo['date'])
    lines.extend(splitmsg(horo['read']))
    lines.append(horo['lucky'])
    lines.append(horo['numbers'])
    return lines
