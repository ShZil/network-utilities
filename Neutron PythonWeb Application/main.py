import Neutron

win = Neutron.Window("Example")

def setName():
    name = win.getElementById("inputName").value
    win.getElementById("title").innerHTML = "Hello: " + name


win.display(f"""

<!DOCTYPE html>
<html>
   <head lang="en">
      <meta charset="UTF-8">
   </head>
   <body>
      <h1 id="title">Hello: </h1>
      <input id="inputName">
      <button id="submitName" onclick="setName()">Submit</button>
   </body>
</html>
""", pyfunctions=[setName]) # Link up any Python functions so that they can be used inside the HTML
win.show()
