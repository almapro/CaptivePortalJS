#!/usr/bin/env python3
import os
import sys
from setuptools import setup, Command

logo = r"""
CaptivePortalJS {}
"""

try:
    raw_input # type: ignore
    sys.exit("Python 3.x is needed! Exiting...")
except NameError:
    pass

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./**/__pycache__ ./**/*.pyc ./*.pyc ./*.tgz ./*.egg-info')

setup(
    name="captiveportaljs",
    author="AlMA PRO",
    author_email="alma.pro.leader@gmail.com",
    description="A captive portal that automates everything throught tools, protocols & techniques",
    keywords=["captive portal", "js", "hacking", "network"],
    license="MIT",
    version="1.0.0",
    url="https://github.com/almapro/CaptivePortalJS",
    scripts=['bin/captiveportaljs'],
    packages=['captiveportaljs'],
    cmdclass={"clean": CleanCommand},
    include_package_data=True,
)

print(logo.format("1.0.0"));
