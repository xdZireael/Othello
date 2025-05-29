"""Game Modes for Othello"""

import logging

from othello.command_parser import CommandParser, CommandKind, CommandParserException
from othello.config import save_board_state_history
from othello.othello_board import Color
from othello.controllers import (
    GameController,
)


logger = logging.getLogger("Othello")


class OthelloCLI:
    """
    A class representing a Normal Othello game.
    """

    NB_PLAYS_IN_HISTORY = 5
    parser: CommandParser

    def __init__(
        self,
        controller: GameController,
        blitz_mode: bool = False,
    ):
        # Initialize the base board first
        self.controller = controller
        self.blitz_mode = blitz_mode
        self.running = False

        logger.debug(
            "CLI initialized, current_player: %s.", self.controller.get_current_player()
        )

    def display_board(self):
        """
        Display the current state of the board and indicate the current player's turn.

        This function prints a string representation of the Othello board and
        indicates which player's turn it is by displaying the player's name
        and corresponding symbol.
        """
        logger.debug("Entering display_board function from cli.py.")
        print(str(self.controller))
        print(
            f"\n{self.controller.get_current_player().name}'s turn "
            f"({self.controller.get_current_player().value})"
        )

    def check_game_over(self, possible_moves):
        """
        Checks if the game is over by delegating to the board's is_game_over method.
        If the game is over, prints the appropriate game over message and final score.

        :param possible_moves: A bitboard of the possible capture moves for the current player.
        :type possible_moves: Bitboard
        :return: True if the game is over, False otherwise.
        :rtype: bool
        """
        logger.debug("Entering check_game_over function from cli.py.")

        if self.controller.is_game_over:
            logger.debug("Game over condition detected.")

            # Print final score
            black_score = self.controller.popcount(Color.BLACK)
            white_score = self.controller.popcount(Color.WHITE)
            logger.debug(
                "   Final score - Black: %s, White: %s", black_score, white_score
            )
            print(f"Final score - Black: {black_score}, White: {white_score}")
            print(self.controller.game_over_message)

            return True

        # If no moves for current player but game isn't over (other player can still move)
        if not possible_moves.bits:
            logger.debug(
                "   No moves available for %s player. Skipping turn.",
                self.controller.get_current_player(),
            )
            print(
                f"No valid moves for {self.controller.get_current_player().name}. Skipping turn."
            )

        return False

    def display_possible_moves(self, possible_moves):
        """
        Prints the possible moves in a human-readable format.

        The function takes a bitboard of possible moves and prints it
        in a human-readable format. The format is a series of letters
        and numbers, where each letter corresponds to a column and
        each number corresponds to a row. For example, the coordinate
        "a1" would correspond to the top-left corner of the board.

        :param possible_moves: A bitboard of the possible capture moves for the current player.
        :type possible_moves: Bitboard
        """
        logger.debug(
            "Entering display_possible_moves function from cli.py,"
            " with parameter possible_moves."
        )
        logger.debug("   Available moves:\n%s", str(possible_moves))
        print("Possible moves: ")
        for y_coord in range(self.controller.size.value):
            for x_coord in range(self.controller.size.value):
                if possible_moves.get(x_coord, y_coord):
                    print(f"{chr(ord('a') + x_coord)}{y_coord + 1}", end=" ")
        print()

    @staticmethod
    def get_player_move():
        """
        Prompts the current player to enter their move.

        This function reads the player's move input in the format of a letter
        followed by a number (e.g., "a1"). It converts the input into x and y
        coordinates, where 'a' corresponds to 0 and '1' corresponds to 0, and
        returns these coordinates.

        :return: A tuple containing the x and y coordinates of the move.
        :rtype: tuple[int, int]
        """
        logger.debug("Entering get_player_move function from cli.py.")
        move = input("Enter your move: ").strip().lower()
        logger.debug("   Player entered: %s", move)

        x_coord = ord(move[0]) - ord("a")
        y_coord = int(move[1]) - 1
        return x_coord, y_coord

    def process_move(self, x_coord, y_coord, possible_moves):
        """
        Processes a move by the current player at the given coordinates.

        This function checks if the move at the specified coordinates is legal by
        consulting the possible moves bitboard. If the move is legal, it plays the
        move on the board. If the move is not legal, it prints an error message
        indicating the move is invalid.

        :param x_coord: The x coordinate of the move.
        :param y_coord: The y coordinate of the move.
        :param possible_moves: A bitboard of the possible capture moves for the current player.
        :type x_coord: int
        :type y_coord: int
        :type possible_moves: Bitboard
        """
        logger.debug(
            "Entering process_move function from cli.py, with parameters x_coord:"
            "%s, y_coord: %s, and possible_moves.",
            x_coord,
            y_coord,
        )
        if not possible_moves.get(x_coord, y_coord):
            logger.debug("   The move is not legal to play")
            print("Invalid move. Not a legal play. Try again.")
            return False
        logger.debug("   Move (%s, %s) is legal, playing.", x_coord, y_coord)
        self.controller.play(x_coord, y_coord)
        return True

    def check_parser_input(self, command_str, command_kind, *args):
        """
        Checks if the given command from the parser is valid and executes it.

        If the command is invalid, it prints an error message and prompts the
        player again. If the command is valid, it processes the move and switches
        the player. If the player has won, it prints a message and exits.

        :param command_str: The command string from the parser.
        :param command_kind: The type of command.
        :param args: Additional arguments from the parser.
        :type command_str: str
        :type command_kind: CommandKind
        :type args: tuple
        """
        logger.debug(
            "Entering check_parser_input function from cli.py, with parameters"
            " command_str: %s, command_kind, and args."
        )
        if command_kind == CommandKind.PLAY_MOVE:
            play_command = args[0]
            x_coord, y_coord = play_command.x_coord, play_command.y_coord
            logger.debug("   Play move command at (%s, %s).", x_coord, y_coord)

            if not self.process_move(
                x_coord,
                y_coord,
                self.controller.get_possible_moves(
                    self.controller.get_current_player()
                ),
            ):
                logger.debug("   The move is not legal.")
                print("Invalid move. Try again.")
                return

        else:
            match command_kind:
                case CommandKind.HELP:
                    logger.debug("   Executing %s command.", command_kind)
                    self.parser.print_help()
                case CommandKind.RULES:
                    logger.debug("   Executing %s command.", command_kind)
                    CommandParser.print_rules()
                case CommandKind.SAVE_AND_QUIT:
                    logger.debug("   Executing %s command.", command_kind)
                    save_board_state_history(self.controller)
                    logger.debug("   Game saved, exiting.")
                    self.running = False
                case CommandKind.SAVE_HISTORY:
                    logger.debug("   Executing %s command.", command_kind)
                    save_board_state_history(self.controller, only_hist=True)
                case CommandKind.FORFEIT:
                    logger.debug(
                        "   %s executed %s command.",
                        self.controller.get_current_player().name,
                        command_kind,
                    )
                    print(f"{self.controller.get_current_player().name} forfeited.")
                    winner = (~self.controller.get_current_player()).name
                    logger.debug(
                        "   Game Over, %s wins! Exiting.",
                        winner,
                    )
                    print(f"Game Over, {winner} wins!")
                    self.running = False
                case CommandKind.RESTART:
                    logger.debug("   Executing %s command.", command_kind)
                    self.controller.restart()
                    self.play()
                    logger.debug("   Board restarted to initial state")
                case CommandKind.QUIT:
                    logger.debug("   Executing %s command.", command_kind)
                    print("Exiting without saving...")
                    self.running = False
                case _:
                    logger.debug("   Invalid command: %s.", command_str)
                    print("Invalid command. Try again.")
                    self.parser.print_help()

    def display_history(self):
        """
        Displays the last self.NB_PLAYS_IN_HISTORY turns
        """
        logger.debug("Entering display history function from cli.py.")
        to_print = "Play history:\n" + "\n".join(
            [
                f"{play[4]} placed a piece at {chr(ord('A') + play[2])}{play[3] + 1}"
                for play in self.controller.get_history()[-self.NB_PLAYS_IN_HISTORY :]
            ]
        )
        print(to_print, "\n")

    def play(self):
        """
        Starts the game loop for Normal mode.

        This function starts the main game loop. The loop begins by displaying
        the current state of the board. It then prompts the current player for
        input. The input is parsed into a CommandType, which is a tuple of a
        CommandKind and some relevant information for that kind. The function
        then processes the command based on the kind.

        The loop continues until the game is over, or the user quits.
        """
        logger.debug("Entering play function from cli.py.")
        self.parser = CommandParser(board_size=self.controller.size.value)

        possible_moves = self.controller.get_possible_moves(
            self.controller.get_current_player()
        )

        def human_play_callback():
            if self.blitz_mode:
                print(self.controller.display_time())
            command_str = input("Enter your move or command: ").strip()
            logger.debug("   Player input: '%s'.", command_str)
            try:
                command_kind, *args = self.parser.parse_str(command_str)
                self.check_parser_input(command_str, command_kind, *args)

            except CommandParserException as err:
                print(f"Error: {err}\nInvalid command. Please try again.")
                self.parser.print_help()

        def turn_display():
            print(f"=== turn {self.controller.get_turn_number()} ===")
            self.display_history()
            self.display_board()
            possible_moves = self.controller.get_possible_moves(
                self.controller.get_current_player()
            )
            self.display_possible_moves(possible_moves)

        self.controller.human_play_callback = human_play_callback
        self.controller.post_play_callback = turn_display
        turn_display()

        self.running = True

        while self.running:
            if self.check_game_over(possible_moves):
                self.running = False
            else:
                self.controller.next_move()
