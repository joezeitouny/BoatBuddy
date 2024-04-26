## 0.14.5 (2024-04-26)

* Added ability to upload and download system configuration files
* Version bump to 0.14.5

## 0.14.4 (2024-04-26)

* UI Layout improvements
* Version bump to 0.14.4

## 0.14.3 (2024-04-25)

* Added a tolerance margin when calculating the anchor circle radius based on the allowed distance
* UI Layout improvements
* Updating anchor allowed distance no longer resets the maximum observed distance nor the timing registers
* Version bump to 0.14.3

## 0.14.2 (2024-04-23)

* Added support for reading auxiliary temperature from the battery monitor (if present) in the Victron BLE plugin
* Version bump to 0.14.2

## 0.14.1 (2024-04-21)

* Added ability to show / hide boat tracks on the map when an anchor alarm is active
* Added extra checks to validate OUTPUT_PATH and TMP_PATH configuration settings during application startup
* Version bump to 0.14.1

## 0.14.0 (2024-04-21)

* Added feature to persist active enchor alarm session on disk and recover it when the application restarts
* Added ability to specify SMTP server settings
* Version bump to 0.14.0

## 0.13.15 (2024-04-21)

* UI Layout improvements
* Version bump to 0.13.15

## 0.13.14 (2024-04-20)

* UI Layout improvements
* Version bump to 0.13.14

## 0.13.13 (2024-04-19)

* UI Layout improvements
* Version bump to 0.13.13

## 0.13.12 (2024-04-18)

* UI Layout improvements
* Version bump to 0.13.12

## 0.13.11 (2024-04-18)

* UI Layout improvements
* Allowed distance field is now clickable in the anchor alarm feature
* Version bump to 0.13.11

## 0.13.10 (2024-04-18)

* UI Layout improvements
* Version bump to 0.13.10

## 0.13.9 (2024-04-18)

* UI Layout improvements
* Added ability to reset maximum recorded distance in the anchor alarm feature
* Version bump to 0.13.9

## 0.13.8 (2024-04-18)

* UI Layout improvements
* Updated Open Layers library to v9.1.0
* Increased GPS Plugin sampling rate
* Version bump to 0.13.8

## 0.13.7 (2024-04-18)

* UI Layout improvements
* Fixed an issue with sampling rates for plugins
* Version bump to 0.13.7

## 0.13.6 (2024-04-17)

* UI Layout improvements
* Version bump to 0.13.6

## 0.13.5 (2024-04-16)

* UI Layout improvements
* Email layout improvements
* Version bump to 0.13.5

## 0.13.4 (2024-04-12)

* Fixed an issue where Email attachments weren't correctly named
* Version bump to 0.13.4

## 0.13.3 (2024-04-12)

* Email layout improvements
* Version bump to 0.13.3

## 0.13.2 (2024-04-12)

* Removed the dependency on yagmail and Gmail. Emails will now be sent from app@boatbuddy.site
* Version bump to 0.13.2

## 0.13.1 (2024-04-11)

* CPU Performance improvements
* Version bump to 0.13.1

## 0.13.0 (2024-04-11)

* Launching the website in a browser during startup is now configurable in the json configuration file
* Version bump to 0.13.0

## 0.12.2 (2024-04-09)

* Added ability to refresh the whole page by clicking on the time field in the navigation bar section
* Version bump to 0.12.2

## 0.12.1 (2024-03-31)

* Added support for passing in the configuration file path through an environment variable
* Removed support for specifying the server IP address for the web application
* Switched the used sound library from playsound to pydub
* Cleaned up the requirements file
* Added a Dockerfile for experimentation
* Version bump to 0.12.1

## 0.12.0 (2024-03-31)

* Removed the anchor map animation as it was causing problems when controlling the application from multiple screens
* Fixed an issue where Victron BLE plugin would repeatedly report that it is down when connecting to a BMV that doesn't have the starter battery configured as Auxiliary
* Added support for reporting on housing battery power 
* Added support to display housing battery voltage on the left side pane 
* Fixed an issue where SS SOC value wasn't correctly rounded in the excel output
* Added Housing battery minimum power and housing battery minimum current entries in the summary list
* Added created by section in the about us page
* Removed the NMEA0183 Instruments tab from the display when the NMEA module is disabled
* Removed "Use Home Position" button from the display if the GPS Home Position field is not configured 
* UI Layout improvements
* Version bump to 0.12.0

