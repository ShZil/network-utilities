__author__ = 'Shaked Dan Zilberman'


def print_dict(x: dict) -> None:
    from pygments import highlight, lexers, formatters
    from json import dumps
    formatted_json = dumps(x, sort_keys=False, indent=4)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)


if __name__ == '__main__':
    print("This is a utility module.")
