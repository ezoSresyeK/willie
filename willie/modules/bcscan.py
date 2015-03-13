# coding=utf8
"""
bcscan - scans for users on bad channels.

Copyright 2014 - KeyserSoze
Liscensed under MIT License

"""

from willie.module import commands, priority, event, interval, rule
from willie.modules.whois import whois
from willie.modules.adminchan import hasaccess, actual_ban, \
    actual_kick, sescapet, usescapet
import json
from time import sleep

debug_enabled = False
TIMER = 60 * 45
if debug_enabled:
    TIMER = 60 * 5


def debug(func, message, enabled=False):
    """Print debug info."""
    if debug_enabled or enabled:
        print(func + ': ' + str(message))


def abc(bot, chan, bchan):
    """Wrapper for function."""

    _add_bad_chan(bot, chan, bchan)


def dbc(bot, chan, bchan):
    """Wrapper for function."""

    _del_bad_chan(bot, chan, bchan)


def enbc(bot, chan, bchan):
    """Wrapper for function."""

    _enable_bad_chan(bot, chan, bchan)


def dibc(bot, chan, bchan):
    """Wrapper for function."""

    _disable_bad_chan(bot, chan, bchan)


def sbc(bot, chan, bchan):
    """Wrapper for function."""

    try:
        _chan_status(bot, chan, bchan)
    except KeyError:
        debug('sbc', 'in KeyError', True)


options = {
    'add': abc,
    'del': dbc,
    'en': enbc,
    'di': dibc,
    'delete': dbc,
    'enable': enbc,
    'disable': dibc,
    'ena': enbc,
    'dis': dibc,
    'status': sbc
}


def _serializev(value):
    return json.dumps(value, ensure_ascii=False)


def _deserializev(value):
    value = unicode(value)
    return json.loads(value)


def _get_conf(bot, chan):
    debug('_get_conf', 'enter')
    _check_setup(bot)
    ret = None
    loaded = bot.memory['loaded']
    if not loaded:
        loaded = True
        for key in bot.db.bcscan.keys():
            _load(bot, usescapet(key[0]))
    if chan not in bot.memory['bcscan']:
        ret = _load(bot, chan)
    else:
        ret = bot.memory['bcscan'][chan]

    debug('_get_conf', 'exit')

    return ret


def _load(bot, key):
    if sescapet(key) in bot.db.bcscan:
        c = bot.db.bcscan.get(sescapet(key), ['data'])
        debug('_load', c)
        t = _deserializev(c[0])
        bot.memory['bcscan'][key] = t
        ret = bot.memory['bcscan'][key]
        return ret


def _create_conf(bot, chan):
    debug('_create_conf', 'enter')
    _check_setup(bot)
    bot.memory['bcscan'][chan] = {}
    bot.memory['bcscan'][chan]['enabled'] = False
    bot.memory['bcscan'][chan]['badchans'] = []
    debug('_create_conf', 'exit')


def _set_conf(bot, chan):
    debug('_set_conf', 'enter')
    _check_setup(bot)
    if chan in bot.memory['bcscan']:
        data = {}
        data['data'] = _serializev(bot.memory['bcscan'][chan])
        bot.db.bcscan.update(sescapet(chan), data)
    debug('_set_conf', 'exit')


def _check_setup(bot):
    debug('_check_setup', 'enter')
    if not bot.db:
        return False

    if not bot.db.check_table('bcscan', ['chan', 'data'], 'chan'):
        bot.db.add_table('bcscan', ['chan', 'data'], 'chan')

    if 'bcscan' not in bot.memory:
        bot.memory['bcscan'] = {}

    if 'bckicks' not in bot.memory:
        bot.memory['bckicks'] = {}

    if 'loaded' not in bot.memory:
        bot.memory['loaded'] = False
    debug('_check_setup', 'exit')


@commands('bcman')
def bad_chan_man(bot, trigger):
    """
    Manage bad channels.

    .bcman [channel] add/del/en/di/status chan(s)

    """

    debug('bad_chan_man', 'enter')

    priv, channel, text, idx = _check_priv(bot, trigger)
    if not priv:
        return

    _man_bcscan(bot, channel, text, idx)
    debug('bad_chan_man', 'exit')


def _check_priv(bot, trigger):
    text = trigger.group().split()
    idx = 1
    channel = trigger.sender

    if len(text) > idx + 1:
        if text[1][0] == '#':
            idx = 2
            channel = text[1]

    return trigger.admin or \
        hasaccess(bot, trigger, channel, trigger.nick, "AaOo",
                  False), channel, text, idx


def _man_bcscan(bot, channel, text, idx):
    debug('_man_bcscan', 'enter')
    for chan in text[idx + 1:]:
        try:
            options[text[idx]](bot, channel, chan)
        except KeyError:
            bot.reply("Sorry, check help.")
    debug('_man_bcscan', 'exit')


