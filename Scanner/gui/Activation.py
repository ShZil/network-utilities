from register import Register
from gui.ScanClasses import DummyScan, Analysis, Scan
from gui.dialogs import popup
from gui.AppState import State


def activate(*x):
    """Activates a scan.
    If the scan cannot be activated,
    pops a relevant error message"""
    if not State().ask_for_permission():
        return

    s: Scan = State().highlighted_scan
    if Register().is_running(s.name) or s.is_running:
        import db
        from datetime import timedelta
        time = int(db.get_information_about_scan(s.name)[2])
        indefinite_message = "running indefintely forever" if Register().is_infinite_scan(s.name) else "not running indefinitely, and will stop at some point soon."
        if time == 0:
            time_message = f"The datebase lists this scan's time estimation as infinite."
        else:
            time_message = f"The database lists this scan at roughly {time} second(s). So it'll probably be done in {str(timedelta(seconds=time))}[^1]"
        popup(
            "Cannot run scan",
            f"**This scan is already running!**\n{s.name} \n\
            This scan is {indefinite_message}. \n\
            {time_message} \
            \n\n**TIP:** You can see which scans are currently running according to the ellipsis (...)! \n\
            \n\n**Note:** Time estimate might be off, depending on your network size and scan configuration.",
            error=True
        )
        return

    # print(f"Play {s.name}!")
    if s is DummyScan():
        popup("Cannot start scan", f"Select a scan first!\nYou can select a scan by left-clicking on a name in the right column of the screen.\n\
                You can read all about each scan by clicking on it, and then on the Information button on top.", warning=True)
    if not isinstance(s, Analysis):
        if not popup("Start scan", f"Starting the scan: {s.name}", cancel=True):
            popup(
                "Canceled scan",
                "The scan has been cancelled.\n\n<sub><sup>Cancel culture, I'm telling ya.</sup></sub>",
                warning=True
            )
            return
    Register().start(s.name, s.act, s.finished)


if __name__ == '__main__':
    print("This file is responsible for any methods called by the Activation Button (▶) in Scan Screen.")
