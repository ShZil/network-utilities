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
RuntimeError: deque mutated during iteration
```

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
```py
diagram = None
...
if __name__ == '__main__':
    diagram = Diagram()


Output:
AttributeError: 'NoneType' object has no attribute 'show'
```

The problem is, inside `Diagram.__init__`, the last call is blocking:
```py
self.root.mainloop()
```
so initialisation never actually finishes.
Now, I shall restructure the code, such that this last statement is outside `__init__`.

[21:14] Some thinkning later, I solved it:
```py
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
```py
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
    GREEN, UNDER_DIAGRAM_FONT_SIZE, RIGHT_COLUMN_WIDTH, SAVE_BUTTONS_HOVER_BACKGROUND, SAVE_BUTTONS_FONT_SIZE.
    ```
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
```py
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
(0) Remove all `from ___ import *` -- only use sepcific imports. Maybe use an IDE (e.g. PyCharm) to do this.
(1) Add docstrings and comments and type hints (a lot!)
(2) Improve GUI
(3) `File` module and Import/Export scans
(4) `Know.` Screen
(5) `Start` Screen
Obviously, I do not expect it to work first-try.

[17:49] "circular import". That's what I was afraid of.

[17:51] The problem is that `gui` is importing stuff from `main`, which hurts module separation, and ultimately leads to circular imports.
Let's separate.

[17:58] Introduced `globalstuff.py` to solve circular import, for globals `G` and `lookup`.

[18:00] Flashback:

```
[17:23] Use ImportDefence to import everything necessary.
Note, `import pywin32` will always try to install,
but doing the actual `import win32api` under `ImportDefence()` will not know which module to install if missing.
```

Now this causes an infinite loop.
Not the best way to solve this (probably), but it's enough:
I added a test that checks whether the module is installed, and if not, tries to install it.


[18:10] "TypeError: unhashable type: 'NetworkEntity'", so I'll make it hashable!
I vaugely recall having had some trouble with this in the past, when creating `NetworkStorage.py`,
but I think it'll be alright if I separate `.compare` and `.__eq__`.

[19:23] In exe.py, move the ImportDefence to be executed first, before the other imports.
Also, add some graphics libraries there.
Additionally, catch PermissionError's around remove_scapy_warnings().

[19:25] in NetworkEntity.__eq__, add a check for 'other==None'.
Add test: openGL version must be 2.0 at least, by kivy requirements.
Actually, nevermind, because `kivy` already displays a fine error message for that.

[23:12] The scans do execute, but on the same thread as the `kivy` gui, so it gets frozen.
Instead, I'm going to let `Register` handle the threads for the scans.

[23:21] Register now handles the scans in the following fashion:
`Register().start(s.name, s.act, s.finished)` -- starts a new thread.
The thread contains:
```py
def _add_callback(action, callback):
    action()  # s.act()
    callback()  # s.finished()
```
It's the `Scan`'s responsibility to manage a property called `is_running: bool`,
although `Register().is_running(name: str) -> bool` is also available.



### 2023-03-11
[00:04] I tried to write a solution for displaying opacities and updating the graph and lookup,
and I did it too hastely. So, since I'm not staisfied with it, I deleted all the changes (Except unrelated ones).
I shall think about this first, and then implement.
I think the 5 second interval updating is good enough, and will work for both finite and infinite scans.

[00:32] I tried to investigate how to disable the popup's sound effects. No working results.

[00:35] Some small changes are listed in GitHub.

[12:27] Debugging the closing of the appilcation.
I managed to get TK to close after Kivy, by replacing `diagram.root.quit()` with `diagram.root.after(0, diagram.root.destroy)`,
but the console is still running and occasionally prints a newline.

[12:30] I found this thread: `<Timer(Thread-22, started 10764)>`, which is probably running this code:
```py
# exe.py
def keep_resolving_storage():
    sleep(10)
    NetworkStorage()._resolve()
    from gui import diagram
    if diagram is not None:
        if diagram.renew(G):
            update_kivy_diagram()
    Timer(5.0, keep_resolving_storage).start()
```

So I added a check: `if is_kivy_running:`, so that it stops renewing the diagrams and lookup when the application is closed.
This also explains the newlines at regular intervals, of probably around 5 seconds.

[12:50] I restructured the method above to use a `Thread+while` instead of `Timer`.
Now, I can clearly see what's going on. And, for some reason, it's convinced that `is_kivy_running` is `True`.

[12:53] My guess: booleans are passed by value between modules, and not updated.

[13:05] I asked ChatGPT. Turns out, the variable `is_kivy_running` is not shared well between threads.
So, I need to use `threading.Event` instead.

[14:01] YES! It works! The lovely message I've longed for has appeared: `Press any key to continue . . .`.

[14:06] Rename markdown_popup -> popup, and extend its range of responsibilities:
It now takes in:
- title: str, message: str
- kwargs: error=False, warning=False, question=False, info=False
if all kwargs are false, display a `win32 Message Box`!
Else, display a `QMessageBox` with the wanted icon.

[15:35] `os.system("color 00")` doesn't work, because the `color` command does not allow for the foreground to be the same as the background.

[16:51] Have the diagrams update on regular intervals (5 seconds). Might globalise the delay later.

[16:56] Because I'm using the Singleton pattern in `NetworkStorage`, I do not need a global `lookup`!
Just replaced all its occurences with `NetworkStorage()` and it'll work fine.
Performance shouldn't change too much.



### 2023-03-13
[18:50] Adding Know-Screen functionality.
During Cyber class today, I noticed that I can't view the addresses, just a basically-useless circle of dots.
This is frustrating, because although the programme works, it isn't useful to the user.
This will soon be solved by introducing clickable or hoverable dots, that display addresses.
But until that (comparatively complex) code is finished, let's do something simpler, that I'll have to do sooner or later:
add the know screen. So, currently, it just displays the `lookup: NetworkStorage` itself (using `Iterator` and `ToString` functionalities).

[19:07] Consider displaying the text in a table format, which is more natural here. Also, add scrolling mechanism.

[19:09] Decreased `util.MAX_THREADS` from 300 to 100, because the programme was lagging a lot during scans, and this might be one of the reasons.
Probably a thread mistake tho, like "the GUI thread is running a scan".
Also remove `active_count()` warnings, and delay more: 0.02s instead of 0.01s.



### 2023-03-16
[15:30] Implemented the Export button.
Related things to add soon:
- The file should be encrypted with a password.
- Import button functionality.
- Save more data than just the `NetworkStorage`, e.g. the network ID, the scans and their timesteps.
- Compress the data: I know a lot of information about how the data is structured and what it contains, and saving it as ASCII characters (or worse -- UTF-8 or Unicode) is just wasteful and somewhat disrespectful.



### 2023-03-17
[15:16] Working on turning the Know screen to a table.

[15:56] I twice defined `NetworkEntity.__eq__`, which is a mistake,
and now the NetworkStorage resolves improperly (has duplicates).
Thus, I renamed one to `.equals`.

[23:21] I'm fighting a bothersome error `KeyError` in the comparison of graphs (`nx.utils.graphs_equal(renewed, self.graph)`).
I'm not sure what's causing it, so I've just been printing, reading docs and logs, catching exceptions, resturcturing code snippets from my code.
ChatGPT's assistence has proved useless here lol



### 2023-03-18
[16:55] Added Scrolling mechanism to Know screen.
With assistance of ChatGPT. It's really useful for small snippets like these.

[16:56] Changed `pause` to `REM pause` in `run.bat`, so that the console window closes automatically when the application is closed.
This is getting ever-closer to an actual application. Now just find a way to hide the console entirely.

[16:57] Yesterday I added the ability to cancel scans.
It's not wise for the GUI and UX, since now more clicks (choices) are required,
but it's honestly a useful functionality, preventing misclicks.

[17:01] Yesterday, I fixed a bug in `exe.py`.
The `router` and `here` entities, which I alledgedly added, weren't displayed.
Turns out I forgot to import them post-initialisation, so they were `None`s.

[17:03] Yesterday I added `...` when a scan runs,
which is both a neat feature for UX, and **very** easy to implement with the way my code is structured.

[17:07] I haven't reproduced the bug relating to the `KeyError`.
I believe the issue was related to `G`'s (nonexistant) thread safety.
Now, when it's used, a `.copy()` is applied.

[17:08] Set window size.
To tidy up the code (future steps):
- Docstrings.
- Remove magic numbers.
- Comments?
- PEP8.
- Find repeating strings.
- Remove magic strings.



### 2023-03-22
[15:04] Removed continuous ICMP printing.

[16:35] Created `ScanFileBuilder` with the help of ChatGPT.
I wrote the actual logic, it just made a simple class with a list.
Admittedly, getting ChatGPT to write what I want, and tackling its errors,
all took more time than just writing the class on my own. 

Prompt (before all the corrections):
```
I'd like to create a file factory class for saving information about LAN scans. Python.
I have a file `files.py`, which contains two methods: importer and exporter, called by their GUI buttons from another module. After I ask the user for the path (whether for saving or loading), I want to construct an instance of said class.
The file should contain (separate lines in the actual file, and python fields in the instance) the following data:
- The scan ID via `main.py`'s `get_scan_id()`
- The discovered network entities via ```from NetworkStorage import NetworkStorage; data = [str(x) for x in NetworkStorage()]```
- The scans that were executed and their timestamps
- A string in the beginning of the file that says "SHZILSCAN" (for confirmation that this is a correct file)
- Possibly more parts

Could you please generate an overview of the class, using Python (and many comments and sections for me to complete, by knowing the architecture of the entire project), with a good programming pattern to use here (use the Builder pattern), for me to put into `files.py` (it should only be used inside that module)?

