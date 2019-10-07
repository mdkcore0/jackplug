# JackPlug
ZMQ based microservice communications library

Two transports are supported: **ipc** (though *IPCEndpoint*, using the following path
as default: */tmp/jack.plug*), and **tcp** (*TCPEndpoint*, using *3559* as the default
port number).
```
## Requirements
    * pyzmq
    * simb.pilsner
