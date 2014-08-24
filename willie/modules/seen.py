# coding=utf8
"""
seen.py - Willie Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2012, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

import time
import datetime
import re
from willie.tools import Ddict, Nick, get_timezone, format_time
from willie.module import commands, rule, priority
from willie.config import ConfigurationError
from willie import db

@rule('(.*)')
@priority('low')
def note(bot, trigger):
    if not bot.db:
        raise ConfigurationError("Database not set up, or unavailable.")
    if not bot.db.check_table("seen_db", ['nick', 'timestamp', 'channel', 'message'], 'nick'):
        bot.db.add_table("seen_db", ['nick', 'timestamp', 'channel', 'message'], 'nick')

    sd = dict()
    sd['timestamp'] = time.strftime("%a %b %d %H:%M:%S %Y", time.gmtime()).replace("'", "''")
    sd['channel'] = trigger.sender.replace("'", "''")
    sd['message'] = trigger.replace("'", "''")
    bot.db.seen_db.update(trigger.nick.replace("'", "''"), sd)

@commands('seen')
def seen(bot, trigger):
    nick = trigger.group(2).strip()
    if nick in bot.db.seen_db:
        sn = bot.db.seen_db.get(nick, ['timestamp', 'channel', 'message'])
        tz = get_timezone(bot.db, bot.config, None, trigger.nick,
                          trigger.sender)
        saw = datetime.datetime.utcfromtimestamp(time.mktime(time.strptime(sn[0],
                        "%a %b %d %H:%M:%S %Y")))
        timestamp = format_time(bot.db, bot.config, tz, trigger.nick,
                               trigger.sender, saw)
        msg = "I last saw %s at %s on %s saying %s" % (nick, timestamp, sn[1], sn[2])
        bot.say(str(trigger.nick) + ': ' + msg)
    else:
        bot.say("Sorry, I haven't seen %s around." % nick)
