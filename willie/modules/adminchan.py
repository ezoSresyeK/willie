# coding=utf8
"""
adminchannel - Chan Management module.

Copyright 2014 - KeyserSoze
Licensed under MIT License

"""

from __future__ import unicode_literals

import re
import time
from willie.module import commands, priority, OP, rule, \
    event, interval
from willie.tools import Nick, WillieMemory
from willie.config import ConfigurationError
from willie.modules.whois import whois
from willie import formatting


gattr = {}
gattr['name'] = 'gattr'
gattr['id'] = 'usr'
gattr['cols'] = ['usr', 'attr']
bans = list()
protect = {}


def check_attr_db(bot):
    if not bot.db:
        raise ConfigurationError("Database not set up or unavail")
    if not bot.db.check_table(gattr['name'], gattr['cols'],
                              gattr['id']):
        bot.db.add_table(gattr['name'], gattr['cols'], gattr['id'])
    return


def display_help(bot, trigger):
    bot.msg(trigger.nick, 'Changes attributes - To use attr:')
    bot.msg(trigger.nick,
            '.attr [g,c] [user,chan] (channel) [+,-] [(AaOoVvpb),(vpo)]')
    bot.msg(trigger.nick,
            '[g,c] = global/chan, only >A can access g')
    bot.msg(trigger.nick,
            '[user,chan] = (as expected), selects on which you\
            wish to set attributes')
    bot.msg(trigger.nick,
            '(channel) channel on which user is to be set')
    bot.msg(trigger.nick,
            '[+/-] = add or remove flags')
    bot.msg(trigger.nick,
            '[(AaOoVvpb),(vpo)] = available flags to set,\
            former on users, latter on channels')
    bot.msg(trigger.nick, 'O = global owner, can do all attributes')
    bot.msg(trigger.nick, 'A = global admin, can not set +O\
            can set all other modes')
    bot.msg(trigger.nick, 'o = channel owner, can set flags for\
            apb on users')
    bot.msg(trigger.nick, 'a = chan admin, can set flags pb')
    bot.msg(trigger.nick, 'V = voice user in all channels')
    bot.msg(trigger.nick, 'v = voice user on current channel')
    bot.msg(trigger.nick, 'p = protect user from chan protect')
    bot.msg(trigger.nick, 'b = user is banned')
    bot.msg(trigger.nick, 'chan modes - only settable by users\
            with +O or +A or +o or +a:')
    bot.msg(trigger.nick, 'v = voice all on chan')
    bot.msg(trigger.nick, 'p = protect chan from flooding')
    bot.msg(trigger.nick, 'o = use services to get op')
    bot.msg(trigger.nick, 'for a list of users and access, do\
            .attr list [chan,user,global] (#chan,user)')


def setusr(bot, table, user, privs):
    oprivs = getusr(bot, table, user)
    nprivs = str()
    rprivs = str()

    if not privs[0] == '+':
        bot.say("the privs must start with +")
        return "Fail"

    if '-' not in privs:
        nprivs = privs
        rprivs = '*'
    else:
        nprivs = privs.split('-')[0]
        rprivs = privs.split('-')[1]

    for c in oprivs:
        if c not in rprivs:
            nprivs += c

    privs = {}
    privs['attr'] = sescapet(nprivs[1:])
    getattr(bot.db, sescapet(table).lower()).update(sescapet(user), privs)
    return "Set %s on %s" % (user, nprivs)


def setuattr(bot, table, user, text):
    attr = getuattr(bot, table, user)
    attr = {}
    attr['attr'] = text
    tbl = getattr(bot.db, sescapet(table).lower())
    tbl.update(sescapet(user), attr)


def getuattr(bot, table, user):
    if not bot.db.check_table(sescapet(table).lower(),
                              gattr['cols'], gattr['id']):
        bot.db.add_table(sescapet(table).lower(), gattr['cols'],
                         gattr['id'])
        return ""

    exit = True
    for key in getattr(bot.db, sescapet(table).lower()).keys('usr'):
        if key[0] == sescapet(user):
            exit = False
    if exit:
        return ""

    text = getattr(bot.db, sescapet(table).lower()).get(
        sescapet(user), ['attr'])
    return text[0]


