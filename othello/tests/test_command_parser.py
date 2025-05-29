import pytest

from othello.command_parser import (
    CommandKind,
    CommandParser,
    CommandParserException,
    PlayCommand,
)


def test_help():
    cp = CommandParser(8)
    assert cp.parse_str("?") == (CommandKind.HELP,)


def test_rules():
    cp = CommandParser(8)
    assert cp.parse_str("r") == (CommandKind.RULES,)


def test_save():
    cp = CommandParser(8)
    assert cp.parse_str("s") == (CommandKind.SAVE_AND_QUIT,)


def test_save_hist():
    cp = CommandParser(8)
    assert cp.parse_str("sh") == (CommandKind.SAVE_HISTORY,)


def test_forfeit():
    cp = CommandParser(8)
    assert cp.parse_str("ff") == (CommandKind.FORFEIT,)


def test_restart():
    cp = CommandParser(8)
    assert cp.parse_str("restart") == (CommandKind.RESTART,)


def test_legal_plays():
    cp = CommandParser(8)
    assert cp.parse_str("b3") == (CommandKind.PLAY_MOVE, PlayCommand(1, 2))
    assert cp.parse_str("a4") == (CommandKind.PLAY_MOVE, PlayCommand(0, 3))
    assert cp.parse_str("a1") == (CommandKind.PLAY_MOVE, PlayCommand(0, 0))
    assert cp.parse_str("h8") == (CommandKind.PLAY_MOVE, PlayCommand(7, 7))


def test_illegal_plays():
    cp = CommandParser(6)
    with pytest.raises(CommandParserException):
        cp.parse_str("h8")
        cp.parse_str("a9")
        cp.parse_str("a0")


def test_illegal_data():
    cp = CommandParser(6)
    with pytest.raises(CommandParserException):
        cp.parse_str("aaaaaaaaaaaa")


def test_print_help(capsys):
    cp = CommandParser(8)
    cp.print_help()
    captured = capsys.readouterr()
    assert "Othello Game Help" in captured.out
    assert "=================" in captured.out
    assert "Coordinate format: [column][row] (e.g., a1, b2)" in captured.out
    assert "Othello Game Commands" in captured.out
    assert "restart - Restart the game" in captured.out
    assert "ff" in captured.out and "Forfeit" in captured.out
    assert "?" in captured.out
    assert "r" in captured.out
    assert "q" in captured.out
    assert "s" in captured.out
    assert "sh" in captured.out


def test_print_rules(capsys, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda: "")
    cp = CommandParser(8)
    CommandParser.print_rules()
    captured = capsys.readouterr()
    assert "Othello/Reversi Rules" in captured.out
    assert "====================" in captured.out
    assert "Objective:" in captured.out
    assert "The goal is to have the majority of your color discs" in captured.out
    assert "Setup:" in captured.out
    assert "The game is played on an 8×8 board" in captured.out
    assert "Black moves first" in captured.out
    assert "Gameplay:" in captured.out
    assert (
        "A move consists of placing a disc of your color on an empty square"
        in captured.out
    )
    assert "To outflank means to place a disc" in captured.out
    assert (
        "All of the opponent's discs that are outflanked are flipped to your color"
        in captured.out
    )
    assert "Winning:" in captured.out
    assert "The player with the most discs of their color on the" in captured.out
    assert (
        "If both players have the same number of discs, the game is a draw."
        in captured.out
    )
    assert "Press Enter to continue playing..." in captured.out
