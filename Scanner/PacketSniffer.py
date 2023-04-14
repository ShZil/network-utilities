from import_handler import ImportDefence
from typing import TypeVar, Any, GenericAlias, ClassVar
import sys
_T = TypeVar("_T")
_S = TypeVar("_S")
with ImportDefence():
    from scapy.all import AsyncSniffer, IP
    import sqlite3
    import pickle
    from typing_extensions import Self, SupportsIndex
    from collections.abc import Callable, Iterable, Iterator


class ListWithSQL:
    CREATE = '''CREATE TABLE IF NOT EXISTS ? (id INTEGER PRIMARY KEY AUTOINCREMENT, item BLOB)'''
    INSERT = "INSERT INTO {} (item) VALUES (?)"
    def __init__(self, path: str, table_name: str, maxram: int = 100):
        self.path = path
        self.tablename = table_name
        self.ram = list()
        self.length = 0
        self.maxram = maxram

        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(ListWithSQL.CREATE, (self.tablename,))
            conn.commit()

    
    def copy(self):
        copied = ListWithSQL(self.path, self.tablename + "_copy", self.maxram)
        for item in self:
            copied.append(item)
        return copied

    def append(self, __object: _T) -> None:
        self.ram.append(__object)
        self.length += 1
        if len(self.ram) >= self.maxram:
            self._flush_to_sql()
    
    def _flush_to_sql(self) -> None:
        to_database = [(pickle.dumps(p),) for p in self.ram]
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.executemany(ListWithSQL.INSERT.format(self.tablename), to_database)
            conn.commit()
        self.ram = []
    
    def extend(self, __iterable: Iterable[_T]) -> None:
        for item in __iterable:
            self.append(item)
    
    def pop(self, __index: SupportsIndex = -1) -> _T:
        raise NotImplementedError("I don't think you should pop elements from a ListWithSQL.")

    def index(self, __value: _T, __start: SupportsIndex = 0, __stop: SupportsIndex = sys.maxsize) -> int:
        if __start < 0:
            __start += self.length
        if __stop < 0:
            __stop += self.length
        if __start < 0:
            __start = 0
        if __stop > self.length:
            __stop = self.length

        for i in range(__start, __stop):
            item = self[i]
            if item == __value:
                return i
        else:
            raise ValueError(f"{__value} is not in list")
    
    def count(self, __value: _T) -> int:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            row = cursor.execute('SELECT COUNT(item) FROM ? WHERE item = ?', (self.tablename, pickle.dumps(__value),)).fetchone()
            return row[0] + self.ram.count(__value)

    def insert(self, __index: SupportsIndex, __object: _T) -> None:
        raise NotImplementedError("Inserting manually is not supported for ListWithSQL. Please use `append` instead.")
    
    def remove(self, __value: _T) -> None:
        raise NotImplementedError("I don't think you should remove elements from a ListWithSQL.")
    
    def sort(self: list, *, key: None = None, reverse: bool = False) -> None:
        raise NotImplementedError("Sorting is not supported for ListWithSQL. Please use `__iter__` and sort manually instead.")
    
    def __len__(self) -> int:
        return self.length
    
    def __iter__(self) -> Iterator[_T]:
        for i in range(self.length):
            yield self[i]
        
    __hash__: ClassVar[None]  # type: ignore[assignment]
    def __getitem__(self, __i: SupportsIndex) -> _T:
        row = None
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            row = cursor.execute('SELECT item FROM ? WHERE id = ?', (self.tablename, __i,)).fetchone()
        if row:
            return pickle.loads(row[0])
        else:
            return self.ram[__i - len(self) + len(self.ram)]
    
    def __setitem__(self, __key: SupportsIndex, __value: _T) -> None: ...
    
    def __delitem__(self, __key: SupportsIndex | slice) -> None:
        raise NotImplementedError("I don't think you should remove (__delitem__) elements from a ListWithSQL.")
    
    def __add__(self, __value: list[_T]) -> list[_T]: ...
    def __add__(self, __value: list[_S]) -> list[_S | _T]: ...
    def __iadd__(self, __value: Iterable[_T]) -> Self: ...  # type: ignore[misc]
    def __mul__(self, __value: SupportsIndex) -> list[_T]: ...
    def __rmul__(self, __value: SupportsIndex) -> list[_T]: ...
    def __imul__(self, __value: SupportsIndex) -> Self: ...
    def __contains__(self, __key: object) -> bool: ...
    def __reversed__(self) -> Iterator[_T]: ...
    def __gt__(self, __value: list[_T]) -> bool: ...
    def __ge__(self, __value: list[_T]) -> bool: ...
    def __lt__(self, __value: list[_T]) -> bool: ...
    def __le__(self, __value: list[_T]) -> bool: ...
    def __class_getitem__(cls, __item: Any) -> GenericAlias: ...


