### 2022-09-25
Created folder ./Scanner
Created file main.py
Created file run.bat
    - `@echo off` to disable Batch echoing.
    - `color 0A` to set the colors to black (bg) and lime (fg).
    - `title Shzil Network Scanner` to set the CMD's title.
    - `python main.py %*` to activate `main.py`, with all the command line arguments (`%*`).
    - `pause` so the window doesn't automatically close on error.
Created file util.py

[22:25] Let me define the tasks, create a to-do list:
[ ] Find online devices' addresses.
[ ] Scan the devices' ports.
[ ] Create a GUI.
[ ] Save information to DB.
[ ] Packet building and sending. "Scratch-like packet building and sending and receiving"
[ ] Trace routes to outside computers.
[ ] Apply Graph Theory algorithms?
[ ] User actions
[ ] Move all my communication through another device? "Reroute all my packets through a different subnet computer [Wrong MAC, router IP]."
[ ] Algorithmically recognise attacks / show information to enable a human to indentify attacks
[ ] Virtual network creator
[ ] Record some activity and replay it later
[ ] DHCP as new device enters

[22:31] Requirements from Zvika:
- Communication (Server-Clients / peer-to-peer / API)
- OS - threads, processes, WinAPI, Registry
- UX / UI
- DB
- Cryptography
- Documented tests
- Independent learning
- Different user types (normal, admin, owner...)
- No CMD! web/html or Android or py.UI
- Git
- Document EVERYTHING

### 2022-09-26
[14:48] Adding util.print_dict
[20:42] Some more changes listed in GitHub commits
[20:45] Created file ip_handler.py

### 2022-09-27
[16:15] Making a few plans:
- Add @threadify(arg=list[]) decorator! (Threading; w/ progress bar)
- Add method find_device_ARP and find_device_ICMP, both @threadify
- Apply them to all_possible_IPv4_addresses
- Add @timing decorator

### 2022-09-30
[00:44] Found a website listing some network-related windows cmd commands,
maybe read the output of those too?
https://www.techrepublic.com/article/ten-windows-10-network-commands-everyone-one-should-know/
https://www.digitalcitizen.life/command-prompt-advanced-networking-commands/
http://support.seagate.com/rightnow/Flash/central_axis/IPCommands.pdf

[00:58] maybe switch to `ipconfig /allcompartments /all`, rewrite some parser and have possibly more info. Or maybe it doesn't give more info.

[01:02] DHCP testing could use command(s) `ipconfig /release & ipconfig /renew`

[15:34] Gonna rewrite the @threadify to limit the amount of active threads.

[18:54] Done lol. See util.py:88 for additional change

[21:02] Found a site that contains python code for basically the entire project: 
https://thepacketgeek.com/scapy/building-network-tools/part-10/

[21:23] Enjoying myself with some data analysis on the threadified task :)

### 2022-10-02
[21:23] Found out about a technique called "TCP/IP Stack Fingerprinting". Each OS has a slightly different implementation of the protocols, and using these differences one can guess whether what the OS of a remote device is.

[21:28] Related link: https://nmap.org/book/nmap-os-db.html; https://nmap.org/book/osdetect-fingerprint-format.html#osdetect-fp-format; [DB: https://svn.nmap.org/nmap/nmap-os-db; Parsing: https://nmap.org/book/osdetect-methods.html] in nmap-os-db.txt

[21:57] Passive method: https://www.netresec.com/?page=Blog&month=2011-11&post=Passive-OS-Fingerprinting
And larger DB for passive fingerprinting: https://ostechnix.com/identify-operating-system-ttl-ping/

[22:25] A PDF describing the packets for an active Nmap-like scan: https://www.giac.org/paper/gsec/159/tcp-ip-stack-fingerprinting-principles/100625

[23:49] Nmap is short for Network Mapper. I'm creating an Nmap copy.

### 2022-10-14
Working some more on the project. Updates in GitHub.

[23:54] Do it so new computers are added to the graph, and computers which disconnect are slowly faded away.

### 2022-10-15
[00:05] Add repeats for can_connect_ICMP and can_connect_ICMP

[19:04] To identify dis/re-connected devices, send continous ICMP ping requests. Do some tests with the bare data before visualising
