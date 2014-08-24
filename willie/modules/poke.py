"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://willie.dftba.net
"""

import random
from willie.module import commands

@commands('poke', 'pokes')
def poke(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'): return

    if poke_avoid():
        if text[1] == bot.nick:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick
            else:
                text[1] = 'herself'

        if text[1] in bot.config.admins:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick

    text.insert(2, trigger.nick)

    verb = poke_get_verb(poke_safe(trigger.sender), text)
    action = random.choice(verb)
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', action,
               '\x01'])


def poke_safe(word):
    poke_safe_chans = ['#TheFoxesDen']
    #return any(word in s for s in poke_safe_chans)
    return False

def poke_avoid():
    return False

def poke_get_verb(poke_safe, text):
    if poke_safe:
        return [
            'pokes ' + text[1] + ' in the eye',
            'pokes ' + text[1] + ' playfully',
            'spread em wide ' + text[1] + '. The poker is coming',
            'spread em wide ' + text[1] + '. ' + text[2] + ' is coming to poke you',
            'pokes ' + text[1] + ' on behalf of ' + text[2]
        ]
    else:
        return [
            'pokes ' + text[1] + ' in the eye',
            'pokes ' + text[1] + ' playfully',
            'spread em wide ' + text[1] + '. The poker is coming',
            'spread em wide ' + text[1] + '. ' + text[2] + ' is coming to poke you',
            'pokes ' + text[1] + ' on behalf of ' + text[2]
        ]
