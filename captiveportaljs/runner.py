import os
import threading
import curses
from time import sleep
from typing import Callable
from captiveportaljs.curseswindow import CursesWindow, GetOutOfLoop
from captiveportaljs.networking import Networking
from captiveportaljs.utils import check_sudo_mode

def scanner_thread(devices_window, stop):
    # type: (CursesWindow, Callable) -> None
    devices = []
    disconnected_devices = []
    while True:
        if stop():
            break;
        devices_window.entries.clear()
        scan_result = Networking.range_scan('192.168.71.1/24')[0]
        new_devices = []
        for result in scan_result:
            new_devices.append({ 'ip': result[1].psrc, 'mac': result[1].hwsrc })
        reconnected_devices = [
            device
            for device in list(filter(lambda d: not d in new_devices, disconnected_devices))
        ]
        disconnected_devices = [
            device
            for device in list(filter(lambda d: not d in new_devices, devices))
        ]
        for device in new_devices:
            if device in reconnected_devices:
                devices_window.log_info(['Device ({}) reconnected with IP ({})'.format(device['mac'], device['ip'])])
                devices_window.print_info(['IP: {} MAC: {} (reconnected)'.format(device['ip'], device['mac'])])
            else:
                devices_window.print_info(['IP: {} MAC: {}'.format(device['ip'], device['mac'])])
        for device in disconnected_devices:
            devices_window.log_info(['Device ({}) disconnected'.format(device['mac'])])
            devices_window.print_error(['IP: {} MAC: {} (disconnected)'.format(device['ip'], device['mac'])])
        devices = new_devices + disconnected_devices
        devices_window.set_title('Devices on network ({})'.format(len(devices)))
        devices_window.display()
        sleep(5)

def curses_wrapper(screen):
    # type: (curses._CursesWindow) -> curses._CursesWindow
    curses.init_pair(1, curses.COLOR_GREEN, screen.getbkgd()) # type: ignore
    curses.init_pair(2, curses.COLOR_RED, screen.getbkgd()) # type: ignore
    curses.init_pair(3, curses.COLOR_YELLOW, screen.getbkgd()) # type: ignore
    curses.init_pair(4, curses.COLOR_CYAN, screen.getbkgd()) # type: ignore
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.cbreak()
    curses.noecho()
    screen.keypad(True)
    screen.nodelay(True)
    return screen

def run():
    check_sudo_mode()
    screen = curses.wrapper(curses_wrapper)
    max_screen_height, max_screen_width = screen.getmaxyx()
    curses.noecho()
    curses.curs_set(0)
    main = CursesWindow(max_screen_height - 5, int(max_screen_width / 2), 0, 0, 'Main')
    devices = CursesWindow(max_screen_height - 5, int(max_screen_width / 2), int(max_screen_width / 2), 0, 'Devices on network (0)')
    messages = CursesWindow(5, max_screen_width, 0, max_screen_height - 5, 'Messages')
    messages.set_focused(False)
    devices.set_focused(False)
    stop = False
    messages.print_info(['Enabling IP forwarding...'])
    Networking.enable_ip_forwarding()
    messages.print_good(['Enabled'])
    scanner = threading.Thread(target=scanner_thread, args=(devices, lambda: stop))
    scanner.start()
    try:
        counter = 1
        while True:
            resized = curses.is_term_resized(max_screen_height, max_screen_width)
            if resized:
                max_screen_height, max_screen_width = screen.getmaxyx()
                curses.resize_term(max_screen_height, max_screen_width)
                main.resize_window(max_screen_height - 5, int(max_screen_width / 2), 0, 0)
                devices.resize_window(max_screen_height - 5, int(max_screen_width / 2), int(max_screen_width / 2), 0)
                messages.resize_window(5 , max_screen_width, 0, max_screen_height - 5)
            main.log_good(['Here {}'.format(counter)])
            counter += 1
            sleep(0.3)
            key = main.window.getch() if main.focused else messages.window.getch() if messages.focused else devices.window.getch()
            if key == ord('\t'):
                if main.focused:
                    main.set_focused(False)
                    devices.set_focused(True)
                    main.display()
                elif devices.focused:
                    devices.set_focused(False)
                    messages.set_focused(True)
                    devices.display()
                elif messages.focused:
                    messages.set_focused(False)
                    main.set_focused(True)
                    messages.display()
            if main.focused: main.handle_key(key)
            if devices.focused: devices.handle_key(key)
            if messages.focused: messages.handle_key(key)
    except GetOutOfLoop:
        messages.print_error(['Pressed exit key (q)', 'Exiting...'])
    except KeyboardInterrupt:
        messages.print_error(['(^C) interrupted'])
    except EOFError:
        messages.print_error(['(^D) interrupted'])
    except Exception as e:
        messages.print_error(['Unhandled error: {}'.format(str(e)), 'Exiting...'])
        sleep(3)
    stop = True
    messages.print_info(['Stopping scanner thread...'])
    scanner.join()
    messages.print_info(['Stopped'])
    messages.print_info(['Disabling IP forwarding...'])
    Networking.disable_ip_forwarding()
    messages.print_info(['Disabled'])
    curses.curs_set(1)
    curses.endwin()
    os.system('clear')
