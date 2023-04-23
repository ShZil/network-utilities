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
    CREATE = '''CREATE TABLE IF NOT EXISTS list_with_sql (id INTEGER PRIMARY KEY AUTOINCREMENT, item BLOB)'''
    INSERT = "INSERT INTO list_with_sql (item) VALUES (?)"
    CLEAR = "DELETE FROM list_with_sql"
    RESET_AUTOINCREMENT = "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='list_with_sql'"
    def __init__(self, path: str, maxram: int = 100):
        self.path = path
        self.ram = list()
        self.length = 0
        self.maxram = maxram

        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(ListWithSQL.CREATE)
            cursor.execute(ListWithSQL.CLEAR)
            cursor.execute(ListWithSQL.RESET_AUTOINCREMENT)
            conn.commit()

    def copy(self):
        copied = ListWithSQL(self.path, "list_with_sql_copy", self.maxram)
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
            cursor.executemany(ListWithSQL.INSERT, to_database)
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
            cursor.execute(f"SELECT COUNT(*) FROM list_with_sql WHERE item=?", (pickle.dumps(__value),))
            sql_count = cursor.fetchone()[0]
        ram_count = self.ram.count(__value)
        return ram_count + sql_count

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
    def __getitem__(self, __i: SupportsIndex | slice) -> _T:
        if isinstance(__i, slice):
            return [self[j] for j in range(*__i.indices(len(self)))]

        if not (-len(self) <= __i < len(self)):
            raise IndexError("list index out of range")

        if __i < 0:
            __i += len(self)

        if __i >= len(self) - len(self.ram):
            return self.ram[__i - len(self) + len(self.ram)]

        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT item FROM list_with_sql WHERE id = ?", (__i + 1,))
            res = cursor.fetchone()
            if res is None:
                raise IndexError("list index out of range")
            return pickle.loads(res[0])

    def __setitem__(self, __key: SupportsIndex, __value: _T) -> None:
        # Convert negative indices to positive indices
        if isinstance(__key, int) and __key < 0:
            __key += len(self)

        # If index is in range of SQL data, update it in the SQL table
        if __key < len(self) - len(self.ram):
            with sqlite3.connect(self.path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE list_with_sql SET item=? WHERE id=?", (pickle.dumps(__value), __key + 1))

        # If index is in range of RAM data, update it in RAM
        elif __key < len(self):
            self.ram[__key - len(self) + len(self.ram)] = __value

        # If index is out of range, raise an IndexError
        else:
            raise IndexError('list assignment index out of range')

    def __delitem__(self, __key: SupportsIndex | slice) -> None:
        raise NotImplementedError("I don't think you should remove (__delitem__) elements from a ListWithSQL.")

    def __contains__(self, __key: object) -> bool:
        if __key in self.ram:
            return True
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM list_with_sql WHERE item=?", (pickle.dumps(__key),))
            return cursor.fetchone()[0] > 0

    def __reversed__(self) -> Iterator[_T]:
        for item in reversed(self.ram):
            yield item
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT item FROM list_with_sql ORDER BY id DESC")
            while True:
                res = cursor.fetchone()
                if res is None:
                    break
                yield pickle.loads(res[0])


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
