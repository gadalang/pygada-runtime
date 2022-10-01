"""Package for creating and running Gada nodes in Python."""
from . import __version__ as version_info
from .__version__ import __version__
from .__main__ import AbstractRunContext, run


__all__ = ["AbstractRunContext", "run", "__version__", "version_info"]
