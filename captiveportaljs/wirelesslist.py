import urwid

class AccessPointItem(urwid.Columns):
    def __init__(self, ap):
        self.ap = ap
        encryption = '{} ({})'.format(self.ap.encryption, self.ap.cipher) if self.ap.cipher else self.ap.encryption
        self.essid_text = urwid.Text(self.ap.essid)
        self.bssid_text = urwid.Text(self.ap.bssid)
        self.channel_text = urwid.Text(str(self.ap.channel))
        self.encryption_text = urwid.Text(encryption)
        self.signal_strength_text = urwid.Text(str(self.ap.signal_strength))
        self.wps_text = urwid.Text('YES' if self.ap.wps else 'NO')
        self.clients_text = urwid.Text(str(len(self.ap.clients)))
        super().__init__([
            self.essid_text,
            self.bssid_text,
            self.channel_text,
            self.encryption_text,
            self.signal_strength_text,
            self.wps_text,
            self.clients_text,
        ])
        from captiveportaljs.core import Core
        Core.get_context('wireless').connect(self.add_client, '{}-add_client'.format(self.ap.id))
        Core.get_context('wireless').connect(self.ap_changed, '{}-changed'.format(self.ap.id))

    def ap_changed(self, *_):
        encryption = '{} ({})'.format(self.ap.encryption, self.ap.cipher) if self.ap.cipher else self.ap.encryption
        self.essid_text.set_text(self.ap.essid)
        self.bssid_text.set_text(self.ap.bssid)
        self.channel_text.set_text(str(self.ap.channel))
        self.encryption_text.set_text(encryption)
        self.signal_strength_text.set_text(str(self.ap.signal_strength))
        self.wps_text.set_text('YES' if self.ap.wps else 'NO')
        self.clients_text.set_text(str(len(self.ap.clients)))

    def add_client(self, _, **kw):
        client = kw['client']
        if client not in self.ap.clients:
            self.ap.clients.append(client)
            self.ap_changed()

    def selectable(self):
        return True
