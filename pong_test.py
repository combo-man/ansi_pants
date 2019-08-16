from ansi_pants import AnsiPants
import random, math, colorsys

n_balls = 30
balls   = []
wid, hi = 80, 24

def draw_ball(ap, ball, char='O'):
    ap.draw_char(char,
                 math.floor(ball['x']), 
                 math.floor(ball['y']), 
                 [math.floor(x * 256) for x in colorsys.hsv_to_rgb(ball['color'], 0.75, 0.75)])
def start(ap):
    wid, hi = ap.get_dimensions()
    for i in range(n_balls):
        theta = random.random() * math.pi * 2
        speed = max(random.random() * 3, 1)
        b = {'color': random.random(), 
             'vx': math.sin(theta) * speed,
             'vy': math.cos(theta) * speed,
             'x': random.random() * wid,
             'y': random.random() * hi}

        draw_ball(ap, b) 
        balls.append(b)

def update(ap):
    wid, hi = ap.get_dimensions()
    ap.clear_screen()
    if ap.get_char() == 'q':
        return ap.quit()
    for b in balls:
        draw_ball(ap, b, 'o')
    for b in balls:
        b['x'] += b['vx']
        b['y'] += b['vy']
        if b['x'] >= wid:
            b['x'] = wid - 1
            b['vx'] *= -1
        if b['x'] < 0:
            b['x'] = 0
            b['vx'] *= -1
        if b['y'] > hi:
            b['y'] = hi - 1
            b['vy'] *= -1
        if b['y'] < 0:
            b['y'] = 0
            b['vy'] *= -1

        draw_ball(ap, b) 

ap = AnsiPants(start=start, update=update)
ap.start()





