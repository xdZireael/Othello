from copy import copy
import pytest

from othello.bitboard import Bitboard
from othello.othello_board import (
    BoardSize,
    CannotPopException,
    Color,
    OthelloBoard,
    IllegalMoveException,
)


def test_init_six():
    b = OthelloBoard(BoardSize.SIX_BY_SIX)
    assert (
        str(b)
        == """  a b c d e f
1 _ _ _ _ _ _
2 _ _ · _ _ _
3 _ · O X _ _
4 _ _ X O · _
5 _ _ _ · _ _
6 _ _ _ _ _ _"""
    )


def test_init_eight():
    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    assert (
        str(b)
        == """  a b c d e f g h
1 _ _ _ _ _ _ _ _
2 _ _ _ _ _ _ _ _
3 _ _ _ · _ _ _ _
4 _ _ · O X _ _ _
5 _ _ _ X O · _ _
6 _ _ _ _ · _ _ _
7 _ _ _ _ _ _ _ _
8 _ _ _ _ _ _ _ _"""
    )


def test_init_ten():
    b = OthelloBoard(BoardSize.TEN_BY_TEN)
    print(b)
    assert (
        str(b)
        == """   a b c d e f g h i j
1  _ _ _ _ _ _ _ _ _ _
2  _ _ _ _ _ _ _ _ _ _
3  _ _ _ _ _ _ _ _ _ _
4  _ _ _ _ · _ _ _ _ _
5  _ _ _ · O X _ _ _ _
6  _ _ _ _ X O · _ _ _
7  _ _ _ _ _ · _ _ _ _
8  _ _ _ _ _ _ _ _ _ _
9  _ _ _ _ _ _ _ _ _ _
10 _ _ _ _ _ _ _ _ _ _"""
    )


def test_init_twelve():
    b = OthelloBoard(BoardSize.TWELVE_BY_TWELVE)
    print(b)
    assert (
        str(b)
        == """   a b c d e f g h i j k l
1  _ _ _ _ _ _ _ _ _ _ _ _
2  _ _ _ _ _ _ _ _ _ _ _ _
3  _ _ _ _ _ _ _ _ _ _ _ _
4  _ _ _ _ _ _ _ _ _ _ _ _
5  _ _ _ _ _ · _ _ _ _ _ _
6  _ _ _ _ · O X _ _ _ _ _
7  _ _ _ _ _ X O · _ _ _ _
8  _ _ _ _ _ _ · _ _ _ _ _
9  _ _ _ _ _ _ _ _ _ _ _ _
10 _ _ _ _ _ _ _ _ _ _ _ _
11 _ _ _ _ _ _ _ _ _ _ _ _
12 _ _ _ _ _ _ _ _ _ _ _ _"""
    )


""" black's turn, C => candidate
| | | | | | | | |
| | | | | | | | |
| | | |C| | | | |
| | |C|O|X| | | |
| | | |X|O|C| | |
| | | | |C| | | |
| | | | | | | | |
| | | | | | | | |
"""


def test_line_cap_move_starting_pos():
    """
    Test if the legal moves at the starting position are correctly computed by the line cap move algorithm.

    The legal moves at the starting position are the four corner squares of the board (i.e. A1, A8, H1, H8).
    """

    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    legal_mask = 0b0000000000000000000100000010000000000100000010000000000000000000
    cap = b.line_cap_move(Color.BLACK)
    assert cap.bits == legal_mask


""" black's turn, C => candidate
| | | | | | | | |
| | | | | | | | |
| | | |C|C|C| | |
| | |C|O|O|X| | |
| | | |X|O|C| | |
| | | |C|O| | | |
| | | | |X|C| | |
| | | | | | | | |
"""


