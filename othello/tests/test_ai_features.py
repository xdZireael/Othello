import pytest
from copy import deepcopy

from othello.othello_board import OthelloBoard, BoardSize, Color
from othello.ai_features import (
    all_in_one_heuristic,
    corners_captured_heuristic,
    coin_parity_heuristic,
    find_best_move,
    minimax,
    alphabeta,
    mobility_heuristic,
    random_move,
)

# region Fixtures


@pytest.fixture
def board_start_pos():
    """Creates an Othello board with the starting position."""
    board = OthelloBoard(BoardSize.SIX_BY_SIX)
    return board


@pytest.fixture
def board_with_corners():
    """Creates an Othello board where BLACK has 2 corners and WHITE has 1."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.black.set(0, 0, True)
    board.black.set(7, 7, True)
    board.white.set(7, 0, True)
    return board


@pytest.fixture
def board_with_all_corners():
    """Creates an Othello board where BLACK has all four corners."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.black.set(0, 0, True)
    board.black.set(7, 0, True)
    board.black.set(0, 7, True)
    board.black.set(7, 7, True)
    return board


@pytest.fixture
def board_one_corner_each():
    """Creates an Othello board where BLACK has 1 corner and WHITE has 1 corner."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.black.set(0, 0, True)
    board.white.set(7, 7, True)
    return board


@pytest.fixture
def board_6_one_move_possible():
    """Creates an Othello board where WHITE only have 1 possible move."""
    board = OthelloBoard(BoardSize.SIX_BY_SIX)
    board.current_player = Color.WHITE
    board.black.set(0, 4, True)
    board.black.set(0, 5, True)
    board.black.set(1, 4, True)
    board.black.set(1, 5, True)
    board.black.set(2, 4, True)
    board.black.set(2, 5, True)
    board.black.set(3, 4, True)
    board.black.set(3, 5, True)
    board.black.set(4, 4, True)
    board.black.set(4, 5, True)
    board.white.set(1, 1, True)
    board.white.set(1, 2, True)
    board.white.set(1, 3, True)
    board.white.set(2, 2, True)
    board.white.set(2, 3, True)
    board.black.set(2, 3, False)
    board.white.set(3, 2, True)
    board.black.set(3, 2, False)
    board.white.set(3, 3, True)
    board.white.set(4, 2, True)
    return board


@pytest.fixture
def board_6_test_best_moves():
    """Creates an Othello board to test WHITE's best moves."""
    board = OthelloBoard(BoardSize.SIX_BY_SIX)
    board.current_player = Color.WHITE
    board.black.set(1, 0, True)
    board.black.set(1, 1, True)
    board.black.set(1, 2, True)
    board.black.set(1, 3, True)
    board.black.set(1, 4, True)
    board.black.set(2, 3, True)
    board.black.set(3, 2, True)
    board.white.set(2, 2, True)
    board.white.set(3, 3, True)
    return board


@pytest.fixture
def board_6_game_over():
    """Creates an Othello board that is completely full and so in a game-over state."""
    board = OthelloBoard(BoardSize.SIX_BY_SIX)
    board.current_player = Color.BLACK

    for x in range(6):
        for y in range(6):
            if (x + y) % 2 == 0:
                board.black.set(x, y, True)
            else:
                board.white.set(x, y, True)

    return board


@pytest.fixture
def board_6_empty():
    """Create an empty board with no possible moves."""
    board = OthelloBoard(BoardSize.SIX_BY_SIX)
    board.white.set(2, 2, False)
    board.white.set(3, 3, False)
    board.black.set(2, 3, False)
    board.black.set(3, 2, False)
    return board


# endregion Fixtures

# region Corners Captured


def test_empty_board_corners(board_start_pos):
    """Tests that an empty board gives a score of 0 for both players."""
    assert corners_captured_heuristic(board_start_pos, Color.BLACK) == 0
    assert corners_captured_heuristic(board_start_pos, Color.WHITE) == 0


