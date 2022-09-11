import time
import numpy as np
import pyaudio
from . import config
from . import mute_alsa


class Microphone:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = False
        self.frames_per_buffer = int(config.MIC_RATE / config.FPS)
        self.running = False

    def start(self):
        self.running = True
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=config.MIC_RATE,
            input_device_index=1,
            frames_per_buffer=self.frames_per_buffer,
            #        frames_per_buffer=4096,
            input=True,
        )

        overflows = 0
        prev_ovf_time = time.time()

    def animate(self):
        if self.running:
            try:
                y = np.fromstring(
                    self.stream.read(
                        self.frames_per_buffer, exception_on_overflow=False
                    ),
                    dtype=np.int16,
                )
                y = y.astype(np.float32)
                self.stream.read(
                    self.stream.get_read_available(), exception_on_overflow=False
                )
                return y
            except IOError:
                overflows += 1
                if time.time() > prev_ovf_time + 1:
                    prev_ovf_time = time.time()
                    print("Audio buffer has overflowed {} times".format(overflows))
                return False

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
