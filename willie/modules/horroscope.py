"""
horroscope.py - Slap Module.

Copyright 2014, KeyserSoze

http://willie.dftba.net

"""

from horoscope import Horoscope
from willie.module import rule, priority, interval, commands
from willie.modules import unicode as uc

hs = {}


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
        result = hs[word.lower()]['horoscope']

    if result == '':
        return

    result = uc.encode(result)
    print(result)

    bot.say('Horroscope for ' + word.lower())
    splitmsg(bot, result)
    #bot.say(result)


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
            result = hs[sign.lower()]['horoscope']
        else:
            return

    if result == '':
        return

    result = uc.encode(result)
    bot.say('Horroscope for ' + sign.lower())
    splitmsg(bot, result)
    #bot.say(result)


@interval(60 * 60 * 6)
def update_hs(bot):
    """ internal function to update horroscopes every 6 hours."""

    hs['aries'] = Horoscope.get_todays_horoscope('Aries')
    hs['taurus'] = Horoscope.get_todays_horoscope('Taurus')
    hs['gemini'] = Horoscope.get_todays_horoscope('Gemini')
    hs['cancer'] = Horoscope.get_todays_horoscope('Cancer')
    hs['leo'] = Horoscope.get_todays_horoscope('Leo')
    hs['virgo'] = Horoscope.get_todays_horoscope('Virgo')
    hs['libra'] = Horoscope.get_todays_horoscope('Libra')
    hs['scorpio'] = Horoscope.get_todays_horoscope('Scorpio')
    hs['sagittarius'] = Horoscope.get_todays_horoscope('Sagittarius')
    hs['capricorn'] = Horoscope.get_todays_horoscope('Capricorn')
    hs['aquarius'] = Horoscope.get_todays_horoscope('Aquarius')
    hs['pisces'] = Horoscope.get_todays_horoscope('Pisces')


def splitmsg(bot, msg):
    words = msg.split()
    length = 0
    msg = ''
    for word in words:
        if len(word) + length > 300:
            bot.say(msg)
            msg = ''
            length = 0
        else:
            msg = msg + ' ' + word
            length = length + len(word)

    bot.say(msg)


def format_sign(sign):
    sign_info = hs[sign.lower()]['sunsign']
    ret = ''
    ret = 'Sign: ' + sign_info['sanskrit_name'] + ', '
    ret = ret + 'Meaning: ' + sign_info['meaning_of_name'] + ', '
    ret = ret + 'Lord: ' + sign_info['lord'] + ', '
    ret = ret + 'Lucky Color: ' + sign_info['lucky_color'] + ', '
    ret = ret + 'Lucky Day: ' + sign_info['lucky_day'] + ', '
    ret = ret + 'Lucky Number: ' + sign_info['lucky_number'] + '.'
    return ret
