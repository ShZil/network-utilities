import Neutron
__author__ = 'ShZil'
print("Hi 1")

win = Neutron.Window("Example", css="main.css")
print("Hi 2")

HeaderObject = Neutron.elements.Header(win, id="title", content="Hello")

print("Hi 3")

def setName():
    HeaderObject.setAttribute("style", "color: red;")
    HeaderObject.innerHTML = "Hello world!"
    win.getElementById("submit").innerHTML = "clicked!"
    print("Hi 7")

print("Hi 4")

Neutron.elements.Button(win, id="submit", content="Hi", onclick=Neutron.event(setName))

print("Hi 5")
win.show()
print("Hi 6")
