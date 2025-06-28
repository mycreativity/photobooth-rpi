from kivy.core.text import LabelBase


VERSION = "1.0"
PHOTO_FOLDER = "photos"
FPS = 60

LabelBase.register(name='DISPLAY', fn_regular='assets/fonts/Pacifico-Regular.ttf')
LabelBase.register(name='HEADING', fn_regular='assets/fonts/Pacifico-Regular.ttf')
LabelBase.register(name='TEXT', fn_regular='assets/fonts/Poppins-Regular.ttf')
LabelBase.register(name='BUTTON', fn_regular='assets/fonts/Poppins-ExtraBold.ttf')
LabelBase.register(name='BUTTON_LARGE', fn_regular='assets/fonts/Poppins-ExtraBold.ttf')
LabelBase.register(name='LABEL', fn_regular='assets/fonts/Poppins-Regular.ttf')
LabelBase.register(name='MONO', fn_regular='assets/fonts/SpaceMono-Regular.ttf')

FONT_DISPLAY = 'DISPLAY'
FONT_HEADING = 'HEADING'
FONT_TEXT = 'TEXT'
FONT_BUTTON = 'BUTTON'
FONT_BUTTON_LARGE = 'BUTTON_LARGE'
FONT_LABEL = 'LABEL'
FONT_MONO = 'MONO'

PRIMARY_COLOR = '#d1551dff'
PRIMARY_COLOR_DARK = '#a43008ff'
SECONDARY_COLOR = '#643a1eff'
SECONDARY_COLOR_DARK = (100, 130, 150)
SURFACE_COLOR = '#eedabaff'