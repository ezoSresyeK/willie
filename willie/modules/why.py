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

whyuri = 'http://www.leonatkinson.com/random/index.php/rest.html?method=advice'
r_paragraph = re.compile(r'<quote>.*?</quote>')

@commands('why')
def why(bot, trigger):
    page = web.get(whyuri)
    paragraphs = r_paragraph.findall(page)
    line = re.sub(r'<[^>]*?>', '', unicode(paragraphs[0]))
    bot.say(line.lower().capitalize() + ".")
