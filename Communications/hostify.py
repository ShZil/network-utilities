from socket import gethostbyaddr as hostify_base
from socket import herror as hostify_error1
from socket import gaierror as hostify_error2
from threading import Thread

__author__ = 'Shaked Dan Zilberman'
lookup_hostify = {}

# Disables host viewing
disable_hostify = False

### Hostify
def hostify(address):
    """Returns the host name of an IPv4 address. Uses a cache."""
    if disable_hostify:
        return "HOST"
    global lookup_hostify
    try:
        return lookup_hostify[address]
    except KeyError:
        try:
            host = hostify_base(address)[0]
            lookup_hostify[address] = host
            return host
        except (hostify_error1, hostify_error2):
            lookup_hostify[address] = ""
            return ""


def hostify_sync(addresses):
    """Quickly add hosts of an IPv4 list to hostify cache"""
    threads = []
    for address in addresses:
        t = Thread(target=hostify, args=(address,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
