"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://willie.dftba.net
"""

import random
from willie.module import commands

@commands('punch', 'punches')
def punch(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'): return

    if punch_avoid():
        if text[1] == bot.nick:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick
            else:
                text[1] = 'herself'

        if text[1] in bot.config.admins:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick

    text.insert(2, trigger.nick)

    verb = punch_get_verb(punch_safe(trigger.sender), text)
    action = random.choice(verb)
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', action,
               '\x01'])


def punch_safe(word):
    punch_safe_chans = ['#TheFoxesDen']
    #return any(word in s for s in punch_safe_chans)
    return False

def punch_avoid():
    return True

def punch_get_verb(punch_safe, text):
    if punch_safe:
        return [
            'punches ' + text[1] + ' with ' + text[2] + '\'s fist',
            'punches ' + text[1] + ' with a big purple dildo in the face while holding a bucket of rotten fish under ' + text[1] + '\'s nose'
        ]
    else:
        return [
            'punches ' + text[1] + ' with ' + text[2] + '\'s fist',
            'punches ' + text[1] + ' with a big purple dildo in the face while holding a bucket of rotten fish under ' + text[1] + '\'s nose'
        ]
