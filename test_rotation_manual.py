from app_logger import setup_logger


def main() -> None: 
    """Проверяет принудительную ротацию лог-файла."""
    
    log = setup_logger("rotation_test")

    log.info("Message prior to rotation")

    handler = next(
        h for h in log.handlers
        if hasattr(h, "doRollover")
    )

    handler.doRollover()

    log.info("Message after rotation")

    print("Rotation complete. Check the logs folder..")
    
if __name__ == "__main__": 
    main()
