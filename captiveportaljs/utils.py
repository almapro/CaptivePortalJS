"""
Creds: WifiPhisher (https://github.com/wifiphisher/wifiphisher)
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)

from logging import getLogger
from subprocess import PIPE, Popen
import os

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
