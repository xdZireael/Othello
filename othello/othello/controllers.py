"""Controllers for the Othello game."""

from __future__ import annotations


import logging
from random import choice
import time

from othello.ai_features import find_best_move
from othello.othello_board import (
    Color,
    OthelloBoard,
)
from othello.blitz_timer import BlitzTimer
from othello.parser import DEFAULT_BLITZ_TIME

logger = logging.getLogger("Othello")


class Player:
    """
    Base class for a player in the game.
    """

    def __init__(self):
        """
        Player initialization.
        """
        self.controller = None
        self.color = None

    def attach(self, controller: GameController):
        """
        Attach a game controller to the player.

        :param controller: The game controller to attach
        :type controller: GameController
        """
        self.controller = controller

    def set_color(self, color: Color):
        """
        Set the color for this player.

        :param color: The color to assign to this player (BLACK or WHITE)
        :type color: Color
        """
        self.color = color

    def next_move(self):
        """
        Base method for determining the next move.
        Implemented by subclasses.
        """


class HumanPlayer(Player):
    """
    Player class representing a human player.
    Triggers the human play callback when it's time to make a move.
    """

    def next_move(self):
        """
        Signal that it's time for the human player to make a move.
        Calls the human_play_callback if it has been set in the controller.

        :raises Exception: if the controller is not defined.
        """
        if self.controller is not None:
            if self.controller.human_play_callback is not None:
                self.controller.human_play_callback()


class RandomPlayer(Player):
    """
    Player class that makes random moves selected from available legal moves.
    """

    def next_move(self):
        """
        Choose a random legal move and play it on the board.
        """
        if self.controller is not None and self.color is not None:
            move = choice(
                self.controller.get_possible_moves(self.color).hot_bits_coordinates()
            )
            self.controller.play(move[0], move[1])


class AIPlayer(Player):
    """
    Player class that uses AI algorithms to determine the next move.
    """

    def __init__(
        self,
        board: OthelloBoard,
        depth: int = 3,
        algorithm: str = "minimax",
        heuristic: str = "coin_parity",
        benchmark: bool = False,
    ):
        """
        Initialize an AI player.

        :param board: The Othello game board
        :type board: OthelloBoard
        :param depth: The depth of the search algorithm, defaults to 3
        :type depth: int, optional
        :param algorithm: The search algorithm to use, defaults to "minimax"
        :type algorithm: str, optional
        :param heuristic: The heuristic function to evaluate board positions,
            defaults to "coin_parity"
        :type heuristic: str, optional
        """
        super().__init__()
        self.board = board
        self.depth = depth
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.benchmark = benchmark

    def next_move(self):
        """
        Determine the best move using specified AI algorithm and heuristic,
        then play it on the board.

        :raises Exception: if the controller is not defined
        """
        if self.benchmark:
            start_time = time.time()  # Start timer

        if self.controller is not None:
            move = find_best_move(
                self.board, self.depth, self.color, self.algorithm, self.heuristic
            )
            self.controller.play(move[0], move[1])

        if self.benchmark:
            end_time = time.time()  # End timer
            execution_time = end_time - start_time
            print(f"Execution time: {execution_time:.4f} seconds")


