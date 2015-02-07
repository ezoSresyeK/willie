# coding=utf8
"""
seen.py - Willie Seen Module.

Copyright 2008, Sean B. Palmer, inamidst.com
Copyright (c) 2012, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net

"""
from __future__ import unicode_literals

import time
import datetime
from willie.tools import get_timezone, format_time
from willie.module import commands, rule, priority
from willie.config import ConfigurationError


def check_db(bot):
    """Internal db consistency method."""

    if not bot.db:
        raise ConfigurationError(
            "Database not set up, or unavailable.")
    if not bot.db.check_table("seen_db",
                              ['nick', 'timestamp',
                               'channel', 'message'], 'nick'):

        bot.db.add_table("seen_db",
                         ['nick', 'timestamp', 'channel',
                          'message'], 'nick')
    if not bot.db.check_table("seen_db",
                              ['nick', 'timestamp', 'channel',
                               'message', 'mask', 'actual_nick'],
                              'nick'):
        bot.db.seen_db.add_columns(['mask', 'actual_nick'])
    if not bot.db.check_table("seen_db",
                              ['nick', 'timestamp', 'channel',
                               'message', 'mask', 'actual_nick',
                               'ident'], 'nick'):
        bot.db.seen_db.add_columns(['ident'])


@rule('(.*)')
@priority('low')
def note(bot, trigger):
    """Internal: notes a message from a user."""

    check_db(bot)

    sd = dict()

    try:
        sd['timestamp'] = time.strftime(
            "%a %b %d %H:%M:%S %Y", time.gmtime()).replace("'", "''")
        sd['channel'] = trigger.sender.replace("'", "''")
        sd['message'] = trigger.replace("'", "''")
        sd['mask'] = trigger.hostmask.split('@')[1]
        sd['actual_nick'] = trigger.nick.replace("'", "''")
        sd['ident'] = trigger.hostmask.split('@')[0].split('!')[1]
        bot.db.seen_db.update(trigger.nick.replace("'", "''").lower(),
                              sd)
    except:
        return


@commands('seen')
def seen(bot, trigger):
    """Get the last message and mask of seen person.

    ex: .seen nick

    """

    nick = trigger.group(2).strip().lower()
    if nick in bot.db.seen_db:
        sn = bot.db.seen_db.get(nick, ['timestamp',
                                       'channel',
                                       'message',
                                       'mask',
                                       'actual_nick',
                                       'ident'])
        tz = get_timezone(bot.db, bot.config, None, trigger.nick,
                          trigger.sender)
        saw = datetime.datetime.utcfromtimestamp(
            time.mktime(time.strptime(sn[0], "%a %b %d %H:%M:%S %Y")))
        timestamp = format_time(bot.db, bot.config, tz, trigger.nick,
                                trigger.sender, saw)
        msg = "At %s %s!%s@%s in %s said: %s" % (timestamp,
                                                 sn[4],
                                                 sn[5],
                                                 sn[3],
                                                 sn[1],
                                                 sn[2])
        bot.say(str(trigger.nick) + ': ' + msg)
    else:
        bot.say("Sorry, I haven't seen %s around." % nick)
