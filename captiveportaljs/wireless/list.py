import urwid
from . import AccessPoint

class AccessPointItem(urwid.WidgetWrap):
    def __init__(self, window, ap: AccessPoint):
        self.window = window
        self.ap = ap
        super().__init__(self.get_text())
        from captiveportaljs.core import Core
        Core.get_context('wireless').connect(self.add_client, '{}-add_client'.format(self.ap.id))
        Core.get_context('wireless').connect(self.ap_changed, '{}-changed'.format(self.ap.id))

    def get_text(self):
        encryption = '{} ({})'.format(self.ap.encryption, self.ap.cipher) if self.ap.cipher else self.ap.encryption
        self.essid_text = urwid.Text(self.ap.essid)
        self.bssid_text = urwid.Text(self.ap.bssid)
        self.channel_text = urwid.Text(str(self.ap.channel))
        self.encryption_text = urwid.Text(encryption)
        self.signal_strength_text = urwid.Text(str(self.ap.signal_strength))
        self.wps_text = urwid.Text('YES' if self.ap.wps else 'NO')
        self.clients_text = urwid.Text(str(len(self.ap.clients)))
        return urwid.Columns([
            self.essid_text,
            self.bssid_text,
            self.channel_text,
            self.encryption_text,
            self.signal_strength_text,
            self.wps_text,
            self.clients_text,
        ])

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

    def keypress(self, _, key):
        return key

class AccessPointListWalker(urwid.ListWalker):
    def __init__(self, window) -> None:
        self.window = window
        super().__init__()

    def positions(self, reverse=False):
        from captiveportaljs.wireless import Wireless
        list = Wireless.access_points
        if reverse: return reversed(list)
        return list

    def view_changed(self):
        self._modified()

    def get_focus(self):
        from captiveportaljs.wireless import Wireless
        if not Wireless.focused:
            return None, 0
        return AccessPointItem(self.window, Wireless.focused), self.index

    def set_focus(self, index):
        from captiveportaljs.wireless import Wireless
        if index <= len(Wireless.access_points) - 1:
            self.index = index

    def get_next(self, position):
        from captiveportaljs.wireless import Wireless
        next_position = position + 1
        if next_position > len(Wireless.access_points) -1:
            return None, None
        return AccessPointItem(self.window, Wireless.access_points[next_position]), next_position

    def get_prev(self, position):
        from captiveportaljs.wireless import Wireless
        prev_position = position - 1
        if prev_position < 0:
            return None, None
        return AccessPointItem(self.window, Wireless.access_points[prev_position]), prev_position

class AccessPointListBox(urwid.ListBox):
    def __init__(self, window):
        self.window = window
        super().__init__(AccessPointListWalker(window))

    def view_changed(self):
        self.body.view_changed()