## 0.11.2 (2024-03-11)

* Fixed an issue where a session couldn't be started if the Victron BLE module is not enabled
* Version bump to 0.11.2

## 0.11.1 (2024-03-09)

* Added "Use last anchor position" feature
* UI layout improvements
* Fixed an issue with the Telegram module where the module is not registering correctly its internal state
* Version bump to 0.11.1

## 0.11.0 (2024-03-08)

* Added support for displaying housing battery voltage on the dashboard
* Removed database storage feature
* Removed Rich console feature
* Introduced support for Victron BLE readouts
* Added ability to use a preset position when setting an anchor
* UI layout improvements
* Version bump to 0.11.0

## 0.10.1 (2024-02-02)

* Added boat name on main UI
* UI layout improvements
* Version bump to 0.10.1

## 0.9.5 (2023-12-03)

* Layout improvements
* Version bump to 0.9.5

## 0.9.4 (2023-12-02)

* Layout improvements
* Version bump to 0.9.4

## 0.9.3 (2023-11-29)

* Layout improvements
* Version bump to 0.9.3

## 0.9.2 (2023-11-28)

* Layout improvements
* Version bump to 0.9.2

## 0.9.1 (2023-11-27)

* Added support for current gauge
* Removed unnecessary error notifications
* Version bump to 0.9.1

## 0.9.0 (2023-11-26)

* Replaced Gauge Plugin
* Refactored code to dynamically load Electrical metrics section UI elements at runtime
* Added NMEA Instruments section
* Layout improvements
* Version bump to 0.9.0

## 0.8.18 (2023-11-22)

* Fixed an issue where anchor map doesn't show after a web page refresh
* Version bump to 0.8.18

## 0.8.17 (2023-11-22)

* Updated third party libraries
* Removed all synchronous calls from the Web UI
* Fixed browser reported issues
* Version bump to 0.8.17

## 0.8.16 (2023-11-18)

* Layout improvements
* Update anchor allowed distance during an anchor session no longer erases the boat position history markers
* Added overlay message to appear when anchor alarm is running and the GPS module goes down
* Renamed system metrics section to electrical system metrics
* Version bump to 0.8.16

## 0.8.15 (2023-11-13)

* Layout improvements
* Added max anchor distance metric
* Version bump to 0.8.15

## 0.8.14 (2023-11-12)

* Layout improvements
* Version bump to 0.8.14

## 0.8.13 (2023-11-12)

* Added ability to track current boat position on map when using the anchor alarm feature
* Anchor duration is now represented in days hours and minutes format
* Version bump to 0.8.13

## 0.8.12 (2023-11-11)

* Layout improvements
* Version bump to 0.8.12

## 0.8.11 (2023-11-11)

* Reduced the amount of digits in the seconds coordinates of the calculated anchor position when setting the anchor using a bearing and a distance
* Layout improvements
* Added GPS accuracy field
* Version bump to 0.8.11

## 0.8.10 (2023-11-05)

* Added a feature to limit the history of anchor data to a predefined threshold
* Added input validation checks for the set and update anchor alarm form
* Added the ability to set an anchor with a current position, a distance from anchor and a bearing to anchor
* Version bump to 0.8.10

## 0.8.9 (2023-11-03)

* Layout improvements
* Version bump to 0.8.9

## 0.8.8 (2023-11-01)

* Added support for versioning to JSON responses
* Version bump to 0.8.8

## 0.8.7 (2023-10-30)

* Added map buttons to switch between default and satellite layers
* Added map buttons to zoom in / out
* Rewrote the code logic for drawing boat historical points on the map to use layers instead of overlays
* Layout improvements
* Version bump to 0.8.7

## 0.8.6 (2023-10-26)

* Layout improvements
* Version bump to 0.8.6

## 0.8.5 (2023-10-25)

* Layout improvements
* Added zoom animation on the map that plays after setting an anchor
* Version bump to 0.8.5

## 0.8.4 (2023-10-25)

