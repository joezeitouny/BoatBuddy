import time
import copy
from enum import Enum
from threading import Thread, Event
import os
import json
from latloncalc.latlon import LatLon, Latitude, Longitude, string2latlon

from BoatBuddy.log_manager import LogManager
from BoatBuddy.plugin_manager import PluginManager
from BoatBuddy.email_manager import EmailManager
from BoatBuddy.generic_plugin import PluginStatus
from BoatBuddy.notifications_manager import NotificationsManager, NotificationEntryType
from BoatBuddy.utils import ModuleStatus
from BoatBuddy import utils, globals


class AnchorManagerStatus(Enum):
    STARTING = 1
    RUNNING = 2
    DOWN = 3


class AnchorManager:
    def __init__(self, options, log_manager: LogManager, plugin_manager: PluginManager, email_manager: EmailManager,
                 notifications_manager: NotificationsManager):
        self._options = options
        self._log_manager = log_manager
        self._plugin_manager = plugin_manager
        self._email_manager = email_manager
        self._notifications_manager = notifications_manager
        self._exit_signal = Event()
        self._status = AnchorManagerStatus.STARTING
        self._anchor_timestamp_utc = None
        self._anchor_timestamp_local = None
        self._anchor_latitude = ''
        self._anchor_longitude = ''
        self._anchor_allowed_distance = 0
        self._anchor_is_set = False
        self._anchor_alarm_is_active = False
        self._anchor_distance = 0
        self._current_longitude = ''
        self._current_latitude = ''
        self._position_history = []
        self._anchor_bearing = 0
        self._gps_accuracy = 'N/A'
        self._max_anchor_distance = 0

        directory_path = self._options.tmp_path
        filename = globals.ANCHOR_MANAGER_FILENAME
        self._session_filename = os.path.join(directory_path, filename)

        if self._options.anchor_alarm_module:
            self._anchor_thread = Thread(target=self._main_loop)
            self._anchor_thread.start()

            self._persist_session_to_disk_thread = Thread(target=self._persist_session_to_disk)
            self._persist_session_to_disk_thread.start()

            self._log_manager.info('Anchor alarm module successfully started!')
        else:
            self._status = AnchorManagerStatus.DOWN

    def finalize(self):
        if not self._options.anchor_alarm_module:
            return

        self._exit_signal.set()
        if self._anchor_thread:
            self._anchor_thread.join()

        self._status = AnchorManagerStatus.DOWN
        self._log_manager.info('Anchor manager instance is ready to be destroyed')

    def set_anchor_alternative(self, latitude, longitude, bearing: int, distance: int, allowed_distance: int) -> bool:
        # validate the input
        latlon_anchor = None
        try:
            latlon_anchor = string2latlon(latitude, longitude, 'd%°%m%\'%S%\" %H')
        except Exception as e:
            return False

        anchor_coordinates = utils.calculate_destination_point(latlon_anchor.lat.decimal_degree,
                                                               latlon_anchor.lon.decimal_degree,
                                                               bearing, distance)
        anchor_latlon = LatLon(Latitude(anchor_coordinates[0]), Longitude(anchor_coordinates[1]))

        # Get the string representation with reduced precision for seconds
        anchor_lat_formatted_string = '{lat}°{lat_min}\'{lat_sec}" {lat_hem}'.format(
            lat=round(anchor_latlon.lat.degree), lat_min=round(anchor_latlon.lat.minute),
            lat_sec=round(anchor_latlon.lat.second, 2),
            lat_hem=anchor_latlon.lat.to_string('%H')
        )

        anchor_lon_formatted_string = '{lon}°{lon_min}\'{lon_sec}" {lon_hem}'.format(
            lon=round(anchor_latlon.lon.degree), lon_min=round(anchor_latlon.lon.minute),
            lon_sec=round(anchor_latlon.lon.second, 2),
            lon_hem=anchor_latlon.lon.to_string('%H')
        )

        return self.set_anchor(anchor_lat_formatted_string,
                               anchor_lon_formatted_string, allowed_distance)

    def set_anchor(self, latitude, longitude, allowed_distance: int, preserve_history=False) -> bool:
        # validate the input
        try:
            latlon_anchor = string2latlon(latitude, longitude, 'd%°%m%\'%S%\" %H')
        except Exception as e:
            return False

        # cancel existing anchor (if any)
        self.cancel_anchor()

        self._anchor_latitude = latitude
        self._anchor_longitude = longitude
        self._anchor_allowed_distance = allowed_distance

        if not preserve_history:
            # record the current timestamp
            self._anchor_timestamp_utc = time.gmtime()
            self._anchor_timestamp_local = time.localtime()
            # reset the history and the max anchor distance registers
            self._position_history = []
            self._max_anchor_distance = 0

        # reset the anchor bearing
        self._anchor_bearing = 0

        # reset the gps accuracy
        self._gps_accuracy = 'N/A'

        # register that the anchor is set
        self._anchor_is_set = True

        return True

    def _set_anchor_from_disk(self):
        try:
            # Open the JSON file
            with open(self._session_filename) as f:
                # Load JSON data
                data = json.load(f)

            # Recover the data from disk
            latitude = data["latitude"]
            longitude = data["longitude"]
            allowed_distance = utils.try_parse_int(data["allowed_distance"])
            timestamp_utc = time.strptime(data["timestamp_utc"], "%Y-%m-%d %H:%M:%S %Z")
            timestamp_local = time.strptime(data["timestamp_local"], "%Y-%m-%d %H:%M:%S %Z")
            max_anchor_distance = utils.try_parse_float(data["max_anchor_distance"])
            position_history = data["position_history"]

            # validate the input
            try:
                latlon_anchor = string2latlon(latitude, longitude, 'd%°%m%\'%S%\" %H')
            except Exception as e:
                return False

            # Setup necessary instance variables
            self._anchor_latitude = latitude
            self._anchor_longitude = longitude
            self._anchor_allowed_distance = allowed_distance
            self._anchor_timestamp_utc = timestamp_utc
            self._anchor_timestamp_local = timestamp_local
            self._max_anchor_distance = max_anchor_distance
            self._position_history = position_history

            # reset the anchor bearing
            self._anchor_bearing = 0

            # reset the gps accuracy
            self._gps_accuracy = 'N/A'

            # register that the anchor is set
            self._anchor_is_set = True
        except Exception as e:
            self._log_manager.info(
                f'Exception occurred while trying to recover a previous anchor session from disk. Details {e}')

    def _persist_session_to_disk(self):
        while not self._exit_signal.is_set():
            try:
                gps_plugin_status = self._plugin_manager.get_gps_plugin_status()
                if self._anchor_is_set and gps_plugin_status == PluginStatus.RUNNING:
                    # Prepare the data to be written to the JSON file
                    data = {
                        "latitude": self._anchor_latitude,
                        "longitude": self._anchor_longitude,
                        "allowed_distance": self._anchor_allowed_distance,
                        "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S %Z", self._anchor_timestamp_utc),
                        "timestamp_local": time.strftime("%Y-%m-%d %H:%M:%S %Z", self._anchor_timestamp_local),
                        "max_anchor_distance": self._max_anchor_distance,
                        "position_history": self._position_history
                    }

                    # Write the data to the JSON file
                    with open(self._session_filename, 'w') as f:
                        json.dump(data, f, indent=4)  # indent for pretty formatting
            except Exception as e:
                self._log_manager.info(
                    f'Exception occurred while trying to write the current anchor session to disk. Details {e}')

            # sleep a bit
            time.sleep(globals.ANCHOR_MANAGER_PERSIST_SESSION_TO_DISK_RATE)

    def cancel_anchor(self):
        if self._anchor_is_set:
            self._anchor_is_set = False

            # delete the anchor session data from disk (if any)
            if utils.file_exists(self._session_filename):
                os.remove(self._session_filename)

        if self._anchor_alarm_is_active:
            self._anchor_alarm_is_active = False

            # send out a notification
            self._notifications_manager.notify('anchor', ModuleStatus.ALARM_CLEARED.value,
                                               NotificationEntryType.MODULE)

    def anchor_is_set(self):
        return self._anchor_is_set

    def anchor_latitude(self):
        return self._anchor_latitude

    def anchor_longitude(self):
        return self._anchor_longitude

    def anchor_allowed_distance(self):
        return self._anchor_allowed_distance

    def anchor_alarm_is_active(self):
        return self._anchor_alarm_is_active

    def anchor_distance(self):
        return self._anchor_distance

    def current_longitude(self):
        return self._current_longitude

    def current_latitude(self):
        return self._current_latitude

    def anchor_timestamp_utc(self):
        if self._anchor_timestamp_utc:
            return time.strftime("%Y-%m-%d %H:%M:%S", self._anchor_timestamp_utc)
        else:
            return ''

    def anchor_timestamp_local(self):
        if self._anchor_timestamp_local:
            return time.strftime("%Y-%m-%d %H:%M:%S", self._anchor_timestamp_local)
        else:
            return ''

    def position_history(self):
        return self._position_history

    def anchor_duration_in_seconds(self):
        if self._anchor_timestamp_utc:
            return abs(time.mktime(time.gmtime()) - time.mktime(self._anchor_timestamp_utc))
        else:
            return 0

    def anchor_bearing(self):
        return self._anchor_bearing

    def gps_accuracy(self):
        return self._gps_accuracy

    def max_anchor_distance(self):
        return self._max_anchor_distance

    def reset_max_anchor_distance(self):
        self._max_anchor_distance = 0

    def _main_loop(self):
        while not self._exit_signal.is_set():
            try:
                gps_plugin_status = self._plugin_manager.get_gps_plugin_status()
                if self._anchor_is_set:
                    # check first if the GPS module is running otherwise raise the alarm
                    if not gps_plugin_status == PluginStatus.RUNNING:
                        self._anchor_alarm_is_active = True

                        # send out a notification
                        self._notifications_manager.notify('anchor', ModuleStatus.ALARM_ACTIVE.value,
                                                           NotificationEntryType.MODULE,
                                                           f'GPS Module is down')

                        # sleep for 1 second
                        time.sleep(1)

                        continue

                    # retrieve the current gps accuracy and store it
                    self._gps_accuracy = self._plugin_manager.get_gps_plugin_accuracy()

                    # Retrieve current gps position and calculate distance
                    gps_entry = self._plugin_manager.get_gps_plugin_metrics()
                    if len(gps_entry) > 0:
                        self._current_latitude = gps_entry[0]
                        self._current_longitude = gps_entry[1]

                    latlon_anchor = string2latlon(self._anchor_latitude, self._anchor_longitude, 'd%°%m%\'%S%\" %H')
                    latlon_current = string2latlon(self._current_latitude, self._current_longitude, 'd%°%m%\'%S%\" %H')

                    # calculate the bearing to anchor
                    self._anchor_bearing = utils.calculate_bearing(latlon_current.lat, latlon_current.lon,
                                                                   latlon_anchor.lat, latlon_anchor.lon)

                    # Calculate the distance from anchor
                    # Only calculate the distance if the current position is different from the anchor position
                    if latlon_anchor.to_string() != latlon_current.to_string():
                        self._anchor_distance = round(latlon_current.distance(latlon_anchor) * 1000, 1)

                        # update the max distance field
                        if self._anchor_distance > self._max_anchor_distance:
                            self._max_anchor_distance = self._anchor_distance

                        # if current distance from the previous recorded position is larger than
                        # the save it to memory
                        if len(self._position_history) == 0:
                            if self._anchor_distance > 1:
                                self._position_history.append([self._current_latitude, self._current_longitude])
                        else:
                            latlon_previous_entry = string2latlon(
                                self._position_history[len(self._position_history) - 1][0],
                                self._position_history[len(self._position_history) - 1][1], 'd%°%m%\'%S%\" %H')
                            distance = round(latlon_current.distance(latlon_previous_entry) * 1000, 1)
                            if distance > 1:
                                self._position_history.append([self._current_latitude, self._current_longitude])

                        # cleanup history
                        self._position_history = copy.deepcopy(
                            self._position_history[-globals.ANCHOR_MANAGER_HISTORY_CACHE_LIMIT:])

                        # check if current distance exceeds the allowed distance
                        if self._anchor_distance > self._anchor_allowed_distance:
                            # mark the anchor alarm as active
                            self._anchor_alarm_is_active = True

                            # send out a notification
                            self._notifications_manager.notify('anchor', ModuleStatus.ALARM_ACTIVE.value,
                                                               NotificationEntryType.MODULE,
                                                               f'Distance from anchor is {self._anchor_distance}m '
                                                               f'whereas the allowed distance '
                                                               f'is {self._anchor_allowed_distance}m')

                            # sleep a bit
                            time.sleep(globals.ANCHOR_MANAGER_SAMPLING_RATE)

                            # skip the rest of the loop code
                            continue

                    # If this point in this loop is reached then deactivate the alarm (if active)
                    if self._anchor_alarm_is_active:
                        self._anchor_alarm_is_active = False

                        # send out a notification
                        self._notifications_manager.notify('anchor', ModuleStatus.ALARM_CLEARED.value,
                                                           NotificationEntryType.MODULE)
                elif gps_plugin_status == PluginStatus.RUNNING and utils.file_exists(self._session_filename):
                    self._set_anchor_from_disk()
            except Exception as e:
                if self._status != AnchorManagerStatus.DOWN:
                    self._log_manager.info(f'Exception occurred in Anchor manager main thread. Details {e}')

                    self._status = AnchorManagerStatus.DOWN

            # sleep a bit
            time.sleep(globals.ANCHOR_MANAGER_SAMPLING_RATE)
