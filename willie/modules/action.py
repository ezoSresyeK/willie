# coding=utf8
"""
action.py - Willie action module
Copyright 2014 llmII
Licensed under MIT license
"""
from __future__ import unicode_literals

import re
import random
from willie.module import commands, rule, priority
from willie.config import ConfigurationError
from willie import db
from willie.modules import unicode as uc

ocommands = {}
ocommands['name'] = 'commands'
ocommands['id'] = 'id'
ocommands['cols'] = ['id', 'command']

actions = {}
actions['id'] = 'id'
actions['cols'] = ['id', 'command', 'safe']

safe = {}
safe['name'] = 'safe'
safe['id'] = 'id'
safe['cols'] = ['id', 'channel']

blocked = {}
blocked['name'] = 'blocked'
blocked['id'] = 'channel'
blocked['cols'] = ['channel', 'command']

inventory = {}
inventory['name'] = 'inventory'
inventory['id'] = 'id'
inventory['cols'] = ['id', 'item']

required = [ocommands, safe, blocked, inventory]

"""
table commands; id, command
table $action; id, actions, safe
table safe; id, channel
table blocked; channel, command
table inventory; id, item
"""

def check_db(bot):
    ret = True
    if not bot.db:
        raise ConfigurationError("Database not set up, or unavailable")
    for each in required:
        try:
            if not bot.db.check_table(each['name'], each['cols'], each['id']):
                bot.db.add_table(each['name'], each['cols'], each['id'])
                ret = False
        except:
            continue
    return ret

def check_action(bot, action):
    if not bot.db.check_table(action, actions['cols'], actions['id']):
        return False
    return True

def create_action(bot, action):
    if not bot.db.check_table(action, actions['cols'], actions['id']):
        bot.db.add_table(action, actions['cols'], actions['id'])
        return False
    return True


def check_command(bot, command):
    if not bot.db.commands.contains(command, 'command'):
        return False
    return True

def create_command(bot, command):
    if not bot.db.commands.contains(command, 'command'):
        cadd = {}
        cadd['command'] = command
        bot.db.commands.update(str(bot.db.commands.size() + 1), cadd)
    return True

def check_blocked(bot, chan, command):
    if chan in bot.db.blocked:
        if command in (bot.db.blocked.get('blocked', ['command'])[1].split(',')):
            return True
    return False


@rule('(.*)')
def act(bot, trigger):
    text = trigger.group().split()
    if len(text) < 2: return
    check_db(bot)

    try:
        if not text[0][0] == '.': return
    except:
        return

    com = text[0][1:]
    nick = text[1]
    item = str()

    if len(text) > 2:
        item = text[2]

    try:
        if not (check_command(bot, com) or check_action(bot, com)):
            return
    except:
        return

    safe = False

    if bot.db.safe.contains(trigger.sender.replace("'", "''"), 'channel'):
        safe = True

    bcoms = list()
    if bot.db.blocked.contains(trigger.sender.replace("'","''"), 'channel'):
        bcoms = bot.db.blocked.get(trigger.sender.replace("'", "''"), ['command'])[0].split(',')

    for block in bcoms:
        if block == com:
            return

    cstr = str()

    if getattr(bot.db, com.replace("'", "''")).size() == 0:
        return

    if safe:
        try:
            cstrs = getattr(bot.db, com.replace("'", "''")).get('yes', ['command'], 'safe')
            cstr = random.choice(cstrs)
        except:
            return
    else:
        rint = random.randint(1, getattr(bot.db, com.replace("'", "''")).size())
        cstr = getattr(bot.db, com.replace("'", "''")).get(str(rint), ['command'])[0]

    if not item:
        try:
            rint = random.randint(0, bot.db.inventory.size() - 1)
            item = bot.db.inventory.get(str(rint), 'item')
        except:
            item = 'bannana'


    cstr = cstr.replace('$nick', nick).replace('$sender', trigger.nick).replace('$item', item)

    bot.write(['PRIVMSG', trigger.sender, ' :\x01ACTION', cstr, '\x01'])

