import threading
from enum import Enum

from BoatBuddy import config, utils
from BoatBuddy.sound_manager import SoundManager


class NotificationType(Enum):
    SOUND = 1


class NotificationEntry:
    def __init__(self, key, value, notification_type: NotificationType, severity, configuration_range, frequency,
                 interval=None):
        self._key = key
        self._value = value
        self._notification_type = notification_type
        self._severity = severity
        self._configuration_range = configuration_range
        self._frequency = frequency
        self._interval = interval

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value

    def get_severity(self):
        return self._severity

    def get_notification_type(self):
        return self._notification_type

    def get_configuration_range(self):
        return self._configuration_range

    def get_frequency(self):
        return self._frequency

    def get_interval(self):
        return self._interval


class NotificationsManager:

    def __init__(self, sound_manager: SoundManager):
        self._notifications_queue = {}
        self._sound_manager = sound_manager

    def process_entry(self, key, value):
        notifications_scheme = config.NOTIFICATIONS_RULES.copy()

        # First check if the provided key has an notification configuration
        if key not in notifications_scheme:
            return

        # If an empty value is provided then return
        if value is None or value == '':
            return

        # Next, check if the value is falls within a range where a notification should occur
        notification_configuration = notifications_scheme[key]
        for severity in notification_configuration:
            configuration_range = notification_configuration[severity]['range']
            if configuration_range[1] >= utils.try_parse_float(value) > configuration_range[0]:
                notification_interval = None
                if notification_configuration[severity]['frequency'] == 'interval':
                    notification_interval = utils.try_parse_int(notification_configuration[severity]['interval'])
                self.schedule_notification(key, value, NotificationType.SOUND, severity, configuration_range,
                                           notification_configuration[severity]['frequency'],
                                           notification_interval)
                return

        # If this point in the code is reached then notifications for this entry (if any) should be cleared
        self.clear_notification(key)

    def schedule_notification(self, key, value, notification_type, severity, configuration_range, frequency,
                              interval=None):
        # If this is a new key then create a new entry for it in memory
        if key not in self._notifications_queue:
            # Play the notification sound
            if severity == 'alarm':
                self._sound_manager.play_sound_async('/resources/alarm.mp3')
            elif severity == 'warning':
                self._sound_manager.play_sound_async('/resources/warning.mp3')

            new_notification_entry = NotificationEntry(key, value, notification_type, severity,
                                                       configuration_range, frequency, interval)
            if frequency == 'interval':
                new_timer = threading.Timer(interval, self.notification_loop, args=[key])
                new_timer.start()
                self._notifications_queue[key] = {'instance': new_notification_entry, 'timer': new_timer}
            elif frequency == 'once':
                self._notifications_queue[key] = {'instance': new_notification_entry, 'timer': None}
        elif self._notifications_queue[key]['instance'].get_configuration_range() != configuration_range:
            # if the range provided is the same as what is stored in memory then this notification is already scheduled
            # Otherwise clear the old notification and schedule a new one
            self.clear_notification(key)
            new_notification_entry = NotificationEntry(key, value, notification_type, severity,
                                                       configuration_range, frequency, interval)
            if frequency == 'interval':
                new_timer = threading.Timer(interval, self.notification_loop, args=[key])
                new_timer.start()
                self._notifications_queue[key] = {'instance': new_notification_entry, 'timer': new_timer}
            elif frequency == 'once':
                self._notifications_queue[key] = {'instance': new_notification_entry, 'timer': None}

    def clear_notification(self, key):
        if key not in self._notifications_queue:
            return

        # cancel the timer (if any)
        notification_timer = self._notifications_queue[key]['timer']
        if notification_timer is not None:
            notification_timer.cancel()

        # Remove the entry from memory
        self._notifications_queue.pop(key)

    def notification_loop(self, key):
        # Play the notification
        notification_entry = self._notifications_queue[key]['instance']

        if notification_entry.get_severity() == 'alarm':
            self._sound_manager.play_sound_async('/resources/alarm.mp3')
        elif notification_entry.get_severity() == 'warning':
            self._sound_manager.play_sound_async('/resources/warning.mp3')

        # Reschedule the timer
        self._notifications_queue[key]['timer'] = threading.Timer(notification_entry.get_interval(),
                                                                  self.notification_loop, args=[key])
        self._notifications_queue[key]['timer'].start()

    def finalize(self):
        if len(self._notifications_queue) > 0:
            # Loop through all the notification entries and cancel their respective timers (if any)
            for key in self._notifications_queue:
                if self._notifications_queue[key]['timer'] is not None:
                    self._notifications_queue[key]['timer'].cancel()

            self._notifications_queue.clear()
