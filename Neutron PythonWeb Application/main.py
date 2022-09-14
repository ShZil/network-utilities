import Neutron
from time import sleep
__author__ = 'ShZil'

win = Neutron.Window("Example", size=(600,100))

# The loader covers while all the other elements and css loads
win.loader(content="<h3>Loading App...</h3>", color="#fff", after=lambda: win.toggle_fullscreen())

print("Hi")

# win.show()
sleep(1)
