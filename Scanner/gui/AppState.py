from import_handler import ImportDefence
with ImportDefence():
    import win32api
    from kivy.clock import Clock

from gui.Hover import Hover
from gui.ScanClasses import DummyScan

class State:
    def __init__(self) -> None:
        self.screenManager = None
        self.currentScreen = None
        self.permission = False
        self.highlighted_scan = DummyScan()
        self.scans = [DummyScan()]

    def setScreenManager(self, screens):
        self.screenManager = screens

    def screen(self, name=None):
        if name is None:
            return self.currentScreen
        Hover.enter(name)
        self.screenManager.current = name
        self.currentScreen = name

    def resize_callback(self, *_):
        # Called from Hover's `._bind`.
        def _resize_callback(*_):
            self.scan(self.highlighted_scan)
            self.highlighted_scan.select(0)

        Clock.schedule_once(_resize_callback, 0.15)

    def scan(self, scan):
        if scan not in self.scans:
            self.scans.append(scan)
        self.highlighted_scan = scan
        for scan in self.scans:
            scan.deselect()

    def ask_for_permission(self):
        if not self.permission:
            self.permission = win32api.MessageBox(
                0,
                'Do you have legal permission to execute scans on this network?',
                'Confirm permission',
                0x00000004
            ) == 6
        return self.permission


if __name__ == '__main__':
    print("This file is responsible for the State class/object.")
    print("It keeps track of the state in terms of:")
    print("    - Screen Manager of kivy, and which screen is currently displayed.")
    print("        All calls to change screen must pass through here.")
    print("    - Permission to scan the network is handled here.")
    print("    - Highlighting a scan button is handled here.")
