import machine, esp, neopixel, time

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# To inject directly a buffer:
def esprgb(np, grb_list):
    esp.neopixel_write(np.pin, bytearray(i for grb in grb_list for i in grb), True)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def rainbow_cycle(np, wait, loop=1):
    for _ in range(loop):
        for j in range(255):
            for i in range(np.n):
                rc_index = (i * 256 // np.n) + j
                np[i] = wheel(rc_index & 255)
            np.write()
            time.sleep_ms(wait)

def color_chase(np, color, wait, n=1, loop=1):
    # wait in fraction of second
    # n: number of LEDs to keep on
    # loop: how many times to loop the animation
    for j in range(loop):
        for i in range(np.n):
            np[i-n] = BLACK
            if color == 'rainbow':
                rc_index = (i * 256 // np.n) + j
                np[i] = wheel(rc_index & 255)
            else:
                np[i] = color
            time.sleep(wait)
            np.write()

def off(np):
    esprgb(np, [BLACK]*24)

def on(np):
    esprgb(np, [WHITE]*24)

# GPIO5 == D1 on NodeMCU
np = neopixel.NeoPixel(machine.Pin(5), 24)
rainbow_cycle(np, 1, 1)

off(np)
#color_chase(np, RED, 0.1, 3, 3)
color_chase(np, WHITE, 0.1, 1, 3)
color_chase(np, WHITE, 0.1, 4, 3)
#color_chase(np, 'rainbow', 0.1, 1, 3)

for _ in range(3):
    esprgb(np, ([RED]*4+[BLACK]*2+[GREEN]*4+[BLACK]*2)*2)
    time.sleep(1)
    esprgb(np, ([GREEN]*4+[BLACK]*2+[RED]*4+[BLACK]*2)*2)
    time.sleep(1)

on(np)
time.sleep(2)
off(np)
