import shutil
import sys
import tty
import termios
import os
import time
import select
import traceback
import math
'''
TODO:
Organize private and public methods. Also organize method
order so it has some sort of legibility :P

Add a script to run all tests in some sane way. Will probably
require user interaction, but could also pipe to an output file
and assert (would break on every change to output behaviour!!!).

Refactor color arguments into color objects. This way they can easily be
generated and cached at init.
Possibly generate named colors (web safe???)?

Also change color lists to reflect that bright is a mode, not a color.
Make this a trait of color objects.
Maybe add bold, underline etc as well.
'''

class AnsiPants:
    '''
    AnsiPants: The single-file terminal drawing library.

    Args:
        in_file (file): The input file to read from.
        out_file (file): The output file to write to.
        flush_always (bool): Flush standard output for every write?
        start (function): User-supplied startup callback.
        update (function): User-supplied update callback.
        kill (function): User-supplied termination callback.
        fps (int): Frames per second to attempt to run at.
        raw_mode (bool): True = raw, False = cbreak

    Attributes:
        _ansi_color_table: Lookup table for basic ANSI color codes.

        _ansi_line_set: Move cursor down a row and to first column.
        _ansi_escape: Escape code header.
        _ansi_reset_color: Restore current color to default.
        _ansi_color_plate16: Format string for single basic color (fg or bg).
        _ansi_pair_plate16: Format string for basic color pair.
        _ansi_pair_plate8bit: Format string for 256-color fg and bg.
        _ansi_fg_plate_rgb: Format string for single rgb fg color.
        _ansi_bg_plate_rgb: Format string for single rgb bg color.
        _ansi_pair_plate_rgb: Format string for rgb color pair.

        _ansi_color_list: List of supported basic color names.

        _height: Height of viewport.
        _width: Width of viewport.
        _cursor_x: Current x position of the cursor.
        _cursor_y: Current y position of the cursor.
        _in_file: Current input file in use.
        _out_file: Current output file in use.
        _start_call: Current user supplied startup callback.
        _update_call: Current user supplied update callback.
        _kill_call: Current user supplied termination callback.
        _flush_always: Wether to flush all writes to output file.
        _last_frame: The last time self.run was called.
        _exit: Wether to terminate program.
        _fps: The current frames per second to run at.
        _clock: Elapsed frames since startup.
        _delta: The last recorded delta between frames.
        _raw_mode: Is file in raw mode.
        _buffer_mode: Wether to use an intermediary buffer.
    '''

    _ansi_color_table = {
        'fg': ['30', '31', '32', '33', '34', '35', '36', '37',
               '30;1', '31;1', '32;1', '33;1', '34;1',
               '35;1', '36;1', '37;1'],
        'bg': ['40', '41', '42', '43', '44', '45', '46',
               '47', '100', '101', '102', '103', '104',
               '105', '106', '107']
    }

    _ansi_line_set       = '\r\n'
    _ansi_escape         = '\u001b'
    _ansi_reset_color    = '\u001b[0;m'
    _ansi_color_plate16  = '\u001b[{}m'
    _ansi_pair_plate16   = '\u001b[0;{};{}m'
    _ansi_pair_plate8bit = '\u001b[38;5;{}m\u001b[38;5;{}m'
    _ansi_fg_plate_rgb   = '\u001b[38;2;{};{};{}m'
    _ansi_bg_plate_rgb   = '\u001b[48;2;{};{};{}m'
    _ansi_pair_plate_rgb = '\u001b[38;2;{};{};{}m\u001b[48;2;{};{};{}m'
    _ansi_offset_plate   = '\u001b[{};{}H'

    _ansi_color_list = ['black', 'red', 'green', 'yellow',
                        'blue', 'magenta', 'cyan', 'white',
                        'b_black', 'b_red', 'b_green', 'b_yellow',
                        'b_blue', 'b_magenta', 'b_cyan', 'b_white']


    def __init__(self, in_file=sys.stdin, out_file=sys.stdout, flush_always=False,
                 start=None, update=None, kill=None, fps=30, raw_mode=False):

        yd, xd            = shutil.get_terminal_size()
        self._height      = yd
        self._width       = xd
        self._in_file     = in_file
        self._out_file    = out_file
        self._start_call  = start
        self._update_call = update
        self._kill_call   = kill
        self._flush_always = flush_always
        self._last_frame  = time.time()
        self._exit        = False
        self._fps         = fps
        self._clock       = 0
        self._delta       = 0
        self._raw_mode    = raw_mode
        self._cursor_x    = 0
        self._cursor_y    = 0
        self._buffer_mode = False

    def __del__(self):
        '''Restore terminal if self is collected somehow.'''
        self._cleanup()

    def start(self):
        '''Initiate terminal session. Called at __init__.'''
        #change terminal settings, save for restoration at exit
        os.system('setterm -cursor off')
        self.prev_settings = termios.tcgetattr(self._in_file)
        if self._raw_mode:
            tty.setraw(self._in_file)
        else:
            tty.setcbreak(self._in_file)

        self.reset_cursor()
        self.clear_screen()
        if self._start_call:
            self._start_call(self)

        #call main loop
        try:
            while not self._exit:
                self._run()
        except:
            self._on_error(traceback.format_exc())
        finally:
            self._cleanup()

        print('goodbye!')
        time.sleep(.25)

    def quit(self):
        '''Set exit flag. Terminate program after current update cycle.'''
        self._exit = True

    def get_dimensions(self):
        '''Get current terminal dimensions.'''
        return (self._height, self._width)

    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, fps):
        self._fps = fps

    @property
    def clock(self):
        return self._clock

    @property
    def flush_mode(self):
        return self._flush_always

    @flush_mode.setter
    def flush_mode(self, mode):
        self._flush_always = mode

    @property
    def buffer_mode(self):
        return self_buffer_mode

    @buffer_mode.setter
    def buffer_mode(self, mode):
        self._buffer_mode = mode

    @property
    def out_file(self):
        return self._out_file

    @out_file.setter
    def out_file(self, file_ref):
        self._out_file.flush()
        self._out_file = file_ref

    @property 
    def in_file(self):
        return self._in_file

    @in_file.setter
    def in_file(self, file_ref):
        '''
        TODO: Actually do this
        NASTY!
        '''
        pass

    def draw_char(self, char, x, y, fg_color='white', bg_color='black'):
        '''Draw an (optionally) colored char at (x, y) in output file.'''
        self.move_cursor(x, y)
        self.write(self.get_colorized(char, fg_color, bg_color))

    def draw_str(self, string, x, y, fg_color_list=False,
                 bg_color_list=False, fg_color='white', bg_color='black'):
        '''
        Draw an (optionally) colored str at (x, y) in output file.
        Automatically clips at viewport borders.

        TODO:
            Add modes for vertical strings and wraparound drawing

        '''
        end = min(x + len(s), self._width - 1)
        res = []
        c = 0
        for i in range(x, end):
            fg = (fg_color_list and fg_color_list[i]) or fg_color
            bg = (bg_color_list and bg_color_list[i]) or bg_color
            res.append(self.get_colorized(string[c], fg, bg))
            c += 1

        self.move_cursor(x, y)
        self.write(''.join(res))

    def write(self, txt, flush=False):
        '''Write data to outfile'''
        self._out_file.write(txt)
        if flush or self._flush_always:
            self.flush_screen()

    def reset_cursor(self):
        '''
        Puts cursor back to 0, 0
        TODO:
            Replace with a call to move_cursor?
        '''
        self.write(u'\u001b[f')

    def reset_color(self):
        '''Reset color (and all styling flags!)'''
        self.write(self._ansi_reset_color)

    def get_cursor_pos(self):
        '''Gets the current cursor position'''
        return (self._cursor_x, self._cursor_y)

    def move_cursor(self, x, y):
        '''Moves cursor to x, y (y, x in terminal conventions)'''
        self._cursor_x = x % self.width
        self._cursor_y = y % self.height
        self.write(self._ansi_offset_plate.format(y, x))

    def clear_screen(self):
        '''Clear the display'''
        self.write(chr(27) + '[2J')

    def flush_screen(self):
        '''Flush the outfile!'''
        self._out_file.flush()

    def set_color(self, fg_color, bg_color):
        '''Sets the color to use for any subsequent prints.'''
        pair = self._get_color_plate_pair(fg_color, bg_color)
        self.write(pair.format('', ''))

    def get_colorized(self, string, fg_color, bg_color):
        '''Returns colorized version of string'''
        return self._get_color_plate_pair(fg_color, bg_color) + string

    def write_data(self, *args):
        '''Convert buffer and write to output. (See: bake_ansi_string )'''
        self.write(self.bake_ansi_string(*args))
        self.reset_cursor()

    def make_ansi_data(self, char_table, fg_color_table, bg_color_table, off_x=0, off_y=0):
        '''
        Converts 3 x*y arrays into a a list of ANSI control strings.
        All 3 arrays must be of the same size (x*y).
        char_table is an x*y array of single characters.
        (fg/bg)_color_table is an x*y array of color codes (See: _ansi_color_table)
        off_x and off_y are offsets from the top-left corner of terminal.
        '''
        string_data = [self._ansi_offset_plate.format(off_y, off_x)]
        plate = ''
        for y in range(len(char_table)):
            for x in range(len(char_table[y])):
                plate = self._get_color_plate_pair(fg_color_table[y][x], bg_color_table[y][x])
                string_data.append(plate + char_table[y][x])

            string_data.append(self._ansi_reset_color)
            #\r moves the cursor back to beginning of line, cause honestly fsck newline behaviour
            string_data.append(self._ansi_line_set)
            string_data.append('\u001b[{}C'.format(off_x-1))

        return string_data

    def bake_ansi_string(self, *args):
        '''Shortcut method to stringify make_ansi_data'''
        return ''.join(self.make_ansi_data(*args))

    def get_char(self, wait=0):
        '''
        Gets a single char from input file, without waiting.
        Returns an empty string if nothing in file.
        '''
        if select.select([self._in_file], [], [], wait) == ([self._in_file], [], []):
            return self._in_file.read(1)
        return ''

    def _run(self):
        '''Main update loop.'''
        #update reported dimensions
        self._height, self._width = shutil.get_terminal_size()
        ctime = time.time()
        self._delta = ctime - self._last_frame
        #loop while behind
        if self._delta >= 1/self._fps:
            self._last_frame = ctime
            self._clock += 1
            if self._update_call:
                self._update_call(self)
                self._out_file.flush()

    def _on_error(self, err):
        '''Do this if all else fails.'''
        while self.get_char() != 'q':
            fg, bg = 'white', 'red'
            if math.floor(time.time() % 2):
                fg, bg = bg, fg
            self.set_color(fg, bg)
            self.clear_screen()
            self.reset_cursor()
            self.write('Oh no, AnsiPants encountered an error!' + self._ansi_line_set)
            self.write(self._ansi_line_set * 3)
            for l in err.splitlines():
                self.write(l + self._ansi_line_set)

            self.write(self._ansi_line_set * 3)
            self.write('Press q to exit.' + self._ansi_line_set)
            time.sleep(0.5)
        self.clear_screen()

    def _cleanup(self):
        '''Restores terminal to previous settings. Called at __del__.'''
        if self._kill_call:
            self._kill_call()
        os.system('setterm -cursor on')
        termios.tcsetattr(self._in_file, termios.TCSADRAIN, self.prev_settings)
        self.reset_color()
        self.clear_screen()
        self.reset_cursor()

    def _get_color_plate(self, color, layer='fg'):
        '''
        Generate a color plate (for a given layer
        '''
        if isinstance(color, list):
            if layer == 'fg':
                return self._ansi_fg_plate_rgb.format(*color)
            return self._ansi_bg_plate_rgb.format(*color)

        return self._ansi_color_plate16.format(self._lookup_color_code(color, layer))

    def _get_color_plate_pair(self, fg_color, bg_color):
        '''
        Gets a string representing a foreground and background color pair.
        TODO:
            Implement string caching
        '''
        fg = self._get_color_plate(fg_color, 'fg')
        bg = self._get_color_plate(bg_color, 'bg')
        return self._ansi_reset_color + fg + bg

    def _lookup_color_code(self, color, layer='fg'):
        '''
        TODO:
            Make more better.
        '''
        return self._ansi_color_table[layer][self._ansi_color_list.index(color)]

