"""
Copyright (c) 2016 BYNE. All rights reserved.

This example subclass PlugBase to act as a plug ("server").
"""

import sys
import signal
import asyncio

from jackplug.plug import PlugBase
from jackplug.utils import IPCEndpoint
from jackplug.utils import TCPEndpoint


class PlugTest(PlugBase):
    def __init__(self, *args, **kwargs):
        super(PlugTest, self).__init__(*args, **kwargs)

        self.on_timeout(self._timeout_occurred)

    async def _timeout_occurred(self, service):
        print(f"Timeout occurred on service (plug) {service}!")

    async def start(self):
        print("Waiting for connections")

        loop = asyncio.get_running_loop()
        for signame in {'SIGINT', 'SIGTERM'}:
            loop.add_signal_handler(
                getattr(signal, signame),
                self.close
            )

        await PlugBase.start(self)

    async def recv(self, service, message):
        print(f"Recv ({service}): {message}")
        print("Ok, answering :)")

        await self.send(service, message)


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

    print("Acting as Plug")

    endpoint = None
    if use_ipc:
        endpoint = IPCEndpoint(pathname="/tmp/jack.plug.test")
    elif use_tcp:
        endpoint = TCPEndpoint(address="*", port="1234")

    plug = PlugTest(endpoint=endpoint)

    try:
        asyncio.run(plug.start())
    except asyncio.CancelledError:
        pass
    finally:
        pass

    print("Exiting Plug...")
