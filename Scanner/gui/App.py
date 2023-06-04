from import_handler import ImportDefence
with ImportDefence():
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, FadeTransition

from gui.AppState import State
from gui.Screens.StartScreen import StartScreen
from gui.Screens.ScanScreen import ScanScreen
from gui.Screens.SaveScreen import SaveScreen
from gui.Screens.KnowScreen import KnowScreen
from gui.Screens.ViewScreen import ViewScreen
from gui.Hover import Hover


class MyApp(App):
    """The main application, using `kivy`.
    Includes five screens:
    1. ScanScreen
    2. SaveScreen
    3. KnowScreen
    4. StartScreen
    5. ViewScreen (only accessible through `SaveScreen.ImportButton`)


    Args:
        App (kivy): the kivy base app.
    """

    def build(self):
        """Construct the GUI of the application.
        This is the entry point of creating the structure of the kivy GUI.

        Returns:
            ScreenManager: the base widget of the app.
        """
        self.title = 'Local Network Scanner'
        self.icon = 'favicon.png'
        from kivy.core.window import Window
        Window.size = (1300, 800)

        screens = ScreenManager(transition=FadeTransition())
        State().setScreenManager(screens)

        screens.add_widget(StartScreen())
        screens.add_widget(ScanScreen())
        screens.add_widget(SaveScreen())
        screens.add_widget(KnowScreen())
        screens.add_widget(ViewScreen())

        State().screen('Start')

        Hover.start()

        return screens


if __name__ == '__main__':
    print("This file handles a class called MyApp (yes, tutorial-ly, I know) which extends kivy's App.")
    print("It builds the kivy GUI, plain and simple.")