def _chan_status(bot, channel, bchannel):
    chan = _get_conf(bot, bchannel)
    if chan is None:
        debug('_chan_status', 'in return')
        return
    debug('_chan_status', chan)
    bot.reply("BCSCAN Enabled: %s." % (chan['enabled']))

    count = 0
    temp = ""
    for c in chan['badchans']:
        count = count + 1
        temp = temp + c + ' '

        if count == 15:
            bot.reply('Blocked chans: %s' % (temp))
            count = 0
            temp = ""
    bot.reply('Blocked chans: %s' % (temp))


def _add_bad_chan(bot, channel, bchannel):
    debug('_add_bad_chan', 'enter')
    chan = _get_conf(bot, channel)
    if chan is None:
        _create_conf(bot, channel)

    chan = _get_conf(bot, channel)

    chan['badchans'].append(bchannel)
    _set_conf(bot, channel)
    debug('_add_bad_chan', 'exit')


def _del_bad_chan(bot, channel, bchannel):
    debug('_del_bad_chan', 'enter')
    chan = _get_conf(bot, channel)
    if chan is not None:
        chan['badchans'].remove(bchannel)
        _set_conf(bot, channel)
    debug('_del_bad_chan', 'exit')


def _enable_bad_chan(bot, channel, bchan, complete=False):
    debug('_enable_bad_chan', 'enter')
    chan = _get_conf(bot, channel)
    if chan is None:
        _create_conf(bot, channel)

    chan = _get_conf(bot, channel)

    chan['enabled'] = True
    _set_conf(bot, channel)

    if not complete:
        _enable_bad_chan(bot, bchan, channel, True)
    debug('_enable_bad_chan', 'exit')


def _disable_bad_chan(bot, channel, bchan, complete=False):
    debug('_disable_bad_chan', 'enter')
    chan = _get_conf(bot, channel)
    if chan is not None:
        chan['enabled'] = False
        _set_conf(bot, channel)

    if not complete:
        _disable_bad_chan(bot, bchan, channel, True)
    debug('_disable_bad_chan', 'exit')


@event('JOIN')
@interval(TIMER)
@priority('high')
@rule('.*')
def scan(bot, trigger=None):
    """Scan chan for bad users."""

    _check_setup(bot)
    _get_conf(bot, 'test')  # Init
    debug('scan', 'enter')
    _event = 'NONE'
    try:
        _event = trigger.event
    except AttributeError:
        pass
    if _event == 'JOIN':
        _check_user(bot, trigger.sender, trigger.nick)
    else:
        for chan in bot.memory['bcscan'].keys():
            c = _get_conf(bot, chan)
            if c['enabled']:
                for nick in bot.privileges[chan].keys():
                    debug('scan', nick)
                    _check_user(bot, chan, nick)
    debug('scan', 'exit')


@commands('forcescan')
def forcescan(bot, trigger):
    """Force scan."""
    priv, _, _, _ = _check_priv(bot, trigger)

    if priv:
        scan(bot)


def _check_user(bot, chan, nick):
    debug('_check_user', 'enter')
    if not _pre_check(bot, chan, nick):
        _do_whois(bot, chan, nick, _actual_check)
    debug('_check_user', 'exit')


def _actual_check(bot, chan, nick, c, chans):
    debug('_check_user', chans)
    for ch in chans:
        for bch in c['badchans']:
            debug('_check_user', (ch, bch))
            if bch.lower() in ch.lower():
                _add_kick(bot, chan, nick)


def _do_whois(bot, chan, nick, fun):
    c = _get_conf(bot, chan)
    if c is None:
        return
    u = whois(bot, nick)
    sleep(5)
    chans = None

    try:
        chans = u.chans.split()
    except AttributeError:
        return

    fun(bot, chan, nick, c, chans)


def _add_kick(bot, chan, nick):
    debug('_add_kick', 'enter')
    if chan not in bot.memory['bckicks']:
        bot.memory['bckicks'][chan] = {}

    if nick not in bot.memory['bckicks'][chan]:
        bot.memory['bckicks'][chan][nick] = 0
    else:
        bot.memory['bckicks'][chan][nick] = \
            bot.memory['bckicks'][chan][nick] + 1

    if bot.memory['bckicks'][chan][nick] == 3:
        del bot.memory['bckicks'][chan][nick]
        actual_ban(bot, nick, chan, 60, '+b', 'bcscan', None)

    actual_kick(bot, chan, nick, nick, 'bad channels')
    debug('_add_kick', 'exit')


def _pre_check(bot, chan, nick):
    debug('_pre_check', 'enter')
    if chan not in bot.memory['bckicks']:
        return False
    if nick not in bot.memory['bckicks'][chan]:
        return False

    _add_kick(bot, chan, nick)
    debug('_pre_check', 'exit')
    return True
