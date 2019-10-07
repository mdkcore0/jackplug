# JackPlug
ZMQ based microservice communications library

Two transports are supported: **ipc** (though *IPCEndpoint*, using the following path
as default: */tmp/jack.plug*), and **tcp** (*TCPEndpoint*, using *3559* as the default
port number).

## Requirements
    * pyzmq 15.4.0
    * simb.pilsner

## Examples
An example of the use of this library can be found on the *examples* folder, and
running them is pretty straightforward:

Run *examples/jack.py* and *examples/plug.py*, in different terminals. You
should set the same transport argument on both of them (**ipc** or **tcp**).

```
    $ python examples/jack.py ipc
    --
    $ python examples/plug.py ipc
```
