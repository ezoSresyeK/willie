# coding=utf8
"""
seen.py - Willie Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2012, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

import time
import datetime
import random
import re
from willie.tools import Nick, get_timezone, format_time
from willie.module import commands, rule, priority
from cleverbot import Cleverbot

mycb = Cleverbot()

@rule('(.*)')
@priority('high')
def chat(bot, trigger):
    txt = str()
    channel = trigger.sender
    talk = True
    pm = False
    replace = "jen"
    samount = random.randint(0,3)
    if trigger.groups():
        txt = trigger.groups()
    else:
        txt = trigger.bytes
    txt = txt[0]
    if txt == "": return
    if txt[0] == '.': return
    if txt.find(bot.config.nick) == -1: talk = False
    if txt.find("mafalda") > -1 or random.randint(0, 10000) < 5:
        talk = True
    if random.randint(0, 10000) < 5:
        talk = False
    if not talk: return
    if not channel.startswith("#"): pm = True
    if txt.find(bot.config.nick) > -1:
        replace = bot.config.nick

    time.sleep(samount)
    msgo = str()
    try:
        msgo = mycb.ask(txt)
    except:
        return
    response = re.sub('(?i)cleverbot', bot.config.nick, msgo)
    if msgo:
        if pm:
            bot.say(response)
        else:
            delim = random.choice((',', ':'))
            msg = '%s' % (response)
            if random.random() <= 0.25:
                msg = trigger.nick + delim + ' ' + msg
            if random.random() < 0.09:
                chat(bot, trigger)
            bot.say(msg)
