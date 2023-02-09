## 0.2.5 (2023-02-09)

* Cleaned up the code in the plugin manager file
* Improved the implementation of the state machine inside the Victron and NMEA plugins
* Cleaned up the import statements in the modules
* Version bump to 0.2.5

## 0.2.4 (2023-02-09)

* Removed unused import statement in the console manager
* Version bump to 0.2.4

## 0.2.3 (2023-02-09)

* Fixed an issue where the Victron plugin keeps on creating new sessions when running the session in auto-victron mode
* Ported the fix above to the NMEA plugin
* Version bump to 0.2.3

## 0.2.2 (2023-02-08)

* Reverted back the code around retrieving the application name and version
* Version bump to 0.2.2

## 0.2.1 (2023-02-08)

* Included missing dependencies in the project TOML file
* Version bump to 0.2.1

## 0.2.0 (2023-02-08)

* Consolidated application name and application version fields to be in the project TOML file only
* In the rich console: Renamed Victron Metrics to Victron Plugin and NMEA Metrics to NMEA Plugin
* Introduced the plugin status feature (any plugin can be queried for its status at any point in time) Added the plugin
  status information to the rich console Rewrote the victron plugin module to make use of timer for data retrieval Added
  failsafe int and float parsing functions and refactored the victron plugin to make use of those
* Improved the Help message for the run-mode option Renamed the constants for the session run mode to include "session"
  in their wording Switched from using threads to using a timer for the main loop in the NMEA plugin Added failsafe
  constructs to the summary method inside the NMEA plugin Refactored the code of the plugin manager to remove redundant
  methods such as initialize and prepare_for_shutdown Improved the error handling inside the Victron plugin main loop
* Introduced the auto-victron and auto-nmea session run modes Added events implementation to the Victron plugin
* Added the run mode interval feature which keeps the system in session mode and splits the sessions based on the chosen
  interval
* Version bump to 0.2.0

## 0.1.0 (2023-02-07)

* Introduced the run mode option to replace the limited-mode function
* Set the default run mode to 'Continuous' Optimized the code in the console manager to remove redundant lines of code
  Fixed the get_last_log_entries function in the config module to return the entries in the correct order Improved the
  code in the victron plugin module to handle server connection problems
* Version bump to 0.1.0

## 0.0.10 (2023-02-07)

* Created PluginManager class and moved the bulk of the code in the main file to that class
* Added the ConsoleManager class Added a rich console experience to the application
* Minor adjustments to the header used in the rich console layout
* Updated the TOML file to include the newly introduced "rich" dependency
* Added the feature to filter the list of key value pairs that are presented in the rich console Divided the summary
  layout in the rich console into two sections, header and body
* Added colour styles to the log layout depending on the log type
* Version bump to 0.0.10

## 0.0.9 (2023-02-05)

* Fixed an issue where distance from last entry and cumulative distance metrics could be erroneous if the previous entry
  doesn't have valid gps coordinates Added exception handler for the reverse location lookup code segment Travelled
  distance and heading in the summary section are now only reported if end coordinates are different from the start ones
  Added a helper method to help reset metadata entries after a connection is lost to the NMEA server Fixed apparent wind
  angle metric to report values from -179 to 180
* Only write to GPX files if the GPX and the NMEA options are both set
* Improved the formatting of the date part in the Logging module Removed the console output stream handler Set a limit
  to the log file size by using a RotatingFileHandler Added a configuration setting to define the log file size limit.
  Set the default to 1 MB
* Added Tank 1 and Tank 2 types are their corresponding levels metrics to log entries and to the summary sheet
* Fixed some incorrectly reported metrics such as battery current and battery power which occurred when the values were
  negative ones
* Version bump to 0.0.9
* Updated toml file to include newly added dependency

## 0.0.8 (2023-02-03)

* Fixed bug in GPX feature where TrackPoints where added even if there is no gpx fix obtained from the nmeaplugin Fixed
  a bug in GPX feature where the GPS file was populated even if the NMEA feature is not activated Fixed an issue with
  the summary feature where last and first gps entries could be confused for empty ones Fixed a bug where a captured
  heading metric log message was output at INFO level instead of DEBUG
* Changed the default log level in the config file to INFO instead of DEBUG
* Version bump to 0.0.8

## 0.0.7 (2023-02-03)

* Renamed the TimePlugin class to ClockPlugin Renamed the TimeEntry class to ClockEntry Improved session handling
  mechanism Improved thread handling inside the NMEAPlugin class
* Version bump to 0.0.7

## 0.0.6 (2023-02-03)

* Updated the README file with more information
* Renamed Helper to utils Renamed Plugin to GenericPlugin Across the board refactoring the names of the files and
  instance variables to meet Python common naming conventions
* Renamed files to use underscore for filenames with multiple words
* Renamed instance methods to start with underscore
* Added an initial snapshot to be taken after the first 10 seconds Renamed some constants in the config file Set the
  default disk write interval to be 15 minutes
* Made use of the logging package across the whole application and refactored the relevant code parts accordingly
  Improved the threading mechanism used in the main file Improved the threading mechanism used in the main file Log
  output is also collected to a log file Log level can now be provided as a command line option Renamed the raise_events
  function in the GenericPlugin to register_for_events
* Comments improved in the config file
* Bumped the version to 0.0.6


