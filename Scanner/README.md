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

[18:54] Protocols for possible new scans:
- Neighbor Discovery Protocol (NDP) over ICMPv6 (Neighbor Solicitation, found via sniffing; Router Solicitation)
- Reverse Address Resolution Protocol (RARP) over IPv4 (found with the Wikipedia article on NDP).



### 2022-11-21
[20:16] Inserting changes from Cyber class today:
- Better user interface in tests.py module.
- New test: check whether Npcap exists

[21:37] I implemented a new system that queues all actions in advance, prints them to the CMD, and then executes them.



### 2022-11-24
[14:18] I need to add special network entity "local broadcast" that will be like 10.0.0.255 or 192.168.3.255 (set all the Device ID bits to 1, as guided by the subnet mask).
Currently, however, the special entities are created prior to the `ipconfig()` call, so a rewrite is needed.



### 2022-11-26
[17:14] Instead of a @probabilistic_cache, have a time stamp assigned to each cached datum, and when it gets too old replace it.



### 2022-12-10
[23:24] The due sate is getting closer, and I realise my code isn't very well-structured.
So I shall organise it!
Plus, one important feature still missing is the TCP port scanner, so I need to add that.



### 2022-12-14
[12:46] Started doing the TCP scan. Imported base code from TCP_Port_Scanner.py (in this repository), and integrated it with the rest of the code.

[14:07] Integration successful, code is working.
Additionally, tested on another home network.



### 2022-12-24
[00:17] Get a little bit of work done on the project.
Focused on fixing bugs and filling requests (noted by the "*******" in comments).

[01:33] Plan to continue:
- Add OS-ID
- Save packets
- Design user screens
- Choose GUI library

### 2022-12-25
[01:08] Finally! I found how to mute it!



