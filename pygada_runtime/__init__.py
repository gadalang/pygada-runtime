from . import __version__ as version_info
from .__version__ import __version_major__, __version_long__, __version__, __status__

from ._main import *
from ._runner import Process, run
from ._stream import *
