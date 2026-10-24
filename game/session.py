import time

from app_logger import setup_logger
from game.engine import Game
from ui.render import draw
from ui.input_handler import handle_input, handle_system_input
from ui.menus import pause_menu
from services.score_repository import save_score


logger = setup_logger(__name__)

def play(stdscr, game=None, save_id = None):
    if game is None:
        game = Game()
    
    last = time.monotonic()
    score_saved = False
    
    logger.info("Game loop started")    
    
    while True:
        draw(stdscr, game, False)
        
        if game.game_over and not score_saved:
            logger.info(
                "The game is over. Score: %s, lines: %s, level: %s",
                game.score,
                game.lines,
                game.level,
            )
            
            try:
                save_score(game.score, game.lines, game.level)
                logger.info("The game result has been saved in PostgreSQL.")
            except Exception:
                logger.exception("Failed to save the game result")
            finally:
                score_saved = True
        
        key = stdscr.getch()    
        
        action = handle_system_input(key, game.game_over)

        if action == "quit":
            logger.info("The player has exited the game loop")
            return False

        if action == "restart":
            logger.info("The player chose to restart the game")
            return True

        if action == "pause":
            logger.info("The game is paused")
            
            pause_action, save_id = pause_menu(
                stdscr, game, save_id
            )
        
            if pause_action == "quit":
                logger.info("Exiting the game via the pause menu")
                return False
            
            logger.info("The game continues")
            
            last = time.monotonic()
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
        