from ansi_pants import AnsiPants
import random, math

STAR_CHARS = '.*'
COLORS = ['red'] * 2
COLORS += ['green'] * 3
COLORS += ['blue']
COLORS += ['yellow'] * 3

WIDTH = 80
HEIGHT = 24
N_STARS = 128
STARS = []

for i in range(N_STARS):
    STARS.append({
        'color': random.choice(COLORS),
        'layer': random.randint(1, 7),
        'x_pos': random.randint(0, WIDTH),
        'y_pos': random.randint(0, HEIGHT)})

sorted(STARS, key=lambda x : x['layer'], reverse=True)
def update(ap, delta):
    if ap.get_char() == 'q':
        ap.quit() 
    ap.clear_screen()
    for i, star in enumerate(STARS):
        mv_scale = 1/(star['layer'])
        prev_pos = star['y_pos']
        star['y_pos'] += mv_scale
        if star['y_pos'] >= HEIGHT:
            star['y_pos'] = 0
            star['x_pos'] = random.randint(0, WIDTH)

        char = None
        color = None
        if (ap.get_clock() + i) // 10 % 2 == 0:
            char = '.' if star['layer'] > 3 else '*'
            color = 'b_' + star['color']
        else:
            char = '.'
            color = star['color']
        ap.draw_char(char, star['x_pos'], math.floor(star['y_pos']), color, 'black')

ap = AnsiPants(update=update, flush_always=True)
ap.start()
