import curses

from game.settings import W, H
from game.shapes import SHAPES, KINDS


COLORS = {
    "I": curses.COLOR_CYAN,
    "O": curses.COLOR_YELLOW,
    "T": curses.COLOR_MAGENTA,
    "S": curses.COLOR_GREEN,
    "Z": curses.COLOR_RED,
    "J": curses.COLOR_BLUE,
    "L": curses.COLOR_WHITE,
}
PAIR = {k: i + 1 for i, k in enumerate(KINDS)}

def draw_cell(win, y, x, kind, ghost=False):
    attr = curses.color_pair(PAIR[kind])
    try:
        if ghost:
            win.addstr(y, x, "░░", attr)
        else:
            win.addstr(y, x, "██", attr | curses.A_BOLD)
    except curses.error:
        pass

def draw(stdscr, g, paused):
    stdscr.erase()
    ox, oy = 2, 1  # field displacement

    # frame
    for r in range(H + 1):
        stdscr.addstr(oy + r, ox - 1, "|")
        stdscr.addstr(oy + r, ox + W * 2, "|")
    stdscr.addstr(oy + H, ox - 1, "+" + "-" * (W * 2) + "+")

    # fixed blocks
    for r in range(H):
        for c in range(W):
            if g.board[r][c]:
                draw_cell(stdscr, oy + r, ox + c * 2, g.board[r][c])

    if not g.game_over:
        # the “ghost” of the figure
        gy = g.ghost_y()
        for r, row in enumerate(g.shape):
            for c, cell in enumerate(row):
                if cell and gy + r >= 0:
                    draw_cell(stdscr, oy + gy + r, ox + (g.x + c) * 2, g.kind, ghost=True)
        # the current figure
        for r, row in enumerate(g.shape):
            for c, cell in enumerate(row):
                if cell and g.y + r >= 0:
                    draw_cell(stdscr, oy + g.y + r, ox + (g.x + c) * 2, g.kind)

    # side panel
    px = ox + W * 2 + 4
    stdscr.addstr(oy, px, "ТЕТРИС", curses.A_BOLD)
    stdscr.addstr(oy + 2, px, f"Счёт:    {g.score}")
    stdscr.addstr(oy + 3, px, f"Линии:   {g.lines}")
    stdscr.addstr(oy + 4, px, f"Уровень: {g.level}")
    stdscr.addstr(oy + 6, px, "Следующая:")
    for r, row in enumerate(SHAPES[g.next_kind]):
        for c, cell in enumerate(row):
            if cell:
                draw_cell(stdscr, oy + 7 + r, px + c * 2, g.next_kind)
    help_lines = ["← →  движение", "↑    поворот", "↓    быстрее", "Пробел сброс", "P    пауза", "Q    выход"]
    for i, line in enumerate(help_lines):
        stdscr.addstr(oy + 12 + i, px, line)

    if paused:
        stdscr.addstr(oy + H // 2, ox + 4, " ПАУЗА ", curses.A_REVERSE)
    if g.game_over:
        stdscr.addstr(oy + H // 2 - 1, ox + 2, " GAME OVER ", curses.A_REVERSE)
        stdscr.addstr(oy + H // 2 + 1, ox + 1, " R - заново, Q - выход ")
    stdscr.refresh()

