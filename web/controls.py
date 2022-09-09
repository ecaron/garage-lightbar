"""Light animation handler"""
import time
import board  # pylint: disable=import-error
import neopixel  # pylint: disable=import-error
from urllib.parse import parse_qs  # pylint: disable=wrong-import-order
from adafruit_led_animation.helper import PixelMap
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.color import WHITE

# from adafruit_led_animation.sequence import AnimationSequence
# from adafruit_led_animation import helper

pixels = neopixel.NeoPixel(board.D18, 60, auto_write=False)
blue_lights = [13, 14, 15, 16, 17, 18, 19, 20, 21]
blue_map = PixelMap(pixels, blue_lights, individual_pixels=True)

white_right_lights = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
white_right_map = PixelMap(pixels, white_right_lights, individual_pixels=True)

white_left_lights = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
white_left_map = PixelMap(pixels, white_left_lights, individual_pixels=True)

white_lights = white_right_lights + white_left_lights
white_map = PixelMap(pixels, white_lights, individual_pixels=True)

red_lights = [47, 48, 49, 50, 51, 52, 53, 54, 55]
red_map = PixelMap(pixels, red_lights, individual_pixels=True)

PREV_POWER = 0
PREV_BRIGHTNESS = 0
PREV_PATTERN = ""


def lights(light_state): # pylint: disable=too-many-branches,too-many-statements
    """Animates, powers and alters the light state"""
    global PREV_POWER, PREV_BRIGHTNESS, PREV_PATTERN # pylint: disable=global-statement
    pattern = Blink(white_map, speed=1.0, color=(0, 0, 0))
    while True: # pylint: disable=too-many-nested-blocks
        if light_state.get_power() == 1:
            if PREV_POWER == 0:
                PREV_POWER = 1
            if (
                PREV_PATTERN != light_state.get_pattern()
                or PREV_BRIGHTNESS != light_state.get_brightness
            ):
                PREV_PATTERN = light_state.get_pattern()
                PREV_BRIGHTNESS = light_state.get_brightness()
                new_pattern = parse_qs(PREV_PATTERN)
                if new_pattern["speed"][0] == "slowest":
                    speed = 1
                elif new_pattern["speed"][0] == "slow":
                    speed = 0.8
                elif new_pattern["speed"][0] == "normal":
                    speed = 0.4
                elif new_pattern["speed"][0] == "fast":
                    speed = 0.2
                elif new_pattern["speed"][0] == "fastest":
                    speed = 0.1

                tuple_color = WHITE
                if "color" in new_pattern and len(new_pattern["color"]) == 1:
                    hex_color = new_pattern["color"][0].lstrip("#")
                    tuple_color = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

                if new_pattern["zone"][0] == "rb-all":
                    new_map = PixelMap(
                        pixels, blue_lights + red_lights, individual_pixels=True
                    )
                elif new_pattern["zone"][0] == "white-all":
                    new_map = PixelMap(pixels, white_lights, individual_pixels=True)
                elif new_pattern["zone"][0] == "all":
                    new_map = PixelMap(
                        pixels,
                        blue_lights + white_lights + red_lights,
                        individual_pixels=True,
                    )

                if new_pattern["pattern"][0] == "blink":
                    pattern = Blink(new_map, speed=speed, color=tuple_color)
                elif new_pattern["pattern"][0] == "chase":
                    pattern = Chase(new_map, speed=speed, color=tuple_color)
                elif new_pattern["pattern"][0] == "colorcycle":
                    if "colors" in new_pattern and len(new_pattern["colors"]) > 0:
                        colors = []
                        for hex_color in new_pattern["colors"]:
                            hex_color = hex_color.lstrip("#")
                            colors.append(
                                tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
                            )
                        pattern = ColorCycle(new_map, speed=speed, colors=colors)
                    else:
                        pattern = ColorCycle(new_map, speed=speed)
                elif new_pattern["pattern"][0] == "comet":
                    pattern = Comet(new_map, speed=speed, color=tuple_color)
                elif new_pattern["pattern"][0] == "pulse":
                    pattern = Pulse(new_map, speed=speed, color=tuple_color)
                elif new_pattern["pattern"][0] == "rainbow":
                    pattern = Rainbow(new_map, speed=speed)
                elif new_pattern["pattern"][0] == "rainbowchase":
                    pattern = RainbowChase(new_map, speed=speed)
                elif new_pattern["pattern"][0] == "rainbowcomet":
                    pattern = RainbowComet(new_map, speed=speed)
                elif new_pattern["pattern"][0] == "rainbowsparkle":
                    pattern = RainbowSparkle(new_map, speed=speed)

                pixels.fill((0, 0, 0))
                pixels.show()

            pattern.animate()
        else:
            if PREV_POWER == 1:
                pixels.fill((0, 0, 0))
                pixels.show()
                PREV_POWER = 0
            time.sleep(0.2)
