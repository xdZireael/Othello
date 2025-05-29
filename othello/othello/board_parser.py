"""This module contains utilities used for loading an OthelloBoard from a save"""

import re
import logging

import othello.logger as log
from othello.bitboard import Bitboard
from othello.othello_board import BoardSize, Color, IllegalMoveException, OthelloBoard


logger = logging.getLogger("Othello")


class BoardParserException(Exception):
    """
    Thrown on parsing error, contains a custom message as well as the line where it happened
    """

    def __init__(self, msg: str, line: int):
        super().__init__(f"{msg} AT LINE {line}")


class BoardParser:
    """
    Takes a board at initialization and allows for retrieving an OthelloBoard matching
    the state of the board save str representation.
    """

    comment_char = "#"
    empty_char = " "

    def __init__(self, raw_save: str):
        logger.debug(
            "Initializing BoardParser with %d lines of input.",
            len(raw_save.split("\n")),
        )
        self.__buffer = raw_save.split("\n")
        self.__x = 0
        self.__y = 0
        self.__case_values = tuple(c.value for c in Color)
        logger.debug("   Case values initialized: %s.", self.__case_values)

    def get_current_line(self) -> str:
        """
        Returns the current line of the raw save.

        :return: The raw string of the current line
        :rtype: str
        """
        return self.__buffer[self.__y]

    def parse(self) -> OthelloBoard:
        """
        Parses the board given at init time and returns an OthelloBoard configured accordingly.
        """
        logger.debug("Starting board parsing, parse function in board_parser.py.")
        board = self.__parse_board()
        logger.debug("   Board parsed successfully.")
        if (maybe_computed_board := self.__parse_history(board)) is not None:
            logger.debug("   History parsed successfully.")
            board = maybe_computed_board

        return board

    def __parse_board(self):
        """
        Parse the board from the raw save.

        This method parses the board from the raw save given at init time and returns an
        OthelloBoard configured accordingly.

        :return: An OthelloBoard configured with the state of the raw save
        :rtype: OthelloBoard
        """
        logger.debug("Entering function __parse_board from board_parser.py.")
        color = None
        # first we need to find the color.
        self.__skip_newlines()
        if self.__eof():
            log.log_error_message(
                BoardParserException("trying to parse an empty board", self.__y)
            )
            raise BoardParserException("trying to parse an empty board", self.__y)
        if self.__current() not in (Color.BLACK.value, Color.WHITE.value):
            log.log_error_message(
                BoardParserException("expected to find color", self.__y)
            )
            raise BoardParserException("expected to find color", self.__y)
        color = Color.BLACK if self.__current() == Color.BLACK.value else Color.WHITE
        # then we need to find the start of the board
        self.__skip_newlines()
        self.__x = 0
        self.__next_line()
        # we pre-parse the first line to find the supposed size of the board
        if self.__eof():
            log.log_error_message(BoardParserException("reached end of file", self.__y))
            raise BoardParserException("reached end of file", self.__y)
        if (board_size := self.__find_board_size()) not in (
            bs.value for bs in BoardSize
        ):
            log.log_error_message(
                BoardParserException("illegal board size value", self.__y)
            )
            raise BoardParserException("illegal board size value", self.__y)

        # and now we generate the two masks and add black and white pieces line by line
        black_mask = Bitboard(board_size)
        white_mask = Bitboard(board_size)
        for board_y in range(board_size):
            if self.__eof():
                log.log_error_message(
                    BoardParserException(
                        "reached end of file before finished parsing", self.__y
                    )
                )
                raise BoardParserException(
                    "reached end of file before finished parsing", self.__y
                )
            self.__skip_newlines()
            (line_black_mask, line_white_mask) = self.__line_mask(board_y, board_size)
            black_mask |= line_black_mask
            white_mask |= line_white_mask
            if board_y < board_size - 1:
                self.__next_line()
        logger.debug(
            "   Board fully parsed: black_mask=%s, white_mask=%s, current_player=%s.",
            black_mask,
            white_mask,
            color,
        )
        return OthelloBoard(
            BoardSize.from_value(board_size),
            black=black_mask,
            white=white_mask,
            current_player=color,
        )

    def __parse_history(self, board: OthelloBoard):
        """
        Parse the history from the raw save given at init time and returns an
        OthelloBoard configured accordingly.

        This method parses the history from the raw save given at init time and returns an
        OthelloBoard configured accordingly.
        If there is no history, it returns None.

        :param board: The board to generate the moves from
        :type board: OthelloBoard
        :return: An OthelloBoard configured with the state of the raw save
        :rtype: OthelloBoard | None
        """
        logger.debug("Entering function __parse_history from board_parser.py.")
        self.__skip_newlines()
        if self.__eof():
            logger.debug("   No history section found (EOF).")
            return None
        str_board_max_column = chr(ord("a") + board.size.value)
        str_board_max_line = board.size.value + 1
        play_regex = rf"(([a-{str_board_max_column}][1-{str_board_max_line}])|(-1-1))"
        line_regex = rf"(\d+)\. X {play_regex}( O {play_regex})?"
        line_regex_compiled = re.compile(line_regex)

        computed_board = OthelloBoard(board.size)
        while not self.__eof():
            self.__parse_history_turn(computed_board, line_regex_compiled)
            self.__skip_newlines()
        logger.debug("   History parsing complete.")
        return computed_board

    def __parse_history_turn(self, board: OthelloBoard, line_regex):
        """
        Parse a single turn from the history file into the given board
        :param board: The OthelloBoard to play the moves into
        :param line_regex: The compiled regex used to parse the line
        :raises BoardParserException: If the line is not correctly formatted
        :raises IllegalMoveException: If either the black or white move is illegal
        """
        logger.debug("Parsing one turn")
        line = str()
        while not self.__eol():
            line += self.__current()
            self.__next_char()

        if (matches := line_regex.match(line)) is None:
            logger.error("Incorrect line format.")
            raise BoardParserException(f'incorrect line format: "{line}"', self.__y)

        turn_id = int(matches.group(1))
        black_play = matches.group(2)
        white_play = matches.group(6)
        if turn_id != board.get_turn_id():
            logger.error("Incorrect turn number in history.")
            raise BoardParserException("incorrect turn number in history", self.__y)
        move = BoardParser.__parse_move(black_play)
        try:
            board.play(move[0], move[1])
        except IllegalMoveException as exc:
            log.log_error_message(exc, context="Black move is illegal.")
            raise BoardParserException(
                f"black move {black_play} is illegal ({exc})", self.__y
            ) from exc

        if white_play is not None:
            move = BoardParser.__parse_move(white_play)
            try:
                board.play(move[0], move[1])
            except IllegalMoveException as exc:
                print(board)
                log.log_error_message(exc, context="Black move is illegal.")
                raise BoardParserException(
                    f"white move {white_play} is illegal ({exc})", self.__y
                ) from exc

    @staticmethod
    def __parse_move(move: str) -> tuple[int, int]:
        """
        Parses a move string in the format of a letter followed by a number.

        This function converts the move string into x and y coordinates for the board.
        The letter represents the column (where 'a' is the first column), and the
        number represents the row (where '1' is the first row). The special move
        "-1-1" is used to represent a pass or invalid move and is returned as (-1, -1).

        :param move: The move string to parse.
        :type move: str
        :return: A tuple containing the x and y coordinates of the move.
        :rtype: tuple[int, int]
        """
        logger.debug("Parsing move string: '%s'.", move)
        empty_move_str = "-1-1"

        if move == empty_move_str:
            return (-1, -1)
        move_x_coord = ord(move[0]) - ord("a")
        move_y_coord = int(move[1:]) - 1
        logger.debug(
            "   Move parsed as coordinates: (%d, %d)", move_x_coord, move_y_coord
        )
        return (move_x_coord, move_y_coord)

    def __next_char(self):
        """
        Move to the next character in the buffer.
        If we reach the end of the current line, move to the next line and reset the column to 0.
        If we are already at the end of the file, do nothing.
        """

        if self.__eol():
            self.__y += 1
            self.__x = 0
        else:
            self.__x += 1

    def __next_line(self):
        """
        Move to the next line in the buffer.
        If we are already at the end of the file, raise a BoardParserException.
        """
        if not self.__eof():
            self.__y += 1
            self.__x = 0
        else:
            raise BoardParserException("already reached EOF", self.__y)

    def __eol(self, peek_cursor=0):
        """
        Returns True if we are at the end of the line, or if the first
        character we peek at is a '#'.
        The peek_cursor parameter is used to peek at a character ahead of the current position.
        :param peek_cursor: The number of characters to peek ahead.
        :type peek_cursor: int
        :return: True if we are at the end of the line or if the peeked character is '#'.
        :rtype: bool
        """
        return (
            self.__x + peek_cursor == len(self.__buffer[self.__y])
            or self.__peek(peek_cursor) == self.comment_char
        )

    def __eof(self):
        """
        Returns True if we are at the end of the file (EOF), or if we are at the last line
        of the file and the line is empty.
        :return: True if we are at EOF or if the last line is empty.
        :rtype: bool
        """
        return self.__y >= len(self.__buffer) or (
            self.__eol() and self.__y >= len(self.__buffer) - 1
        )

    def __line_mask(self, board_y: int, board_size: int) -> tuple[Bitboard, Bitboard]:
        """
        Reads a line of the board and returns the bitmasks for the black and white pieces
        on that line.

        :param board_y: The y coordinate of the line to read.
        :type board_y: int
        :param board_size: The size of the board.
        :type board_size: int
        :return: A tuple containing the black and white bitmasks.
        :rtype: tuple[Bitboard, Bitboard]
        """
        logger.debug(
            "Creating line mask for board_y=%d, board_size=%d.", board_y, board_size
        )

        black_mask = Bitboard(board_size)
        white_mask = Bitboard(board_size)
        case_cursor = 0
        while not self.__eol():
            peek_value = self.__current()
            if peek_value in self.__case_values:
                if peek_value == Color.BLACK.value:
                    black_mask.set(case_cursor, board_y, True)
                elif peek_value == Color.WHITE.value:
                    white_mask.set(case_cursor, board_y, True)
                case_cursor += 1
            elif peek_value != self.empty_char:
                logger.error("Expected to find either a case or a space.")
                raise BoardParserException(
                    f"expected to find either a case or a space, found {peek_value}",
                    self.__y,
                )
            self.__next_char()
        if case_cursor != board_size:
            logger.error(
                "Line of size %d where it should have been %d.", case_cursor, board_size
            )
            raise BoardParserException(
                f"Line of size {case_cursor} where it should have been {board_size}",
                self.__y,
            )
        logger.debug(
            "   Line mask created: black=%s, white=%s.", black_mask, white_mask
        )
        return (black_mask, white_mask)

    def __find_board_size(self) -> int:
        """
        Finds the size of the board by peeking at the first line of the board representation.

        It will count the number of cases until it finds a newline or the end of the file.
        If it finds a character that is not a case or a space, a BoardParserException is raised.

        :return: The size of the board
        :rtype: int
        """
        board_size = 0
        peek_cursor = 0
        while not self.__eol(peek_cursor):
            peek_value = self.__peek(peek_cursor)
            if peek_value in self.__case_values:
                board_size += 1
            elif peek_value != self.empty_char:
                raise BoardParserException(
                    f"expected to find either a case or a space, found {peek_value}",
                    self.__y,
                )
            peek_cursor += 1
        logger.debug("Detected board size: %d", board_size)
        return board_size

    def __peek(self, n_to_peek: int) -> str:
        """
        Peeks at the n_to_peek character after the current position and returns it.

        :param n_to_peek: The number of characters to peek after the current position
        :type n_to_peek: int
        :return: The character at the peeked position
        :rtype: str
        """
        return self.__buffer[self.__y][self.__x + n_to_peek]

    def __skip_spaces(self):
        """
        Skips all the spaces after the current position.

        This method iterates over the current line, calling __next_char
        until it finds a non-space character.
        It is used to skip the spaces between cases in the board representation.
        """
        while not self.__eol() and self.__current() == self.empty_char:
            self.__next_char()

    def __skip_newlines(self):
        """
        Skips all the newlines after the current position.

        This method is used to advance the parser after a command or a board
        representation has been found. It iterates over the lines of the file,
        calling __next_line until it finds a line that is not empty. It also
        skips all the spaces at the beginning of the line.
        """
        self.__skip_spaces()
        while not self.__eof() and self.__eol():
            self.__next_line()
            self.__x = 0
            self.__skip_spaces()

    def __current(self) -> str:
        """
        Returns the character at the current position in the buffer.

        :return: The character at the current position
        :rtype: str
        """
        return self.__buffer[self.__y][self.__x]
