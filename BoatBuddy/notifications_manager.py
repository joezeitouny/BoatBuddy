import threading
from enum import Enum

from BoatBuddy import config, utils
from BoatBuddy.sound_manager import SoundManager


class EntryType(Enum):
    METRIC = 'metric'
    MODULE = 'module'


class NotificationType(Enum):
    SOUND = 'sound'
    EMAIL = 'email'


class NotificationEntry:
    def __init__(self, key, value, entry_type: EntryType, notification_types: [], severity, frequency,
                 configuration_range=None, interval=None, cool_off_interval=None):
        self._key = key
        self._value = value
        self._entry_type = entry_type
        self._notification_types = notification_types
        self._severity = severity
        self._frequency = frequency
        self._configuration_range = configuration_range
        self._interval = interval
        self._cool_off_interval = cool_off_interval

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value

    def get_entry_type(self):
        return self._entry_type

    def get_severity(self):
        return self._severity

    def get_notification_types(self):
        return self._notification_types

    def get_frequency(self):
        return self._frequency

    def get_configuration_range(self):
        return self._configuration_range

    def get_interval(self):
        return self._interval

    def get_cool_off_interval(self):
        return self._cool_off_interval


class NotificationsManager:

    def __init__(self, options, args, sound_manager: SoundManager):
        self._options = options
        self._args = args
        self._sound_manager = sound_manager
        self._notifications_queue = {}
        self._frozen_notifications = {}

    def process_entry(self, key, value, entry_type):
        notifications_rules = None
        if entry_type == EntryType.METRIC:
            notifications_rules = config.METRICS_NOTIFICATIONS_RULES.copy()
        elif entry_type == EntryType.MODULE:
            notifications_rules = config.MODULES_NOTIFICATIONS_RULES.copy()

        # If there are no notification rules defined for this entry type then return
        if not notifications_rules:
            return

        # First check if the provided key has a notification configuration
        if key not in notifications_rules:
            return

        # If an empty value is provided then return
        if value is None or value == '' or str(value).upper() == 'N/A':
            return

        # Next, check if the value is falls within a range where a notification should occur
        notification_configuration = notifications_rules[key]
        for severity in notification_configuration:
            if entry_type == EntryType.METRIC:
                configuration_range = notification_configuration[severity]['range']
                if configuration_range[1] >= utils.try_parse_float(value) > configuration_range[0]:
                    notification_interval = None
                    cool_off_interval = None
                    if notification_configuration[severity]['frequency'] == 'interval':
                        notification_interval = utils.try_parse_int(notification_configuration[severity]['interval'])
                    if 'cool-off-interval' in notification_configuration[severity]:
                        cool_off_interval = utils.try_parse_int(
                            notification_configuration[severity]['cool-off-interval'])
                    self._schedule_notification(key, value, entry_type,
                                                notification_configuration[severity]['notifications'],
                                                severity, configuration_range,
                                                notification_configuration[severity]['frequency'],
                                                notification_interval, cool_off_interval)
                    return
            elif entry_type == EntryType.MODULE:
                status = notification_configuration[severity]['status']
                if value == status:
                    notification_interval = None
                    cool_off_interval = None
                    if notification_configuration[severity]['frequency'] == 'interval':
                        notification_interval = utils.try_parse_int(notification_configuration[severity]['interval'])
                    if 'cool-off-interval' in notification_configuration[severity]:
                        cool_off_interval = utils.try_parse_int(
                            notification_configuration[severity]['cool-off-interval'])
                    self._schedule_notification(key, value, entry_type,
                                                notification_configuration[severity]['notifications'],
                                                severity, notification_configuration[severity]['frequency'],
                                                None,
                                                notification_interval, cool_off_interval)
                    return

        # If this point in the code is reached then notifications for this entry (if any) should be cleared
        self._clear_notification_entry_after_interval(key)

    def _schedule_notification(self, key, value, entry_type, notification_types, severity, frequency,
                               configuration_range=None, interval=None, cool_off_interval=None):

        if key not in self._notifications_queue:
            # this is a new notification entry
            self._process_notification(key, value, entry_type, notification_types, severity, frequency,
                                       configuration_range, interval, cool_off_interval)
            self._add_notification_entry(key, value, entry_type, notification_types, severity, frequency,
                                         configuration_range, interval, cool_off_interval)
        elif self._notifications_queue[key]['instance'].get_entry_type() == EntryType.METRIC and \
                self._notifications_queue[key]['instance'].get_configuration_range() != configuration_range or \
                self._notifications_queue[key]['instance'].get_entry_type() == EntryType.MODULE and \
                self._notifications_queue[key]['instance'].get_value() != value:
            # If there is already an entry in the que with the same key
            # and if the range provided is different as what is stored in memory
            # Or if the new entry is for a module and has a different value than the old one then
            # this notification is different and needs to be treated as new notification
            # thus we need clear the old notification entry and schedule a new one
            self._clear_notification_entry(key)
            self._process_notification(key, value, entry_type, notification_types, severity, frequency,
                                       configuration_range, interval, cool_off_interval)
            self._add_notification_entry(key, value, entry_type, notification_types, severity, frequency,
                                         configuration_range, interval, cool_off_interval)

    def _process_notification(self, key, value, entry_type, notification_types, severity, frequency,
                              configuration_range, interval, cool_off_interval):
        if NotificationType.SOUND.value in notification_types:
            self._process_sound_notification(severity)

        if NotificationType.EMAIL.value in notification_types:
            self._process_email_notification(key, value, entry_type, severity, frequency, configuration_range, interval,
                                             cool_off_interval)

    def _process_clear_notification(self, key, notification_types, severity):
        if NotificationType.EMAIL.value in notification_types:
            self._process_clear_email_notification(key, severity)

    def _process_sound_notification(self, severity):
        if severity == 'alarm':
            self._sound_manager.play_sound_async('/resources/alarm.mp3')
        elif severity == 'warning':
            self._sound_manager.play_sound_async('/resources/warning.mp3')

    def _process_email_notification(self, key, value, entry_type, severity, frequency, configuration_range, interval,
                                    cool_off_interval):
        try:
            configuration_range_str = 'N/A'
            interval_str = 'N/A'
            cool_off_interval_str = 'N/A'
            if configuration_range:
                configuration_range_str = str(configuration_range)
            if interval:
                interval_str = str(interval)
            if cool_off_interval:
                cool_off_interval_str = str(cool_off_interval)
            body = f'Notification triggered for the following {entry_type.value}:\r\nKey:' \
                   f' {key}\r\nValue: {value}\r\nSeverity: {severity}' + \
                   f'\r\nFrequency: {frequency}\r\nConfiguration Range: ' \
                   f'{configuration_range_str}\r\nInterval: {interval_str} seconds\r\n ' \
                   f'Cool Off Interval: {cool_off_interval_str} seconds\r\n\r\n' \
                   f'--\r\n{config.APPLICATION_NAME} ({config.APPLICATION_VERSION})'
            subject = f'{config.APPLICATION_NAME} - ({str(severity).upper()}) ' \
                      f'notification for {entry_type.value} \'{key}\''
            utils.send_email(self._options, subject, body)
            utils.get_logger().info(f'Email notification sent! Notification triggered '
                                    f'for the following {entry_type.value}. Key: {key} Value: {value} '
                                    f'Severity: {severity} Frequency: {frequency} '
                                    f'Configuration Range: {configuration_range_str} Interval: {interval_str} '
                                    f'Cool Off Interval: {cool_off_interval_str}')
        except Exception as e:
            utils.get_logger().error(f'Error while sending email notification for {entry_type.value} '
                                     f'\'{key}\'. Details: {e}')

    def _process_clear_email_notification(self, key, severity):
        notification_entry = self._notifications_queue[key]['instance']
        try:
            body = f'Notification cleared for ' \
                   f'{notification_entry.get_entry_type().value} \'{key}\'\r\n\r\n' \
                   f'--\r\n{config.APPLICATION_NAME} ({config.APPLICATION_VERSION})'
            subject = f'{config.APPLICATION_NAME} - ({str(severity).upper()}) cleared ' \
                      f'for {notification_entry.get_entry_type().value} \'{key}\''
            utils.send_email(self._options, subject, body)
            utils.get_logger().info(f'Email notification sent! Notification cleared for '
                                    f' {notification_entry.get_entry_type().value} \'{key}\'')
        except Exception as e:
            utils.get_logger().error(f'Error while sending email notification '
                                     f'for {notification_entry.get_entry_type().value} \'{key}\'. Details: {e}')

    def _add_notification_entry(self, key, value, entry_type, notification_types, severity, frequency,
                                configuration_range, interval, cool_off_interval):
        new_notification_entry = NotificationEntry(key, value, entry_type, notification_types, severity,
                                                   frequency, configuration_range, interval, cool_off_interval)
        new_timer = None
        if frequency == 'interval':
            new_timer = threading.Timer(interval, self._notification_loop, args=[key])
            new_timer.start()
        self._notifications_queue[key] = {'instance': new_notification_entry, 'timer': new_timer}

        utils.get_logger().info(f'Adding new notification with key \'{key}\', value \'{value}\', ' +
                                f'severity \'{severity}\'')

    def _clear_notification_entry_after_interval(self, key):
        if key in self._frozen_notifications:
            return

        if key not in self._notifications_queue:
            return

        cool_off_interval = None
        notification_entry = self._notifications_queue[key]['instance']
        if notification_entry.get_cool_off_interval():
            cool_off_interval = utils.try_parse_int(notification_entry.get_cool_off_interval())
        elif self._options.cool_off_interval:
            cool_off_interval = utils.try_parse_int(self._options.cool_off_interval)

        if cool_off_interval:
            delay_timer = threading.Timer(cool_off_interval, self._clear_notification_entry, args=[key])
            delay_timer.start()
            self._frozen_notifications[key] = delay_timer

            utils.get_logger().info(f'Scheduling a timer to clear notification '
                                    f'for {notification_entry.get_entry_type().value} with key \'{key}\' '
                                    f'after {cool_off_interval} seconds')
        else:
            self._clear_notification_entry(key)

    def _clear_notification_entry(self, key):
        if key not in self._notifications_queue:
            return

        if key in self._frozen_notifications:
            self._frozen_notifications[key].cancel()
            self._frozen_notifications.pop(key)

        notification_entry = self._notifications_queue[key]['instance']
        self._process_clear_notification(key, notification_entry.get_notification_types(),
                                         notification_entry.get_severity())

        utils.get_logger().info(f'Cleared notification '
                                f'for {notification_entry.get_entry_type().value} with key \'{key}\'')

        # cancel the timer (if any)
        notification_timer = self._notifications_queue[key]['timer']
        if notification_timer is not None:
            notification_timer.cancel()

        # Remove the entry from memory
        self._notifications_queue.pop(key)

    def _notification_loop(self, key):
        notification_entry = self._notifications_queue[key]['instance']

        # Process the notification
        self._process_notification(key, notification_entry.get_value(), notification_entry.get_entry_type(),
                                   notification_entry.get_notification_types(), notification_entry.get_severity(),
                                   notification_entry.get_frequency(), notification_entry.get_configuration_range(),
                                   notification_entry.get_interval(), notification_entry.get_cool_off_interval())

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

        if len(self._frozen_notifications) > 0:
            # Loop through all the frozen notification entries and cancel their respective timers (if any)
            for key in self._frozen_notifications:
                self._notifications_queue[key].cancel()

            self._notifications_queue.clear()
