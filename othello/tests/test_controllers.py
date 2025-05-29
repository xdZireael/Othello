import pytest
from othello.bitboard import Bitboard
from othello.controllers import (
    AIPlayer,
    GameController,
    HumanPlayer,
    Player,
    RandomPlayer,
)

from unittest.mock import MagicMock, patch

from othello.othello_board import BoardSize, Color, OthelloBoard


def test_player_init():
    p = HumanPlayer()
    assert p.controller is None
    assert p.color is None

    controller_mock = MagicMock()
    p.attach(controller_mock)
    p.set_color(Color.BLACK)

    assert p.controller == controller_mock
    assert p.color is Color.BLACK


def test_human_next_move():
    p = HumanPlayer()
    assert p.controller is None
    assert p.color is None
    controller_mock = MagicMock()
    p.attach(controller_mock)
    p.set_color(Color.BLACK)
    controller_mock.human_play_callback = None
    p.next_move()
    controller_mock.human_play_callback = MagicMock()
    p.next_move()
    controller_mock.human_play_callback.assert_called_once()


def test_random_player_next_move():
    p = RandomPlayer()
    assert p.controller is None
    assert p.color is None
    controller_mock = MagicMock()
    p.attach(controller_mock)
    p.set_color(Color.BLACK)
    possible_moves_mock = MagicMock()
    possible_moves_mock.hot_bits_coordinates.return_value = [(3, 4), (5, 6)]
    controller_mock.get_possible_moves.return_value = possible_moves_mock
    p.next_move()
    controller_mock.get_possible_moves.assert_called_once_with(Color.BLACK)
    controller_mock.play.assert_called_once()
    play_args = controller_mock.play.call_args[0]
    assert play_args in [(3, 4), (5, 6)]
    p.next_move()


def test_ai_player_next_move():
    board_mock = MagicMock(spec=OthelloBoard)
    p = AIPlayer(
        board=board_mock, depth=3, algorithm="minimax", heuristic="coin_parity"
    )
    assert p.board == board_mock
    assert p.depth == 3
    assert p.algorithm == "minimax"
    assert p.heuristic == "coin_parity"
    controller_mock = MagicMock()
    p.attach(controller_mock)
    p.set_color(Color.BLACK)
    with patch("othello.controllers.find_best_move") as mock_find_best_move:
        mock_find_best_move.return_value = (4, 5)
        p.next_move()
        mock_find_best_move.assert_called_once_with(
            board_mock, 3, Color.BLACK, "minimax", "coin_parity"
        )
        controller_mock.play.assert_called_once_with(4, 5)
    p = AIPlayer(board=board_mock, depth=5, algorithm="alphabeta", heuristic="mobility")
    p.attach(controller_mock)
    p.set_color(Color.WHITE)


def test_game_controller_init():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    assert controller._board == board_mock
    assert controller.size == board_mock.size
    assert controller.first_player_human
    assert controller.post_play_callback is None
    assert not controller.is_blitz()
    assert controller.human_play_callback is None
    black_player_mock.attach.assert_called_once_with(controller)
    black_player_mock.set_color.assert_called_once_with(Color.BLACK)
    white_player_mock.attach.assert_called_once_with(controller)
    white_player_mock.set_color.assert_called_once_with(Color.WHITE)
    assert controller.players[Color.BLACK] == black_player_mock
    assert controller.players[Color.WHITE] == white_player_mock


def test_game_controller_init_with_blitz():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    controller = GameController(
        board_mock, black_player_mock, white_player_mock, blitz_mode=True, time_limit=60
    )
    assert controller.is_blitz
    assert controller.time_limit == 60


def test_next_move():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    board_mock.current_player = Color.BLACK
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    controller.next_move()
    black_player_mock.next_move.assert_called_once()
    board_mock.current_player = Color.WHITE
    controller.next_move()
    white_player_mock.next_move.assert_called_once()


def test_get_possible_moves():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    expected_moves = MagicMock()
    board_mock.line_cap_move.return_value = expected_moves
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    result = controller.get_possible_moves(Color.BLACK)
    board_mock.line_cap_move.assert_called_once_with(Color.BLACK)
    assert result == expected_moves


def test_get_last_play():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    expected_play = (3, 4)
    board_mock.get_last_play.return_value = expected_play
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    result = controller.get_last_play()
    board_mock.get_last_play.assert_called_once()
    assert result == expected_play


