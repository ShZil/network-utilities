from import_handler import ImportDefence
with ImportDefence():
    from io import StringIO
    from math import floor, ceil
    from queue import Queue
    import sys
    from threading import Thread, active_count
    from time import sleep
    import sys
    from pygments import highlight, lexers, formatters
    from json import dumps
    import os


__author__ = 'Shaked Dan Zilberman'
MAX_THREADS: int = 300


def print_dict(x: dict) -> None:
    """Prints a python dictionary using JSON syntax and console colouring.

    Args:
        x (dict): the dictionary to print.
    """
    formatted_json = dumps(x, sort_keys=False, indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)


def shift(seq: list, n: int) -> list:
    """Shifts / Rotates / Rolls a list `seq` by `n` places.

    Args:
        seq (list): The list to shift.
        n (int): The amount of places to shift by.

    Returns:
        list: the shifted list.
    """
    if len(seq) == 0: return []
    if len(seq) == 1: return seq
    if n == 0: return seq
    n = n % len(seq)
    return seq[n:] + seq[:n]


def barstyle(name: str) -> str:
    """Selects a style for @threadify's progress bar.

    Available styles:
        Dot Fill   :  ███████∙∙∙∙∙∙∙
        Default    : [───────       ]
        Unstyled   : [-------       ]
        Hash Fill  : |#######       |
    
    Usage:
    ```
    def function():
        # some code
    
    function.options = {"format": style("default")}
    function = threadify(function)
    ```

    Args:
        name (str): the name of the style.

    Returns:
        str: the format.
    """
    try:
        return {
            "dotfill": " █∙ ",
            # "squarefill": " ▣▢ ",
            # "circlefill": " ◉◯ ",
            "default": "[─ ]",
            "unstyled": "[- ]",
            "hashfill": "|# |"
        }[name.lower().replace(' ', '')]
    except NameError:
        return "[─ ]"


