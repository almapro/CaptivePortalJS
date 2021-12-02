import curses, curses.panel
import threading

class GetOutOfLoop(Exception):
    def __init__(self, message):
        self.message = message
        pass

class CursesWindow:
    def __init__(self, window, panel, title, maximized_window, maximized_panel):
        # type: (curses._CursesWindow, curses.panel._Curses_Panel, str, curses._CursesWindow, curses.panel._Curses_Panel) -> None
        self.title = title
        self.help_shown = False
        self.window = window
        self.maximized_window = maximized_window
        self.maximized_panel = maximized_panel
        self.panel = panel
        self.focused = True
        self.entries = []
        self.top = 0
        self.cursor = 0
        self.scroll_enabled = True
        self.log = []
        self.log_top = 0
        self.log_cursor = 0
        self.log_scroll_enabled = True
        self.log_shown = False
        self.maximized = False
        self.draw_window_borders()

    def set_title(self, title):
        # type: (str) -> None
        self.title = title
        self.display()

    def set_focused(self, focused):
        # type: (bool) -> None
        self.focused = focused
        self.display()

    def set_log_shown(self, log_shown):
        self.log_shown = log_shown
        self.display()

    def set_maximized(self, maximized):
        self.maximized = maximized
        if maximized:
            self.panel.bottom()
        else:
            self.panel.top()

    def clear_entries(self):
        self.top = 0
        self.cursor = 0
        self.scroll_enabled = True
        self.entries.clear()
        self.display()

    def clear_log(self):
        self.log_top = 0
        self.log_cursor = 0
        self.log_scroll_enabled = True
        self.log.clear()
        self.display()

    def resize_window(self, height, width):
        # type: (int, int) -> None
        self.window.resize(height, width)
        self.window.redrawwin()
        self.window.refresh()
        self.handle_key(ord('E'))
        self.display()

    def draw_window_borders(self):
        if self.help_shown: return
        window = self.maximized_window if self.maximized else self.window
        window.clear()
        window.box()
        title = ' LOG ({}) '.format(len(self.log)) if self.log_shown else ' {} '.format(self.title)
        window.move(0, int(window.getmaxyx()[1] / 2) - int(len(title) / 2))
        window.addstr(title, curses.A_BOLD if self.focused else curses.A_NORMAL)
        window.refresh()

    def display(self):
        if curses.panel.top_panel() == self.maximized_panel and not self.focused: return
        if self.log_shown:
            self.display_log()
        else:
            self.display_entries()

    def display_log(self):
        if self.help_shown: return
        if not self.log_shown: return
        self.draw_window_borders()
        window = self.maximized_window if self.maximized else self.window
        max_height = window.getmaxyx()[0] - 2
        max_width = window.getmaxyx()[1] - 2
        log = self.log[self.log_top:self.log_top + max_height]
        for idx, item in enumerate(log):
            text, color_pair = item
            if idx + 1 == self.log_cursor and self.focused:
                self.print_to_window(text.ljust(max_width), curses.color_pair(5), idx + 1)
            else:
                self.print_to_window(text, color_pair, idx + 1)

    def display_entries(self):
        if self.help_shown: return
        if self.log_shown: return
        self.draw_window_borders()
        window = self.maximized_window if self.maximized else self.window
        max_height = window.getmaxyx()[0] - 2
        max_width = window.getmaxyx()[1] - 2
        entries = self.entries[self.top:self.top + max_height]
        for idx, item in enumerate(entries):
            text, color_pair = item
            if idx + 1 == self.cursor and self.focused:
                self.print_to_window(text.ljust(max_width), curses.color_pair(5), idx + 1)
            else:
                self.print_to_window(text, color_pair, idx + 1)

    def print_to_window(self, text, color_pair, line):
        # type: (str, int, int) -> None
        window = self.maximized_window if self.maximized else self.window
        window.move(line, 1)
        window.addstr(self.display_string(window.getmaxyx()[1] - 2, text), color_pair)
        window.refresh()

    def print_raw(self, texts, color_pair):
        # type: (list[str], int) -> None
        window = self.maximized_window if self.maximized else self.window
        max_lines = window.getmaxyx()[0] - 2
        for text in texts:
            self.entries.append([text, color_pair])
            if self.scroll_enabled:
                if self.cursor < max_lines:
                    self.cursor += 1
                if len(self.entries) > max_lines:
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

    def log_raw(self, texts, color_pair):
        # type: (list[str], int) -> None
        window = self.maximized_window if self.maximized else self.window
        max_lines = window.getmaxyx()[0] - 2
        for text in texts:
            self.log.append([text, color_pair])
            if self.log_scroll_enabled:
                if self.log_cursor < max_lines:
                    self.log_cursor += 1
                if len(self.log) > max_lines:
                    self.log_top += 1
            self.display()

    def log_good(self, texts):
        # type: (list[str]) -> None
        self.log_raw(texts, curses.color_pair(1))

    def log_error(self, texts):
        # type: (list[str]) -> None
        self.log_raw(texts, curses.color_pair(2))

    def log_warning(self, texts):
        # type: (list[str]) -> None
        self.log_raw(texts, curses.color_pair(3))

    def log_info(self, texts):
        # type: (list[str]) -> None
        self.log_raw(texts, curses.color_pair(4))

    def show_help(self):
        self.help_shown = True
        window = self.maximized_window if self.maximized else self.window
        window.clear()
        window.border()
        window.move(0, int(window.getmaxyx()[1] / 2) - int(len(' Help ') / 2))
        window.addstr(' Help ', curses.A_BOLD)
        while True:
            window.move(1, 1)
            window.addstr('Entries: {} Log: {}'.format(len(self.entries), len(self.log)), curses.A_BOLD)
            key = window.getch()
            if key == ord('q') or key == ord('?') or key == 27: break
        self.help_shown = False
        self.display()

    def handle_key(self, key):
        # type: (int) -> None
        if key == -1: return
        window = self.maximized_window if self.maximized else self.window
        max_lines = window.getmaxyx()[0] - 2
        if key == ord('?'):
            threading.Thread(target=self.show_help).start()
        if key == ord('q'):
            if self.log_shown:
                self.set_log_shown(False)
            else:
                raise GetOutOfLoop('')
        if key == curses.KEY_UP or key == ord('k'):
            if self.log_shown:
                if self.log_top > 0 and self.log_cursor == 1: self.log_top -= 1
                elif self.log_top > 0 or self.log_cursor > 1: self.log_cursor -= 1
                self.log_scroll_enabled = False
            else:
                if self.top > 0 and self.cursor == 1: self.top -= 1
                elif self.top > 0 or self.cursor > 1: self.cursor -= 1
                self.scroll_enabled = False
        if key == curses.KEY_DOWN or key == curses.ACS_DARROW or key == ord('j'):
            if self.log_shown:
                next_line = self.log_cursor + 1
                if next_line > max_lines:
                    if self.log_top + max_lines < len(self.log):
                        self.log_top += 1
                elif next_line <= max_lines:
                    self.log_cursor = next_line
                if self.log_cursor > max_lines:
                    self.log_cursor = min(len(self.log), max_lines)
                if self.log_cursor == max_lines and self.log_top + max_lines == len(self.log): self.log_scroll_enabled = True
            else:
                next_line = self.cursor + 1
                if next_line > max_lines:
                    if self.top + max_lines < len(self.entries):
                        self.top += 1
                elif next_line <= max_lines:
                    self.cursor = next_line
                if self.cursor > max_lines:
                    self.cursor = min(len(self.entries), max_lines)
                if self.cursor == max_lines and self.top + max_lines == len(self.entries): self.scroll_enabled = True
        if key == curses.KEY_NPAGE or key == ord('K'):
            if self.log_shown:
                if self.log_cursor == 1:
                    self.log_top = max(0, self.log_top - max_lines)
                self.log_cursor = 1
                self.log_scroll_enabled = False
            else:
                if self.cursor == 1:
                    self.top = max(0, self.top - max_lines)
                self.cursor = 1
                self.scroll_enabled = False
        if key == curses.KEY_PPAGE or key == ord('J'):
            if self.log_shown:
                if self.log_cursor == max_lines:
                    self.log_top += max_lines
                    if  len(self.log) - self.log_top == 0:
                        self.log_top -= max_lines
                    elif len(self.log) - self.log_top > 0:
                        self.log_top -= max_lines - ( len(self.log) - self.log_top )
                self.log_cursor = min(len(self.log), min(len(self.log) + 1, max_lines))
                if len(self.log) - self.log_top <= max_lines: self.log_scroll_enabled = True
            else:
                if self.cursor == max_lines:
                    self.top += max_lines
                    if  len(self.entries) - self.top == 0:
                        self.top -= max_lines
                    elif len(self.entries) - self.top > 0:
                        self.top -= max_lines - ( len(self.entries) - self.top )
                self.cursor = min(len(self.entries), min(len(self.entries) + 1, max_lines))
                if len(self.entries) - self.top <= max_lines: self.scroll_enabled = True
        if key == curses.KEY_HOME or key == ord('H'):
            if self.log_shown:
                self.log_cursor = 1
                self.log_top = 0
                self.log_scroll_enabled = False
            else:
                self.cursor = 1
                self.top = 0
                self.scroll_enabled = False
        if key == curses.KEY_END or key == ord('E'):
            if self.log_shown:
                self.log_cursor = min(len(self.log), max_lines)
                self.log_top = max(0, min(len(self.log) - max_lines, len(self.log)))
                self.log_scroll_enabled = True
            else:
                self.cursor = min(len(self.entries), max_lines)
                self.top = max(0, min(len(self.entries) - max_lines, len(self.entries)))
                self.scroll_enabled = True
        if key == curses.KEY_DC or key == ord('C'):
            if self.log_shown:
                self.log = []
                self.log_cursor = self.log_top = 0
                self.log_scroll_enabled = True
            else:
                self.entries = []
                self.cursor = self.top = 0
                self.scroll_enabled = True
        if key == ord('L'):
            if self.log_shown:
                self.set_log_shown(False)
            else:
                self.set_log_shown(True)
        self.display()
