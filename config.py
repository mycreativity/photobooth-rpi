from utils.font_utils import FontUtils


VERSION = "1.0"
PHOTO_FOLDER = "photos"
FPS = 60

FONT_DISPLAY = FontUtils.load_font('assets/fonts/Pacifico-Regular.ttf', 20)
# LabelBase.register(name='HEADING', fn_regular='assets/fonts/Pacifico-Regular.ttf')
# LabelBase.register(name='TEXT', fn_regular='assets/fonts/Poppins-Regular.ttf')
# LabelBase.register(name='BUTTON', fn_regular='assets/fonts/Poppins-ExtraBold.ttf')
# LabelBase.register(name='BUTTON_LARGE', fn_regular='assets/fonts/Poppins-ExtraBold.ttf')
# LabelBase.register(name='LABEL', fn_regular='assets/fonts/Poppins-Regular.ttf')
FONT_MONO = FontUtils.load_font('assets/fonts/SpaceMono-Regular.ttf', 12)

PRIMARY_COLOR = (209, 85, 29)
PRIMARY_COLOR_DARK = (164, 48, 8)
SECONDARY_COLOR = '#643a1eff'
SECONDARY_COLOR_DARK = (100, 130, 150)
SURFACE_COLOR = '#eedabaff'