class PacketSniffer:
    _instance = None
    DB_PATH = 'packets.db'
    SQL_CREATE_TABLE = '''CREATE TABLE IF NOT EXISTS packets (id INTEGER PRIMARY KEY AUTOINCREMENT, packet BLOB, proto TEXT, src TEXT, dst TEXT, ttl INTEGER, flags TEXT, options BLOB, timestamp INTEGER)'''
    INSERT_STATEMENT = "INSERT INTO packets(packet, proto, src, dst, ttl, flags, options, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    CLEAR_TABLE = '''DELETE FROM packets;'''

    def __new__(cls, max_packets=100):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.max_packets = max_packets
            cls._instance.packets = []
            cls._instance.sniff_thread = AsyncSniffer(prn=cls._instance._packet_handler, lfilter=cls._instance._ip_filter)
            cls._instance.sniff_thread.start()
            cls._instance.length = 0
        return cls._instance

    def __init__(self, max_packets=100):
        self.max_packets = max_packets
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(self.SQL_CREATE_TABLE)
            cursor.execute(self.CLEAR_TABLE)

    def stop(self):
        if self.sniff_thread:
            self.sniff_thread.stop()
            self.sniff_thread = None

        self._flush_packets()

    def get_packet(self, i: int):
        packet_row = None
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            packet_row = cursor.execute('SELECT packet FROM packets WHERE id = ?', (i,)).fetchone()
        return pickle.loads(packet_row[0]) if packet_row else None


    def _packet_handler(self, packet):
        from time import time as now
        if IP in packet:
            fields = packet[IP].fields
            self.packets.append({'packet': packet, **fields, 'timestamp': int(now())})
            self.length += 1
            if len(self.packets) >= self.max_packets:
                self._flush_packets()
    
    def __len__(self):
        return self.length

    def _flush_packets(self):
        packets_to_insert = [(pickle.dumps(p['packet']), p['proto'], p['src'], p['dst'], int(p['ttl']), str(p['flags']), pickle.dumps(p['options']), int(p['timestamp'])) for p in self.packets]

        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.executemany(PacketSniffer.INSERT_STATEMENT, packets_to_insert)
            try:
                conn.commit()
            except sqlite3.OperationalError:
                return
        self.packets = []

    def _ip_filter(self, packet):
        return IP in packet
    
    def __iter__(self):
        packets = self.packets.copy()

        # Yield all packets from the SQL database
        for i in range(self.length - len(packets)):
            packet = self.get_packet(i)
            if packet is None:
                break
            yield packet

        # Yield all the packets from the `self.packets` (but `copy()`ied earlier).
        for packet in packets:
            yield packet['packet']


if __name__ == '__main__':
    print("This module contains the PacketSniffer class.")
    import time
    packet_sniffer = PacketSniffer(max_packets=40)
    time.sleep(5)
    print(f"{len(packet_sniffer)} packet(s) were sniffed.")
    for packet in packet_sniffer:
        print(packet)
    packet_sniffer.stop()
