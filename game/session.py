import time 
from datetime import datetime, timezone

from app_logger import setup_logger 
from game.engine import Game 
from ui.render import draw 
from ui.input_handler import handle_input, handle_system_input 
from ui.menus import pause_menu 
# from services.score_repository import save_score 
# from services.session_repository import save_session


logger = setup_logger(__name__)

SESSION_LIMIT = 60


def play(stdscr, game=None, save_id=None): 
    if game is None: game = Game()
    started_at = datetime.now(timezone.utc)

    # Start of active gameplay time tracking.
    active_started_at = time.monotonic()
    active_elapsed = 0.0
    paused = False

    # Piece-drop timer.
    last = time.monotonic()

    # score_saved = False
    # session_saved = False

    logger.info("Game loop started")

    def finish_session(end_reason):
        # nonlocal session_saved

        # if session_saved:
        #     return

        # You cannot add the past tense during a pause..
        if paused:
            duration = active_elapsed
        else:
            duration = (
                active_elapsed
                + time.monotonic()
                - active_started_at
            )

        duration = min(duration, SESSION_LIMIT)

        # try:
        #     save_session(
        #         started_at=started_at,
        #         ended_at=datetime.now(timezone.utc),
        #         duration_seconds=int(duration),
        #         score=game.score,
        #         lines=game.lines,
        #         level=game.level,
        #         end_reason=end_reason,
        #     )

        #     logger.info(
        #         "Session saved. Reason: %s, duration: %s seconds",
        #         end_reason,
        #         int(duration),
        #     )
        # except Exception:
        #     logger.exception("Failed to save the session")
        # finally:
        #     session_saved = True

    while True:
        # If the game is already lost, we end the session..
        # The completion screen remains accessible..
        # if game.game_over:
        #     if not score_saved:
        #         logger.info(
        #             "The game is over. Score: %s, lines: %s, level: %s",
        #             game.score,
        #             game.lines,
        #             game.level,
        #         )

        #         # try:
        #         #     save_score(game.score, game.lines, game.level)
        #         #     logger.info("The game result has been saved in PostgreSQL.")
        #         # except Exception:
        #         #     logger.exception("Failed to save the game result")
        #         # finally:
        #         #     score_saved = True

        #     finish_session("game_over")

        # The limit is checked only while the game is in progress.
        if not game.game_over:
            elapsed = (
                active_elapsed
                + time.monotonic()
                - active_started_at
            )

            if elapsed >= SESSION_LIMIT:
                logger.info("The session time limit has expired")
                finish_session("time_limit")
                return False

        draw(stdscr, game, False)

        key = stdscr.getch()

        # A re-check is necessary to avoid processing
        # game action after the limit has expired.
        if not game.game_over:
            elapsed = (
                active_elapsed
                + time.monotonic()
                - active_started_at
            )

            if elapsed >= SESSION_LIMIT:
                logger.info("The session time limit has expired")
                finish_session("time_limit")
                return False

        action = handle_system_input(key, game.game_over)

        if action == "quit":
            logger.info("The player has exited the game loop")
            finish_session("player_quit")
            return False

        if action == "restart":
            logger.info("The player chose to restart the game")
            finish_session("restart")
            return True

        if action == "pause" and not game.game_over:
            logger.info("The game is paused")

            # We record the active time before the pause.
            active_elapsed += time.monotonic() - active_started_at
            paused = True

            pause_action, save_id = pause_menu(
                stdscr, game, save_id
            )

            if pause_action == "quit":
                logger.info("Exiting the game via the pause menu")
                finish_session("player_quit")
                return False
            
            # We are resuming the count from the moment we come out of the pause.
            active_started_at = time.monotonic()
            last = time.monotonic()
            paused = False

            logger.info("The game continues")
            continue

        if game.game_over:
            continue

        reset_timer = handle_input(key, game)

        if reset_timer:
            last = time.monotonic()

        now = time.monotonic()

        if now - last >= game.delay:
            game.step()
            last = now
