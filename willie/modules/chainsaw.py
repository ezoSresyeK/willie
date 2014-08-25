"""
slap.py - Slap Module
Copyright 2009, Michael Yanovich, yanovich.net

http://willie.dftba.net
"""

import random
from willie.module import commands

@commands('chainsaw', 'chainsaws')
def chainsaw(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2 or text[1].startswith('#'): return

    if chainsaw_avoid():
        if text[1] == bot.nick:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick
            else:
                text[1] = 'herself'

        if text[1] in bot.config.admins:
            if (trigger.nick not in bot.config.admins):
                text[1] = trigger.nick

    text.insert(2, trigger.nick)

    verb = chainsaw_get_verb(chainsaw_safe(trigger.sender), text)
    action = random.choice(verb)
    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', action,
               '\x01'])


def chainsaw_safe(word):
    chainsaw_safe_chans = ['#TheFoxesDen']
    #return any(word in s for s in chainsaw_safe_chans)
    return False

def chainsaw_avoid():
    return True

def chainsaw_get_verb(chainsaw_safe, text):
    if chainsaw_safe:
        return [
            'smiles sweetly at ' + text[1] + ' taking out the chainsaw and slicing ' + text[1] + '\'s arms and legs off leaving only eyeballs behind, smiling deviantly at their horrific work'
        ]
    else:
        return [
            'smiles sweetly at ' + text[1] + ' taking out the chainsaw and slicing ' + text[1] + '\'s arms and legs off leaving only eyeballs behind, smiling deviantly at their horrific work'
        ]