def test_corners_advantage_black(board_with_corners):
    """Tests that BLACK gets a positive score when having more corners than WHITE."""
    assert corners_captured_heuristic(board_with_corners, Color.BLACK) > 0
    assert corners_captured_heuristic(board_with_corners, Color.WHITE) < 0


def test_all_corners_black(board_with_all_corners):
    """Tests that BLACK gets the maximum score when owning all corners."""
    assert corners_captured_heuristic(board_with_all_corners, Color.BLACK) == 100
    assert corners_captured_heuristic(board_with_all_corners, Color.WHITE) == -100


def test_one_corner_each(board_one_corner_each):
    """Tests that if both players have the same number of corners, the score is 0."""
    assert corners_captured_heuristic(board_one_corner_each, Color.BLACK) == 0
    assert corners_captured_heuristic(board_one_corner_each, Color.WHITE) == 0


# endregion Corners Captured

# region Coin Parity


def test_empty_board_coin_parity(board_start_pos):
    """Tests that an empty board gives a score of 0 for both players."""
    assert coin_parity_heuristic(board_start_pos, Color.BLACK) == 0
    assert coin_parity_heuristic(board_start_pos, Color.WHITE) == 0


def test_coin_parity_advantage_black(board_with_corners):
    """Tests that BLACK gets a positive score when having more coins than WHITE."""
    assert coin_parity_heuristic(board_with_corners, Color.BLACK) > 0
    assert coin_parity_heuristic(board_with_corners, Color.WHITE) < 0


def test_coin_parity_advantage_white(board_one_corner_each):
    """Tests that WHITE gets a negative score when having more coins than BLACK."""
    board_one_corner_each.white.set(1, 1, True)
    assert coin_parity_heuristic(board_one_corner_each, Color.BLACK) < 0
    assert coin_parity_heuristic(board_one_corner_each, Color.WHITE) > 0


def test_draw_coin_parity(board_one_corner_each):
    """Tests that if both players have the same number of coins, the score is 0."""
    assert coin_parity_heuristic(board_one_corner_each, Color.BLACK) == 0
    assert coin_parity_heuristic(board_one_corner_each, Color.WHITE) == 0


def test_invalid_color_empty_coin_parity(board_start_pos):
    """Tests that the function returns Color.EMPTY when no color is given. (invalid color)"""
    assert coin_parity_heuristic(board_start_pos, Color.EMPTY) == Color.EMPTY


# endregion Coin Parity

# region Mobility


def test_mobility_start_pos(board_start_pos):
    assert mobility_heuristic(board_start_pos, Color.BLACK) == 0
    assert mobility_heuristic(board_start_pos, Color.WHITE) == 0


def test_mobility_no_move(board_6_empty):
    assert mobility_heuristic(board_6_empty, Color.BLACK) == 0
    assert mobility_heuristic(board_6_empty, Color.WHITE) == 0


def test_mobility_no_color(board_start_pos):
    assert mobility_heuristic(board_start_pos, Color.EMPTY) == Color.EMPTY


# endregion Mobility

# region All In One Heuristic


def test_all_in_one_start_pos(board_start_pos):
    assert all_in_one_heuristic(board_start_pos, Color.BLACK) == 0
    assert all_in_one_heuristic(board_start_pos, Color.WHITE) == 0


def test_all_in_one_advantage_black(board_with_corners):
    assert all_in_one_heuristic(board_with_corners, Color.BLACK) > 0
    assert all_in_one_heuristic(board_with_corners, Color.WHITE) < 0


# endregion All In One Heuristic

# region Minimax/Alphabeta


def test_minimax_ab_basic_evaluation(board_start_pos):
    board_copy_minimax = deepcopy(board_start_pos)
    assert minimax(board_copy_minimax, 1, Color.BLACK, corners_captured_heuristic) == 0
    board_copy_alphabeta = deepcopy(board_start_pos)
    assert (
        alphabeta(
            board_copy_alphabeta,
            1,
            float("-inf"),
            float("inf"),
            Color.BLACK,
            corners_captured_heuristic,
        )
        == 0
    )


