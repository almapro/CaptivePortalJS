"""
Creds: WifiPhisher (https://github.com/wifiphisher/wifiphisher)
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)

from logging import getLogger
from subprocess import PIPE, Popen
import os
import sys

# pylint: disable=C0103
logger = getLogger(__name__)

def execute_commands(commands):
    """Execute each command and log any errors."""
    for command in commands:
        _, error = Popen(command.split(), stderr=PIPE, stdout=open(os.devnull, 'w')).communicate()
        if error:
            logger.error(
                "{command} has failed with the following error:\n{error}".
                format(command=command, error=error))

def check_sudo_mode():
    """If the user doesn't run the program with super user privileges, don't allow them to continue."""
    if not 'SUDO_UID' in os.environ.keys():
        sys.exit("You need root privileges or sudo to use Captive Portal JS!")
