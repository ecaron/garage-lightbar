import board
import neopixel
import time
import adafruit_led_animation.color as color
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.helper import PixelMap
from adafruit_led_animation.sequence import AnimationSequence

pixels = neopixel.NeoPixel(board.D18, 60, auto_write=False)

blue_lights = [13, 14, 15, 16, 17, 18, 19, 20, 21]
blue_map = PixelMap(pixels, blue_lights, individual_pixels=True)

white_right_lights = [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
white_right_map = PixelMap(pixels, white_right_lights, individual_pixels=True)

white_left_lights = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]
white_left_map = PixelMap(pixels, white_left_lights, individual_pixels=True)

red_lights = [47, 48, 49, 50, 51, 52, 53, 54, 55]
red_map = PixelMap(pixels, red_lights, individual_pixels=True)

white_lights = white_right_lights + white_left_lights
white_map = PixelMap(pixels, white_lights, individual_pixels=True)

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

red_solid = Solid(red_map, color.RED)
white_solid = Solid(white_map, color.WHITE)
blue_solid = Solid(blue_map, color.BLUE)
red_blink = Blink(red_map, .1, color.RED)
white_blink = Blink(white_map, .1, color.WHITE)
blue_blink = Blink(blue_map, .1, color.BLUE)

animations = AnimationSequence(
    red_blink,
    white_blink,
    blue_blink,
    advance_interval=.5,
    auto_clear=True,
)

while True:
    animations.animate()