def threadify(f, silent=False):
    """This function turns methods (tasks) into thread-based on-list execution.
    Therefore, the execution will be faster.
    Returns the same result as `[f() for _ in input]`, but faster.
    
    Return values from the task are saved in an array, which is the return value of the decorated function.
    The values are not messy (which is what normally happens with threading), but organised according to the `args`.
    Meaning, `returned[0] = f(args[0]); returned[1] = f(args(1))...`.

    **This function is blocking.**
    Its internals run asyncronosly, but calling this will wait until all the tasks are done.
    **It will slurp up any printing done by other threads!**

    Also, if the arguments were `f(a, b, c)`, the new argument is `f(list[tuple(a, b, c)])`.
    E.g., the function `add(x: int, y: int)`, if it's `@threadify`-ied, will be called by `add([(x0, y0), (x1, y1), (x2, y2)...])`.
    If the function receives a single not-tuple argument, you can just put it in the list `[a, b, c, d]` -> f(a) + f(b) + f(c) + f(d).
    If the function receives a single tuple as an argument, wrap it in another tuple: `[a: tuple, b: tuple, c: tuple, d: tuple]` -> `f([(a, ), (b, ), (c, ), (d, )])`.
    If a code-based explanation for the logic is better, here are the relevant (pseudo)code pieces:
    ```py
    for arg in args:
        a = arg if isinstance(arg, tuple) else (arg, )
        f(*a)
    ```
    Doesn't support keyword-arguments.
    The amount of threads per decorated function call is limited by `MAX_THREADS`.
    
    The function can have an `f.options` dict as an attribute, overriding any of these:
    ```
        options={
            # daemon: bool -- if True, the threads forcibly end when main ends.
            # Else, they can continue running in the background.
            "daemon": True,
            # printing: bool -- should there be a progress bar?
            "printing": True,
            # min_printing_length: int -- the minimal size of the progress bar (in characters). The actual length can be larger, if the terminal is wide enough.
            "min_printing_length": 10,
            # format: str -- the format of the progress bar. 
            # For printing_length=6 and this format, after half the execution, the bar would look like "[---   ]  (50%)".
            "format": "[- ]",
            # output: bool -- should the output (via print()s) of the tasks be logged?
            "output": True,
            # give: str -- decides what the function returns: "results" is the return value of the tasks; "output" is the printing of the tasks; "both" is a tuple of both.
            # Any other value defaults to "results".
            "give": "results"
        }
    ```

    Args:
        f (function): The task to be turned into a threaded task.
        silent (bool): forces `options["output"]` and `options["printing"]` to be `False`.

    Returns:
        list: a list of values returned from the multiple calls to the function, sorted by the call order (i.e. not disorganised by the threads).
    """
    # Set up the options dictionary with default values.
    options={
        "daemon": True,
        "printing": True,
        "min_printing_length": 10,
        "format": "[─ ]",
        "output": True,
        "give": "results"
    }
    # Add options set via `f.options`, if such an attribute exists.
    try:
        options = {**options, **f.options}
    except AttributeError:
        pass
    
    name = f.__name__
    name = name.replace("_base", "")
    if silent:
        options["output"] = False
        options["printing"] = False

    def wrapper(args: list[tuple] | list) -> list | str | tuple[list, str]:
        if not isinstance(args, list):
            raise TypeError("Threadify-ied functions must receive a single argument of type list.")
        
        # The return values from the function calls.
        values = [None] * len(args)
        # The exceptions raised during tasks thread-safe queue.
        fails = Queue(maxsize=len(args))
        
        # Define a task inner wrapper for `f`
        def task(func, arg, index):
            # Convert arg to tuple if needed ("If the function receives a single not-tuple argument,..." in docstring)
            args = arg if isinstance(arg, tuple) else (arg, )
            try:
                # Execute the function & save to `values` list.

                # Force the function to end within a given timeout!
                values[index] = func(*args)
            except Exception as e:
                # Catch any exception and add it to the `fails` queue
                fails.put(e)
                return
        
        real_stdout = sys.stdout
        output = StringIO()
        if options["output"]:
            # Redirect printing
            sys.stdout = output
        
        # Create Thread objects
        threads = [Thread(target=task, args=(f, x, i), daemon=True) for i, x in enumerate(args)]
        
        def start_threads(threads: list):
            # Activate the threads, waiting for threads to be freed if needed.
            for thread in threads:
                thread.start()
                while active_count() >= MAX_THREADS and MAX_THREADS > 0:
                    print(active_count(), "threads active.", file=real_stdout)
                    sleep(0.01)
        
        starter = Thread(target=start_threads, args=(threads, ))
        starter.start()
        
        # BUGFIX ************: Make it so the progress bar starts already during threads.starts()

        # Print a progress bar if requested
        if options["printing"]:
            width = os.get_terminal_size().columns - len(f"@threadify: {name}    ")
            if width < options["min_printing_length"]: width = options["min_printing_length"]
            while any([thread.is_alive() for thread in threads]):
                ratio = sum([thread.is_alive() for thread in threads]) / len(threads)

                print(f"@threadify: {name} {progress(ratio, options['format'], width)}   \r", end='', file=real_stdout)
                sleep(0.1)
            print(f"@threadify: {name} {progress(0, options['format'], width)}   \r", end='', file=real_stdout)
            print("\n")
        
        # Join all threads
        starter.join()  # You have to join `starter` first, because if somehow some thread is still not active, joining it will raise a RuntimeError.
        for thread in threads:
            thread.join()
        
        # Restore printing
        sys.stdout = real_stdout

        # If any exceptions happened, print them orderly and raise another.
        if not fails.empty:
            while not fails.empty:
                err = fails.get()
                print(type(err), err, sep="\n")
            raise Exception("@threadify-ied function has raised some exceptions.")

        # Handle the output from the tasks
        output = output.getvalue()
        if options["output"] and output.strip() != "":
            print("\n\nTasks' output:\n", output, sep='')
            print("\n\n")
        print()

        # Returning logic.
        if options["give"] == "output": return output
        if options["give"] == "both": return values, output
        return values
        
    # Make `wrapper` inherit `f`'s properties.
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper


def progress(ratio: float, form: str, width: int):
    if len(form) < 4: form = form.rjust(4)
    start, fill, nofill, end = tuple(form)
    width -= len("[] (100%)")
    done = fill * ceil(width * (1 - ratio))
    waiting = nofill * floor(width * (ratio))
    percent = ceil(100 * (1 - ratio))

    return f"{start}{done}{waiting}{end} ({percent}%)"


def memorise(f):
    """A decorator that saves the return value of a function to a cache,
    so that when it's called again (with the same arguments!),
    no calculations are made and the result is returned from the cache.

    Args:
        f (function): the function to decorate and add a cache to

    Returns:
        function: the decorated function with a cache
    """
    # ********* Add a time limit on each datum
    memory = {}
    def wrapper(*args):
        try:
            if args in memory:
                return memory[args]
            else:
                result = f(*args)
                memory[args] = result
                return result
        except TypeError:
            print("@memorise function cannot receive unhashable types! (e.g. lists, sets)")
            raise
    
    # Make `wrapper` inherit `f`'s properties.
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper


