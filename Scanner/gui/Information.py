from import_handler import ImportDefence
with ImportDefence():
    import re
    from threading import enumerate as enumerate_threads

from gui.dialogs import popup
import db
from ipconfig import ipconfig
from gui.ScanClasses import DummyScan
from gui.AppState import State


def display_information(*_):
    highlighted = State().highlighted_scan
    if highlighted is DummyScan() or highlighted is None:
        popup(f"General Information", general_information(), info=True)
    else:
        name = highlighted.name
        information = information_about(name)
        if information == '': return
        popup(f"Information about {name}", information, info=True)


def display_information_knowledge(*_):
    highlighted = State().highlighted_scan
    if highlighted is DummyScan() or highlighted is None:
        popup(f"General Knowledge", general_knowledge(), info=True)
    else:
        name = highlighted.name
        information = information_about(name)
        if information == '': return
        popup(f"Information about {name}", information, info=True)


def information_about(name: str) -> str:
    # Get the entry about the scan and destructure it
    entry = db.get_information_about_scan(name)
    if entry is None:
        popup(f"Information about {name}", "It appears the database has no information regarding this scan.\
              \n\nPlease try updating your installation!", warning=True)
        return ""
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
    
    def _html_from_osi_model(message: str) -> str:
        import re

        pattern = r"<([A-Z][^>]*)>"
        replacement = r"<tr><td>\1</td></tr>"

        new_string = re.sub(pattern, replacement, message)
        new_string = re.sub(r"<tr><td>([^<>]*)</td></tr>\s*<tr><td>", r"<tr><td>\1</td></tr>", new_string)

        new_string = re.sub(r"<tr>", "<table><tr>", new_string, count=1)
        new_string = new_string.rsplit("</tr>", 1)[0] + "</tr></table>"
        
        return new_string
    description = _html_from_osi_model(description)

    time_estimate = f"{time}s{perrepeat}" if time > 0 else f"Infinite{perrepeat}"
    # description = re.sub(
    #     "<[^<>]+>",
    #     "<br>```\\g<0>```",
    #     description,
    #     flags=re.DOTALL
    # )

    # Return everything in markdown format.
    return '\n'.join([
        f"# {name}",
        f"## Description",
        f"{description}",
        f"## Time estimate",
        f"{time_estimate}",
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
        threads = [f'* `{name}`' for name in threads]
        return threads

    from NetworkStorage import here, router
    return '\n\n'.join([
        f"# General Information",
        f"## This device",
        f"IPv4 Address: `{here.ip}`",
        f"Network Interface: `{interface}`",
        f"## Router (Gateway)",
        f"IPv4 Address: `{router.ip}`",
        f"## Local Network",
        f"Subnet mask: `{mask}`",
        f"Possible IPv4 addresses: `{computers_in_network} addresses`",
        f"## Others",
        f"Premission to scan: `{State().permission}`",
        f"## Current Threads",
        *_get_readable_threads()
    ])


def general_knowledge() -> str:
    return '\n\n'.join([
        f"# General Knowledge",
        f"## Network Storage Information",
        f"### MAC Address",
        f"A Media Access Control address (also hardware or physical address) is a unique, 12-character alphanumeric attribute,",
        f"that is used to identify individual electronic devices on a network.",
        f"An example of a MAC address is: `00-B0-D0-63-C2-26`.",
        f"### IPv4 Address",
        f"An Internet Protocol Version 4 address is a 32-bit number that uniquely identifies a network interface on a machine.",
        f"It's often used for routing packets to the correct destination.",
        f"An example of an IPv4 address is: `1.2.129.4`.",
        f"### IPv6 Address",
        f"An Internet Protocol Version 6 address is a numeric label that is used to identify and locate a network interface of a computer,",
        f"or a network node participating in a computer network using IPv6.",
        f"IP addresses are included in the packet header to indicate the source and the destination of each packet.",
        f"The IP address of the destination is used to make decisions about routing IP packets to other networks.",
        f"IPv6 is the successor to the first addressing infrastructure of the Internet, Internet Protocol version 4 (IPv4).",
        f"In contrast to IPv4, which defined an IP address as a 32-bit value, IPv6 addresses have a size of 128 bits.",
        f"Therefore, in comparison, IPv6 has a vastly enlarged address space.",
        f"An example of an IPv6 address is: `2001:0db8:85a3:0000:0000:8a2e:0370:7334`.",
        f"### Name",
        f"A hostname is a label that is assigned to a device connected to a computer network",
        f"and that is used to identify the device in various forms of electronic communication,",
        f"such as the World Wide Web.",
        f"Hostnames may be simple names consisting of a single word or phrase, or they may be structured.",
        f"#### DNS",
        f"Internet hostnames may be a Domain Name System (DNS) domain.",
        f"In this case, a hostname is also called a domain name.",
        f"This name is tightly linked to DNS, but for devices which have not registered an IP with a name on a DNS server, it simply asks them or the router for their name;",
        f"this is especially applicable for devices within a LAN.",
        f"An example of a hostname: `en.wikipedia.org` (from DNS), or `DESKTOP-0123AB` (not DNS).",
        f"## Special Information",
        f"**Each network entity might have more information, that can be discovered or concluded from the scans.**",
        f"**It's also displayed in the `Device Profile`.**",
        f"### Role",
        f"Some entities in a network have a special role.",
        f"One of them is `here` -- the device you're running the software from.",
        f"The other is `router` -- A default gateway is the node in a computer network that serves as the forwarding host to other networks, usually including the WWW.",
        f"### OS",
        f"An operating system is system software that manages computer hardware and software resources,",
        f"and provides common services for computer programs.",
        f"Examples of operating systems are: `Windows`, `Android`, `Unix`, `Linux`, `iOS`, `ChromeOS`, `macOS`.",
        f"Remote OS detection using _TCP/IP stack fingerprinting_, or a simplified subset thereof.",
        f"Certain parameters within the IP and TCP protocols' definitions are left up to the implementation.",
        f"Different operating systems, and different versions of the same operating system, set different defaults for these values.",
        f"By collecting and examining these values, one may differentiate among various operating systems, and implementations of TCP/IP.",
        f"The TCP/IP fields that may vary include the following:",
        f"* Initial packet size (16 bits)",
        f"* Initial TTL (8 bits)",
        f"* Window size (16 bits)",
        f"* Max segment size (16 bits)",
        f"* Window scaling value (8 bits)",
        f"* \"don't fragment\" flag (1 bit)",
        f"* \"sackOK\" flag (1 bit)",
        f"* \"nop\" flag (1 bit)",
        f"These values could be combined to form a 67-bit signature, or fingerprint, for the target machine.",
        f"Just inspecting the Initial TTL and window size fields is often enough in order to successfully identify an operating system,",
        f"which eases the task of performing manual OS fingerprinting.",
        f"### Network Card Vendor",
        f"MAC addresses are primarily assigned by device manufacturers, and are therefore often referred to as the _burned-in address_, or as an _Ethernet hardware address_, _hardware address_, or _physical address_.",
        f"Each address can be stored in hardware, such as the card's read-only memory, or by a firmware mechanism.",
        f"The first three octets identify the organization that issued the identifier and are known as the organizationally unique identifier (OUI).",
        f"This can then be mapped onto a Vendor or Manufacturer of the network card.",
        f"### Opacity",
        f"`Live ICMP` enables the calculation of the `opacity` of a device.",
        f"A device is opaque if it's completely connected with no noise (i.e. responded to the last ping request).",
        f"A device is completely transparent if it's not responded to the last several ping requests.",
        f"Transparency in-between is calculated using a probablity-based equation,",
        f"which factors in the chance for noise as well, by a history of the last 60 (usually) ping responses.",
        f"### ARP Cache Entry Type",
        f"An _ARP Cache_ is a collection of Address Resolution Protocol entries",
        f"that are created when an IP address is resolved to a MAC address (so the computer can effectively communicate with the IP address).",
        f"There are two types of ARP entries: `static` and `dynamic`.",
        f"A dynamic ARP entry (the Ethernet MAC to IP address link) is kept on a device for some period of time,",
        f"as long as it is being used.",
        f"The opposite of a dynamic ARP entry is static ARP entry.",
        f"With a static ARP entry, you are manually entering the link between the Ethernet MAC address and the IP address.",
        f"Because of management headaches and the lack of significant negatives to using dynamic ARP entries,",
        f"dynamic ARP entries are used most of the time.",
        f"Oftentimes, a `broadcast` address is placed as a `static`,",
        f"whereas links regarding real devices on the network are stored as dynamic ARP entries.",
        f"The ARP Cache, alongside the stateless nature of ARP,",
        f"is sometimes explioted by hackers to preform an `ARP Spoofing` attack on a device.",
        f"### Discovery",
        f"This software enables the action of `Reveal Myself`.",
        f"You may see an explnation of how it works on its information panel.",
        f"Here, you will see the results of the `Discovery` process, i.e. the name that was chosen by the remote device that revealed itself.",
        f"### Open TCP Ports",
        f"#### TCP",
        f"Transmission Control Protocol (TCP) is one of the main protocols of the Internet protocol suite (IP/TCP).",
        f"It provides reliable, ordered, and error-checked delivery of a stream of octets between applications running on hosts communicating.",
        f"Major internet applications such as the World Wide Web, email, remote administration, and file transfer rely on TCP,",
        f"which is part of the Transport Layer of the TCP/IP suite, or layer 4 of the OSI model.",
        f"#### TCP Ports",
        f"A _port_ is a (usually 16-bit) number assigned to uniquely identify a connection endpoint and to direct data to a specific service.",
        f"At the software level, within an OS, a port is a logical construct to indentify a specific process or a type of network service.",
        f"#### Open / Closed TCP Ports",
        f"The term _open port_ is used to mean a TCP or UDP port number that is configured to accept packets.",
        f"In contrast, a port which rejects connections or ignores all packets directed at it is called a closed port."
    ])


if __name__ == '__main__':
    print("This file is responsible for any methods called by the Information Button (ℹ) in Scan Screen and in Know Screen.")
