from captiveportaljs.iptables import IPTables
from captiveportaljs.colors import print_good, print_error
from time import sleep

def run():
    try:
        print('Enabling IP forwarding...')
        IPTables.enable_ip_forwarding()
        print_good('Enabled')
        while(True):
            print('sleeping...')
            sleep(1)
    except KeyboardInterrupt:
        print_error('\n\n(^C) interrupted')
    except EOFError:
        print_error('\n\n(^D) interrupted')
