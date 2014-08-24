"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://willie.dftba.net
"""

import random
from willie.module import commands

@commands('torture', 'tortures')
def torture(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'): return

    if torture_avoid():
        if text[1] == bot.nick:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick
            else:
                text[1] = 'herself'

        if text[1] in bot.config.admins:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick

    text.insert(2, trigger.nick)

    verb = torture_get_verb(torture_safe(trigger.sender), text)
    action = random.choice(verb)
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', action,
               '\x01'])


def torture_safe(word):
    torture_safe_chans = ['#TheFoxesDen']
    #return any(word in s for s in torture_safe_chans)
    return False

def torture_avoid():
    return True

def torture_get_verb(torture_safe, text):
    if torture_safe:
        return [
            'takes out a fork... approaching ' + text[1] + ' proceeds to ram the fork up their godforsaken nose',
            'puts ' + text[1] + ' in a hazmat suite farting inside it before sealing it up tight and running a couple meters away, lighting a cigar and puffing for a few minutes watching them suffer in stench'
        ]
    else:
        return [
            'takes out a fork... approaching ' + text[1] + ' proceeds to ram the fork up their godforsaken nose',
            'puts ' + text[1] + ' in a hazmat suite farting inside it before sealing it up tight and running a couple meters away, lighting a cigar and puffing for a few minutes watching them suffer in stench'
        ]
