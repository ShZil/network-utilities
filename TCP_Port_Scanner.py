from scapy.all import *
from random import randint
from time import sleep
from multiprocessing import Process

MINPORT = 0
MAXPORT = 1023
ip = '10.0.0.138'
ports = {}


def task(port):
    seq = randint(0, 1000)
    syn_segment = TCP(dport=port, seq=seq, flags='S')
    syn_packet = IP(dst=ip) / syn_segment
    syn_ack_packet = sr1(syn_packet, timeout=5, verbose=False)
    if syn_ack_packet is None:
        ports[port] = "Closed"
    else:
        if 'R' in syn_ack_packet[TCP].flags:
            ports[port] = "Reset"
        else:
            ports[port] = "Open"


def ready(threads):
    for t in threads:
        t.join()


def animation(text, delay=.5):
    print(end=text)
    n_dots = 0

    while True:
        if n_dots == 3:
            print(end='\b\b\b', flush=True)
            print(end='   ',    flush=True)
            print(end='\b\b\b', flush=True)
            n_dots = 0
        else:
            print(end='.', flush=True)
            n_dots += 1
        sleep(delay)


def print_port(port):
    try:
        state = ports[port]
    except KeyError:
        state = "No Data"
    print((' ' * (5 - len(str(port)))) + str(port) + " " + state)


def print_port_if_open(port):
    try:
        state = ports[port]
    except KeyError:
        state = "No Data"
    if state == "Open":
        print((' ' * (5 - len(str(port)))) + str(port) + " " + state)


def main():
    animate = Process(target=animation, args=("Starting",.3))
    animate.start()
    threads = []
    for port in range(MINPORT, MAXPORT+1, 1):
        t = Thread(target=task, args=(port,))
        threads.append(t)
        t.start()
    ready(threads)
    print("\rDone!      ")
    animate.terminate()
    # for port in range(MINPORT, MAXPORT+1, 1):
        # print_port(port)
    print("==============")
    for port in range(MINPORT, MAXPORT+1, 1):
        print_port_if_open(port)


if __name__ == "__main__":
    main()
