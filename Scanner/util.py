from typing import Callable
from import_handler import ImportDefence
with ImportDefence():
    from io import StringIO
    from math import floor, ceil
    from queue import Queue
    import sys
    from threading import Thread, active_count
    from time import sleep
    import sys
    import os


__author__ = 'Shaked Dan Zilberman'
MAX_THREADS: int = 50



def shift(seq: list, n: int) -> list:
    """Shifts / Rotates / Rolls a list `seq` by `n` places.

    Example:
        shift([1, 2, 3, 4], 1) -> [2, 3, 4, 1]

    Args:
        seq (list): The list to shift.
        n (int): The amount of places to shift by.

    Returns:
        list: the shifted list.
    """
    if len(seq) == 0:
        return []
    if len(seq) == 1:
        return seq
    if n == 0:
        return seq
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
    
    For `name`:
    Whitespaces are ignored, capital letters are `.lower`ed.
    If the name was not found, uses the Default style.

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
    It will stop generating new threads if `globalstuff`'s `terminator` is set.

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
    options = {
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
            raise TypeError(
                "Threadify-ied functions must receive a single argument of type list."
            )

        # The return values from the function calls.
        values = [None] * len(args)
        # The exceptions raised during tasks thread-safe queue.
        fails = Queue(maxsize=len(args))

        # Define a task inner wrapper for `f`
        def task(func, arg, index):
            # Convert arg to tuple if needed ("If the function receives a
            # single not-tuple argument,..." in docstring)
            args = arg if isinstance(arg, tuple) else (arg, )
            try:
                # Execute the function & save to `values` list.
                values[index] = func(*args)
            except Exception as e:
                # Catch any exception and add it to the `fails` queue
                fails.put(e)
                return

        # Rename `task` to user-friendly name
        task.__name__ = f.__name__ + '_task'

        real_stdout = sys.stdout
        output = StringIO()
        if options["output"]:
            # Redirect printing
            sys.stdout = output

        # Create Thread objects
        threads = [Thread(target=task, args=(f, x, i), daemon=True)
                   for i, x in enumerate(args)]

        def threadify_start_threads(threads: list):
            from globalstuff import terminator
            # Activate the threads, waiting for threads to be freed if needed.
            for thread in threads:
                thread.start()
                while active_count() >= MAX_THREADS and MAX_THREADS > 0:
                    # print(active_count(), "threads active.", file=real_stdout)
                    sleep(0.02)
                    if terminator.is_set():
                        return
                if terminator.is_set():
                        return

        # Rename `threadify_start_threads` to user-friendly name
        threadify_start_threads.__name__ = f.__name__ + '_threadify_start_threads'

        starter = Thread(target=threadify_start_threads, args=(threads, ))
        starter.start()

        # Print a progress bar if requested
        if options["printing"]:
            width = os.get_terminal_size().columns - \
                len(f"@threadify: {name}    ")
            if width < options["min_printing_length"]:
                width = options["min_printing_length"]
            while any([thread.is_alive() for thread in threads]):
                ratio = sum([thread.is_alive()
                            for thread in threads]) / len(args)

                print(
                    f"@threadify: {name} {progress(ratio, options['format'], width)}   \r",
                    end='',
                    file=real_stdout
                )
                sleep(0.1)
            print(
                f"@threadify: {name} {progress(0, options['format'], width)}   \r",
                end='',
                file=real_stdout
            )
            print("\n")

        # Join all threads
        # You have to join `starter` first, because if somehow some thread is
        # still not active, joining it will raise a RuntimeError.
        # Also, if the `terminator` was set, not all threads will have been started, and you need to catch those RuntimeErrors.
        starter.join()
        for thread in threads:
            try:
                thread.join()
            except RuntimeError:
                pass

        # Restore printing
        sys.stdout = real_stdout

        # If any exceptions happened, print them orderly and raise another.
        if not fails.empty:
            while not fails.empty:
                err = fails.get()
                print(type(err), err, sep="\n")
            raise Exception(
                "@threadify-ied function has raised some exceptions."
            )

        # Handle the output from the tasks
        output = output.getvalue()
        if options["output"] and output.strip() != "":
            print("\n\nTasks' output:\n", output, sep='')
            print("\n\n")
        # print()

        # Returning logic.
        if options["give"] == "output":
            return output
        if options["give"] == "both":
            return values, output
        return values

    # Make `wrapper` inherit `f`'s properties.
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper


def progress(ratio: float, form: str, width: int) -> str:
    """This function generates a printable progress bar.
    The bar is filled according to `ratio`, which ranges from 0 (all done) to 1 (nothing done).
    Notice, 0 means the bar is completely filled, and 1 means the bar is completely empty, not the opposite.
    The ratio should decrease from 1 to 0, in order for the bar to fill up.
    The characters are taken from `form`, which is a 4-chraracter string specifying the style of the bar.
    `form` contains the start character, the filler, the no-filler, and the end character; in that order.
    `width` is the amount of characters the progress bar can expand into, usually the width of the console, minus some padding.

    Example:
        progress(0.3, '[- ]', 20) -> '[--------   ] (70%)' (19 characters long)

    Args:
        ratio (float): the ratio of unfilled/all of the bar. Ranges from 0 to 1.
        form (str): the characters of the progress bar. 4 characters long.
        width (int): the amount of characters the bar may expand into and take up.

    Returns:
        str: a progress bar of this format: `{start}{done}{waiting}{end} ({percent}%)`
    """
    if len(form) < 4:
        form = form.rjust(4)
    start, fill, nofill, end, *ignore = tuple(form)
    width -= len("[] (100%)")

    done_length: int = ceil(width * (1 - ratio))
    done: str = fill * done_length

    wating_length: int = floor(width * (ratio))
    waiting: str = nofill * wating_length

    percent: int = ceil(100 * (1 - ratio))

    return f"{start}{done}{waiting}{end} ({percent}%)"


def memorise(f: Callable) -> Callable:
    """A decorator that saves the return value of a function to a cache,
    so that when it's called again (with the same arguments!),
    no calculations are made and the result is returned from the cache.
    The arguments to the function must be hashable,
    so no lists or sets, but it can get ints or strings or tuples.

    A cached datum that's retreived 10 seconds or more after it was calculated,
    will be calculated again.
    The amount of seconds can be varied with `TIME_LIMIT`.

    Args:
        f (function): the function to decorate and add a cache to.

    Returns:
        function: the decorated function with a cache.
    """
    memory = {}
    from time import time as now
    TIME_LIMIT: int = 180  # in seconds

    def wrapper(*args):
        try:
            # Do I have the cached result of these arguments?
            if args in memory:
                # If I do have the cached result, calculate whether I'm still within the TIME_LIMIT.
                value, time_created = memory[args]
                if now() - time_created < TIME_LIMIT:
                    # If I am, just return the cached value.
                    return value
                else:
                    # If not, calculate the value again.
                    result = f(*args)
                    memory[args] = (result, now())
                    return result
            else:
                # If I don't have the cached result, calculate it.
                result = f(*args)
                memory[args] = (result, now())
                return result
        except TypeError:
            print("@memorise function cannot receive unhashable types! (e.g. lists, sets)")
            raise

    # Make `wrapper` inherit `f`'s properties.
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper


def one_cache(f: Callable) -> Callable:
    """A decorator that saves the return value of a function to a cache,
    so that when it's called again,
    no calculations are made and the result is returned from the cache.
    This completely ignores arguments, so use it only when:
    1. There are no arguments; or
    2. Arguments don't matter; or
    3. The function is expected to be called with the same arguments.

    The function must return some non-None value.

    Args:
        f (function): the function to decorate and add a cache to.

    Returns:
        function: the decorated function with a cache.
    """
    # This is a list for it to be a reference type.
    memory = [None]

    def wrapper(*args):
        # If I have cache, return it.
        if memory[0] is not None:
            return memory[0]
        # If I don't have cache, call the function.
        memory[0] = f(*args)
        if memory[0] is None:
            raise ValueError("A @one_cache function cannot return None!")
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

    if the percent is outside the range [0, 100] inclusive, returns "X".

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
    if not (0 <= percent <= 100):
        return "X"

    characters = " ░▒▓█"
    # characters = " -─=≡▄█"

    # the 0.1 doesn't change the results,
    # it just prevents an `IndexError: string index out of range` for `percent=100`.
    jump = 0.1 + 100 / len(characters)
    level = floor(percent / jump)
    return characters[level]


if __name__ == '__main__':
    print("This is a utility module.")
    print("It provides various methods, content managers, and decorators,")
    print("That are used all throughout the software.")
