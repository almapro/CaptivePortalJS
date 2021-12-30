import urwid
from .accesspoint import AccessPoint
from .list import AccessPointListBox

class WirelessWindow(urwid.Frame):
    def __init__(self, headers):
        self.headers = []
        if len(headers):
            for header in headers:
                if isinstance(header, str):
                    self.headers.append(urwid.Text(header))
                else:
                    self.headers.append(header)
            self.headers.append(urwid.Divider('-'))
        self.list = AccessPointListBox(self)
        self.index = 0
        self.access_points = [] # type: list[AccessPoint]
        super().__init__(self.list)

    def view_changed(self):
        self.list.view_changed()

    def add_ap(self, ap: AccessPoint):
        found = False
        for access_point in self.access_points:
            if access_point.bssid == ap.bssid and access_point.essid == ap.essid:
                found = True
                break
        if not found:
            self.access_points.append(ap)
            self.view_changed()

    def selectable(self):
        return True

    def log_info(self, entries):
        from captiveportaljs.core import Core
        Core.get_context('logs').send('info', entries=entries)

    def log_good(self, entries):
        from captiveportaljs.core import Core
        Core.get_context('logs').send('good', entries=entries)

    def log_warning(self, entries):
        from captiveportaljs.core import Core
        Core.get_context('logs').send('warning', entries=entries)

    def log_error(self, entries):
        from captiveportaljs.core import Core
        Core.get_context('logs').send('error', entries=entries)
 
    def message_info(self, entries):
        from captiveportaljs.core import Core
        Core.get_context('messages').send('info', entries=entries)

    def message_good(self, entries):
        from captiveportaljs.core import Core
        Core.get_context('messages').send('good', entries=entries)

    def message_warning(self, entries):
        from captiveportaljs.core import Core
        Core.get_context('messages').send('warning', entries=entries)

    def message_error(self, entries):
        from captiveportaljs.core import Core
        Core.get_context('messages').send('error', entries=entries)

    def refresh(self, *_):
        self.body = urwid.AttrMap(self.list, '')
