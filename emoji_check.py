from ansi_pants import AnsiPants
import urllib.request, json

url      = 'https://unpkg.com/emoji.json@12.1.0/emoji.json'
response = urllib.request.urlopen(url)
txt_data = response.read().decode('utf-8')
data     = json.loads(txt_data)
offset   = 0
def render_page(ap, offset=0):
    wid, hi = ap.get_dimensions()
    index   = (offset * wid * hi)

    for x in range(wid):
        for y in range(hi):
            if index >= len(data):
                return
            ap.draw_char(data[index], x, y)

def update(ap):
    wid, hi = ap.get_dimensions()
    key     = ap.get_char()
    if key == 'a':
        offset -= 1
        render_page(ap, offset)
    if key == 'd':
        offset += 1
        render_page(ap, offset)

        
    

