import pytest
import sys

from othello.parser import (
    GameMode,
    AIColor,
    AIMode,
    AIHeuristic,
    parse_args,
    default_config,
)


# TEST DEFAULT CONFIGURATION


def test_default_config(monkeypatch):
    """
    Test the default configuration of the parser.

    When the parser is called without arguments, it should return the default
    configuration.
    """
    monkeypatch.setattr(sys, "argv", ["othello"])
    mode, parse_config = parse_args()

    assert mode == GameMode.NORMAL.value
    assert parse_config == default_config


# TEST REGULAR OPTIONS


# file
def test_file(monkeypatch):
    """
    Test parsing of a game file.

    This test ensures that when a filename is provided as an argument,
    the parser correctly identifies the filename. It also checks that
    invalid combinations of arguments result in a SystemExit exception.
    """

    monkeypatch.setattr(sys, "argv", ["othello", "dummyGame.txt"])
    mode, parse_config = parse_args()
    assert parse_config["filename"] == "dummyGame.txt"

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "dummyGame.txt", "-a", "s"])
        _, parse_config = parse_args()


# help


def test_help(monkeypatch):
    """
    Test the help option.

    This test ensures that when the -h option is provided, the parser
    raises a SystemExit exception.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-h"])
        parse_args()


# version


def test_version(monkeypatch):
    """
    Test the version option.

    This test ensures that when the -v option is provided, the parser
    raises a SystemExit exception.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-v"])
        parse_args()


# debug


def test_debug(monkeypatch):
    """
    Test the debug option.

    This test ensures that when the -d option is provided, the parser
    correctly sets the debug flag to True in the configuration.
    """

    monkeypatch.setattr(sys, "argv", ["othello", "-d"])
    mode, parse_config = parse_args()

    assert parse_config["debug"] is True


# size


def test_size(monkeypatch):
    """
    Test the size option.

    This test ensures that when the -s option is provided with a valid size,
    the parser correctly sets the size in the configuration.
    """

    monkeypatch.setattr(sys, "argv", ["othello"])
    mode, parse_config = parse_args()

    assert parse_config["size"] == 8

    monkeypatch.setattr(sys, "argv", ["othello", "-s", "6"])
    mode, parse_config = parse_args()

    assert parse_config["size"] == 6

    monkeypatch.setattr(sys, "argv", ["othello", "-s", "8"])
    mode, parse_config = parse_args()

    assert parse_config["size"] == 8

    monkeypatch.setattr(sys, "argv", ["othello", "-s", "10"])
    mode, parse_config = parse_args()

    assert parse_config["size"] == 10

    monkeypatch.setattr(sys, "argv", ["othello", "-s", "12"])
    mode, parse_config = parse_args()

    assert parse_config["size"] == 12


# TEST MODES


# blitz mode
def test_blitz_mode(monkeypatch):
    """
    Test the blitz mode option.

    This test ensures that when the -b option is provided, the parser
    correctly sets the game mode to Blitz and sets the time limit to 30
    seconds. Also, when the -t option is provided after -b, the parser
    correctly sets the time limit to the specified value.
    """
    monkeypatch.setattr(sys, "argv", ["othello", "-b"])
    mode, parse_config = parse_args()

    assert mode == GameMode.BLITZ.value
    assert parse_config["mode"] == GameMode.BLITZ.value
    assert parse_config["blitz_time"] == 30

    monkeypatch.setattr(sys, "argv", ["othello", "-b", "-t", "60"])
    mode, parse_config = parse_args()

    assert mode == GameMode.BLITZ.value
    assert parse_config["mode"] == GameMode.BLITZ.value
    assert parse_config["blitz_time"] == 60


# contest


def test_contest_mode(monkeypatch):
    """
    Test the contest mode option.

    This test ensures that when the -c option is provided with a valid filename,
    the parser correctly sets the game mode to Contest and sets the filename
    in the configuration.
    """
    monkeypatch.setattr(sys, "argv", ["othello", "-c", "dummy_game.txt"])
    mode, parse_config = parse_args()

    assert mode == GameMode.CONTEST.value
    assert parse_config["mode"] == GameMode.CONTEST.value
    assert parse_config["filename"] == "dummy_game.txt"


# ai


