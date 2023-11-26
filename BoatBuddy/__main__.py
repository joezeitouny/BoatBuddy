import json
import logging
import optparse
import os

from BoatBuddy import globals, utils
from BoatBuddy.console_manager import ConsoleManager
from BoatBuddy.database_manager import DatabaseWrapper
from BoatBuddy.flask_manager import FlaskManager

if __name__ == '__main__':
    # Create an options list using the Options Parser
    parser = optparse.OptionParser()
    parser.set_description(f'Version {globals.APPLICATION_VERSION}. '
                           f'A suite of tools to help collecting NMEA0183 and other marine metrics in a digital '
                           f'logbook format.')
    parser.set_usage("python3 -m BoatBuddy --config=CONFIGURATION_PATH")
    parser.add_option('--config', dest='configuration_path', type='string', help=f'Path to the configuration file')

    (options, args) = parser.parse_args()
    if not options.configuration_path:
        print(f'Invalid argument: Configuration path is a required argument\r\n')
        parser.print_help()
    elif not os.path.exists(options.configuration_path):
        print(f'Invalid argument: Valid JSON configuration file path is required\r\n')
        parser.print_help()
    else:
        try:
            # Open the configuration JSON file
            f = open(f'{options.configuration_path}')

            # returns JSON object as
            # a dictionary
            data = json.load(f)

            options.output_path = data['output_path']
            options.tmp_path = data['tmp_path']
            options.filename_prefix = data['filename_prefix']
            options.summary_filename_prefix = data['summary_filename_prefix']
            options.excel = utils.try_parse_bool(data['output_to_excel'])
            options.csv = utils.try_parse_bool(data['output_to_csv'])
            options.gpx = utils.try_parse_bool(data['output_to_gpx'])
            options.web_module = utils.try_parse_bool(data['web_application']['web_module'])
            options.web_host = data['web_application']['web_host']
            options.web_port = data['web_application']['web_port']
            options.web_theme = data['web_application']['web_theme']
            options.web_sunrise = data['web_application']['web_sunrise']
            options.web_sunset = data['web_application']['web_sunset']
            options.nmea_module = utils.try_parse_bool(data['nmea']['nmea_module'])
            options.nmea_server_ip = data['nmea']['nmea_server_ip']
            options.nmea_server_port = utils.try_parse_int(data['nmea']['nmea_server_port'])
            options.victron_module = utils.try_parse_bool(data['victron']['victron_module'])
            options.victron_server_ip = data['victron']['victron_server_ip']
            options.victron_tcp_port = utils.try_parse_int(data['victron']['victron_tcp_port'])
            options.gps_module = utils.try_parse_bool(data['gps']['gps_module'])
            options.gps_serial_port = data['gps']['gps_serial_port']
            options.anchor_alarm_module = utils.try_parse_bool(data['anchor_alarm']['anchor_alarm_module'])
            options.anchor_alarm_default_allowed_distance = \
                utils.try_parse_int(data['anchor_alarm']['anchor_alarm_default_allowed_distance'])
            options.anchor_alarm_mapbox_api_key = data['anchor_alarm']['anchor_alarm_mapbox_api_key']
            options.database_module = utils.try_parse_bool(data['database']['database_module'])
            options.database_name = data['database']['database_name']
            options.database_host = data['database']['database_host']
            options.database_user = data['database']['database_user']
            options.database_password = data['database']['database_password']
            options.database_wrapper = data['database']['database_wrapper']
            options.database_live_feed_entry_interval = \
                utils.try_parse_int(data['database']['database_live_feed_entry_interval'])
            options.database_cleanup_events = utils.try_parse_bool(data['database']['database_cleanup_events'])
            options.database_log_table_limit = utils.try_parse_int(data['database']['database_log_table_limit'])
            options.database_event_table_limit = utils.try_parse_int(data['database']['database_event_table_limit'])
            options.console_show_victron_plugin = utils.try_parse_bool(data['console']['console_show_victron_plugin'])
            options.console_show_nmea_plugin = utils.try_parse_bool(data['console']['console_show_nmea_plugin'])
            options.console_show_gps_plugin = utils.try_parse_bool(data['console']['console_show_gps_plugin'])
            options.console_show_log = utils.try_parse_bool(data['console']['console_show_log'])
            options.console_session_header_fields = data['console']['console_session_header_fields']
            options.console_victron_summary_fields = data['console']['console_victron_summary_fields']
            options.console_nmea_summary_fields = data['console']['console_nmea_summary_fields']
            options.console_gps_summary_fields = data['console']['console_gps_summary_fields']
            options.console_victron_metrics = data['console']['console_victron_metrics']
            options.console_nmea_metrics = data['console']['console_nmea_metrics']
            options.console_gps_metrics = data['console']['console_gps_metrics']
            options.email_module = utils.try_parse_bool(data['email']['email_module'])
            options.email_address = data['email']['email_address']
            options.email_password = data['email']['email_password']
            options.telegram_module = utils.try_parse_bool(data['telegram']['telegram_module'])
            options.telegram_bot_token = data['telegram']['telegram_bot_token']
            options.telegram_recipient_id = data['telegram']['telegram_recipient_id']
            options.email_session_report = utils.try_parse_bool(data['email']['email_session_report'])
            options.notifications_module = utils.try_parse_bool(data['notification']['notifications_module'])
            options.notification_email = utils.try_parse_bool(data['notification']['notification_email'])
            options.notification_sound = utils.try_parse_bool(data['notification']['notification_sound'])
            options.notification_console = utils.try_parse_bool(data['notification']['notification_console'])
            options.notification_cool_off_interval = utils.try_parse_int(
                data['notification']['notification_cool_off_interval'])
            options.session_module = utils.try_parse_bool(data['session']['session_module'])
            options.session_run_mode = data['session']['session_run_mode']
            options.session_disk_write_interval = utils.try_parse_int(data['session']['session_disk_write_interval'])
            options.session_summary_report = utils.try_parse_bool(data['session']['session_summary_report'])
            options.session_paging_interval = utils.try_parse_int(data['session']['session_paging_interval'])
            options.log_module = utils.try_parse_bool(data['log']['log_module'])
            options.log_level = data['log']['log_level']
            options.sound_module = utils.try_parse_bool(data['sound']['sound_module'])
            options.metrics_electrical_system = data['metrics']['metrics_electrical_system']
            options.metrics_nmea = data['metrics']['metrics_nmea']
            options.metrics_colouring_scheme = data['metrics']['metrics_colouring_scheme']
            options.metrics_notifications_rules = data['metrics']['metrics_notifications_rules']
            options.modules_notifications_rules = data['modules']['modules_notifications_rules']
        except Exception as e:
            print(f'Error while parsing the specified JSON configuration file. Details {e}\r\n')
            parser.print_help()
            quit()

        log_numeric_level = getattr(logging, options.log_level.upper(), None)
        if not options.output_path:
            print(f'Invalid argument: Output directory defined in OUTPUT_PATH is required.\r\n')
            parser.print_help()
        elif not isinstance(log_numeric_level, int):
            print(f'Invalid argument: Log level "{options.log_level}"')
            parser.print_help()
        elif not options.excel and not options.gpx and not options.csv and not options.session_summary_report:
            print(f'Invalid argument: At least one output medium needs to be specified\r\n')
            parser.print_help()
        elif options.web_module and not options.web_theme:
            print(f'Invalid argument: Web theme option must be specified')
            parser.print_help()
        elif options.web_module and not (str(options.web_theme).lower() == "auto" or
                                         str(options.web_theme).lower() == "dark" or
                                         str(options.web_theme).lower() == "light"):
            print(f'Invalid argument: Invalid web theme option')
            parser.print_help()
        elif options.nmea_module and not (options.nmea_server_ip and options.nmea_server_port):
            print(f'Invalid argument: NMEA server IP and port need to be configured to be able to use the NMEA '
                  f'module\r\n')
            parser.print_help()
        elif options.victron_module and not (options.victron_server_ip and options.victron_tcp_port):
            print(f'Invalid argument: Victron server IP and port need to be configured to be able to use the '
                  f'victron module\r\n')
            parser.print_help()
        elif options.gps_module and not options.gps_serial_port:
            print(f'Invalid argument: GPS serial port need to be configured to be able to use the GPS module\r\n')
            parser.print_help()
        elif options.database_module and options.database_wrapper != DatabaseWrapper.MYSQL.value:
            print(f'Invalid argument: Invalid database wrapper value provided\r\n')
            parser.print_help()
        elif options.database_module and (not options.database_host or not options.database_name
                                          or not options.database_user or not options.database_password
                                          or options.database_live_feed_entry_interval == 0):
            print(f'Invalid argument: All database module configuration need to be supplied '
                  f'in order to this feature\r\n')
            parser.print_help()
        elif str(options.session_run_mode).lower() == globals.SessionRunMode.AUTO_NMEA.value and \
                not options.nmea_module:
            print(f'Invalid argument: Cannot use the \'auto-nmea\' session run mode ' +
                  f'when the NMEA module is disabled\r\n')
            parser.print_help()
        elif str(options.session_run_mode).lower() == globals.SessionRunMode.AUTO_VICTRON.value and \
                not options.victron_module:
            print(f'Invalid argument: Cannot use the \'auto-victron\' session run mode ' +
                  f'when the Victron module is disabled\r\n')
            parser.print_help()
        elif str(options.session_run_mode).lower() == globals.SessionRunMode.AUTO_GPS.value and not options.gps_module:
            print(f'Invalid argument: Cannot use the \'auto-gps\' session run mode ' +
                  f'when the GPS module is disabled\r\n')
            parser.print_help()
        elif options.session_disk_write_interval < globals.INITIAL_SNAPSHOT_INTERVAL:
            print(f'Invalid argument: Specified disk write interval cannot be less than ' +
                  f'{globals.INITIAL_SNAPSHOT_INTERVAL} seconds')
            parser.print_help()
        elif options.session_paging_interval < options.session_disk_write_interval:
            print(f'Invalid argument: Specified run mode interval time cannot be less than the value chosen for ' +
                  f'disk write interval which is {options.session_disk_write_interval} seconds')
            parser.print_help()
        elif options.email_module and not (options.email_address or options.email_password):
            print(f'Invalid argument: Email credentials need to be supplied in order to use the email module')
            parser.print_help()
        elif options.email_session_report and not options.email_module:
            print(f'Invalid argument: Email module needs to be activated in order to use the email report feature')
            parser.print_help()
        elif options.notifications_module and not options.notification_cool_off_interval:
            print(f'Invalid argument: Notification cool-off interval need to be provided if the '
                  f'notification module is turned on')
            parser.print_help()
        elif options.web_module and not (options.web_host or options.web_port):
            print(f'Invalid argument: Web module requires the host and port parameters to be provided')
            parser.print_help()
        elif options.anchor_alarm_module and not options.gps_module:
            print(f'Invalid argument: Anchor alarm module cannot be enabled without the GPS module being enabled too')
            parser.print_help()
        elif options.telegram_module and not options.telegram_bot_token and not options.telegram_recipient_id:
            print(f'Invalid argument: Telegram module requires the bot token and the recipient id '
                  f'parameters to be provided')
            parser.print_help()
        else:
            if options.web_module:
                FlaskManager(options)
            else:
                # Load the console manager
                ConsoleManager(options)
