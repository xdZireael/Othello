"""
Logger used for debug mode.
Uses logging to display debug messages and error messages.
"""

import logging
from typing import Any


def logging_config(debug: bool) -> None:
    """
    Set up the logger if the debug mode is enabled.
    Write the log in a file.
    Uncomment the line 'logging.StreamHandler() to have the log written onto the console.

    Argument:
      debug: a boolean used to set the logging level
    """
    if not isinstance(debug, bool):
        raise TypeError()
    if debug:
        level = logging.DEBUG
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                # logging.StreamHandler(),  # Log to the console, uncomment this line if you need it
                logging.FileHandler("othello.log", mode="w")  # Log to a file
            ],
        )


def log_error_message(error: str | Any, context: str | None = None) -> None:
    """
    Log an error message with a given context.

    Arguments:
      error: a string of the error message to be logged
      context: a string describing the context of the error, can be None if no context is given
    """

    logger = logging.getLogger("Othello")
    if context is not None:
        ctxt = f"Context: {context}"
        logger.error(ctxt)
    err = f"Error: {error}"
    logger.error(err, exc_info=True)
