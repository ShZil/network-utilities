from flexx import flx

__author__ = 'Shaked Dan Zilberman'


class Example(flx.Widget):

    def init(self):
        with flx.VBox():
            flx.Label(text='Local Network Scanner', style="text-align: center; font-size: 24px; font-weight: bold;")

            with flx.HBox(flex=1):
                self.hello = flx.Button(text='hello', flex=1)
                self.bye = flx.Button(text='bye', flex=2)
    

    @flx.reaction('hello.pointer_click')
    def _button_clicked(self, *events):
        ev = events[-1]
        print("hello")


def main():
    app = flx.App(Example)
    app.launch('app')
    flx.run()


if __name__ == '__main__':
    main()
