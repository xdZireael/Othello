import pytest
import os
import sys
from io import StringIO
from unittest.mock import MagicMock, mock_open, patch
from othello.config import (
    save_board_state_history,
    save_config,
    load_config,
    display_config,
)


@pytest.fixture
def temp_config_file(tmpdir):
    """
    Creates a temporary file used to test saving and loading of configuration
    files. The file is deleted after the test is run.

    Yields:
        str: The path to the temporary file.
    """
    temp_file = tmpdir.join("test_config.othellorc")
    yield str(temp_file)
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_save_and_load_config(temp_config_file):
    # Define a sample configuration
    sample_config = {
        "mode": "normal",
        "filename": "save.feur",
        "size": "8",
        "debug": "false",
        "blitz_time": "30",
        "ai_color": "X",
        "ai_mode": "minimax",
        "ai_shallow": "true",
        "ai_depth": "3",
        "ai_heuristic": "default",
        "ai_time": "5",
    }

    save_config(
        sample_config, filename_prefix=temp_config_file.replace(".othellorc", "")
    )

    loaded_config = load_config(
        filename_prefix=temp_config_file.replace(".othellorc", "")
    )

    assert loaded_config == sample_config


def test_load_nonexistent_config():
    with pytest.raises(FileNotFoundError):
        load_config(filename_prefix="nonexistent")


def test_save_config_invalid_filename():
    invalid_config = {"mode": "normal"}
    with pytest.raises(IOError):
        save_config(invalid_config, filename_prefix="/invalid/path/test_config")


def test_load_config_invalid_filename():
    with pytest.raises(FileNotFoundError):
        load_config(filename_prefix="/invalid/path/test_config")


def test_save_and_load_empty_config(temp_config_file):
    empty_config = {}

    save_config(
        empty_config, filename_prefix=temp_config_file.replace(".othellorc", "")
    )

    loaded_config = load_config(
        filename_prefix=temp_config_file.replace(".othellorc", "")
    )

    assert loaded_config == empty_config


def test_display_config():
    """
    Test display_config with an empty dictionnary, and one containing a small configuration
    """
    dummy_config = {}
    expected_output = "Configuration:\n"
    captured_output = StringIO()

    # redirect stdout into our variable, then reset it
    sys.stdout = captured_output
    display_config(dummy_config)
    sys.stdout = sys.__stdout__

    assert expected_output == captured_output.getvalue()

    dummy_config2 = {"mode": "normal", "filename": None, "size": 8}
    expected_output2 = "Configuration:\n  mode: normal\n  filename: None\n  size: 8\n"
    captured_output2 = StringIO()

    sys.stdout = captured_output2
    display_config(dummy_config2)
    sys.stdout = sys.__stdout__

    assert expected_output2 == captured_output2.getvalue()


def test_invalid_display_config():
    invalid_config = ["not a dict"]
    invalid_config2 = "not_a_dict"
    invalid_config3 = 299.792

    with pytest.raises(SystemExit):
        display_config(invalid_config)
    with pytest.raises(SystemExit):
        display_config(invalid_config2)
    with pytest.raises(SystemExit):
        display_config(invalid_config3)


def test_save_board_state_with_prefix_and_full_state(tmp_path):
    controller = MagicMock()
    controller.export.return_value = "FULL_STATE"
    filename_prefix = str(tmp_path / "game")

    save_board_state_history(
        controller, filename_prefix=filename_prefix, only_hist=False
    )

    with open(f"{filename_prefix}.sav", "r", encoding="utf-8") as f:
        assert f.read() == "FULL_STATE"
    controller.export.assert_called_once()
    controller.export_history.assert_not_called()


def test_save_board_state_with_prefix_and_history_only(tmp_path):
    controller = MagicMock()
    controller.export_history.return_value = "HISTORY_ONLY"
    filename_prefix = str(tmp_path / "game")

    save_board_state_history(
        controller, filename_prefix=filename_prefix, only_hist=True
    )

    with open(f"{filename_prefix}.sav", "r", encoding="utf-8") as f:
        assert f.read() == "HISTORY_ONLY"
    controller.export_history.assert_called_once()
    controller.export.assert_not_called()


@patch("builtins.input", side_effect=["invalid/name", "validname"])
@patch("builtins.open", new_callable=mock_open)
def test_save_board_state_prompts_for_valid_filename(mock_open_func, mock_input):
    controller = MagicMock()
    controller.export.return_value = "DATA"

    # Fail first time, succeed second time
    def open_side_effect(name, *args, **kwargs):
        if "invalid" in name:
            raise OSError("Invalid filename")
        return mock_open_func.return_value

    mock_open_func.side_effect = open_side_effect

    save_board_state_history(controller, filename_prefix=None, only_hist=False)

    assert mock_input.call_count == 2
    controller.export.assert_called_once()


@patch("builtins.open", new_callable=mock_open)
def test_save_board_state_write_error(mock_open_func):
    controller = MagicMock()
    controller.export.return_value = "DATA"

    mock_open_func.side_effect = IOError("disk full")

    with pytest.raises(IOError):
        save_board_state_history(
            controller, filename_prefix="testfail", only_hist=False
        )


@patch("othello.logger.log_error_message")
@patch("builtins.open", new_callable=mock_open)
def test_error_logging_on_write_failure(mock_open_func, mock_log_error):
    controller = MagicMock()
    controller.export.return_value = "DATA"
    mock_open_func.side_effect = IOError("Write failed")

    with pytest.raises(IOError):
        save_board_state_history(
            controller, filename_prefix="somefile", only_hist=False
        )

    mock_log_error.assert_called_once()
    args, kwargs = mock_log_error.call_args
    assert "Write failed" in args[0]
    assert "Failed to save board state" in kwargs["context"]
