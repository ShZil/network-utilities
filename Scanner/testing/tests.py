from main import *
from ip_handler import *
from ipconfig import *
import os


def dictify_example1():
    x = 'Windows IP Configuration\n            Host Name . . . . . . . . . . . . : MyComputer-007\n            Primary Dns Suffix  . . . . . . . :\n            Node Type . . . . . . . . . . . . : Hybrid\n            IP Routing Enabled. . . . . . . . : No'
    return dictify(x) == {'Windows IP Configuration': {'Host Name': 'MyComputer-007', 'Primary Dns Suffix': [], 'Node Type': 'Hybrid', 'IP Routing Enabled': 'No'}}


def dictify_example2():
    x = 'Wireless LAN adapter Wi-Fi:\n            Media State . . . . . . . . . . . : Media disconnected\n            Connection-specific DNS Suffix  . : local\n            Description . . . . . . . . . . . : Wireless-ABCDE\n            Physical Addresses. . . . . . . . : AB-CD-EF-01-02-03\n                                                AB-CD-EF-01-02-04\n                                                AB-CD-EF-01-02-05\n            DHCP Enabled. . . . . . . . . . . : Yes\n            Autoconfiguration Enabled . . . . : Yes'
    return dictify(x) == {'Wireless LAN adapter Wi-Fi': {'Media State': 'Media disconnected', 'Connection-specific DNS Suffix': 'local', 'Description': 'Wireless-ABCDE', 'Physical Addresses': ['AB-CD-EF-01-02-03', 'AB-CD-EF-01-02-04', 'AB-CD-EF-01-02-05'], 'DHCP Enabled': 'Yes', 'Autoconfiguration Enabled': 'Yes'}}


def ipconfig_data():
    data = ipconfig()
    for key in ["IPv4 Address", "Subnet Mask"]:
        if not key in data:
            print("ipconfig() has no key \"" + key + "\".")
            return False
    return True


def bitify_examples():
    return bitify("0.0.0.0") == '00000000000000000000000000000000' \
        and bitify("255.255.255.255") == '11111111111111111111111111111111' \
        and bitify("192.168.0.1") == '11000000101010000000000000000001'


def unbitify_examples():
    return unbitify('00000000000000000000000000000000') == "0.0.0.0" \
        and unbitify('11111111111111111111111111111111') == "255.255.255.255" \
        and unbitify('11000000101010000000000000000001') == "192.168.0.1"


def valid_subnet_mask():
    mask = ipconfig()["Subnet Mask"]
    mask = bitify(mask)
    counting, ones, zeros = "ones", 0, 0
    for c in mask:
        if c == '1':
            if not counting == "ones": return False
            ones += 1
        elif c == '0':
            counting = "zeros"
            zeros += 1
        else:
            return False
    return ones + zeros == 32


def threadify_echo_test():
    echo = lambda x: x
    echo = threadify(echo, silent=True)
    return echo([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]


def shift_list_test():
    a = [1, 2, 3]
    return shift(a, 1) == [2, 3, 1] and shift(a, 2) == [3, 1, 2] and shift(a, 3) == a


def does_winpcap_exist():
    """WinPcap / Npcap aren't installed. It is essential that you install either one. https://npcap.com/#download"""
    try:
        from scapy.all import sendp, Ether, IP, ICMP
    except (ImportError, ModuleNotFoundError):
        return False
    
    try:
        with NoPrinting():
            sendp(Ether() / IP() / ICMP(), verbose=0)  # Sends a default to ICMP packet to localhost (so no network traffic generated).
    except RuntimeError:
        return False
    return True


def does_fallback_font_exist():
    """A necessary font (Segoe UI Symbol) was not found under `fonts/Segoe UI Symbol.ttf`. Please check your installation of the software."""
    import os.path
    return os.path.isfile(r".\fonts\Segoe UI Symbol.ttf")


# Each element is a boolean function. False means the test failed.
tests = [dictify_example1, dictify_example2, ipconfig_data, bitify_examples, unbitify_examples, valid_subnet_mask, threadify_echo_test, shift_list_test, does_winpcap_exist, does_fallback_font_exist]
def test() -> None:
    os.system("")  # Enables ANSI colouring
    results = [not run() for run in tests]
    with open('tests_log.txt', 'w') as log:
        log.write('\n'.join([
                test.__name__ + " " + ("Successful" if not result else "Unsucessful")
                for test, result in zip(tests, results)
            ]))
        if not any(results): log.write("\n\nAll tests were successful.")
    if any(results):
        print("Failed tests:")
        for i in [index for index, bad_result in enumerate(results) if bad_result]:
            test = tests[i]
            print("    •", test.__doc__ if test.__doc__ else test.__name__)
        print("The software might work incorrectly or crash.\nContinue execution only if you're sure.\nOtherwise, close this window.")
        input("Press any key to continue. . . ")
    else:
        print("All tests were successful.")
    print("\033[0m")  # End colors


if __name__ == '__main__':
    print("This module runs a few tests.")
    test()
