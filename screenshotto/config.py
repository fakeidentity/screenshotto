# -*- coding: utf-8 -*-

import os
from configparser import SafeConfigParser, NoSectionError
from logging import getLogger
import re

import appdirs

from .log import modulename
from .__init__ import APPNAME
from . import knownpaths
from .validpath import is_pathname_valid, is_path_exists_or_creatable

log = getLogger(modulename())
log.debug("Helo its me ur config")

config_dir = appdirs.user_config_dir(APPNAME, False)
configfn = f"{APPNAME}.ini"
config_path = os.path.join(config_dir, configfn)

# Default values

def default_dir():
    log.debug("Determining default img_dir")
    img_dir = knownpaths.get_path(knownpaths.FOLDERID.Pictures,
                        knownpaths.UserHandle.current)
    assert is_path_exists_or_creatable(img_dir), \
           f"'{img_dir}' is not a valid path"
    if is_pathname_valid(APPNAME):
        validappname = APPNAME
    else:
        log.warning(f"'{APPNAME}' is not suitable as part of a valid path")
        validappname = os.path.basename(os.path.dirname(__file__))
    img_dir = os.path.join(img_dir, validappname)
    log.debug(f"'{img_dir}' is our default img_dir")

    return img_dir


data = {
    "img_dir": default_dir,
    "strftime": "%Y-%m-%d %H%M",
    "filename": "{strftime}.png"
}


def get_config():
    config = SafeConfigParser(interpolation=None)
    if not user_config_exists():
        log.debug("No existing config file.")
        generate_config()
        log.info(f"Config file: {config_path}")
    config.read([config_path])
    return config


def user_config_exists():
    return os.path.isfile(config_path)


def generate_config(configdata=None):
    log.debug("Generating config")
    global _old_data

    if not configdata:
        configdata = data

    for k, v in data.items():
        if callable(v):
            data[k] = v()

    config = SafeConfigParser(allow_no_value=True, interpolation=None)

    sect = APPNAME
    config.add_section(sect)
    config.set(sect, "; This file will regenerate itself if you fuck it up.")
    config.set(sect, "; :)\n")

    config.set(sect, "\n; Where to save the images")
    config.set(sect, "img_dir", configdata["img_dir"])

    config.set(sect, "\n; How to format the date/time")
    config.set(sect, "; See http://strftime.org/ or "
               "https://docs.python.org/3.6/library/datetime.html"
               "#strftime-and-strptime-behavior for a reference")
    config.set(sect, "; '%c' gives a complete date and time "
               "appropriate to your locale")
    config.set(sect, "; '%a %d %B %Y %H:%M' is nice and human-readable "
               "- it looks like 'Sat 16 June 2018 09:00'")
    config.set(sect, "; '%Y-%m-%d %H%M' should be easy to sort and browse")
    config.set(sect, "strftime", configdata["strftime"])

    config.set(sect, "\n; Image filename format")
    config.set(sect, "; {strftime} is a placeholder "
               "for the date the image was captured "
               "where the time is formatted as specified "
               "in the 'strftime' option ")
    config.set(sect, "; You might like to use 'Desktop - {strftime}.png'")
    config.set(sect, "; You can choose not to include {strftime} at all"
               " but then every new image would overwrite the previous one.")
    config.set(sect, "; The image format is based on the extension"
               ", so you can use .png, .jpg, and so on "
               "and the image will be in that format.")
    config.set(sect, "filename", configdata["filename"])

    write_cfg(config)
    _old_data = configdata.copy()


def write_cfg(config, config_fp=config_path):
    # save / write to file
    log.debug(f"Writing config file to '{config_path}'.")
    os.makedirs(config_dir, exist_ok=True)
    with open(config_fp, "w", encoding="utf-8") as f:
        config.write(f)


config = get_config()

_require_regen = False
num_options_in_file = 0
try:
    for setting_name in config.options(APPNAME):
        num_options_in_file += 1

        val = config.get(APPNAME, setting_name)

        # silently fix accidental quotes around config file values
        if val.startswith('"') and val.endswith('"') or \
           val.startswith("'") and val.endswith("'"):
            log.warning("Some idiot put quotes around the value of "
                     f"{setting_name} in the config file. We'll fix it.")
            val = val[1:-1]
            _require_regen = True

        # replace some common, invalid windows filename characters
        # for the options that eventually affect/turn into filenames
        if setting_name in ["strftime", "filename"]:
            val, num_invalid_chars = re.subn(r"[<>:\"/\\|?*]", "_", val)
            if num_invalid_chars:
                log.warning(f"Replaced {num_invalid_chars} characters that are "
                            "not allowed in windows filenames "
                            "in {setting_name}.")
                _require_regen = True

        data[setting_name] = val
except NoSectionError:
    log.warning(f"No '{APPNAME}' section in config. Maybe somebody fucked it up? "
                "It'll fix itself.")

_old_data = data.copy()

log.debug(data)

# Ensure any missing elements are written to file.
# Everything will work without this, but I think it's nicer to automagically
#  fix the file than to continually work around a broken one.
if len(data) > num_options_in_file:
    log.debug("Config file is missing one or more options. "
              "Generating a new file. Old settings carry over.")
    _require_regen = True

if _require_regen:
    generate_config()

def has_changed():
    if _old_data != data:
        return True
    return False
