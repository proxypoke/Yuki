#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: slowpoke <proxypoke at lavabit dot com>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

'''Main module.'''

from . import dpt

# pip install blackbox
from blackbox import IRC, Parser

import threading
import json
import argparse
import time


def main():
    '''Program entry point. Gets command line arguments.'''
    parser = argparse.ArgumentParser(
        description="A bot to watch for Daily Programming Threads on /g/."
    )
    parser.add_argument("config", help="path to config file")
    args = parser.parse_args()

    config = load_config(args.config)
    connect(config)


def load_config(path):
    '''Load a config file, checking for required options.'''
    # settings which are required for usage.
    required = ("server",
                "port",
                "nick",
                )
    with open(path) as configfile:
        config = json.load(configfile)
        for setting in required:
            if not setting in config:
                raise KeyError("Invalid config, missing option '{0}'."
                               .format(setting))

        if not "user" in config:
            config["user"] = config.get("nick")
        if not "realname" in config:
            config["realname"] = config.get("user")
        if not "channels" in config:
            config["channels"] = ''
        if not "nickserv" in config:
            config["nickserv"] = None
        if not "ssl" in config:
            config["ssl"] = False

        return config


def connect(config):
    '''Connect to the server using the given config.'''
    parser = Parser()

    irc = IRC(ssl=config["ssl"])
    irc.connect(config["server"], config["port"])

    irc.nickname(config["nick"])
    irc.username(config["user"], config["realname"])

    while True:
        data = irc.recv()
        event = parser.parse(data)
        if event.command == "376":  # End of MOTD
            break

    if config["nickserv"]:
        irc.say("NickServ", "IDENTIFY {0}".format(config["nickserv"]))
        while True:
            data = irc.recv()
            event = parser.parse(data)
            if (event.params[-1] ==
                    "Password accepted - you are now recognized."):
                break

    irc.join(config["channels"])

    loop(irc, parser, config)


def loop(irc, parser, config):
    '''Connection loop. Receive data and handle commands.'''

    update(irc, config)
    check = threading.Timer(30, update, args=[irc, config])

    while True:
        data = irc.recv()
        event = parser.parse(data)
        print(data)

        if event.command == "PRIVMSG":
            words = event.params[-1].split()
            if "~dpt" in words:
                threads = dpt.get_dpts(check=False)
                if len(threads) == 1:
                    thread = threads[0]
                    url = dpt.thread_url.format(thread['no'])
                    irc.say(event.params[0],
                            "There's a DPT at {0}. [{2}, {1} replies]"
                            .format(url, thread['replies'],
                                    'λ' if dpt.match_image(thread) else '?'))
                elif len(threads) > 1:
                    irc.say(event.params[0],
                            "There appear to be multiple DPTs:")
                    for thread in threads:
                        url = dpt.thread_url.format(thread['no'])
                        irc.say(event.params[0], "{0} [{2} {1} replies]"
                                .format(url, thread['replies'],
                                        'λ' if dpt.match_image(thread) else '?'))
                else:
                    irc.say(event.params[0],
                            "There does not appear to be an active DPT.")
            elif "~quit" in words:
                irc.quit("Time to program. Bye.")
                break

        # restart timer if it's off
        if not check.is_alive():
            check = threading.Timer(30, update, args=[irc, config])
            check.start()


def update(irc, config):
    '''Update the list of DPTs and issue notices upon 404 etc.'''
    channels = config["channels"].split(',')

    dpt.check_for_dpt()

    _404 = dpt.get_404()
    for thread in _404:
        for channel in channels:
            irc.say(channel, "Oh no! A DPT has 404'd: {0} [{1} replies]"
                    .format(dpt.thread_url.format(thread['no']),
                            thread['replies']))

    new = dpt.get_new()
    for thread in new:
        for channel in channels:
            irc.say(channel, "A new DPT has appeared: {0} [{1}]"
                    .format(dpt.thread_url.format(thread['no']),
                            'λ' if dpt.match_image(thread) else '?'))
