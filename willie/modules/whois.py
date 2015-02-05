"""
whois.py - Willie Whois module
Copyright 2014, Ellis Percival (Flyte) willie@failcode.co.uk
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net

A module to enable Willie to perform WHOIS lookups on nicknames.
This can either be to have Willie perform lookups on behalf of
other people, or can be imported and used by other modules.
"""

from willie.module import commands, event, rule
from time import sleep
from datetime import datetime, timedelta

AGE_THRESHOLD = timedelta(days=1)

class Whois(object):
    def __init__(self, data):
        to, self.nick, self.ident, self.host, star, self.name = data
        self.datetime = datetime.now()

    def __repr__(self):
        return '%s(nick=%r, ident=%r, host=%r, name=%r, datetime=%r)' % (
            self.__class__.__name__,
            self.nick,
            self.ident,
            self.host,
            self.name,
            self.datetime
        )

    def __str__(self):
        return '%s!%s@%s * %s' % (
            self.nick, self.ident, self.host, self.name)

    def set_chans(self, trigger):
        self.chans = trigger


class WhoisFailed(Exception):
    pass


def setup(bot):
    bot.memory['whois'] = {}


def check_setup(bot):
    if 'whois' not in bot.memory:
        bot.memory['whois'] = {}


def _clear_old_entries(bot):
    """
    Removes entries from the bot's memory which are older
    than AGE_THRESHOLD.
    """
    to_del = []
    for nick, whois in bot.memory['whois'].items():
        if whois.datetime < datetime.now() - AGE_THRESHOLD:
            to_del.append(nick)
    for nick in to_del:
        try:
            del bot.memory['whois'][nick]
        except KeyError:
            pass


def send_whois(bot, nick):
    """
    Sends the WHOIS command to the server for the
    specified nick.
    """
    bot.write(['WHOIS', nick])


def get_whois(bot, nick):
    """
    Waits for the response to be put into the bot's
    memory by the receiving thread.
    """
    check_setup(bot)
    i = 0
    while nick.lower() not in bot.memory['whois'] and i < 10:
        i += 1
        sleep(1)

    if nick.lower() not in bot.memory['whois']:
        return
        #raise WhoisFailed('No reply from server')
    elif bot.memory['whois'][nick.lower()] is None:
        try:
            del bot.memory['whois'][nick.lower()]
        except KeyError:
            pass
        #raise WhoisFailed('No such nickname')

    # A little housekeeping
    _clear_old_entries(bot)

    return bot.memory['whois'][nick.lower()]


def whois(bot, nick):
    """
    Sends the WHOIS command to the server then waits for
    the response to be put into the bot's memory by the
    receiving thread.
    """
    # Remove entry first so that we get the latest
    check_setup(bot)
    try:
        del bot.memory['whois'][nick]
    except KeyError:
        pass
    send_whois(bot, nick)
    return get_whois(bot, nick)


@event('311')
@rule(r'.*')
def whois_found_reply(bot, trigger):
    """
    Listens for successful WHOIS responses and saves
    them to the bot's memory.
    """
    check_setup(bot)
    nick = trigger.args[1]
    bot.memory['whois'][nick.lower()] = Whois(trigger.args)


@event('319')
@rule(r'.*')
def whois_chan_list(bot, trigger):
    nick = trigger.args[1]
    bot.memory['whois'][nick.lower()].set_chans(trigger)


#@event('401')
#@rule(r'.*')
def whois_not_found_reply(bot, trigger):
    """
    Listens for unsuccessful WHOIS responses and saves
    None to the bot's memory so that the initial
    whois function is aware that the lookup failed.
    """
    check_setup(bot)
    nick = trigger.args[1]
    bot.memory['whois'][nick] = None

    # Give the initiating whois function time to see
    # that the lookup has failed, then remove the None.
    sleep(5)
    try:
        del bot.memory['whois'][nick]
    except KeyError:
        pass


@commands('whois')
def display_whois(bot, trigger):
    """PM's you the chans the nick is in."""
    try:
        w = whois(bot, trigger.group().split()[1])
        sleep(3)
        bot.msg(trigger.nick,
                '%s is on the following chans: %s' % (w.nick, w.chans))
    except:
        bot.msg(trigger.nick,
                '%s could not be found'
                % (trigger.group().split()[1]))
