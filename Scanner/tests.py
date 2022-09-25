from main import *


def dictify_example1():
    x = 'Windows IP Configuration\n            Host Name . . . . . . . . . . . . : MyComputer-007\n            Primary Dns Suffix  . . . . . . . :\n            Node Type . . . . . . . . . . . . : Hybrid\n            IP Routing Enabled. . . . . . . . : No'
    return dictify(x) == {'Windows IP Configuration': {'Host Name': 'MyComputer-007', 'Primary Dns Suffix': '', 'Node Type': 'Hybrid', 'IP Routing Enabled': 'No'}}


def dictify_example2():
    x = 'Wireless LAN adapter Wi-Fi:\n            Media State . . . . . . . . . . . : Media disconnected\n            Connection-specific DNS Suffix  . : local\n            Description . . . . . . . . . . . : Wireless-ABCDE\n            Physical Addresses. . . . . . . . : AB-CD-EF-01-02-03\n                                                AB-CD-EF-01-02-04\n                                                AB-CD-EF-01-02-05\n            DHCP Enabled. . . . . . . . . . . : Yes\n            Autoconfiguration Enabled . . . . : Yes'
    return dictify(x) == {'Wireless LAN adapter Wi-Fi': {'Media State': 'Media disconnected', 'Connection-specific DNS Suffix': 'local', 'Description': 'Wireless-ABCDE', 'Physical Addresses': ['AB-CD-EF-01-02-03', 'AB-CD-EF-01-02-04', 'AB-CD-EF-01-02-05'], 'DHCP Enabled': 'Yes', 'Autoconfiguration Enabled': 'Yes'}}


tests = [dictify_example1, dictify_example2]
def test():
    results = [not run() for run in tests]
    if any(results):
        print("Failed tests:")
        for i in [index for index, bad_result in enumerate(results) if bad_result]:
            print("    ", tests[i].__name__)
    else:
        print("All tests were successful.")

if __name__ == '__main__':
    print("This module runs a few tests.")
