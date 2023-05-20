from util import threadify
from import_handler import ImportDefence
with ImportDefence():
    import sqlite3
    import requests
    from threading import Lock


class MACVendorDict:
    _instance = None
    path = 'mac_vendors.db'
    CREATE_QUERY = '''CREATE TABLE IF NOT EXISTS mac_vendors (mac TEXT PRIMARY KEY, text TEXT)'''
    SELECT_QUERY = 'SELECT text FROM mac_vendors WHERE mac=?'
    INSERT_QUERY = 'INSERT INTO mac_vendors (mac, text) VALUES (?, ?)'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lock = Lock()
            with sqlite3.connect(cls.path) as conn:
                cursor = conn.cursor()
                cursor.execute(cls.CREATE_QUERY)
        return cls._instance

    def __contains__(self, mac):
        with self.lock, sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(self.SELECT_QUERY, (mac,))
            return cursor.fetchone() is not None

    def __setitem__(self, mac, text):
        with self.lock, sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(self.INSERT_QUERY, (mac, text))
            conn.commit()

    def __getitem__(self, mac):
        with self.lock, sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(self.SELECT_QUERY, (mac,))
            result = cursor.fetchone()
        return result[0] if result else None

    def get(self, mac, default=None):
        return self[mac] if mac in self else default



def vendor_mapper(mac):
    if mac in MACVendorDict():
        return
    response = requests.get(f'https://www.macvendorlookup.com/api/v2/{mac}')
    if response.status_code != 200:
        return
    vendor = response.text
    MACVendorDict()[mac] = vendor
    return vendor


@threadify
def mapper_wrapper(entity):
    from NetworkStorage import nothing, SpecialInformation
    if entity.mac == nothing.mac:
        return
    vendor = vendor_mapper(entity.mac)
    if vendor is None:
        return
    SpecialInformation()[entity, 'Network Card Vendor'] = vendor


def vendor_mapping():
    from NetworkStorage import NetworkStorage
    MACVendorDict()
    mapper_wrapper(list(NetworkStorage()))


if __name__ == '__main__':
    print("This analysis uses an API to map MAC physical network card address,")
    print("to a vendor / manufacturer according to the organizationally unique identifier (OUI) found in the start of the MAC address,")
    print("using https://www.macvendorlookup.com/api/v2 API.")
    print("Saves a cache using SQL to `mac_vendors.db`.")
