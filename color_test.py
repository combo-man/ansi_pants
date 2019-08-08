from ansi_pants import AnsiPants
import random, colorsys, math, time, string
def update(ap):
    if ap.get_char() == 'q':
        return ap.quit()
    x, y = ap.get_dimensions()
    for i in range(10):
        sat = abs(math.sin(time.time()))
        val = abs(math.cos(time.time() / 3))
        fg = [math.floor(x*256) for x in colorsys.hsv_to_rgb(random.random(), sat, val)]
        bg = [0] * 3
        ap.draw_char(random.choice(string.printable), 
                     random.randint(0, x-1),
                     random.randint(0, y-1),
                     fg,
                     bg)

def start(ap):
    ap.draw_str('WATCH ME GO', x=0, y=0, fg_color='red', bg_color='green')

AP = AnsiPants(update=update, start=start, fps=60)
AP.start()
