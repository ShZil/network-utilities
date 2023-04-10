import os


def cmdtitle(*s, sep=''):
    os.system(f'title {sep.join(s)}')


def cmdcolor(c):
    os.system(f'color {str(c).zfill(2)}')


if __name__ == '__main__':
    print("This module is responsible for styling the CMD or console.")
    print("It can change the title of the CMD window,")
    print("And the colour of the text.")
