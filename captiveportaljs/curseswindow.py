import curses
import threading

class GetOutOfLoop(Exception):
    pass

class CursesWindow:
    def __init__(self, height, width, x, y, title):
        # type: (int, int, int, int, str) -> None
        self.title = title
        self.help_shown = False
        self.window = curses.newwin(height, width, y, x)
        self.window.nodelay(True)
        self.window.notimeout(True)
        self.window.immedok(True)
        self.window.keypad(True)
        self.log = []
        self.messages_log = []
        self.devices_log = []
        self.scroll_enabled = True
        self.focused = True
        self.top = 0
        self.cursor = 0
        self.draw_window_borders()

    def set_title(self, title):
        # type: (str) -> None
        self.title = title

    def set_focused(self, focused):
        # type: (bool) -> None
        self.focused = focused
        self.display()

    def resize_window(self, height, width, x, y):
        # type: (int, int, int, int) -> None
        try:
            self.window.mvwin(y, x)
        except:
            pass
        self.window.resize(height, width)
        self.window.redrawwin()
        self.window.refresh()
        self.handle_key(ord('E'))
        self.display()

    def draw_window_borders(self):
        if self.help_shown: return
        self.window.clear()
        self.window.border()
        self.window.move(0, 1)
        self.window.move(0, int(self.window.getmaxyx()[1] / 2) - int(len(' {} '.format(self.title)) / 2))
        self.window.addstr(' {} '.format(self.title), curses.A_BOLD if self.focused else curses.A_NORMAL)
        self.window.refresh()

    def display(self):
        if self.help_shown: return
        self.draw_window_borders()
        max_height = self.window.getmaxyx()[0] - 2
        max_width = self.window.getmaxyx()[1] - 2
        log_entries = self.log[self.top:self.top + max_height]
        for idx, item in enumerate(log_entries):
            text, color_pair = item
            if idx + 1 == self.cursor and self.focused:
                self.print_to_window(text.ljust(max_width), curses.color_pair(5), idx + 1)
            else:
                self.print_to_window(text, color_pair, idx + 1)

    def print_to_window(self, text, color_pair, line):
        # type: (str, int, int) -> None
        self.window.move(line, 1)
        self.window.addstr(self.display_string(self.window.getmaxyx()[1] - 2, text), color_pair)
        self.window.refresh()

    def print_raw(self, texts, color_pair):
        # type: (list[str], int) -> None
        max_lines = self.window.getmaxyx()[0] - 2
        for text in texts:
            self.log.append([text, color_pair])
            if self.scroll_enabled:
                if self.cursor < max_lines:
                    self.cursor += 1
                if len(self.log) > max_lines:
                    self.top += 1
            self.display()

    def print_good(self, texts):
        # type: (list[str]) -> None
        self.print_raw(texts, curses.color_pair(1))

    def print_error(self, texts):
        # type: (list[str]) -> None
        self.print_raw(texts, curses.color_pair(2))

    def print_warning(self, texts):
        # type: (list[str]) -> None
        self.print_raw(texts, curses.color_pair(3))

    def print_info(self, texts):
        # type: (list[str]) -> None
        self.print_raw(texts, curses.color_pair(4))

    def display_string(self, window_width, target_line):
        # type: (int, str) -> str
        return target_line if window_width >= len(target_line) else target_line[:window_width]

    def show_help(self):
        self.help_shown = True
        self.window.clear()
        self.window.border()
        self.window.move(0, int(self.window.getmaxyx()[1] / 2) - int(len(' Help ') / 2))
        self.window.addstr(' Help ', curses.A_BOLD)
        while True:
            self.window.move(1, 1)
            self.window.addstr('Cursor: {}'.format(self.cursor), curses.A_BOLD)
            key = self.window.getch()
            if key == ord('q') or key == ord('?') or key == 27: break
        self.help_shown = False
        self.window.refresh()

    def handle_key(self, key):
        # type: (int) -> None
        if key == -1: return
        max_lines = self.window.getmaxyx()[0] - 2
        if key == ord('?'):
            threading.Thread(target=self.show_help).start()
        if key == ord('q'):
            raise GetOutOfLoop
        if key == curses.KEY_UP or key == ord('k'):
            if self.top > 0 and self.cursor == 1: self.top -= 1
            elif self.top > 0 or self.cursor > 1: self.cursor -= 1
            self.scroll_enabled = False
        if key == curses.KEY_DOWN or key == curses.ACS_DARROW or key == ord('j'):
            next_line = self.cursor + 1
            if next_line == max_lines:
                if self.top + max_lines < len(self.log):
                    self.top += 1
                else:
                    self.cursor = next_line
            elif next_line < max_lines:
                if self.top + next_line < max_lines and len(self.log) > max_lines:
                    self.cursor = next_line
            if self.cursor > max_lines or self.cursor > len(self.log) - 3:
                self.curor = min(len(self.log) - 3, max_lines)
            if self.cursor == max_lines: self.scroll_enabled = True
        if key == curses.KEY_NPAGE or key == ord('K'):
            if self.cursor == 1:
                self.top = max(0, self.top - max_lines)
            self.cursor = 1
            self.scroll_enabled = False
        if key == curses.KEY_PPAGE or key == ord('J'):
            if self.cursor == max_lines:
                self.top += max_lines
                if  len(self.log) - self.top == 0:
                    self.top -= max_lines
                elif len(self.log) - self.top > 0:
                    self.top -= max_lines - ( len(self.log) - self.top )
            self.cursor = min(len(self.log), min(len(self.log) + 1, max_lines))
            if len(self.log) - self.top <= max_lines: self.scroll_enabled = True
        if key == curses.KEY_HOME or key == ord('H'):
            self.cursor = 1
            self.top = 0
            self.scroll_enabled = False
        if key == curses.KEY_END or key == ord('E'):
            self.cursor = min(len(self.log), max_lines)
            self.top = max(0, min(len(self.log) - max_lines, len(self.log)))
            self.scroll_enabled = True
        if key == curses.KEY_DC or key == ord('C'):
            self.log = []
            self.cursor = self. top = 0
            # self.top = 0
            self.scroll_enabled = True
        self.display()
