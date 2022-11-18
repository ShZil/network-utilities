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

[17:15] Maybe I'll add an Encapsulated/Abstracted data structure, that can also be saved as an SQL DB for example.
Idea source: In Cyber class today, there were a lot of ARP-yielded IPv4 addresses. Perhaps even all of the possible ones on the network.
Moti (Zvika's assistant; knows **a lot** about cyber-y stuff) suggested there being some kind of Firewall program that might be "stealing" all unused IPv4 addresses.
He also said I could check the MAC addresses, maybe they're all from the same source? Or maybe it's generating random MACs?
I tried using a dictionary, but because of key-uniqueness, I could not see duplicate MACs (or IPs if I use them as the key).
Therefore, I had to use a `list[tuple[str(MAC), str(IP)]]`. This seems... not extensible. So, a custom class is probably the way.

[23:14] Maybe add a Virtual Network option, where you define the ipconfig screen manually,
and can place some entities with handpicked values -- to test the maths (like numbers of possible IPv4s in subnet).

### 2022-11-08
[22:25] Correction from Cyber class: the indexes should be reversed (negated, in Python) for the sorting to happen correctly.

[23:48] I added the address range subnet something, but on the way I made the base-address solver, so why not add it too?
It's not used right now, but it might be in the future. Plus, it's more practial than the range thing, because it's an actual IPv4 address.

### 2022-11-09
[16:24] Some changes listed in GitHub.

### 2022-11-11
[12:01] In util.TablePrinting, I added a static dictionary `aligns` with three options (left, center, right),
from which a value (lambda function) is chosen.
Also, renamed some symbols to improve readability.

[13:07] Added hostify.batch which is a tester/copy/interactive version of `main.hostify()`.

[13:18] Added support for multiple addresses at once.

[18:57] A question was raised last lesson -- where do the Reverse DNS hostnames come from?
They aren't servers, these are not domain names, but accessing them is supposedly through the same command(s).
Therefore, I'm currently researching this.
1. Windows computers have a `hosts` file (no extension), stored in `%SystemRoot%\System32\drivers\etc\hosts`.
2. Each computer has a hostname, accessible via the `hostname` command,
and changable through the Windows Control Panel interface (at `Control Panel\System and Security\System\See the name of this computer`, or just `Settings\Search "name"`).
3. I cannot find how this happens... Maybe I'll sniff packets when it happens and try to understand.
4. Bluetooth discovery (under `Settings/Bluetooth & other devices`) has the text "Now discoverable as {hostname}" under a tickbox that turns Bluetooth on/off.

[19:25] Added locked NetworkEntity `mDNS` according to this site:
https://stevessmarthomeguide.com/multicast-dns/


### 2022-11-13
[21:03] I've been walking around the house for a few good hours, using my parents and grandma as rubber ducks, and I think I finally cracked it!
So the problem that's been weighing on me is this: How, from a binary string, do you get the opacity value of a device? (ICMP continuous)
Firstly, I reduced the problem to two steps:
1. Calculate meaningful quantities from the binary string.
2. Use those quantities to determine the opacity.
In the current version (LERP by distance to last positive), I only have one meaningful quantity: `distance_to_last`. When it equals 0, the opacity is 100%. When it passes a certain threshold, the opacity is 0%.
The first quest was thus to find more.
Motivated by the observation that some devices have a "shaky" connections (they'll randomly not respond to half the ICMP echoes), I conjured that I should be more lenient when judging them.
How shall I measure this "shakiness"? By defining `connectivity`, or "the connection's quality", by: the percent of positives before last positive out of total requests.
I shall demonstrate via an example: `101010100000`'s connectivity would consider the part before `distance_to_last`, i.e. `1010101`. It has 4 `1`s, and a total of `7` digits. Thus, its connectivity is `4/7`.
At this point I noticed I have two parameters, and kind of got stuck, missing additional inspiration or creativity.
Then I saw this silly coincidence, which led to 3 more parameters: `distance_to_last` starts with a `d`, whereas `connectivity` starts with a `c`. How cool would it be if the next two parameters started with `b` and `a`?
The first one I concieved was `a`: average pf the last 60 data points. Pretty standard, would be the naive approach. Perhaps I could integrate it here too.
Now, I had `a`, `c`, and `d`. I just had to get a `b`! What words start with B?... Best. Best what? Best strike, longest series.
I can measure the length of the longest continuous chain of positive responses! (And while I'm at it, negative too, 'cause why not?).
I later thought of `e` - `wEighted average`, which is like `a` but using a function `f: x (time since response) -> y (importance of that response)`, which will probably just be a dropping exponential.

Now, with all my 5 parameters, A, B, C, D, and E, I can unite them into a formula!
Not so fast. First, I shall determine how each parameter relates to the opacity.
Then, using a lovely Desmos utility Ron Dorman made for me, I can try out different functions, and find the optimal one.

[22:30] Maybe find edge cases of `hostify`? Where each method returns a different string.

[22:33] Also implement that `@probabilistic_cache` for hostify; testing `hostify` now returns different results than what's rendered, pointing at some old data (which is unfavourable).
However, balance that. Treat `hostify` as a costy function.

[22:35] Please add something in `@threadify` that prevents finished processes appearing as 99%! (Print a 100% statement just before returning)

[22:58] This is the Desmos sketch to continue working on tomorrow: https://www.desmos.com/calculator/8mnk4m9gfw

### 2022-11-14
[16:00] At class today, Ran downloaded the wanted programs (Git; Nmap; VSCode), and I made a Batch file that `git clone`s the repository to a local path.

### 2022-11-17
[00:46] A new approach was divinely revealed to me during a shower. I can solve the problem percisely instead of guessing and tuning parameters.

[09:40] I spoke to Erez after maths ended; I explained the problem and started (with his assistance) thinking of it in terms of Probability Theory.

[14:40] During Cyber class today (for ~40 minutes) I tried continuing what Erez and I did, but no progress (it's really noisy with lots of distractions).

[19:30] I went to the local library, sat down with a Statistics & Probability textbook, and did maths. And I got a formula.

### 2022-11-18
[17:50] Finished uploading the papers (manually) into their digital copy.
