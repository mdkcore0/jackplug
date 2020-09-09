#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Copyright (c) 2016 BYNE. All rights reserved.

This example subclasses JackBase to create a new class and send some messages
to the "server".
"""

import sys
from random import randint

from zmq.eventloop import ioloop

from jackplug.jack import JackBase
from jackplug.utils import IPCEndpoint
from jackplug.utils import TCPEndpoint


class JackTest(JackBase):
    __send_loop = None

    def __init__(self, *args, **kwargs):
        super(JackTest, self).__init__(*args, **kwargs)

        print("Starting send loop")
        self._send_loop = ioloop.PeriodicCallback(self.send, 2000)
        self._send_loop.start()

        self.on_timeout(self._timeout_occurred)
        self.start()

    def _timeout_occurred(self):
        print("Timeout occurred!")

    def recv(self, message):
        print("Recv: %s" % message)

    def send(self):
        message = {"event": "message",
                   "data": "ABC"
                   }
        JackBase.send(self, message)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Thou shalt run as: %s [ipc | tcp]" % sys.argv[0])
        sys.exit()

    use_ipc = False
    use_tcp = False

    if sys.argv[1] == 'ipc':
        print("Using IPC transport")
        use_ipc = True
    elif sys.argv[1] == 'tcp':
        print("Using TCP transport")
        use_tcp = True
    else:
        print("Unknown argument: %s" % sys.argv[1])
        sys.exit()

    ident = "Jack%s" % (randint(0, 1000))
    print("Acting as Jack (%s)" % ident)

    endpoint = None
    if use_ipc:
        endpoint = IPCEndpoint(pathname="/tmp/jack.plug.test")
    elif use_tcp:
        endpoint = TCPEndpoint(address="127.0.0.1", port="1234")

    jack = JackTest(service=ident, endpoint=endpoint)
    print("Exiting Jack...")
