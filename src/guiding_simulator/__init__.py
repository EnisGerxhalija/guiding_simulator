"""Guiding Simulator: Analysis and simulation code for tip/tilt guiding simulator

Keep this file light. Import only what forms the public API, and never load
data, read files or run analysis at import time.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("guiding-simulator")
except PackageNotFoundError:  # pragma: no cover - only when not installed
    __version__ = "0.0.0+unknown"

# To let users write `from guiding_simulator import thing`, import it here and list
# it in __all__, e.g.:  from guiding_simulator.example import gaussian
__all__ = ["__version__"]
