from import_handler import ImportDefence
with ImportDefence():
    from scapy.all import AsyncSniffer, IP
    import sqlite3
    import pickle


class PacketSniffer:
    def __init__(self, max_packets=100):
        self.db_conn = sqlite3.connect('packets.db')
        self.db_cursor = self.db_conn.cursor()
        self.max_packets = max_packets
        self.packets = []

        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS packets (id INTEGER PRIMARY KEY AUTOINCREMENT, packet BLOB, proto TEXT, src TEXT, dst TEXT, ttl INT, flags TEXT, options BLOB)''')
        self.sniff_thread = AsyncSniffer(prn=self._packet_handler, filter=self._ip_filter)

        self.sniff_thread.start()

    def stop(self):
        if self.sniff_thread:
            self.sniff_thread.stop()
            self.sniff_thread = None

        self._flush_packets()

        self.db_cursor.close()
        self.db_conn.close()

    def get_packet(self, i: int):
        packet_row = self.db_cursor.execute('SELECT packet FROM packets WHERE id = ?', (i,)).fetchone()
        return pickle.loads(packet_row[0]) if packet_row else None

    def get_packets(self, src=None, dst=None):
        # Set default values to match any IP address
        if src is None:
            src = '%.%.%.%'
        if dst is None:
            dst = '%.%.%.%'

        # Retrieve packets from SQL
        query = "SELECT * FROM packets WHERE src LIKE ? AND dst LIKE ?"
        self.cursor.execute(query, (src, dst))
        rows = self.cursor.fetchall()

        # Decode and return pickled packets from SQL
        packets = [pickle.loads(row[1]) for row in rows]

        # Add packets from list that match the filter
        for packet in self.packets:
            if (src == '%.%.%.%' or packet['src'] == src) and (dst == '%.%.%.%' or packet['dst'] == dst):
                packets.append(packet['packet'])

        return packets


    def _packet_handler(self, packet):
        if IP in packet:
            fields = packet[IP].fields
            self.packets.append({'packet': packet, **fields})
            if len(self.packets) >= self.max_packets:
                self._flush_packets()

    def _flush_packets(self):
        packets_to_insert = [(pickle.dumps(p['packet']), *p.values()) for p in self.packets]
        self.db_cursor.executemany("INSERT INTO packets(packet, proto, src, dst, ttl, flags, options) VALUES (?, ?, ?, ?, ?, ?, ?)", packets_to_insert)
        self.db_conn.commit()
        self.packets = []

    def _ip_filter(self, packet):
        return IP in packet
