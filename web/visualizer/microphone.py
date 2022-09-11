"""Attach to the microphone and route the input back to the visualizer"""
import time
import numpy as np
import pyaudio
from . import config
from . import mute_alsa # pylint: disable=unused-import


class Microphone:
    """Microphone class, for starting and stopping"""

    def __init__(self):
        """Setup the listener"""
        self.p = pyaudio.PyAudio() # pylint: disable=invalid-name
        self.stream = False
        self.frames_per_buffer = int(config.MIC_RATE / config.FPS)
        self.running = False
        self.overflows = 0
        self.prev_ovf_time = time.time()

    def start(self):
        """Start listening"""
        self.running = True
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=config.MIC_RATE,
            input_device_index=1,
            frames_per_buffer=self.frames_per_buffer,
            input=True,
        )


    def animate(self):
        """Keep listening, as long as we're supposed to, and pass back what we find"""
        if self.running:
            try:
                y = np.fromstring( # pylint: disable=invalid-name
                    self.stream.read(
                        self.frames_per_buffer, exception_on_overflow=False
                    ),
                    dtype=np.int16,
                )
                y = y.astype(np.float32) # pylint: disable=invalid-name
                self.stream.read(
                    self.stream.get_read_available(), exception_on_overflow=False
                )
                return y
            except IOError:
                self.overflows += 1
                if time.time() > self.prev_ovf_time + 1:
                    self.prev_ovf_time = time.time()
                    print(f"Audio buffer has overflowed {self.overflows} times")
        return False

    def stop(self):
        """Turn off the mic if it isn't in use"""
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