def test_popcount():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    black_bitboard = MagicMock()
    black_bitboard.popcount.return_value = 10
    white_bitboard = MagicMock()
    white_bitboard.popcount.return_value = 8
    board_mock.black = black_bitboard
    board_mock.white = white_bitboard
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    black_count = controller.popcount(Color.BLACK)
    black_bitboard.popcount.assert_called_once()
    assert black_count == 10
    white_count = controller.popcount(Color.WHITE)
    white_bitboard.popcount.assert_called_once()
    assert white_count == 8


def test_get_position():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    black_bitboard = MagicMock()
    black_bitboard.get.return_value = True
    white_bitboard = MagicMock()
    white_bitboard.get.return_value = False
    board_mock.black = black_bitboard
    board_mock.white = white_bitboard
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    black_pos = controller.get_position(Color.BLACK, 3, 4)
    black_bitboard.get.assert_called_once_with(3, 4)
    assert black_pos
    white_pos = controller.get_position(Color.WHITE, 3, 4)
    white_bitboard.get.assert_called_once_with(3, 4)
    assert not white_pos


def test_restart():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    controller.restart()
    board_mock.restart.assert_called_once()


def test_get_turn_number():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    board_mock.get_turn_id.return_value = 5
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    result = controller.get_turn_number()
    board_mock.get_turn_id.assert_called_once()
    assert result == 5


def test_get_current_player():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    board_mock.current_player = Color.BLACK
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    result = controller.get_current_player()
    assert result == Color.BLACK


def test_current_player_is_human():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    human_player = MagicMock()
    ai_player = MagicMock()
    board_mock.current_player = Color.BLACK
    controller = GameController(board_mock, human_player, ai_player)
    with patch("othello.controllers.isinstance", return_value=True):
        result = controller.current_player_is_human()
        assert result
    board_mock.current_player = Color.WHITE
    with patch("othello.controllers.isinstance", return_value=False):
        result = controller.current_player_is_human()
        assert not result


def test_get_pieces_count():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    black_bitboard = MagicMock()
    black_bitboard.popcount.return_value = 15
    white_bitboard = MagicMock()
    white_bitboard.popcount.return_value = 12
    board_mock.black = black_bitboard
    board_mock.white = white_bitboard
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    black_count = controller.get_pieces_count(Color.BLACK)
    black_bitboard.popcount.assert_called_once()
    assert black_count == 15
    white_count = controller.get_pieces_count(Color.WHITE)
    white_bitboard.popcount.assert_called_once()
    assert white_count == 12


def test_get_history():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    history = [(0, 0, 3, 4, Color.BLACK), (0, 0, 5, 6, Color.WHITE)]
    board_mock.get_history.return_value = history
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    result = controller.get_history()
    board_mock.get_history.assert_called_once()
    assert result == history


def test_export():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    export_str = "# Board state\nX\n_..."
    board_mock.export.return_value = export_str
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    result = controller.export()
    board_mock.export.assert_called_once()
    assert result == export_str


def test_export_history():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    history_str = "# history\n1. X d3 O c5\n..."
    board_mock.export_history.return_value = history_str
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    result = controller.export_history()
    board_mock.export_history.assert_called_once()
    assert result == history_str


def test_str():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    board_str = "  a b c d\n1 _ _ _ _\n2 _ X O _\n..."
    board_mock.__str__.return_value = board_str
    controller = GameController(board_mock, black_player_mock, white_player_mock)
    result = str(controller)
    board_mock.__str__.assert_called_once()
    assert result == board_str


def test_display_time_player():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    controller = GameController(
        board_mock,
        MagicMock(spec=Player),
        MagicMock(spec=Player),
        True,
        30,
    )
    assert controller.display_time_player(Color.BLACK) == "29:59"
    controller = GameController(
        board_mock, MagicMock(spec=Player), MagicMock(spec=Player), False, 30
    )
    assert controller.display_time_player(Color.BLACK) is None


def test_play_early_return_when_game_over():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    controller = GameController(
        board_mock, MagicMock(spec=Player), MagicMock(spec=Player)
    )
    controller.logger = MagicMock()
    controller._check_for_blit_game_over = MagicMock()
    controller.is_game_over = True

    controller.play(1, 2)

    controller.logger.debug.assert_called_once_with(
        "Tried to play (%d:%d) in a game over game", 1, 2
    )
    controller._check_for_blit_game_over.assert_not_called()
    controller._board.play.assert_not_called()


def test_blitz_game_over_black():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    board_mock.current_player = Color.BLACK
    board_mock.black = MagicMock()
    board_mock.white = MagicMock()
    board_mock.black.popcount.return_value = 3
    board_mock.white.popcount.return_value = 3
    controller = GameController(
        board_mock,
        MagicMock(spec=Player),
        MagicMock(spec=Player),
        True,
        30,
    )
    controller.blitz.remaining_time["black"] = 0
    controller.play(0, 0)
    assert controller.is_game_over
    assert controller.game_over_message == "Black's time is up! White wins!"


