# coding=utf8
"""
seen.py - Willie Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2012, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""

from willie import web
from willie.module import commands, rule, priority
import re

@commands('fd')
def fucking_dinner(bot, trigger):
    txt = trigger.group(2)
    url = 'http://www.whatthefuckshouldimakefordinner.com'
    if txt == '-v':
        url = 'http://whatthefuckshouldimakefordinner.com/veg.php'
    page = web.decode(web.get(url))
    re_mark = re.compile('<dt><a href="(.*?)" target="_blank">(.*?)</a></dt>')
    results = re_mark.findall(page)
    if results:
        bot.say("WHY DON'T YOU EAT SOME FUCKING: " + results[0][1] +
                  " HERE IS THE RECIPE: " + results[0][0])
    else:
        bot.say("I DON'T FUCKING KNOW, EAT PIZZA.")

