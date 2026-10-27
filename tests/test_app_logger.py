import logging 
from collections.abc import Iterator 
from pathlib import Path
import pytest 
import app_logger 
from logging.handlers import TimedRotatingFileHandler
import os
import time
from app_logger import cleanup_old_archives

@pytest.fixture 
def logger_and_log_file( 
    monkeypatch: pytest.MonkeyPatch, 
    tmp_path: Path, 
) -> Iterator[tuple[logging.Logger, Path]]: 
    """Creates an isolated logger and a temporary file for the test."""
    
    log_dir = tmp_path / "logs"
    log_file = log_dir / "app.log"

    monkeypatch.setattr(app_logger, "LOG_DIR", log_dir)
    monkeypatch.setattr(app_logger, "LOG_FILE", log_file)

    logger_name = f"test.{tmp_path.name}"
    logger = app_logger.setup_logger(logger_name)

    yield logger, log_file

    # We close the file after the test to free up the resource.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

def test_info_is_written_and_debug_is_filtered( 
    logger_and_log_file: tuple[logging.Logger, Path], 
) -> None: 
    """INFO is written to the file, DEBUG is not."""

    logger, log_file = logger_and_log_file

    logger.info("Message INFO")
    logger.debug("Message DEBUG")

    for handler in logger.handlers:
        handler.flush()

    content = log_file.read_text(encoding="utf-8")

    assert "Message INFO" in content
    assert "Messageе DEBUG" not in content
    assert "INFO" in content
    
def test_repeated_setup_does_not_duplicate_handlers( 
    logger_and_log_file: tuple[logging.Logger, Path], 
) -> None: 
    """Re‑configuration does not add extra handlers."""
    
    logger, log_file = logger_and_log_file

    # We only count handlers that were created by our application.
    app_handlers_before = [
        handler
        for handler in logger.handlers
        if isinstance(handler, TimedRotatingFileHandler)
    ]

    same_logger = app_logger.setup_logger(logger.name)

    app_handlers_after = [
        handler
        for handler in logger.handlers
        if isinstance(handler, TimedRotatingFileHandler)
    ]

    assert same_logger is logger
    assert len(app_handlers_before) == 1
    assert len(app_handlers_after) == 1

    logger.info("One entry")

    for handler in logger.handlers:
        handler.flush()

    content = log_file.read_text(encoding="utf-8")

    assert content.count("One entry") == 1

    
def test_rotation_creates_archive( 
    logger_and_log_file: tuple[logging.Logger, Path], 
) -> None: 
    """Forced rotation creates an archive of the previous file."""
    
    logger, log_file = logger_and_log_file

    logger.info("Message prior to rotation")

    handler = next(
        handler
        for handler in logger.handlers
        if isinstance(handler, TimedRotatingFileHandler)
    )

    handler.flush()
    handler.doRollover()

    logger.info("Message after rotation")

    for current_handler in logger.handlers:
        current_handler.flush()

    archives = list(log_file.parent.glob("app.log.*"))

    assert len(archives) == 1
    assert "Message prior to rotation" in archives[0].read_text(
        encoding="utf-8"
    )
    assert "Message after rotation" in log_file.read_text(
        encoding="utf-8"
    )

def test_rotation_handler_has_24_hourly_backups( 
    logger_and_log_file: tuple[logging.Logger, Path], 
) -> None: 
    """The handler is configured for hourly rotation and 24 archives."""
    
    logger, _ = logger_and_log_file

    handler = next(
        handler
        for handler in logger.handlers
        if isinstance(handler, TimedRotatingFileHandler)
    )

    assert handler.when == "H"
    assert handler.interval == 3600
    assert handler.backupCount == 24
    
def test_old_archives_are_deleted_but_recent_archives_remain( 
    tmp_path: Path, 
) -> None: 
    """Old archives are deleted, while new ones remain."""
    
    log_file = tmp_path / "app.log"
    old_archive = tmp_path / "app.log.old"
    recent_archive = tmp_path / "app.log.recent"

    old_archive.write_text("Old archive", encoding="utf-8")
    recent_archive.write_text("Latest archive", encoding="utf-8")

    now = time.time()
    old_time = now - (25 * 60 * 60)
    recent_time = now - (2 * 60 * 60)

    os.utime(old_archive, (old_time, old_time))
    os.utime(recent_archive, (recent_time, recent_time))

    cleanup_old_archives(log_file)

    assert not old_archive.exists()
    assert recent_archive.exists()
