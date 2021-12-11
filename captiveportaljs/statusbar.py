import urwid


class StatusBar(urwid.Pile):
    def __init__(self):
        statusline = urwid.AttrMap(urwid.Columns([
            urwid.Text('Test')
        ]), 'statusbar')
        statusmessage = urwid.Text('Hi')
        super().__init__([statusline, statusmessage])
