from import_handler import ImportDefence
with ImportDefence():
    from scapy.all import AsyncSniffer, IP
    import sqlite3
    import pickle


class PacketSniffer:
    _instance = None
    DB_PATH = 'packets.db'
    SQL_CREATE_TABLE = '''CREATE TABLE IF NOT EXISTS packets (id INTEGER PRIMARY KEY AUTOINCREMENT, packet BLOB, proto TEXT, src TEXT, dst TEXT, ttl INTEGER, flags TEXT, options BLOB, timestamp INTEGER)'''
    INSERT_STATEMENT = "INSERT INTO packets(packet, proto, src, dst, ttl, flags, options, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    def __new__(cls, max_packets=100):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.max_packets = max_packets
            cls._instance.packets = []
            cls._instance.sniff_thread = AsyncSniffer(prn=cls._instance._packet_handler, lfilter=cls._instance._ip_filter)
            cls._instance.sniff_thread.start()
        return cls._instance

    def __init__(self, max_packets=100):
        self.max_packets = max_packets
        self.db_conn = sqlite3.connect(self.DB_PATH)
        self.cursor = self.db_conn.cursor()
        self.cursor.execute(self.SQL_CREATE_TABLE)

    def stop(self):
        if self.sniff_thread:
            self.sniff_thread.stop()
            self.sniff_thread = None

        self._flush_packets()

        self.cursor.close()
        self.db_conn.close()

    def get_packet(self, i: int):
        packet_row = self.cursor.execute('SELECT packet FROM packets WHERE id = ?', (i,)).fetchone()
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
            self.packets.append({'packet': packet, **fields, 'timestamp': int(time.time())})
            if len(self.packets) >= self.max_packets:
                self._flush_packets()

    def _flush_packets(self):
        packets_to_insert = [(pickle.dumps(p['packet']), p['proto'], p['src'], p['dst'], int(p['ttl']), str(p['flags']), pickle.dumps(p['options']), int(p['timestamp'])) for p in self.packets]

        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.executemany(PacketSniffer.INSERT_STATEMENT, packets_to_insert)
            conn.commit()
        self.packets = []

    def _ip_filter(self, packet):
        return IP in packet


if __name__ == '__main__':
    print("This module contains the PacketSniffer class.")
    import time
    packet_sniffer = PacketSniffer(max_packets=5)
    time.sleep(5)
    packets = packet_sniffer.get_packets()
    print(f"{len(packets)} packet(s) were sniffed.")
    for packet in packets:
        print(packet)
    packet_sniffer.stop()
