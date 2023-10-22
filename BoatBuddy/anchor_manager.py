import time
from enum import Enum
from threading import Thread, Event

from latloncalc.latlon import LatLon, Latitude, Longitude, string2latlon

from BoatBuddy.log_manager import LogManager
from BoatBuddy.plugin_manager import PluginManager
from BoatBuddy.email_manager import EmailManager
from BoatBuddy.generic_plugin import PluginStatus
from BoatBuddy import utils


class AnchorManagerStatus(Enum):
    STARTING = 1
    RUNNING = 2
    DOWN = 3


class AnchorManager:
    def __init__(self, options, log_manager: LogManager, plugin_manager: PluginManager, email_manager: EmailManager):
        self._options = options
        self._log_manager = log_manager
        self._plugin_manager = plugin_manager
        self._email_manager = email_manager
        self._exit_signal = Event()

        self._status = AnchorManagerStatus.STARTING
        self._anchor_latitude = ''
        self._anchor_longitude = ''
        self._anchor_allowed_distance = 0
        self._anchor_is_set = False
        self._anchor_alarm_is_active = False
        self._anchor_distance = 0

        if self._options.anchor_alarm_module:
            self._anchor_thread = Thread(target=self._main_loop)
            self._anchor_thread.start()
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

    def set_anchor(self, latitude, longitude, allowed_distance: int):
        # cancel existing anchor (if any)
        self.cancel_anchor()

        self._anchor_latitude = latitude
        self._anchor_longitude = longitude
        self._anchor_allowed_distance = allowed_distance
        self._anchor_is_set = True

    def cancel_anchor(self):
        self._anchor_is_set = False
        self._anchor_alarm_is_active = False

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

    def _main_loop(self):
        while not self._exit_signal.is_set():
            try:
                if self._anchor_is_set:
                    # check first if the GPS module is running otherwise raise the alarm
                    gps_plugin_status = self._plugin_manager.get_gps_plugin_status()
                    if not gps_plugin_status == PluginStatus.RUNNING:
                        self._anchor_alarm_is_active = True
                        continue

                    # Retrieve current gps position and calculate distance
                    gps_latitude = ''
                    gps_longitude = ''

                    gps_entry = self._plugin_manager.get_gps_plugin_metrics()
                    if len(gps_entry) > 0:
                        gps_latitude = gps_entry[0]
                        gps_longitude = gps_entry[1]

                    # calculate the distance from anchor
                    latlon_anchor = string2latlon(self._anchor_latitude, self._anchor_longitude, 'd%°%m%\'%S%\" %H')
                    latlon_current = string2latlon(gps_latitude, gps_longitude, 'd%°%m%\'%S%\" %H')

                    # Only calculate the distance if the current position is different from the anchor position
                    if latlon_anchor.to_string() != latlon_current.to_string():
                        distance_from_anchor = round(latlon_current.distance(latlon_anchor) * 1000, 1)

                        # check if current distance exceeds the allowed distance
                        if distance_from_anchor > self._anchor_allowed_distance:
                            self._anchor_alarm_is_active = True
                            continue

                    # If this point in this loop is reached then deactivate the alarm
                    self._anchor_alarm_is_active = False

                    # sleep for 1 second
                    time.sleep(1)
            except Exception as e:
                if self._status != AnchorManagerStatus.DOWN:
                    self._log_manager.info(f'Exception occurred in Anchor manager main thread. Details {e}')

                    self._status = AnchorManagerStatus.DOWN

