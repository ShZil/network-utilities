from typing import Callable


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


if __name__ == '__main__':
    print("This module provides two cache-related function decorators.")
    print("One is a multiargument cache with time limit, called @memorise.")
    print("The other is a single-entry no-time-limit cache, called @one_cache.")
