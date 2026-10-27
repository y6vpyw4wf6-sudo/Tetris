import curses
# import psycopg

from game.engine import Game
from game.settings import W, H
from game.session import play
from ui.render import COLORS, PAIR
from ui.menus import main_menu, select_save_menu, show_message
from services.save_repository import get_save, get_latest_save


def run_app(stdscr): 
    curses.curs_set(0) 
    curses.start_color() 
    curses.use_default_colors()
    
    for kind, color in COLORS.items():
        curses.init_pair(PAIR[kind], color, -1)

    stdscr.keypad(True)
    stdscr.timeout(30)

    h, w = stdscr.getmaxyx()

    if h < H + 3 or w < 50:
        raise SystemExit(
            f"Терминал слишком маленький: "
            f"нужно минимум 50x{H + 3}, сейчас {w}x{h}"
        )

    while True:
        choice = main_menu(stdscr)

        if choice == "exit":
            break

        game = None
        save_id = None

        # try:
        if choice == "new_game":
            game = Game()
        elif choice in ("load_save", "continue"):
            show_message(
                stdscr,
                "Загрузка сохранений временно отключена.",
            )
            continue
                
        #     if choice == "load_save":
        #         save_id = select_save_menu(stdscr)

        #         # The player pressed Esc.
        #         if save_id is None:
        #             continue

        #         saved = get_save(save_id)

        #         if saved is None:
        #             show_message(
        #                 stdscr,
        #                 "Сохранение не найдено.",
        #             )
        #             continue

        #         game = Game.load_state(saved["game_state"])

        #     elif choice == "continue":
        #         saved = get_latest_save()

        #         if saved is None:
        #             show_message(
        #                 stdscr,
        #                 "Сохранений пока нет. "
        #                 "Сначала начни новую игру.",
        #             )
        #             continue

        #         save_id = saved["id"]
        #         game = Game.load_state(saved["game_state"])

        # except (
        #     psycopg.Error,
        #     ValueError,
        #     KeyError,
        #     TypeError,
        # ) as exc:
        #     show_message(
        #         stdscr,
        #         f"Не удалось загрузить игру: {exc}",
        #     )
        #     continue


        while True:
            restart = play(
                stdscr,
                game=game,
                save_id=save_id,
            )

            if not restart:
                break

            # We start a new game after the restart command.
            game = Game()
            save_id = None
