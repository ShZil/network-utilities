from import_handler import ImportDefence
with ImportDefence():
    from scapy.all import AsyncSniffer, IP
    import sqlite3
    import pickle


class PacketSniffer:
    _instance = None
    DB_PATH = 'packets.db'
    SQL_CREATE_TABLE = '''CREATE TABLE IF NOT EXISTS packets (id INTEGER PRIMARY KEY AUTOINCREMENT, packet BLOB, proto TEXT, src TEXT, dst TEXT, ttl INT, flags TEXT, options BLOB)'''

    def __new__(cls, max_packets=100):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._db_conn = sqlite3.connect(cls.DB_PATH)
            cls._instance._db_cursor = cls._instance._db_conn.cursor()
            cls._instance._max_packets = max_packets
            cls._instance._packets = []
            cls._instance._db_cursor.execute(cls.SQL_CREATE_TABLE)
            cls._instance._sniff_thread = AsyncSniffer(prn=cls._instance._packet_handler, filter=cls._instance._ip_filter)
            cls._instance._sniff_thread.start()
        return cls._instance

    def __init__(self):
        pass

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


if __name__ == '__main__':
    print("This module contains the PacketSniffer class.")
    import time
    packet_sniffer = PacketSniffer()
    time.sleep(5)
    packets = packet_sniffer.get_packets()
    print(packets)
    packet_sniffer.stop()
