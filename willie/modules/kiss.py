"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://willie.dftba.net
"""

import random
from willie.module import commands

@commands('kiss', 'kisses')
def kiss(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'): return

    if kiss_avoid():
        if text[1] == bot.nick:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick
            else:
                text[1] = 'herself'

        if text[1] in bot.config.admins:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick

    text.insert(2, trigger.nick)
    verb = kiss_get_verb(kiss_safe(trigger.sender), text)
    action = random.choice(verb)
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', action,
               '\x01'])


def kiss_safe(word):
    kiss_safe_chans = ['#TheFoxesDen']
    #return any(word in s for s in kiss_safe_chans)
    return False

def kiss_avoid():
    return False

def kiss_get_verb(kiss_safe, text):
    if kiss_safe:
        return [
            'on behalf of ' + text[2] + ' kisses ' + text[1] + ' gently touching her lips to theirs, licking their lips before pulling away'
        ]
    else:
        return [
            'on behalf of ' + text[2] + ' kisses ' + text[1] + ' gently touching her lips to theirs, licking their lips before pulling away'
        ]
