# Network Utilities
## For cyber programmers!
#### by Shzil
A few network utilities to analyse and act on internet networks. Mostly python-scapy.
**DO NOT USE FOR MALICIOUS INTENTS!**
**ALWAYS MAKE SURE YOU HAVE CONSENT FROM NETWORK OWNER(S) TO EXECUTE THESE CODES.**

## Additional ideas:
- [ ] See in-network packet distrubution between protocols (not just ARP)

## TCP Port Scanner
Using `TCP_Port_Scanner.py`, you can scan open ports of a remote device using the Transmission Control Protocol.

**Settings:**
```py
    # Port Range
    MINPORT = 0
    MAXPORT = 1023
    # Destination IPv4 Address
    ip = '0.0.0.0'
```

Sends a TCP(SYN) packet to each port, to check whether it's Closed, Reset, or Open.
Uses threads, not iteration.
Then, it prints all open ports.

## Network Mapper
Under `./Network Mapper`, you'll find a few files to help you map your current local network as well as connections to the Internet. Uses ipconfig, IP(ICMP), route tracing, and Networkx + Matplotlib libraries. Cache is saved in txt files.
Run by typing `run` in the command line (batch file which calls `main.py`).

**Settings:** _(Inside `main.py`)_
```py
    # True = do network scanning and then render
    # False = no internet, just rendering
    scan = True
    # Number of times to repeat scanning which determines connectable IPv4 devices.
    # Min = 0. WARNING: Heavy on performance
    repeats = 5
    # Number of times to repeat scanning from cache for connectable IPv4 devices.
    cache_repeats = 3
    # Number of times to repeat tracing routes.
    # Note: each trace includes 3 checks.
    #   Thus, This is for additional route information, not reliability.
    route_repeats = 1
    # Completely disable Host Names (`hostify`) by setting this to True.
    no_hosts = False
    # Allowing self-loops (edge where `start node == end node`) in graph?
    self_loops = False
    # Draw text labels (ip+host name) on Graph for *all* nodes?
    do_labels = False
    # Render the ghost nodes? [Setting this to false
    #                          might disconnect some parts of the graph]
    show_ghosts = True
    # Time Per Packet (hand-measured!). Only affects time display pre-scanning.
    tpp = 0.09
    # Timeout for each scapy(sr1). Do not raise too much.
    timeout = 1
    # Maximum number of hops in traceroute. Windows uses 30.
    route_max = 20
    # On the graph, display the IP and Host of destinations?
    # (overrides do_labels for certain nodes)
    display_destinations = True
    # On the graph, display the name of important nodes?
    # i.e. the computer "Here", local area "Router", and "DNS" servers.
    display_base = True
    # How careful when guessing which ghost-nodes match?
    # 0=no guessing, 1=quite certain, 10=uncertain
    # Technical meaning:
    #   how many Timed-out nodes allowed in parallel chains between the same ends?
    #   max value, any shorter/equal chain will be merged.
    guess_ghosts = 25
    # How many times to repeat the Timed-out node-chain merging?
    chain_removal_repeats = 3
    # How many hex digits allowed for each timedout ghost node?
    timeout_digits = 5
    # smallest distance in order to choose a node by clicking on it?
    smallest_dist = 0.01
    # LAYOUT SELECTION. Choose the most-fitting method.
    # Ordered by my preferences (top is best).
    def layout(G):
        return nx.kamada_kawai_layout(G)
        # return nx.spring_layout(G)
        # return nx.planar_layout(G)
        # return nx.shell_layout(G)
        # return nx.spectral_layout(G)
```

**Stages of execution:**

1. √ Repurpose personal tracert.py

2. √ Get information from `>ipconfig`

3. √ Realise map of local area network:
    1. √ Do some Cybery math to list all computers.
    2. √ Check which computers actually exist.
    3. √ Trace route (todo1) to every computer.

4. √ Visualise (using NetworkX)
    1. √ Colours! (IPv4 → Integer Number → colour for the node).
    Close addresses (similar networks) -- closer colours
5. √ Cache and re-render of graph

## ARP Displayer
Under `./ARP Displayer`, you'll find code which can preform operations using the Address Resolution Protocol.
Uses ARP, scapy sniffing, socket's host translation, and Networkx + Matplotlib libraries. Cache is saved in txt files.
Run by typing `run` in the command line (batch file which calls `main.py`).

**Settings:** _(inside `main.py`)_
```py
    # Turn `no_hosts` to `True` to disable `hostify(address)`.
    no_hosts = False
    # Start sniffing from scratch (True) or load cache and start from there (False)?
    from_scratch = True
    # Remove edges indicating a who-has ARP request (True) or not (False)?
    no_who_has = True
    # Include nodes outside the local network? Yes=True; No=False
    outta_net = True
    # Print only unique and new ARP packets or sus alerts?
    unique_only = True
    # Select layout for the graph.
    def layout(G):
        nodes = ipv4sort(list(G.nodes))
        return nx.circular_layout(nodes)
        # return nx.kamada_kawai_layout(G)
        # return nx.spring_layout(G)  # Fruchterman-Reingold algorithm
```

**Stages of execution:**
1. Get computer info from `ipconfig`
2. Read cache (if requested)
3. Split to sniffing ARP thread and graph rendering thread.
4. On each packet, save it. On each graph closed, display updated one.
