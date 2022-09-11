"""Expose audio visualization methods to the NeoPixel animation library"""
# pylint: disable=invalid-name
from __future__ import print_function
from __future__ import division
import time
import os
import functools
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.color import BLACK
from . import config
from .microphone import Microphone
from . import dsp

class Visualizer(Animation): # pylint: disable=too-many-instance-attributes
    """Visualizer class to be used by the Adafruit animation sequences"""

    def __init__(self, pixel_object, method, name=None):
        """The previous time that the frames_per_second() function was called"""
        super().__init__(pixel_object, speed=1, color=BLACK, name=name)
        self._time_prev = time.time() * 1000.0
        self.method = method
        self.pixels = pixel_object
        self.microphone = Microphone()

        """Gamma lookup table used for nonlinear brightness correction"""
        self._gamma = np.load(os.path.join(os.path.dirname(__file__), "gamma_table.npy"))

        """Pixel values that were most recently displayed on the LED strip"""
        self._prev_pixels = np.tile(253, (3, len(pixel_object)))
        self.raw_pixels = np.tile(1, (3, len(pixel_object)))

        """The low-pass filter used to estimate frames-per-second"""
        self._fps = dsp.ExpFilter(val=config.FPS, alpha_decay=0.2, alpha_rise=0.2)
        self.r_filt = dsp.ExpFilter(
            np.tile(0.01, len(pixel_object) // 2), alpha_decay=0.2, alpha_rise=0.99
        )
        self.g_filt = dsp.ExpFilter(
            np.tile(0.01, len(pixel_object) // 2), alpha_decay=0.05, alpha_rise=0.3
        )
        self.b_filt = dsp.ExpFilter(
            np.tile(0.01, len(pixel_object) // 2), alpha_decay=0.1, alpha_rise=0.5
        )
        self.common_mode = dsp.ExpFilter(
            np.tile(0.01, len(pixel_object) // 2), alpha_decay=0.99, alpha_rise=0.01
        )
        self.p_filt = dsp.ExpFilter(
            np.tile(1, (3, len(pixel_object) // 2)), alpha_decay=0.1, alpha_rise=0.99
        )
        self.p = np.tile(1.0, (3, len(pixel_object) // 2))
        self.gain = dsp.ExpFilter(
            np.tile(0.01, config.N_FFT_BINS), alpha_decay=0.001, alpha_rise=0.99
        )
        self._prev_spectrum = np.tile(0.01, len(pixel_object) // 2)
        self.fft_plot_filter = dsp.ExpFilter(
            np.tile(1e-1, config.N_FFT_BINS), alpha_decay=0.5, alpha_rise=0.99
        )
        self.mel_gain = dsp.ExpFilter(
            np.tile(1e-1, config.N_FFT_BINS), alpha_decay=0.01, alpha_rise=0.99
        )
        self.mel_smoothing = dsp.ExpFilter(
            np.tile(1e-1, config.N_FFT_BINS), alpha_decay=0.5, alpha_rise=0.99
        )
        self.volume = dsp.ExpFilter(
            config.MIN_VOLUME_THRESHOLD, alpha_decay=0.02, alpha_rise=0.02
        )
        self.fft_window = np.hamming(
            int(config.MIC_RATE / config.FPS) * config.N_ROLLING_HISTORY
        )
        self.prev_fps_update = time.time()
        # Number of audio samples to read every time frame
        self.samples_per_frame = int(config.MIC_RATE / config.FPS)

        # Array containing the rolling audio sample window
        self.y_roll = (
            np.random.rand(config.N_ROLLING_HISTORY, self.samples_per_frame) / 1e16
        )
        self.microphone.start()

    def disable(self):
        """Pass the note to turn off the microphone listeners"""
        self.microphone.stop()

    def draw(self):
        """Not supported - animation should be called instead"""
        raise NotImplementedError()

    def animate(self, show=True):
        """Grab the audio states & animate them"""
        if show is True:
            self.audio_update(self.microphone.animate())

    def frames_per_second(self):
        """Return the estimated frames per second

        Returns the current estimate for frames-per-second (FPS).
        FPS is estimated by measured the amount of time that has elapsed since
        this function was previously called. The FPS estimate is low-pass filtered
        to reduce noise.

        This function is intended to be called one time for every iteration of
        the program's main loop.

        Returns
        -------
        fps : float
            Estimated frames-per-second. This value is low-pass filtered
            to reduce noise.
        """
        time_now = time.time() * 1000.0
        dt = time_now - self._time_prev
        self._time_prev = time_now
        if dt == 0.0:
            return self._fps.value
        return self._fps.update(1000.0 / dt)

    @functools.lru_cache
    def _normalized_linspace(self, size):
        return np.linspace(0, 1, size)

    def interpolate(self, y, new_length):
        """Intelligently resizes the array by linearly interpolating the values

        Parameters
        ----------
        y : np.array
            Array that should be resized

        new_length : int
            The length of the new interpolated array

        Returns
        -------
        z : np.array
            New array with length of new_length that contains the interpolated
            values of y.
        """
        if len(y) == new_length:
            return y
        x_old = self._normalized_linspace(len(y))
        x_new = self._normalized_linspace(new_length)
        z = np.interp(x_new, x_old, y)
        return z

    def visualize_scroll(self, y):
        """Effect that originates in the center and scrolls outwards"""
        y = y**2.0
        self.gain.update(y)
        y /= self.gain.value
        y *= 255.0
        r = int(np.max(y[: len(y) // 3]))
        g = int(np.max(y[len(y) // 3 : 2 * len(y) // 3]))
        b = int(np.max(y[2 * len(y) // 3 :]))
        # Scrolling effect window
        self.p[:, 1:] = self.p[:, :-1]
        self.p *= 0.98
        self.p = gaussian_filter1d(self.p, sigma=0.2)
        # Create new color originating at the center
        self.p[0, 0] = r
        self.p[1, 0] = g
        self.p[2, 0] = b
        # Update the LED strip
        return np.concatenate((self.p[:, ::-1], self.p), axis=1)

    def visualize_energy(self, y):
        """Effect that expands from the center with increasing sound energy"""
        y = np.copy(y)
        self.gain.update(y)
        y /= self.gain.value
        # Scale by the width of the LED strip
        y *= float((len(self.pixels) // 2) - 1)
        # Map color channels according to energy in the different freq bands
        scale = 0.9
        r = int(np.mean(y[: len(y) // 3] ** scale))
        g = int(np.mean(y[len(y) // 3 : 2 * len(y) // 3] ** scale))
        b = int(np.mean(y[2 * len(y) // 3 :] ** scale))
        # Assign color to different frequency regions
        self.p[0, :r] = 255.0
        self.p[0, r:] = 0.0
        self.p[1, :g] = 255.0
        self.p[1, g:] = 0.0
        self.p[2, :b] = 255.0
        self.p[2, b:] = 0.0
        self.p_filt.update(self.p)
        self.p = np.round(self.p_filt.value)
        # Apply substantial blur to smooth the edges
        self.p[0, :] = gaussian_filter1d(self.p[0, :], sigma=4.0)
        self.p[1, :] = gaussian_filter1d(self.p[1, :], sigma=4.0)
        self.p[2, :] = gaussian_filter1d(self.p[2, :], sigma=4.0)
        # Set the new pixel value
        return np.concatenate((self.p[:, ::-1], self.p), axis=1)

    def visualize_spectrum(self, y):
        """Effect that maps the Mel filterbank frequencies onto the LED strip"""
        y = np.copy(self.interpolate(y, len(self.pixels) // 2))
        self.common_mode.update(y)
        diff = y - self._prev_spectrum
        self._prev_spectrum = np.copy(y)
        # Color channel mappings
        r = self.r_filt.update(y - self.common_mode.value)
        g = np.abs(diff)
        b = self.b_filt.update(np.copy(y))
        # Mirror the color channels for symmetric output
        r = np.concatenate((r[::-1], r))
        g = np.concatenate((g[::-1], g))
        b = np.concatenate((b[::-1], b))
        # output = np.array([r, g, b]) * 255
        output = np.array([g, r, b]) * 255
        return output

    def audio_update(self, audio_samples):
        """Take the microphone feedback and visualize it"""
        if len(audio_samples) == 0:
            return
        # Normalize samples between 0 and 1
        y = audio_samples / 2.0**15
        # Construct a rolling window of audio samples
        self.y_roll[:-1] = self.y_roll[1:]
        self.y_roll[-1, :] = np.copy(y)
        y_data = np.concatenate(self.y_roll, axis=0).astype(np.float32)

        vol = np.max(np.abs(y_data))
        if vol < config.MIN_VOLUME_THRESHOLD:
            # print('No audio input. Volume below threshold. Volume:', vol)
            self.pixels.fill((0, 0, 0))
        else:
            # print('Audio input. Volume:', vol)
            # Transform audio input into the frequency domain
            N = len(y_data)
            N_zeros = 2 ** int(np.ceil(np.log2(N))) - N
            # Pad with zeros until the next power of two
            y_data *= self.fft_window
            y_padded = np.pad(y_data, (0, N_zeros), mode="constant")
            YS = np.abs(np.fft.rfft(y_padded)[: N // 2])
            # Construct a Mel filterbank from the FFT data
            mel = np.atleast_2d(YS).T * dsp.MEL_Y.T
            # Scale data to values more suitable for visualization
            # mel = np.sum(mel, axis=0)
            mel = np.sum(mel, axis=0)
            mel = mel**2.0
            # Gain normalization
            self.mel_gain.update(np.max(gaussian_filter1d(mel, sigma=1.0)))
            mel /= self.mel_gain.value
            mel = self.mel_smoothing.update(mel)
            # Map filterbank output onto LED strip
            if self.method == "spectrum":
                self.raw_pixels = self.visualize_spectrum(mel)
            elif self.method == "scroll":
                self.raw_pixels = self.visualize_scroll(mel)
            else:
                self.raw_pixels = self.visualize_energy(mel)
            self.update()

    def update(self):
        """Writes new LED values to the Raspberry Pi's LED strip
        Raspberry Pi uses the rpi_ws281x to control the LED strip directly.
        This function updates the LED strip with new values.
        """
        # Truncate values and cast to integer
        self.raw_pixels = np.clip(self.raw_pixels, 0, 255).astype(int)
        # Optional gamma correction
        p = self._gamma[self.raw_pixels]
        # Encode 24-bit LED values in 32 bit integers
        # r = np.left_shift(p[0][:].astype(int), 8)
        # g = np.left_shift(p[1][:].astype(int), 16)
        # b = p[2][:].astype(int)
        # rgb = np.bitwise_or(np.bitwise_or(r, g), b)
        r = p[0][:].astype(int)
        g = p[1][:].astype(int)
        b = p[2][:].astype(int)

        # Update the pixels
        for i in range(len(self.pixels)):

            if i < 12:
                offset = 21
            else:
                offset = 24
            offset = 0
            # Ignore pixels if they haven't changed (saves bandwidth)
            if np.array_equal(p[:, i], self._prev_pixels[:, i]):
                continue

            self.pixels[offset + i] = (r[i], g[i], b[i])

        # strip._led_data[i] = int(rgb[i])
        self._prev_pixels = np.copy(p)
        self.pixels.show()
