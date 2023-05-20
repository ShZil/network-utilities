from import_handler import ImportDefence
with ImportDefence():
    import requests


import sqlite3
import requests

class MACVendorDict:
    _instance = None
    _db_file = 'mac_vendors.db'
    CREATE_QUERY = '''CREATE TABLE IF NOT EXISTS mac_vendor (mac TEXT PRIMARY KEY, text TEXT)'''
    SELECT_QUERY = 'SELECT text FROM mac_vendor WHERE mac=?'
    INSERT_QUERY = 'INSERT INTO mac_vendor (mac, text) VALUES (?, ?)'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = sqlite3.connect(cls._db_file)
            cls._instance.c = cls._instance.conn.cursor()
            cls._instance.c.execute(cls.CREATE_QUERY)
        return cls._instance

    def __contains__(self, mac):
        self.c.execute(self.SELECT_QUERY, (mac,))
        return self.c.fetchone() is not None

    def __setitem__(self, mac, text):
        self.c.execute(self.INSERT_QUERY, (mac, text))
        self.conn.commit()

    def __getitem__(self, mac):
        self.c.execute(self.SELECT_QUERY, (mac,))
        result = self.c.fetchone()
        return result[0] if result else None

    def get(self, mac, default=None):
        return self[mac] if mac in self else default


def vendor_mapping(mac):
    from NetworkStorage import SpecialInformation, match
    if mac in MACVendorDict():
        return MACVendorDict()[mac]
    response = requests.get(f'https://www.macvendorlookup.com/api/v2/{mac}')
    if response.status_code != 200:
        return
    vendor = response.text
    MACVendorDict()[mac] = vendor
    SpecialInformation()[match(mac), 'Network Card Vendor'] = vendor


if __name__ == '__main__':
    print("This analysis uses an API to map MAC physical network card address,")
    print("to a vendor / manufacturer according to the organizationally unique identifier (OUI) found in the start of the MAC address,")
    print("using https://www.macvendorlookup.com/api/v2 API.")
