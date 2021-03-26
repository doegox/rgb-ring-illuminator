# RGB Illuminator Ring For Industry Microscope 

<img src="img/rgb_ring_illuminator.jpg" alt="rgb_ring_illuminator" width="200"/>

## Inspiration

The idea came from a [tweet by @Siliconinsid](https://twitter.com/Siliconinsid/status/1367609351733719041) showing experimental sectorial Rheinberg illumination of a chip die with two different colors.

<img src="https://pbs.twimg.com/media/Evq5boeXIAAa_58?format=jpg&name=medium" alt="@Siliconinsid setup" width="200"/>

<img src="https://pbs.twimg.com/media/Evq5bpLXcAAhJXb?format=jpg&name=small" alt="@Siliconinsid die" width="200"/>

I'm using an industry / inspection microscope so I thought it could be interesting to modify an existing ring illuminator to integrate an RGB ring.

I immediately ordered the required components and 20 days later...

## BOM

* 12€ "Ring Illuminator Industry Microscope", e.g. [this one](https://www.aliexpress.com/item/32650371367.html) which is cheap as we'll keep only the enclosure
* 2.75€ "RGB led ring WS2812", e.g. [this one (24 LEDs model)](https://www.aliexpress.com/item/4000054747490.html)
* 2.10€ "30 degree lens for 5050 WS2812", e.g. [this one (30° 100pcs)](https://www.aliexpress.com/item/1005001860359687.html)
* 1.50€ "Level converter 3.3V 5V", e.g. [this one](https://www.aliexpress.com/item/32975077699.html)
* 3.65€ "W600-PICO", e.g. [this one](https://www.aliexpress.com/item/4000314757449.html)

Total with shipping: 22€ !

When buying the ring enclosure and the RGB ring, make sure they fit. I've no idea if it'll be always the case or not...

<img src="img/fit_ring.jpg" alt="fit ring in enclosure" width="200"/>

We'll need also

* some wires
* a micro-USB cable (the USB cable of the ring only delivers power, it has no data wires)
* double-sided tape
* UV glue

## Wemos W600-PICO

Warning: this might not be the most suitable MCU. I had a few spares and wanted to try it as it's small enough to fit in the enclosure, it's dirt cheap and supports MicroPython and Wi-Fi. But it has some caveats as well, as we'll see...

* [Documentation](https://www.wemos.cc/en/latest/w600/w600_pico.html)
* [Getting started](https://www.wemos.cc/en/latest/tutorials/w600/get_started_with_micropython_w600.html)
* [Intro to W600 by Les](https://bigl.es/microcontroller-monday-wemos-w600-pico/)

Its IOs are driven at 3.3V. Firstly I thought the RGB ring would accept a data line driven at 3.3V. It kind of worked but with some weird artifacts. Adding a level shifter solved the issues.

## WS2812B

* [Datasheet](https://www.kitronik.co.uk/pdf/WS2812B-LED-datasheet.pdf)
* [Tutorial for MicroPython and ESP](https://randomnerdtutorials.com/micropython-ws2812b-addressable-rgb-leds-neopixel-esp32-esp8266/)

It uses a proprietary daisy-chain protocol.

## Wiring

No schematics but it's pretty easy.

| PC  | W600-PICO | Level Shifter | RGB Ring |
|:---:|:---------:|:-------------:|:--------:|
| USB | Micro USB |               |          |
|     | GND       | GND           | GND      |
|     | 5V        | HV            | 5V       |
|     | 3V3       | LV            |          |
|     | PB18      | LV1           |          |
|     |           | HV1           | DI       |

Warning: documentation shows MOSI on PB17 but apparently MOSI is rather on PB18 when using the W600 soft-SPI library.

<img src="img/wiring.jpg" alt="wiring picture" width="200"/>

Beware, when taping the ring in the enclosure, be sure to position it properly along horizontal/vertical.
Easiest is probably to start from a diagonal so you can define half and duplicate:
`ring.show(([color_verticale]*6+[color_horizontale]*6)*2)`

## Lenses

To focus light towards the center of the ring, glue the 30° lenses slightly tilted with e.g. some UV glue.

<img src="img/lenses.jpg" alt="tilted lenses" width="200"/>

## W600 in Action

### W600 Software Basics

```python
screen /dev/ttyUSB0 115200
>>> help()
>>> help('modules')
>>> import os
>>> os.listdir()
['sys', 'lib', 'cert', 'boot.py', 'main.py', 'easyw600.py']
```

### W600 File Transfer

W600 has incompatibilities with the stock ampy so we'll use a patched version as explained [here](https://bigl.es/microcontroller-monday-wemos-w600-pico/).

```bash
git clone git@github.com:scientifichackers/ampy.git
cd ampy
python3 -m pip install --user -e .
```

Then apply the patch [ampy-w600.patch](ampy-w600.patch) (original modification of `ampy/pyboard.py` is [here](https://drive.google.com/file/d/1qCvD3ZlEkNoJyoEa_Hlw1Ei1yq9ZsJbG/view)).

Usage:
```
ampy --help
ampy -p /dev/ttyUSB0 -b 115200 ls flash
ampy -p /dev/ttyUSB0 -b 115200 get /flash/boot.py > boot.py
```

### W600 WS2812 Driver

On other MicroPython or Arduino MCUs you can directly use the 
NeoPixel library, e.g. [the one for ESP8266](http://docs.micropython.org/en/v1.8.2/esp8266/esp8266/tutorial/neopixel.html).

But it's not part of the W600 firmware :(

There is a pure Python version [here](https://github.com/JanBednarik/micropython-ws2812), which abuses the SPI to emit the WS2812 protocol.
But W600 has only soft SPI and with an API slightly different, so we'll need t patch this lib.

```
git clone https://github.com/JanBednarik/micropython-ws2812
```
Then apply the patch [ws2812-w600.patch](ws2812-w600.patch) and finally send the file to the W600.
```
ampy -p /dev/ttyUSB0 -b 115200 put micropython-ws2812/ws2812.py
```

### W600 Ring Usage Examples

```python
from ws2812 import WS2812
ring = WS2812(led_count=24)
# all white
ring.show([(255,255,255)]*24)
# all red
ring.show([(255,0,0)]*24)
# kind of rainbow, for test
ring.show(([(255,0,0)]+[(255,255,0)]+[(0,255,0)]+[(0,255,255)]+[(0,0,255)]+[(255,0,255)])*4)
# half red, half green, similar to the original idea tweet
ring.show(([(255,0,0)]*6+[(0,255,0)]*6)*2)
# same, but disable LEDs in corners
ring.show(([(255,0,0)]*4+[(0,0,0)]*2+[(0,255,0)]*4+[(0,0,0)]*2)*2)
```

### W600 Software, untested

Flashing tool

```
git clone https://github.com/vshymanskyy/w600tool
python3 -m pip install --user pyserial PyPrind xmodem
cd w600tool
python3 w600tool.py -p /dev/ttyUSB0 -u wm_w600.fls --upload-baud 115200
```

## Misc

Consumption: 0.7A (3.3W) when all RGB are turned on and white.

One can add buttons or potentiometer to the design. Beware W600 has no ADC so a [trick with RC](https://www.microcontrollertips.com/mcus-using-digital-input-read-analog-signal-without-adc/) needs to be used.

## TODO test Wi-Fi

Example of web service for ESP8266 and RGB strip: https://github.com/petabite/uPixels based on https://github.com/petabite/uWeb

Maybe doable but must be adapted from NeoPixel to ws2812 driver.

## TODO move to ESP8266

W600 has really too many limitations, next step will be to try again with an ESP8266...

