from setuptools import setup
from setuptools import find_packages

setup(
    name='JackPlug',
    version='0.1',
    author='Rodrigo Oliveira',
    author_email='rodrigo@byne.com.br',
    packages=find_packages(),
    install_requires=[
        'simb.pilsner',
        'pyzmq==18.1.0',
        'tornado==4.5.3'
    ],
    long_description=open('README.md').read(),
)
