import urwid
from captiveportaljs.list import List

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
