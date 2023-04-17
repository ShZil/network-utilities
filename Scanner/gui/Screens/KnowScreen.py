from import_handler import ImportDefence
with ImportDefence():
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.button import Button

from threading import Thread


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
        super().__init__(text="Device Profile", size_hint=(.2, .1), pos_hint={'x': 0.39, 'top': 0.1}, font_size=20, background_color=[0,1,0,1], font_name="Roboto", **kwargs)
        self.bind(on_press=self.device_profile)

    def device_profile(*_):
        from NetworkStorage import NetworkStorage, match, SpecialInformation
        def _match_device(address):
            try:
                entity = match(address)
                for item in NetworkStorage():
                    if entity.equals(item):
                        return item
            except ValueError:
                name = address
                if name == "Unknown": return None
                for item in NetworkStorage():
                    if item.name == name:
                        return item
            return None

        def _construct_content(info: dict):
            return '\n\n'.join([f"### {key}:\n{value}" for key, value in info.items()])
        
        def _device_profile():
            address = get_string("Insert device's MAC/IP/IPv6 address or name:")
            entity = _match_device(address)
            if entity == None:
                popup("Device Profile", "The device was not found.\nCheck whether you wrote the address correctly.", warning=True)
                return
            regular_info = entity.to_dict()
            special_info = SpecialInformation()[entity]
            information = {**regular_info, **special_info}
            popup("Device Profile", _construct_content(information), info=True)

        Thread(target=_device_profile).start()
    