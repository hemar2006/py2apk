# py2apk

[![GitHub issues](https://img.shields.io/github/issues/anbuhckr/py2apk)](https://github.com/anbuhckr/py2apk/issues)
[![GitHub forks](https://img.shields.io/github/forks/anbuhckr/py2apk)](https://github.com/anbuhckr/py2apk/network)
[![GitHub stars](https://img.shields.io/github/stars/anbuhckr/py2apk)](https://github.com/anbuhckr/py2apk/stargazers)
[![GitHub license](https://img.shields.io/github/license/anbuhckr/py2apk)](./LICENSE)
![PyPI - Python Version](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue)

Easly create standalone android app for web developer with python, html, css, js.
Focus creating your web app with html, css, and js. Let this small python tools converting to apk.

## Table of Contents

* [Installation](#installation)
* [Getting Started](#getting-started)


## Installation

To install py2apk, simply:

```
$ python3 -m pip install -U git+https://github.com/anbuhckr/py2apk.git
```

or from source:

```
$ python3 setup.py install
```

## Getting Started

```sh
#download android-sdk, gradle, jdk for first time only
$ python3 -m py2apk install

#usage:
$ python3 -m py2apk help

#create new app
$ python3 -m py2apk new

#build app
$ python3 -m py2apk build

#install debug app in emulator
$ python3 -m py2apk run

#package app
$ python3 -m py2apk package

#verify signed app
$ python3 -m py2apk verify
```
