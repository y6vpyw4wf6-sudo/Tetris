from app_logger import setup_logger


def main() -> None: 
    """Демонстрирует работу логирования."""
    
    log = setup_logger(__name__)

    log.info("Приложение запущено")
    log.info("Проверка записи на русском языке")
    log.debug("Это сообщение не должно попасть в файл")
    log.warning("Это предупреждение для проверки")

if __name__ == "__main__": 
    main()