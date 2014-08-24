"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://willie.dftba.net
"""

import random
from willie.module import commands

@commands('spank', 'spanks')
def spank(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'): return

    if text[1] == bot.nick:
        if (trigger.nick not in bot.config.admins):
            text[1] = trigger.nick
        else:
            text[1] = 'herself'

    if text[1] in bot.config.admins:
        if (trigger.nick not in bot.config.admins):
            text[1] = trigger.nick

    verb = spank_get_verb(spank_safe(trigger.sender), text)
    action = random.choice(verb)
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', action,
               '\x01'])


def spank_safe(word):
    spank_safe_chans = ['#TheFoxesDen']
    return any(word in s for s in spank_safe_chans)

def spank_get_verb(spank_safe, text):
    if spank_safe:
        return [
            'spanks ' + text[1] + ' till their tongue falls out of their head',
            'bends ' + text[1] + ' over her leg and beats them violently. ' + text[1] + ' walks away barely able to sit welps branding their bum',
            'spanks ' + text[1]  + ' so hard their teeth fall out in shock',
            'bends ' + text[1] + ' over her leg and swiftly removes their pants giving them a few firm licks to the bum leaving behind a red hand print',
            'grabs a paddle and spanks ' + text[1] + ' all over' ]
    else:
        return [
            'spanks ' + text[1] + ' till their tongue falls out of their head',
            'spanks ' + text[1] + ' so lovingly they cum in their pants',
            'bends ' + text[1] + ' over her leg and beats them violently. ' + text[1] + ' walks away barely able to sit welps branding their bum',
            'spanks ' + text[1] + ' so hard their teeth fall out in shock',
            'bends ' + text[1] + ' over her leg and swiftly removes their pants giving them a few firm licks to the bum leaving behind a red hand print',
            'grabs a paddle and spanks ' + text[1] + ' all over' ]
