from import_handler import ImportDefence
with ImportDefence():
    from kivy.core.text import LabelBase


def add_fonts():
    """Loads a font (`kivy`'s), from the folder `fonts/`."""
    def _add_font(path, name, fallback='fonts/Segoe UI Symbol.ttf'):
        path = f'fonts/{path}'
        try:
            LabelBase.register(name=name, fn_regular=path)
        except OSError:
            LabelBase.register(name=name, fn_regular=fallback)

    _add_font('BainsleyBold.ttf', 'Symbols')
    _add_font('Segoe UI Symbol.ttf', 'Symbols+')
    _add_font('Symbola.ttf', 'Symbols++')
    _add_font('Consolas.ttf', 'Monospace')


if __name__ == '__main__':
    print("This file is responsible for loading the fonts for the kivy gui.")
