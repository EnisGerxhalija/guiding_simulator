"""Tests for logging set-up."""

import logging

from guiding_simulator.logging_utils import setup_logging


def test_setup_logging_writes_to_file(tmp_path):
    root = logging.getLogger()
    saved_handlers, saved_level = root.handlers[:], root.level
    try:
        log_file = tmp_path / "logs" / "run.log"
        setup_logging("DEBUG", log_file=log_file)
        logging.getLogger("guiding_simulator.demo").debug("hello %s", "world")
        assert "hello world" in log_file.read_text(encoding="utf-8")
    finally:  # put pytest's own logging set-up back
        for handler in root.handlers:
            handler.close()
        root.handlers[:] = saved_handlers
        root.setLevel(saved_level)