def getusr(bot, table, user):
    if not bot.db.check_table(sescapet(table).lower(),
                              gattr['cols'], gattr['id']):
        bot.db.add_table(sescapet(table).lower(), gattr['cols'],
                         gattr['id'])
        return ""

    exit = True
    for key in getattr(bot.db, sescapet(table).lower()).keys('usr'):
        if key[0] == sescapet(user):
            exit = False
    if exit:
        return ""

    privs = getattr(bot.db, sescapet(table).lower()).get(
        sescapet(user), ['attr'])
    return privs[0]


def list_access(bot, trigger, text):
    if text[2] == 'chan':
        if not hascap(bot, text[3], trigger.nick, 'AaOo'):
            return

        chanattr = str()
        for key in getattr(bot.db, sescapet(text[3]).lower()).keys('usr'):
            if key[0] == '@':
                chanattr = getattr(bot.db, sescapet(text[3]).lower()).get(
                    key[0], ['attr'], 'usr')[0]
                continue
            privs = getattr(bot.db, sescapet(text[3]).lower()).get(key[0],
                                                                   ['attr'],
                                                                   'usr')
            bot.say("User %s: %s" % (key[0], privs[0]))
        if not (chanattr == ""):
            bot.say("Channel %s: %s" % (text[3], chanattr[0]))
    elif text[2] == 'global':
        if not hascap(bot, 'gattr', trigger.nick, 'AO'):
            return

        for key in getattr(bot.db, 'gattr').keys('usr'):
            privs = getattr(bot.db, 'gattr').get(key[0], ['attr'],
                                                 'usr')
            bot.say("Global %s: %s" % (key[0], privs[0]))
    elif text[2] == 'user':
        privs = getusr(bot, sescapet(trigger.sender).lower(),
                       sescapet(text[3]))
        bot.say('%s modes: %s' % (text[3], privs[0]))
        return
    elif text[2] == 'attr':
        privs = getuattr(bot, sescapet(trigger.sender).lower(),
                       sescapet(text[3]))
        bot.say('%s modes: %s' % (text[3], privs))
        return


def gset(bot, trigger, text):
    if not hascap(bot, 'gattr', trigger.nick, 'AO'):
        if not trigger.owner:
            return

    if not hascap(bot, 'gattr', trigger.nick, 'O'):
        if not trigger.owner:
            if 'O' in text[3]:
                return
    usr = text[2]
    privs = text[3]
    bot.say(setusr(bot, 'gattr', usr, privs))
    return


def cset(bot, trigger, text):
    if text[2][0] == '#':
        if not hascap(bot, text[2], trigger.nick, 'AaOo'):
            if not trigger.owner:
                return
        setusr(bot, text[2], '@', text[3])
        bot.say('Set chan (%s) mode %s' % (text[2], text[3]))
    else:
        user = text[2]
        chan = text[3]
        privs = text[4]

        if not hascap(bot, chan, trigger.nick, 'AaOo'):
            if not trigger.owner:
                return
        if ('A' in privs or 'O' in privs or 'B' in privs):
            return
        if 'o' in privs and (not hascap(bot, chan, trigger.nick,
                                        'AOo')):
            if not trigger.owner:
                return

        setusr(bot, chan, user, privs)
        bot.say('Set user (%s) on chan (%s) mode (%s)' %
                (user, chan, privs))

    return


def aset(bot, trigger, text):
    user = text[2]
    chan = text[3]
    privs = text[4]

    if hascap(bot, chan, trigger.nick, 'AaOo') or \
       trigger.owner:
        setuattr(bot, chan, '@@@', privs)


def hascap(bot, place, user, req):
    if not bot.db.check_table(sescapet(place).lower(), gattr['cols'],
                              gattr['id']):
        bot.db.add_table(sescapet(place).lower(), gattr['cols'], gattr['id'])
    privs = str()
    privs += getusr(bot, sescapet(place).lower(), sescapet(user))
    privs += getusr(bot, 'gattr', sescapet(user))
    ret = False
    for c in req:
        for c2 in privs:
            if c2 == c:
                ret = True
    return ret


def sescapet(thing):
    ret = thing.replace("^", "uuu")
    ret = ret.replace("'", "ttt")
    ret = ret.replace('.', 'ddd')
    ret = ret.replace('-', 'sss')
    return ret.replace('#', "ccc")

def usescapet(thing):
    ret = thing.replace("uuu", "^")
    ret = ret.replace("ttt", "'")
    ret = ret.replace("ddd", ".")
    ret = ret.replace('sss', '-')
    return ret.replace('ccc', '#')


