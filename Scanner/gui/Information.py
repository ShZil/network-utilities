from import_handler import ImportDefence
with ImportDefence():
    import re
    from threading import enumerate as enumerate_threads

from gui.dialogs import popup
import db
from ipconfig import ipconfig
from gui.ScanClasses import DummyScan
from gui.AppState import State


def display_information():
    highlighted = State().highlighted_scan
    if highlighted is DummyScan() or highlighted is None:
        popup(f"General Information", general_information(), info=True)
    else:
        popup(
            f"Information about {highlighted.name}",
            information_about(highlighted.name),
            info=True
        )


def information_about(name: str) -> str:
    # Get the entry about the scan and destructure it
    entry = db.get_information_about_scan(name)
    name0, description, time, reward, certainty, safety, mode, repeats = entry
    if name != name0:
        raise ValueError(
            f"Weird name problem: key is `{name}`, database says `{name0}`."
        )

    # Generate phrases
    perrepeat = " per repeat" if repeats else ""
    hasrepeats = "Repeatable" if repeats else "Not repeatable"
    certainty_prompt = "That's pretty uncertain" if certainty <= 50 else "That's mildly certain" if certainty <= 80 else "That's pretty certain" if certainty <= 100 else "???"
    safety_prompt = "That's really unsafe" if safety <= 30 else "That's pretty unsafe" if safety <= 70 else "That's quite safe" if safety < 100 else "That's perfectly safe -- completely undetectable"

    # If the description includes a packet model, escape it into a code block.
    if not description.endswith(('.', '. ', '>')):
        description += '.'
    description = re.sub(
        "<[^<>]+>",
        "<br>```\\g<0>```",
        description,
        flags=re.DOTALL
    )

    # Return everything in markdown format.
    return '\n'.join([
        f"# {name}",
        f"## Description",
        f"{description}",
        f"## Time estimate",
        f"{time}s{perrepeat}",
        f"## Risk and Reward",
        f"### What you get",
        f"{reward}",
        f"### How reliable is that?",
        f"{certainty}% certain that the data are correct.",
        f"{certainty_prompt}.",
        f"### Safety",
        f"Running this is {safety}% safe.",
        f"{safety_prompt}.",
        f"## Others",
        f"- {hasrepeats}",
        f"- Mode: {mode}"
    ])


def general_information() -> str:
    computers_in_network = len(ipconfig()["All Possible Addresses"])
    interface = ipconfig()["Interface"]
    mask = ipconfig()["Subnet Mask"]

    def _get_readable_threads():
        def find_between(s):
            # "some(str)ing"
            # "some", "str)ing"
            # "str)ing"
            # "str", "ing"
            # "str"
            return (s.split('('))[1].split(')')[0]

        threads = enumerate_threads()
        threads = [thread.name for thread in threads]
        threads = [name if '(' not in name else find_between(name) for name in threads]
        uniques = set(threads)
        counts = [threads.count(name) for name in uniques]
        threads = [
            f"{count} × {name}" if count > 1 else name for name,
            count in zip(uniques, counts)
        ]
        threads = ['* ' + name for name in threads]
        return threads

    from NetworkStorage import here, router
    return '\n\n'.join([
        f"# General Information",
        f"## This device",
        f"IPv4 Address: {here.ip}",
        f"Network Interface: {interface}",
        f"## Router (Gateway)",
        f"IPv4 Address: {router.ip}",
        f"## Local Network",
        f"Subnet mask: {mask}",
        f"Possible IPv4 addresses: {computers_in_network} addresses",
        f"## Others",
        f"Premission to scan: {State().permission}",
        f"## Current Threads",
        *_get_readable_threads()
    ])


if __name__ == '__main__':
    print("This file is responsible for any methods called by the Information Button (ℹ) in Scan Screen.")
