"""
Everything related to the actual board of Othello.
"""

# pylint: disable=invalid-unary-operand-type  # disabled because it actually is correctly used
from __future__ import annotations
from copy import copy
from enum import Enum
from string import ascii_lowercase
import logging

from othello.bitboard import Bitboard, Direction

logger = logging.getLogger("Othello")


class Color(Enum):
    """
    Enum with the possibilities for a case as well as their string representation.
    """

    BLACK = "X"
    WHITE = "O"
    POSSIBLE = "·"
    EMPTY = "_"

    def __invert__(self) -> Color:
        if self is Color.BLACK:
            return Color.WHITE
        if self is Color.WHITE:
            return Color.BLACK
        return Color.EMPTY

    def __str__(self) -> str:
        if self is Color.BLACK:
            return "black"
        if self is Color.WHITE:
            return "white"
        return "empty"


class IllegalMoveException(Exception):
    """
    Thrown when the user tries to push an illegal move
    """

    def __init__(self, x_coord: int, y_coord: int, current_player: Color):
        super().__init__(
            f"Move {x_coord}:{y_coord} from player {current_player} is illegal"
        )


class CannotPopException(Exception):
    """
    Throws when trying to pop on a board in the init state
    """

    def __init__(self):
        super().__init__("Cannot pop from this board")


class IllegalBoardSizeException(Exception):
    """
    Thrown when trying to construct an illegal BoardSize
    """

    def __init__(self, size: int):
        super().__init__(f"board of size {size} are not possible")


class BoardSize(Enum):
    """
    Available board sizes.
    """

    SIX_BY_SIX = 6
    EIGHT_BY_EIGHT = 8
    TEN_BY_TEN = 10
    TWELVE_BY_TWELVE = 12

    @staticmethod
    def from_value(value: int) -> BoardSize:
        """
        Converts an integer value to the corresponding BoardSize member if and only if it is valid.
        :params value: The value we are trying to convert to a BoardSize member
        :returns: A BoardSize member with the corresponding value if it is a legal value
        :raises: IllegalBoardSizeException on illegal board size value
        """
        reversed_dep = {bs.value: bs for bs in BoardSize}
        if value in reversed_dep:
            return reversed_dep[value]
        raise IllegalBoardSizeException(value)


