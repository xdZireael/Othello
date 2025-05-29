import logging
import pytest
from unittest.mock import patch, MagicMock

from othello.logger import logging_config, log_error_message


# TEST INITIALIZATION


def test_logger_instance_creation():
    """
    Test that the logger instance created is named 'Othello'
    """
    with patch("logging.getLogger") as mock_get_logger:
        log_error_message(error="Test")
        mock_get_logger.assert_called_once_with("Othello")


def test_init_with_debug():
    """
    Test the logging_config function with debug mode enabled.
    It should configure logging to use basicConfig with debug level and write logs to a file.
    """
    with patch("logging.basicConfig") as mock_basic_config:
        logging_config(debug=True)
        mock_basic_config.assert_called_once()
        _, kwargs = mock_basic_config.call_args

        assert kwargs["level"] == logging.DEBUG
        assert kwargs["handlers"][0].baseFilename.endswith("othello.log")


def test_initialization_without_debug():
    """
    Test the logging_config function with debug mode disabled.
    It should not do anything.
    """
    with patch("logging.basicConfig") as mock_basic_config:
        logging_config(debug=False)

        # no calling to 'basic_config'
        mock_basic_config.assert_not_called()


# TEST DEBUG OUTPUT


# debug message
def test_debug_output_in_file():
    """
    Test that a debug message is properly written in the log file.
    """
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Set up debug mode
        logging_config(debug=True)

        # Get logger and send a debug message
        logger = logging.getLogger("Othello")
        debug_message = "This is a debug message"
        logger.debug(debug_message)

        # Verify the debug message was logged
        mock_logger.debug.assert_called_once_with(debug_message)


# empty error message
def test_log_empty_error_message():
    """
    Test that an error message that is an empty string is still written in the log file, and does not raise an error.
    """
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        log_error_message(error="")
        mock_logger.error.assert_called_once_with("Error: ", exc_info=True)


# error message with context
def test_log_error_with_context():
    """
    Test that an error message, with context provided, is properly written in the log file.
    """
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        log_error_message(error="Test error", context="Test context")

        assert mock_logger.error.call_count == 2
        assert "Context: Test context" in mock_logger.error.call_args_list[0][0][0]
        assert "Error: Test error" in mock_logger.error.call_args_list[1][0][0]


# error message without context
def test_log_error_without_context():
    """
    Test that an error message, without any context provided, is properly written in the log file.
    """
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        log_error_message(error="Test error")

        assert mock_logger.error.call_count == 1
        assert "Error: Test error" in mock_logger.error.call_args[0][0]


# error message is getting exec_info
def test_log_error_exc_info():
    """
    Test that an error message, with context provided, is getting execution information that lead to the error.
    """
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        log_error_message(error="Test error")

        _, kwargs = mock_logger.error.call_args
        assert kwargs.get("exc_info") is True


# TEST ERRORS


def test_logging_config_with_non_boolean():
    """
    Test that the debug argument must be a boolean.
    Testing with a string, an integer and None.
    """
    with pytest.raises(TypeError):
        logging_config("not a boolean")

    with pytest.raises(TypeError):
        logging_config(1)

    with pytest.raises(TypeError):
        logging_config(None)


def test_logging_config_no_argument():
    """
    Test that the function logging_config should be given an argument.
    """
    with pytest.raises(TypeError):
        logging_config()


def test_log_error_message_missing_argument():
    """
    Test that the function log_error_message should be given at least an error string as argument.
    Testing without any argument, and without error but context.
    """
    with pytest.raises(TypeError):
        log_error_message()

    with pytest.raises(TypeError):
        log_error_message(context="Valid context")
