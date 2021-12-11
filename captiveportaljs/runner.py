from captiveportaljs.core import Core
from captiveportaljs.utils import check_sudo_mode

def run():
    check_sudo_mode()
    Core.start()
