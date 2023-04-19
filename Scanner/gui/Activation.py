from register import Register
from gui.ScanClasses import DummyScan
from gui.dialogs import popup
from gui.AppState import State

def activate(x):
    if State().ask_for_permission():
        s = State().highlighted_scan
        if Register().is_running(s.name) or s.is_running:
            popup(
                "Cannot run scan",
                f"**This scan is already running!**\n\n{s.name}",
                error=True
            )
            return

        # print(f"Play {s.name}!")
        if s is DummyScan():
            popup("Cannot start scan", f"Select a scan first!", warning=True)
        if popup("Start scan", f"Starting the scan: {s.name}", cancel=True):
            Register().start(s.name, s.act, s.finished)
        else:
            popup(
                "Canceled scan",
                "The scan has been cancelled.\n\n\n<sub><sup>Cancel culture, I'm telling ya.</sup></sub>",
                warning=True
            )

if __name__ == '__main__':
    print("This file is responsible for any methods called by the Activation Button (▶) in Scan Screen.")
