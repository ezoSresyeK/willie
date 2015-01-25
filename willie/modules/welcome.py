#!/usr/bin/env python

import random
import time
from willie.module import rule, priority, event, interval

greeting = ['hello', 'Hallo', 'Hi', 'Welcome', 'Sup', 'Oh no it\'s']
#            'did you jizz in your pants today?',
#            'have you jizzed in your pants recently?']
check = False
do_greet = True
greeted = 0


@event('JOIN')
@rule('.*')
def hello_join(bot, trigger):
    global greeted
    if trigger.nick == bot.config.nick:
        return
    random_greeting = random.choice(greeting)
    punctuation = random.choice(('!', ' '))
    time.sleep(random.randint(1, 4))
    greeted = greeted + 1
    if greeted > 5:
        greeted = 0
    if do_greet:
        bot.say(random_greeting + ' ' + trigger.nick + punctuation)


@rule(r'.*(bye|goodbye|seeya|cya|ttyl|g2g|gnight|goodnight).*')
@priority('high')
def goodbye(bot, trigger):
    byemsg = random.choice(
        ('Bye', 'Goodbye', 'Seeya',
         'Auf Wiedersehen', 'Au revoir', 'Ttyl'))
    punctuation = random.choice(('!', ' '))
    bot.say(byemsg + ' ' + trigger.nick + punctuation)


@interval(60 * 5)
def greet_again(bot):
    global check, do_greet
    if check:
        check = False
        do_greet = True


@interval(3)
def stop_greet(bot):
    global check, do_greet, greeted
    if not check and greeted > 5:
        greeted = 0
        do_greet = False
        check = True