def test_line_cap_move_later_pos():
    """
    Test if the legal moves are correctly computed by the line cap move algorithm at a given position later in the game.

    The given position is the following:
    - Black's turn.
    - Black's pions are at E4, D5, D4, E5, F5, F4, C4, C5, G5, G4, H4, H5.
    - White's pions are at D3, E3, F3, G3, H3, H2.
    - The legal moves are the four corner squares of the board (i.e. A1, A8, H1, H8) and the squares at
      C3, F2, G1, H7.
    """
    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    b.white.bits = 0b0000000000000000000100000001000000011000000000000000000000000000
    b.black.bits = 0b0000000000010000000000000000100000100000000000000000000000000000
    legal_mask = 0b0000000000100000000010000010000000000100001110000000000000000000
    cap = b.line_cap_move(Color.BLACK)
    assert cap.bits == legal_mask


""" white's turn, C => candidate
| | | | | | | | |
| | | | | | | | |
| | |C| |C| | | |
| | |X|X|X| | | |
| | |C|X|O| | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
"""


def test_line_cap_move_starting_pos_whites():
    """
    Test if the legal moves are correctly computed by the line cap move algorithm at the starting position of the game,
    with white playing first.

    The given position is the standard starting position of the game, with the black pions at E4 and D5, and the white pions at D4 and E5.
    The legal moves are the four corner squares of the board (i.e. A1, A8, H1, H8) and the squares at
    C3, F2, G1, H7.
    """
    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    b.white.bits = 0b0000000000000000000000000001000000000000000000000000000000000000
    b.black.bits = 0b0000000000000000000000000000100000011100000000000000000000000000
    legal_mask = 0b0000000000000000000000000000010000000000000101000000000000000000
    cap = b.line_cap_move(Color.WHITE)
    assert cap.bits == legal_mask


""" black's turn, C => candidate
| | | | | | | | |
| | | | | | | | |
| | | | | | |C| |
| | |C|O|O|X|C| |
| | |C|X|O| | | |
| | |C|C|O| | | |
| | | | |X| | | |
| | | | |C| | | |
"""


def test_line_cap_move_later_pos_whites():
    """
    Test if the legal moves are correctly computed by the line cap move algorithm at a given position later in the game,
    with white playing.

    The given position is as follows:
    - White's turn.
    - White's pions are at D3, E3, F3, G3, H3, E4.
    - Black's pions are at D4, E5, F5, G5, H5, F4.
    - The legal moves are the squares at A1, A8, H1, H8, C3, F2, G1, H7.
    """

    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    b.white.bits = 0b0000000000000000000100000001000000011000000000000000000000000000
    b.black.bits = 0b0000000000010000000000000000100000100000000000000000000000000000
    legal_mask = 0b0001000000000000000011000000010001000100010000000000000000000000
    cap = b.line_cap_move(Color.WHITE)
    assert cap.bits == legal_mask


""" black's turn, M => bit of the mask
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | |O|X| | | |
| | | |X|M| | | |
| | | | |M| | | |
| | | | | | | | |
| | | | | | | | |
"""


def test_line_cap_start_position():
    """
    Test if the line cap move algorithm is correctly computing the mask of a given point in the standard starting position of the game,
    with black playing first.

    The given position is the standard starting position of the game, with the black pions at D4 and E5, and the white pions at D5 and E4.
    The mask returned by the line cap move algorithm should be 0b0000000000000000000100000001000000000000000000000000000000000000.
    """
    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    thruth_mask = 0b0000000000000000000100000001000000000000000000000000000000000000
    mask = b.line_cap(4, 5, Color.BLACK)
    assert thruth_mask == mask.bits


"""
  a b c d e f g h
1 _ _ _ _ O O O O
2 _ _ _ _ X X X O
3 _ _ O X _ _ X O
4 _ _ X O _ _ X O
5 _ _ O X C _ X O
6 _ _ _ X X X X O
7 _ _ O _ _ _ _ _
8 _ _ _ O _ _ _ _"""


def test_complex_position():
    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    b.white.bits = 0b0000100000000100100000001000010010001000100001001000000011110000
    b.black.bits = 0b0000000000000000011110000100100001000100010010000111000000000000
    cap = b.line_cap(4, 4, Color.WHITE)
    thruth_mask = 0b0000000000000000000010000001100000000000000000000000000000000000
    assert cap.bits == thruth_mask


