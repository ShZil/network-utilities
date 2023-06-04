from import_handler import ImportDefence
with ImportDefence():
    from typing import Callable, Union

from ipconfig import ipconfig


def do_simple_scan(scan: Callable, all_possible_addresses: list[str], *, results=False, repeats=3) -> list[str]:
    """This is a wrapper for simple* scans, like ARP or ICMP.

    (*) Simple means they are standardised:
    [X] Have been @threadify-ied.
    [X] Get list[str] of IPv4 addresses as input (post-threadify).
    [X] Output list[bool] indicating online-ness of the addresses (index-correlated) (post-threadify).

    Note: index-correlatedness, lists as input, and lists as output are handled by @threadify.
    The requirements for the base function are just that it's of the form: `scan: str (IPv4 address) -> bool (connectivity)`.


    Args:
        scan (function): a @threadify-ied method from list[str] all_possible_addresses -> list[bool] online.
        all_possible_addresses (list[str]): a list of IPv4 to test connectivity to.
        results (bool, optional): Decides whether to print the results. Defaults to True.
        repeats (int, optional): How many times should the full-range of addresses be scanned? Defaults to 3.

    Returns:
        list[str]: the addresses which replied, at least once, to the scan.
    """
    # if the amount of repeats is non-positive, the result is always empty.
    if repeats < 1:
        return []

    # Parsing the title & protocol.
    title = scan.__name__
    protocol = "".join(char for char in title if char.isupper())

    # Define a <lambda> that returns a list[str] of connectable addresses.
    def get_new():
        """
        The get_new function scans all possible addresses and returns a list of
        addresses that are online.
        This is a wrapper around `scan`.

        Returns:
            list[str]: A list of addresses that are online
        """
        return [
            address for address, online
            in zip(all_possible_addresses, scan(all_possible_addresses))
            if online
        ]

    # Call it `repeats` times and unite all results into a set.
    connectable_addresses = set()
    for _ in range(repeats):
        connectable_addresses = connectable_addresses.union(get_new())

    # Turn it into a sorted list (just for convenience, order doesn't matter).
    connectable_addresses = sorted(
        connectable_addresses,
        key=lambda x: int(''.join(x.split('.')))
    )

    # Print if asked
    if results:
        print(
            "There are",
            len(connectable_addresses),
            protocol,
            "connectable addresses in this subnet:"
        )
        print('    ' + '\n    '.join(connectable_addresses))

    return connectable_addresses


def standardise_simple_scans(scans: list[Union[tuple[Callable, int], Callable]]) -> list[Callable]:
    """This function standardises a collection of simple scans.
    The argument is a list of tuples, where each tuple has two items:
    (1) The scan (Callable), (2) The amount of repeats.

    If a Callable is provided instead of a tuple,
    it takes the default value of 1 repeat.

    If a non-positive (i.e. negative or zero) amount of repeats is provided,
    the scan is ignored.

    It returns a list of actions, provided by `does_simple_scan`,
    with updated names and docstrings.
    `does_simple_scan` is a wrapper around `do_simple_scan`,
    that provides the arguments: scan, ipconfig()["All Possible Addresses"], and repeats.

    Args:
        scans (list[tuple[Callable, int] + Callable]): a list of the scans.

    Returns:
        list[Callable]: a list of the actions -- scans times repeats.
    """
    # If `repeats` is not provided, default it to 1.
    scans = [scan if isinstance(scan, tuple) else (scan, 1) for scan in scans]
    # Filter only scans with a positive amount of repeats.
    scans = [scan for scan in scans if scan[1] > 0]

    # Wrapper around `do_simple_scan`, that provides the wanted arguments and returns a <lambda>.
    def does_simple_scan(scan):
        """
        The does_simple_scan function takes a scan and returns a function that will perform the scan.
        This is a wrapper around `do_simple_scan` that provides the wanted arguments.

        Args:
            scan (callable): the scan to wrap.

        Returns:
            callable: the wrapped function.
        """
        scan, repeats = scan
        return (
            lambda: do_simple_scan(
                scan,
                ipconfig()["All Possible Addresses"],
                repeats=repeats)
        )
    lambdas = [does_simple_scan(scan) for scan in scans]

    # Handle all the __name__s and __doc__s.
    for (scan, repeats), method in zip(scans, lambdas):
        prefix = f"{repeats} × " if repeats > 1 else ""
        method.__name__ = prefix + scan.__name__
        method.__doc__ = prefix + scan.__doc__
    return lambdas


def simple_scan(scan: Callable, repeats: int) -> Callable:
    """Wrapper around `do_simple_scan`,
    that handles the `__name__` and `__doc__`.

    Args:
        scan (Callable): the scan to standardise and repeat.
        repeats (int): the amount of repeats.

    Returns:
        Callable: a standardised simple scan.
    """
    def result():
        """
        The result function is a wrapper for the do_simple_scan function.
        It takes in the scan function, and all possible addresses from ipconfig().
        The result is returned by `do_simple_scan`, so this is a wrapper around it.

        Returns:
            list[tuple]: A list of tuples containing the sacns and repeats.
        """
        return do_simple_scan(scan,
                              ipconfig()["All Possible Addresses"],
                              repeats=repeats)
    prefix = f"{repeats} × " if repeats > 1 else ""
    result.__name__, result.__doc__ = prefix + scan.__name__, prefix + scan.__doc__
    return result


if __name__ == '__main__':
    print("This module is responsible for the conceptual type called Simple Scan.")
    print("It represents a scan that answers a list of criteria:")
    print("[X] Have been @threadify-ied.")
    print("[X] Get list[str] of IPv4 addresses as input (post-threadify).")
    print("[X] Output list[bool] indicating online-ness of the addresses (index-correlated) (post-threadify).")
    print("\nNote: index-correlatedness, lists as input, and lists as output are handled by @threadify.")
    print("The requirements for the base function are just that it's of the form: `scan: str (IPv4 address) -> bool (connectivity)`.")
