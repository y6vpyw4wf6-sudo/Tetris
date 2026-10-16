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
import time

from game.engine import Game
from game.settings import W, H
from ui.render import draw, COLORS, PAIR
from ui.input_handler import handle_input, handle_system_input
from services.score_repository import save_score


def play(stdscr):
    game = Game()
    paused = False
    last = time.monotonic()
    score_saved = False
    
    while True:
        draw(stdscr, game, paused)
        
        if game.game_over and not score_saved:
            save_score(game.score, game.lines, game.level)
            score_saved = True
        
        key = stdscr.getch()    
        
        action = handle_system_input(key, game.game_over)

        if action == "quit":
            return False

        if action == "restart":
            return True

        if action == "pause":
            paused = not paused
            last = time.monotonic()
            continue

        if paused or game.game_over:
            continue

        reset_timer = handle_input(key, game)

        if reset_timer:
            last = time.monotonic()

        now = time.monotonic()
        if now - last >= game.delay:
            game.step()
            last = now

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    for kind, color in COLORS.items():
        curses.init_pair(PAIR[kind], color, -1)
    stdscr.keypad(True)
    stdscr.timeout(30)  # getch does not block for longer than 30 ms.

    h, w = stdscr.getmaxyx()
    if h < H + 3 or w < 50:
        raise SystemExit(f"Терминал слишком маленький: нужно минимум 50x{H + 3}, сейчас {w}x{h}")

    while play(stdscr):
        pass

if __name__ == "__main__":
    curses.wrapper(main)