* Added anchor bearing and duration of metrics
* Layout improvements
* Version bump to 0.8.4

## 0.8.3 (2023-10-24)

* Fixed an issue where the anchor map only loads on the webpage where the anchor alarm is set
* Version bump to 0.8.3

## 0.8.2 (2023-10-24)

* Fixed the order in which relevant boat position markers (the yellow dots) appear on the map compared to the boat marker (the blue dot)
* Version bump to 0.8.2

## 0.8.1 (2023-10-24)

* Added the ability to render satellite images in the anchor alarm map when supplying Mapbox API token to the configuration file
* Version bump to 0.8.1

## 0.8.0 (2023-10-24)

* Added the anchor alarm feature
* UI based notifications on the webpage now fade out after few seconds
* Version bump to 0.8.0

## 0.7.1 (2023-07-21)

* Fine tune the requirements.txt file
* Fixed a typo in a console message that appears when the flask web app is launching
* Version bump to 0.7.1

## 0.7.0 (2023-03-22)

* Added dark and light themes and ability to switch between those two automatically or manually.
* Version bump to 0.7.0

## 0.6.3 (2023-03-15)

* Removed local fonts
* Prepped the HTML code so that it is ready for HTTPS environments
* Version bump to 0.6.3

## 0.6.2 (2023-03-15)

* Added Favicon to website
* Version bump to 0.6.2

## 0.6.1 (2023-03-15)

* Fixed the fonts not correctly loaded issue web rendering the website in a browser
* Updated the project homepage value
* Updated the Readme file
* Version bump to 0.6.1

## 0.6.0 (2023-03-10)

* Fixed issue with CSV files not rendering correctly
* Empty values are now reported as string "N/A" across the board 
* Summary values are computed when snapshots are taken except the ones that deal with reverse location lookup 
* Database structure is modified to accommodate string values as empty values
* Version bump to 0.6.0

## 0.5.15 (2023-03-08)

* Added application logo
* Changed the responsive layout behaviour of the right column in the navbar so that the elements stick together on
  smaller screen resolutions
* Added reference documents
* Version bump to 0.5.15

## 0.5.14 (2023-03-07)

* Added modal message to notify the user when connection to the server drops
* Reduced the waiting period between the initialization of the modules from 0.2 to 0.1 seconds
* Added bootstrap icons to the Web UI
* Version bump to 0.5.14

## 0.5.13 (2023-03-07)

* Improvements in the web application UI for smaller screen sizes
* Version bump to 0.5.13

## 0.5.12 (2023-03-07)

* Improvements in the web application UI for smaller screen sizes
* Version bump to 0.5.12

## 0.5.11 (2023-03-06)

* Web application UI now accomodates for smaller screen sizes
* Alerts are now of type warning for a normal notification and success for notifications that inform of clearance
* Version bump to 0.5.11

## 0.5.10 (2023-03-06)

* Web application UI improvements
* Version bump to 0.5.10

## 0.5.9 (2023-03-03)

* Added notification alerts
* Web application UI improvements
* Version bump to 0.5.9

## 0.5.8 (2023-03-03)

* Removed the need for CMySQLConnection module
* Version bump to 0.5.8

## 0.5.7 (2023-03-03)

* Added web application feature
* Version bump to 0.5.7

## 0.5.6 (2023-02-24)

* Improved the email, logging, plugin and notifications modules to generate events for the database manager to consume
* Moved all modules initializations to be handled inside the ConsoleManager class and added Rich status UI elements to
  inform the user about the loading process
* Created a log manager class and consolidated all logging related logic in it
* Created a DatabaseManager class to help with database related tasks
* Added a feature that allows the application to write all logs, events, sessions and live feed to a MySQL database
* Version bump to 0.5.6

## 0.5.5 (2023-02-22)

* Moved the modules initialisation step to the Console Manager class
* Added console output messages during application startup and shutdown
* Version bump to 0.5.5

## 0.5.4 (2023-02-21)

* Changed the colour used in columns to bright_yellow if the status of the plugin is 'STARTING'
* Added colouring of for the columns in the rich console UI to reflect the plugin status
* Added gitignore files
* Version bump to 0.5.4

## 0.5.3 (2023-02-21)

