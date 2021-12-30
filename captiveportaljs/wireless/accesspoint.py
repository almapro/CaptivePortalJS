from uuid import uuid4 as v4

class AccessPoint(object):
    def __init__(self, essid: str, bssid: str, channel: int, encryption: str, signal_strength: int, wps: bool, cipher: str, suite: str):
        self.id = str(v4())
        self.essid = essid
        self.bssid = bssid
        self.channel = channel
        self.encryption = encryption
        self.wps = wps
        self.cipher = cipher
        self.suite = suite
        self.signal_strength = signal_strength
        self.clients = []

    def set_channel(self, channel: int):
        self.channel = channel

    def set_encryption(self, encryption: str):
        self.encryption = encryption

    def set_wps(self, wps: bool):
        self.wps = wps

    def set_cipher(self, cipher: str):
        self.cipher = cipher

    def set_suite(self, suite: str):
        self.suite = suite

    def set_signal_strength(self, strength: int):
        self.signal_strength = strength

    def add_client(self, client: str):
        from captiveportaljs.core import Core
        if not client in ['01:80:c2:00:00:00', '00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff', None] and not client.startswith('01:00:5e:') and not client.startswith('33:33:'):
            if client not in self.clients:
                self.clients.append(client)
                Core.get_context('wireless').send('{}-changed'.format(self.id))
