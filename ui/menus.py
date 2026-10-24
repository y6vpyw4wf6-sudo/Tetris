import curses
import psycopg
from app_logger import setup_logger

from services.save_repository import (
    list_saves,
    save_game,
)

logger = setup_logger(__name__)

def pause_menu(stdscr, game, save_id=None): 
    """Displays the pause menu and processes the player’s actions."""
    options = [
        "Продолжить игру",
        "Сохранить игру",
        "Выйти без сохранения",
    ]

    selected = 0
    message = ""

    # While the menu is open, we’re waiting for key presses.
    stdscr.timeout(-1)

    try:
        while True:
            stdscr.erase()
            h, w = stdscr.getmaxyx()

            title = "ТЕТРИС — ПАУЗА"
            stdscr.addstr(2, max(0, (w - len(title)) // 2), title)

            for i, option in enumerate(options):
                prefix = "> " if i == selected else "  "
                text = prefix + option
                x = max(0, (w - len(text)) // 2

                )
                stdscr.addstr(5 + i * 2, x, text)

            if message:
                stdscr.addstr(12, 2, message[:max(0, w - 4)])

            stdscr.addstr(
                15, 2, "Стрелки — выбор, Enter — подтвердить"
            )
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options)

            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options)

            elif key in (10, 13, curses.KEY_ENTER):
                # Continue the game.
                if selected == 0:
                    return "continue", save_id

                # Save the game.
                elif selected == 1:
                    name = "Моя партия"

                    if save_id is None:
                        # New batch: we’re requesting the name.
                        stdscr.erase()
                        stdscr.addstr(2, 2, "Название сохранения: ")
                        stdscr.addstr(3, 2, "> ")
                        stdscr.refresh()

                        curses.curs_set(1)
                        curses.echo()

                        try:
                            raw_name = stdscr.getstr(
                                3, 4, 100
                            )
                        finally:
                            curses.noecho()
                            curses.curs_set(0)

                        name = raw_name.decode(
                            "utf-8", errors="replace"
                        ).strip() 
                        
                        if not name:
                            name = "Моя партия"

                    try:
                        save_id = save_game(
                            name,
                            game.get_state(),
                            save_id=save_id,
                        )
                        message = (
                            f"Сохранение №{save_id} готово."
                        )

                    except (psycopg.Error, ValueError) as exc:
                        message = (
                            f"Не удалось сохранить: {exc}"
                        )

                # Exit the current game.
                elif selected == 2:
                    return "quit", save_id

    finally:
        # After exiting the menu, we return to the normal mode.
        stdscr.timeout(30)
        
def select_save_menu(stdscr): 
    """Shows the saves and returns the ID of the selected game."""
    
    saves = list_saves()

    if not saves:
        show_message(stdscr, "Сохранений пока нет.")
        return None

    selected = 0
    offset = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = "ВЫБЕРИ СОХРАНЕНИЕ"
        stdscr.addstr(
            2,
            max(0, (w - len(title)) // 2),
            title,
        )

        # How many saves fit on the screen?.
        visible_count = max(1, h - 9)

        # We don’t show anything outside the list.
        offset = min(offset, max(0, len(saves) - visible_count))

        for i in range(
            offset,
            min(offset + visible_count, len(saves)),
        ):
            save = saves[i]

            line = (
                f"{save['name']} | "
                f"Очки: {save['score']} | "
                f"Уровень: {save['level']}"
            )

            # We don’t let the long title go beyond the screen boundaries.
            line = line[:max(1, w - 8)]

            prefix = "> " if i == selected else "  "
            stdscr.addstr(5 + i - offset, 2, prefix + line)

        stdscr.addstr(
            h - 2,
            2,
            "↑ ↓ — выбор, Enter — загрузить, Esc — назад"[:max(1, w - 4)],
        )
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(saves)

        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(saves)

        elif key in (10, 13, curses.KEY_ENTER):
            save = saves[selected]
            
            logger.info(
                "Save selected: id=%s, name=%s",
                save["id"],
                save["name"]
            )
            
            return save["id"]
        

        elif key == 27:  # Esc
            logger.info("Save selection cancelled")
            return None

        # When moving, the selected item remains visible.
        if selected < offset:
            offset = selected
        elif selected >= offset + visible_count:
            offset = selected - visible_count + 1

        
def main_menu(stdscr): 
    """Displays the main menu and returns the player’s choice."""
    
    options = [
        "Новая игра",
        "Загрузить сохранение",
        "Продолжить последнюю игру",
        "Выход",
    ]

    selected = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = "ТЕТРИС"
        stdscr.addstr(
            2,
            max(0, (w - len(title)) // 2),
            title,
        )

        for i, option in enumerate(options):
            prefix = "> " if i == selected else "  "
            text = prefix + option
            x = max(0, (w - len(text)) // 2)

            stdscr.addstr(6 + i * 2, x, text)

        hint = "Стрелки — выбор, Enter — подтвердить"
        stdscr.addstr(15, 2, hint[:max(1, w - 4)])
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)

        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)

        elif key in (10, 13, curses.KEY_ENTER):
            if selected == 0:
                logger.info("A new game has been selected in the main menu")
                return "new_game"
            
            elif selected == 1:
                logger.info("Loading a save file has been selected in the main menu")
                return "load_save"            

            elif selected == 2:
                logger.info("Resuming the last game has been selected in the main menu")
                return "continue"

            elif selected == 3:
                logger.info("Exit game has been selected in the main menu")
                return "exit"

def show_message(stdscr, message): 
    """Displays a message and waits for a key to be pressed."""   
    stdscr.timeout(-1)

    try:
        stdscr.erase()
        stdscr.addstr(3, 2, message[:100])
        stdscr.addstr(5, 2, "Нажми любую клавишу...")
        stdscr.refresh()
        stdscr.getch()
    finally:
        stdscr.timeout(30)