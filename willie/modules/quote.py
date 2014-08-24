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
from willie.tools import Ddict, Nick, get_timezone, format_time
from willie.module import commands, rule, priority
from willie.modules import unicode as uc

@commands('addquote')
@priority('medium')
def addquote(bot, trigger):
    """adds quote to quotes
    .addquote (quote goes here)
    """
    if not trigger.admin: return
    text = trigger.group(2)
    if not text:
        return bot.say('No quote provided.')
    fn = open('quotes.txt', 'a')
    text = uc.encode(text)
    fn.write(text)
    fn.write('\n')
    fn.close()
    bot.reply('Quote added.')

@commands('quote')
@priority('medium')
def retrievequote(bot, trigger):
    """gets a quote from quotes
    .quote | random quote
    .quote (number) | get this number quote
    .quote (word) | get random quote with this word
    """
    text = trigger.group(2)
    try:
        fn = open('quotes.txt', 'r')
    except:
        return bot.reply('Please add a quote first.')

    lines = fn.readlines()
    if len(lines) < 1:
        return bot.reply('There are currently no quotes saved.')
    MAX = len(lines)
    fn.close()
    random.seed()
    randomized = True

    try:
        number = int(text)
        if number < 0:
            number = MAX - abs(number) + 1
        randomized = False
    except:
        number = random.randint(1, MAX)

    if not (0 <= number <= MAX):
        return bot.reply("I'm not sure which quote you'd like to see")

    if randomized and text:
        which = list()
        for linenumber, line in enumerate(lines):
            if uc.decode(line).find(text) > -1:
                which.append(linenumber)

        if which:
            number = random.choice(which)
            number = number + 1

    if lines:
        if number == 1:
            line = lines[0]
        elif number == 0:
            return bot.say('There is no "0th" quote!')
        else:
            line = lines[number - 1]
        bot.say('Quote %s of %s: ' % (number, MAX) + uc.decode(line))
    else:
        bot.reply('There are currently no quotes saved.')

@commands('rmquote')
@priority('medium')
def delquote(bot, trigger):
    """Delete's quote numbered
    .rmquote (number) | remove quote at index number
    """
    if not trigger.admin: return
    text = trigger.group(2)
    number = int()

    try:
        fn = open('quotes.txt', 'r')
    except:
        return bot.reply('No quotes to delete.')

    lines = fn.readlines()
    MAX = len(lines)
    fn.close()

    try:
        number = int(text)
    except:
        return bot.reply('Please enter a quote number to delete.')

    if number > 0:
        newlines = lines[:number - 1] + lines[number:]
    elif number == 0:
        return bot.reply('There is no "0th" quote!')
    elif number ==  -1:
        newlines = lines[:number]
    else:
        newlines = lines[:number] + lines[number + 1:]

    fn = open('quotes.txt', 'w')
    for line in newlines:
        txt = line
        if txt:
            fn.write(txt)
            if txt[-1] != '\n':
                fn.write('\n')
    fn.close()
    bot.reply('Succesfully deleted quote %s.' % (number))


