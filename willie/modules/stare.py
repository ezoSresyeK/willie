"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://willie.dftba.net
"""

import random
from willie.module import commands

@commands('stare', 'stares')
def stare(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'): return

    if stare_avoid():
        if text[1] == bot.nick:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick
            else:
                text[1] = 'herself'

        if text[1] in bot.config.admins:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick

    text.insert(2, trigger.nick)

    verb = stare_get_verb(stare_safe(trigger.sender), text)
    action = random.choice(verb)
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', action,
               '\x01'])


def stare_safe(word):
    stare_safe_chans = ['#TheFoxesDen']
    #return any(word in s for s in stare_safe_chans)
    return False

def stare_avoid():
    return True

def stare_get_verb(stare_safe, text):
    if stare_safe:
        return [
            text[2] + ' stares into ' + text[1] +'\'s eyes deeply, losing themself in their gaze.',
            'pokes ' + text[1] + ' eyes out with ' + text[2] + '\'s stare' ]
    else:
        return [
            text[2] + ' stares into ' + text[1] +'\'s eyes deeply, losing themself in their gaze.',
            'pokes ' + text[1] + ' eyes out with ' + text[2] + '\'s stare' ]
