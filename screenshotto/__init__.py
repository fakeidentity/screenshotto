import os
import appdirs
from . import version


APPNAME = "Screenshotto"
__version__ = version.version
VERSION_STRING = f"{APPNAME} - version {__version__}"
CONFIG_DIR = appdirs.user_config_dir(APPNAME, False)
CONFIG_FN = f"{APPNAME}.ini"
CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FN)
