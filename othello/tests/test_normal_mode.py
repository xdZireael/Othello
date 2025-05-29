import pytest
from unittest.mock import MagicMock, patch
from othello.controllers import GameController
from othello.othello_board import BoardSize, Color, Bitboard, OthelloBoard
from othello.command_parser import CommandKind, CommandParserException
from othello.cli import OthelloCLI


@pytest.fixture
def normal_game():
    """Fixture to create a NormalGame instance with mocked board."""
    controller_mock = MagicMock(spec=GameController)
    game = OthelloCLI(controller=controller_mock)
    game.controller = MagicMock()
    game.controller.black = MagicMock()
    game.controller.white = MagicMock()
    game.controller.size = BoardSize.EIGHT_BY_EIGHT
    game.controller.get_current_player.return_value = Color.BLACK
    return game


def test_check_game_over_when_board_says_game_over(normal_game):
    """Test that check_game_over returns True when board.is_game_over is True."""
    normal_game.controller._board.is_game_over.return_value = True
    normal_game.controller.popcount.return_value = 0

    result = normal_game.check_game_over(MagicMock())

    assert result is True


def test_check_game_over_prints_correct_winner(normal_game, capsys):
    """Test that correct winner is printed when game is over."""

    def popcount_side_effect(*args, **kwargs):
        if args == (Color.BLACK,):  # If called with argument 1
            return 40
        elif args == (Color.WHITE,):  # If called with argument 2
            return 24
        else:
            return 0

    normal_game.controller.is_game_over = True
    normal_game.controller.game_over_message = "Black wins!"
    normal_game.controller.popcount.side_effect = popcount_side_effect
    normal_game.check_game_over(MagicMock())
    captured = capsys.readouterr()

    print(captured.out)
    assert "Black wins!" in captured.out
    assert "Final score - Black: 40, White: 24" in captured.out


def test_check_game_over_prints_tie(normal_game, capsys):
    """Test that tie is printed when scores are equal."""
    normal_game.controller.is_game_over.return_value = True
    normal_game.controller.popcount.return_value = 32
    normal_game.controller.popcount.return_value = 32
    normal_game.controller.game_over_message = "The game is a tie!"

    normal_game.check_game_over(MagicMock())
    captured = capsys.readouterr()

    assert "The game is a tie!" in captured.out
    assert "Final score - Black: 32, White: 32" in captured.out


def test_check_game_over_skips_turn_when_no_moves(normal_game, capsys):
    """Test that turn is skipped when current player has no moves but game isn't over."""
    normal_game.controller.is_game_over = False
    possible_moves = MagicMock()
    possible_moves.bits = 0

    result = normal_game.check_game_over(possible_moves)
    captured = capsys.readouterr()

    assert result is False
    assert "No valid moves for" in captured.out
    assert "Skipping turn" in captured.out


def test_check_game_over_continues_when_moves_exist(normal_game):
    """Test that game continues when moves exist."""
    normal_game.controller.is_game_over = False
    possible_moves = MagicMock()
    possible_moves.bits = 1

    result = normal_game.check_game_over(possible_moves)

    assert result is False


def test_check_game_over_white_more_popcount(normal_game):
    """Test that check_game_over returns True when white has more pieces."""
    normal_game.controller.is_game_over.return_value = True
    normal_game.controller.popcount.return_value = 40

    result = normal_game.check_game_over(MagicMock())

    assert result is True


def test_get_player_move(normal_game, capsys):
    """Test that player input is parsed correctly."""
    with patch("builtins.input", return_value="e4"):
        result = OthelloCLI.get_player_move()
        captured = capsys.readouterr()

    assert result == (4, 3)


def test_process_valid_move(normal_game):
    """Test that valid moves are processed correctly."""
    possible_moves = MagicMock()
    possible_moves.get.return_value = True
    normal_game.controller.play = MagicMock()

    result = normal_game.process_move(3, 2, possible_moves)

    assert result is True
    normal_game.controller.play.assert_called_once_with(3, 2)


def test_process_invalid_move(normal_game, capsys):
    """Test that invalid moves are rejected."""
    possible_moves = MagicMock()
    possible_moves.get.return_value = False

    result = normal_game.process_move(1, 1, possible_moves)
    captured = capsys.readouterr()

    assert result is False
    assert "Invalid move" in captured.out


def test_display_possible_moves(normal_game, capsys):
    """Test that possible moves are displayed correctly."""
    possible_moves = MagicMock()
    possible_moves.get.side_effect = lambda x, y: (x, y) in [(2, 3), (4, 5)]

    normal_game.display_possible_moves(possible_moves)
    captured = capsys.readouterr()

    assert "Possible moves:" in captured.out
    assert "c4" in captured.out
    assert "e6" in captured.out