@commands('attr')
@priority('high')
def attr(bot, trigger):
    """
    Command to change global attributes of users as well as chan
     attributes. Do .attr help to understand.
    """
    check_attr_db(bot)

    try:
        text = trigger.group().split()
    except:
        display_help(bot, trigger)
        return

    try:
        if text[1] == 'help':
            display_help(bot, trigger)
            return
        elif text[1] == 'list':
            list_access(bot, trigger, text)
            return
        elif text[1] == 'g':
            gset(bot, trigger, text)
        elif text[1] == 'c':
            cset(bot, trigger, text)
        elif text[1] == 'a':
            aset(bot, trigger, text)
    except:
        bot.say('see .attr help')
    return


def setup(bot):
    if bot.db and not bot.db.preferences.has_columns('topic_mask'):
        bot.memory['flooddetect'] = WillieMemory()
        bot.memory['flooded'] = WillieMemory()
        bot.db.preferences.add_columns(['topic_mask'])


def hasaccess(bot, trigger, chan, nick, req, emulate_protected):
    hasax = hascap(bot, chan, nick, req)
    sender_hasax = hascap(bot, chan, trigger.nick, req)
    protected = hascap(bot, chan, '@', 'p')
    isoponchan = bool()
    chan = chan.lower()
    if trigger.nick in bot.privileges[chan]:
        isoponchan = bot.privileges[chan][trigger.nick] >= OP
    else:
        isoponchan = False

    if emulate_protected:
        protected = True

    if protected:
        if not (sender_hasax or isoponchan):
            return False
    else:
        if not (hasax or isoponchan or sender_hasax):
            return False
    return True


def getwhowhere(bot, trigger):
    text = trigger.group().split()
    chan = str()
    nick = str()
    lastidx = 1

    if len(text) == 1:
        chan = trigger.sender
        nick = trigger.nick
    elif len(text) == 2:
        chan = trigger.sender
        nick = text[1]
        lastidx = 2
    elif len(text) >= 3:
        if text[1][0] == '#':
            chan = text[1]
            nick = text[2]
            lastidx = 3
        else:
            chan = trigger.sender
            nick = text[1]
            lastidx = 2

    return (chan, nick, lastidx)


def moduser(bot, trigger, emulate_protected, mode, req):
    whowhere = getwhowhere(bot, trigger)
    chan = whowhere[0].lower()
    nick = whowhere[1]
    nicks = list()
    index = 1
    temp = nick
    vstr = mode[0]
    mstr = mode[0]

    tmp = 5
    while 0 < tmp:
        tmp = tmp - 1
        mstr = mstr + mode[1]

    if not hasaccess(bot, trigger, chan, nick, req,
                     emulate_protected):
        return

    for n in trigger.group().split()[whowhere[2]:]:
        if index == 5:
            index = 0
            nicks.append(
                ['MODE', chan, mstr, temp.lstrip().rstrip()])
            temp = str()

        temp = temp + ' ' + n
        index = index + 1

    while index > 0:
         index = index -1
         vstr = vstr + mode[1]

    nicks.append(['MODE', chan, vstr, temp.lstrip().rstrip()])

    if bot.privileges[chan][bot.nick] >= OP:
        for nl in nicks:
            bot.write(nl)
            #bot.write('MODE %s %s :%s' % (chan, mode, nl))
            bot.msg(chan, 'set mode %s on %s in %s (%s)' %
                    (mode, nl[3], chan, trigger.nick))


@commands('op', 'o')
@priority('high')
def op(bot, trigger):
    """
    Command to op users, if no nick given, or chan, ops user
     calling.
    """
    moduser(bot, trigger, False, '+o', 'AaOo')


@commands('deop')
@priority('high')
def deop(bot, trigger):
    """
    Command to deop users, operates in similar manner to op.
    """
    moduser(bot, trigger, True, '-o', 'AaOo')


@commands('voice', 'v')
@priority('low')
def voice(bot, trigger):
    """
    Command to voice users, behaves as op.
    """
    moduser(bot, trigger, False, '+v', 'AaOoVv')


@commands('devoice', 'dv')
@priority('high')
def devoice(bot, trigger):
    """
    Command to devoice users, behaves as deop.
    """
    moduser(bot, trigger, True, '-v', 'AaOoVv')


@commands('kick', 'k')
@priority('high')
def kick(bot, trigger):
    """
    Kicks user, must be op in chan, or have access.
    """
    whowhere = getwhowhere(bot, trigger)
    chan = whowhere[0]
    nick = whowhere[1]
    reason = ' '.join(trigger.group().split()[whowhere[2]:])

    if not hasaccess(bot, trigger, chan, nick, "AaOo", True):
        return
    actual_kick(bot, chan, nick, trigger.nick, reason)


