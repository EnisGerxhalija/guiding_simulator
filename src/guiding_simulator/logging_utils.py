"""Logging set-up for scripts and notebooks.

Library modules only *create* loggers::

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Loaded %d files", n)

and never configure logging themselves. The entry point (a script or a
notebook) calls :func:`setup_logging` once, choosing where messages go.
"""

import logging
import sys
from pathlib import Path

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def setup_logging(
    level: str | int = "INFO", log_file: str | Path | None = None
) -> None:
    """Send log messages to the terminal and, optionally, to a file.

    Safe to call more than once (e.g. when re-running a notebook cell): any
    previous configuration is replaced.

    Parameters
    ----------
    level : str or int, default "INFO"
        Lowest level to show: "DEBUG", "INFO", "WARNING" or "ERROR".
    log_file : str or pathlib.Path, optional
        Also write messages to this file. Its folder is created if needed.
    """
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if log_file is not None:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(level=level, format=LOG_FORMAT, handlers=handlers, force=True)
