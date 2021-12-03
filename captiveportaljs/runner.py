import os
import threading
import curses, curses.panel
from time import sleep
from captiveportaljs.curseswindow import CursesWindow, GetOutOfLoop
from captiveportaljs.networking import Networking
from captiveportaljs.utils import check_sudo_mode
from captiveportaljs.wireless import Wireless, WirelessInterface

def curses_wrapper(screen):
    # type: (curses._CursesWindow) -> curses._CursesWindow
    curses.init_pair(1, curses.COLOR_GREEN, screen.getbkgd()) # type: ignore
    curses.init_pair(2, curses.COLOR_RED, screen.getbkgd()) # type: ignore
    curses.init_pair(3, curses.COLOR_YELLOW, screen.getbkgd()) # type: ignore
    curses.init_pair(4, curses.COLOR_CYAN, screen.getbkgd()) # type: ignore
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.cbreak()
    curses.noecho()
    curses.curs_set(0)
    screen.keypad(True)
    screen.nodelay(True)
    return screen

def create_window_with_panel(height, width, x, y):
    window = curses.newwin(height, width, y, x)
    window.scrollok(True)
    window.nodelay(True)
    window.notimeout(True)
    window.immedok(True)
    window.keypad(True)
    panel = curses.panel.new_panel(window)
    return window, panel

def run():
    check_sudo_mode()
    screen = curses.wrapper(curses_wrapper)
    max_screen_height, max_screen_width = screen.getmaxyx()
    maximized_window, maximized_panel = create_window_with_panel(max_screen_height, max_screen_width, 0, 0)
    maximized_panel.bottom()
    curses.panel.update_panels()
    screen.refresh()
    main_window, main_panel = create_window_with_panel(max_screen_height - 5, int(max_screen_width / 2), 0, 0)
    main = CursesWindow(main_window, main_panel, 'Main', maximized_window, maximized_panel)
    devices_window, devices_panel = create_window_with_panel(max_screen_height - 5, int(max_screen_width / 2), int(max_screen_width / 2), 0)
    devices = CursesWindow(devices_window, devices_panel, 'Devices on network (0)', maximized_window, maximized_panel)
    messages_window, messages_panel = create_window_with_panel(5, max_screen_width, 0, max_screen_height - 5)
    messages = CursesWindow(messages_window, messages_panel, 'Messages', maximized_window, maximized_panel)
    messages.set_focused(False)
    devices.set_focused(False)
    stop = False
    maximized_view = False
    active_networking_interface = Networking.get_active_interface()
    wireless_interfaces = Wireless.get_interfaces()
    networking_scanner = None # type: threading.Thread | None
    wireless_scanner = None # type: threading.Thread | None
    if active_networking_interface:
        messages.print_info(['Enabling IP forwarding...'])
        Networking.enable_ip_forwarding()
        messages.print_good(['Enabled'])
        messages.print_info(['Starting networking scanner thread...'])
        networking_scanner = threading.Thread(target=Networking.scanner_thread, args=(devices, active_networking_interface, lambda: stop))
        networking_scanner.start()
        messages.print_good(['Started'])
        if active_networking_interface in wireless_interfaces:
            wireless_interfaces.remove(active_networking_interface)
    if len(wireless_interfaces) > 0:
        messages.print_info(['Starting wireless scanner thread...'])
        wireless_card = Wireless.get_interface_info(wireless_interfaces[0])
        wireless_interface = WirelessInterface(wireless_card)
        wireless_scanner = threading.Thread(target=Wireless.scanner_thread, args=(main, wireless_interface, lambda: stop))
        wireless_scanner.start()
        messages.print_good(['Started'])
    try:
        counter = 1
        while True:
            resized = curses.is_term_resized(max_screen_height, max_screen_width)
            if resized:
                max_screen_height, max_screen_width = screen.getmaxyx()
                curses.resize_term(max_screen_height, max_screen_width)
                main.resize_window(max_screen_height - 5, int(max_screen_width / 2))
                devices.resize_window(max_screen_height - 5, int(max_screen_width / 2))
                messages.resize_window(5 , max_screen_width)
                maximized_window.resize(max_screen_height, max_screen_width)
                screen.refresh()
            main.log_good(['Here {}'.format(counter)])
            counter += 1
            sleep(0.3)
            key = maximized_window.getch() if maximized_view else main.window.getch() if main.focused else messages.window.getch() if messages.focused else devices.window.getch()
            if key == ord('\t'):
                if main.focused and not main.maximized:
                    main.set_focused(False)
                    devices.set_focused(True)
                    main.display()
                elif devices.focused and not devices.maximized:
                    devices.set_focused(False)
                    messages.set_focused(True)
                    devices.display()
                elif messages.focused and not messages.maximized:
                    messages.set_focused(False)
                    main.set_focused(True)
                    messages.display()
            if key == ord('m'):
                if not maximized_view:
                    maximized_view = True
                    if main.focused: main.set_maximized(True)
                    if devices.focused: devices.set_maximized(True)
                    if messages.focused: messages.set_maximized(True)
                    maximized_panel.top()
                else:
                    maximized_view = False
                    if main.focused: main.set_maximized(False)
                    if devices.focused: devices.set_maximized(False)
                    if messages.focused: messages.set_maximized(False)
                    maximized_window.clear()
                    maximized_panel.bottom()
                curses.panel.update_panels()
                screen.refresh()
            if main.focused: main.handle_key(key)
            if devices.focused: devices.handle_key(key)
            if messages.focused: messages.handle_key(key)
    except GetOutOfLoop as r:
        if r.message != '':
            messages.print_error([r.message])
        messages.print_error(['Pressed exit key (q)', 'Exiting...'])
    except KeyboardInterrupt:
        messages.print_error(['(^C) interrupted'])
    except EOFError:
        messages.print_error(['(^D) interrupted'])
    except Exception as e:
        messages.print_error(['Unhandled error: {}'.format(str(e)), 'Exiting...'])
        sleep(3)
    stop = True
    if networking_scanner:
        messages.print_info(['Stopping networking scanner thread...'])
        networking_scanner.join()
        messages.print_info(['Stopped'])
        messages.print_info(['Disabling IP forwarding...'])
        Networking.disable_ip_forwarding()
        messages.print_info(['Disabled'])
    if wireless_scanner:
        messages.print_info(['Stopping wireless scanner thread...'])
        wireless_scanner.join()
        messages.print_info(['Stopped'])
    curses.curs_set(1)
    curses.endwin()
    curses.reset_shell_mode()
    curses.echo()
    os.system('clear')
