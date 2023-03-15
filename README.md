# BoatBuddy

[![Alt text](https://img.shields.io/pypi/v/boatbuddy.svg?style=flat-square)](https://pypi.python.org/pypi/boatbuddy/) [![Alt text](https://img.shields.io/github/license/joezeitouny/boatbuddy)](https://pypi.python.org/pypi/boatbuddy/)

A suite of tools to help collecting NMEA0183 and other marine metrics in a digital logbook format.

### Installation

**Requirements:	Python 3.x >= 3.5**

`BoatBuddy` can be installed via `pip` or an equivalent via:

```console
$ pip install BoatBuddy
```

#### From Source

You can install `BoatBuddy` from source just as you would install any other Python package:

```console
$ pip install git+https://github.com/joezeitouny/BoatBuddy.git
```

This will allow you to keep up to date with development on GitHub:

```console
$ pip install -U git+https://github.com/joezeitouny/BoatBuddy.git
```

### Features

- Ability to generate Excel and / or CSV logs
- Generate GPX file with GPS coordinates combined with timestamps
- Ability to generate a summary log for each session
- Sessions can be tied by the NMEA server, Victron system availability or by a specified time interval

### Usage

```console
$ python -m BoatBuddy --config=CONFIGURATION_FILENAME [options]
```

Where CONFIGURATION_FILENAME points to the file where the JSON configuration file is located on your system.

For the full list of available options

```console
$ python -m BoatBuddy --help
```
