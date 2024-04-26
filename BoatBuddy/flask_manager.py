import time
import datetime
import webbrowser
from flask import render_template, jsonify, request
from flask import send_file
from rich.console import Console

from BoatBuddy import app
from BoatBuddy import utils, globals
from BoatBuddy.anchor_manager import AnchorManager
from BoatBuddy.email_manager import EmailManager
from BoatBuddy.telegram_manager import TelegramManager
from BoatBuddy.generic_plugin import PluginStatus
from BoatBuddy.log_manager import LogManager
from BoatBuddy.notifications_manager import NotificationsManager, NotificationEvents, NotificationEntryType
from BoatBuddy.plugin_manager import PluginManager, PluginManagerStatus
from BoatBuddy.sound_manager import SoundManager, SoundType


class ApplicationModules:
    def __init__(self, options, log_manager: LogManager, sound_manager: SoundManager, email_manager: EmailManager,
                 notifications_manager: NotificationsManager, plugin_manager: PluginManager,
                 anchor_manager: AnchorManager, telegram_manager: TelegramManager):
        self._options = options
        self._log_manager = log_manager
        self._sound_manager = sound_manager
        self._email_manager = email_manager
        self._notifications_manager = notifications_manager
        self._plugin_manager = plugin_manager
        self._anchor_manager = anchor_manager
        self._telegram_manager = telegram_manager

    def get_options(self):
        return self._options

    def get_log_manager(self) -> LogManager:
        return self._log_manager

    def get_sound_manager(self) -> SoundManager:
        return self._sound_manager

    def get_email_manager(self) -> EmailManager:
        return self._email_manager

    def get_notifications_manager(self) -> NotificationsManager:
        return self._notifications_manager

    def get_plugin_manager(self) -> PluginManager:
        return self._plugin_manager

    def get_anchor_manager(self) -> AnchorManager:
        return self._anchor_manager

    def get_telegram_manager(self) -> TelegramManager:
        return self._telegram_manager


application_modules: ApplicationModules
notification_message = ''


