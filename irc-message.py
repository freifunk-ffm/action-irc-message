#! /usr/bin/env python

import sys
import ssl
import argparse

import irc.client

target = None
"The nick or channel to which to send messages"
message = None

def on_connect(connection, event):
    if irc.client.is_channel(target):
        connection.join(target)
        return

def on_join(connection, event):
    connection.privmsg(target, message)
    connection.quit("Bye")


def on_disconnect(connection, event):
    raise SystemExit()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('server')
    parser.add_argument('nickname')
    parser.add_argument('target', help="a nickname or channel")
    parser.add_argument('message')
    parser.add_argument('-p', '--port', default=6697, type=int)
    return parser.parse_args()


def main():
    global target
    global message

    args = get_args()
    target = args.target
    message = args.message

    ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
    reactor = irc.client.Reactor()
    try:
        c = reactor.server().connect(
            args.server, args.port, args.nickname, connect_factory=ssl_factory
        )
    except irc.client.ServerConnectionError:
        print(sys.exc_info()[1])
        raise SystemExit(1)

    c.add_global_handler("welcome", on_connect)
    c.add_global_handler("join", on_join)
    c.add_global_handler("disconnect", on_disconnect)

    reactor.process_forever()


if __name__ == '__main__':
    main()
