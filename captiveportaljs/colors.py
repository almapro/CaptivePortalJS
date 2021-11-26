from __future__ import (absolute_import, division, print_function, unicode_literals)

RESET  = '\033[0m'
RED    = '\033[31m'
GREEN  = '\033[32m'
ORANGE = '\033[33m'
BLUE   = '\033[34m'
PURPLE = '\033[35m'
CYAN   = '\033[36m'
GRAY   = '\033[37m'
TAN    = '\033[93m'

def print_good(text):
    print(GREEN + text + RESET)

def print_error(text):
    print(RED + text + RESET)

def print_info(text):
    print(CYAN + text + RESET)

def print_warning(text):
    print(ORANGE + text + RESET)
