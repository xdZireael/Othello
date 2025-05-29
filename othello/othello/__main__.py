"""
Entry point for the othello executable.
"""

import logging

import othello
from othello.board_parser import BoardParser
from othello import parser
import othello.logger as log
from othello.gui import OthelloGUI
from othello.cli import OthelloCLI
from othello.othello_board import BoardSize, OthelloBoard
from othello.controllers import (
    AIPlayer,
    GameController,
    HumanPlayer,
    RandomPlayer,
)
from othello.config import display_config


def main():
    """
    Entry point for the Othello game.

    The main function is responsible for handling the game loop based on the
    provided command line arguments. It will parse the arguments, set up the
    game mode, and start the game loop.

    The game loop will print the current state of the board, the current player,
    and the valid moves for that player. It will then ask the player for input,
    and attempt to make the move. If the move is invalid, it will ask again.
    If the move is valid, it will update the board and switch to the other player.

    The game loop will continue until the game is over, or the user quits.

    Args:
        None
    """
    mode, config = parser.parse_args()

    log.logging_config(config["debug"])
    logger = logging.getLogger("Othello")

    logger.debug("Start of a Othello game.")
    logger.debug("Debug mode is enabled.")
    logger.debug("Game mode: %s", mode)

    current_config = parser.default_config.copy()
    current_config.update(config)

    display_config(config)

    controller = None

    board = None

    # first we try to retrieve a save from given filename if it exists
    if (filename := config["filename"]) is None:
        board = OthelloBoard(BoardSize.from_value(config["size"]))
    else:
        try:
            with open(filename, "r", encoding="utf-8") as file:
                file_content = file.read()
            board = BoardParser(file_content).parse()
        except FileNotFoundError:
            context = f"File not found: {filename}"
            log.log_error_message(FileNotFoundError, context=context)
            raise
        except Exception as err:
            log.log_error_message(err, context="Failed to load game.")
            raise

    # then we setup black and white, specifying if they are AI players or not
    if config["benchmark"]:
        # In benchmark mode, we can have different configurations for each player
        if config["ai_color"] == "B":  # Both players with separate configs
            black_player = AIPlayer(
                board,
                config["ai_depth"],
                config["ai_mode"],
                config["ai_heuristic"],
                benchmark=True,
            )
            white_player = AIPlayer(
                board,
                config["white_ai_depth"],
                config["white_ai_mode"],
                config["white_ai_heuristic"],
                benchmark=True,
            )
        elif config["ai_color"] == "A":  # Both players with same config
            black_player = AIPlayer(
                board,
                config["ai_depth"],
                config["ai_mode"],
                config["ai_heuristic"],
                benchmark=True,
            )
            white_player = AIPlayer(
                board,
                config["ai_depth"],
                config["ai_mode"],
                config["ai_heuristic"],
                benchmark=True,
            )
        elif config["ai_color"] == "X":  # AI as black, random as white
            black_player = AIPlayer(
                board,
                config["ai_depth"],
                config["ai_mode"],
                config["ai_heuristic"],
                benchmark=True,
            )
            white_player = RandomPlayer()
        elif config["ai_color"] == "O":  # AI as white, random as black
            black_player = RandomPlayer()
            white_player = AIPlayer(
                board,
                config["ai_depth"],
                config["ai_mode"],
                config["ai_heuristic"],
                benchmark=True,
            )
    else:
        black_player = (
            AIPlayer(
                board,
                config["ai_depth"],
                config["ai_mode"],
                config["ai_heuristic"],
                benchmark=True,
            )
            if mode == parser.GameMode.AI.value and config["ai_color"] == "X"
            else HumanPlayer()
        )
        white_player = (
            AIPlayer(
                board,
                config["ai_depth"],
                config["ai_mode"],
                config["ai_heuristic"],
                benchmark=True,
            )
            if mode == parser.GameMode.AI.value and config["ai_color"] == "O"
            else HumanPlayer()
        )

    # [Rest of the main function remains the same...]

    logger.debug(f"   Black player is of class {black_player.__class__}.")
    logger.debug(f"   White player is of class {white_player.__class__}.")

    # then we setup the game controller depenging of the gamemode given
    controller = (
        GameController(board, black_player, white_player, True, config["blitz_time"])
        if mode == parser.GameMode.BLITZ.value
        else GameController(board, black_player, white_player)
    )

    # finally, we run either in gui or in cli
    if config["gui"]:
        logger.debug("Starting graphical user interface.")
        gui = OthelloGUI(controller)
        gui.run()
    else:
        print(othello.__ascii_art__)
        logger.debug("Starting command line user interface.")
        cli = OthelloCLI(controller, controller.is_blitz())
        cli.play()


if __name__ == "__main__":
    main()
