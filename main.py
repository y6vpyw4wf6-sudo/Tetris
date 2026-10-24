#!/usr/bin/env python3
"""Простой тетрис для терминала на curses.

Управление:
  ← →      движение
  ↑ / X    поворот
  ↓        ускорить падение
  Пробел   мгновенно сбросить фигуру
  P        пауза
  Q        выход
"""

import curses 

from app import run_app
from app_logger import setup_logger


logger = setup_logger(__name__)

def main(): 
    logger.info("Launching the game Tetris")
    
    try:
        curses.wrapper(run_app)
    except Exception:
        logger.exception("An unexpected error occurred while launching the game")
        raise
    finally:
        logger.info("The end of a game of Tetris")
    


if __name__ == "__main__": 
    main()