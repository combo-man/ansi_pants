from ansi_pants import AnsiPants
import string
def update(ap, delta):
    if ap.get_char() == 'q':
        return ap.quit()
    messages = [
        'THIS IS A SCHEDULED TEST. DO NOT BE ALARMED.    ',
        'DING DONG ',
        string.printable, 
        'Ansi. Pants. Ansi. Stance.',
        'WE GOT A CASE OF THE wahwahs   ',
        ':^)                '
    ]

    def ticker(ap, s, y, start):
        offset = ap.get_clock()
        to_print = ''.join(s[(x + offset) % len(s)] for x in range(len(s)))
        colors = ['b_green'] * len(s)
        for x, char in enumerate(to_print):
            ap.draw_char(char, (start - len(to_print) // 2) + x, y, fg_color=colors[x])

    for y, m in enumerate(messages):
        ticker(ap, m, y, len(max(messages)) // 2)
       
a = AnsiPants(update=update)
a.start()