def one_cache(f):
    """A decorator that saves the return value of a function to a cache,
    so that when it's called again,
    no calculations are made and the result is returned from the cache.
    This completely ignores arguments, so use it only when:
    1. There are no arguments; or
    2. Arguments don't matter; or
    3. The function is expected to be called with the same arguments.

    Args:
        f (function): the function to decorate and add a cache to

    Returns:
        function: the decorated function with a cache
    """
    # This is a list for it to be a reference type.
    memory = [None]
    def wrapper(*args):
        if memory[0] is not None:
            return memory[0]
        else:
            memory[0] = f(*args)
            return memory[0]
    
    # Make `wrapper` inherit `f`'s properties.
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper


def render_opacity(percent: int | float):
    """Returns a character to display a given opacity/fillness,
    according to a percent:
    0%-20% -> " "
    ...
    40%-60% -> "▒"
    ...
    80%-100% -> "█"

    if the percent is outside the range [0, 100], returns "X".

    ```
        -10%  X
         -5%  X
         0%   
         5%   
         10%   
         15%   
         20%   
         25%  ░
         30%  ░
         35%  ░
         40%  ░
         45%  ▒
         50%  ▒
         55%  ▒
         60%  ▒
         65%  ▓
         70%  ▓
         75%  ▓
         80%  ▓
         85%  █
         90%  █
         95%  █
        100%  █
        105%  X
        110%  X
        115%  X
        120%  X
    ```

    Args:
        percent (int | float): the percent to match.

    Returns:
        str: a single character representing that percent of fillness.
    """
    if not (0 <= percent <= 100): return "X"

    characters = " ░▒▓█"
    # characters = " -─=≡▄█"
    jump = 0.1 + 100 / len(characters)
    level = floor(percent / jump)
    return characters[level]


def nameof(action):
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


class _Printing:
    """This context manager delays and stores all outputs via `print`s.
    It is not meant to be used directly, but other classes can inherit it.
    """
    def __init__(self):
        pass

    def __enter__(self):
        self.real_stdout = sys.stdout
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.real_stdout



class InstantPrinting(_Printing):
    """This context manager delays and stores all outputs via `print`s, and prints everything when closed.
    Usage:
    ```py
    with InstantPrinting():
        # do some stuff here including printing
    # Here, exiting the context, the printing will all happen immediately.
    ```
    """
    def __init__(self):
        self.output = StringIO()
    
    def __enter__(self):
        super().__enter__()
        sys.stdout = self.output
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        print(self.output.getvalue())


class NoPrinting(_Printing):
    """This context manager prevents all output (through `sys.stdout`, e.g. normal `print` statements) from showing.
    Usage:
    ```py
    with NoPrinting():
        # do some stuff here including printing
        # Nothing will actually display
    ```

    Technical note: this just inherits `_Printing` with no additional behaviour.
    """
    pass



class _SplitStringIO:
    """This class is like the io.StringIO, but it splits different `write` statements.
    Internally, this is a `list` of `StringIO`s.
    Not meant for use outside the `util` module.
    """
    def __init__(self):
        self.content = []


    def write(self, data):
        self.content.append(StringIO())
        self.content[-1].write(data)
        
    
    def getvalue(self):
        return [string.getvalue() for string in self.content]
    

    def flush():
        pass



class JustifyPrinting(InstantPrinting):
    """This context manager delays and stores all outputs via `print`s, and prints everything when closed,
    justifying every print statement to form a nice-looking block of text, where each line is centred and as widespread as is allowed.

    Note: Messing with `print`'s default values (`sep=' ', end='\\n'`) is not recommended,
    since this context manager treats space-separated strings as belonging to the same statement,
    and newline-separated string as belonging to different statements.

    Usage:
    ```py
    with JustifyPrinting():
        # do some stuff here including printing
    # Here, exiting the context, the printing will all happen immediately and (hopefully) nicely.
    ```
    """

    def __init__(self):
        self.output = _SplitStringIO()

    def __exit__(self, exc_type, exc_val, exc_tb):
        _Printing.__exit__(self, exc_type, exc_val, exc_tb)
        blocks = self.output.getvalue()
        width = int(os.get_terminal_size().columns)

        MIN_SEP = 3  # There must be at least one space between blocks.
        MAX_SEP = 10  # There cannot be more than ten spaces between blocks.

        statements = [""]
        for block in blocks:
            if block == '\n':
                statements.append("")
            else:
                statements[-1] += block
        blocks = statements
        

        lines = [[]]
        for block in blocks:
            # Lengths of all previous blocks
            # + Length of current block
            # + assuming `MIN_SEP` spaces in-between (thus, #spaces = #blocks * MIN_SEP)
            # > width of console in characters
            if sum(map(len, lines[-1])) + len(block) + len(lines[-1]) * MIN_SEP > width:
                lines.append([])
            lines[-1].append(block)

        for line in lines:
            # Optimal case: total_length + total_separator_length = width
            # total_separator_length = sep * (len(line) - 1)
            # => sep = (width - total_length) // (len(line) - 1)
            line = [part for part in line if part.strip() != '']
            if len(line) == 1:
                print(line[0].center(width))
                continue
            total_length = sum([len(block) for block in line])
            sep = (width - total_length) // (len(line) - 1)
            if sep > MAX_SEP: sep = MAX_SEP
            sep *= ' '
            print(sep.join(line).center(width))