def test_export_board():
    board_raw = """# board
O
_ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _
_ _ X _ X _ _ _ _ _
_ _ X X O O O _ _ _
_ _ X _ X X X _ _ _
_ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _
# history
1. X g6 O g5
2. X e4 O d5
3. X c6 O c5
4. X c4"""
    board = OthelloBoard(BoardSize.TEN_BY_TEN)
    board.play(6, 5)
    board.play(6, 4)
    board.play(4, 3)
    board.play(3, 4)
    board.play(2, 5)
    board.play(2, 4)
    board.play(2, 3)
    print(board.export())
    assert board_raw == board.export()


def test_game_over_exception_when_board_full():
    size = BoardSize.SIX_BY_SIX
    board = OthelloBoard(size)
    white = Bitboard(size.value)
    black = Bitboard(size.value)
    for x in range(size.value):
        for y in range(size.value):
            if (x, y) == (3, 3):
                continue
            elif (x, y) == (3, 4):
                white.set(x, y, True)
            elif (x, y) == (3, 5):
                black.set(x, y, True)
            else:
                white.set(x, y, True)
    board.black = black
    board.white = white
    board.current_player = Color.BLACK

    assert not board.is_game_over()

    board.play(3, 3)
    assert board.is_game_over()

    assert board.is_game_over()


def test_illegal_move_occupied_cell():
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.play(5, 4)
    with pytest.raises(IllegalMoveException):
        board.play(5, 4)


def test_invert():
    p = Color.BLACK
    assert ~p == Color.WHITE
    assert ~~p == Color.BLACK
    p = Color.EMPTY
    assert ~p == Color.EMPTY


def test_pop_empty_board():
    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    with pytest.raises(CannotPopException):
        b.pop()

    b.play(5, 4)
    b.pop()
    with pytest.raises(CannotPopException):
        b.pop()


def test_boardsize_from():
    assert BoardSize.SIX_BY_SIX is BoardSize.from_value(6)
    assert BoardSize.EIGHT_BY_EIGHT is BoardSize.from_value(8)
    assert BoardSize.TEN_BY_TEN is BoardSize.from_value(10)
    assert BoardSize.TWELVE_BY_TWELVE is BoardSize.from_value(12)
    with pytest.raises(Exception):
        BoardSize.from_value(4)


def test_eq():
    def __set(b: OthelloBoard):
        b.play(5, 4)
        b.play(5, 5)

    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    __set(b)
    b2 = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    __set(b2)
    assert b == b2
    b3 = copy(b2)
    b3.current_player = Color.WHITE
    assert b != b3
    b.play(4, 5)
    assert b != b2
    assert b != Bitboard(8)


def test_cant_build_illegal_board():
    black = Bitboard(6)
    white = Bitboard(10)
    with pytest.raises(Exception):
        OthelloBoard(BoardSize.SIX_BY_SIX, black=black, white=white)


def test__str__():
    """
    Test if the string representation of the board is correctly computed at the starting position of the game.

    The given position is the standard starting position of the game, with the black pions at D4 and E5, and the white pions at D5 and E4.
    The expected string representation of the board is the following:
    a b c d e f g h
    0
    1
    2
    3      O X
    4      X O
    5
    6
    7
    """
    b = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    starting_board = """  a b c d e f g h
1 _ _ _ _ _ _ _ _
2 _ _ _ _ _ _ _ _
3 _ _ _ · _ _ _ _
4 _ _ · O X _ _ _
5 _ _ _ X O · _ _
6 _ _ _ _ · _ _ _
7 _ _ _ _ _ _ _ _
8 _ _ _ _ _ _ _ _"""
    assert str(b) == starting_board


def test_restart():
    board = OthelloBoard(BoardSize.TEN_BY_TEN)
    init_state = copy(board)
    board.play(6, 5)
    board.play(6, 4)
    board.play(4, 3)
    board.play(3, 4)
    assert board != init_state
    board.restart()
    assert board == init_state