The file should be binary. The extension is `.scan`.
```

[17:08] I already encountered this error: `RuntimeError: deque mutated during iteration`. Just wrap the queue with `list(...)` method.

[17:41] Added ViewScreen and some kivy titles.

[17:45] See the importing results as plaintext in ViewScreen.

[17:47] I wanted to write a bit about the motivation behind the `HEADER = "SHZILSCAN"`.
The actual string doesn't really matter, but it doesn't serve the same purpose as `PNG` in images.
Technically, currently it does -- it helps recognise the file.
In the future, when I encode with a password,
instead of saving the password and checking equality (which would be beyond ridiculous),
I have a constant header to the file.
Then, upon decoding, I can check to see whether that header is present.
if it is, great.
If it isn't, it means the password is wrong (or the file is corrupted).

[18:51] I don't want to clutter the main GUI thread(s) with code, because that would make them not respond.
So, I shifted the importing and exporting code to separate threads.

[19:22] Cannot change screens from outside the main kivy thread.
I tried to figure out a simple solution to this:
- Remove ViewScreen and put the info on KnowScreen?
- Print the information as a popup?
- Creating a loop in the main kivy threads that waits for an event?
I decided:
- Just move the `state.screen("View")` outside of the thread.

[19:24] Print the running threads, not only at regular intervals (`exe.py: keep_resolving_storage`),
but also upon termination of the application.

[20:23] Just adding a tiny 'w' will hide the console window?! No way.
In `run.bat`, changed `python` to `pythonw`, by the advice of ChatGPT.

[20:25] NVM it doesn't work. Also tried adding `start /B` at the start of that line.

[20:41] I've created a dummy python tkinter file to test whether `pythonw` works. 
It does work.
I tried adding `starter.py` that starts the `exe.py` with `subprocess.Popen`...
It doesn't work.

[21:08] I'm struggling with this so much, that ChatGPT suggested: "you may need to seek assistance from a technical support specialist who can help you diagnose the issue further". 

[21:40] ONE issue solved: https://github.com/kivy/kivy/issues/7004
```set "KIVY_NO_CONSOLELOG=true"```

Also, removed the call to remove_scapy_warnings, because idc about them when there's no console.

[23:14] I'm gonna do something big: remove all references to stdout in the code. Everywhere. I have a GitHub backup in case things go wrong.

[23:49] This is too difficult. I'm going to need Moti's help, probably, unless I can solve it myself.
Such a simple problem -- making the console window disappear -- such a difficult way to solve it.
Note to self: use WakaTime's reports in the project's report.

This is currently a stable build.
I just need to add primitive symmetric file encryption, and it's ready to be presented.

Later, I can improve:
- Optimise file saving (content length)
- GUI inconsistency in position of `Pages()`
- Searching for an address in `Know.` Screen
- Add a start screen
- Ctrl+F any "*****"s (indicator of TODOs I've placed)



### 2023-03-24
[13:41] Some small changes in GitHub.

[13:42] Trying to implement a password system in `files.py`,
using `tkinter.simpledialog.askstring`,
and a `password` property in `ScanFileBuilder`.



### 2023-03-26
[16:56] Added `_get_readable_threads` under `gui.py:general_information`

[17:24] TODO: refactor the names, add docstrings, and comments, and PEP8; pay close attentions to the threads' names that appear on General Information.

[17:54] Even ChatGPT has limitations:
I tried to ask if for modules that won't work with `ImportDefence` (I explained the criteria exactly),
but it kept giving wrong answers.
Hopefully, the new capabilities of GPT-4 will succeed in this.

[19:54] I just had a shower, and it (as usual) sparked an idea: 
In `@threading`, rename the `task` based on `f`. That way, one can see how many `"task" threads` are dedicated to each call.
This shall be a part of a bigger trend: renaming threads to have a user-friendly name (because they are displayed to the user under General Information).



### 2023-03-27
[18:42] Trivially implemented `Live ARP`.
Now it's time to fix bugs and,,, that's it.
It's really easy to implement a new scan.

[18:54] I decided that `Live ARP` is really slow.
So, when it starts, I'm gonna run `arp -a` in a terminal,
and read the output.

[19:05] Wrote a regex using `regexr.com` to detect useful lines in `arp -a`.



### 2023-03-28
[11:39] Implemented the regex for `Live ARP`.
Now, the need has become clear for more special network entities.

[12:08] Implemented a `LAN` variable in `NetworkStorage`, that allows for the clear syntax of:
```py
if entity in LAN:
    G.add_edge(router, entity)
```
Which offers a logical visual distinction between entities in the LAN and outside it.

[12:12] TODO: fix the flipping difference between the kivy and tk diagrams.
You know what the problem is (kivy starts from bottom left, tk from top left).
You know how to solve that (coordinate transformation in `KivyDiagram` and `TKDiagram`).
Just do it.



### 2023-03-31
[22:07] Testing the software on a new LAN.
Added the "Public Address" semi-scan button's functionality.

[22:37] I struggled with such a silly bug: I forgot `()` next to `NetworkStorage`.
Half an hour went up in flames for that.
Anyways, `Public Address` is now functional.

[22:49] Started renaming threads' functions to be more user-friendly.
- threadify's `task`.
- `Register.start._add_callback` hides the name of the scan action.
- `_resolver`
- `start_kivy`



### 2023-04-01
[23:41] Yeah, April's Fools.
I'm trying to add a textual representation of the nodes on the diagrams.



### 2023-04-02
[00:28] I've tried to add a special (tight and bold) edge between the routers' internal and external entities,
but it caused a crash I couldn't trace, so that ain't happening.
Many, many browser tabs.

[18:00] Create `files.py:encrypt` and `files.py:decrypt`, using `cryptography.fernet.Fernet`.

[18:10] Separate code to module `files_cryptography.py`.

[18:25] BUG: Running just `ARP Sweep` once doesn't update `Know Table` nor the `Diagram`.

[19:27] BUGFIX: quite simple honestly, just add a dynamic import for `gui.py:diagram` under `exe.py:keep_resolving_storage`.

[21:16] I fought the password input for a long time.
Tkinter - it just refused to continue running code after `simpledialog.askstring`, including returning the string value.
PySimpleGUI - I tried it too, it just froze.
Kivy - I tried adding a `TextInput` to the `SaveScreen`, but Kivy won't even start the window when importing `TextInput`.
I finally decided to use the simplest solution - python's built-in `input()`.

[21:20] It crashes immediately. Change to dynamic import.

[21:24] Correct password -- works. Wrong password -- shows nothing.

[21:36] The problem is that current encryption/decryption doesn't halt when the password is wrong.

[22:18] Finally, an encryption-decryption file that works!
If the decryption is too slow, it means the password is wrong,
so I added a timeout check.

[22:20] Cleaning up the printing:
- Don't print special entities in `NetworkStorage` initialisation.
- Don't print the scans' names in `gui.py:ScanScreenRightColumn` initialisation.

[22:23] Next up: implement more scans
Supporting infrastructure:
- OS column for `OS-ID`
- Configure popup for `TCP Ports`
- Packet memory for `OS-ID`
Also,
- Scan history for the files.



### 2023-04-06
[00:51] Asked a friend for help with the Cryptography, because he is well-versed in the ways of the Python.
So he asked Copilot to write a class for that, and this is the result.

[00:52] Integrating `tag` and `nonce` into the class.

[01:02] Change to CBC (still with Copilot), because there is no `tag` and `nonce` there,
it's just simply encrypting the file itself with a password and IV.
The password supplied is hashed and split in two (128 bytes each): `key` and `iv`.

[01:08] I had to correct Copilot's code.
I also changed `self.key` to a local variable `key` that's gone after the constructor,
which is better, because we needn't save it for all that long.
Let's try testing.

[01:26] Abstracted `get_password` in `files.py`.

[01:35] Printing changes: changed `main.py:do_simple_scan`'s default value to `results=False`.

[01:52] Revered to `tkinter:askstring`.

[01:53] Asked ChatGPT for a user string input in win32api, and it gave a fine answer.

[01:57] With ChatGPT, made a new version of `get_password` with PyQt5.

[02:17] Alright, it just keeps crashing. I'm gonna postpone fixing this to tomorrow, because it's getting late.

[20:03] Module testing on `files_cryptography`. Noticed and fixed a simple bug:
`_init_` instead of `__init__`. This is because WhatsApp sends code using the formatting,
where `_STRING_` -> _STRING_ becomes italics. And copying doesn't include the hidden underscores.
Also added a `if __name__ == '__main__'` clause.

[20:23] `ValueError: Incorrect IV length (it must be 16 bytes long)`. Oof. Let's fix that.

[20:27] Rename `password` to `hashed`, for there not to be dynamic type changing, which is allowed in Python, but confusing.

[20:28] Fix the bug: the `hashed` is 32 bytes long, so take 16 to IV and 16 to the key (not 128).

[20:32] IDEA: add a dictionary of special information, like OS (from `OS-ID`), or entry type (from `Live ARP`'s first stage).
Use this dictionary in Know Screen.

[20:34] Testing report: `Export` works fine and quite fast, `Import` crashes.

[20:38] Why create two instances of the same object? This makes no sense given the current usage.
Plus, fixing it looks super Pythonic, which is good.

[20:57] BUG: `Import`ing twice crashes the software. Also, `Import`ing with a wrong password crashes the software too.

[21:19] It gets to `files.py:137: raise ValueError("Couldn't decrypt the file. The password is wrong")`,
and has a popup for the error (!) but then immediately crashes.
This narrows down the places in my code where the error might be.
It's probably because of mishandling exceptions that are under `gui.py`'s responsibility.

[21:27] Changed the code in `gui.py:_importing` to hopefully catch more exceptions and edge cases,
like the one currently crashing my application.

[22:45] With some printing statements, I narrowed down the location of the bug to the `popup`.
I just changed `error=True` to nothing, and now it uses `win32api.MessageBox` instead of `QApplication`,
and that works?!
Alright. Not complaining.

[22:58] STABLE BUILD. Finally.

[23:08] Gonna `autopep8` the `.py` files in the project!



### 2023-04-07
[00:34] I'm `autopep8`-ing the files, going over the fixes and changing those I don't like.
Use `GitHub Desktop` to see what changed, and the `Git` extension of `VS Code`.

[01:15] Done with `pep8`-ing. Next up:
- rename files to a consistent format (I like `NetworkStorage.py`'s format, make everything look like a class name in Java)
- add type hints to everything (okay maybe not everything, just function's signatures)
- add docstrings and comments.



### 2023-04-09
[14:23] Motivation: find where the `print`ing happens, to remove all unnecessary logs.
Procedure: set up VSCode's Python IDE stuff.
Problem: runs from a different path, so couldn't find `scans.db:information table`.
Fix: run `db.py` (which runs `db.py:init`), to create the table.
Couldn't reproduce the printing.

[14:43] Added test against the problem above, called `is_sqlite_table_information_present`.

[14:45] TODO: add the following modules:
- Global Packet Sniffer (init from `exe.py`; use to implement `OS-ID`;
                         perhaps use special class to integrate seemlessly with SQL database?;
                         button to see packet statistics in Know Screen?)
- Scan History (implement from `register.py`)
- Special Information (implement using a similar class to Global Packet Sniffer for integration with SQL;
                       add button in Know Screen to ask for an address and get a popup with the device's "profile",
                       showing NetworkStorage information as well as Special Information (e.g. OS, Ports)).

[17:09] With ChatGPT assistance, I wrote `class PacketSniffer`,
as an implementation of the first module requested above ("Global Packet Sniffer").
I could've written that code, but ChatGPT makes it much faster.

[17:32] I improved `PacketSniffer` using ChatGPT.
Firstly, it uses a `packets.db` file with SQLite3, when the `self.packets: list` fills up to 100 entries.
Secondly, it allows filtering based on IP layer properties: src and dst.
That's pretty much it. I asked it for a few tweaks when I saw stuff I didn't like.

[17:46] Improved `PacketSniffer` to implement the Singleton pattern, using ChatGPT.

[17:47] ChatGPT wrote `filter=...`, instead of `lfilter=...`. Fixed.

[17:48] ChatGPT uses inconsistent naming: initialise with `_`, use without. Python no like. Python mad. I fix.

[17:56] Save the time a packet was sniffed too.

[18:05] Type mismatch: `sqlite3.InterfaceError: Error binding parameter 5 - probably unsupported type.`.
ChatGPT couldn't be helpful on this, so I solved it alone (yay!);
just cast `ttl` to an integer.

[18:12] Fix: `TypeError: PacketSniffer.__init__() got an unexpected keyword argument 'max_packets'`.

[18:17] BUG: `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 14956 and this is thread id 1536.`
FIX: Make the DB connection local to each method.

[18:25] I'm so glad I'm module-testing `PacketSniffer.py`. There are so many problems with it... Thanks, ChatGPT.

[18:26] LOL right it's `INTEGER`, not `INT` in SQL.
Also, cast to string the FlagValue of scapy.

[18:55] Finished creating the module PacketSniffer.



### 2023-04-10
[00:19] Add `PacketSniffer.__len__`, and `.length` property.

[01:17] Move the responsibility on Infinite Scans to Register,
which is a more logical place than some obscure place in `gui.py`.

[01:36] Fought against "WARNING: QApplication was not created in the main() thread."
I lost.

[01:55] Wrote `SpecialInformation` with ChatGPT.

[01:57] Upgraded `SpecialInformation` with Singleton pattern.

[02:15] Improve `SpecialInformation` to use `NetworkEntity.equals` and merge information seemlessly.

[02:30] Finish implementing `operating_system_fingerprinting`

[02:44] Add `KnowScreenDeviceProfileButton`.

[02:48] Move responsibility of `get_password` to `gui.py`, and rename to `get_string`.

[03:26] I've been working on "Device Profile" for too long after midnight. This is my progress:
- Add `NetworkEntity.to_dict`
- Add `NetworkStorage.py:match(str)`
- Fixed a bug that was crashing the software by moving an import to inside a function
- Created a button for Device Profile, and put it in the middle of Know Screen.
- Add button's functionality (doesn't fully work):
I'm gonna detail it here, because otherwise I'll have no idea what I wrote there tomorrow.
The button's on_press is binded to `device_profile`.
All `device_profile` does is create a `Thread` to `_device_profile`.
`_device_profile` does this:
1. gets the address from the user using `get_string`.
2. gets a NetworkEntity from NetworkStorage that has this address, either as MAC or IP or IPv6, or name.
This is done by `_match_device(str) -> NetworkEntity from NetworkStorage or None`, using `match(str) -> fake NetworkEntity that has one field set and the rest as default values`.
3. if the entity wasn't found, say so in a popup.
4. if the entity was found, display its information (both "regular" like MAC/IP/IPv6/name and "special" from SpeicalInformation) with a popup and markdown.
Markdown is handled by `_construct_content(information: dict) -> markdown str`.
Note, it doesn't currently work.
I'll try fixing it -- I'll see what I can do.
But perhaps not today.

[03:49] Doing some old-fashioned print-based debugging.

[03:55] VSCode Python IDE helped me find the bug.
I placed a breakpoint according to my knowledge,
and it presented the exception!
From there, it's a trivial solution.

[03:59] This still doesn't work. Find out why. Fix. Goodnight!

[15:48] Managed to set up a `launch.json` to debug efficiently.
It runs `exe.py` from `Scanner`, not from the root directory,
which is good because it can now access the same files as regular execution!

[15:55] BUGFIX: `SpecialInformation.__setitem__` recognised only `(Entity, key, value)` and not `(Entity, dict)`.

[16:14] I can't figure out why -- the popup immediately crashes,
but only that of Device Profile, not for example General Information.
I've tried to understand why using a breakpoint and analysis of the variables,
but I found nothing out of the ordinary.
Also, not entering an address causes a crash.
Instead, I'll start separating the code into files,
which will make navigation easier.

[16:58] Use ChatGPT to generate this:
```py
class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class MyClassExample(metaclass=Singleton):
    def __init__(self):
        self.text = "bubbles"
