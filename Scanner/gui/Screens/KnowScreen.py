from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.screenmanager import Screen
    from kivy.uix.boxlayout import BoxLayout

from threading import Thread
from gui.Hover import Hover
from gui.Screens.Pages import Pages
from gui.dialogs import get_string, popup
from globalstuff import *


def update_know_screen(text):
    return print("update_know_screen:", text)


class KnowScreen(Screen):
    """Builds an interface that looks like this:

    ```md
    The Window (Unicode Box Art):
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.                                  │
        │  #6 Know.                                  │
        │             #3 Device Profile              │
        │                   #2 Data                  │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘
    ```

    Args:
        Screen (kivy): the base class for a screen.
    """

    def __init__(self, **kw):
        name = 'Know'
        super().__init__(name=name, **kw)
        Hover.enter(name)

        everything = BoxLayout(orientation='vertical')
        title = Label(
            text=f"[color={GREEN}]Knowledge about Network[/color]",
            size=(0, TITLE_HEIGHT),
            size_hint=(1, None),
            font_size=TITLE_FONT_SIZE,
            underline=True,
            pos_hint={'center_x': .5, 'top': 1},
            markup=True
        )
        everything.add_widget(title)
        everything.add_widget(Pages())
        everything.add_widget(KnowScreenDeviceProfileButton())
        everything.add_widget(KnowScreenInfoLabel())

        self.add_widget(everything)


class KnowScreenInfoLabel(ScrollView):
    """Holds the requested data in string format, displayed to the user.
    Has a scrolling mechanic.

    Args:
        Label (kivy): the base class from kivy.
    """

    def __init__(self, **kwargs):
        super().__init__(width=1200, **kwargs)
        self.label = Label(
            text='\nLoading data...',
            color=(1, 1, 1, 1),
            font_size=20,
            font_name="Monospace",
            size_hint_y=None,
            text_size=(self.width, None),
            halign='center'
        )
        self.label.bind(texture_size=self.label.setter('size'))
        self.add_widget(self.label)
        global update_know_screen
        update_know_screen = self.data

    def data(self, text):
        if isinstance(text, str):
            self.label.text = text
        else:
            try:
                items = text.tablestring()
                # print('\n'.join(items))
            except AttributeError:
                items = [str(x) for x in text]
            self.label.text = '\n'.join(items)


class KnowScreenDeviceProfileButton(Button):
    def __init__(self, **kwargs):
        super().__init__(text="Device Profile", size_hint=(.2, .1), pos_hint={'x': 0.39, 'top': 0.1}, font_size=20, background_color=[0, 1, 0, 1], font_name="Roboto", **kwargs)
        self.bind(on_press=device_profile)
        Hover.add(self)

def device_profile(*a):
    print(a)

    def _match_device(address):
        from NetworkStorage import NetworkStorage, match
        try:
            entity = match(address)
            for item in NetworkStorage():
                if entity.equals(item):
                    return item
        except ValueError:
            name = address
            if name == "Unknown":
                return None
            for item in NetworkStorage():
                if item.name == name:
                    return item
        return None

    def _construct_content(info: dict):
        return '\n\n'.join([f"### {key}:\n{value}" for key, value in info.items()])

    def _device_profile():
        from NetworkStorage import SpecialInformation
        address = get_string("Device Profile - Choose Address", "Insert device's MAC/IP/IPv6 address or name:")
        entity = _match_device(address)
        if entity is None:
            popup("Device Profile", f"The device was not found.\nCheck whether you wrote the address correctly.\nThe address: `{address}`", warning=True)
            return
        regular_info = entity.to_dict()
        special_info = SpecialInformation()[entity]
        information = {**regular_info, **special_info}
        print(_construct_content(information))
        # try:
        #     popup("Device Profile", _construct_content(information), info=True)
        # except Exception as e:
        #     print(e)
        print("Popped")

    Thread(target=_device_profile).start()
    # _device_profile()


if __name__ == '__main__':
    print("This file provides the Know Screen for the gui.\n")
    print("""
        ┌────────────────────────────────────────────┐
        │                  [#1 Title]                │
        │  #4 Save.                                  │
        │  #5 Scan.                                  │
        │  #6 Know.                                  │
        │             #3 Device Profile              │
        │                   #2 Data                  │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │          [_______________________]         │
        │                                            │
        │                                            │
        └────────────────────────────────────────────┘""")
