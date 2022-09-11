from __future__ import print_function
from __future__ import division

import platform
import numpy as np
from . import config

import neopixel
import board

strip = neopixel.NeoPixel(
    board.D18, 60, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB
)

strip.show()

_gamma = np.load(config.GAMMA_TABLE_PATH)
"""Gamma lookup table used for nonlinear brightness correction"""

_prev_pixels = np.tile(253, (3, config.N_PIXELS))
"""Pixel values that were most recently displayed on the LED strip"""

pixels = np.tile(1, (3, config.N_PIXELS))
"""Pixel values for the LED strip"""

_is_python_2 = int(platform.python_version_tuple()[0]) == 2


def off():
    global strip
    strip.fill((0, 0, 0))
    strip.show()


def update():
    """Writes new LED values to the Raspberry Pi's LED strip

    Raspberry Pi uses the rpi_ws281x to control the LED strip directly.
    This function updates the LED strip with new values.
    """
    global pixels, _prev_pixels
    # Truncate values and cast to integer
    pixels = np.clip(pixels, 0, 255).astype(int)
    # Optional gamma correction
    p = _gamma[pixels] if config.SOFTWARE_GAMMA_CORRECTION else np.copy(pixels)
    # Encode 24-bit LED values in 32 bit integers
    # r = np.left_shift(p[0][:].astype(int), 8)
    # g = np.left_shift(p[1][:].astype(int), 16)
    # b = p[2][:].astype(int)
    # rgb = np.bitwise_or(np.bitwise_or(r, g), b)
    r = p[0][:].astype(int)
    g = p[1][:].astype(int)
    b = p[2][:].astype(int)

    # Update the pixels
    for i in range(config.N_PIXELS):

        if i < 12:
            offset = 21
        else:
            offset = 24

        # Ignore pixels if they haven't changed (saves bandwidth)
        if np.array_equal(p[:, i], _prev_pixels[:, i]):
            continue

        strip[offset + i] = (r[i], g[i], b[i])
        # strip._led_data[i] = int(rgb[i])
    _prev_pixels = np.copy(p)
    strip.show()


# Execute this file to run a LED strand test
# If everything is working, you should see a red, green, and blue pixel scroll
# across the LED strip continuously
if __name__ == "__main__":
    import time

    # Turn all pixels off
    pixels *= 0
    pixels[0, 0] = 255  # Set 1st pixel red
    pixels[1, 1] = 255  # Set 2nd pixel green
    pixels[2, 2] = 255  # Set 3rd pixel blue
    print("Starting LED strand test")
    while True:
        pixels = np.roll(pixels, 1, axis=1)
        update()
        time.sleep(0.1)
