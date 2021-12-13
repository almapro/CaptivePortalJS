import logging
import sys
from captiveportaljs import runner

logging.basicConfig(filename='captiveportal.log', encoding='utf-8', level=logging.DEBUG, force=True, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w')

try:
    raw_input # type: ignore
    sys.exit("Python 3.x is needed! Exiting...")
except NameError:
    pass

if __name__ == '__main__':
    runner.run();
