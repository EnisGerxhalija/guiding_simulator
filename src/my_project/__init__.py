"""My Project: A short description of the project.

Keep this file light. Import only what forms the public API, and never load
data, read files or run analysis at import time.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("my-project")
except PackageNotFoundError:  # pragma: no cover - only when not installed
    __version__ = "0.0.0+unknown"

# To let users write `from my_project import thing`, import it here and list
# it in __all__, e.g.:  from my_project.example import gaussian
__all__ = ["__version__"]
