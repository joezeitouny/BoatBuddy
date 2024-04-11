import os
from enum import Enum
from threading import Thread, Event, Lock
import time

from pydub import AudioSegment
from pydub.playback import play

from BoatBuddy.log_manager import LogManager


class SoundType(Enum):
    WARNING = 1
    ALARM = 2
    APPLICATION_STARTED = 3
    SESSION_STARTED = 4
    SESSION_ENDED = 5


class SoundManager:

    def __init__(self, options, log_manager: LogManager):
        self._options = options
        self._log_manager = log_manager
        self._sound_queue = []
        self._sound_thread = None
        self._exit_signal = Event()
        self._sound_thread = Thread(target=self._main_loop)

        if self._options.sound_module:
            self._mutex = Lock()
            self._sound_thread.start()
            self._log_manager.info('Sound module successfully started!')

    def play_sound_async(self, sound_type: SoundType):
        if not self._options.sound_module:
            return

        filename = None
        if sound_type == SoundType.APPLICATION_STARTED:
            filename = '/resources/application_started.mp3'
        elif sound_type == SoundType.ALARM:
            filename = '/resources/alarm.mp3'
        elif sound_type == SoundType.WARNING:
            filename = '/resources/warning.mp3'
        elif sound_type == SoundType.SESSION_STARTED:
            filename = '/resources/session_started.mp3'
        elif sound_type == SoundType.SESSION_ENDED:
            filename = '/resources/session_ended.wav'

        if filename:
            self._mutex.acquire()
            if len(self._sound_queue) == 0:
                self._sound_queue.append(filename)
            elif self._sound_queue[len(self._sound_queue) - 1] != filename:
                self._sound_queue.append(filename)
            self._mutex.release()

    def finalize(self):
        if not self._options.sound_module:
            return

        self._exit_signal.set()
        if self._sound_thread:
            self._sound_thread.join()

        self._log_manager.info('Sound manager instance is ready to be destroyed')

    def _main_loop(self):
        while not self._exit_signal.is_set():
            self._mutex.acquire()
            if len(self._sound_queue):
                self._play_sound(self._sound_queue.pop(0))
            self._mutex.release()

            time.sleep(1)  # Sleep for one second

    def _play_sound(self, filename):
        full_path = os.path.dirname(os.path.abspath(__file__)) + filename
        self._log_manager.debug(f'Playing a sound with filename: {full_path}')
        sound = AudioSegment.from_file(full_path)
        play(sound)
