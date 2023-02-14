import threading
from enum import Enum

import yagmail

from BoatBuddy import config, utils
from BoatBuddy.sound_manager import SoundManager


class NotificationType(Enum):
    SOUND = 'sound'
    EMAIL = 'email'


class NotificationEntry:
    def __init__(self, key, value, notification_types: [], severity, configuration_range, frequency,
                 interval=None):
        self._key = key
        self._value = value
        self._notification_types = notification_types
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

    def get_notification_types(self):
        return self._notification_types

    def get_configuration_range(self):
        return self._configuration_range

    def get_frequency(self):
        return self._frequency

    def get_interval(self):
        return self._interval


class NotificationsManager:

    def __init__(self, options, args, sound_manager: SoundManager):
        self._options = options
        self._args = args
        self._sound_manager = sound_manager
        self._notifications_queue = {}

    def process_entry(self, key, value):
        notifications_scheme = config.NOTIFICATIONS_RULES.copy()

        # First check if the provided key has a notification configuration
        if key not in notifications_scheme:
            return

        # If an empty value is provided then return
        if value is None or value == '' or str(value).upper() == 'N/A':
            return

        # Next, check if the value is falls within a range where a notification should occur
        notification_configuration = notifications_scheme[key]
        for severity in notification_configuration:
            configuration_range = notification_configuration[severity]['range']
            if configuration_range[1] >= utils.try_parse_float(value) > configuration_range[0]:
                notification_interval = None
                if notification_configuration[severity]['frequency'] == 'interval':
                    notification_interval = utils.try_parse_int(notification_configuration[severity]['interval'])
                self._schedule_notification(key, value, notification_configuration[severity]['notifications'],
                                            severity, configuration_range,
                                            notification_configuration[severity]['frequency'],
                                            notification_interval)
                return

        # If this point in the code is reached then notifications for this entry (if any) should be cleared
        self._clear_notification_entry(key)

    def _schedule_notification(self, key, value, notification_types, severity, configuration_range, frequency,
                               interval=None):

        if key not in self._notifications_queue:
            # this is a new notification entry
            self._process_notification(key, value, notification_types, severity, configuration_range,
                                       frequency, interval)
            self._add_notification_entry(key, value, notification_types, severity, configuration_range, frequency,
                                         interval)
            return

        # If there is already an entry in the que with the same key
        # and if the range provided is different as what is stored in memory then
        # this notification is different and needs to be treated as new notification
        # thus we need clear the old notification entry and schedule a new one
        if self._notifications_queue[key]['instance'].get_configuration_range() != configuration_range:
            self._clear_notification_entry(key)
            self._process_notification(key, value, notification_types, severity, configuration_range,
                                       frequency, interval)
            self._add_notification_entry(key, value, notification_types, severity, configuration_range, frequency,
                                         interval)

    def _process_notification(self, key, value, notification_types, severity, configuration_range, frequency, interval):
        if NotificationType.SOUND.value in notification_types:
            self._process_sound_notification(severity)

        if NotificationType.EMAIL.value in notification_types:
            self._process_email_notification(key, value, severity, configuration_range, frequency, interval)

    def _process_clear_notification(self, key, notification_types, severity):
        if NotificationType.EMAIL.value in notification_types:
            self._process_clear_email_notification(key, severity)

    def _process_sound_notification(self, severity):
        if severity == 'alarm':
            self._sound_manager.play_sound_async('/resources/alarm.mp3')
        elif severity == 'warning':
            self._sound_manager.play_sound_async('/resources/warning.mp3')

    def _process_email_notification(self, key, value, severity, configuration_range, frequency, interval):
        if not self._options.email_address or not self._options.email_password:
            return

        try:
            receiver = self._options.email_address
            interval_str = 'N/A'
            if interval:
                interval_str = str(interval)
            body = f'Notification triggered for the following metric:\r\nKey: {key}\r\nValue: {value}\r\nSeverity: {severity}' + \
                   f'\r\nConfiguration Range: {configuration_range}\r\nFrequency: {frequency}\r\nInterval: {interval_str}'

            yagmail.register(self._options.email_address, self._options.email_password)
            yag = yagmail.SMTP(receiver)
            yag.send(to=receiver, subject=f'{config.APPLICATION_NAME} - ({str(severity).upper()}) for metric {key}'
                     , contents=body)
        except Exception as e:
            utils.get_logger().error(f'Error while sending email notification for key {key}. Details: {e}')

    def _process_clear_email_notification(self, key, severity):
        if not self._options.email_address or not self._options.email_password:
            return
        try:
            receiver = self._options.email_address
            body = f'Notification cleared for the following metric: {key}\r\n'

            yagmail.register(self._options.email_address, self._options.email_password)
            yag = yagmail.SMTP(receiver)
            yag.send(to=receiver,
                     subject=f'{config.APPLICATION_NAME} - ({str(severity).upper()}) cleared for metric {key}'
                     , contents=body)
        except Exception as e:
            utils.get_logger().error(f'Error while sending email notification for key {key}. Details: {e}')

    def _add_notification_entry(self, key, value, notification_types, severity, configuration_range, frequency,
                                interval):
        new_notification_entry = NotificationEntry(key, value, notification_types, severity,
                                                   configuration_range, frequency, interval)
        new_timer = None
        if frequency == 'interval':
            new_timer = threading.Timer(interval, self._notification_loop, args=[key])
            new_timer.start()
        self._notifications_queue[key] = {'instance': new_notification_entry, 'timer': new_timer}

        utils.get_logger().info(f'Adding new notification with key \'{key}\', value \'{value}\', ' +
                                f'severity \'{severity}\'')

    def _clear_notification_entry(self, key):
        if key not in self._notifications_queue:
            return

        notification_entry = self._notifications_queue[key]['instance']
        self._process_clear_notification(key, notification_entry.get_notification_types(),
                                         notification_entry.get_severity())

        utils.get_logger().info(f'Clearing notification for key \'{key}\'')

        # cancel the timer (if any)
        notification_timer = self._notifications_queue[key]['timer']
        if notification_timer is not None:
            notification_timer.cancel()

        # Remove the entry from memory
        self._notifications_queue.pop(key)

    def _notification_loop(self, key):
        notification_entry = self._notifications_queue[key]['instance']

        # Process the notification
        self._process_notification(key, notification_entry.get_value(), notification_entry.get_notification_types(),
                                   notification_entry.get_severity(), notification_entry.get_configuration_range(),
                                   notification_entry.get_frequency(), notification_entry.get_interval())

        # Reschedule the timer
        self._notifications_queue[key]['timer'] = threading.Timer(notification_entry.get_interval(),
                                                                  self._notification_loop, args=[key])
        self._notifications_queue[key]['timer'].start()

    def finalize(self):
        if len(self._notifications_queue) > 0:
            # Loop through all the notification entries and cancel their respective timers (if any)
            for key in self._notifications_queue:
                if self._notifications_queue[key]['timer'] is not None:
                    self._notifications_queue[key]['timer'].cancel()

            self._notifications_queue.clear()