class FlaskManager:
    def __init__(self, options):
        self._options = options

        # Create a console instance
        _console = Console()
        _console.print(f'[bright_yellow]Application is starting up. Please wait...[/bright_yellow]')

        with _console.status('[bold bright_yellow]Loading logging module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _log_manager = LogManager(self._options)
            _console.print(f'[green]Loading logging module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading sound module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _sound_manager = SoundManager(self._options, _log_manager)
            _console.print(f'[green]Loading sound module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading email module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _email_manager = EmailManager(self._options, _log_manager)
            _console.print(f'[green]Loading email module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading Telegram module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _telegram_manager = TelegramManager(self._options, _log_manager)
            _console.print(f'[green]Loading Telegram module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading notifications module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _notifications_manager = NotificationsManager(self._options, _log_manager, _sound_manager,
                                                          _email_manager, _telegram_manager)
            _console.print(f'[green]Loading notifications module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading plugins module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _plugin_manager = PluginManager(self._options, _log_manager, _notifications_manager, _sound_manager,
                                            _email_manager)
            _console.print(f'[green]Loading plugins module...Done[/green]')

        with _console.status('[bold bright_yellow]Loading anchor module...[/bold bright_yellow]'):
            time.sleep(0.1)
            _anchor_manager = AnchorManager(self._options, _log_manager, _plugin_manager, _email_manager,
                                            _notifications_manager)
            _console.print(f'[green]Loading anchor module...Done[/green]')

        with _console.status(f'[bold bright_yellow]Firing up web UI...[/bold bright_yellow]'):
            time.sleep(0.1)
            # Play the application started chime
            _sound_manager.play_sound_async(SoundType.APPLICATION_STARTED)
            _console.print(f'[green]Firing up web UI...Done[/green]')

        global application_modules
        application_modules = ApplicationModules(self._options, _log_manager, _sound_manager, _email_manager,
                                                 _notifications_manager, _plugin_manager,
                                                 _anchor_manager, _telegram_manager)

        if self._options.web_launch_browser_during_startup:
            webbrowser.open(f'http://localhost:{self._options.web_port}')

        app.run(debug=False, host='0.0.0.0', port=self._options.web_port)


def get_plugin_status_str(plugin_status: PluginStatus):
    plugin_status_str = ''
    if plugin_status == PluginStatus.DOWN:
        plugin_status_str = 'Down'
    elif plugin_status == PluginStatus.STARTING:
        plugin_status_str = 'Starting'
    elif plugin_status == PluginStatus.RUNNING:
        plugin_status_str = 'Running'
    return plugin_status_str


@app.route('/')
def index():
    # Get application name and version
    boat_name = application_modules.get_options().boat_name
    application_name = utils.get_application_name()
    application_version = utils.get_application_version()
    session_run_mode = str(application_modules.get_options().session_run_mode).lower()
    anchor_alarm_module = application_modules.get_options().anchor_alarm_module
    anchor_alarm_mapbox_api_key = application_modules.get_options().anchor_alarm_mapbox_api_key
    metrics_electrical_system = application_modules.get_options().metrics_electrical_system
    metrics_nmea = application_modules.get_options().metrics_nmea

    home_position_available = ((application_modules.get_options().gps_latitude_home and
                               application_modules.get_options().gps_longitude_home) and
                               (len(application_modules.get_options().gps_latitude_home) > 0 and
                                len(application_modules.get_options().gps_longitude_home) > 0))

    return render_template('index.html', boat_name=boat_name, application_name=application_name,
                           application_version=application_version,
                           session_run_mode=session_run_mode, anchor_alarm_module=anchor_alarm_module,
                           anchor_alarm_mapbox_api_key=anchor_alarm_mapbox_api_key,
                           metrics_electrical_system=metrics_electrical_system, metrics_nmea=metrics_nmea,
                           home_position_available=home_position_available)


def is_json_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'json'


@app.route('/upload_config', methods=['GET', 'POST'])
def upload_config():
    if 'config_file' in request.files:
        file = request.files['config_file']
        if file and is_json_file(file.filename):
            try:
                file.save(application_modules.get_options().configuration_path)
                # Store the uploaded JSON file on your server
                return 'System configuration updated successfully!'
            except Exception as e:
                return f'Error while trying to update the configuration on the server. Details: {e}'
    return 'Invalid file type'


@app.route('/configuration')
def download_config():
    filename = application_modules.get_options().configuration_path
    return send_file(filename, as_attachment=True)


@app.route('/toggle_session')
def start_stop_session():
    if not str(application_modules.get_options().session_run_mode).lower() == globals.SessionRunMode.MANUAL.value:
        return

    if application_modules.get_plugin_manager().get_status() == PluginManagerStatus.IDLE:
        application_modules.get_plugin_manager().start_session()
    elif application_modules.get_plugin_manager().get_status() == PluginManagerStatus.SESSION_ACTIVE:
        application_modules.get_plugin_manager().end_session()

    return jsonify({})


@app.route('/anchor_alarm_data')
def get_anchor_alarm_data():
    anchor_is_set = False
    anchor_alarm_is_active = False
    anchor_allowed_distance = 0
    anchor_distance = 0
    anchor_latitude = ''
    anchor_longitude = ''
    current_latitude = ''
    current_longitude = ''
    anchor_alarm_default_allowed_distance = ''
    anchor_timestamp_utc = ''
    anchor_timestamp_local = ''
    anchor_alarm_module = application_modules.get_options().anchor_alarm_module
    gps_module_running = False
    position_history = []
    anchor_duration_in_seconds = 0
    anchor_bearing = 0
    gps_accuracy = 'N/A'
    max_anchor_distance = 0

    if application_modules.get_options().anchor_alarm_module:
        gps_module_running = application_modules.get_plugin_manager().get_gps_plugin_status() == PluginStatus.RUNNING
        anchor_alarm_default_allowed_distance = application_modules.get_options().anchor_alarm_default_allowed_distance
        anchor_is_set = application_modules.get_anchor_manager().anchor_is_set()
        anchor_timestamp_utc = application_modules.get_anchor_manager().anchor_timestamp_utc()
        anchor_timestamp_local = application_modules.get_anchor_manager().anchor_timestamp_local()
        anchor_alarm_is_active = application_modules.get_anchor_manager().anchor_alarm_is_active()
        anchor_allowed_distance = application_modules.get_anchor_manager().anchor_allowed_distance()
        anchor_distance = application_modules.get_anchor_manager().anchor_distance()
        anchor_latitude = application_modules.get_anchor_manager().anchor_latitude()
        anchor_longitude = application_modules.get_anchor_manager().anchor_longitude()
        current_latitude = application_modules.get_anchor_manager().current_latitude()
        current_longitude = application_modules.get_anchor_manager().current_longitude()
        position_history = application_modules.get_anchor_manager().position_history()
        anchor_duration_in_seconds = application_modules.get_anchor_manager().anchor_duration_in_seconds()
        anchor_bearing = application_modules.get_anchor_manager().anchor_bearing()
        gps_accuracy = application_modules.get_anchor_manager().gps_accuracy()
        max_anchor_distance = application_modules.get_anchor_manager().max_anchor_distance()

    data = {'data_format_version': globals.JSON_RESPONSE_FORMAT_VERSION,
            'gps_module_running': gps_module_running, 'anchor_alarm_module': anchor_alarm_module,
            'anchor_is_set': anchor_is_set,
            'anchor_timestamp_utc': anchor_timestamp_utc, 'anchor_timestamp_local': anchor_timestamp_local,
            'anchor_alarm_is_active': anchor_alarm_is_active,
            'anchor_allowed_distance': anchor_allowed_distance, 'anchor_distance': anchor_distance,
            'anchor_latitude': anchor_latitude, 'anchor_longitude': anchor_longitude,
            'anchor_alarm_default_allowed_distance': anchor_alarm_default_allowed_distance,
            'current_latitude': current_latitude, 'current_longitude': current_longitude,
            'position_history': position_history, 'anchor_duration_in_seconds': anchor_duration_in_seconds,
            'anchor_bearing': anchor_bearing, 'gps_accuracy': gps_accuracy, 'max_anchor_distance': max_anchor_distance}

    return jsonify(data)


@app.route('/gps_coordinates')
def get_gps_coordinates():
    gps_latitude = ''
    gps_longitude = ''

    gps_entry = application_modules.get_plugin_manager().get_gps_plugin_metrics()
    if len(gps_entry) > 0:
        gps_latitude = gps_entry[0]
        gps_longitude = gps_entry[1]

    data = {'data_format_version': globals.JSON_RESPONSE_FORMAT_VERSION, 'gps_latitude': gps_latitude,
            'gps_longitude': gps_longitude}

    return jsonify(data)


@app.route('/home_gps_coordinates')
def get_home_gps_coordinates():
    gps_latitude = application_modules.get_options().gps_latitude_home
    gps_longitude = application_modules.get_options().gps_longitude_home

    data = {'data_format_version': globals.JSON_RESPONSE_FORMAT_VERSION, 'gps_latitude': gps_latitude,
            'gps_longitude': gps_longitude}

    return jsonify(data)


@app.route('/set_anchor', methods=['POST'])
def set_anchor():
    latitude = request.form.get('latitude')  # Get the latitude value from the request
    longitude = request.form.get('longitude')  # Get the longitude value from the request
    allowed_distance = request.form.get('allowed_distance')  # Get the allowed distance value from the request
    preserve_history = False
    if 'preserve_history' in request.form:
        preserve_history = utils.try_parse_bool(request.form.get('preserve_history'))

    return jsonify(
        application_modules.get_anchor_manager().set_anchor(latitude, longitude, utils.try_parse_int(allowed_distance),
                                                            preserve_history))


@app.route('/set_anchor_alternative', methods=['POST'])
def set_anchor_alternative():
    # Get current GPS coordinates
    gps_latitude = ''
    gps_longitude = ''

    gps_entry = application_modules.get_plugin_manager().get_gps_plugin_metrics()
    if len(gps_entry) > 0:
        gps_latitude = gps_entry[0]
        gps_longitude = gps_entry[1]

    bearing = request.form.get('bearing')  # Get the bearing value from the request
    distance = request.form.get('distance')  # Get the distance value from the request
    allowed_distance = request.form.get('allowed_distance')  # Get the allowed distance value from the request

    return jsonify(
        application_modules.get_anchor_manager().set_anchor_alternative(gps_latitude, gps_longitude,
                                                                        utils.try_parse_int(bearing),
                                                                        utils.try_parse_int(distance),
                                                                        utils.try_parse_int(allowed_distance)))


@app.route('/reset_max_anchor_distance')
def reset_max_anchor_distance():
    application_modules.get_anchor_manager().reset_max_anchor_distance()

    return jsonify(True)


@app.route('/cancel_anchor')
def cancel_anchor():
    application_modules.get_anchor_manager().cancel_anchor()

    return jsonify(True)


@app.route('/current_time')
def get_current_time():
    curr_time = time.strftime("%H:%M:%S", time.localtime())

    data = {'data_format_version': globals.JSON_RESPONSE_FORMAT_VERSION, 'curr_time': curr_time}
    return jsonify(data)


@app.route('/nmea_data')
def get_nmea_data():
    heading = ""
    true_wind_speed = ""
    true_wind_direction = ""
    apparent_wind_speed = ""
    apparent_wind_angle = ""
    latitude = ""
    longitude = ""
    water_temperature = ""
    depth = ""
    speed_over_ground = ""
    speed_over_water = ""
    nmea_module = False
    nmea_status = ""

    if application_modules.get_options().nmea_module:
        nmea_module = True
        plugin_status = application_modules.get_plugin_manager().get_nmea_plugin_status()
        nmea_status = get_plugin_status_str(plugin_status)

        nmea_metrics = application_modules.get_plugin_manager().get_nmea_plugin_metrics()
        if nmea_metrics and len(nmea_metrics) > 0:
            if nmea_metrics[0] != globals.EMPTY_METRIC_VALUE:
                heading = nmea_metrics[0]

            if nmea_metrics[1] != globals.EMPTY_METRIC_VALUE:
                true_wind_speed = nmea_metrics[1]

            if nmea_metrics[2] != globals.EMPTY_METRIC_VALUE:
                true_wind_direction = nmea_metrics[2]

            if nmea_metrics[3] != globals.EMPTY_METRIC_VALUE:
                apparent_wind_speed = nmea_metrics[3]

            if nmea_metrics[4] != globals.EMPTY_METRIC_VALUE:
                apparent_wind_angle = nmea_metrics[4]

            if nmea_metrics[5] != globals.EMPTY_METRIC_VALUE and nmea_metrics[6] != globals.EMPTY_METRIC_VALUE:
                latitude = nmea_metrics[5]
                longitude = nmea_metrics[6]

            if nmea_metrics[7] != globals.EMPTY_METRIC_VALUE:
                water_temperature = nmea_metrics[7]

            if nmea_metrics[8] != globals.EMPTY_METRIC_VALUE:
                depth = nmea_metrics[8]

            if nmea_metrics[9] != globals.EMPTY_METRIC_VALUE:
                speed_over_ground = nmea_metrics[9]

            if nmea_metrics[10] != globals.EMPTY_METRIC_VALUE:
                speed_over_water = nmea_metrics[10]

    data = {'data_format_version': globals.JSON_RESPONSE_FORMAT_VERSION,
            'nmea_status': nmea_status, 'nmea_module': nmea_module, 'heading': heading,
            'true_wind_speed': true_wind_speed, 'true_wind_direction': true_wind_direction,
            'apparent_wind_speed': apparent_wind_speed, 'apparent_wind_angle': apparent_wind_angle,
            'latitude': latitude, 'longitude': longitude, 'water_temperature': water_temperature,
            'depth': depth, 'speed_over_ground': speed_over_ground, 'speed_over_water': speed_over_water}

    return jsonify(data)


@app.route('/data')
def get_data():
    status = application_modules.get_plugin_manager().get_status().value

    web_theme = str(application_modules.get_options().web_theme).lower()
    sunrise_time = str(application_modules.get_options().web_sunrise)
    sunset_time = str(application_modules.get_options().web_sunset)

    current_time = datetime.datetime.now()
    day_light = False
    if sunrise_time <= current_time.strftime('%H:%M') <= sunset_time:
        day_light = True

    victron_modbus_tcp_module = False
    victron_ble_module = False
    victron_modbus_tcp_status = ''
    victron_ble_status = ''
    active_input_source = 'N/A'
    ve_bus_state = 'N/A'
    housing_battery_state = 'N/A'
    pv_current = 0
    housing_battery_soc = 0
    housing_battery_voltage = 0.0
    housing_battery_current = 0
    housing_battery_power = 0
    starter_battery_voltage = 0.0
    housing_battery_consumed_ah = 0
    housing_battery_remaining_mins = 0
    auxiliary_temperature = 0
    fuel_tank = 0
    water_tank = 0
    pv_power = 0
    if application_modules.get_options().victron_modbus_tcp_module:
        victron_modbus_tcp_module = True
        # Populate the victron layout
        plugin_status = application_modules.get_plugin_manager().get_victron_modbus_tcp_plugin_status()
        victron_modbus_tcp_status = get_plugin_status_str(plugin_status)
        victron_modbus_tcp_metrics = application_modules.get_plugin_manager().get_victron_modbus_tcp_plugin_metrics()
        if victron_modbus_tcp_metrics and len(victron_modbus_tcp_metrics) > 0:
            active_input_source = victron_modbus_tcp_metrics[0]
            ve_bus_state = victron_modbus_tcp_metrics[6]
            housing_battery_state = victron_modbus_tcp_metrics[12]

            if (str(application_modules.get_options().data_source_housing_battery_voltage).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                housing_battery_voltage = utils.try_parse_float(victron_modbus_tcp_metrics[8])

            if (str(application_modules.get_options().data_source_housing_battery_current).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                housing_battery_current = utils.try_parse_float(victron_modbus_tcp_metrics[9])

            if (str(application_modules.get_options().data_source_housing_battery_power).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                housing_battery_power = utils.try_parse_float(victron_modbus_tcp_metrics[10])

            if (str(application_modules.get_options().data_source_housing_battery_soc).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                housing_battery_soc = utils.try_parse_int(victron_modbus_tcp_metrics[11])

            if (str(application_modules.get_options().data_source_starter_battery_voltage).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                starter_battery_voltage = utils.try_parse_float(victron_modbus_tcp_metrics[15])
            pv_power = utils.try_parse_int(victron_modbus_tcp_metrics[13])
            pv_current = utils.try_parse_float(victron_modbus_tcp_metrics[14])
            fuel_tank = utils.try_parse_int(victron_modbus_tcp_metrics[16])
            water_tank = utils.try_parse_int(victron_modbus_tcp_metrics[18])

    if application_modules.get_options().victron_ble_module:
        victron_ble_module = True

        # Populate the victron layout
        plugin_status = application_modules.get_plugin_manager().get_victron_ble_plugin_status()
        victron_ble_status = get_plugin_status_str(plugin_status)
        victron_ble_metrics = application_modules.get_plugin_manager().get_victron_ble_plugin_metrics()

        if victron_ble_metrics and len(victron_ble_metrics) > 0:
            if (str(application_modules.get_options().data_source_housing_battery_voltage).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                housing_battery_voltage = utils.try_parse_float(victron_ble_metrics[0])

            if (str(application_modules.get_options().data_source_housing_battery_current).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                housing_battery_current = utils.try_parse_float(victron_ble_metrics[1])

            if (str(application_modules.get_options().data_source_housing_battery_power).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                housing_battery_power = utils.try_parse_float(victron_ble_metrics[2])

            if (str(application_modules.get_options().data_source_housing_battery_soc).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                housing_battery_soc = utils.try_parse_float(victron_ble_metrics[3])

            if (str(application_modules.get_options().data_source_starter_battery_voltage).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                starter_battery_voltage = utils.try_parse_float(victron_ble_metrics[4])

            housing_battery_consumed_ah = utils.try_parse_float(victron_ble_metrics[5])
            housing_battery_remaining_mins = utils.try_parse_int(victron_ble_metrics[6])
            auxiliary_temperature = utils.try_parse_int(victron_ble_metrics[7])

    nmea_module = False
    nmea_status = ''
    if application_modules.get_options().nmea_module:
        nmea_module = True
        plugin_status = application_modules.get_plugin_manager().get_nmea_plugin_status()
        nmea_status = get_plugin_status_str(plugin_status)

    gps_module = False
    gps_status = ''

    if application_modules.get_options().gps_module:
        gps_module = True
        plugin_status = application_modules.get_plugin_manager().get_gps_plugin_status()
        gps_status = get_plugin_status_str(plugin_status)

    # Collect session information
    session_name = ''
    start_time = ''
    start_time_utc = ''
    duration = ''
    start_gps_lat = ''
    start_gps_lon = ''
    distance = ''
    heading = ''
    average_wind_speed = ''
    average_wind_direction = ''
    average_water_temperature = ''
    average_depth = ''
    average_sog = ''
    average_sow = ''
    housing_battery_max_voltage = ''
    housing_battery_min_voltage = ''
    housing_battery_avg_voltage = ''
    housing_battery_max_current = ''
    housing_battery_min_current = ''
    housing_battery_avg_current = ''
    housing_battery_max_soc = ''
    housing_battery_min_soc = ''
    housing_battery_avg_soc = ''
    housing_battery_max_consumed_ah = ''
    housing_battery_min_consumed_ah = ''
    housing_battery_avg_consumed_ah = ''
    housing_battery_avg_remaining_mins = ''
    housing_battery_max_power = ''
    housing_battery_min_power = ''
    housing_battery_avg_power = ''
    pv_max_power = ''
    pv_avg_power = ''
    pv_max_current = ''
    pv_avg_current = ''
    starter_battery_max_voltage = ''
    starter_battery_min_voltage = ''
    starter_battery_avg_voltage = ''
    tank1_max_level = ''
    tank1_min_level = ''
    tank1_avg_level = ''
    tank2_max_level = ''
    tank2_min_level = ''
    tank2_avg_level = ''
    if application_modules.get_plugin_manager().get_status() == PluginManagerStatus.SESSION_ACTIVE:
        session_name = application_modules.get_plugin_manager().get_session_name()
        session_clock_metrics = application_modules.get_plugin_manager().get_session_clock_metrics()
        session_summary_metrics = application_modules.get_plugin_manager().get_session_summary_metrics()
        start_time = session_clock_metrics['Start Time (Local)']
        start_time_utc = session_clock_metrics['Start Time (UTC)']
        duration = session_clock_metrics['Duration']

        if application_modules.get_options().nmea_module:
            start_gps_lat = session_summary_metrics['[NM] Start GPS Lat (d°m\'S\" H)']
            start_gps_lon = session_summary_metrics['[NM] Start GPS Lon (d°m\'S\" H)']
            distance = session_summary_metrics['[NM] Dst. (miles)']
            heading = session_summary_metrics['[NM] Hdg. (°)']
            average_wind_speed = session_summary_metrics['[NM] Avg. Wind Speed (kts)']
            average_wind_direction = session_summary_metrics['[NM] Avg. Wind Direction (°)']
            average_water_temperature = session_summary_metrics['[NM] Avg. Water Temp. (°C)']
            average_depth = session_summary_metrics['[NM] Avg. Depth (m)']
            average_sog = session_summary_metrics['[NM] Avg. SOG (kts)']
            average_sow = session_summary_metrics['[NM] Avg. SOW (kts)']

        if application_modules.get_options().victron_ble_module:
            if (str(application_modules.get_options().data_source_housing_battery_voltage).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                housing_battery_max_voltage = session_summary_metrics['[BLE] Housing batt. max voltage (V)']
                housing_battery_min_voltage = session_summary_metrics['[BLE] Housing batt. min voltage (V)']
                housing_battery_avg_voltage = session_summary_metrics['[BLE] Housing batt. avg. voltage (V)']

            if (str(application_modules.get_options().data_source_housing_battery_current).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                housing_battery_max_current = session_summary_metrics['[BLE] Housing batt. max current (A)']
                housing_battery_min_current = session_summary_metrics['[BLE] Housing batt. min current (A)']
                housing_battery_avg_current = session_summary_metrics['[BLE] Housing batt. avg. current (A)']

            if (str(application_modules.get_options().data_source_housing_battery_power).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                housing_battery_max_power = session_summary_metrics['[BLE] Housing batt. max power (W)']
                housing_battery_min_power = session_summary_metrics['[BLE] Housing batt. min power (W)']
                housing_battery_avg_power = session_summary_metrics['[BLE] Housing batt. avg. power (W)']

            if (str(application_modules.get_options().data_source_starter_battery_voltage).lower() ==
                    globals.DataSource.VICTRON_BLE.value):
                starter_battery_max_voltage = session_summary_metrics['[BLE] Starter batt. max voltage (V)']
                starter_battery_min_voltage = session_summary_metrics['[BLE] Starter batt. min voltage (V)']
                starter_battery_avg_voltage = session_summary_metrics['[BLE] Starter batt. min voltage (V)']

            housing_battery_max_soc = session_summary_metrics['[BLE] Housing batt. max SOC']
            housing_battery_min_soc = session_summary_metrics['[BLE] Housing batt. min SOC']
            housing_battery_avg_soc = session_summary_metrics['[BLE] Housing batt. avg. SOC']
            housing_battery_max_consumed_ah = session_summary_metrics['[BLE] Housing batt. max consumed Ah']
            housing_battery_min_consumed_ah = session_summary_metrics['[BLE] Housing batt. min consumed Ah']
            housing_battery_avg_consumed_ah = session_summary_metrics['[BLE] Housing batt. avg. consumed Ah']
            housing_battery_avg_remaining_mins = session_summary_metrics['[BLE] Housing batt. avg. remaining mins']

        if application_modules.get_options().victron_modbus_tcp_module:
            if (str(application_modules.get_options().data_source_housing_battery_voltage).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                housing_battery_max_voltage = session_summary_metrics['[GX] Batt. max voltage (V)']
                housing_battery_min_voltage = session_summary_metrics['[GX] Batt. min voltage (V)']
                housing_battery_avg_voltage = session_summary_metrics['[GX] Batt. avg. voltage (V)']

            if (str(application_modules.get_options().data_source_housing_battery_current).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                housing_battery_max_current = session_summary_metrics['[GX] Batt. max current (A)']
                housing_battery_min_current = session_summary_metrics['[GX] Batt. min current (A)']
                housing_battery_avg_current = session_summary_metrics['[GX] Batt. avg. current (A)']

            if (str(application_modules.get_options().data_source_starter_battery_voltage).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                starter_battery_max_voltage = session_summary_metrics['[GX] Strt. batt. max voltage (V)']
                starter_battery_min_voltage = session_summary_metrics['[GX] Strt. batt. min voltage (V)']
                starter_battery_avg_voltage = session_summary_metrics['[GX] Strt. batt. avg. voltage']

            if (str(application_modules.get_options().data_source_housing_battery_power).lower() ==
                    globals.DataSource.VICTRON_MODBUS_TCP.value):
                housing_battery_max_power = session_summary_metrics['[GX] Batt. max power (W)']
                housing_battery_min_power = session_summary_metrics['[GX] Batt. min power (W)']
                housing_battery_avg_power = session_summary_metrics['[GX] Batt. avg. power (W)']
            pv_max_power = session_summary_metrics['[GX] PV max power (W)']
            pv_avg_power = session_summary_metrics['[GX] PV avg. power']
            pv_max_current = session_summary_metrics['[GX] PV max current (A)']
            pv_avg_current = session_summary_metrics['[GX] PV avg. current (A)']
            tank1_max_level = session_summary_metrics['[GX] Tank 1 max lvl']
            tank1_min_level = session_summary_metrics['[GX] Tank 1 min lvl']
            tank1_avg_level = session_summary_metrics['[GX] Tank 1 avg. lvl']
            tank2_max_level = session_summary_metrics['[GX] Tank 2 max lvl']
            tank2_min_level = session_summary_metrics['[GX] Tank 2 min lvl']
            tank2_avg_level = session_summary_metrics['[GX] Tank 2 avg. lvl']

    last_notification = ''
    global notification_message
    if notification_message != application_modules.get_notifications_manager().get_last_message():
        notification_message = application_modules.get_notifications_manager().get_last_message()
        last_notification = notification_message

    data = {'data_format_version': globals.JSON_RESPONSE_FORMAT_VERSION,
            'web_theme': web_theme, 'day_light': day_light, 'victron_modbus_tcp_module': victron_modbus_tcp_module,
            'victron_ble_module': victron_ble_module,
            'housing_battery_soc': housing_battery_soc,
            'housing_battery_voltage': housing_battery_voltage,
            'victron_ble_status': victron_ble_status,
            'victron_modbus_tcp_status': victron_modbus_tcp_status,
            'fuel_tank': fuel_tank, 'water_tank': water_tank,
            'starter_battery_voltage': starter_battery_voltage,
            'pv_power': pv_power,
            'active_input_source': active_input_source, 've_bus_state': ve_bus_state,
            'housing_battery_consumed_ah': housing_battery_consumed_ah,
            'housing_battery_remaining_mins': housing_battery_remaining_mins,
            'auxiliary_temperature': auxiliary_temperature,
            'housing_battery_state': housing_battery_state,
            'housing_battery_current': housing_battery_current,
            'housing_battery_power': housing_battery_power,
            'pv_current': pv_current, 'status': status, 'nmea_module': nmea_module, 'nmea_status': nmea_status,
            'gps_module': gps_module, 'gps_status': gps_status,
            'session_name': session_name, 'start_time': start_time,
            'start_time_utc': start_time_utc, 'duration': duration, 'start_gps_lat': start_gps_lat,
            'start_gps_lon': start_gps_lon, 'distance': distance, 'heading': heading,
            'average_wind_speed': average_wind_speed, 'average_wind_direction': average_wind_direction,
            'average_water_temperature': average_water_temperature, 'average_depth': average_depth,
            'average_sog': average_sog, 'average_sow': average_sow,
            'housing_battery_max_voltage': housing_battery_max_voltage,
            'housing_battery_min_voltage': housing_battery_min_voltage,
            'housing_battery_avg_voltage': housing_battery_avg_voltage,
            'housing_battery_max_current': housing_battery_max_current,
            'housing_battery_min_current': housing_battery_min_current,
            'housing_battery_avg_current': housing_battery_avg_current,
            'housing_battery_max_power': housing_battery_max_power,
            'housing_battery_min_power': housing_battery_min_power,
            'housing_battery_avg_power': housing_battery_avg_power,
            'housing_battery_max_soc': housing_battery_max_soc,
            'housing_battery_min_soc': housing_battery_min_soc,
            'housing_battery_avg_soc': housing_battery_avg_soc,
            'housing_battery_max_consumed_ah': housing_battery_max_consumed_ah,
            'housing_battery_min_consumed_ah': housing_battery_min_consumed_ah,
            'housing_battery_avg_consumed_ah': housing_battery_avg_consumed_ah,
            'housing_battery_avg_remaining_mins': housing_battery_avg_remaining_mins,
            'pv_max_power': pv_max_power, 'pv_avg_power': pv_avg_power, 'pv_max_current': pv_max_current,
            'pv_avg_current': pv_avg_current, 'starter_battery_max_voltage': starter_battery_max_voltage,
            'starter_battery_min_voltage': starter_battery_min_voltage,
            'starter_battery_avg_voltage': starter_battery_avg_voltage,
            'tank1_max_level': tank1_max_level, 'tank1_min_level': tank1_min_level, 'tank1_avg_level': tank1_avg_level,
            'tank2_max_level': tank2_max_level, 'tank2_min_level': tank2_min_level, 'tank2_avg_level': tank2_avg_level,
            'last_notification': last_notification}
    return jsonify(data)