```
Suggestion: Consider using this on Register, NetworkStorage, SpecialInformation, etc.

[17:19] Moved code from `main.py` to a new file called `SimpleScan.py`,
and added docstrings and comments.

[17:30] Moved code to `PublicAddress.py` and `CommandLineStyle.py` from `main.py`.
The goal is to eradicate `main.py`.

[17:35] BUGFIX: incorrectly written type hint.

[17:38] `remove_scapy_warnings` would ask for 3 confirmations if PermissionError and "If you're sure you've got everything correct, press any key to continue. . .".
I added a `return`, so now only one confirmation is requested.

[17:46] Moved code to `OS_ID.py`.

[18:07] Moved code to `ScanID.py`.

[18:08] BUGFIX: exception logger won't show datetime.

[19:24] Added scan history module inside `class Register`, using ChatGPT:
```
Prompt: Write a class ScanHistory in Python. It's singleton. There exists a Scan class, that, before executing the scan, does `ScanHistory().add(self)`. The Scan class has a field 'name' that is a string. I need to be able to extract the scan history, as a list of names and timestamps. 

Answer: Here's an implementation of the ScanHistory class in Python that meets your requirements: [...]

Prompt: You know what? I want to do the scan history inside a class I made called Register. How do you suggest I change it to do that?

class Register(dict):
    [...]

Answer: To add scan history to your Register class, you can modify it as follows: [...]
We've added a history list to keep track of the scan history, and modified the start method to add the name of the scan and the current timestamp to the history list after executing the scan and its callback. The get_history method simply returns a copy of the history list.

Here's an example of how you might use this modified Register class: [...]

Prompt: what type does time.time() return?

Answer: The time.time() function in Python returns the time in seconds since the epoch as a floating-point number. Specifically, it returns the number of seconds that have elapsed since January 1, 1970, 00:00:00 UTC (Coordinated Universal Time), not counting leap seconds. The returned value is commonly referred to as a Unix timestamp.
```

[19:27] And that concludes all three modules I wanted to add.
Just use Scan History in `files.py`, and that's it for additions for now.
So, I need more testing, bugfixing, solve attention grabbers (***********), and implement the rest of the scans.



### 2023-04-11
[20:41] Alright. Let's see what I can work on today.

[21:17] Working on `files.py`. My changes:
- Added scan history: `timestamp (4 bytes) + name (encoded string) + duration (3 bytes)`, from `Register().get_history()`
- Parse scan history in `importer()`: e.g. "2023-04-11 21:17:05 ICMP Sweep for 12[s]."
- `ScanFileBuilder.parse`: `scan_id, entities, history, *rest = self.parts` and make sure that `rest` is empty.
- Parse scan history in `ScanFileBuilder.parse`: {first 4 bytes} + {middle part} + {last 3 bytes}
```py
(x[:4], x[4:-3].decode(), x[:-3])
```
- Comments encouraging me to encode NetworkEntities more efficiently, and move that responsibility to `NetworkStorage.py`.
- Don't encrypt/decrypt if the `password == ''`.
- Removed printing statements in `ScanFileBuilder.write_to` because I can now use an actual debugger.
- In `register.py:Register`, I changed the form of `self.history: list` to be: `[name: str, start_time: int, duration: int]`
- In `register.py:Register.start._add_callback`, I used the mutability of lists to update the `duration` value upon returning from the `action()`.
- In `register.py:Register.get_history`, I'm returning a list of tuples.

[21:30] BUGFIX: Misplaced parentheses: `packet[ARP.op] should have been `packet[ARP].op`.
This should not have been overlooked for so long.
LESSON: Just goes to show I need more testing.

[21:39] With the help of ChatGPT, and a bit of convincing it, I made `PacketSniffer` an iterator (with `yield`s).
This must be done, because `OS_ID.py:19: for packet in PacketSniffer():` requires it to run.
I chose to use `yield`s because, for many packets, I wouldn't have to store them all in dynamic memory,
which would be quite intensive. Instead, I'm fetching them one by one.
Also, make a copy of `self.packets`, to avoid multiple-threads-accessing-the-same-list issues.

[21:46] BUGFIX: I wrote `here.ipv4` instead of `here.ip`
The previous error was in the previous line in `OS-ID` (21:30).
It's clear that this scan wasn't tested lol.

