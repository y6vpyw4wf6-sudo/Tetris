import logging 
import os 
from logging.handlers import TimedRotatingFileHandler 
from pathlib import Path 
import time


BASE_DIR = Path(__file__).resolve().parent 
LOG_DIR = BASE_DIR / "logs" 
LOG_FILE = LOG_DIR / "app.log"

LOG_LEVEL = logging.INFO 
LOG_RETENTION_HOURS = 24 
LOG_RETENTION_SECONDS = LOG_RETENTION_HOURS * 60 * 60

LOG_FORMAT = ( 
    "%(asctime)s,%(msecs)03d | %(levelname)s | " 
    "%(name)s | %(message)s" 
) 
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def cleanup_old_archives(log_file: Path) -> None: 
    """Deletes log archives that are older than 24 hours."""
    
    expiration_time = time.time() - LOG_RETENTION_SECONDS

    for archive in log_file.parent.glob(f"{log_file.name}.*"):
        try:
            if archive.is_file() and archive.stat().st_mtime < expiration_time:
                archive.unlink()
        except OSError:
            # The archive cleanup error should not stop the application.
            continue

class RetentionTimedRotatingFileHandler(TimedRotatingFileHandler): 
    """Hourly rotation with additional age‑based cleaning."""
    
    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        cleanup_old_archives(Path(self.baseFilename))

    def doRollover(self) -> None:
        super().doRollover()

        # After renaming the file, we record the time when the archive was created.
        log_file = Path(self.baseFilename)
        archives = list(log_file.parent.glob(f"{log_file.name}.*"))

        if archives:
            try:
                newest_archive = max(
                    archives,
                    key=lambda archive: archive.stat().st_ctime,
                )
                os.utime(newest_archive, None)
            except OSError:
                pass

        cleanup_old_archives(log_file)
        
def setup_logger(name: str) -> logging.Logger: 
    """Configures the logger with hourly rotation and a 24‑hour retention period."""
    
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False

    if logger.handlers:
        return logger

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        cleanup_old_archives(LOG_FILE)

        handler = RetentionTimedRotatingFileHandler(
            filename=LOG_FILE,
            when="H",
            interval=1,
            backupCount=LOG_RETENTION_HOURS,
            encoding="utf-8",
            delay=False,
        )

    except OSError as exc:
        raise RuntimeError(
            f"Не удалось создать или открыть файл логов "
            f"'{LOG_FILE}': {exc}"
        ) from exc

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
