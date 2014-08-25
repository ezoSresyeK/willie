# coding=utf8
"""
fuckingweather.py - Willie module for The Fucking Weather
Copyright 2013 Michael Yanovich
Copyright 2013 Edward Powell

Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from willie.module import commands, rate, priority, NOLIMIT
from willie import web
import re


@commands('fucking_weather', 'fw')
@rate(30)
@priority('low')
def fucking_weather(bot, trigger):
    text = trigger.group(2)
    if not text:
        bot.reply("INVALID FUCKING PLACE. PLEASE ENTER A FUCKING ZIP CODE, OR A FUCKING CITY-STATE PAIR.")
        return
    text = web.quote(text)
    try:
        page = web.decode(web.get("http://thefuckingweather.com/?where=%s" % (text)))
    except:
        bot.reply("I COULDN'T ACCESS THE FUCKING SITE.")
        return

    re_mark = re.compile('<p class="remark">(.*?)</p>')
    re_temp = re.compile('<span class="temperature" tempf="\S+">(\S+)</span>')
    re_condition = re.compile('<p class="large specialCondition">(.*?)</p>')
    re_flavor = re.compile('<p class="flavor">(.*?)</p>')
    re_location = re.compile('<span id="locationDisplaySpan" class="small">(.*?)</span>')

    temps = re_temp.findall(page)
    remarks = re_mark.findall(page)
    conditions = re_condition.findall(page)
    flavor = re_flavor.findall(page)
    new_location = re_location.findall(page)

    response = str()

    if new_location and new_location[0]:
        response += new_location[0] + ': '

    if temps:
        tempf = float(temps[0])
        tempc = (tempf - 32.0) * (5 / 9.0)
        response += u'%.1f°F?! %.1f°C?! ' % (tempf, tempc)

    if remarks:
        response += remarks[0]
    else:
        response += "THE FUCKING SITE DOESN'T CONTAIN ANY FUCKING INFORMATION ABOUT THE FUCKING WEATHER FOR THE PROVIDED FUCKING LOCATION."

    if conditions:
        response += ' ' + conditions[0]

    if flavor:
        response += ' -- ' + flavor[0].replace('  ', ' ')

    bot.reply(response)

