import random

from game.settings import W, H, LINE_SCORE
from game.shapes import SHAPES, KINDS, rotate
from app_logger import setup_logger


logger = setup_logger(__name__)


class Game:
    def __init__(self):
        self.rng = random.Random()
        self.board = [[None] * W for _ in range(H)]
        self.bag = []
        self.score = 0
        self.lines = 0
        self.game_over = False
        self.next_kind = self._draw_kind()
        self._spawn()
        
        logger.info("A new game has started")

    def _draw_kind(self):
        # “7-bag”: each figure appears once per cycle.
        if not self.bag:
            self.bag = KINDS[:]
            self.rng.shuffle(self.bag)
        return self.bag.pop()

    def _spawn(self):
        self.kind = self.next_kind
        self.next_kind = self._draw_kind()
        self.shape = [row[:] for row in SHAPES[self.kind]]
        self.x = (W - len(self.shape[0])) // 2
        self.y = 0
        if self._collides(self.shape, self.x, self.y):
            self.game_over = True
            logger.info("The game is over. Score: %s", self.score)

    @property
    def level(self):
        return self.lines // 10 + 1

    @property
    def delay(self):
        return max(0.08, 0.5 - (self.level - 1) * 0.04)

    def _collides(self, shape, x, y):
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if not cell:
                    continue
                nx, ny = x + c, y + r
                if nx < 0 or nx >= W or ny >= H:
                    return True
                if ny >= 0 and self.board[ny][nx]:
                    return True
        return False

    def move(self, dx):
        if not self._collides(self.shape, self.x + dx, self.y):
            self.x += dx

    def rotate(self):
        new = rotate(self.shape)
        # Simple “wall kicks”: we try shifting by 0, -1, +1, -2, +2.
        for dx in (0, -1, 1, -2, 2):
            if not self._collides(new, self.x + dx, self.y):
                self.shape, self.x = new, self.x + dx
                return

    def step(self):
        """Shift down by 1. Returns True if the figure has been fixed."""
        if not self._collides(self.shape, self.x, self.y + 1):
            self.y += 1
            return False
        self._lock()
        return True

    def hard_drop(self):
        while not self._collides(self.shape, self.x, self.y + 1):
            self.y += 1
            self.score += 2
        self._lock()

    def _lock(self):
        for r, row in enumerate(self.shape):
            for c, cell in enumerate(row):
                if cell and 0 <= self.y + r < H:
                    self.board[self.y + r][self.x + c] = self.kind
        full = [i for i, row in enumerate(self.board) if all(row)]
        for i in full:
            del self.board[i]
            self.board.insert(0, [None] * W)
        self.lines += len(full)
        self.score += LINE_SCORE[len(full)] * self.level
        self._spawn()

    def ghost_y(self):
        y = self.y
        while not self._collides(self.shape, self.x, y + 1):
            y += 1
        return y
    
    
    def get_state(self): 
        """Returns the complete game state as a dictionary.""" 
        return { 
                "version": 1, 
                "board": [row[:] for row in self.board], 
                "bag": self.bag[:], 
                "score": self.score, 
                "lines": self.lines, 
                "game_over": self.game_over, 
                "kind": self.kind, 
                "shape": [row[:] for row in self.shape], 
                "x": self.x, 
                "y": self.y, 
                "next_kind": self.next_kind, 
                "random_state": self._to_lists(self.rng.getstate()), 
                }
    
    @staticmethod 
    def _to_lists(value): 
        """Converts nested tuples into lists.""" 
        if isinstance(value, (tuple, list)): 
            return [Game._to_lists(item) for item in value]
        return value
    
    @staticmethod 
    def _to_tuples(value): 
        """Converts nested lists back into tuples.""" 
        if isinstance(value, (tuple, list)): 
            return tuple(Game._to_tuples(item) for item in value)
    
        return value
    
    @classmethod 
    def load_state(cls, state): 
        """Creates a game from a previously saved state."""
        if not isinstance(state, dict):
            raise ValueError("Состояние игры должно быть словарём")

        if state.get("version") != 1:
            raise ValueError("Неизвестная версия сохранения")

        required = {
            "board", "bag", "score", "lines", "game_over",
            "kind", "shape", "x", "y", "next_kind", "random_state"
        }

        if not required.issubset(state):
            raise ValueError("В сохранении отсутствуют обязательные данные")

        board = state["board"]

        if (
            not isinstance(board, list)
            or len(board) != H
            or any(not isinstance(row, list) or len(row) != W for row in board)
        ):
            raise ValueError("Некорректный размер игрового поля")

        if any(
            cell is not None and cell not in KINDS
            for row in board
            for cell in row
        ):
            raise ValueError("Игровое поле содержит неизвестные блоки")

        if state["kind"] not in KINDS or state["next_kind"] not in KINDS:
            raise ValueError("Неизвестный тип фигуры")

        if (
            not isinstance(state["bag"], list)
            or any(kind not in KINDS for kind in state["bag"])
        ):
            raise ValueError("Некорректная очередь фигур")

        if (
            not isinstance(state["shape"], list)
            or not state["shape"]
            or any(not isinstance(row, list) or not row for row in state["shape"])
            or any(cell not in (0, 1) for row in state["shape"] for cell in row)
        ):
            raise ValueError("Некорректная форма фигуры")

        if (
            type(state["score"]) is not int
            or state["score"] < 0
            or type(state["lines"]) is not int
            or state["lines"] < 0
        ):
            raise ValueError("Некорректный счёт или количество линий")

        if type(state["game_over"]) is not bool:
            raise ValueError("Некорректное состояние игры")

        if type(state["x"]) is not int or type(state["y"]) is not int:
            raise ValueError("Некорректные координаты фигуры")

        # We create an object without launching a new batch.
        game = cls.__new__(cls)

        game.board = [row[:] for row in board]
        game.bag = state["bag"][:]
        game.score = state["score"]
        game.lines = state["lines"]
        game.game_over = state["game_over"]
        game.kind = state["kind"]
        game.shape = [row[:] for row in state["shape"]]
        game.x = state["x"]
        game.y = state["y"]
        game.next_kind = state["next_kind"]

        # We are restoring the random number generator.
        game.rng = random.Random()
        game.rng.setstate(cls._to_tuples(state["random_state"]))

        return game

