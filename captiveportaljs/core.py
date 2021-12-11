import threading
import blinker
import urwid
import asyncio
from captiveportaljs.network import Network
from captiveportaljs.window import Window
from captiveportaljs.statusbar import StatusBar

class Core:
    PALETTE = [
        ('header', 'bold', ''),
        ('item_hover', 'black', 'white'),
        ('statusbar', 'black', 'white'),
        ('info', 'light cyan', ''),
        ('good', 'light green', ''),
        ('warning', 'yellow', ''),
        ('error', 'light red', ''),
    ]
    CTX = blinker.Signal() # type: blinker.Signal
    CONTEXTS = {
        'devices': blinker.Signal(), # type: blinker.Signal
        'wireless': blinker.Signal(), # type: blinker.Signal
        'messages': blinker.Signal(), # type: blinker.Signal
        'logs': blinker.Signal(), # type: blinker.Signal
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
    stop = False

    @staticmethod
    def start():
        devices = Window([], [])
        Core.set_window('devices', devices, 'Devices on network (0)')
        wireless = Window([], [])
        Core.set_window('wireless', wireless, 'Wireless Access Points/Stations (0/0)')
        messages = Window([], [])
        Core.set_window('messages', messages, 'Messages')
        Core.get_context('messages').connect(messages.entry, 'info')
        Core.get_context('messages').connect(messages.entry, 'good')
        Core.get_context('messages').connect(messages.entry, 'warning')
        Core.get_context('messages').connect(messages.entry, 'error')
        logs = Window([], [])
        Core.set_window('logs', logs, 'Logs')
        Core.get_context('logs').connect(logs.entry, 'info')
        Core.get_context('logs').connect(logs.entry, 'good')
        Core.get_context('logs').connect(logs.entry, 'warning')
        Core.get_context('logs').connect(logs.entry, 'error')
        main = Window(['Header'], [])
        Core.set_window('main', main, 'Main')
        statusbar = StatusBar()
        active_networking_interface = Network.get_active_interface()
        networking_scanner = None # type: threading.Thread | None
        if active_networking_interface:
            Core.activate_scanner('network', blinker.signal('network'))
            devices.message_info(['Enabling IP forwarding...'])
            Network.enable_ip_forwarding()
            devices.message_good(['Enabled'])
            devices.message_info(['Starting networking scanner thread...'])
            networking_scanner = threading.Thread(target=Network.scanner_thread, args=(devices, active_networking_interface, lambda: Core.stop))
            networking_scanner.start()
            devices.message_good(['Started'])
        linebox = urwid.LineBox(urwid.Frame(main, header=urwid.Pile(main.headers), footer=statusbar), 'Main')
        loop = asyncio.get_event_loop()
        Core.loop = urwid.MainLoop(linebox, event_loop=urwid.AsyncioEventLoop(loop=loop), unhandled_input=Core.keypress, palette=Core.PALETTE)
        Core.loop.run()
        if networking_scanner and Core.SCANNERS['network']:
            networking_scanner.join()

    @staticmethod
    def keypress(key):
        if key == 'Q':
            asyncio.get_running_loop().create_task(Core.exit_from_core())
        if key == 'q':
            asyncio.get_running_loop().create_task(Core.exit_from_core())
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
        if key in list(Core.CONTEXTS):
            return
        Core.CONTEXTS[key] = ctx

    @staticmethod
    def get_context(key):
        # type: (str) -> blinker.Signal
        if not key in list(Core.CONTEXTS):
            ctx = blinker.Signal()
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
        # type: (str) -> None | Window
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
                linebox = Core.loop.widget # type: urwid.Frame
                linebox.set_title(Core.get_window_title(key))
                frame = linebox.original_widget # type: urwid.Frame
                frame.body = window
                frame.header = urwid.Pile(window.headers)

    @staticmethod
    def nop(): pass

    @staticmethod
    async def exit_from_core():
        Core.stop = True
        for scanner in list(Core.SCANNERS):
            if Core.SCANNERS[scanner]:
                window = Core.get_window('messages')
                if scanner == 'network':
                    if window:
                        window.entry_info(['Disabling IP forwarding...'])
                        Network.disable_ip_forwarding()
                        window.entry_good(['Disabled'])
                if window:
                    window.entry_info(['Stopping {} scanner...'.format(scanner)])
                    if Core.loop:
                        Core.loop.set_alarm_in(0.01, window.refresh)
                while Core.SCANNERS[scanner]:
                    await asyncio.sleep(0.5)
                if window:
                    window.entry_good(['Stopped'])
                    if Core.loop:
                        Core.loop.set_alarm_in(0.01, window.refresh)
        raise urwid.ExitMainLoop