def test_check_parser_input(normal_game):
    # Create the mock game instance
    mock_controller = MagicMock(spec=GameController)
    mock_controller.size = BoardSize.EIGHT_BY_EIGHT
    normal_game = OthelloCLI(mock_controller)
    normal_game.parser = MagicMock()
    normal_game.running = True
    normal_game.process_move = MagicMock()

    # Test PLAY_MOVE with valid move
    play_command = MagicMock()
    play_command.x_coord = 3
    play_command.y_coord = 4
    mock_controller.get_possible_moves.return_value = [(3, 4)]
    normal_game.process_move.return_value = True

    normal_game.check_parser_input("e4", CommandKind.PLAY_MOVE, play_command)
    normal_game.process_move.assert_called_with(
        3, 4, mock_controller.get_possible_moves.return_value
    )

    # Test PLAY_MOVE with invalid move
    normal_game.process_move.reset_mock()
    normal_game.process_move.return_value = False
    with patch("builtins.print") as mock_print:
        normal_game.check_parser_input("e4", CommandKind.PLAY_MOVE, play_command)
        mock_print.assert_called_with("Invalid move. Try again.")

    # Test HELP command
    normal_game.check_parser_input("help", CommandKind.HELP)
    normal_game.parser.print_help.assert_called_once()

    # Test RULES command
    normal_game.parser.print_rules = MagicMock()

    # Test SAVE_AND_QUIT command
    with patch(
        "othello.cli.save_board_state_history"
    ) as mock_save:  # Adjust import path as needed
        normal_game.check_parser_input("save", CommandKind.SAVE_AND_QUIT)
        mock_save.assert_called_with(mock_controller)
        assert normal_game.running is False

    # Reset running state for subsequent tests
    normal_game.running = True

    # Test SAVE_HISTORY command
    with patch(
        "othello.cli.save_board_state_history"
    ) as mock_save:  # Adjust import path as needed
        normal_game.check_parser_input("history", CommandKind.SAVE_HISTORY)
        mock_save.assert_called_with(mock_controller, only_hist=True)

    # Test FORFEIT command
    mock_player = MagicMock()
    mock_player.name = "BLACK"
    mock_opponent = MagicMock()
    mock_opponent.name = "WHITE"
    mock_controller.get_current_player.return_value = mock_player
    mock_player.__invert__.return_value = mock_opponent

    with patch("builtins.print") as mock_print:
        normal_game.check_parser_input("forfeit", CommandKind.FORFEIT)
        mock_print.assert_any_call("BLACK forfeited.")
        mock_print.assert_any_call("Game Over, WHITE wins!")
        assert normal_game.running is False

    # Reset running state for subsequent tests
    normal_game.running = True

    # Test RESTART command
    with patch("othello.cli.OthelloCLI.play") as mock_play:
        normal_game.check_parser_input("restart", CommandKind.RESTART)
        mock_controller.restart.assert_called_once()

    # Test QUIT command
    with patch("builtins.print") as mock_print:
        normal_game.check_parser_input("quit", CommandKind.QUIT)
        mock_print.assert_called_with("Exiting without saving...")
        assert normal_game.running is False

    # Reset running state for subsequent tests
    normal_game.running = True

    # Test invalid command
    with patch("builtins.print") as mock_print:
        normal_game.check_parser_input(
            "invalid", MagicMock()
        )  # Use a MagicMock that won't match any case
        mock_print.assert_called_with("Invalid command. Try again.")
        normal_game.parser.print_help.assert_called()


def test_play(normal_game):
    # Set up additional mocks needed for play function
    normal_game.parser = MagicMock()
    normal_game.display_history = MagicMock()
    normal_game.display_board = MagicMock()
    normal_game.display_possible_moves = MagicMock()
    normal_game.check_game_over = MagicMock()
    normal_game.check_parser_input = MagicMock()

    # Configure controller mock (may already be set up in fixture)
    normal_game.controller.get_turn_number.return_value = 1
    normal_game.controller.get_possible_moves.return_value = [(3, 4)]

    # Configure check_game_over to break the loop
    # First call returns False (continue loop), second returns True (exit loop)
    normal_game.check_game_over.side_effect = [False, True]

    # Set up command parsing
    command_mock = MagicMock()
    normal_game.parser.parse_str.return_value = (CommandKind.PLAY_MOVE, command_mock)

    # Mock input function
    with patch("builtins.input", return_value="e4"):
        # Run the play method
        normal_game.play()

    # Verify the expected methods were called
    assert normal_game.display_history.called
    assert normal_game.display_board.called
    assert normal_game.display_possible_moves.called
    assert normal_game.controller.next_move.called
    assert normal_game.check_game_over.call_count == 2