def actual_kick(bot, chan, nick, kicker, reason):
    bot.write(['KICK', chan, nick,
               ':(' + kicker + ') ' + reason])


def get_ts_reason(bot, trigger, lastidx):
    reason = "REASON: Just cuz."
    ts = 10

    try:
        if len(trigger.group().split()) >= lastidx + 1:
            ts = int(trigger.group().split()[lastidx])
        if len(trigger.group().split()) >= lastidx + 2:
            ts = int(trigger.group().split()[lastidx])
            reason = "REASON: " + \
                ' '. join(trigger.group().split()[lastidx + 1:])
    except:
        reason = "REASON: " + \
            ' '.join(trigger.group().split()[lastidx:])

    return ts, reason


def banman(bot, trigger, mode, caller=None):
    whowhere = getwhowhere(bot, trigger)
    chan = whowhere[0]
    nick = whowhere[1]
    ts = 10
    reason = "REASON: Just cuz."

    ts, reason = get_ts_reason(bot, trigger, whowhere[2])

    if not hasaccess(bot, trigger, chan, nick, "AaOo", True):
        return
    if bot.privileges[chan][bot.nick] < OP:
        return

    if ts > 60:
        ts = 60

    actual_ban(bot, nick, chan, ts, mode, caller, reason)
    return


def add_to_ban_list(bot, nick, chan, ts, mode, caller, reason, mask):
    if chan not in bot.memory['bans']:
        bot.memory['bans'][chan] = {}
    if nick not in bot.memory['bans'][chan]:
        bot.memory['bans'][chan][nick] = tuple()

    bot.memory['bans'][chan][nick] = (ts, mode, caller, reason, mask)


def del_from_ban_list(bot, nick, chan):
    if chan in bot.memory['bans'] \
       and nick in bot.memory['bans'][chan]:
        del bot.memory['bans'][chan][nick]


def actual_ban(bot, nick, chan, ts, mode, caller, reason):
    if 'bans' not in bot.memory:
        bot.memory['bans'] = {}

    temp = whois(bot, nick)

    if temp is None:
        bot.msg(chan, "They simply don't exist.")
        return

    mask = temp.host
    mask = '*!*@' + mask

    if mode == '+b':
        add_to_ban_list(bot, nick, chan, ts, mode, caller, reason,
                        mask)
        bans.append((mask, chan, ts, caller, nick))

    if mode == '-b':
        del_from_ban_list(bot, nick, chan)

    if caller == 'gag':
        bot.write(['MODE', chan, '-o', nick])
        bot.write(['MODE', chan, '-v', nick])
        bot.msg(chan,
                "ATTENTION: %s will be unable to type in %s "
                "for %s minutes." % (nick, chan, ts))
        bot.msg(chan, reason)

    if caller == 'ungag':
        bot.msg(chan, "ATTENTION: %s can talk again on %s" %
                (nick, chan))

    bot.write(['MODE', chan, mode, mask])


@commands('ban', 'b', 'gag')
@priority('high')
def ban(bot, trigger):
    """Ban user, must be op in chan, or have access."""
    caller = None
    if trigger.group().split()[0] == '.gag':
        caller = 'gag'
    banman(bot, trigger, '+b', caller)


@commands('unban', 'ungag')
@priority('high')
def unban(bot, trigger):
    """
    Unbans a user, behaves similar to devoice.
    """
    caller = None
    if trigger.group().split()[0] == '.ungag':
        caller = 'ungag'
    banman(bot, trigger, '-b', caller)


@commands('quiet')
@priority('high')
def quiet(bot, trigger):
    """
    Quiets a user, works similar to op, only works on certain
     networks.
    """
    moduser(bot, trigger, False, '+q', 'AaOo')


@commands('unquiet')
@priority('high')
def unquiet(bot, trigger):
    """
    Unquiets a user, works similar to deop, only works on certain
     networks
    """
    moduser(bot, trigger, True, '+q', 'AaOo')


@commands('kickban', 'kb')
@priority('high')
def kickban(bot, trigger):
    """
    Kicks and bans a user, works similar to ban and then kick.
    """
    ban(bot, trigger)
    kick(bot, trigger)


