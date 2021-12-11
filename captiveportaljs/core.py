import blinker
import urwid
from time import sleep
from captiveportaljs.window import Window
from captiveportaljs.statusbar import StatusBar

class Core:
    PALETTE = [
        ('header', 'bold', ''),
        ('item_hover', 'black', 'white'),
        ('statusbar', 'black', 'white'),
    ]
    CTX = blinker.signal('Core') # type: blinker.Signal
    CONTEXTS = {
        'messages': blinker.signal('messages'), # type: blinker.Signal
    }
    SCANNERS = {
        'network': False,
        'wireless': False,
    }
    WINDOWS = []
    ACTIVE_WINDOW = 'main'

    def __init__(self):
        raise Exception('Core class is static')

    loop = None # type: None | urwid.MainLoop

    @staticmethod
    def start():
        devices = Window([], [])
        Core.set_window('devices', devices, 'Devices on network (0)')
        wireless = Window([], [])
        Core.set_window('wireless', wireless, 'Wireless Access Points/Stations (0/0)')
        messages = Window([], [])
        Core.set_window('messages', messages, 'Messages')
        logs = Window([], [])
        Core.set_window('logs', logs, 'Logs')
        main = Window(['Header'], [])
        Core.set_window('main', main, 'Main')
        statusbar = StatusBar()
        linebox = urwid.LineBox(urwid.Frame(main, header=urwid.Pile(main.headers), footer=statusbar), 'Main')
        Core.loop = urwid.MainLoop(linebox, unhandled_input=Core.keypress, palette=Core.PALETTE)
        Core.loop.run()

    @staticmethod
    def keypress(key):
        if key == 'Q':
            Core.CTX.send('exit')
        if key == 'q':
            Core.CTX.send('exit')
        if key == 'm':
            Core.set_active_window('main')
        if key == 'd':
            Core.set_active_window('devices')
        if key == 'w':
            Core.set_active_window('wireless')
        if key == 'M':
            Core.set_active_window('messages')
        if key == 'l':
            Core.set_active_window('logs')
        if key == 'tab':
            window_to_activate = 'main'
            for idx, window in enumerate(Core.WINDOWS):
                if window[0] == Core.ACTIVE_WINDOW:
                    if len(Core.WINDOWS) - 1 == idx:
                        window_to_activate = Core.WINDOWS[0][0]
                    else:
                        window_to_activate = Core.WINDOWS[idx + 1][0]
            Core.set_active_window(window_to_activate)

    @staticmethod
    def set_context(key, ctx):
        # type: (str, blinker.Signal) -> None
        if Core.get_context(key):
            return
        Core.CONTEXTS[key] = ctx

    @staticmethod
    def get_context(key):
        if not key in list(Core.CONTEXTS):
            ctx = blinker.signal(key)
            Core.set_context(key, ctx)
        return Core.CONTEXTS[key]

    @staticmethod
    def activate_scanner(scanner, ctx):
        if scanner in list(Core.SCANNERS):
            Core.SCANNERS[scanner] = True
            Core.set_context(scanner, ctx)

    @staticmethod
    def set_window(key, window, title):
        # type: (str, Window, str) -> None
        if Core.get_window(key):
            return
        Core.WINDOWS.append([key, window, title])

    @staticmethod
    def set_window_title(key, title):
        # type: (str, str) -> None
        for idx, window in enumerate(Core.WINDOWS):
            if window[0] == key:
                Core.WINDOWS[idx][3] = title
                if Core.ACTIVE_WINDOW == key:
                    Core.set_active_window(key)

    @staticmethod
    def get_window(key):
        for window in Core.WINDOWS:
            if window[0] == key:
                return window[1]
        return None

    @staticmethod
    def get_window_title(key):
        for window in Core.WINDOWS:
            if window[0] == key:
                return window[2]
        return ''

    @staticmethod
    def set_active_window(key):
        if Core.loop:
            window = Core.get_window(key)
            if window:
                Core.ACTIVE_WINDOW = key
                linebox = Core.loop.widget # type: urwid.LineBox
                linebox.set_title(Core.get_window_title(key))
                frame = linebox.original_widget # type: urwid.Frame
                frame.body = window
                frame.header = urwid.Pile(window.headers)

@Core.CTX.connect
def exit_from_core(subject):
    if subject == 'exit':
        for scanner in Core.SCANNERS:
            if (Core.SCANNERS[scanner]):
                Core.get_context('messages').send(['info', 'Stopping {} scanner...'.format(scanner)])
                while (Core.SCANNERS[scanner]):
                    Core.get_context(scanner).send('stop')
                    sleep(0.5)
                Core.get_context('messages').get_context('messages').send(['good', 'Stopped'])
        raise urwid.ExitMainLoop
