from .log import getLogger, modulename

log = getLogger(modulename())
log.debug("Hello from util")


def image_fn(dt):
    """
    Takes a datetime.datetime.
    Returns a string filename that an image taken at 'dt' should be saved as
    based on the config options.
    """
    from . import config

    fnformat = config.data["filename"]
    datestr = dt.strftime(config.data["strftime"])
    imgfn = fnformat.format(strftime=datestr)
    return imgfn


def image_fp(dt):
    """
    Takes a datetime.datetime.
    Returns a pathlib.Path that an image taken at 'dt' should be saved to
    based on the config options. Includes filename.
    """
    from pathlib import Path
    from . import config

    imgfn = image_fn(dt)
    img_dir = Path(config.data["img_dir"])
    img_dir.mkdir(parents=True, exist_ok=True)
    imgfp = img_dir / imgfn
    return imgfp


def save_screenshot():
    """
    Captures a screenshot of the entire screen (all monitors)
    and saves it.
    Output directory and filename are based on config options.
    """
    from datetime import datetime
    from .validpath import is_pathname_valid
    from desktopmagic.screengrab_win32 import getScreenAsImage

    img = getScreenAsImage()
    imgfp = image_fp(datetime.now())
    assert is_pathname_valid(str(imgfp)), \
           "Final image filename is not a valid path."
    img.save(imgfp)
    log.debug(f"Screenshot saved to '{imgfp}'")
    return imgfp


#from contextlib import contextmanager
#@contextmanager
#def new_console():
    #import sys
    #import ctypes
    #kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    #allocated = bool(kernel32.AllocConsole())
    #old_stdin = sys.stdin
    #old_stderr = sys.stderr
    #old_stdout = sys.stdout
    #try:
        #with open('CONIN$', 'r') as sys.stdin,\
             #open('CONOUT$', 'w') as sys.stdout,\
             #open('CONOUT$', 'w', buffering=1) as sys.stderr:
            #yield
    #finally:
        #sys.stderr = old_stderr
        #sys.stdout = old_stdout
        #sys.stdin = old_stdin


def attach_console(title=None):
    import sys
    import subprocess
    import ctypes
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    executable = sys.executable.replace("pythonw.exe", "python.exe")
    cmd = [executable, "-c", "print()"]
    child = subprocess.Popen(cmd,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=False)
    #kernel32.FreeConsole()
    child.stdout.readline()
    attached = bool(kernel32.AttachConsole(child.pid))
    if not attached:
        err = ctypes.get_last_error()
        log.warning("Could not allocate new console. Error code:", err)
    #old_stdin = sys.stdin
    #old_stderr = sys.stderr
    #old_stdout = sys.stdout
    sys.stdin = open('CONIN$', 'r')
    sys.stdout = open('CONOUT$', 'w')
    sys.stderr = open('CONOUT$', 'w', buffering=1)
    if title:
        kernel32.SetConsoleTitleW(title)