@commands('invite')
@priority('low')
def invite(bot, trigger):
    """
    invites a user to the chan, works like op
    """
    whowhere = getwhowhere(bot, trigger)
    chan = whowhere[0]
    nick = whowhere[1]

    if not hasaccess(bot, trigger, chan, nick, "AaOo", True):
        return

    if bot.privileges[chan][bot.nick] >= OP:
        bot.write(['INVITE', nick, chan])
        bot.msg(chan, "Inviting %s courtesy of %s to %s" %
                (nick, trigger.nick, chan))


def default_mask(trigger):
    welcome = formatting.color('Welcome to:', formatting.colors.PURPLE)
    chan = formatting.color(trigger.sender, formatting.colors.TEAL)
    topic_ = formatting.bold('Topic:')
    topic_ = formatting.color('| ' + topic_, formatting.colors.PURPLE)
    arg = formatting.color('{}', formatting.colors.GREEN)
    return '{} {} {} {}'.format(welcome, chan, topic_, arg)


@commands('topic', 'top')
def set_topic(bot, trigger):
    """
    Give ops the ability to change the topic.

    Returns None

    """

    purple, green, bold = '\x0306', '\x0310', '\x02'
    if not hasaccess(bot, trigger, trigger.sender, trigger.nick,
                     "AaOo", True):
        return
    text = trigger.group(2)
    if text == '':
        return
    channel = trigger.sender.lower()

    narg = 1
    mask = None
    if bot.db and channel in bot.db.preferences:
        mask = bot.db.preferences.get(channel, 'topic_mask')
    mask = mask or default_mask(trigger)
    mask = mask.replace('%s', '{}')
    narg = len(re.findall('{}', mask))

    top = trigger.group(2)
    args = []
    if top:
        args = top.split('~', narg)

    if len(args) != narg:
        message = "Not enough arguments. You gave {}, it requires {}.".format(
            len(args), narg)
        return bot.say(message)
    topic = mask.format(*args)

    bot.write(('TOPIC', channel + ' :' + topic))


@commands('tmask')
def set_mask(bot, trigger):
    """
    Set the mask to use for .topic in the current channel. %s is used to allow…                                                                        3…
    """
    if not hasaccess(bot, trigger, trigger.sender, trigger.nick,
                     "AaOo", True):
        return
    if not bot.db:
        bot.say("I'm afraid I can't do that.")
    else:
        bot.db.preferences.update(trigger.sender.lower(), {'topic_mask': trigger.group(2)})
        bot.say("Gotcha, " + trigger.nick)


@commands('showmask')
def show_mask(bot, trigger):
    """Show the topic mask for the current channel."""
    if not hasaccess(bot, trigger, trigger.sender, trigger.nick,
                     "AaOo", True):
        return
    if not bot.db:
        bot.say("I'm afraid I can't do that.")
    elif trigger.sender.lower() in bot.db.preferences:
        bot.say(bot.db.preferences.get(trigger.sender.lower(), 'topic_mask'))
    else:
       bot.say("%s")


def autovoice(bot, trigger):
    nick = trigger.nick
    chan = trigger.sender

    try:
        # chan is +v (autovoice?)
        if hascap(bot, chan, '@', 'v'):
            bot.write(['MODE', chan, '+v', nick])
        # if the nick has voice flag set global or chan
        # voice user
        if hascap(bot, chan, nick, 'Vv'):
            bot.write(['MODE', chan, '+v', nick])
    except:
        return


def autoop(bot, trigger):
    nick = trigger.nick
    chan = trigger.sender

    try:
        if hascap(bot, chan, nick, 'ao'):
            if hascap(bot, chan, nick, 'v'):
                bot.write(['MODE', chan, '+o', nick])
    except:
        return


def autoban(bot, trigger):
    nick = trigger.nick
    chan = trigger.sender

    try:
        if hascap(bot, chan, nick, 'Bb'):
            actual_ban(bot, nick, chan, 60, '+b', 'autoban', None)
            bot.write(['KICK', chan, nick,
                       ':(' + trigger.nick + ') In banlist'])
    except:
        return


@interval(60 * 1)
def clearmybans(bot):
    try:
        bans = bot.memory['bans']

        for chan in bans:
            for nick in bans[chan]:
                temp = bans[chan][nick]
                if temp[0] == 1:
                    if temp[2] == 'gag':
                        bot.msg(chan,
                                "ATTENTION: %s can talk again on %s"
                                % (nick, chan))
                    bot.write(['MODE', chan, '-b', temp[4]])
                    del_from_ban_list(bot, nick, chan)
                else:
                    bans[chan][nick] = (temp[0] - 1, temp[1],
                                        temp[2], temp[3], temp[4])

    except:
        return


