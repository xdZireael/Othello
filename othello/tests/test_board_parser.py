import pytest

from othello.board_parser import BoardParser, BoardParserException
from othello.othello_board import BoardSize, OthelloBoard, Color


def test_starting_board():
    board_raw = """

#comment
X
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X O _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _"""
    parser = BoardParser(board_raw)
    board = parser.parse()
    assert board == OthelloBoard(BoardSize.EIGHT_BY_EIGHT)


def test_more_complex_board():
    board_raw = """
#comment
 # another
O# ---
_ _ _ _ _ _ # other comment
_ _ _ _ _ _
_ _ O X _ _
_ _ X X O _
_ O _ X X _
_ _ _ _ _ _
"""
    truth_board = OthelloBoard(BoardSize.SIX_BY_SIX, current_player=Color.WHITE)
    truth_board.black.bits = 0b000000011000001100001000000000000000
    truth_board.white.bits = 0b000000000010010000000100000000000000
    parser = BoardParser(board_raw)
    board = parser.parse()
    assert board == truth_board


def test_illegal_boards():
    board_raw = """
#comment
 # another
O# ---
_ _ _ _ _ _ # other comment
_ _ _ _ _ _
_ _ O X _ _
_ _ X X O
_ O _ X X _
_ _ _ _ _ _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()
    board_raw = """
#comment
 # another
O# ---
_ _ _ _ _ _ # other comment
_ _ _ _ _ _
_ _ O X _ _
_ _ X X O _
_ O _ X X _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_illegal_color():
    board_raw = """

#comment
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X O _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()

    board_raw = """

#comment
K
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X O _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_two_colors():
    board_raw = """
#comment
 # another
O# ---
O
_ _ _ _ _ _ # other comment
_ _ _ _ _ _
_ _ O X _ _
_ _ X X O _
_ O _ X X _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_no_board():
    board_raw = """
#comment
 # another
O# ---
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_incoherent_turn_numbers():
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f5 O d6
3. X c6 O b6
3. X d7
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_missing_black_play():
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f5 O d6
2. X  O b6
3. X d7
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_illegal_history_move():
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f6 O d6
2. X  O b6
3. X d7
"""

    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f5 O d7
2. X  O b6
3. X d7
"""

    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_incoherent_board():
    board_raw = """
O
_ R _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()
    board_raw = """
O
_ _ _ _ _ _
_ R _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_empty_board():
    board_raw = """"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()

    board_raw = """

    """
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_next_char_on_eol():
    board_raw = """
O
"""
    b = BoardParser(board_raw)
    assert b._BoardParser__y == 0
    b._BoardParser__next_char()
    assert b._BoardParser__y == 1


def test_nextline_on_eof():
    board_raw = """"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b._BoardParser__next_line()


def test_board_illegal_size():
    board_raw = """
X
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ O X _ _ _ _ _ _
_ _ _ _ _ _ X O _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


"""
"""


def test_simple_history():
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f5 O d6
2. X c6 O b6
3. X d7
"""
    b = BoardParser(board_raw)
    o = b.parse()
    assert len(o.get_history()) == 5


def test_only_color():
    board_raw = "O"
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_fuzzy_board():
    board_raw = "azazazaeiazjeoizajezoaiejazoiej  aaajzieajozaije"
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()

    board_raw = """O
    _ _ _ _ _ _
    _ _ _ _ _ _
    _ _ _ _ _ _
    f
    _ _ _ _ _ _
    _ _ _ _ _ _
    _ _ _ _ _ _"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_onecantplay():
    board_raw = """# board
X
O O O X X X
O O X X X X
O X O X X X
O X O O X X
O O O X O O
O O O O O O
# history
1. X b3 O b2
2. X c2 O d2
3. X e1 O e2
4. X f1 O f2
5. X f3 O e4
6. X e5 O f6
7. X f4 O f5
8. X d6 O e6
9. X d5 O b5
10. X e3 O a2
11. X a3 O b4
12. X c5 O a4
13. X a5 O a6
14. X b6 O c6
15. X b1 O a1
16. X -1-1 O c1
"""
    b = BoardParser(board_raw)
    b.parse()


def test_get_current_line():
    file_raw = """line1
line 2
line3"""
    b = BoardParser(file_raw)
    assert b.get_current_line() == "line1"
    b._BoardParser__next_line()
    assert b.get_current_line() == "line 2"
