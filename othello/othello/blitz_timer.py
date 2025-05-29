"""
Implementation of the blitz timer that's used to give both players
a maximum time for all their plays (individually).
"""

from time import time
import logging

from othello.othello_board import Color

logger = logging.getLogger("Othello")


class BlitzTimer:
    """
    BlitzTimer tracks the remaining play time for each player in a timed Othello match.
    """

    def __init__(self, time_limit: int) -> None:
        """
        Initializes a BlitzTimer object.

        Args:
            time_limit (int): The time limit, in minutes.
        """
        logger.debug(
            "Initializing BlitzTimer with time_limit: %d minutes in blitz_timer.py.",
            time_limit,
        )
        self.start_time = None
        self.total_time = time_limit * 60  # Convert minutes to seconds
        self.remaining_time = {"black": self.total_time, "white": self.total_time}
        self.current_player = None
        logger.debug(
            "   BlitzTimer initialized with %d seconds per player.", self.total_time
        )

    def start_timer(self, player: str) -> None:
        """
        Starts the timer for the given player.

        Args:
            player (str): Either 'black' or 'white'.
        """
        logger.debug("Starting timer for player: %s.", player)
        self.start_time = time()
        self.current_player = player

    def pause_timer(self) -> None:
        """
        Pauses the timer and updates the remaining time for the current player.
        """
        if self.start_time and self.current_player:
            elapsed = time() - self.start_time
            base_time = self.remaining_time[self.current_player]
            self.remaining_time[self.current_player] = max(0, base_time - elapsed)
            logger.debug(
                "Timer paused for %s. Elapsed: %.2fs, Remaining: %.2fs.",
                self.current_player,
                elapsed,
                self.remaining_time[self.current_player],
            )
            self.start_time = None
            self.current_player = None
        else:
            logger.debug("Timer not running.")

    def change_player(self, player: str) -> None:
        """
        Switches the timer to a new player.

        Args:
            player (str): Either 'black' or 'white'.
        """
        logger.debug(
            "Changing player from %s to %s in blitz_timer.py.",
            self.current_player,
            player,
        )
        self.pause_timer()
        self.start_timer(player)

    def get_remaining_time(self, player: str) -> float:
        """
        Returns the remaining time for a given player.

        Args:
            player (str): Either 'black' or 'white'.

        Returns:
            float: Remaining time in seconds.
        """
        if self.start_time and player == self.current_player:
            elapsed = time() - self.start_time
            self.start_time = time()
            base_time = self.remaining_time[player]
            self.remaining_time[player] = max(0, base_time - elapsed)
            logger.debug(
                "Updated remaining time for %s: %.2fs (elapsed: %.2fs).",
                player,
                self.remaining_time[player],
                elapsed,
            )
        else:
            logger.debug(
                "Returning cached remaining time for %s: %.2fs.",
                player,
                self.remaining_time[player],
            )
        return self.remaining_time[player]

    def is_time_up(self, player: str) -> bool:
        """
        Checks if a player's time is up.

        Args:
            player (str): Either 'black' or 'white'.

        Returns:
            bool: True if the player's time is up, False otherwise.
        """
        logger.debug("Checking if time is up for player: %s.", player)
        return self.get_remaining_time(player) <= 0

    def time_player(self, player: Color) -> tuple:
        """
        Converts remaining time to minutes and seconds.

        Args:
            player (Color): The player's color.

        Returns:
            tuple: (minutes, seconds).
        """
        logger.debug("Converting time for player: %s.", player)
        total_seconds = int(
            self.get_remaining_time("black" if player is Color.BLACK else "white")
        )
        return divmod(total_seconds, 60)  # Returns (minutes, seconds)

    def display_time_player(self, player: Color) -> str:
        """
        Displays the remaining time for a single player.

        Args:
            player (Color): The player's color.

        Returns:
            str: Time in "MM:SS" format.
        """
        minutes, seconds = self.time_player(player)
        return f"{minutes:02d}:{seconds:02d}"

    def display_time(self) -> str:
        """
        Displays the remaining time for both players.

        Returns:
            str: Time formatted as "Black Time: MM:SS\\nWhite Time: MM:SS".
        """
        logger.debug("Displaying time for both players in blitz_timer.py.")
        black_time = self.display_time_player(Color.BLACK)
        white_time = self.display_time_player(Color.WHITE)

        return f"Black Time: {black_time}\nWhite Time: {white_time}"