class TablePrinting(InstantPrinting):
    """This context manager delays and stores all outputs via `print`s, and prints everything when closed,
    justifying every print statement to form a nice-looking table.

    Note: Messing with `print`'s default values (`sep=' ', end='\\n'`) is not recommended,
    since this context manager treats space-separated strings as belonging to the same statement,
    and newline-separated string as belonging to different statements.

    Usage:
    ```py
    with TablePrinting():
        # do some stuff here including printing
    # Here, exiting the context, the printing will all happen immediately and (hopefully) nicely.
    ```
    """
    aligns = {
        'left': lambda s, w: s.ljust(w),
        'center': lambda s, w: s.center(w),
        'right': lambda s, w: s.rjust(w)
    }

    def __init__(self, align='center'):
        self.output = _SplitStringIO()
        self.align = TablePrinting.aligns["center"]
        if align in TablePrinting.aligns.keys():
            self.align = TablePrinting.aligns[align]


    def __exit__(self, exc_type, exc_val, exc_tb):
        _Printing.__exit__(self, exc_type, exc_val, exc_tb)
        output = self.output.getvalue()
        width = int(os.get_terminal_size().columns)

        # Separate `print statements`.
        # Every block which is just a newline is (probably) a different print, so I'll treat it as such.
        blocks = [""]
        for block in output:
            if block == '\n': blocks.append("")
            else: blocks[-1] += block
        
        # Split the blocks into a `chunk list` (e.g. [a, b, c, d, e, f] + n=2 -> [[a, b], [c, d], [e, f]])
        lengths = [len(block) for block in blocks]
        try:
            n = max(width // max(lengths), 3)
        except ZeroDivisionError:
            # There is no content, only empty strings
            print()
            return
        lines = [blocks[i:i + n] for i in range(0, len(blocks), n)]
        for line in lines:
            for part in line:
                w = width // n
                print(self.align(part, w), end="")
            print()


class AutoLinebreaks(InstantPrinting):
    """This context manager delays and stores all outputs via `print`s, and prints everything when closed,
    wrapping lines only when nessessary to maintain integrity.
    In short: Applies CSS's `word-wrap: normal;` (whereas the console is usually `word-wrap: break-word;`).

    Note: Messing with `print`'s default values (`sep=' ', end='\\n'`) is not recommended,
    since this context manager treats space-separated strings as belonging to the same statement,
    and newline-separated string as belonging to different statements.
    You may do so after familiarising yourself with the code, in order to not induce annoying bugs.

    Usage:
    ```py
    with AutoLinebreaks():
        # do some stuff here including printing
    # Here, exiting the context, the printing will all happen immediately and (hopefully) nicely.
    ```
    """

    def __init__(self):
        self.output = _SplitStringIO()


    def __exit__(self, exc_type, exc_val, exc_tb):
        _Printing.__exit__(self, exc_type, exc_val, exc_tb)
        output = self.output.getvalue()
        width = int(os.get_terminal_size().columns)

        # Separate `print statements`.
        # Every block which is just a newline is (probably) a different print, so I'll treat it as such.
        blocks = [""]
        for block in output:
            if block == '\n': blocks.append("")
            else: blocks[-1] += block
        
        counter = width
        for block in blocks:
            if block.strip() == "": continue
            if counter - len(block) <= 0:
                counter = width
                print('\n' + block, end="")
            else:
                counter -= len(block)
                print(block, end="")
        print()




if __name__ == '__main__':
    print("This is a utility module.")
