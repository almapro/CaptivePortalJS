import os
import curses
from time import sleep
from captiveportaljs.curseswrapper import CursesWrapper
from captiveportaljs.networking import Networking
from captiveportaljs.utils import check_sudo_mode

def run():
    wrapper = CursesWrapper()
    try:
        check_sudo_mode()
        wrapper.print(['Available Phishing Scenarios:'], curses.A_BOLD, wrapper.main_window)
        wrapper.print_info(['Enabling IP forwarding...'])
        Networking.enable_ip_forwarding()
        wrapper.print_good(['Enabled'])
        counter = 1
        while(True):
            wrapper.print_good(['Sleeping {}...'.format(counter)], wrapper.main_window)
            counter += 1
            sleep(0.5)
            key = wrapper.main_window.getch()
            if key == ord('\n'): break;
    except KeyboardInterrupt:
        wrapper.print_error(['(^C) interrupted'])
    except EOFError:
        wrapper.print_error(['(^D) interrupted'])
    wrapper.print_info(['Disabling IP forwarding...'])
    Networking.disable_ip_forwarding()
    wrapper.print_good(['Disabled'])
    curses.curs_set(True)
    os.system('clear')
