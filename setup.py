from setuptools import setup
from setuptools import find_packages

setup(
    name='JackPlug',
    version='0.1',
    author='Rodrigo Oliveira',
    author_email='rodrigo@byne.com.br',
    packages=find_packages(),
    install_requires=[
        'pyzmq==19.0.2',
        'tornado==4.5.3'
    ],
    long_description=open('README.md').read(),
)
