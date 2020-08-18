# JackPlug
ZMQ based microservice communications library

Two transports are supported: **ipc** (though *IPCEndpoint*, using the following path
as default: */tmp/jack.plug*), and **tcp** (*TCPEndpoint*, using *3559* as the default
port number).

## Requirements
* pyzmq 19.0.2
* tornado 4.5.3
* simb.pilsner

## Installation instructions for development:
- Install pyenv and pipenv:
    - macos:

            $ brew install pyenv pipenv

    - linux:
        - Install pyenv from your package manager, or follow [these instructions](https://github.com/pyenv/pyenv#basic-github-checkout)

        - Install pipenv:

                $ pip install -U --user pipenv

- Create a new python virtualenv:

        $ pipenv shell

    pipenv should install the required python version and activate a new virtualenv; if it not occurs, run the following and repeat the command above:

        $ pyenv install 3.8.5
        $ pyenv local 3.8.5
        $ pipenv --python 3.8.5

- Finally activate the virtualenv and you are all set:

        $ pipenv install --dev

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
