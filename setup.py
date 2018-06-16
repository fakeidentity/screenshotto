from setuptools import setup, find_packages
from pip.req import parse_requirements

from screenshotto import __version__


setup(
    name="screenshotto",
    version=__version__,
    description="Take screenshots",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=4.1.1",
        "appdirs>=1.4.3",
        "Desktopmagic>=14.3.11",
        "schedule>=0.5.0"
    ],
    entry_points={
        "console_scripts": [
            "screenshotto = run_screenshotto:cli",
        ],
        "gui_scripts": [
            "screenshotto_silent = run_screenshotto:cli",
        ]
    }
)