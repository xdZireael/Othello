"""CONFIG FILE

This module manages the configuration for the Othello game.

Configuration Options:
    - mode: normal/blitz/contest/ai
    - filename: save.feur/None
    - size: 6/8/10/12
    - debug: false/true
    - blitz_time: 30/X (minutes)
    - ai_color: X/O/A
    - ai_mode: minimax/alphabeta
    - ai_shallow: true/false
    - ai_depth: 3/X (root_depth = 0)
    - ai_heuristic: default/custom
    - ai_time: 5/X (seconds)
"""

import sys
import logging

from othello.controllers import GameController
import othello.logger as log

logger = logging.getLogger("Othello")
SEPARATOR = "="


def save_config(config: dict, filename_prefix: str = "current_config") -> None:
    """Save configuration into a .othellorc file."""
    logger.debug(
        "Saving configuration: %s with filename_prefix: %s", config, filename_prefix
    )
    filename = f"{filename_prefix}.othellorc"

    try:
        file_content = "\n".join(
            f"{key}{SEPARATOR}{str(value).lower() if isinstance(value, bool) else value}"
            for key, value in config.items()
        )
    except Exception as err:
        log.log_error_message(err, "Failed to format configuration.")
        raise

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(file_content)
    except IOError as err:
        log.log_error_message(err, context="Error while saving configuration.")
        raise

    logger.debug("Configuration saved successfully with %d entries.", len(config))


def load_config(filename_prefix: str = "current_config") -> dict:
    """Load a configuration from a .othellorc file."""
    logger.debug("Loading configuration with filename_prefix: %s", filename_prefix)
    filename = f"{filename_prefix}.othellorc"
    config = {}

    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError as err:
        log.log_error_message(err, context="No configuration file found.")
        raise

    try:
        for line in lines:
            if SEPARATOR in line:
                key, value = line.strip().split(SEPARATOR, 1)
                config[key] = value
    except ValueError as err:
        log.log_error_message(err, "Invalid configuration format.")
        raise

    return config


def save_board_state_history(
    controller: GameController, filename_prefix=None, only_hist=False
) -> None:
    """Save the board state history into a .othellorc file."""
    logger.debug("Saving board state history to filename_prefix: %s", filename_prefix)
    if filename_prefix is None:
        while True:
            try:
                # checking if file is "legal"
                filename_prefix = input("enter save file name: ")
                open(filename_prefix + ".sav", "w", encoding="utf-8")
                break
            except Exception as err:
                print(f"Couldn't use {filename_prefix}.sav: {err}")
    filename = f"{filename_prefix}.sav"

    try:
        with open(filename, "w", encoding="utf-8") as file:
            if only_hist:
                file.write(controller.export_history())
            else:
                file.write(controller.export())
        print(f"Game saved in {filename_prefix}.sav")
    except IOError as err:
        log.log_error_message(
            str(err), context=f"Failed to save board state to {filename}."
        )
        raise

    logger.debug(
        "%s state successfully saved to %s",
        "History" if only_hist else "Board",
        filename,
    )


def display_config(config: dict) -> None:
    """Display the configuration."""
    logger.debug("Displaying configuration: %s", str(config))

    if not isinstance(config, dict):
        logger.error("Expected a dictionary.")
        sys.stderr.write("Error: Expected a dictionary.\n")
        sys.exit(1)

    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
