import os
import appdirs


APPNAME = "Screenshotto"
__version__ = "1.0.0"
VERSION_STRING = f"{APPNAME} - version {__version__}"
CONFIG_DIR = appdirs.user_config_dir(APPNAME, False)
CONFIG_FN = f"{APPNAME}.ini"
CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FN)
