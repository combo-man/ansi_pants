from ansi_pants import AnsiPants
import math, time

def box(ap, size):
    ap.clear_screen()
    if ap.get_char() == 'q':
        return ap.quit()
    wid, hi = ap.get_dimensions()
    side = min(wid, hi)
    mid = side // 2
    hor = u'\u2500'
    ver = u'\u2502'
    tl = u'\u250C'
    tr = u'\u2510'
    bl = u'\u2514'
    br = u'\u2518'

    t = time.time()
    d = math.floor(abs(math.sin(t*2)) * size)
    lil, big = mid - d, mid + d
    ap.draw_char(tl, lil, lil)
    ap.draw_char(tr, big, lil)
    ap.draw_char(bl, lil, big)
    ap.draw_char(br, big, big)
    for i in range(lil + 1, big):
        ap.draw_char(hor, i, lil)
        ap.draw_char(hor, i, big)
        ap.draw_char(ver, lil, i)
        ap.draw_char(ver, big, i)


def update(ap, delta):
    box(ap, 14)
AP = AnsiPants(update=update, flush_always=False)
AP.start()
