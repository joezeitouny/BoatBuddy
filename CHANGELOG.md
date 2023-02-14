## 0.3.0 (2023-02-14)

* Renamed 'gps' commmand line option to 'gps-serial-port'
* Introduced 'show-log-in-console' command line option
* Changed the default session run mode to 'manual'
* Renamed 'Starter Batt...' fields to 'Strt. Batt...'
* Introduced the option to show or hide log section in the footer of the rich console based on the 'show-log-in-console'
  command line option value
* Changed defaults of instance metrics in the NMEA plugin to be empty strings
* Improved on the logic to compute starting and ending GPS locations and their respective coordinates in the GPS and
  NMEA plugins
* Improved the logic that detects when a GPS fix is captured
* Version bump to 0.3.0

## 0.2.16 (2023-02-13)

* Cleaned up the ConsoleManager class
* The whole top bar turns red now when a session is active
* Version bump to 0.2.16

## 0.2.15 (2023-02-13)

* Added the GPS plugin layout to the rich console
* Renamed the private methods in the ConsoleManager class
* Increased the vertical size of the summary header section
* Reduced the code complexity around creating the sub layouts in the body section
* Broadened the scope of the exceptions captured in the GPS plugin
* Reintroduced the pyobjc dependency for darwin platforms only
* Version bump to 0.2.15

## 0.2.14 (2023-02-13)

* Removed the pyobjc dependency from the TOML file
* Version bump to 0.2.14

## 0.2.13 (2023-02-13)

* Moved the reset_entries function to the GenericPlugin class and renamed it to clear_entries
* Improved the layout of the rich console to be more readable on small screens
* Added the GPSPlugin feature (though not thoroughly tested yet)
* Added exception handlers around parts of the code where exceptions might arise
* After a connection to the module is re-established the instance variables holding the metrics values are reset
* Refactored and simplified the code of the NotificationsManager class
* Cleaned up the code in the utils file
* Tank 1 and Tank 2 levels are now integer values instead of float
* Version bump to 0.2.13

## 0.2.12 (2023-02-11)

* Moved the code logic for sound playback from the utils file into its own dedicated SoundManager class
* Introduced notification type 'SOUND' in the notification manager
* Version bump to 0.2.12

## 0.2.11 (2023-02-11)

* Introduced a notification manager class to handle sound notifications according to configurable user
* Improved the handling of connection state in the NMEA plugin to tackle false positive situations
* Create a sound buffer to tackle playback of multiple sounds sequentially
* Version bump to 0.2.11

## 0.2.10 (2023-02-10)

* Fixed the sound not playing when running inside a package
* Version bump to 0.2.10

## 0.2.9 (2023-02-10)

* Fixed the filenames used to play sounds from the resources folder
* Version bump to 0.2.9

## 0.2.8 (2023-02-10)

* Improved the colouring of the rows in the rich console
* Added --no-sound command line option to suppress application sounds
* Moved the playsound function to the utils file and created an async version of it
* Moved the constant lists out of the plugin files to the config file
* Added sound notifications for when the application starts and when a session starts or ends
* Version bump to 0.2.8

## 0.2.7 (2023-02-09)

* Reduced the initial snapshot interval from 10 to 1 second
* Animated the session status bar indicator in the rich console
* Version bump to 0.2.7

## 0.2.6 (2023-02-09)

* Changed the names used in the clock plugin fields from Timestamp to Time
* Added the ability to colour metrics values differently based configured ranges
* Version bump to 0.2.6

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


