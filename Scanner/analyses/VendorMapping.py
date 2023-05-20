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
    try:
        url_mac = '%3A'.join(mac.replace(':', '-').split('-'))
        response = requests.get(f'https://hwaddress.com/?q={url_mac}')
    except requests.exceptions.ConnectTimeout:
        return
    if response.status_code != 200:
        return
    html = response.text
    a_tag = html.split('<tr><th>Company</th><td>')[1].split('</td></tr>')[0]
    vendor = a_tag.split('>')[1].split('<')[0]
    return vendor


@threadify
def mapper_wrapper(entity):
    from NetworkStorage import nothing, SpecialInformation
    if entity.mac == nothing.mac:
        return
    if entity.mac in MACVendorDict():
        return
    try:
        vendor = vendor_mapper(entity.mac)
    except IndexError:
        return
    if vendor is None:
        return
    MACVendorDict()[entity.mac] = vendor
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