### 2022-12-26
[17:30] Storm. The power just went out.
I was working on the program and since the power went out,
so did the Internet connection,
but not the computer (since it's a laptop with its own battery).
Saw the ICMP continuous display just go black.

[23:38] Bug report:
```File "...NetworkStorage.py", line 288, in organise
    self._resolve()
  File "...NetworkStorage.py", line 248, in _resolve
    for entity in self.waiting.queue:
RuntimeError: deque mutated during iteration```

Fix found on https://stackoverflow.com/a/58679808:
NetworkStorage.py:248 ```for entity in list(self.waiting.queue):```



### 2022-12-31
[17:20] Uploading changes from Docs>"Cyber Project - Ideas and Concepts". (code I wrote in class)

[20:27] Working on the GUI. `Flexx` proved itself as insufficient (can't run python code).
Trying to use `Kivy` instead; proved that it can run python from button click.



### 2023-01-11
[22:45] Lots and lots of GUI work, for about an hour.



### 2023-01-13
[15:47] Working on the GUI:
- Adding TK diagram to view separately
- Trying to make them (TK & kivy) work in separate threads

[20:43] Uninstalling and reinsatlling all packages solved the `numpy` issue.
Currently, I'm facing this problem: 
```
diagram = None
...
if __name__ == '__main__':
    diagram = Diagram()


Output:
AttributeError: 'NoneType' object has no attribute 'show'
```

The problem is, inside `Diagram.__init__`, the last call is blocking:
```
self.root.mainloop()
```
so initialisation never actually finishes.
Now, I shall restructure the code, such that this last statement is outside `__init__`.

[21:14] Some thinkning later, I solved it:
```
diagram = Diagram()
diagram.root.mainloop()
```
As easy as that.
Instead of blocking `__init__`, block the main thread instead.



### 2023-01-18
[19:46] Asked Omer Shaked for a help to intuitivise the GUI desgin; implementing it now.

[20:56] After much fighting and googling with fonts and Unicode, I've finally found a character-font pair that works!
“⛶” (U+26F6) -- Square Four Corners
Segoe UI Symbol font for Windows

Correctly displays the `open_diagram` button!

[21:00] Good for `play_button` too (“▶” (U+25B6) -- Black Right-Pointing Triangle)

[21:12] Solved the exiting problem!
No longer is the Diagram TK window opened every time you quit the program, only to manually close it,
now it closes automatically too!
(Note: it does reappear for a split second)

Relevant code:
```
diagram.show()
diagram.root.quit()
sys.exit()
```

Wow, am I lucky today. That's quite some fine progress.



### 2023-01-19
[12:46] Added some stuff to the GUI, in Cyber class, as instructed by the TODO in the document I made yesterday.
- ASCII art of the GUI (Scans screen).
- Split `change_page` button to `pages` BoxLayout that contains 3 buttons.
- Add the `operations` part (#2 and #3): `configure` and `info`.



### 2023-01-20
[13:15] Fixed hovering bug, according to suggestion in my comment, and code-design I made in class yesterday.



### 2023-01-21
[17:47] Working on a new class, `AttachedBubble` that extends kivy's `Bubble`, and acts like the "title" property in HTML,
according to the task I wrote yesterday in the temporary file.



### 2023-01-23
[12:47] Omer Shaked advised me to remove the Attached Bubbles, and possibly change the button text upon hover.

[13:19] Multiple changes during class:
- Changed background colour of the `ButtonColumn`.
- add `spacing=-3` to `operations` (bugfix)
- change `open_diagram`'s logo from "Fullscreen" to "Magnifying Glass".
- add `HoverReplace` instead of `AttachedBubble`.
- generalise `Hover`'s code to any behaviour. Implement on HoverReplace.
    Potential change: use OOP to make this make sense.
    Think of additional behaviours (e.g. change bg and font colour), and implement them in a way that allows multiple behaviours.



### 2023-02-05
[13:42] Fixed bugs with Hover:
- Attribute error -- `behaviour` which should've been `behaviours`.
- Font size is too large in HoverReplace
- Added Hover.start() right before the users sees the screen, which `.hide`s all behaviours.

[14:14] Silly me just repeats an O(n) task `n` (i.e. O(n²)) times for no reason!

[14:18] Use Python OOP in `HoverBehvaior`.



### 2023-02-07
[13:50] After some Googling, I found out that I can use kivy's `ScreenManager` to easily handle the Scan/Save/Know/Start screens!

[16:00] Brainstormed an idea for DRYing my code, in rendering the diagram (both TK and Kivy).

[17:48] Implemented and bugfixed.
Note: reverted the change that does `h-=50` to make space for the title. Find a way to add this back.
Also: the TK diagram is rendered from the top-left corner, but the Kivy one is from the bottom-left corner. Flip one pls.

[18:26] Fixed the `h-=50` thingy. Also, docstrings.



### 2023-02-08
[20:01] Screen is stuck on white upon opening. That's problematic.

[21:55] After messing with Git/GithubDesktop, I've decided to revert changes manually,
to the point where I moved code over to `hover.py`. The issue seems to lie in `from kivy.core.window import Window`,
but I'm clueless regarding how to fix it. So, revert, and try on school computer too.
Also I un/re-installed `kivy`.

I added caches for `KivyDiagram` and `TKDiagram`, which will be lost upon reverting, but no biggie.

[22:00] YES! Reverting worked! Now I'll just add the caches again.



### 2023-02-11
[11:57] Copied colours changes (from Cyber class) from the document.

[12:07] Added `color_hex = lambda...`. Also, found a way to remove the annoying white border on the TK diagram.

[12:23] I organised the `gui.py` code a bit. "I think it's ready for integration with the core.
Gonna eat breakfast and try to integrate!"
    - Possibly my last words.

[16:18] Successful step in the right direction: abstracted the scan buttons.

[17:04] Success in changing to Scan objects.

[17:06] A few stupid puns (YMCA, USA) in the printing placeholders.
Also, added `TypeError` defence in case any `action` actually wants to use the useless argument (`x`) kivy gives.

[17:07] Do: add hoverable entities on the diagram -- show ip.
Do: give `Configure` and `Information` some usage.



### 2023-02-14
[15:02] Start working on the screens (using kivy's `ScreenManager`).

[15:16] Use classes to simplify code.

[15:24] Add another font and fallback.



### 2023-02-18
[12:53] Working on the Save Screen.
Possible character: Envelope with downwards arrow above: 📩
(No matching opposite)
Also: Downwards Triangle-Headed Arrow to Bar: ⭳
Upwards Arrow from Bar: ↥

[13:07] `Hover` requires an upgrade, as I expected: widgets from different screens still demand hovering, even when it's not their screen.



### 2023-02-20
[13:16] Ilya tried out my GUI in Cyber class, and it turns out right clicking creates red dots in `kivy` (multi touch emulation).
To disable add this: https://stackoverflow.com/a/37572966

[13:31] AAAAAAAAAAAAAA THE FONTS LOOK SO DIFFERENT THIS IS HORRIBLE

[13:38] Add another font and improve `add_font`.

[13:39] Add font behaviour in HoverReplace, such that the text (long) will appear in Arial (default; change with argument in `__init__`),
while the symbol text (short) appears in the font specified in the widget (i.e. `font_name` argument in Widget initialisation).

[13:55] Bugfix: threadify progress bar goes up, then down, then back up. The issue is that more threads are created, so we’re dividing by a bigger number. Instead, divide by a constant value (`len(args)`), that isn’t changed by a different thread.

[14:16] Choose transition. I chose Fade.

[14:27] Add HoverReplaceBackground that extends HoverReplace, that changes the background colour upon hovering.



### 2023-02-21
[17:27] Adding the changes listed in the docs file, made during Cyber class.

[18:01] Consider changing the background colour lol
this blue doesn't seem right / nice / good.
(In calls to `HoverReplaceBackground`)



### 2023-02-24
[22:58] I suppose I should address the multi-screen `Hover` issue.

[23:11] I decided to convert the lists into dictionaries, using the screen names as keys, and having a `current_screen {set;}`.
I have considered other approaches (such as specifying a screen in each adding call),
but this one felt the most natural -- and would require the least amount of changes _outside_ `Hover`.

[23:13] Now `Hover` doesn't work at all. Oops. Time to debug.

[23:15] The problem was that I'm using `Hover.enter` for two distinct purposes:
A. Adding widgets and behaviours on a screen. (Initialisation time)
B. Displaying the screen with hoverable entities. (Runtime)
I _can_ use it like that, by technically allowing addition of a new entity on the currently displayed screen.
It would never happen, since entity creation should not be during runtime. This unification allows me to leave this as one method.
I call the method with both purposes in mind, but I wrote it with only purpose A in mind.
Oops. Now it basically removes all widgets when you enter a screen in runtime.

[23:19] Multiscreen-compatible hovering now works.

[23:34] I found a way (tkinter is the way; used Google and ChatGPT) to make "Save as" and "Open" popups,
which will be helpful in the `Save` screen, later on.



### 2023-02-25
[15:46] Added `Know Screen`.

[15:55] Add authorisation checkbox.
`State` has been expanded, and now includes:
    permission: bool = False (default), True if permission has been given.
    highlighted_scan: Scan = None (default), a Scan object representing the currently selected scan button.
    scans: Scan[] = a list of scan buttons represented as Scan objects.

[16:55] After wrestling with kivy's canvas and rendering graphics system, I've finally managed to create a highlight for the current scan.

[22:23] Added `display_information` and `display_configuration` (currently mostly empty) as actions of '⚙' and 'ℹ' buttons.
Slight addition to `OperationButton` to enable actions for these buttons.
Changed `State.scan` to include both a set `state.scan(object) -> None` and a get `state.scan() -> Scan`.
TODO:
    1. Separate `gui.py` (that is a mess) into modules.
    2. Then, create a module that allows SQL access (for the scan's information).
    3. Use this module in the `Information` button.
    4. Change `Information`'s default action (i.e. when no scans are selected) to displaying information about the network (e.g. the assigned ID).
    5. Complete the merge of `main.py` and `gui.py`.
    6. Add file (`*.scan`) handling module for `Save` screen.
    7. Finish the `Know` screen.
    8. Add `Start` screen.
And then the product is basically structurally complete!
Within a month? Doable. I think.
Afterwards, I can add some tweaks to improve it.

[22:39] Wow. What a feeling of completeness. Still a lot of things to do, but it's getting together.


### 2023-02-28
[17:17] I noticed a bug in Cyber class. Fixed it.
The bug (from the shared document): "highlight jumps on window resize."

[19:05] Using `kivy.clock.Clock`, add a slight delay before re-rendering highlight.
This is because a bug was occurring, where if you resized the window _too quickly_, the highlight would forget to update.
I found that 150ms (0.15s) is a good time delay, to maximise both user experience and reliability.

[19:24] Added `DummyScan extends Scan implements Singleton`, and used it to add desired program behaviour: deselecting scans by clicking on them again.

[19:48] Designed and added an icon!

[19:49] BUGFIX: `display_information` was using old interface of `state`. Updated to the new interface.



### 2023-03-01
[22:33] Cleaning up the code.
- Removed `class BlackButton` since it's not used anywhere.
- Removed `ButtonColumn.log_all` for the same reason.
- Moved `def activate` to a more logical location.
- Removed most (if not all) magic numbers related to design (colours, sizes, etc.), and moved them to constants:
    ```bg_color, fg_color, button_column_background, DIAGRAM_DIMENSIONS, HOVER_REPLACE_FACTOR,
    DIAGRAM_POINT_RADIUS, BUTTON_COLUMN_FONT_SIZE, SCAN_HIGHLIGHT, OPERATION_BUTTON_FONT_SIZE,
    OPERATION_BUTTON_BACKGROUND, TITLE_HEIGHT, DIAGRAM_SCALE, PAGES_BACKGROUND, TITLE_FONT_SIZE,
    GREEN, UNDER_DIAGRAM_FONT_SIZE, RIGHT_COLUMN_WIDTH, SAVE_BUTTONS_HOVER_BACKGROUND, SAVE_BUTTONS_FONT_SIZE.```
- Also clarified some comments.

[23:12] Excpetions were not displaying, unless `diagram` was still `None` (mutlithreaded), in which case it would say `During handling of the above exception`.
I realised this is because all kivy exceptions are caught in the `finally` cluase. So I added an `except` clause :).
Also `assert` statement, maybe my first time writing one in Python.



### 2023-03-03
[18:53] I'm working on the databse access module (`db.py`). Going over my notes, trying to find where I wrote the SQL table specifications, I found this:
```
hostify
Util cache invalidation
    choose _future date_ and compare it w/ current_time in get()
             -> pair it w/ the value.
    Run performance tests on different methods.

* Global sniffer
  
`CalcStats` button (scan-like?) that calculates statistics (duh).
Example: [Pie diagram with the following parts:] loopback, to me, from me, broadcasts, not to me & not from me (I wanna see how big this is).
```

[20:47] Found it!
```
Scanner - Cyber
DB Table: "Scans"

Name (+ protocol),
Description (long text),
Time (estimate of exec time per repeat),
Reward (What info will I get?),
Certainty (How certain am I that the info is accurate?),
Safety (passive -> 100% safe, active -> less safe, aggressive (many packets) -> not safe),
Mode (multiple settings of the same scan),
Repeat -- boolean (Repeatable: e.g. ICMP Sweep; Not repeatable: e.g. OS-ID)

Examples:
-> TCP ports, ..., 10s, Open TCP ports, 90%, 10% safe, Mode 1 (ports 0-1024, single SYN), true.
-> Passive ARP, ..., inf, MAC & IP, 99%, 100% safe, 1 (just one mode), false.

2022-12-16; 23:50
Feature: ★ Recommended Scan
e.g. last scan is ICMP sweep => recommend OS-ID.
```

and a bonus:
```
**Scanner - User Actions**

scan-like actions:
- Do ICMP Sweep
- Do ARP Sweep
- Background live ICMP
- Background live ARP passive
- Background OS-ID
- Do TCP scan
- Do UDP scan

data:
- Query the DB
- Look at a specific device

permanent:
- Save current state
- Upload past state & compare

outside:
- Get public address
- Do traceroute
```



### 2023-03-04
[01:08] Many changes, mostly related to `db.py`. See github commits.



### 2023-03-07
[15:20] Integrating `db.py` and `gui.py` and `main.py` via a new class `Register`. 
I made a lot of that class' code using ChatGPT.
It's a powerful tool.

[15:27] The grand union!

[15:39] This is a delicate progress, and I'll take a few precautions:
- I'll document stuff, a lot, to refer back to.
- I'll test-run the program after every little change.
- I'll draw flowcharts :yum:

[15:42] Atomise `standardise_simple_scans(scans: list[tuple[Callable, int]]) -> list[Callable]` into `simple_scan(scan: Callable, repeats: int) -> Callable`.
The methods are independent, but do similar tasks: they both "wrap-up" a `Callable` scan, such that it repeats and has some pretty `__name__` and `__doc__`.
The first gets a list of such scans, and returns a list; the second gets just one unit (i.e. atom, thus "atomise") and returns one unit.

I have considered adding a `name: str` argument to `simple_scan`, but since the `__name__` will only be viewed in technical circumstances, I voted against that change.
Because I'm the only one who votes on this (lol), I won.

[15:46] Create `class Register(dict)`:
I asked ChatGPT to generate a class, that extends `dict`, and implements the Singleton pattern. It did. (See `__new__`)
I asked ChatGPT to override `__setitem__`, to ensure the `key` (str) and `value` (callable) are of a certain type. It did.
I asked ChatGPT to override `__getitem__`, and catch any KeyError(s) that arise. It did. I added a WinAPI box to show the error (UPON CLICKING on the button, aka calling the method).

[15:51] Using `db.get_scans()`, automate the `Scan`s creation in `gui.py`.
This fetches the list of scan names from the database, 
then creates `Scan` buttons (in the `ScanScreenRightColumn`),
and binds them to the methods provided by the `Register`.
Registering the scans under `gui.py`, in `register_scans` (called directly from `if __name__=='__main__':`).

[15:55] I noticed there is too much stuff in `if __name__=='__main__':`, so I added `prestart`, which is also called from there.
It's supposed to group:
(1) everything under that clause, before `start_tk` and `start_kivy`, e.g. `add_font`, `register_scans`, and possibly `G`'s initialisation; and
(2) stuff that's currently in `main.py`, that allows for the scans to oparate correctly, i.e. this piece of code (maybe with changes):
```
    remove_scapy_warnings()

    ipconfig()
    title("ShZil Network Scanner - ", ipconfig()["Interface"], " at ", ipconfig()["IPv4 Address"])

    from testing.tests import test
    test()

    print_dict(ipconfig())
    
    global lookup
    lookup = NetworkStorage()

    ipconfig.cache["All Possible Addresses"] = all_possible_addresses = get_all_possible_addresses()
    print("Subnet Size:", len(all_possible_addresses), "possible addresses.")
```
That's the plan. It obviously might change.
I'll not do that right now, but rather when I unite everything to a single file.
That file is the program (executable) itself, and basically just calls stuff from different modules.



### 2023-03-08
[20:56] Working with ChatGPT, I've improved the information popup, so that it:
(A) Supports markdown (with the help of ChatGPT); and
(B) Displays the information from the database (trivial with the way I've structured the code).

Using a new library recommended by the AI, we've created the `markdown_popup` function, that handles all the mess:
1. Creating a QApplication
2. Parsing the Markdown into HTML
3. Creating the message box and its elements
4. Displaying

I also made `information_about`, under `gui.py`, that calls `db.py`'s `get_information_about_scan`, and formats it neatly to Markdown.

[21:23] Formatting into Markdown is composed of multiple steps:
1. Create phrases based on conditions, e.g. `hasrepeats = "Repeatable" if repeats else "Not repeatable"`
2. Escape "packet models" in the description, like `<IP dst=addresses_in_network> <ICMP type=8 (echo-request)>`, into newline-separated code blocks. Uses regex.
3. Insert everything (raw and generated data) into a predefined structure.

[21:35] Added text descriptors for `certainty` and `safety`. 


### 2023-03-09
[14:15] Talked to Zvika, he demands I implement a username-password part in the software.
This is plainly ridiculous, as my software is client side completely;
One can simply skip that part of the code.
Nonetheless, it is required by the ministry of education's requirements.

After a discussion with Moti, I can do the following:
Save the information as files encrypted with a password to open them. Use asymmetric encryption here (public-private pair), with the keys generated from a human password. 
After further discussion:
Moti wants on-disk live encryption.
I want to do encryption with a password upon saving a scan to a file, and it'll obviously be required when opening it.
Zvika says my apporach will suffice.

[21:56] I drew a diagram of the flow of `gui.py`'s code in Cyber class today. Now, I shall commence merging!
Big thing. Better plan it out here in text (general overview):
-> do all the network stages up to determining ID. (including tests) [from `main.py`]
-> register the scans. [from `gui.py:register_scans`]
-> then, intialise the gui stuff. [from `gui.py`]
-> bind the actions to the buttons. [from `main.py` and `gui.py`]
-> then, display the relevant windows. [from `gui.py`]

[22:49] I thought I might make a loading screen, with informative messages and maybe inspiring sentences, while the software loads.
I wasted an hour trying to get ChatGPT to write me some code for that, in whatever GUI python library.
It doesn't work. So, I decided that this isn't important enough for me to waste that much time.



### 2023-03-10
[17:21] Created file `exe.py`, which will be the new main.

[17:23] Use ImportDefence to import everything necessary.
Note, `import pywin32` will always try to install,
but doing the actual `import win32api` under `ImportDefence()` will not know which module to install if missing.

[17:26] Add a main function to `exe.py`. Should combine the required initalisations of `gui.py` and `main.py`, and do some `test`s, then call the GUI starter.

[17:34] Changes listed in GitHub.

[17:47] Merging changes are done. I haven't tested anything.
If it all works, my next steps are:
(1) Add docstrings and comments (a lot!)
(2) Improve GUI
(3) `File` module and Import/Export scans
(4) `Know.` Screen
(5) `Start` Screen
Obviously, I do not expect it to work first-try.

[17:49] "circular import". That's what I was afraid of.
