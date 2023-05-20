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
