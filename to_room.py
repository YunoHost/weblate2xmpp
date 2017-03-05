# coding: utf-8

import sys
import xmpp
from contextlib import contextmanager


@contextmanager
def XMPPBot(password):
    jid = xmpp.protocol.JID("gitbot@im.yunohost.org")

    client = xmpp.Client(jid.getDomain(), debug=[])

    # hack to connect only if I need to send messages
    client.connected = False

    def connect():
        client.connect()

        # yes, this is how this stupid lib tells you that the connection
        # succeed, it return the string "sasl", this doesn't make any sens and
        # it documented nowhere, because xmpp is THE FUTUR
        if client.auth(jid.getNode(), password) != "sasl":
            print("Failed to connect, bad login/password combination")
            sys.exit(1)

        client.sendInitPresence(requestRoster=0)

        presence = xmpp.Presence(to="dev@conference.yunohost.org")
        presence.setTag('x', namespace='http://jabber.org/protocol/muc')

        client.send(presence)

        client.send(xmpp.Presence(to='dev@conference.yunohost.org/GitBot'))

    def sendToChatRoom(message):
        if not client.connected:
            connect()
            client.connected = True

        client.send(xmpp.protocol.Message("dev@conference.yunohost.org", message, typ="groupchat"))

    client.sendToChatRoom = sendToChatRoom

    yield client

    if client.connected:
        client.disconnect()


if __name__ == '__main__':
    if len(sys.argv[1:]) < 2:
        print "Usage : python to_room.py <password> <message>"
        sys.exit(1)

    password, message = sys.argv[1:3]

    with XMPPBot(password) as bot:
        bot.sendToChatRoom(message)
