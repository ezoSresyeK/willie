#!/usr/bin/env python

import random, time
from willie.module import commands, rule, priority, event

greeting = ['hello', 'Hallo', 'Hi', 'Welcome'] #, 'bug off', 'screw this I\'m leaving', 'wtf! it\'s']


@event('JOIN')
@rule('.*')
def hello_join(jenney, input):
    if input.nick == jenney.config.nick:
        return
    if input.sender == "#starbucks":
        jenney.write(['MODE', '#starbucks', "+v", input.nick])
    random_greeting = random.choice(greeting)
    punctuation = random.choice(('!', ' '))
    time.sleep(random.randint(1, 4))
    jenney.say(random_greeting + ' ' + input.nick + punctuation)

@rule(r'.*(bye|goodbye|seeya|cya|ttyl|g2g|gnight|goodnight).*')
@priority('high')
def goodbye(jenney, input):
    byemsg = random.choice(('Bye', 'Goodbye', 'Seeya', 'Auf Wiedersehen', 'Au revoir', 'Ttyl'))
    punctuation = random.choice(('!', ' '))
    jenney.say(byemsg + ' ' + input.nick + punctuation)

