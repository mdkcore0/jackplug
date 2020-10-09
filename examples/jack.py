"""
Copyright (c) 2016 BYNE. All rights reserved.

This example subclasses JackBase to create a new class and send some messages
to the "server".
"""

import sys
import signal
import asyncio

from random import randint

from jackplug.jack import JackBase
from jackplug.utils import IPCEndpoint
from jackplug.utils import TCPEndpoint
from jackplug.utils import PeriodicCall


class JackTest(JackBase):
    __send_loop = None

    def __init__(self, *args, **kwargs):
        super(JackTest, self).__init__(*args, **kwargs)

        self._send_loop = PeriodicCall(2, self.send)
        self.on_timeout(self._timeout_occurred)

    async def start(self):
        print("Starting send loop")

        loop = asyncio.get_running_loop()
        for signame in {'SIGINT', 'SIGTERM'}:
            loop.add_signal_handler(
                getattr(signal, signame),
                self.close
            )

        try:
            await asyncio.gather(
                JackBase.start(self),
                self._send_loop.start()
            )
        except asyncio.CancelledError:
            raise

    async def _timeout_occurred(self):
        print("Timeout occurred!")

    async def recv(self, message):
        print(f"Recv: {message}")

    async def send(self):
        message = {"event": "message", "data": "ABC"}
        await JackBase.send(self, message)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Thou shalt run as: {sys.argv[0]} [ipc | tcp]")
        sys.exit()

    use_ipc = False
    use_tcp = False

    if sys.argv[1] == "ipc":
        print("Using IPC transport")
        use_ipc = True
    elif sys.argv[1] == "tcp":
        print("Using TCP transport")
        use_tcp = True
    else:
        print(f"Unknown argument: {sys.argv[1]}")
        sys.exit()

    ident = f"Jack{randint(0, 1000)}"
    print(f"Acting as Jack ({ident})")

    endpoint = None
    if use_ipc:
        endpoint = IPCEndpoint(pathname="/tmp/jack.plug.test")
    elif use_tcp:
        endpoint = TCPEndpoint(address="127.0.0.1", port="1234")

    jack = JackTest(service=ident.encode(), endpoint=endpoint)

    try:
        asyncio.run(jack.start())
    except asyncio.CancelledError:
        pass
    finally:
        pass

    print("Exiting Jack...")
