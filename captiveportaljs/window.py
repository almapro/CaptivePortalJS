import urwid
from captiveportaljs.list import List, ListRow

class Window(urwid.Frame):
    def __init__(self, headers, items, selectable=True):
        self.headers = []
        viewItems = []
        if len(headers):
            for header in headers:
                self.headers.append(urwid.Text(header))
            self.headers.append(urwid.Divider('-'))
        for item in items:
            viewItems.append(item)
        self.list = List(viewItems, selectable)
        super().__init__(self.list)

    def refresh(self, *_):
        self.body = urwid.AttrMap(self.list, '')

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
 
    def entry(self, sender, **kw):
        if sender == 'info':
            self.entry_info(kw['entries'])
        if sender == 'good':
            self.entry_good(kw['entries'])
        if sender == 'warning':
            self.entry_warning(kw['entries'])
        if sender == 'error':
            self.entry_error(kw['entries'])

    def entry_info(self, entries):
        for entry in entries:
            self.list.walker.append(urwid.AttrMap(ListRow(entry), 'info'))

    def entry_good(self, entries):
        for entry in entries:
            self.list.walker.append(urwid.AttrMap(ListRow(entry), 'good'))

    def entry_warning(self, entries):
        for entry in entries:
            self.list.walker.append(urwid.AttrMap(ListRow(entry), 'warning'))

    def entry_error(self, entries):
        for entry in entries:
            self.list.walker.append(urwid.AttrMap(ListRow(entry), 'error'))
