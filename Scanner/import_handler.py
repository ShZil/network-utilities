class ImportDefence:
    """This context manager ensures all `import` statements were successful,
    and if some weren't, it attempts a `pip install`.

    Source: https://raw.githubusercontent.com/ShZil/network-utilities/main/Scanner/import_handler.py

    This function handles a ModuleNotFoundError,
    attempting to install the not-found module using `pip install`,
    and restarting the script / instructing the user.

    Line-by-line breakdown of the ModuleNotFoundError handler:
    - necessary imports: sys, os, subprocess

    ```py
    import sys
    from subprocess import check_call as do_command, CalledProcessError
    import os
    ```

    - print the failure

    ```py
    print(f"Module `{err.name}` was not found. Attempting `pip install {err.name}`...\n")
    ```

    - try to pip install it

    ```py
    try:
        do_command([sys.executable, "-m", "pip", "install", err.name])
    ```

    - if failed, request manual installation

    ```py
    except CalledProcessError:
        print(f"\\nModule `{err.name}` could not be pip-installed. Please install manually.")
        sys.exit(1)
    ```

    - if succeeded, restart the script

    ```py
    argv = ['\"' + sys.argv[0] + '\"'] + sys.argv[1:]
    os.execv(sys.executable, ['python'] + argv)
    ```

    **Usage:**
    ```py
    from import_handler import ImportDefence

    with ImportDefence():
        import module1
        from module2 import some_function
    ```
    """
    def __enter__(self):
        """To be a context manager, needs an `__enter__` method.

        Returns:
            Self@ImportDefence: the `self` object.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Handles exiting the context.
        Pip-installs the requested packages and reboots the code.

        Args:
            exc_type (type | NoneType): the type of error.
            exc_val (Exception | NoneType): the exception raised.
            exc_tb (traceback | NoneType): a traceback object of the exception.

        Raises:
            exc_val: the exception, if it's not `ModuleNotFoundError`.
        """
        import os
        # If no ModuleNotFoundError occured, clear the screen and print and
        # return to original script.
        if exc_val is None:
            os.system('cls')
            print("All imports were successful.")
            return
        # Otherwise, raise the exception.
        try:
            raise exc_val
        # If the exception is of type ModuleNotFoundError, handle it:
        except ModuleNotFoundError as err:
            import sys
            from subprocess import check_call as do_command, CalledProcessError

            to_install = err.name
            # Some modules have `pip install X` and `import Y`, where `X != Y`.
            # These have to be added manually, since there's no pattern.
            if 'win32' in to_install:
                to_install = 'pywin32'
            if to_install == 'cv2':
                to_install = 'opencv-python'
            if to_install == 'Crypto':
                to_install = 'pycryptodome'
            if to_install == 'PIL':
                to_install = 'pillow'
            if to_install == '_curses':
                to_install = 'windows-curses'
            to_install = to_install.split('.')[0]

            print(
                f"Module `{err.name}` was not found. Attempting `pip install {to_install}`...\n"
            )
            try:
                do_command(
                    [sys.executable, "-m", "pip", "install", to_install]
                )
            except CalledProcessError:
                if_different = f"" if to_install == err.name else f" (from `{err.name}`)"
                print(
                    f"\nModule `{to_install}`{if_different} could not be pip-installed. Please install manually."
                )
                sys.exit(1)
            argv = ['\"' + sys.argv[0] + '\"'] + sys.argv[1:]
            os.execv(sys.executable, ['python'] + argv)
        # If the exception is of type ImportError, log an error and keep raising it.
        except ImportError:
            print("You've misnamed your import. Check it.")
            raise

# possible add pip updating, using:
# `python.exe -m pip install --upgrade pip`
