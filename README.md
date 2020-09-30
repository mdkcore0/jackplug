# JackPlug
ZMQ based microservice communications library

Two transports are supported: **ipc** (though *IPCEndpoint*, using the following path
as default: */tmp/jack.plug*), and **tcp** (*TCPEndpoint*, using *3559* as the default
port number).

## Requirements
* Tornado version 4.5.3 is currently needed, as newer versions does not play
  well on latest pyzmq packages.

### Development requirements:
* python 3.8
* pyenv 1.2.20 (optional)

## Installation instructions for development:
- Install pyenv (optional):
    - macos:

            $ brew install pyenv

    - linux:
        - Install pyenv from your package manager, or follow [these instructions](https://github.com/pyenv/pyenv#basic-github-checkout)

- Create a new python virtualenv (optional):

        $ pyenv install 3.8.5
        $ pyenv virtualenv 3.8.5 jackplug
        $ pyenv activate jackplug

- Install python requirements:

        $ pip install -r requirements.txt

## Examples
An example of the use of this library can be found on the *examples* folder, and
running them is pretty straightforward:

Run *examples/jack.py* and *examples/plug.py*, in different terminals. You
should set the same transport argument on both of them (**ipc** or **tcp**).

```bash
$ python examples/jack.py ipc
```
```bash
$ python examples/plug.py ipc
```
