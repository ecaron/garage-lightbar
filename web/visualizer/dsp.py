"""Digital Signal Processing"""
from __future__ import print_function
import numpy as np
from . import config
from . import melbank


class ExpFilter: # pylint: disable=too-few-public-methods
    """Simple exponential smoothing filter"""

    def __init__(self, val=0.0, alpha_decay=0.5, alpha_rise=0.5):
        """Small rise / decay factors = more smoothing"""
        assert 0.0 < alpha_decay < 1.0, "Invalid decay smoothing factor"
        assert 0.0 < alpha_rise < 1.0, "Invalid rise smoothing factor"
        self.alpha_decay = alpha_decay
        self.alpha_rise = alpha_rise
        self.value = val

    def update(self, value):
        """Attaches the new data"""
        if isinstance(self.value, (list, np.ndarray, tuple)):
            alpha = value - self.value
            alpha[alpha > 0.0] = self.alpha_rise
            alpha[alpha <= 0.0] = self.alpha_decay
        else:
            alpha = self.alpha_rise if value > self.value else self.alpha_decay
        self.value = alpha * value + (1.0 - alpha) * self.value
        return self.value


def rfft(data, window=None):
    """Reverse transform"""
    window = 1.0 if window is None else window(len(data))
    ys = np.abs(np.fft.rfft(data * window))  # pylint: disable=invalid-name
    xs = np.fft.rfftfreq(len(data), 1.0 / config.MIC_RATE) # pylint: disable=invalid-name
    return xs, ys


def fft(data, window=None):
    """Regular transform"""
    window = 1.0 if window is None else window(len(data))
    ys = np.fft.fft(data * window) # pylint: disable=invalid-name
    xs = np.fft.fftfreq(len(data), 1.0 / config.MIC_RATE) # pylint: disable=invalid-name
    return xs, ys


def create_mel_bank():
    """Performs a one-time generation for the melbank"""
    global SAMPLES, MEL_Y, MEL_X # pylint: disable=global-statement
    SAMPLES = int(config.MIC_RATE * config.N_ROLLING_HISTORY / (2.0 * config.FPS))
    MEL_Y, (_, MEL_X) = melbank.compute_melmat(
        num_mel_bands=config.N_FFT_BINS,
        freq_min=config.MIN_FREQUENCY,
        freq_max=config.MAX_FREQUENCY,
        num_fft_bands=SAMPLES,
        sample_rate=config.MIC_RATE,
    )


SAMPLES = None
MEL_Y = None
MEL_X = None
create_mel_bank()