def test_blitz_game_over_white():
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    board_mock.current_player = Color.BLACK
    board_mock.black = MagicMock()
    board_mock.white = MagicMock()
    board_mock.black.popcount.return_value = 3
    board_mock.white.popcount.return_value = 3
    controller = GameController(
        board_mock,
        MagicMock(spec=Player),
        MagicMock(spec=Player),
        True,
        30,
    )
    controller.blitz.remaining_time["white"] = 0
    controller.play(0, 0)
    assert controller.is_game_over
    assert controller.game_over_message == "White's time is up! Black wins!"


def test_blitz_timer_called_after_normal_game_over():
    """Test that blitz.change_player is called after a play that ends the game normally in blitz mode."""
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    board_mock.is_game_over.return_value = True
    controller = GameController(
        board_mock,
        MagicMock(spec=Player),
        MagicMock(spec=Player),
        blitz_mode=True,
        time_limit=30,
    )
    controller.logger = MagicMock()
    post_callback = MagicMock()
    controller.post_play_callback = post_callback
    blitz_mock = MagicMock()
    controller.blitz = blitz_mock
    controller.get_current_player = MagicMock(return_value=Color.BLACK)

    controller.play(3, 4)

    board_mock.play.assert_called_once_with(3, 4)
    assert controller.is_game_over is True
    post_callback.assert_called_once()
    blitz_mock.change_player.assert_called_once_with("black")


def test_blitz_timer_callback_white_player():
    """Test blitz.change_player is called with 'white' when current player is white."""
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    board_mock.is_game_over.return_value = False
    controller = GameController(
        board_mock,
        MagicMock(spec=Player),
        MagicMock(spec=Player),
        blitz_mode=True,
        time_limit=30,
    )
    controller.logger = MagicMock()
    post_callback = MagicMock()
    controller.post_play_callback = post_callback
    blitz_mock = MagicMock()
    controller.blitz = blitz_mock
    controller.get_current_player = MagicMock(return_value=Color.WHITE)

    controller.play(2, 3)

    board_mock.play.assert_called_once_with(2, 3)
    blitz_mock.change_player.assert_called_once_with("white")
    post_callback.assert_called_once()


def test_blitz_timer_called_after_normal_game_over():
    """Test that blitz.change_player is called after a play that ends the game normally in blitz mode."""
    board_mock = MagicMock()
    black_player_mock = MagicMock()
    white_player_mock = MagicMock()
    black_bitboard = MagicMock()
    black_bitboard.popcount.return_value = 15
    white_bitboard = MagicMock()
    white_bitboard.popcount.return_value = 12
    board_mock.black = black_bitboard
    board_mock.white = white_bitboard
    controller = GameController(
        board_mock,
        MagicMock(spec=Player),
        MagicMock(spec=Player),
        blitz_mode=True,
        time_limit=30,
    )
    controller.logger = MagicMock()
    post_callback = MagicMock()
    controller.post_play_callback = post_callback
    blitz_mock = MagicMock()
    blitz_mock.is_time_up.return_value = False
    controller.blitz = blitz_mock
    controller.get_current_player = MagicMock(return_value=Color.BLACK)

    controller.play(3, 4)

    board_mock.play.assert_called_once_with(3, 4)
    assert controller.is_game_over is True
    post_callback.assert_called_once()
    blitz_mock.change_player.assert_called_once_with("black")


def test_blitz_timer_callback_white_player():
    """Test blitz.change_player is called with 'white' when current player is white."""
    board_mock = MagicMock(spec=OthelloBoard)
    board_mock.size = BoardSize.EIGHT_BY_EIGHT
    board_mock.is_game_over.return_value = False  # Game continues after play
    controller = GameController(
        board_mock,
        MagicMock(spec=Player),
        MagicMock(spec=Player),
        blitz_mode=True,
        time_limit=30,
    )
    controller.logger = MagicMock()
    post_callback = MagicMock()
    controller.post_play_callback = post_callback
    blitz_mock = MagicMock()
    blitz_mock.is_time_up.return_value = False
    controller.blitz = blitz_mock
    controller.get_current_player = MagicMock(return_value=Color.WHITE)

    controller.play(2, 3)

    board_mock.play.assert_called_once_with(2, 3)
    blitz_mock.change_player.assert_called_once_with("white")
    post_callback.assert_called_once()
