import errno
import sys
import logging
import pathlib


def get_version() -> str:
    with open(pathlib.Path(__file__).parent / 'version.txt', mode='r') as version_file:
        version = version_file.readline()
    return version


__title__ = 'configmagick'
__version__ = get_version()
__name__ = 'configmagick'

# from .libs.lib_classes import RstFile
# from .libs.lib_classes import RstConf
# from .libs.lib_main import rst_str_replace
# from .libs.lib_main import rst_inc_from_config
# from .libs.lib_main import rst_inc
