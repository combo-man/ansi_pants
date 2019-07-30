from ansi_pants import AnsiPants
import random, colorsys, math, time
def update(ap, delta):
    c = ap.get_char()
    if c == 'q':
        return ap.quit()
    x, y = ap.get_dimensions()
    chars = '$#@!%^&*()-_+={}[]\|><'
    sat = abs(math.sin(time.time()))
    val = abs(math.cos(time.time() / 3))
    fg = [math.floor(x*256) for x in colorsys.hsv_to_rgb(random.random(), sat, val)]
    bg = [0] * 3
    ap.draw_char(random.choice(chars), 
                 random.randint(0, x // 4), 
                 random.randint(0, y // 4),
                 fg,
                 bg,
                 mode='rgb')

def start(ap):
    ap.write('WATCH ME GO')

AP = AnsiPants(update=update, start=start, fps=1000)
AP.start()