[21:50] BUGFIX: NetworkEntity doesn't have default values.
The previous two errors (21:30, 21:46) were in the previous two lines (that aren't comments or trivial `continue`).
This just goes to show: one must test their code after writing it.

[21:52] Suggestion: you can improve boot time if you just move `remove_scapy_warnings` to after the GUI loads.
It's just a cosmetic anyway.

[21:57] BUGFIX: `packet` object requires referring to scapy layers.
Same function. I really needed to test it right after I wrote it.
Thankfully, it's quite simple (because I write clean and clear code lol),
so it's easy to debug.

[22:01] Suggestion: I've added some infrastructure.
Perhaps extract some information from it and present it under General Information?
Suggestion: turn `NetworkStorage` into an SQL-integrated container too, like PacketSniffer.
Maybe even have a superclass to do that.
Suggestion: use draw.io to draw flowcharts of how the code is structured.

[22:58] BUG: `sqlite3.OperationalError: database is locked`.
In thread `PacketSniffer:AsyncSniffer`, I have a `_flush_packets` that tries to access the database:
```py
with sqlite3.connect(self.DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.executemany(PacketSniffer.INSERT_STATEMENT, packets_to_insert)
    conn.commit()  # right here the exception is raised.
```
However, in thread `Scans.OS_ID.operating_system_fingerprinting._fingerprinter`,
I call `PacketSniffer.__iter__`,
which also tries to access the database:
```py
while True:
    packet_row = self.cursor.fetchone()
    if packet_row is None: break
    yield something_from(packet_row)
```
And the clash causes an exception from sqlite3.
I thought of two possible solutions:
1. Solve from `_flush_packets`: Place the `conn.commit()` in a try-except block, and try again, until it allows access.
2. Solve from `__iter__`: Save the query result to a variable and yield from there.
The problems:
1. It might never be freed, and that's an infinite loop.
2. It's a heavy load on the RAM, which is the whole reason why I'm using `yield`s there.

[23:32] First, google the error.
Then, enter Stack Overflow.
https://stackoverflow.com/questions/3172929/operationalerror-database-is-locked
Then, follow the link from a comment that makes sense:
https://stackoverflow.com/questions/53270520/how-to-know-which-process-is-responsible-for-a-operationalerror-database-is-lo/53470118#53470118
Now, I know I need to close the cursor.
So, I've asked ChatGPT to rewrite `class PacketSniffer` and remove `self.cursor` and `self.db_conn`.
I was slightly annoyed by the token limit it had on responses, but I got it to work.
Just copied the result, did some code review on it.

[23:42] And....... Still doesn't work.

[23:44] Since I know how I'm inserting and changing stuff in the SQL database,
I can just have a counter that goes up by one (in `__iter__`),
and yield the packet with that ID.
I can even use `get_packet`, it's that easy.

[23:52] BUGFIX: Well, the error's gone now, so it worked!

[23:57] I've moved `remove_scapy_warnings` to `CommandLineStyle.py`,
and added a justification for that in the `if __name__ == '__main__'`.
This makes `main.py` completely empty! Yay!

Just some stuff from `main.py`'s unmaintained code,
that might be useful in the future:
```py
def add_to_lookup():
        NetworkStorage().add(ip="255.255.255.255")
        from NetworkStorage import router, here
        NetworkStorage().add(router, here)

def do_TCP():
    from NetworkStorage import router
    print(f"Open TCP ports in {router}:")
    with JustifyPrinting():
        for port, res in scan_TCP(router.ip, repeats=20).items():
            if res:
                print(port)
```



### 2023-04-12
[00:14] Update `ImportDefence`: catch `ImportError`s too and log an error about them.

[00:34] Reduce the amount of `parallel_device_discovery` threads in `Live ICMP` from `18` to `6`.

[01:08] BUGFIX: In `files.py:get_password`, missing return statement.
I was tracking a bug for too long: I forgot to `return`.

[01:29] I noticed the program doesn't close,
even after the window is:
some threads keep running.
So, I did some changes in `gui.py`, `exe.py`, `globalstuff.py`:
moved the `terminator` to be in globalstuff.
Use the terminator in `threadify` too.
I also added a `sys.exit()` under `_resolver`, to ensure everything was closing.

[01:32] Got a `RuntimeError: cannot join thread before it is started` in `threadify`,
because some threads were not started when I closed the window,
because `terminator` was set.
Solution: wrap in try-except and ignore `RuntimeError`s.

[01:37] Now closes much faster!
TODO: split `gui.py` into files,
preferably under the folder `GUI/` if possible.

[16:46] Going over `util.py`, adding typehints, improving docstrings, writing comments.

[17:57] Added time limit for `@memorise`.
Tested on a simple `fib` method in IDLE.
Testing worked.
I'm going to choose 180 seconds as the time limit (3 minutes),
because that won't clutter up the software too much,
but it will allow for new, say, `hostify` entries within a reasonable time.

[18:09] Added exception for None-returning functions in `@one_cache`.
As well as docstring upgrades and comments.



### 2023-04-13
[01:58] Improved, I'd say polished, the `util.py` module.
Added typehints, wrote comments, and updated docstrings.
Also changed code (moved expressions out of conditional into variables) to make it clearer (in `JustifyPrinting`)
Added printing as the module's description.

[16:35] I've been dreaming tonight, mostly about time travel, but a bit about the Recommended Scan feature.
I've realised the idea is close to AI ML Transformers,
where you feed it an ordered list of tokens (words for language models, past scans for me),
and you get a probability list for the next token (which would be the Reccomended Scan).

However, this requires too much training data,
and will be heavily biased by my own choices of which scans to run if I train it on my behaviour,
so a better option is to have a probability list that gets updated based on each scan that's executed.
That would simply fall under `Register`'s responsibility.

Perhaps I could design a Directed Graph (nodes = scans),
whose edges would show the "supportiveness" of each scan towards the others.
But that doesn't allow me to get much context:
for example, if the user did ICMP Sweep thrice in a row, I'd recommend Live ICMP.
Or, maybe I can do that with the proposed system?
I'll have to think more, design some stuff, and write some code.

[19:15] I want to draw some stuff.
E.g. I already have a vision for how to explain `@threadify` visually.
I'll use `draw.io`, or at least try, and I'll see what I can get.

[19:50] In `util.py:@threadify.wrapper.task`, in line 194, there was this comment:
```py
# Force the function to end within a given timeout!
```
I removed it, because I no longer deem the addition of this feature necessary.
Also, "if it ain't broke, don't fix it", but this really seems useless,
because `threadify`-ied functions are not usually long tasks.
So, this can be considered as moving responsibility:
timeouts are the responsibility of `f`, not `@threadify`.

[20:38] I've just created two diagrams on `draw.io`: of `@threadify` and of `@memorise`.

[20:40] Dissolving `util.py` into different files. Moved all the printing classes to `PrintingContexts.py`.

[20:43] Moved `print_dict` from `util.py` to `CommandLineStyle.py`.

[20:45] This function wasn't used anywhere (from `util.py`):
```py
def nameof(action: Callable) -> str:
    """Returns a short description of a function by the following logic:
    If a docstring exists, and its length is less than 100 characters, return the docstring.
    Otherwise, return the function's name.

    Args:
        action (function): the function to be named. Primarily, functions intended to be used as actions.

    Returns:
        str: the name chosen for the function.
    """
    if action.__doc__ and len(action.__doc__) < 100:
        return action.__doc__
    else:
        return action.__name__
```
It was probably in `main.py`, but it went into unmaintained territory.

[22:23] Moved `shift` and `render_opacity` from `util.py` to `scans/ICMP.py`,
because they are only used under that module.

[22:27] Moved `one_cache` and `memorise` into `Decorators.py`.
Renamed to `CacheDecorators.py`.

[23:07] Worked on `test.py`:
added printing statements as description,
changed `tests: list` to dynamic with help from ChatGPT and the `inspect` module,
added comments.
This has changed tests_log.txt because the order of the functions is now different.

[23:10] Sort `tests.py`'s `tests: list` in alphabetical order.

[23:12] Deleted `logs.txt` because it wasn't used anywhere.
Probably from an older version of `tests.py`.



### 2023-04-14
[10:25] I'm gonna sketch a simple Python programme to calculate a probability list,
and apply steps to it with a Directed Weighted Hardcoded Graph.
This is to see if I can design such a system,
or if I should design such a system,
for the `★ Recommended Scan` feature.

[11:04] Update on that.
I have a system that takes in a hard-coded graph of scans,
creates a static probabilities list,
and renders the graph with matplotlib.
The rendering allows me to see all the labels,
the connection strengths (as colours),
and the probability of each node (as colours).
TODO: I'll add normalisation for the `probabilities: list[float]`,
and add an ability to choose (randomly) and update probabilities.

[11:23] Trying to normalise the probabilities.

[11:37] Brainstorming with mom, I wrote the following on a piece of paper in red ink:
```
(11:37)
 - - - - - - - - - -
|   ↷               |     ╭         ╮
    (1)   ←→    ↶         | 1: 30%, |
|             (2)   |     | 2: 10%,  |
                          | 3: 40%,  |
|       ⭦   ⭧       |     | 4: 20%  |
         (3)      ↷       ╰         ╯
|         ⭮     (4) |           ==
 - - - - - - - - - -            100%


Act 2.
Keep sum → constant.
Take from (-) connections and flow over to (+)'s.
```
And on the other side:
```
look at node 2's connections.
edges[2] = ┌ 1: +0.4, ┐
           │ 2: -1.1, │
           │ 3: 0,    │
           └ 4: 0     ┘
```

[11:48] And on another piece of paper,
an enlagred version of the graph (which I'm not gonna waste time drawing, again),
and this conclusion:
```
11:48
Treat probabilities as fluid, that flows,
and normalise.
```

[11:55] Went upstairs to digitalise all the papers.

[12:31] Ate hummus (it was good), ready to implement.

[12:45] Use ChatGPT to quickly write the code to render the adjacency matrix of G,
on a second subplot.

[13:52] Polished the matplotlib result.
I still need to enter actual values for the edges' weights...
IDEA: I could make the edges' weights dynamic, and change based on choices.
how would I do that, though?
Maybe, each time a user chooses Action 1 and then Action 2,
I could strengthen the link between them.
For now, the connections are static.

[15:35] I've started implementing ListWithSQL.
However, this is a really long task.
So, this is my progress so far,
and from now on Imma try to use ChatGPT to fill the rest.

[15:37] Unsurprisingly, I made a mistake.
Surprisingly, ChatGPT caught it and fixed it for me.

[16:39] There used to be some f-strings and a `self.tablename: str` field,
but I removed it and hardcoded it to "list_with_sql",
to prevent the slightest chance of an SQL injection.

[16:41] I asked ChatGPT to write some tests for ListWithSQL too,
because that was too much code to write without testing,
for both a human and an AI.

[16:46] BUGFIX: don't forget to clear the table before creation!

[16:52] Finished creating and running the test.
The implementation of ListWithSQL worked surprisingly well.



### 2023-04-17
[22:25] Working on decomposing `gui.py`.

[22:30] It's more intertwined than I thought.
So, I'll just continue splitting the code into files,
and bear with the import warnings for now.
Then, once it's all split, I'll handle the importing.

[23:44] Moving the gui code to under `./gui/`,
to not clutter up the main folder.

[23:51] Please finish decomposing `gui.py`,
because the current build will not work.



### 2023-04-19
[11:36] Working on the project from school, after a long Passover break when I haven’t interacted with the school network and devices.

[11:37] ImportDefence didn’t work on `import requests`, and weirdly entered the “You've misnamed your import. Check it.” print, even though it IS a ModuleNotFoundError. Within a minute of googling I found out that ModuleNotFoundError is a subclass of ImportError, and thus the error would be caught in the first clause, which is problematic.
Solution: move the `except ImportError` to after the `except ModuleNotFoundError`, not before.

[11:43] This computer now has no pip packages. This can be checked with `pip freeze`, which returns an empty output here. I’ll now execute the software and measure the time it takes to load and pip-install all the packages, using my watch.

[11:46] `pip install Crypto` gives an infinite loop :( – 2 minutes 50 seconds before it got stuck.
Solution: add this in `import_handler.py:85`:
```py
if 'Crypto' in to_install:
    to_install = 'pycryptodome'
```

[11:54] Technically 00:35, but it was probably cached somewhere, so don’t treat this as an actual value for a new machine.

[11:58] PyCharm* is mad that the directory `gui` isn’t a module or whatever, so add an empty `__init__.py` file in it.
(*) Yes, I’m using PyCharm. I don’t like PyCharm. I have VSCode at home, which is much more comfortable, and in class I usually use Notepad++, but it’s useless for debugging.

[12:00] Consider using PyCharm to optimise imports, something I’ve been wanting to do.

[12:01] That’s enough for now. I’m gonna do something more fun: work on the MultiMouse project! Once the dissolution of `gui.py` is complete (at home, with Git), I’ll run the software here; I really hate the heat (it’s 32°C!!).

[15:43] Applying all the changes from back home.

[15:53] I just realised, and this is kind of big, that I could try using `matplotlib` to render the graph,
which would be more efficient, more elegant, more beautiful, and simpler.
I just need to find a way to automatically update a networkx graph on a matplotlib.pyplot plot.
Using this comment on Stack Overflow:
https://stackoverflow.com/questions/59794523/how-to-update-a-networkx-plot-in-real-time
And ChatGPT, I made this code snippet:
```py
import networkx as nx
import matplotlib.pyplot as plt

# assume `G: nx.Graph` exists

# initialize the plot
fig, ax = plt.subplots()
pos = nx.spring_layout(G)
nx.draw(G, pos, ax=ax)

# main loop
while True:
    # clear the plot and redraw the graph
    ax.clear()
    pos = nx.spring_layout(G)
    nx.draw(G, pos, ax=ax)

    # draw the new plot and wait for a short time
    plt.draw()
    plt.pause(1)
```

[16:05] With IDLE, I created a working prototype for this behaviour (updating graph on matplotlib):
```py
# start this on another thread
def add():
    while True:
        G.add_node(int(len(G)))
        sleep(1)


# start this on the main thread
def render():
    fig, ax = plt.subplots()

    while True:
        H = G.copy()
        pos = nx.spring_layout(H)
        nx.draw(H, pos, ax=ax)

        plt.draw()
        plt.pause(1)

        ax.clear()
```

[16:09] I'll keep decomposing `gui.py`, because it's impossible to do testing like this.
Then, I'll try to implement the `matplotlib` upgrade.

[16:11] Renamed `color_hex` to `color_to_hex`, and moved to `util.py`.

[16:18] Renamed `add_font` to `add_fonts`, and moved to `gui/KivyFonts.py`.

[16:20] I added the Zentabs extension to VSCode, because there were too many tabs open.
This is an extension I'm familiar with from Atom, and it extends easily to VSCode.

[20:32] Created `gui/Screens/ViewScreen.py`.

[20:33] Removed `prestart`, and moved the two statements to more logical places:
- `G.add_node(router)` -- in `exe.py`, near a similar statement `NetworkStorage().add(router, here)`.
- `start_kivy.__name__ = 'Main GUI Thread'` -- right after the definition of `start_kivy`.

[20:42] With the assistance of ChatGPT, I came up with the name `dialogs.py` for the next file.
It's simple, and obvious in hindsight, but it was kind of difficult to come up with.
ChatGPT's power really shines in natural language (after all it's an LLM),
so using it to generate words and synonyms given context is quite good.

[20:58] Moved `popup` and `get_string` to `gui/dialogs.py`, and added docstrings.

[21:02] Created `gui/Information.py`. I don't really like the name, but it's fine.

[21:05] Add imports in `gui/Screens/SaveScreen.py`.

[21:11] Wow naming is difficult. I created `gui/ScanButton.py` and changed it to `gui/ScanClasses.py`,
because it doesn't contain an actual UI button.

[21:22] Added `Activation.py`, `Diagrams.py`, and `AppState.py`, all under `gui/`.

[21:35] Converted State into a Singleton.

[21:44] After fixing many many many imports,
I believe that's all with the import warnings.
`gui.py` is almost fully dissolved.

[21:49] Deleted `gui.py`. All the code has been migrated to the directory `gui/`.

[21:52] Finally, I might be able to execute the whole software again.
Place your bets! I feel like there's a 95% chance it's not gonna work on the first try,
and 70% chance that there are at least 5 errors to fix.

[21:54] Circular import. Am I going to suffer going through the Circular Import Hell again?
```
Exception has occurred: ImportError
  Hover.py:3:
    from gui.AppState import State
  gui\AppState.py:6:
    from gui.Hover import Hover
  gui\App.py:6:
    from gui.AppState import State
  gui\StartApp.py:7:
    from gui.App import MyApp
  exe.py:34:
    from gui.StartApp import start_tk, start_kivy
ImportError: cannot import name 'State' from partially initialized module 'gui.AppState' (most likely due to a circular import)
```

[22:07] Alright that wasn't too hellish, I just drew a graph on paper to understand,
and changed to dynamic (inside-method) import.
That's error 1, solved. My 95% bet won.

[22:13] Another circular import. Expanded the paper graph,
changed more imports to dynamic (more than necessary to prevent more errors).
That's error 2, solved. Will we get to the 70% bet?

[22:14] That's technically error 3:
`from Screens.Pages import Pages` should have been `from gui.Screens.Pages import Pages`.
Whoops. Fixed now.

[22:15] Strike 4.
One of the imports had a `Scanner.` prefix to it,
because that's auto-generated by VSCode. Removed it.

[22:16] Got to the breakpoint I placed on `start_tk`. 
The tension! Will there be a fifth error, fulfilling the bet? Will it all work as intended?

[22:18] Ladies and gentlemen, the gui has rendered!
And then there's an import error in `keep_resolving_storage`...
So, I'll leave that as a tie between winning the bet and losing it.
There are no stakes anyway lol.

[22:20] There were two hanging dynamic imports of the shape `from gui import something`,
in `keep_resolving_storage` and `files.py:get_password`.
I changed them to the updated modules.

[22:23] My bad, I imported from the wrong novel module.
```py
from globalstuff import update_know_screen
from gui.Diagrams import diagram  # this is None
```
fixed to:
```py
from globalstuff import update_know_screen, diagram
```

Debugging is so much easier with VSCode.

[22:32] I ~gave up on diagram from globalstuff~ am taking another approach to solving why `diagram` stays `None`.
I'll change `Diagram()` to a Singleton. Singletons to the rescue!

[22:44] Good singletons have their initialisation in __new__, not __init__.
I had ChatGPT move the initialisation code and use `cls._instance` instead of `self`,
because it's a repetitive task and boring. I could try to have a Find&Replace do that,
but ChatGPT's input is in natural language, which is faster to think about for me.

[22:50] I found the mysterious network entity printing!
It comes from `update_know_screen`,
if it's not yet converted to a gui action,
and remains a printing statement.

[22:56] Moved the responsibility on `update_know_screen` and `update_view_screen`
exclusively to `gui.Screens.KnowScreen` and `gui.Screens.ViewScreen` respectively.

[23:04] `test.db` uses timestamps, so it changes on each execution,
but doesn't provide information worthy of being uploaded to github,
so I added it to `.gitignore`.
You can generate it from the code that is present, anywhere.

[23:07] TODO in Cyber class tomorrow:
- More testing on another network
- Try starting to add the `matplotlib` diagram instead of tkinter's. (Cleanse the project from tkinter)
- Investigate why Device Profile crashes everything.



### 2023-04-20
[15:45] Working on `Diagrams.py`, to simplify the code and add easy support for future types,
specifically `matplotlib` as discussed earlier.

[16:13] Please keep working on `Diagrams.py`!
It is not complete, and not stable, to say the least.
I won't commit to git yet so you can easily see changes.



### 2023-04-21
[14:26] I spent 6 minutes installing setting up a good-looking status bar clock,
in the VSCode editor.



### 2023-04-22
[20:31] Continue working on `Diagrams.py`.
See GitHub commits for the progress and decisions.

[20:58] Started working on the Project Portfolio.

[22:22] Worked on an empty Project Portfolio,
to later add my information into.
This will constitute 30% of my grade!

[22:40] Changes in `TKDiagram`:
- remove `self.renew` (unused).
- remove `self.graph` (unused).
- use `self.color_cache` instead of `self.color` in `get` operations.
  Use `self.color` only in `set` operations.

[22:47] Add docstring to `KivyDiagram`.

[22:51] Fix `StartApp.py` to accommodate the new changes in `Diagrams.py`,
and have the software ready for testing.

[22:53] Removed `gui.bat`, a remnant from the GUI creation and fine tuning.

[22:54] The software crashes when started from `run.bat`,
without a visible exception. So, execute with VSCode debugger.

[23:00] Bug: `KivyExtensions.py` still uses `update_kivy_diagram`,
which is no longer supported after the `Diagram.py` overhaul.
Solution: update to the new version. However, this requires changing KivyDiagram to a Singleton.

[23:07] Changed `KivyDiagram` to a Singleton with minor assistance from ChatGPT.

[23:10] `TKDiagram` uses the default implementations of the `ContextManager` methods,
so you can just not override them.

[23:21] BUG: Apparently it dislikes when I don't override `__exit__`
(in professional terms: the `__exit__` method is defined as abstract in `ContextManager`)
Solution: revive the overriding of `__exit__`.
However, `__enter__` is fine not being overriden.

[23:25] Python uses `.append` to lists, not `.add`. :facepalm:

[23:28] Add protection against `RuntimeError`s around `TKDiagram().show()` (when terminating).

[23:46] Error logging from `StartApp.py` now redirected to `error log.txt`.

[23:47] UnicodeEncodeError -- fixed with specifiying the encoding.

[23:51] I need to "suck up" any leftover arguments from kivy's call to `KivyDiagram.update`.
Additionally, `Diagrams().update()` needs no argument.

[23:56] Turns out you can keep raising exceptions in Python, and the `finally` block still runs,
so do that for `StartApp.py`. https://stackoverflow.com/questions/49262379/does-finally-always-execute-in-python

[23:58] Added this line in `KivyDiagram.update`
```py
assert self.widget is not None
```
Suggestion: Consider changing all its occurences in `KivyDiagram` to a type check, like:
```py
assert isinstance(self.widget, MyPaintWidget)
```
with the necessary import. Also, ensure that this prevents `None`s from passing.

[23:59] The assertion fails. If it's removed, another error is raised. Find out why the widget is None, and consider these solutions:
- (internal responsibility) skip updating when the widget is None
- (external responsibility) don't call `.update` before calling `.set_widget`.
Currently a non-functional version, solve this bug.



### 2023-04-23
[20:39] Placed an if and a breakpoint to debug why the assertion fails.
```py
if self.widget is None:
    print("Whoops")  # Breakpoint here
```

[20:44] Solved by moving the responsibility on setting the widget to outside the class `MyPaintWidget`.
This previously failed because it was inside `.init` of` `MyPaintWidget` (no `__`, just `init`, 'cuz Kivy),
which is probably called too late.

[20:48] Next error: `TypeError: Cannot create graphics instruction outside the main Kivy thread`.

[21:04] Solution: Move the `render_diagram` call in `KivyDiagram.update` to a `<lambda>` under `kivy.clock.Clock.schedule_once`.
Then, it schedules the action ON THE MAIN KIVY THREAD, and won't raise that bug.

[21:08] BUG: `TypeError: <lambda>() takes 0 positional arguments but 1 was given`.
Solution: Instruct the lambda to ignore arguments: `lambda *_: ...`.

[21:11] Run `autopep8` on `gui/Diagrams.py` and manually fix some changes I didn't like.

[21:14] BUGFIX: Update `Diagram()` (which is now abstract) to `TKDiagram()`.

[21:28] BUG: `RuntimeError: main thread is not in main loop`
Basically an identical error, just on tkinter and not kivy.
How funny.
Solved with `self.root.after(<ms>, <action>)`.

[21:33] Protect around `self.root.after` against `RuntimeError`s.

[21:34] Doing some PEP8 fixes, these are the commands:
```bat
pycodestyle "C:\...\Scanner" --ignore=E501,E731,E402
autopep8 "C:\...\Scanner" --in-place --select=W293,E303,E305,E302,E701,E226,W191,E101,W391,W504,E125,E231,E306,W291,E301,E126,E121,E225,W191,W503 --recursive
```

[21:40] That fixed so many whitespace or newline inconsistencies.
I manually scrolled to make sure nothing is too bad, but it seems alright.
22 Changed files.

[22:11] Even more whitespace/newline changes! With my supervision, ofc.
Using `pycodestyle`, I'll now correct style issues manually,
that were not fixed by `autopep8`, and the code'll be perfect!

[22:51] Corrected *all* of the PEP8 warnings!
The output of `pycodestyle ...` is empty, ignoring these warnings:
```
E501 line too long (X > 79 characters)
E402 module level import not at top of file
E731 do not assign a lambda expression, use a def
```

I chose to ignore them for the following reasons:
1. long lines are not too bad, they are more readable than the alternative.
2. I have `import_handler.ImportDefence` that improves execution on a new computer by automatically pip-installing,
   and I do not wish to give up on that. It's a context manager, so this warning will appear.
3. I like lambda expressions, where they're more readable.
All in all, you need to consider PEP8 guidelines to maintain consistency internally and between programmers,
but you also need to exercise discretion.

[22:58] Counting the lines in the directory usign the `VSCodeCounter` extension.
| language | files | code | comment | blank | total |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Python | 46 | 3,360 | 1,405 | 868 | 5,633 |
| Markdown | 1 | 1,549 | 0 | 669 | 2,218 |
| Batch | 4 | 47 | 1 | 13 | 61 |
| Database | 1 | 38 | 0 | 1 | 39 |

It's only 5,633 lines of Python code (in total!),
so it seems improbable that I'll get the bonus for "extensive project".
Unfortunate.

[23:04] I just closed VSCode/GitHub Desktop, and then remembered I still have to implement `PlotDiagram`!

[23:20] Consider adding an abstract class `DiagramWindow` with methods `show` and `hide`,
and enforce it on `PlotDiagram` and `TKDiagram`, not `KivyDiagram`.

[23:31] ChatGPT proposed:
```
To solve this issue, you can use Matplotlib's built-in mechanism for running the GUI in a separate thread by adding the following code at the beginning of your script:
    import matplotlib
    matplotlib.use('TkAgg')

Another option is to modify the show() method of PlotDiagram to run in the main thread using run_in_main_thread function from the kivy.clock module.
```

[23:48] Currently, `PlotDiagram` doesn't work (due to multi threading issues probably).
Reverted to `TKDiagram` for now.



### 2023-04-28
[15:21] Gonna start debugging why Device Profile crashes the app.

[15:25] Everything seems fine, up until the `dialogs.popup`.

[15:32] Added a title to `get_string`.

[15:46] Testing in IDLE resulted in no error or crash.

[16:02] Maybe the thread is the problem? Nope, tested this on IDLE:
```py
message = '### mac:\n**-**-**-**-**-**\n\n### ip:\n10.0.0.***\n\n### ipv6:\n****:****\n\n### name:\nDESKTOP-****** (censored)'
popup("Device Profile", message, info=True)
>>> -1
from threading import Thread
Thread(target=popup, args=("Device Profile", message), kwargs={'info':True}).start()
>>> [awaiting next command]
```
And both popups (threadless and threaded displayed fine).

[16:03] I'm on a phone call with a friend, trying to debug this,
and he proposed to check the Python versions on IDLE and VSCode,
to see if they are matching.

[16:07] They are matching. printed `sys.version` on both. 🙁

[16:11] Notice, when I close the `get_string` before inputting,
it crashes too. Why is that?

[23:11] Another friend had a problem with `pip install`,
so I updated `import_handler.py` to solve it automatically,
and sent him the file.

[23:59] Working on TraceRoute scan.
Registered the scan (hardcoded to `dst=8.8.8.8`) in `exe.py:register_scans`.
Added `connections = Queue()` in `NetworkStorage.py` to save graph connections that should be added.
Added `connect(ip1, ip2)` to insert to this queue.
Added, in `_resolve`, logic to add the necessary edges from the `connections` queue.
The code in `TraceRouter.py` has two functions now:
- hop: checks the host thrice for responses, and returns the ip (or `'Timed Out'` or `'Undefined'`).
- traceroute: hops a bunch of times and adds the results to `NetworkStorage`.



### 2023-04-29
[00:05] Traceroute is working now.
I'd just like to say it was super easy to implement,
honestly, it took so little time!

[00:08] I texted a friend of mine with the results, and am image of the network graph.
He nicknamed it 'A Pendulum Of Computers', and it kind of looks like one.



### 2023-05-01
[16:26] I tried debugging this further (Device Profile crashes).
I got assistence from a friend, a smart friend.
Nothing. We couldn't solve it. Together.

[16:27] Asked ChatGPT for an alternative to `PyQt5`, for `popup`.
It suggested `easygui`. I gave it the docstring, with some changes,
and asked it to remake `popup`. It did.

[16:36] It failed, and corrected itself,
but that would've required me to have image files in the directory,
rendering each of the icons. 
So I asked it to propose another alternative, and it came up with `PySimpleGUI`.
Rewrote it with `PySimpleGUI`.



### 2023-05-02
[00:22] The markdown part of `popup`, now using a different library,
is now functional. It still doesn't solve the `Device Profile` crash issue,
but it's nice to have it!

I'll save the previous implementation (PyQt5), now the code has the newer one (PySimpleGUI).
**`gui.dialogs.py:popup` using `PyQt5`:**
```py
        with QApplication([]):
            md_text = markdown.markdown(message)
            html_text = f"<html><body>{md_text}</body></html>"

            popup = QMessageBox()
            popup.setWindowTitle(title)
            popup.setTextFormat(Qt.RichText)
            popup.setStandardButtons(QMessageBox.Ok)
            popup.setEscapeButton(QMessageBox.Ok)
            popup.setDefaultButton(QMessageBox.Ok)
            icon = QMessageBox.Critical if error else QMessageBox.Warning if warning else QMessageBox.Question if question else QMessageBox.Information
            popup.setIcon(icon)
            popup.setText(html_text)

            popup.exec_()
            return -1
```

[01:12] Small bugfix: scans' information wouldn't show the packet breakdown,
because it would be escaped as HTML and not rendered.
So, I just removed the `html.unescape`!

[01:45] Added HTML formatting for the packet OSI models,
when showing information about scans,
all under `gui.Information.py:information_about`.

[19:59] Tested CSS on the new popup graphics library (PySimpleGUI).
I'm honestly surprised, it is incredibly simple. Not trivial, but simple.
Anyway, CSS does work, and that's good.

[20:12] Suggestion: move popup code to a different thread,
maintain a `Queue` of messages to display,
and resolve it in the thread.
This way, there'll never be more than one popup,
and there is NO WAY it will keep crashing in `Device Profile`.

[20:29] Used ChatGPT to generate `PopupManager` (Singleton, contains Queue, maintains Thread),
after some brainstorming regarding a good way to do it.

[20:51] Done with creating `PopupManager`.

[21:24] Used https://www.tablesgenerator.com/markdown_tables to generate a table in the docstring,
to explain and differentiate the two behaviours of `popup`.

[21:31] Moved magic numbers to constants in `dialogs.py`.

[21:35] BUG: `sqlite3.OperationalError` on `cursor.executemany(PacketSniffer.INSERT_STATEMENT, packets_to_insert)` in `PacketSniffer.py`.
Solution: extend the `try`-`except` block to be around this call too.
Explanation: It'll be fine,
because the reasonable thing to do here would be to wait a bit and then try to commit again, in a loop.
This does that automatically, because of:
```py
if len(self.packets) >= self.max_packets:
    self._flush_packets()
```
Every time a packet is added, it flushes, so it acts like a "wait and try again repeatedly" mechanism.
There won't be loss because Python lists can handle a dynamic size, specifically 100 and above.

[21:50] Made the popup window non-resizable, because scrolling is allowed.
Allow only vertical scrolling, not horizontal.

[22:02] BUGFIX: `Column.__init__() got an unexpected keyword argument 'vertical_scroll_only'`.
It seems `PySimpleGUIQt` uses a different argument set to `PySimpleGUI`. Solved with ChatGPT.

[22:34] More elaborate messages in popups, because the space looks otherwise unused and empty.

[22:40] Duplicate linebreaks before markdown parsing, because markdown treats only `\n\n` and more as linebreaks.
Plus, more linebreaks aren't gonna hurt anyone.

[23:05] I believe major progress was done today,
regarding the solution to Device Profile's crashing.
Still not fully solved, but on the way.

Insights:
the popup opens, and then the whole application crashes even before the contents are rendered.
The app does not crash if `_device_profile` is not called.

[23:12] It no longesr crashes in the specific case of `if entity is None`,
but still in the general case, even if executed from a thread.

[23:57] Remove padding and border in the GUI of popup (PySimpleGUI).

[23:59] Keep in mind it's not uniform in PySimpleGUIQt... Fixed.

### 2023-05-03
[00:28] Moved `POPUP_CSS`'s contents to a `.css` file.

[00:29] Import naming issue: just `import queue`. 

[00:31] Just trying whatever might work, I'm close to giving up on this:
- Moved to outside function, not in `class KnowScreenDeviceProfileButton(Button)`.
- Just print the content to the console.

[00:40] Stop the `PopupManager` thread when the application leaves.

[00:46] My debugging has led me nowhere.
When I hardcode the data to the popup, it works.
It manages to fetch and format the data correctly.
It crashes with no reason!
Inside a try-except block.
Execution of the popup is on a different thread, and works!
The only thing that's passed onto this different thread is some strings.
It works in IDLE.
This makes perfectly zero sense, and I give up for now.
Printing is good enough.
I might continue debugging it tomorrow.

More angry text in the github commit.

[01:29] I've diverted my efforts to another thing I want for the project.
It's a simple Python file, I'm just having ChatGPT write it for me,
part-by-part, with supervision; it creates a graph of connections between `.py` files,
according to their imports, under a specific directory.

[02:20] Still working on it.
Gonna upload a functional although unpretty stable build to github,
so that any unexpected event (like,,, umm... idk, if I wrote something here it'd be expected) doesn't delete my progess.

[02:37] Just manually inserting positions for the nodes...

[03:12] Stable build.
Trying to find some library (not matplotlib) that'll allow me to render the graph and drag nodes.
I might have to use PowerPoint lol.
Anyways, it's really late. Goodnight!



### 2023-05-04
[02:42] Working on a diagram using `draw.io`,
regarding the modules of my software.

[02:49] Manipulated the internal XML of the file,
and inserted ellipses with the file names,
using the parsing I recently made on `imports_diagram.py`.

[03:00] I'm making the connections according to the code,
and the logical relationships between the modules.

[03:27] This helped me find an incorrect import statement,
in a file that's rarely used, and correct it.

[03:28] And helped me update the register `MessageBox` to a `popup`.

[03:43] I've made fair progress on the connections,
it's mostly all done except GUI.
Now, I've diverted my efforts to rendering a different type of information,
using colours, to display different parts of my system.
I've currently got GUI - Green (with different hues for: Initialise, Main, and Screen);
and File System - Blue (with a different hue for each file).

[15:21] Continue working on the diagram.

[15:29] TBH, this is plenty insightful regarding the arcitecture of my code,
and reflects my code-structure decisions.

[18:28] Done with the connections, did the GUI and the Scans.
I removed some unimportant connections, for the clarity of the diagram.
Now, just more colouring and labelling, and that'll be it with this diagram.

[20:56] Going over this diagram after a break,
it looks great. I like it.

[21:22] Working on popup's ability to wrap lines.

[21:29] Added a batch file to refresh the `scans.db` database,
on any changes in `db.py`. Works first try, wooo.

[21:36] Used Burp Suite Community Edition to investigate `PublicAddress.py`,
specifically the call to `https://api.ipify.org`, and how it looks.

[23:57] Did a bunch of things:
- Improved some database scans' entries. 
- Added a secondary 'by-comma' line-splitting in `popup`, after the 'by-period' splitting.
- Added a margin for the table in `popup_style.css`.
That's it. Good night!



### 2023-05-07
[16:01] I've added a (temporary) scan-like action to view the packets, using a popup.
However, I'm thinking it's much more reasonable to do that action under Know Screen.
This will unite well with Device Profile, and I can put them both in a sidebar, like in Scan Screen.
However, currently, it's in Scan Screen, and working.

[16:04] While adding this scan, I've also tried to find edge cases that my code doesn't handle,
and place conditionals or `try-except`s to catch them.

[16:12] I'm in the process of copying the button column from Scan Screen to Know Screen,
and it seems possible that this'll actually solve the Device Profile crash.
Also, I decided not to duplicate State, because a single highlighted button (between screens),
is fine, and also maybe even desireable.

[16:24] I've made so many changes, I feel like I'm gonna miss something.
Nonetheless, it's good progress.

[22:34] Went over it again, seems fine, committed to GitHub,
gonna test now.

[22:36] I should probably also register them XD.
I'm using a unified interface of `Register`.
The data whether an action is a scan or an analysis is stored in the database,
and under the responsibility of the relevant screen to insert buttons,
with the interface provided from `db.py`.

[22:45] Worked on the layout of Know Screen widgets.

[22:50] I'm satisfied with how Know Screen looks.
I've added another class in `ScanClasses.py`, `Analysis`,
but it's the exact same as Scan (inheritence),
except the background colour is blue and not green.

[22:55] Had a z-index issue -- the `Pages` weren't responding because they were behind the label.

[23:02] At last, some consistency -- finally, the `Pages` stay in the same position between screens.



### 2023-05-08
[00:19] Changed `Activation.py:activate` to ignore all arguments.
By extension, it also accepts 0 arguments, which is what the Analyse Operation asks for.

[00:23] Repositioned the Know Screen title, to be in the correct centre.

[00:24] Compacted creation of `operations` in `KnowScreenRightColumn`.

[00:33] Added boot button for analyses.

[00:34] `str` comes before `list` in Python's `join`. :sad:

[00:38] My, silly-ly, linked both Device Profile and Log Packets to the same function.
Fixed...

[00:45] More silly-ly-ness, I accidentally `'\n'.join`'ed a string.
Whoops. Took a lot of breakpoints to find that one.

[00:48] It feels like the software freezes after boot,
just until the first node of the graph is displayed.
Investigate this.

[00:52] Device Profile worked. Once.
I'm not sure this is stable at all, I'm just glad it worked.
In debug mode, I'll note.

[00:53] I used https://fontdrop.info/#/?darkmode=true to find a character for "Analyse" operation button.

[00:58] Following a friend's advice, I installed the `Draw.io Integration v1.6.6` extension onto VS Code.
Also, uploaded the `draw.io` diagrams I've been working on, to the GitHub repos.
This is gonna be useful.



### 2023-05-09
[15:44] Invert condition in `Activation.py:activate` to decrease indent.

[15:49] With ChatGPT, I changed `get_string` to use `PySimpleGUIQt` instead of `PyQt5`.
It's a lot simpler now.

[16:08] This has caused too many issues, and they are difficult to debug without good access to the threads and `Qt` system.
Therefore, more logically, I've switched `get_string` to use `Win API`.

[17:35] Switched back to `PySimpleGUIQt`.
Made `get_string` asynchronous, and unified it into the `PopupManager` interface.
Now, there won't be a simultaneous input (`get_string`) and display (`popup`).
Also, using the `callback` concept, whose architecture name I do not remember.

[18:00] Some bugfixes in `files.py`.
- `Variable referenced before assignment` -- move assignment `scan_id = result["scan_id"]`.
- Empty history raises an exception (because it interprets bytes as int).
  So, in `<listcomp>`, ignore all empty entries.

[18:02] `dialogs.py:get_string` should put the `IconType.INPUT.value` (as integer) in the tuple.
Also, improve `get_password` to actually work with the new callback architecture of `get_string`.
This is temporary -- it will be put inside `get_string` later.

[18:11] Returned `get_string` to its original interface,
with the internal implementation now handling data movement and blocking-ness,
using the code I previously had under `get_password`.
Now, since the interface is the same,
I don't even have to change other code where `get_string` is used.

[18:15] Suggestion: send the environment variable `OS` in device discovery.
And maybe also some other ones.

[18:20] Forgot to `return` XD.

[18:31] The Device Profile chrash is resolved.
I don't know when, it just stopped crashing at some point.
This is hillarious.

I'd like to write myself a TODO, now that the _thing that drives the plot_ is gone.
0. Work on the formatting of Device Profile: hide `nothing.mac` if it appears (for example), use capital letters etc.
1. Device Discovery
2. Move special entities' unique identification to `SpecialInformation` (like, `router`, or `here`).
3. Add the rest of the scans.
4. Go over the document and find stuff to implement.
5. Use `icon` in popup (`_show_text`).
6. `Ctrl+F` all "Suggestion"s in the `README.md`.
7. Resolve attention grabbers (`*********`) placed throughout the code.
8. Find and TERMINATE all pesky magic numbers in my code.

***************

[22:14] Added docstrings to `db.py`, and an entry about Device Discovery.

[22:17] Moved analyses' code to different folder and split files.

[22:26] Improved `device_profile`.

[22:33] I'm not using the exit code for a lot,
but I just thought it'd look neat in the console output.
So I upgraded `run.bat` to show it.
Resource: Stack Overflow. https://stackoverflow.com/questions/334879/how-do-i-get-the-application-exit-code-from-a-windows-command-line

[22:39] BUGFIX: `ValueError: embedded null character`, unescape all `\` characters.

[23:32] Using https://www.w3schools.com/html/tryit.asp?filename=tryhtml_basic,
and a lot of googling, and a tiny bit of ChatGPT,
I made new CSS for the Log Packets analysis.
I looks wonderful. Heavily inspired by the OSI model visualisations.

[23:37] BUGFIX: Analyses' highlight looks disgusting. Change it to blue.

[23:47] Now doing dynamic CSS-getting for popup.



### 2023-05-10
[00:27] Suggestion: Use this to improve `popup`'s scrollbar: https://www.pysimplegui.org/en/latest/?#ttk-scrollbars

[00:36] The CSS support of PySimpleGUIQt is simply not enough to do what I wanted,
which looked really good on the w3 testing site.
For reference, copy this into the web editor:
```html
<style>
table {background-color: black; border-collapse: collapse;}

table div {display: flex; flex-direction: row; padding: 3px; margin-left: 6px; align-items: center;}

td div {border: solid 1px rgb(255, 255, 0, 0.2); color: orange;}
td div div {border: solid 1px rgb(0, 255, 0, 0.2); color: forestgreen;}
td div div div {border: solid 1px rgb(255, 0, 0, 0.2); color: firebrick;}
td div div div div {border: solid 1px rgb(255, 0, 255, 0.2); color: purple;}
td div div div div div {border: solid 1px rgb(255, 255, 255, 0.2); color: white;}

div.limit-width { width: 1200px; word-break: break-all;}

</style>
<div class="limit-width"><table>
    <tr>
      <td>
        <div>Ether
          <div>IP
            <div>UDP 10.0.0.138:35195 &gt; 239.255.255.250:ssdp
              <div>
                Raw
              </div>
            </div>
          </div>
        </div>
      </td>
    </tr>
</table></div>
```

I had to settle for a less pretty design, but it's fine too.

[20:31] I got annoyed that some threads were not properly closing upon termination.
Two of them were `AsyncSniffer`s, one for `Live ARP` and another for `PacketSniffer`.
Therefore, I decided I want to extend `scapy`'s `AsyncSniffer`,
and the new functionality will be a centralised location where references to all such threads are saved,
and can be terminated nicely with one function call.

[21:15] Also, terminate OS-ID according to the `terminator: Event`.

[21:16] I could summarise all this work to two topics: graceful termination & Device Profile format.

[22:04] I don't actually wanna trim the long `value` strings,
because Device Profile should have the full information.
However, I do wanna trim it when displaying in the table.

[22:13] Well that was really easy, just added
```py
length = min(30, length)
```
in `NetworkEntity.tablestring`.

[22:35] The header of the table didn't align. Fixed.

[22:38] `TypeError: display_information() takes 0 positional arguments but 1 was given`.
Just ignore all arguments.

[22:49] Added more conditionals before stopping `AsyncSniffer`s.
```py
if sniffer.running:
    sniffer.stop()
```

[23:08] Compare `name`s in lowercase to avoid user typing mistakes.
In `DeviceProfile.py:_match_device`.
Also added a try-except around `if nothing[key] == value` to support `SpecialInformation`,
which would raise a `TypeError` in `NetworkEntity.__get__`.
Suggestion: it makes more sense to use a `KeyError` in such cases.



### 2023-05-11
[12:59] In Cyber class, the last lesson possibly, working on the project, suggesting changes and reporting bugs:

BUG: Live ARP doesn’t seem to retrieve the MAC of the router, although it is registered (by `ipconfig`). Perhaps a merge issue?

BUG: When there are many entries in Know Screen’s table, you can scroll upwards and it’ll cover the title. Visual issue.

Remove analyses’ confirmation popup!!!

In Know Screen, add the length of the table (and other numerical values).

In the Save Screen, add a green outline around the buttons? **************
In the Save Screen, add loading ellipsis when saving a file. *****************

Log Packets – if no new packets, show “no new packets since last viewing”.

[13:44] Wrote the Device Discovery scan. Using WireShark on another device, I was able to see the packets, which proves it works. This is the code (don’t forget to register):
```py
# under ./Scans/DeviceDiscovery.py
from import_handler import ImportDefence
with ImportDefence():
    from scapy.sendrecv import send
    from scapy.all import IP, UDP, Raw
    
    from time import sleep
    from threading import Thread


def device_discovery():
    from gui.dialogs import get_string
    name = get_string("Reveal Myself As", "Starting Device Discovery\nInsert the name you wish to reveal to others:")
    from globalstuff import terminator
    while not terminator.is_set():
        packet = IP(dst="255.255.255.255")
        packet /= UDP(dport=3581)
        packet /= Raw(load="Hello there, sir " + name)
        # print(packet.summary())
        send(packet, verbose=0)
        sleep(3)


class DeviceDiscoveryListener:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.thread = Thread(target=self.loop)
            cls._instance.thread.start()
        return cls._instance

    def __init__(self):
        pass

    def loop(self):
        from globalstuff import terminator
        from PacketSniffer import PacketSniffer
        from NetworkStorage import broadcast, SpecialInformation
        while not terminator.is_set():
            for packet in PacketSniffer():
                if UDP not in packet:
                    continue
                if packet[IP].dst != broadcast.ip:
                    continue
                if packet[UDP].dport != 3581:
                    continue
                SpecialInformation()[entity, 'discovery'] = packet[Raw]
            sleep(10)

       
if __name__ == '__main__':
    print("This file is responsible for the Device Discovery scan,")
    print("which reveals this computer to others that use this software")
```


[13:46] Change the popup colour scheme to something that matches the feel of the rest of the programme.

[13:57] After a talk with Ran:
Add ARP Spoofing/Poisoning as a scan – impersonate another IPv4 address.
I need to add “Something Special”, he says, to my programme, to get a perfect score (100).
A feature that others don't have, that's unique, not just executing some CMD command.

[14:01] Please change OS-ID to an analysis.

[14:15] Please make `PublicAddress` not create a new network entity, but insert Special Information about the router.

[14:24] Remove this part from OS-ID:
```py
# ...that has not yet been OS-ID'd
                if entity in SpecialInformation():
                    continue
```
Because it might not have been OS-ID’d, but could have other Special Information.

[14:25] Change PacketSniffer to reduce the use of `__iter__`s: have the ability to add listeners, i.e. Observer Pattern, that will do their own analyses on the information. This will also reduce the amount of threads!

[14:29] Zvika suggested a motivation for adding ARP poison: to disconnect a computer from access to the Internet, remotely, because a student is using it for mischievous purposes. Also, add disclaimers.

[20:53] Back home. Working on the project portfolio, specifically the Date Structures part, because you gotta start somewhere!

[20:54] Adding changes from Cyber class today.

[21:05] Save ARP cache entry type (static or dynamic) under Special Information.

[21:17] Changed the `router` in special network entities from `Locked` to regular.
Now, the new information flowing from, say, `ARP Live`, can get inside `router`,
which fixes "BUG: Live ARP doesn’t seem to retrieve the MAC of the router, although it is registered (by `ipconfig`). Perhaps a merge issue?".
This indeed was a merge issue, since `LockedNetworkEntity` disables merging.

[21:35] Added `role`s to SpecialInformation for the router the the current device (here).

[21:43] In Device Profile, you can also choose by role, which enables quick access to important entities (here, router).

[21:56] BUGFIX: replace `router` with `here`. Copied line and forgot to change.

[22:31] Move the `KnowScreenInfoLabel` appropriately downwards, using kivy (GUI) changes, not randomly sprinkled `\n`s.

[22:34] Have `Configuration.py:display_configuration` ignore all position arguments.

[22:40] "Remove analyses' confirmation popup!!!". Done under `Activation.py:activate`.

[22:50] Using minor ChatGPT assistence, I wrote an alternative `str.title()` to ignore acronyms (i.e. uppercase letters in input string),
because it was heavilty bothering me to see "Arp Cache..." instead of "ARP Cache". Under Device Profile formatting.

[22:54] `OS-ID` is now an analysis, not an active scan.

[23:02] That's enough for today. I want to get some sleep.
Next time, please:
(1) add diagrams of the data structures to the portfolio,
(2) and implement Device Discovery (both sides),
(3) and finish going through the notes from Cyber class today, written above, and correcting the changes you (I) deem worthy.



### 2023-05-15
[23:17] Gonna implement Device Discovery and then go work on the portfolio.

[23:59] Implementing the Observer Behavioural Design Pattern,
because it's much more logical for Packet Sniffer.
This shall also serve to minimise the amount of background active threads.
Resource used: https://www.geeksforgeeks.org/observer-method-python-design-patterns/#



### 2023-05-16
[00:21] Alright, implemented the observing at OS-ID and Discovery.

[00:29] Start some testing.

[00:31] `TypeError: ObserverPublisher.add_observer() missing 1 required positional argument: 'observer'`
I think the issue is that I used `PacketSniffer.add_observer(...`, not `PacketSniffer().add_observer(...`.
Oops, my bad.

[00:35] `AttributeError: 'PacketSniffer' object has no attribute 'data_queue'`
I forgot to initialise ObserverPublisher from PacketSniffer's `__init__`.
I have no one to blame but myself.

[00:41] `Thread-12 (notify_all); Thread-13 (notify-all)`,
Removed some code to make the thread only initialise once (removed the call to `__new__`).
This won't be an issue because ObserverPublisher has no code under `__new__`.

[01:40] Warn the user (in `run.bat`) if their Python version is not 3.10.

[01:50] Changed the popup theme to `sg.theme('DarkGreen5')`, chosen manually from `sg.preview_all_look_and_feel_themes()`.
As per "[13:46] Change the popup colour scheme to something that matches the feel of the rest of the programme.".

[02:55] Loading times are really long when no packages are installed, Python 3.10 isn't installed, Npcap isn't installed,
Qt refuses to function properly, and even after all that it doesn't work.
Can you tell I'm slightly mad? Mostly tired, if I'm honest.
I've tried running the programme on both computers downstairs, and it still doesn't see anything in Discovery.
I'll do more testing -- in class, because that's where I'll be presenting.
Plus, more things are already installed.

[03:20] Added a diagram for `db.py`.

[03:27] Added an incomplete diagram for `NetworkStorage.py`.



### 2023-05-17
[18:32] Did some work on the Portfolio, specifically the first section,
today in Cyber class, without a teacher (we just asked for keys).



### 2023-05-18
[14:17] Working on diagrams for the project portfolio.

[14:23] Finished `db.drawio` diagram.

[15:56] Finished `NetworkStorage.drawio`.

[21:23] Started `PacketSniffer.drawio`.

[21:55] Finished `PacketSniffer.drawio`.
I add a `self.initialised: bool` in `PacketSniffer`,
because I suspect that the `CLEAR_TABLE` call is what clears the packets upon `Log Packets` requests.
This is problematic, so I ~~removed~~ conditioned it -- it'll only run on the first time.

[22:04] Making `overview.drawio`.

[22:19] I'm out of ideas on `overview.drawio`.
It looks fine, just feels slightly empty.
I'll find stuff to add, somewhen.



### 2023-05-19
[18:48] Investigating `hostify`.
It uses two methods: `nslookup` and `socket.gethostbyaddr`.
For `nslookup`, the communication looks like this:
```
(router.ip = 10.0.0.138, router.name = Heights.local)

~> <Ether src=here.mac dst=router.mac> <IPv6> <UDP dst=53> <DNS questions=1> <DNS Query 138.0.0.10.in-addr.arpa PTR IN>

<~ <Ether src=router.mac dst=here.mac> <IPv6> <UDP src=53> <DNS questions=1 answerRRs=1> <DNS Query (like above); DNS Answer Heights.local>
```
For `socket.gethostbyaddr`, I couldn't identify any packets.

[22:11] Some googling has led me to suspect that `socket.gethostbyaddr` uses the [`hosts` file](https://en.wikipedia.org/wiki/Hosts_(file)),
before querying DNS if not found. This is possible, and likely, but probably not the full story,
seeing as my `hosts` file is almost empty, but the programme does still manage to get to get host names without sending a packet.
My googling path: from inspecting the source code (no results),
to https://stackoverflow.com/questions/45328873/how-does-socket-gethostbyname-work,
to https://stackoverflow.com/questions/20284094/how-gethostbyname-or-getnameinfo-work-in-background.



### 2023-05-20
[11:03] Renamed `filterIP` to `filterIPv4` in `NetworkStorage.py`.

[12:49] Shorten `can_connect_ICMP_base` while summarising it for the project portfolio.

[12:49] Shorten `scan_ARP` while summarising it for the project portfolio.

[12:56] Suggestion: add analysis that takes MAC addresses and converts them into special information on the vendor of the MAC Network Card (according to the [first 3 bytes of the MAC address](https://en.wikipedia.org/wiki/Organizationally_unique_identifier)). Use an API here?

[13:14] Options for suggestion above: https://www.macvendorlookup.com/api

[18:55] Implementing the above suggestion.
I added API access manually, basing off `PublicAddress.py`'s code,
and now I wanna add SQLite integration, because I don't want to query the API too often,
an SQLite DB will be a permanent cache, and the [API's website](https://www.macvendorlookup.com/api) warned me:
`
If you are querying too fast, in an inefficient or in an irresponsible way, we will initially throttle API requests coming from the specific IP address.
If it continues, we will temporarily ban your IP block and any associated IP blocks registered through ARIN.
`

[19:05] Using ChatGPT to generate a class for this SQLite-DB MAC-Vendor cache file.

[19:08] Introduce thread-safet with a `Lock`.

[19:26] Introduce threads with `@threadify` and 

[19:29] Register this new analysis and add a database entry about it.

[19:31] Refresh the database.

[19:43] BUGFIX: `SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 3124 and this is thread id 14032.`
Fixed by creating an SQLite cursor and connection for each method,
inside that method, using context managers supplied by sqlite3.
ChatGPT-assisted.

[20:10] This is too overcomplicated, now that I've found a list-based form of the API.
I can give it a *list* of MAC addresses. This greatly reduces the number of API requests (to 1).

[20:33] Use a different API because the previous one wanted payment after so few requests.
Actually, not an API, just reading the Company table row from the HTML page returned.
`https://hwaddress.com/?q={mac}`

[20:47] Functional build using both the new API, threadify, and the SQLite cache table!

[21:18] BUGFIX: `sqlite3.OperationalError('no such column: text')`.
I forgot to rename ALL occurrences of `text` to `vendor` in this file.

[21:22] BUGFIX: In `@threadify`, I need parentheses there... oops.

[21:28] I am very happy, this is working.

[22:14] Created `ability.drawio`.

[22:46] Created `ICMPSweep.drawio`.



### 2023-05-21
[14:11] Working on the project portfolio. The due date is so close.

[14:17] Converted `overview.drawio` to PNG.

[14:38] Converted `modules.drawio` to PNG.

[15:53] Added `ARPSweep.drawio`, and converted to PNG.

[16:07] UDP Port Scan isn't done yet, so remove it, because it won't be done by the time for presenting.

[16:20] Added `LiveICMP.drawio`, and converted to PNG.

[18:23] Quickly implement `TCP Ports` scan.
All the code is already there, just need to redirect I/O:
Inputs -- from `gui.dialogs.get_string`, not `input`.
Outputs -- to `NetworkStorage.SpecialInformation`, not `print`.

[18:29] Suggestion: add the ability to run multiple TCP Port scans on different devices,
in the same time.

[18:38] Debugged `TCP Ports` and updated its DB entry.

[18:58] Renamed threads' names to be more uniform and concise.
More Markdown formatting under `general_information`.

[19:42] Finished `TCP-Ports.drawio`.

[20:07] Adding `StartScreen`.

[20:33] Adding `Screens.drawio`.

[21:33] Making `register.drawio`.

[22:03] Update `modules.drawio`.



### 2023-05-22
[15:32] Working on the project portfolio. One day.
Weaknesses of my software? Ha ha, none! My project is the best and the strongest! XD lol

[16:26] Created `modules extended.drawio`.

[17:13] With ChatGPT, created `classes_diagram.py`,
to assist me when writing the Portfolio section about my classes.

[17:24] ChatGPT finally has a "⏩ Continue generating" button!!! Yes!

[17:59] A friend with Copilot X GPT-4 access helped me debug the GPT-3 classes_diagram code.
I then debugged the result (using my _human_ intelligence) to add type hints.

[18:02] Used GPT-3 again to add type hints for the return values.
These are all tools. We are the ones who have to know which tool to use, and for which tasks.

[23:27] I've been working on the portfolio for a few hours, and I'll keep going.
It doesn't seem like I'll get much sleep tonight.



### 2023-05-23
[00:40] Still working on the portfolio.
Joined a Discord VC with friends who also have to do it tonight.
I've now finished section 2 of the Implementation part, currently 117 pages / 15186 words.

[05:50] I did not sleep tonight.
The project portfolio is nearly done, but it's gonna be close.

[06:31] Copying the journal over to the Portfolio,
this is the last you'll see of me,
unless you open the dynamic version on GitHub.
I hope you've had a great time reading this,
I certainly had the best type constructing and programming this.
Goodbye, and lastly, goodnight!

[07:59] Added more diagrams to complete the portfolio.
My guesses as to page count (200 before code, 350 with code) turned out pretty accurate (197 without, 351 with).
Gonna slightly off that with the diagrams but it's still impressive.

[08:12] Added the diagrams.

[08:22] Converting it to the teacher's desired format and turning it in.

[08:25] Whoo!
