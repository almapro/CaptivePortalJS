import sys
from captiveportaljs import runner

try:
    raw_input # type: ignore
    sys.exit("Python 3.x is needed! Exiting...")
except NameError:
    pass

runner.run();
