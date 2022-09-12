# Retrofit Police Lightbar - LEDs & Audio Visualizer

This is a light-weight program that replaced the incandescent bulbs of an [older police lightbar](https://en.wikipedia.org/wiki/Emergency_vehicle_lighting) with an internet-controlled LED strip. This retrofitting is only intended for home-use. It retains the standard red/white/blue flashers, but also adds many more color capabilities to have it light up the room!

***Disclaimer:** This is a personal project that I put together for my father-in-law. He had a police lightbar that he wanted help fixing up, and lightbars require complex, expensive controllers (for all the different patterns they do, [many wires are required](github-docs/lightbar-previous-wiring.png)). Rather than spending $200+ for a used controller, this was a great opportunity to attach a Raspberry Pi to an LED strip & a microphone.*

***Reason for disclaimer:** I'm not sure if anyone else would be interested in a setup like this. If there is interest, we'd probably want to extract the LED parameters & microphone settings. The configurations are hard-coded, but if others want to use this we should make them easier to alter. If you're interested, contact me! The more, the merrier!*

## Features

* Web interface to control 15 different light patterns
* Physical buttons to cycle through presets, adjust brightness, and turn on/off
* Three sound-sensing modes that adjust lights based on music, sound or noises
* Auto-on based on time of day
* Auto-off after an adjustable number of hours

## Screenshots & Examples

### Light Modes In Action

#### Blink
![Lightbar Blinking](github-docs/blink.gif)

#### Chase
![Lightbar Chasing](github-docs/chase.gif)

#### Color Cycle (with rainbow color defaults)
![Lightbar Color Cycle](github-docs/colorcycle.gif)

#### Comet
![Lightbar Comet](github-docs/comet.gif)

#### Pop
![Lightbar Pop](github-docs/pop.gif)

#### Pulse
![Lightbar Pop](github-docs/pop.gif)

#### Red Blue Flashers
![Lightbar Right Blue](github-docs/red-blue.gif)

#### Red White Blue Flashers
![Lightbar Right White Blue](github-docs/red-white-blue.gif)

#### Unicorn Party 1 - Rainbow
![Lightbar Unicorn Party 1](github-docs/unicorn-party-1.gif)

#### Unicorn Party 2 - Rainbow Chase
![Lightbar Unicorn Party 2](github-docs/unicorn-party-2.gif)

#### Unicorn Party 3 - Rainbow Comet
![Lightbar Unicorn Party 3](github-docs/unicorn-party-3.gif)

#### Unicorn Party 4 - Rainbow Sparkle
![Lightbar Unicorn Party 4](github-docs/unicorn-party-4.gif)

#### Sound Reactive - Energy
![Lightbar Sound Energy](github-docs/sound-energy.gif)

#### Sound Reactive - Scroll
![Lightbar Sound Scroll](github-docs/sound-scroll.gif)

#### Sound Reactive - Spectrum
![Lightbar Sound Spectrum](github-docs/sound-spectrum.gif)


## Web Interface

![Top half of homescreen](github-docs/home-top.png)

![Bottom half of homescreen](github-docs/home-bottom.png)


## Instructions

Here's the crude version of the work that I did to make this work:
1. I removed the wiring & lighting from the lightbar.
2. Follow [Adafruit's Guide to NeoPixel on Raspberry Pi](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring) to attach a Raspberry Pi to an strip of 60 LEDs.
3. Wire a [1x4 Keypad](https://www.adafruit.com/product/1332) to the bottom to allow physical button control. 
4. Install the [USB Desktop Microphone](https://www.amazon.com/dp/B08CF2YP8M) to the Pi, and mount it to the bottom of the lightbar. 
5. Disable all not-critical processes on the Pi, and setup a script to run `app.py` as a service.
6. Enjoy a lightbar that brings people together!

## Hardware Used

* [Whelen Lightbar - Casing Only, circa 1995](https://www.whelen.com/product-category/lighting/lightbars/)
* [Raspberry Pi - Model 3 or newer](https://www.raspberrypi.com/)
* [USB Desktop Microphone](https://www.amazon.com/dp/B08CF2YP8M)
* [Adafruit NeoPixel LED Strip](https://www.adafruit.com/product/1376)
* [1x4 Keypad](https://www.adafruit.com/product/1332)

## Credits & Special Thanks

* [Adafruit's Guide to NeoPixel on Raspberry Pi](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring)
* [NES.css - Theme of the Web Interface](https://nostalgic-css.github.io/NES.css/)
* [Scott Lawson's Amazing Audio Reactive LED Strip](https://github.com/scottlawsonbc/audio-reactive-led-strip)
