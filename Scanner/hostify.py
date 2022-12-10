from import_handler import ImportDefence
with ImportDefence():
    from util import memorise, NoPrinting, threadify
    
    from subprocess import CalledProcessError, check_output as read_command

    from socket import gethostbyaddr as hostify_base
    from socket import herror as hostify_error1
    from socket import gaierror as hostify_error2


# ************ The subprocess windows open and disturb users (aka me) / Prints the errors into the console which is annoying.
# Potential fix: https://stackoverflow.com/questions/1813872/running-a-process-in-pythonw-with-popen-without-a-console
# or https://stackoverflow.com/a/55758810
@memorise
def hostify(address: str):
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

    def use_hostify_base(address):
        try:
            return hostify_base(address)[0]
        except (hostify_error1, hostify_error2):
            return "Unknown"

    # First method -> nslookup
    # If first method failed, second method -> socket.gethostbyaddr
    try:
        with NoPrinting():
            lines = read_command(['nslookup', address]).decode(encoding='utf-8', errors='ignore').split('\n')
        for line in lines:
            if line.strip().startswith('Name:'):
                host = line[len("Name:"):].strip()
                break
        else:
            host = use_hostify_base(address)
    except CalledProcessError:
        host = use_hostify_base(address)
    return host


hostify_sync = threadify(hostify)
