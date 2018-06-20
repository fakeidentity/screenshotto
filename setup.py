from setuptools import setup, find_packages

from screenshotto import version


setup(
    name="screenshotto",
    version=version.version,
    description="Take screenshots",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=4.1.1",
        "appdirs>=1.4.3",
        "Desktopmagic>=14.3.11",
        "schedule>=0.5.0"
        "arrow>=0.12.1",
        "pywin32>=220",
        "Pillow>=5.1.0"
    ],
    scripts=["run_screenshotto.py"],
    entry_points={
        "console_scripts": [
            "screenshotto = run_screenshotto:cli",
        ],
        "gui_scripts": [
            "screenshotto_silent = run_screenshotto:cli",
        ]
    }
)