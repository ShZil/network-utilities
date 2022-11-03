class NetworkStorage:
    data = []

    def add(self, *args, mac=nothing.mac, ip=nothing.ip, ipv6=nothing.ipv6, name=nothing.name):
        entity = NetworkEntity(mac, ip, ipv6, name)
        self.data.append(entity)
