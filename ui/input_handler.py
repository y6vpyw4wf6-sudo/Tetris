import curses


def handle_input(key, game):
    
    if key == curses.KEY_LEFT:
        game.move(-1)
        
    elif key == curses.KEY_RIGHT:
        game.move(1)
        
    elif key in (curses.KEY_UP, ord("x"), ord("X")):
        game.rotate()
        
    elif key == curses.KEY_DOWN:
        if not game.step():
            game.score += 1
        return True
    elif key == ord(" "):
        game.hard_drop()
        return True
    
    return False

def handle_system_input(key, game_over):
    if key in (ord("q"), ord("Q")):
        return "quit"
    
    if game_over:
        if key in (ord("r"), ord("R")):
            return "restart"
        return None
    
    if key in (ord("p"), ord("P")):
        return "pause"
    
    return None