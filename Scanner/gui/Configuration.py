from gui.dialogs import popup


def display_configuration():
    if state.highlighted_scan is None:
        name = "scans"
    elif state.highlighted_scan is DummyScan():
        name = "scans"
    else:
        name = state.highlighted_scan.name
    popup(f"Configuration of {name}", "Coming soon.")


if __name__ == '__main__':
    print("This file is responsible for any methods called by the Configuration Button (⚙) in Scan Screen.")
