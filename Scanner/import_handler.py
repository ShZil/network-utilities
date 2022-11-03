class ImportDefence:
    """This context manager ensures all `import` statements were successful,
    and if some weren't, it attempts a `pip install`.

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
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import os
        # If no ModuleNotFoundError occured, clear the screen and print and return to original script.
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

            print(f"Module `{err.name}` was not found. Attempting `pip install {err.name}`...\n")
            try:
                do_command([sys.executable, "-m", "pip", "install", err.name])
            except CalledProcessError:
                print(f"\nModule `{err.name}` could not be pip-installed. Please install manually.")
                sys.exit(1)
            argv = ['\"' + sys.argv[0] + '\"'] + sys.argv[1:]
            os.execv(sys.executable, ['python'] + argv)
