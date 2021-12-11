import urwid

class List(urwid.ListBox):
    def __init__(self, items, selectable=True):
        self._selectable = selectable
        super().__init__(ListWalker(items))

    def selectable(self):
        return self._selectable

class ListWalker(urwid.SimpleFocusListWalker):
    def __init__(self, content):
        super().__init__(content)

def nop(_, key):
    return key

class ListRow(urwid.WidgetWrap):
    def __init__(self, text):
        # type: (str) -> None
        w = urwid.Text(text)
        w.keypress = nop
        super().__init__(w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == 'enter':
            print('Enter')
        if key == ' ':
            print('Space')
        return super().keypress(size, key)
