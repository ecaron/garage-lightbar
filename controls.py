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
from adafruit_led_animation.animation.sparklepulse import SparklePulse
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation import color
from visualizer import Visualizer


def lights(
    light_state,
):  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
    """Animates, powers and alters the light state"""
    pixels = neopixel.NeoPixel(board.D18, 60, brightness=1.0, auto_write=False)
    blue_lights = [13, 14, 15, 16, 17, 18, 19, 20, 21]
    blue_map = PixelMap(pixels, blue_lights, individual_pixels=True)

    white_right_lights = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
    white_left_lights = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
    white_lights = white_right_lights + white_left_lights
    white_map = PixelMap(pixels, white_lights, individual_pixels=True)

    red_lights = [47, 48, 49, 50, 51, 52, 53, 54, 55]
    red_map = PixelMap(pixels, red_lights, individual_pixels=True)

    prev_power = 0
    prev_brightness = 0
    prev_pattern = ""
    mic_active = False

    pattern = Blink(white_map, speed=1.0, color=(0, 0, 0))
    while True:  # pylint: disable=too-many-nested-blocks
        if light_state.get_power() == 1:
            if prev_power == 0:
                prev_power = 1
            if (
                prev_pattern != light_state.get_pattern()
                or prev_brightness != light_state.get_brightness()
            ):
                prev_pattern = light_state.get_pattern()

                if prev_brightness != light_state.get_brightness():
                    pixels = neopixel.NeoPixel(
                        board.D18,
                        60,
                        brightness=light_state.get_brightness() / 100,
                        auto_write=False,
                    )
                    blue_map = PixelMap(pixels, blue_lights, individual_pixels=True)
                    white_map = PixelMap(pixels, white_lights, individual_pixels=True)
                    red_map = PixelMap(pixels, red_lights, individual_pixels=True)
                    prev_brightness = light_state.get_brightness()

                new_pattern = parse_qs(prev_pattern)

                if "speed" not in new_pattern:
                    speed = 1
                elif new_pattern["speed"][0] == "slowest":
                    speed = 1
                elif new_pattern["speed"][0] == "slow":
                    speed = 0.8
                elif new_pattern["speed"][0] == "normal":
                    speed = 0.4
                elif new_pattern["speed"][0] == "fast":
                    speed = 0.2
                elif new_pattern["speed"][0] == "fastest":
                    speed = 0.1

                tuple_color = color.WHITE
                if "color" in new_pattern and len(new_pattern["color"]) == 1:
                    hex_color = new_pattern["color"][0].lstrip("#")
                    tuple_color = tuple(
                        int(hex_color[i : i + 2], 16) for i in (0, 2, 4)
                    )

                if mic_active:
                    pattern.disable()
                    mic_active = False

                # Zones: all, rwb-toggle, white-all, white-toggle, white-unique,
                # rb-toggle, rb-all, rb-unique
                if "zone" not in new_pattern:
                    new_map = PixelMap(
                        pixels, blue_lights + red_lights, individual_pixels=True
                    )
                elif new_pattern["zone"][0] == "rb-all":
                    new_map = PixelMap(
                        pixels, blue_lights + red_lights, individual_pixels=True
                    )
                elif new_pattern["zone"][0] == "rb-unique":
                    new_map = PixelMap(
                        pixels, blue_lights + red_lights, individual_pixels=True
                    )
                elif new_pattern["zone"][0] == "rb-toggle":
                    toggle_group = [blue_lights, red_lights]
                    new_map = PixelMap(pixels, toggle_group, individual_pixels=True)
                elif new_pattern["zone"][0] == "white":
                    new_map = PixelMap(pixels, white_lights, individual_pixels=True)
                elif new_pattern["zone"][0] == "all":
                    new_map = PixelMap(
                        pixels,
                        blue_lights + white_lights + red_lights,
                        individual_pixels=True,
                    )

                if "pattern" not in new_pattern:
                    pattern = AnimationSequence(
                        AnimationGroup(
                            ColorCycle(red_map, speed, colors=[color.RED, color.BLACK]),
                            ColorCycle(
                                white_map, speed, colors=[color.BLACK, color.BLACK]
                            ),
                            ColorCycle(
                                blue_map, speed, colors=[color.BLACK, color.BLUE]
                            ),
                            sync=True,
                        )
                    )
                elif new_pattern["pattern"][0] == "blink":
                    pattern = Blink(new_map, speed=speed, color=tuple_color)
                elif new_pattern["pattern"][0] == "sound-energy":
                    pattern = Visualizer(white_map, "energy", light_state.get_mic())
                    mic_active = True
                elif new_pattern["pattern"][0] == "sound-scroll":
                    pattern = Visualizer(white_map, "scroll", light_state.get_mic())
                    mic_active = True
                elif new_pattern["pattern"][0] == "sound-spectrum":
                    pattern = Visualizer(white_map, "spectrum", light_state.get_mic())
                    mic_active = True
                elif new_pattern["pattern"][0] == "red-blue":
                    pattern = AnimationSequence(
                        AnimationGroup(
                            ColorCycle(red_map, speed, colors=[color.RED, color.BLACK]),
                            ColorCycle(
                                white_map, speed, colors=[color.BLACK, color.BLACK]
                            ),
                            ColorCycle(
                                blue_map, speed, colors=[color.BLACK, color.BLUE]
                            ),
                            sync=True,
                        )
                    )
                elif new_pattern["pattern"][0] == "red-white-blue":
                    pattern = AnimationSequence(
                        AnimationGroup(
                            ColorCycle(
                                red_map,
                                speed,
                                colors=[
                                    color.RED,
                                    color.BLACK,
                                    color.BLACK,
                                    color.BLACK,
                                ],
                            ),
                            ColorCycle(
                                blue_map,
                                speed,
                                colors=[
                                    color.BLACK,
                                    color.BLACK,
                                    color.BLUE,
                                    color.BLACK,
                                ],
                            ),
                            ColorCycle(
                                white_map,
                                speed,
                                colors=[
                                    color.BLACK,
                                    color.WHITE,
                                    color.BLACK,
                                    color.WHITE,
                                ],
                            ),
                            sync=True,
                        )
                    )
                elif new_pattern["pattern"][0] == "chase":
                    pattern = Chase(
                        new_map, speed=speed / 4, size=3, spacing=2, color=tuple_color
                    )
                elif new_pattern["pattern"][0] == "colorcycle":
                    if "colors[]" in new_pattern and len(new_pattern["colors[]"]) > 0:
                        colors = []
                        for hex_color in new_pattern["colors[]"]:
                            hex_color = hex_color.lstrip("#")
                            colors.append(
                                tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
                            )
                        pattern = ColorCycle(new_map, speed=speed, colors=colors)
                    else:
                        pattern = ColorCycle(new_map, speed=speed)
                elif new_pattern["pattern"][0] == "comet":
                    bounce = True
                    if "answer" in new_pattern and new_pattern["answer"][0] == "no":
                        bounce = False
                    pattern = Comet(
                        new_map, speed=speed / 8, color=tuple_color, bounce=bounce
                    )
                elif new_pattern["pattern"][0] == "pulse":
                    pattern = Pulse(
                        new_map, speed=0.05, period=speed * 8, color=tuple_color
                    )
                elif new_pattern["pattern"][0] == "sparkle":
                    pattern = SparklePulse(
                        new_map, speed=speed / 8, period=speed * 2, color=tuple_color
                    )
                elif new_pattern["pattern"][0] == "rainbow":
                    pattern = Rainbow(white_map, speed=speed, step=2)
                elif new_pattern["pattern"][0] == "rainbowchase":
                    pattern = RainbowChase(
                        white_map, speed=speed / 4, size=4, spacing=2, step=48
                    )
                elif new_pattern["pattern"][0] == "rainbowcomet":
                    pattern = RainbowComet(white_map, speed=speed / 4, bounce=True)
                elif new_pattern["pattern"][0] == "rainbowsparkle":
                    pattern = RainbowSparkle(white_map, speed=speed / 2, step=8)

                pixels.fill((0, 0, 0))
                pixels.show()

            pattern.animate()
        else:
            if prev_power == 1:
                pixels.fill((0, 0, 0))
                pixels.show()
                prev_power = 0
            time.sleep(0.2)
