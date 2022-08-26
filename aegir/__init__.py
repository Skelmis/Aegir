import logging
from collections import namedtuple

from .format_error import FormatError
from .parsed_data import ParsedData
from .source_file import SourceFile
from aegir.aegir import Aegir

__version__ = "0.1.2"

logging.getLogger(__name__).addHandler(logging.NullHandler())
VersionInfo = namedtuple("VersionInfo", "major minor micro releaselevel serial")
version_info = VersionInfo(major=0, minor=1, micro=2, releaselevel="alpha", serial=0)

__all__ = ("Aegir", "FormatError", "ParsedData", "SourceFile")
