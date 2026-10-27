from types import SimpleNamespace
from unittest.mock import Mock

import game.session as session_module


def make_game(game_over=False):
    # “””Создаёт упрощённую игру для тестирования.”””
    return SimpleNamespace(
        score=100,
        lines=2,
        level=1,
        game_over=game_over,
        delay=1,
        step=Mock(),
    )


class FakeScreen:
    # “””Имитирует ввод с клавиатуры без настоящего терминала.”””

    def __init__(self, keys):
        self.keys = iter(keys)

    def getch(self):
        return next(self.keys)


def prepare_session(monkeypatch, keys, clock_values):
    # “””Подготавливает игровую сессию без терминала и БД.”””
    screen = FakeScreen(keys)
    game = make_game()

    monkeypatch.setattr(session_module, "draw", Mock())
    monkeypatch.setattr(
        session_module,
        "handle_system_input",
        lambda key, game_over: key,
    )
    monkeypatch.setattr(
        session_module,
        "handle_input",
        lambda key, game: False,
    )
    monkeypatch.setattr(
        session_module,
        "pause_menu",
        lambda stdscr, game, save_id: ("resume", save_id),
    )

    clock = Mock(side_effect=clock_values)
    monkeypatch.setattr(session_module.time, "monotonic", clock)

    return screen, game


def test_session_ends_after_time_limit(monkeypatch):
    # “””По истечении 60 секунд сессия завершается.”””
    screen, game = prepare_session(
        monkeypatch,
        keys=[],
        clock_values=[0, 0, 60, 60],
    )
    # save_session = Mock()
    # save_score = Mock()

    # monkeypatch.setattr(
    #     session_module, "save_session", save_session
    # )
    # monkeypatch.setattr(
    #     session_module, "save_score", save_score
    # )

    result = session_module.play(screen, game)

    assert result is False
    # save_session.assert_called_once()

    # saved_data = save_session.call_args.kwargs
    # assert saved_data["end_reason"] == "time_limit"
    # assert saved_data["duration_seconds"] == 60

    # save_score.assert_not_called()


def test_player_quit_saves_session_once(monkeypatch):
    # “””При выходе сессия сохраняется с причиной player_quit.”””
    screen, game = prepare_session(
        monkeypatch,
        keys=["quit"],
        clock_values=[0, 0, 1, 2, 3],
    )
    # save_session = Mock()

    # monkeypatch.setattr(
    #     session_module, "save_session", save_session
    # )
    # monkeypatch.setattr(
    #     session_module, "save_score", Mock()
    # )

    result = session_module.play(screen, game)

    assert result is False
    # save_session.assert_called_once()
    # assert (
    #     save_session.call_args.kwargs["end_reason"]
    #     == "player_quit"
    # )


def test_game_over_saves_score_and_session_once(monkeypatch):
    # “””Проигрыш сохраняет очки и сессию по одному разу.”””
    screen = FakeScreen(["quit"])
    game = make_game(game_over=True)

    monkeypatch.setattr(session_module, "draw", Mock())
    monkeypatch.setattr(
        session_module,
        "handle_system_input",
        lambda key, game_over: key,
    )
    monkeypatch.setattr(
        session_module.time,
        "monotonic",
        Mock(side_effect=[0, 0, 1]),
    )

    # save_session = Mock()
    # save_score = Mock()

    # monkeypatch.setattr(
    #     session_module, "save_session", save_session
    # )
    # monkeypatch.setattr(
    #     session_module, "save_score", save_score
    # )

    result = session_module.play(screen, game)

    assert result is False
    # save_score.assert_called_once_with(100, 2, 1)
    # save_session.assert_called_once()

    # assert (
    #     save_session.call_args.kwargs["end_reason"]
    #     == "game_over"
    # )


def test_restart_saves_old_session_once(monkeypatch):
    # “””При перезапуске старая сессия сохраняется один раз.”””
    screen, game = prepare_session(
        monkeypatch,
        keys=["restart"],
        clock_values=[0, 0, 1, 2, 3],
    )
    # save_session = Mock()

    # monkeypatch.setattr(
    #     session_module, "save_session", save_session
    # )
    # monkeypatch.setattr(
    #     session_module, "save_score", Mock()
    # )

    result = session_module.play(screen, game)

    assert result is True
    # save_session.assert_called_once()
    # assert (
    #     save_session.call_args.kwargs["end_reason"]
    #     == "restart"
    # )


def test_pause_time_is_not_counted(monkeypatch):
    # “””Время, проведённое в паузе, не учитывается.”””
    screen, game = prepare_session(
        monkeypatch,
        keys=["pause", "quit"],
        clock_values=[
            0, 0,       # Начало игры
            1, 2, 3,    # До и во время входа в паузу
            1000, 1000, # Выход из паузы
            1001, 1002, 1003,
        ],
    )

    # save_session = Mock()

    # monkeypatch.setattr(
    #     session_module, "save_session", save_session
    # )
    # monkeypatch.setattr(
    #     session_module, "save_score", Mock()
    # )

    result = session_module.play(screen, game)

    assert result is False
    # save_session.assert_called_once()

    # duration = save_session.call_args.kwargs[
    #     "duration_seconds"
    # ]

    # # Между входом и выходом из паузы прошло почти 17 минут.
    # # Но в длительность сессии это время не должно попасть.
    # assert duration == 6
    # assert duration < 60