@commands('aact')
def add_act(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    if len(text) < 2 or not text[1].startswith('!'): return

    acts = text[1][1:].replace("'", "''")
    acstr = ' '.join(text[2:])

    check_db(bot)
    if not check_command(bot, acts):
        create_command(bot, acts)
    if not check_action(bot, acts):
        create_action( bot, acts)

    aact = {}
    aact['command'] = acstr.replace("'", "''")
    aact['safe'] = 'no'
    if not getattr(bot.db, acts).contains(acstr.replace("'", "''"), 'command'):
        getattr(bot.db, acts).update(str(getattr(bot.db, acts).size() + 1), aact)

    bot.say("added command: %s ;%s" % (acts, acstr))

@commands('ract')
def rm_act(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    if len(text) >= 2 and text[1].startswith('!') and check_action(bot, text[1][1:]):
        for each in text[2:]:
            try:
                getattr(bot.db, text[1][1:]).delete(each)
            except:
                continue

@commands('lact')
def list_act(bot, trigger):
    text = trigger.group().split()
    if len(text) == 1:
        clist = list()
        for key in bot.db.commands.keys('id'):
            clist.append(bot.db.commands.get(str(key[0]), ['command'], 'id')[0])
            if len(clist) == 20:
                bot.msg(trigger.nick, 'commands: ' + ', '.join(clist))
                del clist[:]
        bot.msg(trigger.nick, 'commands: ' + ', '.join(clist))
        return

    if not trigger.admin: return
    for each in text[1:]:
        if each.startswith('!') and check_action(bot, each[1:]):
            bot.say("\n")
            bot.say("act: %s, contains:" % (each[1:]))
            for key in getattr(bot.db, each[1:]).keys('id'):
                act = getattr(bot.db, each[1:]).get(str(key[0]), ['command', 'safe'], 'id')
                bot.say("act id: %s, safe: %s" % (key[0], act[1]))
                bot.say("%s" % (act[0]))

@commands('ainv')
def add_inv(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    if len(text) < 2: return
    check_db(bot)

    for each in text[1:]:
        inv = {}
        inv['item'] = each.replace("'", "''")
        if not bot.db.inventory.contains(inv['item'], 'item'):
            bot.db.inventory.update(str(bot.db.inventory.size()), inv)

@commands('rinv')
def rm_inv(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    if len(text) >= 2:
        for each in text[1:]:
            try:
                bot.db.inventory.delete(each)
            except:
                continue

@commands('linv')
def list_inv(bot, trigger):
    if not trigger.admin: return
    for key in bot.db.inventory.keys('id'):
        item = bot.db.inventory.get(str(key[0]), ['item'])
        bot.say("item id: %s, item: %s" % (key[0], item[0]))

@commands('ssafe') # safe; id, channel
def set_safe(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    if len(text) < 2: return
    check_db(bot)

    for each in text[1:]:
        if not each.startswith('#'): continue
        safe = {}
        safe['channel'] = each.replace("'", "''")
        if not bot.db.safe.contains(safe['channel'], 'channel'):
            bot.db.safe.update(str(bot.db.safe.size() + 1), safe)

@commands('rsafe')
def set_unsafe(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    if len(text) >= 2:
        for each in text[1:]:
            try:
                bot.db.safe.delete(each)
            except:
                continue

@commands('lsafe')
def list_safe(bot, trigger):
    if not trigger.admin: return
    for key in bot.db.safe.keys('id'):
        chan = bot.db.safe.get(str(key[0]), ['channel'])
        bot.say("%s is safe" % chan)

#table blocked; channel, command
@commands('bchan')
def block_chan(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    if len(text) < 2: return
    check_db(bot)

    for each in text[1:]:
        if not each.startswith('#'):
            continue

        chan = each.split(',')[0]
        coms = each.split(',')[1:]
        pcoms = list()
        if bot.db.blocked.contains(chan, 'channel'):
            pcoms = bot.db.blocked.get(chan, ['command'], 'channel')[0].split(',')

        acoms = list()
        if pcoms:
            acoms = pcoms[0].split(',')
        else:
            acoms = pcoms

        for com in coms:
            if not (com in acoms):
                acoms.append(com.replace("'", "''"))

        fcoms = {}
        fcoms['command'] = ','.join(acoms)
        bot.db.blocked.update(chan.replace("'", "''"), fcoms)

@commands('ubchan')
def rmblock_chan(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    chan = text[1].replace("'", "''")

    if not chan.startswith('#'):
        return

    if not bot.db.blocked.contains(chan):
        return

    bot.db.blocked.delete(chan)

@commands('lbchan')
def list_block_chan(bot, trigger):
    if not trigger.admin: return
    text = trigger.group().split()
    if not text[1].startswith('#'):
        return

    if not bot.db.blocked.contains(text[1]):
        return

    row = bot.db.blocked.get(text[1].replace("'", "''"), ['command'])[0]
    for each in row.split(','):
        bot.say("%s is blocked in %s" % (each, text[1]))
