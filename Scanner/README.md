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

[23:55] ICMP_inital_check_repeats was added in main.main(), repeating can_connect_ICMP 3 times over the entire network.

[23:59] Improving the printing

### 2022-10-16
[01:42] Better printing. The table is now horizontal.

[01:53] Loosely using the term: this is a Minimum Viable Product.
It can see the devices on the network and has a fine-ish graphical interface.

[02:00] Do: make the addresses print in increasing order pls.
Do: reconsider this decision -- what happens when address 10.0.0.2 joins the network and the last one is 10.0.0.138? Should we shift the entire log of 10.0.0.138?

### 2022-10-22
[01:09] Finished a vc with Almog working on the Project Proposal and discussing ideas.

[01:25] Found this command for an mDNS abstact function, which also revealed that my ICMP scanner is faulty and doesn't always find all addresses.
(ServerFault Thread)[https://serverfault.com/questions/30738/get-ip-addresses-and-computer-names-in-the-same-network]
Command: `for /L %N in (1,1,254) do @nslookup 10.0.0.%N >> names.txt`  // make this formatted better, i.e. just `addr=name`, without all the padding and the server UnKnown thingy. Batch abilities required.

[01:27] Do add: in the "identify dis/re-connected devices with continous ICMP ping echo requests",
have the "Discover New Devices" and "Check Connection to Known Devices" parts execute on different threads and communicate with the data.
Note, discovering new devices should be slower and silent.
Additionally, add an "opacity" variable as perperation for the visual GUI integration.

### 2022-10-24
[23:24] Working on it, separated into threads.
I just got an idea on how to calculate the opacity!
It should be a weighted average, where the most recent value has the heighest weight (decreasing exponentially).

### 2022-10-25
[00:37] Bug: the continouos display just freezes after a while.
Theory: there's a thread that keeps being alive.
A possible way to limit runtime of tasks: https://stackoverflow.com/questions/366682/how-to-limit-execution-time-of-a-function-call

### 2022-10-26
[19:47] Possible additions outlined in this comment: https://serverfault.com/a/30792

[19:57] Idea: use `arp -a` to list the ARP routing table and read that information

[22:46] Calculate the opacity based on whatever algorithm you choose and display it next to the continouos ICMP screen

### 2022-10-27
[21:41] I wrote down some ideas in class today. They're in a self-directed mail on the school account.

### 2022-10-30
[18:05] Gonna work on the ideas from the mail.

[20:05] I think I'm done. I added the auto-pip-installer for `ModuleNotFound` errors, and the sorting in `continouos_ICMP` is enhanced.

[20:58] Somewhat more standard interface for the simple scans.

### 2022-10-31
[21:00] This command is analogous to my simple ICMP scan:
```bat
@echo off
cls
FOR /L %i IN (1,1,254) DO ping.exe -n 1 -w 500 10.0.0.%i | FIND /i "Reply"
```

[21:02] I have considered using broadcast (255.255.255.255 / 10.0.0.255) and multicast (224.0.0.1),
but after testing in my local network, having 0 hosts respond, and reading that
"Many modern OS are now disabling response to the broadcast. They ignore them to avoid security issues."
"Not all hosts (or networks) will accept or respond to multicast traffic.",
I have concluded I shall not include them right now.
Maybe in the future, as a more complex scan which has a low chance of reward.

[22:19] Maybe add an hostify loop? And have a small chance for `hostify` to not return from cache.
Make it an `@probabilistic_cache`

### 2022-11-03
[17:13] From class today: I moved the function `util.handle_module_error()` into a context manager `import_handler.ImportDefence()` (for easier syntax).

