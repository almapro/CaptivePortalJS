import sys
from captiveportaljs import runner

try:
    raw_input # type: ignore
    sys.exit("Python 3.x is needed! Exiting...")
except NameError:
    pass

if __name__ == '__main__':
    runner.another_run();
