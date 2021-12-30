import pyric.pyw as pyw
from pyric.pyw import Card

class WirelessInterface:
    def __init__(self, card: Card):
        self.card = card
        self.up = pyw.isup(card)
        self.mac = pyw.macget(card)
        self.managed = 'managed' == pyw.devinfo(card)['mode']
        self.can_monitor = 'monitor' in pyw.devmodes(card)
        if not self.managed and 'monitor' == pyw.devinfo(card)['mode']:
            self.monitor_card = card
        else:
            self.monitor_card = None

    def enable_monitor(self) -> bool:
        if not self.can_monitor:
            return False
        if not self.managed and self.monitor_card != None:
            return True
        if not self.up:
            pyw.up(self.card)
        try:
            self.monitor_card = pyw.getcard('{}mon'.format(self.card.dev))
        except:
            pass
        if self.monitor_card == None: self.monitor_card = pyw.devadd(self.card, '{}mon'.format(self.card.dev), 'monitor')
        for card,_ in pyw.ifaces(self.card):
            if not card.dev == self.monitor_card.dev:
                pyw.devdel(card)
        pyw.up(self.monitor_card)
        self.managed = False
        return True

    def disable_monitor(self) -> bool:
        if self.managed and self.monitor_card == None:
            return False
        self.card = pyw.devadd(self.monitor_card, self.card.dev.replace('mon', ''), 'managed')
        pyw.devdel(self.monitor_card)
        self.monitor_card = None
        pyw.up(self.card)
        self.managed = True
        return True
