from math import floor, ceil
from threading import Thread, active_count
from time import sleep

__author__ = 'Shaked Dan Zilberman'
MAX_THREADS: int = 300


def print_dict(x: dict) -> None:
    from pygments import highlight, lexers, formatters
    from json import dumps
    formatted_json = dumps(x, sort_keys=False, indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)


def threadify(f):
    """This function turns methods (tasks) into thread-based on-list execution.
    Therefore, the execution will be faster.
    
    Return values from the task are saved in an array, which is the return value of the decorated function.
    The values are not messy (which is what normally happens with threading), but organised according to the `args`.
    Meaning, `returned[0] = f(args[0]); returned[1] = f(args(1))...`.

    *This function is blocking.* Its internals run asyncronosly, but calling this will wait until all the tasks are done.

    Also, if the arguments were `f(a, b, c)`, the new argument is `f(list[tuple(a, b, c)])`.
    E.g., the function `add(x: int, y: int)`, if it's `@threadify`-ied, will be called by `add([(x0, y0), (x1, y1), (x2, y2)...])`.
    If the function receives a single not-tuple argument, you can just put it in the list `[a, b, c, d]` -> f(a) + f(b) + f(c) + f(d).
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
            # printing_length: int -- the size of the progress bar (in characters).
            "printing_length": 10,
            # format: str -- the format of the progress bar. 
            # For printing_length=6 and this format, after half the execution, the bar would look like "[---   ]  (50%)".
            "format": "[- ]"
        }
    ```

    Args:
        f (function): The task to be turned into a threaded task.

    Returns:
        list: a list of values returned from the multiple calls to the function, sorted by the call order (i.e. not disorganised by the threads).
    """

    options={
        "daemon": True,
        "printing": True,
        "printing_length": 10,
        "format": "[- ]"
    }
    try:
        options = {**options, **f.options}
    except AttributeError:
        pass


    def wrapper(args: list[tuple]):
        if not isinstance(args, list):
            raise TypeError("Threadify-ied functions must receive a single argument of type list.")
        
        values = [None] * len(args)
        
        def task(func, arg, index):
            args = arg if isinstance(arg, tuple) else (arg, )
            value = func(*args)
            values[index] = value
        
        threads = [Thread(target=task, args=(f, x, i), daemon=True) for i, x in enumerate(args)]
        for thread in threads:
            thread.start()
            while active_count() >= MAX_THREADS:
                sleep(0.01)
        
        if options["printing"]:
            while any([thread.is_alive() for thread in threads]):
                ratio = sum([thread.is_alive() for thread in threads]) / len(threads)
                done = options["format"][1] * floor(options["printing_length"] * (1 - ratio))
                waiting = options["format"][2] * ceil(options["printing_length"] * (ratio))
                start, end = options["format"][0], options["format"][3]
                print(f"{start}{done}{waiting}{end}  ({floor(100 * ratio)}%)    ", end='\r')
                sleep(0.1)
            print("\n")
        
        for thread in threads:
            thread.join()
        
        return values
        
        
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper


if __name__ == '__main__':
    print("This is a utility module.")
