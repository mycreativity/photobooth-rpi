from kivy.config import Config
# Set window size (e.g. 1080x1920 for portrait touchscreen)
Config.set('graphics', 'width', '1080')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'resizable', False)  # Optional: disable resizing

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from screens.start_screen import StartScreen

class PhotoBoothApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        return sm

if __name__ == '__main__':
    PhotoBoothApp().run()
