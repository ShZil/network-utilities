from import_handler import ImportDefence
with ImportDefence():
    import os
    import sys
    from io import StringIO


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

    Implements:
    `__init__`: initialises an empty list.
    `write`: adds a StringIO to the list, and writes the data into it.
    `getvalue`: returns a list of all the `.getvalue`s of the `StringIO`s.
    `flush`: does nothing.
    """

    def __init__(self):
        self.content = []

    def write(self, data):
        """
        The write function is called to write the data into the IO.
        """
        self.content.append(StringIO())
        self.content[-1].write(data)

    def getvalue(self):
        """
        The getvalue function returns a list of strings, one for each string in the content attribute.
        The getvalue function is called by the write method to return a list of strings that can be written to file or console.

        Returns:
            list[str]: A list of strings contained in the IO.
        """
        return [string.getvalue() for string in self.content]

    def flush():
        """For compatibility with the IO interface that is expected."""
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
            all_previous_blocks = sum(map(len, lines[-1]))
            spaces_in_between = len(lines[-1]) * MIN_SEP
            if all_previous_blocks + len(block) + spaces_in_between > width:
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
            if sep > MAX_SEP:
                sep = MAX_SEP
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
        # Every block which is just a newline is (probably) a different print,
        # so I'll treat it as such.
        blocks = [""]
        for block in output:
            if block == '\n':
                blocks.append("")
            else:
                blocks[-1] += block

        # Split the blocks into a `chunk list` (e.g. [a, b, c, d, e, f] + n=2
        # -> [[a, b], [c, d], [e, f]])
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
        # Every block which is just a newline is (probably) a different print,
        # so I'll treat it as such.
        blocks = [""]
        for block in output:
            if block == '\n':
                blocks.append("")
            else:
                blocks[-1] += block

        counter = width
        for block in blocks:
            if block.strip() == "":
                continue
            if counter - len(block) <= 0:
                counter = width
                print('\n' + block, end="")
            else:
                counter -= len(block)
                print(block, end="")
        print()


if __name__ == '__main__':
    print("This module provides some Printing context managers,")
    print("That allow you to decide how to format your console output")
    print("and whether to even show it!")
