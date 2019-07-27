from ansi_pants import AnsiPants
import random
def update(ap, delta):
    x, y = ap.get_dimensions()
    chars = '$#@!%^&*()-_+={}[]\|><'
    ap.draw_char(random.choice(chars), 
                 random.randint(0, x), 
                 random.randint(0, y),
                 random.choice(ap.color_list),
                 random.choice(ap.color_list))

def start(ap):
    ap.write('WATCH ME GO')

AP = AnsiPants(update=update, start=start)
AP.start()
