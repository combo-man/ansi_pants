import shutil, sys, tty, termios, os, time, select

class AnsiPants:
    '''
    AnsiPants: The single-file terminal drawing library.
    '''
    ansi_codes = {
        'fg': ['30','31','32','33','34','35','36','37',
               '30;1','31;1','32;1','33;1','34;1',
               '35;1','36;1','37;1'],
        'bg': ['40','41','42','43','44','45','46',
               '47','100','101','102','103','104',
               '105','106','107']
    }
   
    pair_plate   = u'\u001b[{};{}m'
    offset_plate = u'\u001b[{};{}H'

    color_list = ['black','red','green','yellow',
                  'blue','magenta','cyan','white',
                  'b_black','b_red','b_green','b_yellow',
                  'b_blue','b_magenta','b_cyan','b_white']


    def __init__(self, in_file=sys.stdin, out_file=sys.stdout, flush_always=False, 
                 start_call=None, update_call=None, kill_call=None, fps=30):   
       
        yd, xd            = shutil.get_terminal_size()
        self._height      = yd
        self._width       = xd
        self._in_file     = in_file
        self._out_file    = out_file
        self._start_call  = start_call
        self._update_call = update_call
        self._kill_call   = kill_call
        self.flush_always = flush_always
        self._last_frame  = time.time()
        self._fps         = 30
        self.start()

    def __del__(self):
        self.cleanup()

    def start(self):
        '''
        Initiate terminal session. Called at __init__.
        '''
        if self._start_call:
            self._start_call(self)

        os.system('setterm -cursor off')
        self.prev_settings = termios.tcgetattr(self._in_file)
        tty.setraw(self._in_file)
        self.reset_cursor()
        self.clear_screen()

    def update(self):
        '''
        Main update loop
        '''
        ctime = time.time()
        delta = ctime - self._last_frame
        diff  = delta - (self._fps / 60)
        if diff > 0:
            self._last_frame = ctime - diff
            if self._update_call:
                self._update_call(self, delta)

    def cleanup(self):
        '''
        Restores terminal to previous settings. Called at __del__.
        '''
        if self._kill_call:
            self._kill_call()

        os.system('setterm -cursor on')
        termios.tcsetattr(self._in_file, termios.TCSADRAIN, self.prev_settings)

    def reset_cursor(self):
        '''
        Puts cursor back to 0, 0
        TODO:
            Replace with a call to move_cursor?
        '''
        self.write(u'\u001b[f', flush=True)

    def clear_screen(self):
        self.write(chr(27) + '[2J', flush=True)

    def get_input_handler(self):
        '''
        Returns a callback to get input
        TODO:
            Replace with event polling?
        '''
        def inputter():
            return self.get_char()

        return inputter

    def write(self, txt, flush=False):
        self._out_file.write(txt) 
        if flush or self.flush_always:
            self.flush_display()
        
    def move_cursor(self, x, y):
        '''
        Moves cursor to x, y (y, x in terminal conventions)
        '''
        self.write(self.offset_plate.format(y, x))

    def write_data(self, *args):
        '''
        Convert buffer and write to output. (See: bake_ansi_string )
        '''
        self.write(self.bake_ansi_string(*args))
        self.reset_cursor()
   
    def flush_display(self):
        self._out_file.flush()  

    def get_color_plate(self, fg_color, bg_color):
        '''
        Gets a string representing a foreground and background color pair.
        TODO:
            Implement string caching
        '''
        try:
            return self._pair_strings[fg_color][bg_color]
        except:
            fg = self.lookup_ansi_code(fg_color, layer='fg')
            bg = self.lookup_ansi_code(bg_color, layer='bg')
            plate = self.pair_plate.format(fg, bg)
            return plate

    def lookup_ansi_code(self, color_string, layer='fg'):
        '''
        TODO:
            Make more better.
        '''
        return self.ansi_codes[layer][self.color_list.index(color_string)]
    
    def make_ansi_data(self, char_table, fg_color_table, bg_color_table, off_x=0, off_y=0):
        '''
        Converts 3 x*y arrays into a a list of ANSI control strings.
        All 3 arrays must be of the same size (x*y).
        char_table is an x*y array of single characters.
        (fg/bg)_color_table is an x*y array of color codes (See: ansi_codes)
        off_x and off_y are offsets from the top-left corner of terminal.
        '''
        string_data = [self.offset_plate.format(off_y, off_x)]
        plate = ''
        for y in range(len(char_table)):
            for x in range(len(char_table[y])):
                plate = self.get_color_plate(fg_color_table[y][x], bg_color_table[y][x])
                string_data.append(plate + char_table[y][x])
    
            string_data.append('\u001b[0m')
            #\r moves the cursor back to beginning of line, cause honestly fsck newline behaviour
            string_data.append('\r\n')
            string_data.append('\u001b[{}C'.format(off_x-1))
    
        return string_data
    
    def bake_ansi_string(self, *args):
      return ''.join(self.make_ansi_data(*args))

    def get_char(self, wait=0):
        '''
        Gets a single char from input file, without waiting.
        Returns an empty string if nothing in file.
        '''
        if select.select([self._in_file], [], [], wait) == ([self._in_file], [], []):
            return self._in_file.read(1)
        else:
            return ''
