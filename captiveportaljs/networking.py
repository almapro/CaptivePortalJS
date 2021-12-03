"""
Creds: WifiPhisher (https://github.com/wifiphisher/wifiphisher)
"""

import subprocess
from time import sleep
import scapy.all as scapy
from ipaddress import IPv4Network
from typing import Callable
from captiveportaljs.utils import execute_commands
from captiveportaljs.curseswindow import CursesWindow

class Networking:
    @staticmethod
    def get_interfaces():
        # type: () -> list[str]
        return list(filter(lambda i: i != 'lo', scapy.get_if_list()))

    @staticmethod
    def get_active_interface():
        # type: () -> str | None
        interfaces = Networking.get_interfaces()
        for interface in interfaces:
            gateway = Networking.get_interface_gateway(interface)
            if gateway != '': return interface
        return None

    @staticmethod
    def get_interface_gateway(interface):
        # type: (str) -> str
        return Networking.get_interface_range(interface).split('/')[0]

    @staticmethod
    def get_interface_ip(interface):
        # type: (str) -> str
        return scapy.get_if_addr(interface)

    @staticmethod
    def get_interface_mac(interface):
        # type: (str) -> str
        return scapy.get_if_hwaddr(interface)

    @staticmethod
    def get_interface_range(interface):
        # type: (str) -> str
        result = subprocess.run(['route', '-n'], capture_output=True).stdout.decode().split('\n')
        ip = ''
        subnet = ''
        for row in result:
            if ip != '' and subnet != '': break
            if interface in row:
                columns = row.split(' ')
                columns = list(filter(lambda c: c != '', columns))
                if columns[1] != '0.0.0.0':
                    ip = columns[1]
                if columns[2] != '0.0.0.0':
                    subnet = columns[2]
        if ip == '' and subnet == '': return '/'
        return '{}/{}'.format(ip, IPv4Network('0.0.0.0/{}'.format(subnet)).prefixlen)

    @staticmethod
    def scanner_thread(window, interface, stop):
        # type: (CursesWindow, str, Callable) -> None
        devices = []
        disconnected_devices = []
        gateway = Networking.get_interface_gateway(interface)
        range = Networking.get_interface_range(interface)
        while True:
            try:
                if stop():
                    break;
                scan_result = Networking.range_scan(range)[0]
                window.clear_entries()
                new_devices = []
                for result in scan_result:
                    new_devices.append({ 'ip': result[1].psrc, 'mac': result[1].hwsrc })
                reconnected_devices = [
                    device
                    for device in list(filter(lambda d: d in new_devices, disconnected_devices))
                ]
                disconnected_devices = [
                    device
                    for device in list(filter(lambda d: not d in new_devices and d['ip'] != gateway, devices))
                ]
                for device in new_devices:
                    if not device in devices:
                        devices.append(device)
                for device in devices:
                    if device in disconnected_devices: continue
                    router = '(Router)' if device['ip'] == gateway else ''
                    if device in reconnected_devices:
                        window.log_info(['Device ({}) reconnected with IP ({})'.format(device['mac'], device['ip'])])
                        window.print_info(['{} {} (reconnected) {}'.format(device['ip'], device['mac'], router)])
                    else:
                        window.log_info(['Device ({}) connected with IP ({})'.format(device['mac'], device['ip'])])
                        window.print_info(['{} {} {}'.format(device['ip'], device['mac'], router)])
                for device in disconnected_devices:
                    window.log_info(['Device ({}) disconnected'.format(device['mac'])])
                    window.print_error(['{} {} (disconnected)'.format(device['ip'], device['mac'])])
                window.set_title('Devices on network ({})'.format(len(devices)))
                window.display()
                sleep(3)
            except Exception as e:
                window.log_error(['{}'.format(e)])

    @staticmethod
    def range_scan(ip_range):
        return scapy.arping(ip_range, verbose=0) # type: ignore

    @staticmethod
    def enable_ip_forwarding():
        execute_commands([
            "sysctl -w net.ipv4.ip_forward=1"
        ])

    @staticmethod
    def disable_ip_forwarding():
        execute_commands([
            "sysctl -w net.ipv4.ip_forward=0"
        ])

    @staticmethod
    def nat(internal_interface, external_interface):
        # type: (str, str) -> None
        execute_commands([
            "iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format(
                external_interface),
            "iptables -A FORWARD -i {} -o {} -j ACCEPT".format(
                internal_interface, external_interface)
        ])

    @staticmethod
    def clear_rules():
        # type: () -> None
        execute_commands([
            "iptables -F", "iptables -X", "iptables -t nat -F",
            "iptables -t nat -X"
        ])

    @staticmethod
    def redirect_requests_localhost(network_gw_ip):
        # type: (str) -> None
        execute_commands([
            "iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT "
            "--to-destination {}:{}".format(network_gw_ip, 80),
            "iptables -t nat -A PREROUTING -p udp --dport 53 -j DNAT "
            "--to-destination {}:{}".format(network_gw_ip, 53),
            "iptables -t nat -A PREROUTING -p tcp --dport 53 -j DNAT "
            "--to-destination {}:{}".format(network_gw_ip, 53),
            "iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT "
            "--to-destination {}:{}".format(network_gw_ip, 443)
        ])
