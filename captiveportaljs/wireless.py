# import pyric
import pyric.pyw as pyw
from pyric.pyw import Card
from scapy.layers import dot11
from scapy.layers.dot11 import Dot11Elt, RadioTap, Dot11Beacon, Dot11ProbeResp
from typing import Callable
from captiveportaljs.curseswindow import CursesWindow

class Wireless:
    @staticmethod
    def get_interfaces():
        # type: () -> list[str]
        return pyw.winterfaces()

    @staticmethod
    def get_interface_info(interface):
        # type: (str) -> Card
        return pyw.getcard(interface)

    @staticmethod
    def set_interface_channel(interface, channel):
        # type: (str, int) -> None
        pyw.chset(interface, channel)

    @staticmethod
    def scanner_thread(window, interface, stop):
        # type: (CursesWindow, WirelessInterface, Callable) -> None
        enabled_monitor = False
        try:
            enabled_monitor = interface.enable_monitor()
        except:
            pass
        if interface.can_monitor and enabled_monitor:
            if interface.monitor_card:
                aps_count = 0
                clients_count = 0
                while True:
                    if stop():
                        interface.disable_monitor()
                        break
                    dot11.sniff(iface=interface.monitor_card.dev, prn=Wireless.process_packets, count=1, store=0)
                    new_aps_count = len(Wireless.access_points) + len(Wireless.hidden_access_points)
                    new_clients_count = 0
                    for ap in Wireless.access_points:
                        new_clients_count += len(ap.clients)
                    for ap in Wireless.hidden_access_points:
                        new_clients_count += len(ap.clients)
                    if new_aps_count != aps_count or clients_count != new_clients_count:
                        aps_count = new_aps_count
                        clients_count = new_clients_count
                        window.clear_entries()
                        for access_point in Wireless.access_points:
                            window.print_info(['{}    {}    {}    {}    {}'.format(access_point.essid, access_point.bssid, access_point.channel, access_point.encryption, access_point.signal_strength)])
                            for client in access_point.clients:
                                window.print_info(['    {}'.format(client)])
                        for access_point in Wireless.hidden_access_points:
                            window.print_info(['{}    {}    {}    {}    {} (hidden)'.format(access_point.essid, access_point.bssid, access_point.channel, access_point.encryption, access_point.signal_strength)])
                            for client in access_point.clients:
                                window.print_info(['    {}'.format(client)])

    access_points = [] # type: list[AccessPoint]
    hidden_access_points = [] # type: list[AccessPoint]

    @staticmethod
    def process_packets(packet):
        # type: (RadioTap) -> None
        if packet.haslayer(Dot11Beacon):
            # check if the packet has info field to prevent processing
            # malform beacon
            if hasattr(packet.payload, 'info'):
                if not packet.info or b"\00" in packet.info:
                    if packet.addr3 not in Wireless.hidden_access_points:
                        Wireless.hidden_access_points.append(packet.addr3)
                else:
                    Wireless.create_ap_from_packet(packet)
        elif packet.haslayer(Dot11ProbeResp):
            if packet.addr3 in Wireless.hidden_access_points:
                Wireless.create_ap_from_packet(packet)
        elif packet.haslayer(dot11.Dot11):
            Wireless.find_clients_from_packet(packet)

    @staticmethod
    def create_ap_from_packet(packet):
        # type: (RadioTap) -> None
        elt_section = packet[Dot11Elt]
        try:
            channel = ord(packet[Dot11Elt][2].info)
            if channel not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ,11, 12, 13]:
                return
        except (TypeError, IndexError):
            return
        bssid = packet.addr3
        essid = None
        encryption = None
        non_decodable_name = "<contains non-printable chars>"
        rssi = Wireless.get_rssi(packet.notdecoded)
        new_signal_strength = Wireless.calculate_signal_strength(rssi)
        try:
            essid = elt_section.info.decode("utf8")
        except UnicodeDecodeError:
            essid = non_decodable_name
        for access_point in Wireless.access_points:
            if bssid == access_point.bssid:
                current_signal_strength = access_point.signal_strength
                signal_difference = new_signal_strength - current_signal_strength
                if signal_difference > 5:
                    access_point.signal_strength = new_signal_strength
                return None
        encryption = Wireless.find_encryption_from_packet(packet)
        access_point = AccessPoint(essid, bssid, channel, encryption)
        access_point.set_signal_strength(new_signal_strength)
        Wireless.access_points.append(access_point)

    @staticmethod
    def find_encryption_from_packet(packet):
        # type: (RadioTap) -> str
        encryption_info = packet.sprintf("%Dot11Beacon.cap%")
        elt_section = packet[Dot11Elt]
        encryption = ''
        found_wps = False
        try:
            while (isinstance(elt_section, Dot11Elt) or (not encryption and not found_wps)):
                if elt_section.ID == 48:
                    encryption = "WPA2"
                elif (elt_section.ID == 221 and elt_section.info.startswith(b"\x00P\xf2\x01\x01\x00")):
                    encryption = "WPA"
                if (elt_section.ID == 221 and elt_section.info.startswith(b"\x00P\xf2\x04")):
                    found_wps = True
                elt_section = elt_section.payload
                if not encryption:
                    if "privacy" in encryption_info:
                        encryption = "WEP"
                    else:
                        encryption = "OPEN"
        except AttributeError:
            pass
        if encryption != "WEP" and found_wps:
            encryption += "/WPS"
        return encryption

    @staticmethod
    def get_rssi(non_decoded_packet):
        # type: (RadioTap) -> int
        try:
            return -(256 - max(ord(non_decoded_packet[-4:-3]), ord(non_decoded_packet[-2:-1])))
        except TypeError:
            return -100

    @staticmethod
    def calculate_signal_strength(rssi):
        # type: (int) -> int
        signal_strength = 0
        if rssi >= -50:
            signal_strength = 100
        else:
            signal_strength = 2 * (rssi + 100)
        return signal_strength

    @staticmethod
    def find_clients_from_packet(packet):
        # type: (RadioTap) -> None
        receiver = packet.addr1
        sender = packet.addr2
        if sender and receiver:
            receiver_identifier = receiver[:8]
            sender_identifier = sender[:8]
        else:
            return
        for identifier in [receiver_identifier, sender_identifier]:
            if not identifier in ['01:80:c2:00:00:00', '00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff', None] and not identifier.startswith('01:00:5e:') and not identifier.startswith('33:33:ff:'):
                for access_point in Wireless.access_points:
                    access_point_bssid = access_point.bssid
                    if access_point_bssid == receiver:
                        access_point.add_client(sender)
                    elif access_point_bssid == sender:
                        access_point.add_client(receiver)

    @staticmethod
    def get_sorted_access_points():
        return sorted(Wireless.access_points, key=lambda ap: ap.signal_strength, reverse=True)

