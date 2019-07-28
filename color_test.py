from ansi_pants import AnsiPants
import random
def update(ap, delta):
    c = ap.get_char()
    if c == 'q':
        return ap.quit()
    x, y = ap.get_dimensions()
    chars = '$#@!%^&*()-_+={}[]\|><'
    ap.draw_char(random.choice(chars), 
                 random.randint(0, x // 4), 
                 random.randint(0, y // 4),
                 random.choice(ap.color_list),
                 random.choice(ap.color_list))

def start(ap):
    ap.write('WATCH ME GO')

AP = AnsiPants(update=update, start=start)
AP.start()