def test_ai_mode(monkeypatch):
    """
    Test the AI mode option.

    This test ensures that when the -a option is provided with a valid color,
    the parser correctly sets the game mode to AI and sets the color in the
    configuration.
    """
    # ai default settings
    monkeypatch.setattr(sys, "argv", ["othello", "-a"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_color"] == AIColor.BLACK.value
    assert parse_config["ai_mode"] == AIMode.MINIMAX.value
    assert parse_config["ai_shallow"] is False
    assert parse_config["ai_depth"] == 3
    assert parse_config["ai_heuristic"] == AIHeuristic.CORNERS_CAPTURED.value
    assert parse_config["ai_time"] == 5

    # ai color
    monkeypatch.setattr(sys, "argv", ["othello", "-aO"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_color"] == AIColor.WHITE.value

    monkeypatch.setattr(sys, "argv", ["othello", "-aA"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_color"] == AIColor.ALL.value

    monkeypatch.setattr(sys, "argv", ["othello", "--ai", "A"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_color"] == AIColor.ALL.value

    # ai mode
    monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-mode", "minimax"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_mode"] == AIMode.MINIMAX.value

    monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-mode", "ab"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_mode"] == AIMode.ALPHABETA.value

    # ai shallow
    monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-shallow"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_shallow"] is True

    # ai depth
    monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-depth", "5"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_depth"] == 5

    # ai heuristic
    monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-heuristic", "coin_parity"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_heuristic"] == AIHeuristic.COIN_PARITY.value

    # ai time
    monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-time", "25"])
    mode, parse_config = parse_args()

    assert mode == GameMode.AI.value
    assert parse_config["mode"] == GameMode.AI.value
    assert parse_config["ai_time"] == 25


# TEST ERRORS


# incorrect option
def test_err_option(monkeypatch):
    """
    Test the error handling of the parser for invalid options.

    This test ensures that when an invalid option is provided, the parser raises
    a SystemExit exception with a non-zero exit status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "--invalid"])
        parse_args()


# mode incompatibility
def test_err_incomp_modes(monkeypatch):
    """
    Test the error handling of the parser for incompatible game modes.

    This test ensures that when game modes are provided that cannot be used
    together, the parser raises a SystemExit exception with a non-zero exit
    status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-b", "-c", "dummyGame.txt"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-c", "dummyGame.txt", "-ai"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-a", "-b"])
        parse_args()


# incorrect size
def test_err_size(monkeypatch):
    """
    Test the error handling of the parser for invalid board sizes.

    This test ensures that when the user provides a board size that is not
    supported, the parser raises a SystemExit exception with a non-zero exit
    status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-s", "3"])
        parse_args()


# incorrect blitz time
def test_err_time(monkeypatch):  # trouver le moyen de faire plusieurs tests
    """
    Test the error handling of the parser for invalid blitz time values.

    This test ensures that when a negative or zero time value is provided, the parser
    raises a SystemExit exception with a non-zero exit status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-b", "-t", "-20"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-t", "20"])
        parse_args()


# incorrect contest file


def test_err_contest(monkeypatch):
    """
    Test the error handling of the parser for invalid contest mode arguments.

    This test ensures that when the contest mode is specified without a
    filename, the parser raises a SystemExit exception with a non-zero exit
    status.
    """

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-c"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-c", ""])
        parse_args()


# incorrect ai color


def test_err_AI_color(monkeypatch):
    """
    Test the error handling of the parser for invalid AI color arguments.

    This test ensures that when an invalid AI color is provided, the parser
    raises a SystemExit exception with a non-zero exit status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-aF"])
        parse_args()


# incorrect ai argument


def test_err_AI_arg(monkeypatch):
    """
    Test the error handling of the parser for invalid AI arguments.

    This test ensures that when an invalid AI argument is provided, the parser
    raises a SystemExit exception with a non-zero exit status.
    """

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-a[invalid]"])
        parse_args()


# incorrect ai depth


def test_err_AI_depth(monkeypatch):
    """
    Test the error handling of the parser for invalid AI depth arguments.

    This test ensures that when an invalid AI depth is provided, the parser
    raises a SystemExit exception with a non-zero exit status.
    """

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-depth", "0"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-depth", "-1"])
        parse_args()


# incorrect ai time limit


def test_err_AI_time(monkeypatch):
    """
    Test the error handling of the parser for invalid AI time limit arguments.

    This test ensures that when an invalid AI time limit is provided, the parser
    raises a SystemExit exception with a non-zero exit status.
    """

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-time", "0"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, "argv", ["othello", "-a", "--ai-time", "-1"])
        parse_args()
