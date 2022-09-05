# import board
# import neopixel
# import time
# from adafruit_led_animation.helper import PixelMap
# from adafruit_led_animation.animation.comet import Comet
# from adafruit_led_animation.animation.rainbowcomet import RainbowComet
# from adafruit_led_animation.animation.rainbowchase import RainbowChase
# from adafruit_led_animation.animation.chase import Chase
# from adafruit_led_animation.animation.rainbow import Rainbow
# from adafruit_led_animation.sequence import AnimationSequence
# from adafruit_led_animation import helper

# pixels = neopixel.NeoPixel(board.D18, 60, auto_write=False)
# blue_lights = [13, 14, 15, 16, 17, 18, 19, 20, 21]
# blue_map = PixelMap(pixels, blue_lights, individual_pixels=True)

# white_right_lights = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
# white_right_map = PixelMap(pixels, white_right_lights, individual_pixels=True)

# white_left_lights = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
# white_left_map = PixelMap(pixels, white_left_lights, individual_pixels=True)

# white_lights = white_right_lights + white_left_lights
# white_map = PixelMap(pixels, white_lights, individual_pixels=True)

# red_lights = [47, 48, 49, 50, 51, 52, 53, 54, 55]
# red_map = PixelMap(pixels, red_lights, individual_pixels=True)

def power():
    return 1

def brightness():
    return 2

def cycle():
    return 3
