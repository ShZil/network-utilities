from util import threadify
from import_handler import ImportDefence
with ImportDefence():
    import sqlite3
    import requests
    from threading import Lock


class MACVendorDict:
    _instance = None
    path = 'mac_vendors.db'
    CREATE_QUERY = '''CREATE TABLE IF NOT EXISTS mac_vendors (mac TEXT PRIMARY KEY, vendor TEXT)'''
    SELECT_QUERY = 'SELECT vendor FROM mac_vendors WHERE mac=?'
    INSERT_QUERY = 'INSERT INTO mac_vendors (mac, vendor) VALUES (?, ?)'

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
        """Get a vendor without KeyError (use `default` if the key is not found).

        Args:
            mac (str): the MAC address to map.
            default (str, optional): the value to return if the key is not found. Defaults to None.

        Returns:
            str | NoneType: the vendor if it is found.
        """
        return self[mac] if mac in self else default


def vendor_mapper(mac):
    """
    The vendor_mapper function takes a MAC address as an argument and returns the vendor of that MAC address.
    The function uses the requests library to make a GET request to hwaddress.com.

    Args:
        mac (str): the MAC address to map to a vendor.

    Returns:
        str: the vendor
    """
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


def mapper_wrapper(entity):
    """
    The mapper_wrapper function is a wrapper for the vendor_mapper function.
    It takes an entity as input, and returns nothing.
    The purpose of this function is to map MAC addresses to vendors, and store that information in the SpecialInformation dictionary.

    Args:
        entity (NetworkEntity): the entity to map the MAC address thereof.
    """
    from NetworkStorage import nothing, SpecialInformation
    if entity.mac == nothing.mac:
        return
    if entity.mac in MACVendorDict():
        SpecialInformation()[entity, 'Network Card Vendor'] = MACVendorDict()[entity.mac]
        return
    try:
        vendor = vendor_mapper(entity.mac)
    except IndexError:
        return
    if vendor is None:
        return
    MACVendorDict()[entity.mac] = vendor  # I could save just the first 3 bytes, but, sometimes the OUI extends further, so I'd rather save the entire MAC.
    SpecialInformation()[entity, 'Network Card Vendor'] = vendor


def vendor_mapping(*_):
    """
    The vendor_mapping function is a wrapper for the mapper_wrapper function.
    It takes no arguments, but it does call the MACVendorDict and NetworkStorage classes (which are both Singletons).
    The MACVendorDict creates a dictionary of all known vendors and their associated OUI's (Organizationally Unique Identifiers) -- this is a cache.
    The NetworkStorage function returns a list of all devices on your network that have been detected.

    This is the entry point of the Vendor Mapping analysis.
    """
    from NetworkStorage import NetworkStorage
    MACVendorDict()
    for entity in list(NetworkStorage()):
        mapper_wrapper(entity)


if __name__ == '__main__':
    print("This analysis uses an API to map MAC physical network card address,")
    print("to a vendor / manufacturer according to the organizationally unique identifier (OUI) found in the start of the MAC address,")
    print("using `hwaddress.com`.")
    print("Saves a cache using SQL to `mac_vendors.db`.")
