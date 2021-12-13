import urwid

class StatusBar(urwid.Pile):
    def __init__(self):
        # cols, _ = urwid.raw_display.Screen().get_cols_rows()
        self.status = urwid.AttrMap(urwid.Text(''), None)
        self.tasks = urwid.Text('Tasks (0)')
        self.wireless = urwid.Text('Wireless (0/0)')
        self.devices = urwid.Text('Devices (0)')
        self.statusline = urwid.AttrMap(
            urwid.Columns([
                self.status,
                self.tasks,
                self.wireless,
                self.devices,
            ]),
            'statusbar'
        )
        self.statusmessage = urwid.Text('Hi')
        super().__init__([self.statusline, self.statusmessage])
        self.devices_count = 0
        self.wireless_count = [0, 0]
        from captiveportaljs.core import Core
        Core.CTX.connect(self.update_status_exiting, 'exiting')
        Core.get_context('devices').connect(self.update_devices_count, sender='scanner')
        Core.get_context('wireless').connect(self.update_wireless_count, sender='scanner')

    def update_status_exiting(self, *_):
        self.status.attr_map = { None: 'statusbar_error' }
        self.status.original_widget.set_text('Exiting...')

    def update_devices_count(self, _, **kw):
        from captiveportaljs.core import Core
        if Core.loop:
            count = kw['count']
            self.devices_count = count
            def update(_, count):
                self.devices.set_text('Devices ({})'.format(count))
            Core.loop.set_alarm_in(0.01, update, count)

    def update_wireless_count(self, _, **kw):
        from captiveportaljs.core import Core
        if Core.loop:
            count = kw['count']
            self.wireless_count = count
            def update(_, count):
                self.wireless.set_text('Wireless ({}/{})'.format(count[0], count[1]))
            Core.loop.set_alarm_in(0.01, update, count)
