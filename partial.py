import board
import neopixel
import time
from adafruit_led_animation.helper import PixelMap
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation import helper
from adafruit_led_animation.color import PURPLE, JADE, AMBER

YELLOW = (255, 150, 0)
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

white_mirror = []
white_invert = []
for i in range(len(white_left_lights)):
    white_mirror.append((white_left_lights[i],white_right_lights[i]))
    white_invert.append((white_left_lights[i],white_right_lights[len(white_left_lights)-1-i]))

white_mirror_map = PixelMap(pixels,white_mirror,individual_pixels=True)
white_invert_map = PixelMap(pixels,white_invert,individual_pixels=True)

end_invert = []
for i in range(len(blue_lights)):
    end_invert.append((blue_lights[i],red_lights[len(red_lights)-1-i]))
end_invert_map = PixelMap(pixels,end_invert,individual_pixels=True)

right_side_lights = blue_lights + white_right_lights
left_side_lights = white_left_lights + red_lights
full = right_side_lights + left_side_lights
full_mirror = []
full_invert = []
for i in range(len(right_side_lights)):
    full_mirror.append((right_side_lights[i],left_side_lights[i]))
    full_invert.append((right_side_lights[i],left_side_lights[len(left_side_lights)-1-i]))
full_map = PixelMap(pixels,full,individual_pixels=True)
full_mirror_map = PixelMap(pixels,full_mirror,individual_pixels=True)
full_invert_map = PixelMap(pixels,full_invert,individual_pixels=True)

comet_h = Comet(
    full_mirror_map, speed=0.1, color=PURPLE, tail_length=3, bounce=True
)
while True:
    comet_h.animate()

#blink = Blink(white_right_map, 0.5, color.PURPLE)
#while True:
#    blink.animate()

light_spot = {"blue": 0, "white_right": 0, "white_left": 0, "red": 0}
while False:
    blue_map[light_spot['blue']] = YELLOW
    blue_map.show()
    light_spot['blue'] = light_spot['blue'] + 1
    white_right_map[light_spot['white_right']] = YELLOW
    white_right_map.show()
    light_spot['white_right'] = light_spot['white_right'] + 1
    white_left_map[light_spot['white_left']] = YELLOW
    white_left_map.show()
    light_spot['white_left'] = light_spot['white_left'] + 1
    red_map[light_spot['red']] = YELLOW
    red_map.show()
    light_spot['red'] = light_spot['red'] + 1

    if light_spot['blue'] >= len(blue_lights):
        light_spot['blue'] = 0
        blue_map.fill(0)

    if light_spot['white_right'] >= len(white_right_lights):
        light_spot['white_right'] = 0
        white_right_map.fill(0)

    if light_spot['white_left'] >= len(white_left_lights):
        light_spot['white_left'] = 0
        white_left_map.fill(0)

    if light_spot['red'] >= len(red_lights):
        light_spot['red'] = 0
        red_map.fill(0)
    time.sleep(0.25)