class OthelloBoard:
    """
    Implementation of an othello board that uses Bitboards
    """

    def __init__(
        self,
        size: BoardSize,
        black=None,
        white=None,
        current_player: Color | None = None,
    ):
        """
        :param size: The size of the Bitboard from the enum `BoardSize`
        :param type: BoardSize
        """
        logger.debug(
            "Initializing OthelloBoard in othello_board.py, with size: %s", size.value
        )
        self.size = size
        self.current_player: Color = (
            Color.BLACK if current_player is None else current_player
        )
        logger.debug("   Current player set to: %s", self.current_player)
        if black is not None and white is not None:
            logger.debug("   Using provided black and white bitboards")
            if self.size.value != black.size or self.size.value != white.size:
                error_msg = f"Provided bitboards size mismatch. Board size: {self.size.value}, \
                Black size: {black.size}, White size: {white.size}"
                logger.error(error_msg)
                raise IllegalBoardSizeException(
                    black.size.value if self.size.value != black.size else white.size
                )
            self.black = black
            self.white = white
        else:
            logger.debug("   Creating new bitboards.")
            self.black = Bitboard(size.value)
            self.white = Bitboard(size.value)
            # we copy a mask from one of our bitboards as they are equals and immutables
            self.__init_board()
        self.mask = self.black.mask
        logger.debug("Board mask initialized: %d.", self.mask)
        self.__history: list[tuple[Bitboard, Bitboard, int, int, Color]] = []
        self.forced_game_over = False

    def __init_board(self):
        """
        Initialize the starting position of the Othello board.

        This method sets up the initial four pieces in the center of the board,
        with two black pieces and two white pieces placed diagonally from each other.
        """
        logger.debug("Initializing starting board position.")
        self.white.set(self.size.value // 2 - 1, self.size.value // 2 - 1, True)
        self.white.set(self.size.value // 2, self.size.value // 2, True)
        self.black.set(self.size.value // 2 - 1, self.size.value // 2, True)
        self.black.set(self.size.value // 2, self.size.value // 2 - 1, True)

    def force_game_over(self):
        """
        Force the game to be over.
        """
        logger.debug("Game over forced by external call.")
        self.forced_game_over = True

    def is_game_over(self) -> bool:
        """
        Checks whether or not a board is in a game over state.
        """
        logger.debug("Checking if game is over in othello_board.py.")
        move_1, move_2 = (
            self.line_cap_move(self.current_player),
            self.line_cap_move(~self.current_player),
        )
        return self.forced_game_over or (
            not move_1.popcount() and not move_2.popcount()
        )

    def shift_along(self, bits_o, bits_p):
        """
        inlining of the shift from bitboard in order to gain ALOT of speed
        """
        size = self.size.value
        mask = self.black.mask
        west_mask = self.black.west_mask
        east_mask = self.black.east_mask

        empty_bits = (~(bits_p | bits_o)) & mask

        moves_bits = 0

        # define all shift operations as inline functions
        tmp = bits_o & ((bits_p >> size) & mask)
        while tmp:
            moves_bits |= empty_bits & ((tmp >> size) & mask)
            tmp = bits_o & ((tmp >> size) & mask)
        tmp = bits_o & ((bits_p << size) & mask)
        while tmp:
            moves_bits |= empty_bits & ((tmp << size) & mask)
            tmp = bits_o & ((tmp << size) & mask)
        tmp = bits_o & (((bits_p << 1) & west_mask) & mask)
        while tmp:
            moves_bits |= empty_bits & (((tmp << 1) & west_mask) & mask)
            tmp = bits_o & (((tmp << 1) & west_mask) & mask)
        tmp = bits_o & (((bits_p >> 1) & east_mask) & mask)
        while tmp:
            moves_bits |= empty_bits & (((tmp >> 1) & east_mask) & mask)
            tmp = bits_o & (((tmp >> 1) & east_mask) & mask)
        tmp = bits_o & (((bits_p >> (size - 1)) & west_mask) & mask)
        while tmp:
            moves_bits |= empty_bits & (((tmp >> (size - 1)) & west_mask) & mask)
            tmp = bits_o & (((tmp >> (size - 1)) & west_mask) & mask)
        tmp = bits_o & (((bits_p >> (size + 1)) & east_mask) & mask)
        while tmp:
            moves_bits |= empty_bits & (((tmp >> (size + 1)) & east_mask) & mask)
            tmp = bits_o & (((tmp >> (size + 1)) & east_mask) & mask)
        tmp = bits_o & (((bits_p << (size + 1)) & west_mask) & mask)
        while tmp:
            moves_bits |= empty_bits & (((tmp << (size + 1)) & west_mask) & mask)
            tmp = bits_o & (((tmp << (size + 1)) & west_mask) & mask)
        tmp = bits_o & (((bits_p << (size - 1)) & east_mask) & mask)
        while tmp:
            moves_bits |= empty_bits & (((tmp << (size - 1)) & east_mask) & mask)
            tmp = bits_o & (((tmp << (size - 1)) & east_mask) & mask)
        return moves_bits

    def line_cap_move(self, current_player: Color) -> Bitboard:
        """
        Returns a bitboard of the possibles plays for `current_player`
        Overrides the bitboard conveniance class for performances concerns
        :param current_player: The player trying to do the capture
        :returns: A Bitboard of the possible capture moves for player `current_player`
        """
        bits_p = self.black.bits if current_player is Color.BLACK else self.white.bits
        bits_o = self.white.bits if current_player is Color.BLACK else self.black.bits

        moves_bits = self.shift_along(bits_o, bits_p)
        return Bitboard(self.size.value, moves_bits)

    def line_cap_move_(self, current_player: Color) -> Bitboard:
        """
        Returns a bitboard of the possibles plays for `current_player`

        :param current_player: The player trying to do the capture
        :returns: A Bitboard of the possible capture moves for player `current_player`
        """
        bits_p = self.black if current_player is Color.BLACK else self.white
        bits_o = self.white if current_player is Color.BLACK else self.black
        moves = Bitboard(self.size.value)
        for shift_dir in Direction:
            candidates = bits_o & (bits_p.shift(shift_dir))
            while candidates.bits:
                moves |= self.__empty_mask() & candidates.shift(shift_dir)
                candidates = bits_o & candidates.shift(shift_dir)
        return moves

    def get_turn_id(self) -> int:
        """
        Returns current turn id.
        There are two moves (one for each player, empty move allowed) in a turn.
        Black first then White. Empty plays are still recorded
        :returns: The turn id starting from 1.
        :rtype: int
        """
        return len(self.__history) // 2 + 1

    def get_last_play(self):
        """
        Returns the last played move.

        Returns:
            tuple[Bitboard, Bitboard, int, int, Color]: last played move.
        """
        if not self.__history:
            return None
        last_play, last_play_idx = self.__history[-1], 0
        while last_play[2] == -1 and last_play[3] == -1:
            last_play_idx += 1
            last_play = self.__history[-last_play_idx]
        return last_play

    def line_cap(self, x_coord: int, y_coord: int, current_player: Color) -> Bitboard:
        """
        Returns the result of a capture. Does not check if the capture is legal.
        Do the check beforehand if you intend to use this function.

        :param x_coord: the x coordinate of the play
        :param y_coord: the y coordinate of the play
        :param current_player: the player making the move
        :returns: The bitboard of the captured bits.
        :rtype: Bitboard
        """
        bits_p = self.black if current_player is Color.BLACK else self.white
        bits_o = self.white if current_player is Color.BLACK else self.black
        position = Bitboard(self.size.value)
        position.set(x_coord, y_coord, True)
        cap_mask = Bitboard(self.size.value, bits=position.bits)
        for shift_dir in Direction:
            direction_mask = Bitboard(self.size.value, position.bits)
            direction_ptr = Bitboard(self.size.value, position.bits)

            while True:
                # we can while True as we always ends up falling either in the elif
                # or the else condition
                direction_ptr = direction_ptr.shift(shift_dir)
                if (direction_ptr & bits_o).bits:
                    direction_mask |= direction_ptr
                elif (direction_ptr & bits_p).bits:
                    cap_mask |= direction_mask
                    break
                else:
                    break

        return cap_mask

    def pop(self):
        """
        Pops the last played move, if last move is (-1, -1), it pops 2 times to pop a real move.
        """
        if len(self.__history) <= 0:
            raise CannotPopException()

        popped = self.__history.pop()
        if popped[2] == -1 and popped[3] == -1:
            popped = self.__history.pop()
        self.black = popped[0]
        self.white = popped[1]
        self.current_player = popped[4]

    def play(self, x_coord: int, y_coord: int):
        """
        Changes the state of the Board, pushing the move at x_coord;y_coord if it is a legal play.
        """
        if x_coord == -1 and y_coord == -1:
            logger.debug("Player %s passes their turn.", self.current_player)
            self.__history.append((self.black, self.white, -1, -1, self.current_player))
        else:
            legal_moves = self.line_cap_move(self.current_player)
            move_mask = Bitboard(self.size.value)
            move_mask.set(x_coord, y_coord, True)
            if (legal_moves & move_mask).bits > 0:
                logger.debug("Move (%s, %s) is legal.", x_coord, y_coord)
                capture_mask = self.line_cap(x_coord, y_coord, self.current_player)
                state_to_save = (
                    self.black,
                    self.white,
                    x_coord,
                    y_coord,
                    self.current_player,
                )
                self.__history.append(state_to_save)
                logger.debug(
                    "Move saved to history, history length: %s.", len(self.__history)
                )
                bits_p = (
                    self.black if self.current_player is Color.BLACK else self.white
                )
                bits_o = (
                    self.white if self.current_player is Color.BLACK else self.black
                )
                bits_p |= capture_mask
                bits_o &= ~capture_mask
                self.black = bits_p if self.current_player is Color.BLACK else bits_o
                self.white = bits_o if self.current_player is Color.BLACK else bits_p
                logger.debug(
                    "Switching current player from %s to %s",
                    self.current_player,
                    ~self.current_player,
                )
                self.current_player = ~self.current_player
                if not self.line_cap_move(self.current_player).bits:
                    logger.debug(
                        "Player %s has no legal moves and must pass.",
                        self.current_player,
                    )
                    self.__history.append(
                        (self.black, self.white, -1, -1, self.current_player)
                    )
                    self.current_player = ~self.current_player
                    logger.debug(
                        "Switching current player back to %s.", self.current_player
                    )
            else:
                logger.error("Move is illegal.")
                raise IllegalMoveException(x_coord, y_coord, self.current_player)

    def get_history(self):
        """
        Returns a copy of the game history
        :returns: the game history
        :rtype: tuple
        """
        return copy(self.__history)

    @staticmethod
    def move_to_str(move):
        """
        Converts a move tuple to a string matching the save file format

        :param move: a move tuple
        :type move: tuple
        :returns: the string representation of the move
        :rtype: str
        """
        if move[2] == -1 and move[3] == -1:
            return "-1-1"
        return f"{chr(ord('a') + move[2])}{move[3] + 1}"

    def export_board(self) -> str:
        """
        Returns a string representation of the board matching the save file format

        :returns: the board string representation
        :rtype: str
        """
        logger.debug(
            "Exporting board to string format in export_board form othello_board.py."
        )
        export_str = f"# board\n{self.current_player.value}\n"
        for coord_y in range(self.size.value):
            for coord_x in range(self.size.value):
                if self.black.get(coord_x, coord_y):
                    export_str += Color.BLACK.value
                elif self.white.get(coord_x, coord_y):
                    export_str += Color.WHITE.value
                else:
                    export_str += Color.EMPTY.value
                if coord_x < self.size.value - 1:
                    export_str += " "
            if coord_y < self.size.value - 1:
                export_str += "\n"
        return export_str

    def export_history(self):
        """
        Returns a string representation of the history of the game matching the save file format.

        :returns: the history string representation
        :rtype: str
        """
        logger.debug("Exporting history to string format in export.")
        export_str = "# history\n"
        for move_index, move in enumerate(self.__history):
            if move[4] is Color.BLACK:
                move_str = OthelloBoard.move_to_str(move)
                export_str += f"{move_index // 2 + 1}. X {move_str}"
            else:
                if not move_index & 1:
                    export_str += f"{move_index // 2 + 1}. X -1-1"
                move_str = OthelloBoard.move_to_str(move)
                export_str += f" O {move_str}"
                export_str += "\n"
        return export_str

    def export(self) -> str:
        """
        Returns a string representation of the whole game state (board + history)
        matching the save file format

        :returns: the string representation
        :rtype: str
        """
        return f"{self.export_board()}\n{self.export_history()}"

    def restart(self):
        """
        Resets the state of the game to a starting one with the same size.
        """
        logger.debug("Restarting game with board size %d.", self.size.value)
        self.__history = []
        self.black = Bitboard(self.size.value)
        self.white = Bitboard(self.size.value)
        self.current_player = Color.BLACK
        self.__init_board()
        logger.debug("Game successfully restarted.")

    def __empty_mask(self) -> Bitboard:
        """
        Compute a bitboard that represents all the empty squares on the board.

        The empty mask is the XOR of the white and black bitboards with the mask
        of the board. This is equivalent to finding all the squares that have not
        been set to either white or black.

        :return: A bitboard representing all the empty squares on the board.
        :rtype: Bitboard
        """
        return Bitboard(
            self.size.value, (self.white.bits | self.black.bits) ^ self.mask
        )

    def __hash__(self) -> int:
        return hash((self.current_player, self.black, self.white))

    def __eq__(self, other) -> bool:
        if isinstance(other, OthelloBoard):
            return (
                other.current_player == self.current_player
                and other.black == self.black
                and other.white == self.white
            )

        return False

    def __str__(self) -> str:
        """
        Returns a string representation of a bitboard
        """
        size_toggle_space = 10
        height_toggle_space = 9
        rez = "  "
        if self.size.value >= size_toggle_space:
            rez += " "

        rez += " ".join(
            [ascii_lowercase[letter_idx] for letter_idx in range(self.size.value)]
        )
        for y_coord in range(self.size.value):
            rez += "\n"
            for x_coord in range(self.size.value):
                has_black = self.black.get(x_coord, y_coord)
                has_white = self.white.get(x_coord, y_coord)
                has_possible = self.line_cap_move(self.current_player).get(
                    x_coord, y_coord
                )
                if not x_coord:
                    rez += str(y_coord + 1) + " "
                    if (
                        self.size.value >= size_toggle_space
                        and y_coord < height_toggle_space
                    ):
                        rez += " "
                if has_black:
                    rez += Color.BLACK.value
                elif has_white:
                    rez += Color.WHITE.value
                elif has_possible:
                    rez += Color.POSSIBLE.value
                else:
                    rez += Color.EMPTY.value
                if x_coord < self.size.value - 1:
                    rez += " "
        return rez