* Included date and time of the notification trigger in the email body
* Improved the way notifications are handled in the Notification manager class.
* Version bump to 0.5.3

## 0.5.2 (2023-02-21)

* Added a general exception catcher in the Console manager to catch unexpected application wide exceptions and exit
  gracefully
* Improved the way notifications are handled in the Notification manager class.
* Version bump to 0.5.2

## 0.5.1 (2023-02-20)

* Added an email manager class and moved the email handling logic from the utils file
* Added a sound type enum
* Changed the section 'Victron System' to 'Victron ESS' in the console ui
* Plugins now output an INFO message when they're started
* Notification and sound modules now make use of mutexes around CS
* Added missing keyring dependency in the TOML file
* Added requirements.txt file
* Renamed the 'process_entry' public function in the notification manager class to 'notify'
* Added a ModuleStatus enum to the utils file
* Added different email body and subject for metrics and modules
* Modules now remain in the notification queue until cleared even if they are configured with 'frequency' once
* Version bump to 0.5.1

## 0.5.0 (2023-02-19)

* Added logic to interpret the value of the notification_console parameter in the Console Manager
* Added SessionRunMode Enum
* Added a sample JSON configuration file
* Moved to using a JSON based configuration file
* Moved user configurable fields and command line options to be specified in the JSON based configuration file
* Modules can now be enabled or disabled in the configuration file settings
* Fixed an issue where frequency and configuration range value were interchanged in email notifications
* Renamed the config.py file to globals.py
* Renamed the plugins sections in the Console to Victron System, NMEA0183 Network and GPS Module
* Added code to retrieve notification_cool_off_interval configuration value on startup
* Improved the way notifications are handled in the Notification Manager by using the concept of cool off interval in
  the add phase of a notification
* Switched from using timers in the Notification Manager to using a continuous thread instead
* Updated README file
* Version bump to 0.5.0

## 0.4.7 (2023-02-15)

* Added support for notifications for when plugins go offline
* Increased the GPS timer interval to 5 seconds
* Renamed the Colouring Scheme and Notification Rules configuration parameters to Metrics Colouring Scheme and Metrics
  Notification Rules respectively
* Added Module specific configuration rules section in the config file
* Improved the logic in the GPS plugin that detects the plugin state
* Moved the logic to handle sending emails to the utils file
* Version bump to 0.4.7

## 0.4.6 (2023-02-15)

* Introduced prefixed to help with module metrics identification
* Introduced the following metrics to the GPS plugin: SOG, COG, Distance from last entry, Cumulative distance, Average
  SOG
* Version bump to 0.4.6

## 0.4.5 (2023-02-15)

* Changed the reported field headers for the GPS module to be prefixed with SERIAL and the corresponding headers from
  the NMEA module to be prefixed with NMEA
* An additional snapshot is now taken right before the session ends
* Version bump to 0.4.5

## 0.4.4 (2023-02-15)

* Added notification cool off feature to help with suppressing notifications bursts. A configurable setting is now
  available in the notifications rules section in the config file
* Reordered the GPS latitude and longitude fields in the NMEA plugin to match with the GPS plugin order
* Changed the formatting of the GPS coordinates to remove extra zeros at the end of the seconds field
* Added 'cool-off-interval' command line option
* Normal entries in the rich console layout are now coloured 'bright_white' for better visibility
* Version bump to 0.4.4

## 0.4.3 (2023-02-14)

* Fixed Notification rules section in the config file
* Version bump to 0.4.3

## 0.4.2 (2023-02-14)

* Added feature to send a report email after the session ends with all the session generated files
* Added 'email-report' command line option
* Fixed the logic with handling exceptions in the GPS plugin
* Removed redundant variable assignment in the VictronPlugin class
* Version bump to 0.4.2

## 0.4.1 (2023-02-14)

* Changed the notification range for Tank 1 lvl
* Version bump to 0.4.1

## 0.4.0 (2023-02-14)

* Added email notification feature
* Added 'email-address' and 'email-password' command line options
* Changed 'log' to 'log-level' in the list of command line options
* Version bump to 0.4.0

## 0.3.1 (2023-02-14)

* Added the missing GPS module summary metrics in the summary section
* Version bump to 0.3.1

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


