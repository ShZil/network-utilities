from import_handler import ImportDefence
with ImportDefence():
    import re
    import ipaddress

class NetworkEntity:
    def __init__(self, mac, ip, ipv6, name):
        self.mac = standard_mac(mac)
        self.ip = check_ip(ip)
        self.ipv6 = extend_ipv6(ipv6)
        self.name = name
    
class NetworkStorage:
    data = []

    def add(self, *args, mac=nothing.mac, ip=nothing.ip, ipv6=nothing.ipv6, name=nothing.name):
        entity = NetworkEntity(mac, ip, ipv6, name)
        self.data.append(entity)
