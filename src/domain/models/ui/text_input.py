import pygame
import pygame.locals as pl
import pyperclip
from pygame.math import Vector2 as vec

from domain.utils import colors

pygame.font.init()

class TxtLine:
    """Stores the text from one line of the input buffer.
    """    
    def __init__(self, left = "", right = ""):
        self.left = left
        """The text on the left of the cursor."""
        self.right = right
        """The text on the right of the cursor."""

class TextInput:
    def __init__(self, rect: pygame.Rect, **kwargs):
        
        self.rect = rect
        """The rect of the text input box."""
        
        self.start_kwargs = kwargs.copy()
        
        _initial_text = kwargs.pop("text", "")
        self.buffer: list[TxtLine] = [TxtLine(_initial_text, "")]
        """The buffer of the input. It's a list of lines."""
        self.left = self.buffer[0].left
        """The text on the left of the cursor."""
        self.right = self.buffer[0].right
        """The text on the right of the cursor."""
        self.y_cursor = 0
        """The index of the current line of the cursor."""
        self.selection_range: tuple[vec, vec] = (vec(0,0), vec(0,0))
        """The selected text. A pair of start/end coordinates (vector 2)."""
        self._clock = pygame.time.Clock()
        self._cursor_blink_interval = 300
        self._cursor_visible = False
        self._last_blink_toggle = 0
        self.focused = False
        """If the text box is focused. Non focused text box wont receive keyboard input."""
        self.place_holder = kwargs.pop("place_holder", "")
        """The placeholder text of the input."""
        
        self.validator = kwargs.pop("validator", lambda x, y: True)
        """The function that will validate the next typed char. Receives the TextInput and the pygame.event.key parameters."""
        self.readonly = kwargs.pop("readonly", False)
        """If the text box is read-only. If set to true, can't be focused and edited."""
        self.contain_in_borders = kwargs.pop("contain_in_borders", True)
        """If the input should prevent the text from overlapping it's box borders."""
        self.tab_callback = kwargs.pop("tab_callback", self._process_tab)
        """The function to be called when pressing the tab key. The default is to add 4 spaces."""
        
        self._font_object = kwargs.pop("font", pygame.font.Font(pygame.font.get_default_font(), 25))
        self._antialias = kwargs.pop("antialias", True)
        self._font_color = kwargs.pop("font_color", colors.BLACK)
        
        self.border_width = kwargs.pop("border_width", 5)
        """The width of the box borders."""
        self.border_color = kwargs.pop("font_color", colors.LIGHT_GRAY)
        """The color of the box borders."""
        self.padding: vec = kwargs.pop("padding", vec(18,18))
        """The horizontal and vertical space between the text and the input borders."""
        self.background_color = kwargs.pop("background_color", colors.WHITE)
        """The background color of the text box."""
        self.place_holder_color = kwargs.pop("place_holder_color", colors.LIGHT_GRAY)
        """Color of the input's placeholder text."""
        self._cursor_width = kwargs.pop("cursor_width", 3)
        self._cursor_color = kwargs.pop("cursor_color", colors.BLACK)
        self.selection_color = kwargs.pop("selection_color", colors.SELECTION_BLUE)
        """Color of the text box background when the text is selected."""

        self._surface = pygame.Surface((self._cursor_width, self._font_object.get_height()))
        self._rerender_required = True
        

    @property
    def value(self):
        """ Get / set the value currently inputted. Doesn't change cursor position if possible."""
        return self.buffer[self.y_cursor].left + self.buffer[self.y_cursor].right
    
    @value.setter
    def value(self, value):#ok
        if len(self.buffer)-1 < self.y_cursor:
            self.buffer.append(TxtLine())
        self.buffer[self.y_cursor] = TxtLine()
        cursor_left = self.cursor_pos[0]
        self.buffer[self.y_cursor].left = value[:cursor_left]
        self.buffer[self.y_cursor].right = value[cursor_left:]
    
    @property
    def cursor_pos(self):#ok
        """ Get / set the position of the cursor. Will clamp to [0, length of input]. """
        return (len(self.buffer[self.y_cursor].left), self.y_cursor)

    @cursor_pos.setter
    def cursor_pos(self, value):#ok
        self.y_cursor = value[1]
        line = self.buffer[self.y_cursor]
        line_value = line.left + line.right
        self.buffer[self.y_cursor].left = line_value[:value[0]]
        self.buffer[self.y_cursor].right = line_value[value[0]:]
        
    def set_buffer(self, lines: list[str]):
        self.buffer.clear()
        self.y_cursor = 0
        for line in lines:
            self.buffer.append(TxtLine(left=line))
    
    
    @property
    def surface(self):
        """ Get the surface with the rendered user input """
        if self._rerender_required:
            self._rerender()
            self._rerender_required = False
        return self._surface
    
    @property
    def antialias(self):
        """ Get / set antialias of the render """
        return self._antialias

    @antialias.setter
    def antialias(self, v):
        self._antialias = v
        self._require_rerender()

    @property
    def font_color(self):
        """ Get / set color of rendered font """
        return self._font_color

    @font_color.setter
    def font_color(self, v):
        self._font_color = v
        self._require_rerender()

    @property
    def font_object(self):
        """ Get / set the font object used to render the text """
        return self._font_object

    @font_object.setter
    def font_object(self, v):
        self._font_object = v
        self._require_rerender()

    @property
    def cursor_visible(self):
        """ Get / set cursor visibility (flips again after `.cursor_interval` if continuously update)"""
        return self._cursor_visible
    
    @cursor_visible.setter
    def cursor_visible(self, v):
        self._cursor_visible = v
        self._last_blink_toggle = 0
        self._require_rerender()
    
    @property
    def cursor_width(self):
        """ Get / set width in pixels of the cursor """
        return self._cursor_width
    
    @cursor_width.setter
    def cursor_width(self, v):
        self._cursor_width = v
        self._require_rerender()
    
    @property
    def cursor_color(self):
        """ Get / set the color of the cursor """
        return self._cursor_color
    
    @cursor_color.setter
    def cursor_color(self, v):
        self._cursor_color = v
        self._require_rerender()

    @property
    def cursor_blink_interval(self):
        """ Get / set the interval of time with which the cursor blinks (toggles), in ms"""
        return self._cursor_blink_interval
    
    @cursor_blink_interval.setter
    def cursor_blink_interval(self, v):
        self._cursor_blink_interval = v
        
    def in_bounds(self, key):
        if not self.contain_in_borders:
            return True
        
        cmd_keys = [pl.K_BACKSPACE, pl.K_DELETE, pl.K_RETURN, pl.K_KP_ENTER, pl.K_LEFT, pl.K_UP, pl.K_DOWN, pl.K_RIGHT]

        if not self.fits_in_line(self.y_cursor, " ") and key not in cmd_keys:
            return False
        
        if (key == pl.K_KP_ENTER or key == pl.K_RETURN) and self.surface.get_height() + self.font_object.get_height() > self.rect.height - (self.border_width*2):
            return False
        
        return True
    
    def fits_in_line(self, line_index: int, text: str):
        return self.get_line_width(line_index, text) + self.padding[0] + self.border_width < self.rect.width - self.padding[0] - self.border_width
        
    def get_line_width(self, index, new_text = ""):
        _text = ''.join(self.buffer[index].left + self.buffer[index].right)
        rendered_surface = self.font_object.render(_text + new_text + " ", self.antialias, self.font_color)
        return rendered_surface.get_width()

    def update_focus(self):
        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0] == 1
        
        hovered = self.rect.collidepoint(mouse_pos)
        self.focused = hovered and clicked
    
    def update(self, events):
        """
        Update the interal state with fresh pygame events.
        Call this every frame with all events returned by `pygame.event.get()`.
        """
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.update_focus()
        
        if not self.focused:
            self.selection_range = None
            self._rerender()
            return
        
        if self.readonly:
            return
        
        value_before = self.value
        
        for event in events:
            if event.type == pl.KEYDOWN:
                v_before = self.buffer[self.y_cursor].left + self.buffer[self.y_cursor].right
                c_before = self.cursor_pos
                if self.validator(self, event.key) and self.in_bounds(event.key):
                    self._process_keydown(event)
                else:
                    self.buffer[self.y_cursor].left = v_before
                    self.buffer[self.y_cursor].right = ""
                    self.cursor_pos = c_before
        
        if self.value != value_before:
            self._require_rerender()
                    
        # Update cursor visibility after self._blink_interval milliseconds
        self._clock.tick()
        self._last_blink_toggle += self._clock.get_time()
        if self._last_blink_toggle > self._cursor_blink_interval:
            self._last_blink_toggle %= self._cursor_blink_interval
            self._cursor_visible = not self._cursor_visible

            self._require_rerender()

        # Make cursor visible when something is pressed
        if [event for event in events if event.type == pl.KEYDOWN]:
            self._last_blink_toggle = 0
            self._cursor_visible = True
            self._require_rerender()
        
    def _require_rerender(self):
        """
        Trigger a re-render of the surface the next time the surface is accessed.
        """
        self._rerender_required = True

    def _rerender(self):
        """ Rerender self._surface."""
        # Final surface is slightly larger than font_render itself, to accomodate for cursor
        _max_line_len = max([len(line.left + line.right) for line in self.buffer])
        _max_line_text = [line.left + line.right for line in self.buffer if len(line.left + line.right) == _max_line_len][0]
        
        max_line_surface = self.font_object.render(_max_line_text + " ",
                                                    self.antialias,
                                                    self.font_color)
        
        
        _size = max_line_surface.get_size()
        self._surface = pygame.Surface((_size[0] + self.cursor_width, _size[1] * len(self.buffer)), pygame.SRCALPHA, 32)
        self._surface = self._surface.convert_alpha()
        
        for i, line in enumerate(self.buffer):
            _text = ''.join(line.left + line.right)
            
            txt_sur = self.font_object.render(_text + " ", self.antialias, self.font_color)
            txt_sur.convert_alpha()
            rendered_surface = pygame.Surface(txt_sur.get_size(), pygame.SRCALPHA, 32)
            rendered_surface.convert_alpha()
            rendered_surface.blit(txt_sur, (0,0))
            
            if self.selection_range != None:
                pygame.draw.rect(self._surface, self.selection_color, ((0, rendered_surface.get_height() * i), rendered_surface.get_size()))
            self._surface.blit(rendered_surface, (0, rendered_surface.get_height() * i))

        if len(self.buffer) == 1 and len(self.buffer[0].left + self.buffer[0].right) == 0:
            _placeholder_size = self.font_object.render(self.place_holder,self.antialias,self.font_color).get_size()
            self._surface = pygame.Surface((_placeholder_size[0] + self.cursor_width, _placeholder_size[1]), pygame.SRCALPHA, 32)
            self._surface = self._surface.convert_alpha()
            rendered_surface = self.font_object.render(self.place_holder, self.antialias, self.place_holder_color, self.background_color)
            self._surface.blit(rendered_surface, (0, rendered_surface.get_height() * i))
            
            
        if self._cursor_visible and self.focused:
            str_left_of_cursor = self.value[:self.cursor_pos[0]]
            cursor_x = self.font_object.size(str_left_of_cursor)[0]
            cursor_rect = pygame.Rect(cursor_x, self.y_cursor * max_line_surface.get_height(), self._cursor_width, self.font_object.get_height())
            self._surface.fill(self._cursor_color, cursor_rect)

    def get_value(self):
        return '\n'.join([line.left + line.right for line in self.buffer])

    def _process_keydown(self, ev):
        key_name = pygame.key.name(ev.key)
        if key_name == "tab":
            self.tab_callback()
            return
        
        attrname = f"_process_{key_name}"
        if hasattr(self, attrname):
            getattr(self, attrname)()
        else:
            self._process_other(ev)

    def _process_delete(self):#ok
        if self.selection_range != None:
            self.clear()
            return
        
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            if len(self.buffer) == 1:
                self.clear()
                return
            
            self.buffer.remove(self.buffer[self.y_cursor])
            self._process_end()
            return
        elif pygame.key.get_mods() & pygame.KMOD_CTRL:
            words = self.buffer[self.y_cursor].right.split(' ')[1:]
            self.buffer[self.y_cursor].right = ' '.join(words)
            return
        
        if len(self.buffer[self.y_cursor].left + self.buffer[self.y_cursor].right) == 0:
            if(len(self.buffer)> 1):
                self.buffer.remove(self.buffer[self.y_cursor])
                            
            if len(self.buffer)-1 >= self.y_cursor:
                self.cursor_pos = (0, self.y_cursor)
            else:
                self.y_cursor = 0
                self.cursor_pos = (0, self.y_cursor)
        else:
            self.buffer[self.y_cursor].right = self.buffer[self.y_cursor].right[1:]
        
    def _process_backspace(self):#ok
        if self.selection_range != None:
            self.clear()
            return
        
        if self.cursor_pos[0] > 0:
            _text_left = self.buffer[self.y_cursor].left
            if pygame.key.get_mods() & pygame.KMOD_CTRL:
                words = _text_left.split(' ')[:-1]
                self.buffer[self.y_cursor].left = ' '.join(words)
            else:
                self.buffer[self.y_cursor].left = _text_left[:-1]
        else:
            if len(self.buffer)-1 >= self.y_cursor:
                _right = self.buffer[self.y_cursor].right
                if len(_right) > 0:
                    self.buffer[self.y_cursor-1].right = _right
                if len(self.buffer) > 1:
                    self.buffer.remove(self.buffer[self.y_cursor])
                    self.y_cursor-=1
                    self.cursor_pos = (len(self.buffer[self.y_cursor].left + self.buffer[self.y_cursor].right), self.y_cursor)
                
    
    def _process_right(self):#ok
        if pygame.key.get_mods() & pygame.KMOD_CTRL:
            words = self.buffer[self.y_cursor].right.strip().split(' ')
            self.cursor_pos = (self.cursor_pos[0] + len(words[0]) +1, self.cursor_pos[1])
            return
        self.cursor_pos = (self.cursor_pos[0] + 1, self.cursor_pos[1])
    
    def _process_left(self):#ok
        if pygame.key.get_mods() & pygame.KMOD_CTRL:
            words = self.buffer[self.y_cursor].left.strip().split(' ')
            self.cursor_pos = (max([self.cursor_pos[0] - len(words[-1]) -1,0]), self.cursor_pos[1])
            return
        
        
        if self.cursor_pos[0] > 0:
            self.cursor_pos = (self.cursor_pos[0] - 1, self.cursor_pos[1])

    def _process_end(self):#ok
        self.cursor_pos = (len(self.buffer[-1].left + self.buffer[-1].right), len(self.buffer)-1)
    
    def _process_home(self):#ok
        self.cursor_pos = (0,0)
        
    def _process_up(self):
        if self.y_cursor > 0:
            if pygame.key.get_mods() & pygame.KMOD_ALT:
                self.invert_lines(self.buffer[self.y_cursor], self.buffer[self.y_cursor-1])
            
            self.cursor_pos = (self.cursor_pos[0], self.cursor_pos[1]-1)
            
    
    def _process_down(self):
        if self.y_cursor < len(self.buffer)-1:
            if pygame.key.get_mods() & pygame.KMOD_ALT:
                self.invert_lines(self.buffer[self.y_cursor], self.buffer[self.y_cursor+1])
            
            self.cursor_pos = (self.cursor_pos[0], self.cursor_pos[1]+1)
    
    def _process_return(self):
        self.enter()
    
    def _process_enter(self):
        self.enter()
        
    def _process_tab(self):
        _spaces = ' ' * 4
        if self.fits_in_line(self.y_cursor, _spaces):
            self.buffer[self.y_cursor].left += _spaces
        
    def _process_point(self):
        self.buffer[self.y_cursor].left += '.'
        
    def _process_escape(self):
        self.selection_range = None

    def _process_other(self, event):#ok
        match event.key:
            case pl.K_PERIOD | pl.K_KP_PERIOD:
                self._process_point()
                return
        
        if pygame.key.get_mods() & pygame.KMOD_CTRL:
            match event.key:
                case pl.K_a:
                    self.select_all()
                    return
                case pl.K_c:
                    self.copy_text()
                    return
                case pl.K_v:
                    self.paste()
                    return
                case pl.K_x:
                    self.copy_text()
                    self.clear()
                    return
                case _:
                    return
        
        if self.selection_range != None:
            self.clear()
        
        self.buffer[self.y_cursor].left += event.unicode
        
    def enter(self):
        if self.selection_range != None:
            self.clear()
            return
        _right = ""
        _right = self.buffer[self.y_cursor].right
        if len(_right) > 0:
            self.buffer[self.y_cursor].right = ""
            
        self.buffer.insert(self.y_cursor+1, TxtLine())
        self.y_cursor += 1
        self.buffer[self.y_cursor].right = _right
        self.cursor_pos = (0, self.y_cursor)
        
    def select_all(self):
        self._process_end()
        self.selection_range = ((0,0),self.cursor_pos)
    
    def clear(self):
        self.buffer = [TxtLine()]
        self.cursor_pos = (0,0)
        self.selection_range = None
        
    def copy_text(self):
        if self.selection_range == None:
            return
        _all_text = '\n'.join([line.left + line.right for line in self.buffer])
        pyperclip.copy(_all_text)
    
    def paste(self):
        txt_arr = pyperclip.paste().replace('\r', '').replace('\t', ' ' * 4).split('\n')
        for i in range(0, len(txt_arr)):
            self.buffer[self.y_cursor].left += txt_arr[i]
            if i < len(txt_arr)-1:
                self.enter()
    
    def invert_lines(self, ln1, ln2):
        _l1 = ln1.left
        _r1 = ln1.right
        _l2 = ln2.left
        _r2 = ln2.right
        
        ln1.left = _l2
        ln1.right = _r2
        ln2.left = _l1
        ln2.right = _r1
        
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(screen, self.background_color, pygame.Rect(self.rect.topleft, self.rect.size))
        pygame.draw.rect(screen, self.border_color, pygame.Rect(self.rect.topleft, self.rect.size), self.border_width)
        screen.blit(self.surface, self.rect.topleft + vec(self.padding))
        
    def from_this_template(self, rect: pygame.Rect, **new_kwargs):
        merged_kwargs = self.start_kwargs.copy()
        for item in new_kwargs.items():
            merged_kwargs[item[0]] = item[1]
        
        return TextInput(rect, **merged_kwargs)
        