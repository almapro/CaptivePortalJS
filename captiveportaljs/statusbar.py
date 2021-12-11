import urwid

class StatusBar(urwid.Pile):
    def __init__(self):
        # cols, _ = urwid.raw_display.Screen().get_cols_rows()
        self.tasks = urwid.Text('Tasks (0)')
        self.wireless = urwid.Text('Wireless (0)')
        self.devices = urwid.Text('Devices (0)')
        self.statusline = urwid.AttrMap(
            urwid.Columns([
                self.tasks,
                self.wireless,
                self.devices,
            ]),
            'statusbar'
        )
        self.statusmessage = urwid.Text('Hi')
        super().__init__([self.statusline, self.statusmessage])
        self.devices_count = 0
        from captiveportaljs.core import Core
        Core.get_context('devices').connect(self.update_devices_count, sender='scanner')

    def update_devices_count(self, _, **kw):
        from captiveportaljs.core import Core
        if Core.loop:
            count = kw['count']
            self.devices_count = count
            def update(_, count):
                self.devices.set_text('Devices ({})'.format(count))
            Core.loop.set_alarm_in(0.01, update, count)