class WirelessInterface:
    def __init__(self, card):
        # type: (Card) -> None
        self.card = card
        self.up = pyw.isup(card)
        self.mac = pyw.macget(card)
        self.managed = 'managed' == pyw.devinfo(card)['mode']
        self.can_monitor = 'monitor' in pyw.devmodes(card)
        self.monitor_card = None

    def enable_monitor(self):
        # type: () -> bool
        if not self.can_monitor:
            return False
        if not self.managed and self.monitor_card != None:
            return True
        if not self.up:
            pyw.up(self.card)
        try:
            self.monitor_card = pyw.getcard('{}mon'.format(self.card.dev))
        except:
            pass
        if self.monitor_card == None: self.monitor_card = pyw.devadd(self.card, '{}mon'.format(self.card.dev), 'monitor')
        for card,_ in pyw.ifaces(self.card):
            if not card.dev == self.monitor_card.dev:
                pyw.devdel(card)
        pyw.up(self.monitor_card)
        self.managed = False
        return True

    def disable_monitor(self):
        # type: () -> bool
        if self.managed and self.monitor_card == None:
            return False
        self.card = pyw.devadd(self.monitor_card, self.card.dev, 'managed')
        pyw.devdel(self.monitor_card)
        self.monitor_card = None
        pyw.up(self.card)
        self.managed = True
        return True

class AccessPoint(object):
    def __init__(self, essid, bssid, channel, encryption):
        # type: (str, str, int, str) -> None
        self.essid = essid
        self.bssid = bssid
        self.channel = channel
        self.encryption = encryption
        self.signal_strength = 0
        self.clients = []

    def set_channel(self, channel):
        # type: (int) -> None
        self.channel = channel
    def set_encryption(self, encryption):
        # type: (str) -> None
        self.encryption = encryption

    def set_signal_strength(self, strenght):
        # type: (int) -> None
        self.signal_strength = strenght

    def add_client(self, client):
        # type: (str) -> None
        if not client in ['01:80:c2:00:00:00', '00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff', None] and not client.startswith('01:00:5e:') and not client.startswith('33:33:ff:'):
            if client not in self.clients:
                self.clients.append(client)
