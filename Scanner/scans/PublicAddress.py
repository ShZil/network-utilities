from import_handler import ImportDefence
with ImportDefence():
    import requests

from NetworkStorage import NetworkStorage
from CacheDecorators import one_cache


def public_address_action():
    NetworkStorage().add(get_public_ip())


@one_cache
def get_public_ip():
    from NetworkStorage import nothing, NetworkStorage, LockedNetworkEntity
    ip = requests.get('https://api.ipify.org').text
    ipv6 = requests.get('https://api64.ipify.org').text
    ipv6 = ipv6 if ipv6 != ip else nothing.ipv6
    try:
        outside = LockedNetworkEntity(
            mac=nothing.mac,
            ip=ip,
            ipv6=ipv6,
            name="Public Address"
        )
    except ValueError:  # api64.ipify.org might not return the IPv6, and instead say "gateway timeout"
        outside = LockedNetworkEntity(
            mac=nothing.mac,
            ip=ip,
            ipv6=nothing.ipv6,
            name="Public Address"
        )
    NetworkStorage().special_add(outside)
    return outside


if __name__ == '__main__':
    print("This scan-like action fetches the public IP of the router,")
    print("using https://api.ipify.org API.")
    print("It has to be act on outside the network, of course.")
