"""
Copyright (c) 2016 BYNE. All rights reserved.

Use JackBase to create a new class or subclass it.

We are calling ZMQ's 'identity' as 'service', to ease the understanding of
services.
"""

import asyncio
import logging
import uuid

import zmq
import zmq.asyncio
from zmq.utils import jsonapi

from .utils import Configuration
from .utils import IPCEndpoint
from .utils import PeriodicCall

log = logging.getLogger("JackPlug")


class JackBase:
    """Base Jack class

    This handles low level communication (plus heartbeat), server side"""

    _timeout_callback = None

    def __init__(self, service, endpoint=IPCEndpoint()):
        """Class contructor

        :param service: name (or identifier) of this jack
        :param endpoint: IPCEndpoint(pathname) or TCPEndpoint(address, port) to
        connect (default pathname: /tmp/jack.plug, default port: 3559)
        """
        self.socket = None
        self._service = service
        self._endpoint = endpoint

        self._identity = str(uuid.uuid4())

        self._conf = Configuration.instance()
        self._liveness = self._conf.ping_max_liveness

        self._heartbeat_loop = PeriodicCall(
            self._conf.ping_interval, self.heartbeat
        )

    async def _recv(self):
        context = zmq.asyncio.Context.instance()
        self.socket = context.socket(zmq.DEALER)

        self.socket.identity = self._service

        # use with flags=zmq.DONTWAIT on send; also, any new message sent after
        # reaching HWM will be discarded (dealer)
        self.socket.setsockopt(zmq.SNDHWM, 3)

        # return immediately if message cannot be sent
        self.socket.setsockopt(zmq.SNDTIMEO, 0)

        # do not queue message if connection not completed (zmq level)
        self.socket.setsockopt(zmq.IMMEDIATE, 1)

        self.socket.connect(self._endpoint.endpoint)

        while True:
            message = await self.socket.recv_multipart()
            await self.recv(jsonapi.loads(message[0]))

    def close(self):
        """Do close Jack with its socket and loopers

        Can be reimplemented on the inherited class, but do not forget to call
        this base function to proper cleanup.
        """
        self._heartbeat_loop.stop()
        self.socket.close()

    @staticmethod
    def set_logger(logger):
        global log

        log.propagate = False
        log = logger

    async def heartbeat(self):
        """Send a ping message to the other endpoint"""
        await JackBase.send(
            self,
            {"event": "ping", "data": {"id": self._identity}}
        )

    async def recv(self, message):
        """Receive a message

        Should be reimplemented on the derived class.

        :param message: received message
        """
        raise NotImplementedError

    async def send(self, message):
        """Send a message

        Tries to send a message to the other endpoint. Also, check service
        liveness.
        :param message: message to be sent
        """
        try:
            await self.socket.send_json(message)
        except zmq.Again as e:
            if message.get("event", None) == "ping":
                self._liveness = self._liveness - 1

                max_str = ""
                if self._liveness + 1 == self._conf.ping_max_liveness:
                    max_str = f" (MAX) | interval: {self._conf.ping_interval}ms"

                if self._liveness >= 0:
                    log.info("Jack: liveness: %s%s", self._liveness, max_str)

                if self._liveness == 0:
                    log.error("Jack: Plug seems unavailable now")
                    if self._timeout_callback:
                        await self._timeout_callback()
            else:
                log.error("Jack: Could not send message: %s", e)
        except Exception as e:
            log.error("Jack: Error: %s", e)
        else:
            self._liveness = self._conf.ping_max_liveness

    async def start(self):
        """Initialize all service loopers"""
        await asyncio.gather(
            self._heartbeat_loop.start(),
            self._recv()
        )

    def on_timeout(self, timeout_callback=None):
        """Register a callback to be called when a timeout occurs

        :param timeout_callback: function to be set as callback. If 'None', it
        will unregister the callback.
        """

        self._timeout_callback = timeout_callback
