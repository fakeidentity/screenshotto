#! python3.6

import os
import sys
from functools import partial
import logging.handlers
import atexit
from pathlib import Path # for schedule
from textwrap import dedent # schedule

import appdirs
import click

from screenshotto.__init__ import (APPNAME, VERSION_STRING, CONFIG_PATH,
                                   CONFIG_DIR)
from screenshotto.log import logger_setup, handle_exception
from screenshotto.clickaliases import ClickAliasedGroup

log_dir = appdirs.user_log_dir(APPNAME, False)
log = logger_setup(log_dir, __file__)

uncaught_exception_handler = partial(handle_exception, log)
sys.excepthook = uncaught_exception_handler

log.debug(VERSION_STRING)

from screenshotto.util import save_screenshot, attach_console
from screenshotto import config

SCHEDFP = Path(CONFIG_DIR) / "schedule.txt"


def set_debug(debug=True):
    log.debug(f"set_debug({debug})")
    for loghandler in log.handlers:
        if isinstance(loghandler, logging.handlers.MemoryHandler):
            conhandler = loghandler.target
            if debug:
                # set flushlevel so debugs are handled when we flush in a sec
                loghandler.flushLevel = logging.DEBUG
            else:
                conhandler.setLevel(logging.INFO)
            # 'send' all log messages that have been queued until this point
            log.debug("Flushing log.")
            loghandler.flush()
            # we don't need to queue/buffer messages anymore
            # so change capacity to 1 - effectively flushing on every message
            # we could remove memhandler and add conhandler here BUT then
            # conhandler wouldn't be last, and strip ansi formatter doesn't work
            loghandler.capacity = 1


def keep_open():
    input("\nPress enter to close...")


def echo(*args, **kwargs):
    try:
        click.echo(*args, **kwargs)
    except AttributeError:
        pass


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS, cls=ClickAliasedGroup,
             invoke_without_command=True)
@click.option("--show-window", "-sw", is_flag=True,
              help="Force show console window and keep it open.")
@click.option("--debug", is_flag=True,
              help="Show debug messages")
@click.option("--version", "-v", is_flag=True,
              help="Print version number")
@click.pass_context
def cli(ctx, show_window, debug, version):
    """
    Capture a screenshot of the entire screen (all monitors) and save it.
    \n
    There is no prompt. The entire operation is unattended,
    though you will see basic log messages.
    \n
    Files are named and saved according to options in the config file
    which is generated automatically on first run
    and can be found in the user config directory.
    """
    if show_window:
        log.debug("Force show window mode")
        atexit.register(keep_open)

        if os.path.basename(sys.executable) == "pythonw.exe":
            log.debug("Currently running with pythonw.exe. "
                      "Attaching new python console.")
            attach_console(APPNAME)

    if debug:
        log.debug("Debug mode")
    set_debug(debug) # important to set this either way so log is flushed!

    if version:
        echo(VERSION_STRING)
    elif not ctx.invoked_subcommand:
        log.debug("No subcommand. Showing help.")
        print(ctx.get_help())


@cli.command(name="screenshot",
             aliases=["capture", "save", "ss"],
             help="Capture and save a screenshot without user interaction")
def screenshot():
    imgfp = save_screenshot()
    echo(f"\nScreenshot saved to:\n\t{imgfp}")


@cli.command(name="config", help="Open config file")
def open_config_for_edit():
    # default config is generated automatically when config.py is imported
    #os.startfile(CONFIG_PATH, "edit")
    click.edit(filename=CONFIG_PATH)


@cli.command(name="log", help="Open log file")
def view_log():
    os.startfile(log.logfp)


@cli.group(name="schedule",
           help="Run screenshot command on a schedule",
           cls=ClickAliasedGroup)
def schedule_group():
    log.debug("schedule_group()")


def write_default_schedule():
    log.debug(f"Writing default schedule to {SCHEDFP}")
    s = dedent("""
    # Uncomment one or more of the example lines below, or add your own here:


    ## https://schedule.readthedocs.io/en/stable/
    #schedule.every().second.do(job)
    #schedule.every(10).seconds.do(job)
    #schedule.every(30).to(60).seconds.do(job)
    #schedule.every().minute.do(job)
    #schedule.every(10).minutes.do(job)
    #schedule.every(5).to(10).minutes.do(job)
    #schedule.every().hour.do(job)
    #schedule.every(6).hours.do(job)
    #schedule.every(6).to(12).hours.do(job)
    #schedule.every().day.do(job)
    #schedule.every().day.at("06:30").do(job)
    #schedule.every(2).days.do(job)
    #schedule.every(2).days.at("15:00").do(job)
    #schedule.every().week.do(job)
    #schedule.every(2).weeks.do(job)
    #schedule.every().monday.do(job)
    #schedule.every().tuesday.do(job)
    #schedule.every().wednesday.do(job)
    #schedule.every().thursday.do(job)
    #schedule.every().friday.do(job)
    #schedule.every().saturday.do(job)
    #schedule.every().sunday.at("23:59").do(job)
    """)
    with open(SCHEDFP, "w") as f:
        f.write(s)


@schedule_group.command(name="edit",
                        help="Open schedule file for editing")
def schedule_edit():
    log.debug("schedule_edit()")
    if not os.path.isfile(SCHEDFP):
        write_default_schedule()
    #os.startfile(SCHEDFP, "edit")
    click.edit(filename=SCHEDFP)


@schedule_group.command(name="run",
                        aliases=["start"],
                        help="Start processing schedule.")
@click.pass_context
def schedule_run(ctx):
    log.debug("schedule_run()")
    if not os.path.isfile(SCHEDFP):
        echo("You don't have a schedule set up!\n")
        ctx.invoke(schedule_edit)
    template = dedent("""
        from time import sleep
        import schedule
        import arrow


        def job():
            termw, _ = click.get_terminal_size()
            print("\\r" + " ".ljust(termw), end="")
            click.get_current_context().invoke(screenshot)
            print()


        {usercode}

        termw, _ = click.get_terminal_size()
        while True:
            nextrun = schedule.next_run()
            if not nextrun:
                log.debug("Schedule has no jobs defined")
                cmdpath = ctx.command_path.split()
                cmdpath[-1] = "edit"
                cmdpath = " ".join(cmdpath)
                echo("Schedule has no jobs defined! "
                           "Maybe try '" + cmdpath + "'")
                break
            nextrun = arrow.get(schedule.next_run(), "local")
            timestr = nextrun.humanize()
            timestr = timestr.replace("just now", "imminently")
            if timestr == "in seconds":
                secs = (nextrun - arrow.now()).total_seconds()
                timestr = "in " + str(int(secs)) + " seconds"
            print(("\\r" + "Next screenshot will be captured "
                  + timestr + "...").ljust(termw),
                  end="")
            schedule.run_pending()
            sleep(1)
        """)
    with open(SCHEDFP, "r") as f:
        code = template.format(usercode=f.read())
    #print(code)
    exec(code)



if __name__ == "__main__":
    cli()