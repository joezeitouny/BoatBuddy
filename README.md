# BoatBuddy

[![Alt text](https://img.shields.io/pypi/v/boatbuddy.svg?style=flat-square)](https://pypi.python.org/pypi/boatbuddy/) [![Alt text](https://img.shields.io/github/license/joezeitouny/boatbuddy)](https://pypi.python.org/pypi/boatbuddy/)

A suite of tools to help collecting NMEA0183 and other marine metrics in a digital logbook format.

### Installation

`BoatBuddy` can be installed via `pip` or an equivalent via:

```console
$ pip install BoatBuddy
```

### Features

- Ability to generate Excel and / or CSV logs
- Generate GPX file with GPS coordinates combined with timestamps
- Ability to generate a summary log for each session
- Sessions can be tied by the NMEA server, Victron system availability or by a specified time interval

### Usage

```console
$ python -m BoatBuddy OUTPUT_DIRECTORY [options]
```

Where OUTPUT_DIRECTORY points to the path where you want the logs to be written to. This will start monitoring the
systems connected on your network and outputting log entries on disk (at specified intervals). At the end of each
session a summary file (if specified) is generated.

You can listen to NMEA0183 events from a server on your network by providing the server IP address

```console
$ python -m BoatBuddy OUTPUT_DIRECTORY --nmea-server-ip=NMEA_SERVER_IP
```

You can also capture data transmitted via Modbus TCP from your victron products

```console
$ python -m BoatBuddy OUTPUT_DIRECTORY --victron-server-ip=VICTRON_SERVER_IP
```

Don't forget to specify a medium format for the files to be written (Excel, CSV or GPX)

For the full list of available options

```console
$ python -m BoatBuddy --help
```
