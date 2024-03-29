from import_handler import ImportDefence
with ImportDefence():
    from subprocess import CalledProcessError, check_output as read_command, DEVNULL

    from socket import gethostbyaddr as hostify_base
    from socket import herror as hostify_error1
    from socket import gaierror as hostify_error2

from CacheDecorators import memorise
from PrintingContexts import NoPrinting
from util import threadify


@memorise
def hostify(address: str) -> str:
    """This function turns an IPv4 address to a host name using one of these methods:
    1. Calling `>nslookup` with that address. If that fails,
    2. Using `socket.gethostbyaddr` function. If that fails,
    3. Returns "Unknown" since all the methods failed.

    Args:
        address (str): the IPv4 address to turn into a host.

    Returns:
        str: the host name.
    """
    host = "Unknown"

    def use_hostify_base(address: str) -> str:
        """Uses `socket.gethostbyaddr` to resolve a name.
        If errors occur, returns "Unknown".

        Args:
            address (str): an IP address.

        Returns:
            str: the host name for that address.
        """
        try:
            # print("Method: socket.gethostbyaddr", end=' -- ')
            return hostify_base(address)[0]
        except (hostify_error1, hostify_error2):
            return "Unknown"

    # First method -> nslookup
    # If first method failed, second method -> socket.gethostbyaddr
    try:
        with NoPrinting():
            lines = read_command(['nslookup', address], stderr=DEVNULL).decode(
                encoding='utf-8', errors='ignore').split('\n')
        for line in lines:
            if line.strip().startswith('Name:'):
                host = line[len("Name:"):].strip()
                # print("Method: nslookup", end=' -- ')
                break
        else:
            host = use_hostify_base(address)
    except CalledProcessError:
        host = use_hostify_base(address)
    # print("Hostified:", host)
    return host


hostify_sync = threadify(hostify, silent=True)
