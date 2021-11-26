import curses
from time import sleep

class CursesWrapper:
    def __init__(self):
        screen = curses.initscr()
        curses.start_color()
        screen.keypad(1)
        screen.erase()
        curses.init_pair(1, curses.COLOR_GREEN, screen.getbkgd())
        curses.init_pair(2, curses.COLOR_RED, screen.getbkgd())
        curses.init_pair(3, curses.COLOR_YELLOW, screen.getbkgd())
        curses.init_pair(4, curses.COLOR_CYAN, screen.getbkgd())
        max_window_height, max_window_width = screen.getmaxyx()
        screen.resize(max_window_height - 5, max_window_width)
        self.main_window = screen
        self.main_window.nodelay(True)
        self.draw_window_borders(self.main_window, 'Main')
        self.messages_window = curses.newwin(5, max_window_width, max_window_height - 5, 0)
        self.messages_window.nodelay(True)
        self.draw_window_borders(self.messages_window, 'Messages')
        self.dimension = [max_window_height, max_window_width]

    def draw_window_borders(self, window, title):
        window.clear()
        window.border()
        window.move(0, 1)
        window.addstr(title, curses.A_BOLD)


    def print(self, texts, color_pair, window=None):
        messages = window == None or window == self.messages_window
        main = window == self.main_window
        x = 1
        y = 1
        window = self.messages_window if messages else window
        max_allowed_lines = window.getmaxyx()[0] - y
        current_line = window.getyx()[0] + 1 if window.getyx()[1] > 0 else 0 + y
        line = y if window.getyx() == [0, 0] or window.getyx()[0] == max_allowed_lines else current_line
        for text in texts:
            window.move(line, x)
            window.addstr(self.display_string(window.getmaxyx()[1] - (y * 2), text), color_pair)
            window.refresh()
            if messages: sleep(1)
            line += 1
            if line >= max_allowed_lines:
                line = y
                window.erase()
                if messages:
                    self.draw_window_borders(window, 'Messages')
                elif main:
                    self.draw_window_borders(window, 'Main')

    def print_good(self, texts, window=None):
        self.print(texts, curses.color_pair(1), window)

    def print_error(self, texts, window=None):
        self.print(texts, curses.color_pair(2), window)

    def print_warning(self, texts, window=None):
        self.print(texts, curses.color_pair(3), window)

    def print_info(self, texts, window=None):
        self.print(texts, curses.color_pair(4), window)

    def display_string(self, window_width, target_line):
        return target_line if window_width >= len(target_line) else target_line[:window_width]
