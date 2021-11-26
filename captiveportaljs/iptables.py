"""
Creds: WifiPhisher (https://github.com/wifiphisher/wifiphisher)
"""

from __future__ import (absolute_import, division, print_function, unicode_literals)

from captiveportaljs.utils import execute_commands

class IPTables():
    """Handles all iptables operations."""

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
        """Do NAT."""
        execute_commands([
            "iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format(
                external_interface),
            "iptables -A FORWARD -i {} -o {} -j ACCEPT".format(
                internal_interface, external_interface)
        ])

    @staticmethod
    def clear_rules():
        # type: () -> None
        """Clear all rules."""
        execute_commands([
            "iptables -F", "iptables -X", "iptables -t nat -F",
            "iptables -t nat -X"
        ])

    @staticmethod
    def redirect_requests_localhost(network_gw_ip):
        # type: () -> None
        """Redirect HTTP, HTTPS & DNS requests to localhost.

        Redirect the following requests to localhost:
            * HTTP (Port 80)
            * HTTPS (Port 443)
            * DNS (Port 53)
        """
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

    def on_exit(self):
        # type: () -> None
        """Start the clean up."""
        self.clear_rules()
