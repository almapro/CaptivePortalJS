import urwid
from uuid import uuid4 as v4
from captiveportaljs.list import List, ListRow

class Window(urwid.Frame):
    def __init__(self, headers, items):
        self.headers = []
        viewItems = []
        if len(headers):
            for header in headers:
                if isinstance(header, str):
                    self.headers.append(urwid.Text(header))
                else:
                    self.headers.append(header)
            self.headers.append(urwid.Divider('-'))
        for item in items:
            viewItems.append(item)
        self.list = List(viewItems)
        self.index = 0
        super().__init__(self.list)

    def selectable(self):
        return True

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
        from captiveportaljs.core import Core
        for entry in entries:
            if isinstance(entry, str):
                item = ListRow(entry)
            else:
                item = entry
            item.id = str(v4())
            self.list.walker.append(urwid.AttrMap(item, 'info', focus_map='item_hover'))
            if Core.loop: Core.loop.set_alarm_in(0.01, self.refresh)

    def entry_good(self, entries):
        from captiveportaljs.core import Core
        for entry in entries:
            item = ListRow(entry)
            if isinstance(entry, str):
                item = ListRow(entry)
            else:
                item = entry
            item.id = str(v4())
            self.list.walker.append(urwid.AttrMap(item, 'good', focus_map='item_hover'))
            if Core.loop: Core.loop.set_alarm_in(0.01, self.refresh)

    def entry_warning(self, entries):
        from captiveportaljs.core import Core
        for entry in entries:
            item = ListRow(entry)
            if isinstance(entry, str):
                item = ListRow(entry)
            else:
                item = entry
            item.id = str(v4())
            self.list.walker.append(urwid.AttrMap(item, 'warning', focus_map='item_hover'))
            if Core.loop: Core.loop.set_alarm_in(0.01, self.refresh)

    def entry_error(self, entries):
        from captiveportaljs.core import Core
        for entry in entries:
            item = ListRow(entry)
            if isinstance(entry, str):
                item = ListRow(entry)
            else:
                item = entry
            item.id = str(v4())
            self.list.walker.append(urwid.AttrMap(item, 'error', focus_map='item_hover'))
            if Core.loop: Core.loop.set_alarm_in(0.01, self.refresh)
