import os
import kiwi

APP_ABS_PATH = os.path.dirname(os.path.abspath(__file__))
GLADEFILE = os.path.join(APP_ABS_PATH, 'kmc_editor.glade')
kiwi.environ.environ.add_resource('glade', APP_ABS_PATH)
