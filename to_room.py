# coding: utf-8

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
        client.auth(jid.getNode(), password)

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
