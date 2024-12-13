from __future__ import annotations

import importlib

from xtream._xtream import XTream

# set the version number within the package using importlib
try:
    __version__: str | None = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    # package is not installed
    __version__ = None


__all__ = ["XTream", "__version__"]
