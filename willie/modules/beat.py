"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://willie.dftba.net
"""

import random
from willie.module import commands

@commands('beat', 'beats')
def beat(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'): return

    if beat_avoid():
        if text[1] == bot.nick:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick
            else:
                text[1] = 'herself'

        if text[1] in bot.config.admins:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick

    text.insert(2, trigger.nick)

    verb = beat_get_verb(beat_safe(trigger.sender), text)
    action = random.choice(verb)
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', action,
               '\x01'])


def beat_safe(word):
    beat_safe_chans = ['#TheFoxesDen']
    #return any(word in s for s in beat_safe_chans)
    return False

def beat_avoid():
    return True

def beat_get_verb(beat_safe, text):
    if beat_safe:
        return [
            'beats the shit outa ' + text[1] + ' with an iron pipe afterwards ramming it up their ass as a tempie check'
        ]
    else:
        return [
            'beats the shit outa ' + text[1] + ' with an iron pipe afterwards ramming it up their ass as a tempie check'
        ]
