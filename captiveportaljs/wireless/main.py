import pyric.pyw as pyw
from pyric.pyw import Card
from scapy.layers import dot11
from scapy.layers.dot11 import Dot11Elt, RadioTap, Dot11Beacon, Dot11ProbeResp
from typing import Callable
from .accesspoint import AccessPoint
from .interface import WirelessInterface
from .window import WirelessWindow

class Wireless:
    @staticmethod
    def get_interfaces() -> list[str]:
        return pyw.winterfaces()

    @staticmethod
    def get_interface_info(interface: str) -> Card:
        return pyw.getcard(interface)

    @staticmethod
    def set_interface_channel(interface, channel):
        # type: (str, int) -> None
        pyw.chset(interface, channel)

    @staticmethod
    def scanner_thread(window: WirelessWindow, interface: WirelessInterface, stop: Callable):
        from captiveportaljs.core import Core
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
                    try:
                        if stop():
                            interface.disable_monitor()
                            Core.SCANNERS['wireless'] = False
                            break
                        dot11.sniff(iface=interface.monitor_card.dev, prn=Wireless.process_packets(window), count=5, store=0)
                        new_aps_count = len(window.access_points)
                        new_clients_count = 0
                        for ap in window.access_points:
                            new_clients_count += len(ap.clients)
                        if new_aps_count != aps_count or clients_count != new_clients_count:
                            aps_count = new_aps_count
                            clients_count = new_clients_count
                            Core.get_context('wireless').send('scanner', count=[aps_count, clients_count])
                            Core.set_window_title('wireless', 'Wireless Access Points/Stations ({}/{})'.format(aps_count, clients_count))
                    except Exception as e:
                        window.log_warning(['{}'.format(e)])

    access_points = [] # type: list[AccessPoint]
    hidden_access_points = [] # type: list[str]
    focused = None # type: None | AccessPoint

    @staticmethod
    def process_packets(window: WirelessWindow):
        def process(packet: RadioTap):
            if packet.haslayer(Dot11Beacon):
                if hasattr(packet.payload, 'info'):
                    if not packet.info or b"\00" in packet.info:
                        if packet.addr3 not in Wireless.hidden_access_points:
                            Wireless.hidden_access_points.append(packet.addr3)
                    else:
                        Wireless.create_ap_from_packet(window, packet)
            elif packet.haslayer(Dot11ProbeResp):
                if packet.addr3 in Wireless.hidden_access_points:
                    Wireless.create_ap_from_packet(window, packet)
            elif packet.haslayer(dot11.Dot11):
                Wireless.find_clients_from_packet(window, packet)
        return process

    @staticmethod
    def create_ap_from_packet(window: WirelessWindow, packet: RadioTap):
        from captiveportaljs.core import Core
        elt_section = packet[Dot11Elt]
        try:
            channel = 1
            for n in range(20):
                try:
                    if elt_section[n].ID == 3 and elt_section[n].len == 1:
                        channel = ord(elt_section[n].info)
                except:
                    pass
            if channel not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ,11, 12, 13]:
                return
        except (TypeError, IndexError):
            return
        bssid = packet.addr3
        essid = None
        non_decodable_name = "<contains non-printable chars>"
        rssi = Wireless.get_rssi(packet.notdecoded)
        new_signal_strength = Wireless.calculate_signal_strength(rssi)
        [
            encryption, # type: str
            wps, # type: bool
            cipher, #: type: str
            suite #: type: str
        ] = Wireless.find_encryption_from_packet(packet)
        try:
            essid = elt_section.info.decode("utf8")
        except UnicodeDecodeError:
            essid = non_decodable_name
        for access_point in Wireless.access_points:
            if bssid == access_point.bssid:
                current_signal_strength = access_point.signal_strength
                signal_difference = new_signal_strength - current_signal_strength
                if signal_difference > 5:
                    access_point.set_signal_strength(new_signal_strength)
                access_point.set_channel(channel)
                access_point.set_wps(wps)
                access_point.set_cipher(cipher)
                access_point.set_suite(suite)
                Core.get_context('wireless').send('{}-changed'.format(access_point.id))
                return None
        access_point = AccessPoint(essid, bssid, channel, encryption, new_signal_strength, wps, cipher, suite)
        window.add_ap(access_point)
        # window.entry_info([
        #     AccessPointItem(window, access_point)
        # ])

    @staticmethod
    def find_encryption_from_packet(
            packet # type: RadioTap
        ):
        encryption_info = packet.sprintf("%Dot11Beacon.cap%")
        elt_section = packet[Dot11Elt]
        encryption = ''
        cipher = ''
        auth_suite = ''
        found_wps = False
        while (isinstance(elt_section, Dot11Elt) or (not encryption and not found_wps)):
            compound = elt_section.info
            if elt_section.ID == 48 or elt_section.ID == 221:
                comp_sections = compound.split(b'\x00\x00')
                if len(comp_sections) >= 4:
                    ciphers = {
                        b'P\xf2\x00': 'GROUP',
                        b'P\xf2\x01': 'WEP',
                        b'P\xf2\x02': 'TKIP',
                        b'P\xf2\x04': 'CCMP',
                        b'P\xf2\x05': 'WEP'
                    }
                    auth_suites = {
                        b'P\xf2\x01': 'MGT',
                        b'P\xf2\x02': 'PSK'
                    }
                    for key, value in ciphers.items():
                        if comp_sections[1].startswith(key):
                            cipher = value
                    for key, value in auth_suites.items():
                        if comp_sections[3].startswith(key):
                            auth_suite = value
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
        return [encryption, encryption != "WEP" and found_wps, cipher, auth_suite]

    @staticmethod
    def get_rssi(non_decoded_packet: RadioTap):
        try:
            # return -(256 - ord(non_decoded_packet[-6:-5]))
            return -(256 - max(ord(non_decoded_packet[-4:-3]), ord(non_decoded_packet[-2:-1])))
        except TypeError:
            return -100

    @staticmethod
    def calculate_signal_strength(rssi):
        # type: (int) -> int
        # signal_strength = 0
        # if rssi >= -50:
        #     signal_strength = 100
        # else:
        #     signal_strength = 2 * (rssi + 100)
        return rssi

    @staticmethod
    def find_clients_from_packet(window: WirelessWindow, packet: RadioTap):
        receiver = packet.addr1
        sender = packet.addr2
        if sender and receiver:
            receiver_identifier = receiver[:8]
            sender_identifier = sender[:8]
        else:
            return
        for identifier in [receiver_identifier, sender_identifier]:
            if not identifier in ['01:80:c2:00:00:00', '00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff', None] and not identifier.startswith('01:00:5e:') and not identifier.startswith('33:33:'):
                for access_point in window.access_points:
                    access_point_bssid = access_point.bssid
                    if access_point_bssid == receiver:
                        access_point.add_client(sender)
                    elif access_point_bssid == sender:
                        access_point.add_client(receiver)

    @staticmethod
    def get_sorted_access_points():
        return sorted(Wireless.access_points, key=lambda ap: ap.signal_strength, reverse=True)
