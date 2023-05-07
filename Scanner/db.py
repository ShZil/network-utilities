from import_handler import ImportDefence
with ImportDefence():
    import sqlite3

CREATE_INFORMATION_TABLE = """CREATE TABLE IF NOT EXISTS `information` (
    `name` VARCHAR(49) NOT NULL,
    `Description` TEXT,
    `Time` FLOAT,
    `Reward` VARCHAR(100),
    `Certainty` TINYINT unsigned,
    `Safety` TINYINT unsigned,
    `Mode` INT,
    `repeats` BOOLEAN,
    PRIMARY KEY (`name`)
);"""
INSERT_INFORMATION = "INSERT INTO information VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
GET_ALL_SCANS = "SELECT name FROM information WHERE mode=1"
GET_ALL_ANALYSES = "SELECT name FROM information WHERE mode=0"
SELECT_SPECIFIC_SCAN = "SELECT * FROM information WHERE name=?"
PATH = "scans.db"
INFORMATION_DATA = [
    # name: str, description: longstr, time: float, reward: str, certainty: int, safety: int, mode: int, repeats: bool
    # NOTE: `mode` is reserved for future use.
    # ("", "", 0.1, "", 0, 0, 0, True),
    ("ICMP Sweep", "Sends a ping-echo-request packet, using the ICMP protocol, to all IP addresses in the local network. <IP dst=addresses_in_network> <ICMP type=8 (echo-request)>", 13, "IP Addresses of Active Devices", 75, 30, 1, True),
    ("ARP Sweep", "Sends a who-has packet, using the ARP protocol, to all IP addresses in the local network. <Ether> <ARP pdst=addresses_in_network op=1 (who-has)>", 9, "MAC & IP addresses of active devices", 95, 10, 1, True),
    ("Live ICMP", "Continually sends ping-echo-request packets, using the ICMP protocol, in two channels:\n* Discovery -- to find new devices;\n* Connection -- to check whether the known devices have disconnected. <IP dst=addresses_in_network/known_addreses> <ICMP type=8 (echo-request)>", 0, "IP and Connection Status of Devices", 80, 40, 1, False),
    ("Live ARP", "**Step 1:** executes `arp -a` to see which addresses are already saved on the device's lookup table.\n**Step 2:** Listens indefinitely to who-has/is-at packets, using the ARP protocol.\nCompletely silent -- sends no packets, just reads those that are received. <Ether> <ARP op=1 (who-has) or op=2 (is-at)>", 0, "MAC & IP addresses of active devices", 99, 100, 1, False),
    ("OS-ID", "Identifies the Operating System (OS) of all known devices. This uses techniques called TCP/IP stack fingerprinting, and inspects the IP:TTL and TCP:window. This is very close to guessing, so be doubtful of the results.\nIt sends no packets by itself (i.e. it's safe),\nbut looks at the packets received from other (possibly unsafe) scans, or any packets that were sniffed silently.", 0, "Probable Operating System of devices", 30, 100, 1, False),
    ("TCP Ports", "Transmission Control Protocol (TCP) Half-Open Port Scan. A usual TCP 3-way handshake is (SYN) - (SYN+ACK) - (ACK); this scan sends a SYN packet, and waits for a SYN+ACK packet, but never completes the handshake. <IP dst=specific_ip> <TCP SYN>", 33, "Open/Reset/Closed TCP ports on a device", 90, 80, 1, True),
    ("UDP Ports", "User Datagram Protocol (UDP) Scanning, can detect some closed ports, because they will respond with an ICMP Port Unreachable error packet. <IP dst=specific_ip> <UDP> -> <IP> <ICMP type=3 (unreachable)>", 0.1, "", 0, 0, 1, True),
    ("woo!", "", 0.1, "", 0, 0, 1, True),
    ("Public Address", "Gets the outside IP address of the router, using `https://api.ipify.org`. <IP> <TCP> <HTTPS GET / HTTP/2 [Host: api.ipify.org]>", 1.3, "Public IP address of the router", 97, 90, 1, True),
    ("Traceroute", "Using ICMP and IP:ttl, find the route to a distant device.", 0.1, "IP addresses of all devices in the route", 0, 0, 1, True),
    ("Log Packets", "Log all the packets that were silently sniffed.", 0, "The packets are already saved, you're just viewing them.", 99, 100, 0, True),
    ("Device Profile", "Log all the packets that were silently sniffed.", 0, "The packets are already saved, you're just viewing them.", 99, 100, 0, True)
]


def get_information_about_scan(name: str):
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()
    try:
        cursor.execute(SELECT_SPECIFIC_SCAN, (name, ))
    except sqlite3.OperationalError:
        raise FileNotFoundError("SQL table 'information' was not found.")
    result = cursor.fetchone()
    connection.close()
    return result


def get_scans():
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()
    try:
        cursor.execute(GET_ALL_SCANS)
    except sqlite3.OperationalError:
        raise FileNotFoundError("SQL table 'information' was not found.")
    # a list of tuples is returned, where each tuple has only a string within
    # (at index 0).
    result = cursor.fetchall()
    # Convert it to a list of strings. list[tuple[single str]] -> list[str]
    result = [item[0] for item in result]
    connection.close()
    return result


def get_analyses():
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()
    try:
        cursor.execute(GET_ALL_ANALYSES)
    except sqlite3.OperationalError:
        raise FileNotFoundError("SQL table 'information' was not found.")
    # a list of tuples is returned, where each tuple has only a string within
    # (at index 0).
    result = cursor.fetchall()
    # Convert it to a list of strings. list[tuple[single str]] -> list[str]
    result = [item[0] for item in result]
    connection.close()
    return result


def init():
    connection = sqlite3.connect(PATH)
    cursor = connection.cursor()
    try:
        cursor.execute(CREATE_INFORMATION_TABLE)
        cursor.executemany(INSERT_INFORMATION, INFORMATION_DATA)
    except sqlite3.OperationalError:
        print("An error occured.")
        raise
    except sqlite3.IntegrityError:
        print("Unique constaint failed.")
    connection.commit()
    connection.close()


if __name__ == '__main__':
    init()
    print(get_information_about_scan('ICMP Sweep'))
    print(get_scans())
    print(get_analyses())