def test_minimax_ab_no_moves(board_6_empty):
    board_copy_minimax = deepcopy(board_6_empty)
    assert minimax(board_copy_minimax, 1, Color.BLACK, corners_captured_heuristic) == 0
    board_copy_alphabeta = deepcopy(board_6_empty)
    assert (
        alphabeta(
            board_copy_alphabeta,
            1,
            float("-inf"),
            float("inf"),
            Color.BLACK,
            corners_captured_heuristic,
        )
        == 0
    )


def test_minimax_ab_min_player(board_start_pos):
    board_copy_minimax = deepcopy(board_start_pos)
    assert minimax(board_copy_minimax, 1, Color.WHITE, corners_captured_heuristic) == 0
    board_copy_alphabeta = deepcopy(board_start_pos)
    assert (
        alphabeta(
            board_copy_alphabeta,
            1,
            float("-inf"),
            float("inf"),
            Color.WHITE,
            corners_captured_heuristic,
        )
        == 0
    )


def test_ab_beta_eq_alpha(board_start_pos):
    assert (
        alphabeta(
            board_start_pos,
            1,
            0,
            0,
            Color.WHITE,
            corners_captured_heuristic,
        )
        == 0
    )


# endregion Minimax/Alphabeta

# region Find Best Move


def test_1_move_possible(board_6_one_move_possible):
    """Tests that the function returns the only possible move."""
    assert find_best_move(
        board_6_one_move_possible, 1, Color.WHITE, "minimax", "corners_captured"
    ) == (5, 5)
    assert find_best_move(
        board_6_one_move_possible, 1, Color.WHITE, "alphabeta", "corners_captured"
    ) == (5, 5)


def test_mobility(board_6_one_move_possible):
    """Tests that the function returns the only possible move."""
    assert find_best_move(
        board_6_one_move_possible, 1, Color.WHITE, "minimax", "mobility"
    ) == (5, 5)
    assert find_best_move(
        board_6_one_move_possible, 1, Color.WHITE, "alphabeta", "mobility"
    ) == (5, 5)


def test_all_in_one(board_6_one_move_possible):
    """Tests that the function returns the only possible move."""
    assert find_best_move(
        board_6_one_move_possible, 1, Color.WHITE, "minimax", "all_in_one"
    ) == (5, 5)
    assert find_best_move(
        board_6_one_move_possible, 1, Color.WHITE, "alphabeta", "all_in_one"
    ) == (5, 5)


def test_best_moves_corners_and_parity(board_6_test_best_moves):
    assert find_best_move(
        board_6_test_best_moves, 1, Color.WHITE, "minimax", "all_in_one"
    ) == (0, 0)
    assert find_best_move(
        board_6_test_best_moves, 1, Color.WHITE, "alphabeta", "corners_captured"
    ) == (0, 0)
    assert find_best_move(
        board_6_test_best_moves, 1, Color.WHITE, "minimax", "coin_parity"
    ) == (0, 3)
    assert find_best_move(
        board_6_test_best_moves, 1, Color.WHITE, "alphabeta", "coin_parity"
    ) == (0, 3)


def test_game_over_best_move(board_6_game_over):
    assert find_best_move(
        board_6_game_over, 1, Color.BLACK, "minimax", "corners_captured"
    ) == (-1, -1)


# endregion Find Best Move

# region Random Move


def test_random_move_start(board_start_pos):
    valid_moves = board_start_pos.line_cap_move(
        board_start_pos.current_player
    ).hot_bits_coordinates()
    assert random_move(board_start_pos) in valid_moves


def test_random_move_1_possible(board_6_one_move_possible):
    assert random_move(board_6_one_move_possible) == (5, 5)


# endregion Random Move