@event('JOIN')
@rule('.*')
@priority('high')
def joinperform(bot, trigger):
    autovoice(bot, trigger)
    autoop(bot, trigger)
    autoban(bot, trigger)


@rule('.*')
@priority('high')
def bworddetect(bot, trigger):
    try:
        if hascap(bot, trigger.sender, trigger.nick, 'p'):
            return
        if not hascap(bot, trigger.sender, '@', 'w'):
            return
        if hasaccess(bot, trigger, trigger.sender, trigger.nick,
                     'AaOo', True):
            return
    except:
        return

    props = None
    words = None
    doban = False

    try:
        props = getuattr(bot, trigger.sender, '@@@')
    except:
        return

    if props and not props == '':
        words = props.split(',')
    else:
        return

    test = trigger

    for word in words:
        if word in test:
            doban = True
            break

    if doban:
        actual_ban(bot, trigger.nick, trigger.sender, 120, '+b',
                   'bwscan', None)
        actual_kick(bot, trigger.sender, trigger.nick, trigger.nick,
                    'bad word detected')


@rule('.*')
@priority('high')
def flooddetect(bot, trigger):
    now = int(time.time())

    try:
        # don't operate on protected ppl or non-protected chans
        if hascap(bot, trigger.sender, trigger.nick, 'p'):
            return
        if not hascap(bot, trigger.sender, '@', 'p'):
            return
    except:
        return

    #function setup, testing capabilities and such
    #also collecting values such as count, interval, repetition
    #shimmed
    count = 7
    timer = 2
    repetition = 5
    props = None

    try:
        props = getusr(bot, trigger.sender, "@@")
    except:
        return

    if props and not props == '':
        p = props.split(',')
        if len(p) == 1:
            count = int(p[0])
        elif len(p) == 2:
            count = int([0])
            timer = int(p[1])
        elif len(p) >= 3:
            count = int(p[0])
            timer = int(p[1])
            repetition = int(p[2])

    #prepare storage
    if 'flooddetect' not in bot.memory:
        bot.memory['flooddetect'] = WillieMemory()
    if 'flooded' not in bot.memory:
        bot.memory['flooded'] = WillieMemory()
    if trigger.sender not in bot.memory['flooddetect']:
        bot.memory['flooddetect'][trigger.sender] = WillieMemory()
    if Nick(trigger.nick) not in \
       bot.memory['flooddetect'][trigger.sender]:
        bot.memory['flooddetect'][trigger.sender][Nick(trigger.nick)] = list()

    #store
    templist = bot.memory['flooddetect'][trigger.sender][Nick(trigger.nick)]
    line = trigger.group()
    templist.append((now, line))

    #prune
    if len(templist) > count and len(templist) > repetition:
        toprune = repetition
        if repetition < count:
            toprune = count
        toprune += 1

        templist[:] = templist[(len(templist) - toprune):]

    # remove flooders
    crep = 1
    ccount = 1
    rem = False
    reason = ""
    for t in reversed(templist):
        if crep >= repetition:
            if Nick(trigger.nick) not in bot.memory['flooded']:
                bot.memory['flooded'][Nick(trigger.nick)] = 1
            else:
                bot.memory['flooded'][Nick(trigger.nick)] += 1
            rem = True
            templist[:] = []
            reason = "Flood detected: %s repetitions" % (repetition)
            break

        onow = t[0]
        oline = t[1]

        if oline == line and ccount > 1:
            crep += 1

        if (now - onow) <= timer and ccount >= count:
            if Nick(trigger.nick) not in bot.memory['flooded']:
                bot.memory['flooded'][Nick(trigger.nick)] = 1
            else:
                bot.memory['flooded'][Nick(trigger.nick)] += 1
            rem = True
            templist[:] = []
            reason = "Flood detected: %s lines in %s seconds" % (count, timer)
            break

        ccount += 1

    if rem:
        bot.write(['KICK', trigger.sender, trigger.nick,
                   ': %s - %s' % (trigger.nick, reason)])

        if bot.memory['flooded'][trigger.nick] >= 3:
            bot.write(['MODE', trigger.sender,
                       '+b', configureHostMask(trigger.nick)])
            bans.append((configureHostMask(trigger.nick),
                         trigger.sender))
            setusr(bot, trigger.sender, trigger.nick, '+b')
            bot.memory['flooded'][trigger.nick] = 0