class GameController:
    """
    Initialize the game controller.

    :param board: The Othello game board
    :param blitz_mode: If True, the game is in blitz mode and the time limit is used
    :param time_limit: The time limit for blitz mode
    """

    def __init__(
        self,
        board: OthelloBoard,
        black_player,
        white_player,
        blitz_mode=False,
        time_limit=0,
    ):
        """
        Initialize the game controller.

        :param board: The Othello game board
        :param blitz_mode: If True, the game is in blitz mode and the time limit is used
        :param time_limit: The time limit for blitz mode
        """
        logger.debug("Initializing controller in GameController, from controllers.py.")
        self._board = board
        self.size = board.size
        self.first_player_human = True
        self.post_play_callback = None
        self.blitz = None
        if blitz_mode:
            self.blitz = BlitzTimer(time_limit)
            self.blitz.start_timer("black")
        self.time_limit = time_limit if time_limit is not None else DEFAULT_BLITZ_TIME
        self.human_play_callback = None
        self.post_play_callback = None
        black_player.attach(self)
        black_player.set_color(Color.BLACK)
        white_player.attach(self)
        white_player.set_color(Color.WHITE)
        self.players = {Color.BLACK: black_player, Color.WHITE: white_player}
        self.is_game_over = False
        self.game_over_message = ""
        self.winner: Color | None
        self.logger = logging.getLogger("Othello")

    def is_blitz(self) -> bool:
        """
        Checks if the game is in blitz mode
        :returns: True if it is the case
        """
        return self.blitz is not None

    def display_time_player(self, p_color: Color) -> str | None:
        """
        Returns the remaining time if available, else None
        """
        if self.blitz is not None:
            return self.blitz.display_time_player(p_color)
        return None

    def next_move(self):
        """
        Call the next_move method of the player whose turn it currently is.
        """
        self.players[self._board.current_player].next_move()

    def _check_for_blitz_game_over(self):
        if self.blitz is not None:
            if self.blitz.is_time_up("black"):
                self.is_game_over = True
                self.winner = Color.WHITE
                self.game_over_message = "Black's time is up! White wins!"
            elif self.blitz.is_time_up("white"):
                self.is_game_over = True
                self.winner = Color.BLACK
                self.game_over_message = "White's time is up! Black wins!"

    def play(self, x_coord: int, y_coord: int):
        """
        Make a move on the board.

        This method changes the state of the board to reflect the move given by
        x_coord and y_coord. If a callback was registered using the
        set_post_play_callback method, it is called after the move is made.

        :param x_coord: The x coordinate of the move (0 indexed)
        :param y_coord: The y coordinate of the move (0 indexed)
        """
        if self.is_game_over:
            self.logger.debug(
                "Tried to play (%d:%d) in a game over game", x_coord, y_coord
            )
            return

        self._check_for_blitz_game_over()
        if not self.is_game_over:
            self._board.play(x_coord, y_coord)
        else:
            return

        if self._board.is_game_over():
            self.is_game_over = True
            black_score = self.popcount(Color.BLACK)
            white_score = self.popcount(Color.WHITE)
            self.logger.debug(
                "Final score - Black: %s, White: %s", black_score, white_score
            )

            if black_score > white_score:
                self.logger.debug("Black wins.")
                self.game_over_message = "Black wins!"
                self.winner = Color.BLACK
            elif white_score > black_score:
                self.logger.debug("White wins.")
                self.game_over_message = "White wins!"
                self.winner = Color.WHITE
            else:
                self.logger.debug("The game is a tie.")
                self.game_over_message = "The game is a tie!"
                self.winner = None

        if self.post_play_callback is not None:
            self.post_play_callback()
        if self.blitz is not None:
            current = "black" if self.get_current_player() == Color.BLACK else "white"
            self.blitz.change_player(current)

    def display_time(self):
        """
        Return displayable time, mostly formatted for CLI and debug
        """
        if self.blitz is not None:
            return self.blitz.display_time()
        return None

    def get_possible_moves(self, player: Color):
        """
        Return a Bitboard of the possible moves for the given player.

        :param player: The player for which to get the possible moves
        :return: A Bitboard of the possible moves for the given player
        """
        return self._board.line_cap_move(player)

    def get_last_play(self):
        """
        Get the coordinates of the last played move.

        :return: A tuple containing the bitboards of each player, the x and y
        coordinates of the last move, and the color of the associated player
        :rtype: tuple[Bitboard, Bitboard, int, int, Color]
        """
        return self._board.get_last_play()

    def popcount(self, color: Color):
        """
        Count the number of pieces of the specified color on the board.

        :param color: The color of pieces to count
        :type color: Color
        :return: The number of pieces of the specified color on the board
        :rtype: int
        """
        return (
            self._board.black.popcount()
            if color is Color.BLACK
            else self._board.white.popcount()
        )

    def get_position(self, player: Color, x_coord: int, y_coord: int):
        """
        Get the state of the specified position on the board for a given player.

        This method checks whether a given board position is occupied by the player's piece.

        :param player: The player whose piece state is being queried.
        :type player: Color
        :param x_coord: The x coordinate of the position on the board (0 indexed).
        :type x_coord: int
        :param y_coord: The y coordinate of the position on the board (0 indexed).
        :type y_coord: int
        :return: True if the player's piece occupies the position, False otherwise.
        :rtype: bool
        """

        to_query = self._board.black if player is Color.BLACK else self._board.white
        return to_query.get(x_coord, y_coord)

    def restart(self):
        """
        Restart the game to its initial state.

        This method resets the game board to the starting configuration,
        clearing any history and setting the current player to the initial player.
        """

        self._board.restart()
        if self.is_blitz():
            del self.blitz
            self.blitz = BlitzTimer(self.time_limit)
            self.blitz.start_timer("black")

    def get_turn_number(self):
        """
        Get the current turn number of the game.

        The turn number is a unique identifier for the current state of the game
        that increments every time a move is made. The first turn is turn number 1,
        and the number increments by one for each subsequent turn.

        :return: The current turn number of the game
        :rtype: int
        """
        return self._board.get_turn_id()

    def get_current_player(self):
        """
        Get the current player.

        This method returns the current player of the game. The first player is
        black, and the second player is white.

        :return: The current player of the game
        :rtype: Color
        """
        return self._board.current_player

    def current_player_is_human(self):
        """
        Check if the current player is a human player.

        :return: True if the current player is a human player, False otherwise
        :rtype: bool
        """
        return isinstance(self.players[self._board.current_player], HumanPlayer)

    def get_pieces_count(self, player_color: Color):
        """
        Get the count of pieces on the board for the given player color.

        This method returns the number of pieces currently on the board
        for the specified player color (black or white).

        :param player_color: The color of the player whose pieces count is to be retrieved.
        :type player_color: Color
        :return: The count of pieces on the board for the specified player color.
        :rtype: int
        """

        return (
            self._board.black.popcount()
            if player_color is Color.BLACK
            else self._board.white.popcount()
        )

    def get_history(self):
        """
        Get the history of the game.

        This method returns a tuple containing the move history of the game. Each
        element of the tuple is a tuple of two elements. The first element is a
        tuple of two integers representing the x and y coordinates of the move,
        and the second element is a Color object representing the player that made
        the move (black or white).

        :return: The history of the game
        :rtype: tuple[tuple[int, int], Color]
        """
        return self._board.get_history()

    def export(self):
        """
        Export the game state to a string.

        This method returns a string representation of the current state of the game,
        including the board and the move history. The returned string is formatted
        according to the Othello save file format.

        :return: The game state as a string
        :rtype: str
        """

        return self._board.export()

    def export_history(self):
        """
        Export the move history of the game to a string.

        This method returns a string representation of the move history of the game,
        formatted according to the Othello save file format.

        :return: The move history of the game as a string
        :rtype: str
        """
        return self._board.export_history()

    def __str__(self):
        """
        Return a string representation of the game state.

        This method returns a string representation of the current state of the game,
        including the board and the move history. The returned string is formatted
        according to the Othello save file format.

        :return: The game state as a string
        :rtype: str
        """
        return str(self._board)
