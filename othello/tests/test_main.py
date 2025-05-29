import pytest
from unittest.mock import MagicMock, patch, mock_open

from othello.__main__ import main
from othello.othello_board import BoardSize, OthelloBoard


BASE_CONFIG = {
    "filename": None,
    "size": 8,
    "debug": False,
    "blitz_time": 30,
    "ai_color": "X",
    "ai_mode": "minimax",
    "ai_depth": 3,
    "ai_heuristic": "corners_captured",
    "gui": False,
    "benchmark": False,
}


def fake_board_constructor(size):
    return OthelloBoard(BoardSize.from_value(size))


@patch("othello.__main__.OthelloCLI", autospec=True)
@patch("othello.__main__.display_config")
@patch("othello.__main__.logging")
@patch("othello.__main__.parser.parse_args")
@patch("othello.__main__.GameController", autospec=True)
def test_main_cli_normal(
    mock_GameController, mock_parse_args, mock_logging, mock_display_config, mock_CLI
):
    config = BASE_CONFIG.copy()
    mode = "normal"
    mock_parse_args.return_value = (mode, config)

    with patch("othello.__main__.OthelloGUI") as mock_GUI:
        fake_controller = MagicMock()
        fake_controller.is_blitz.return_value = False
        mock_GameController.return_value = fake_controller
        main()
        mock_display_config.assert_called_once_with(config)
        if mock_GUI.return_value.run.called:
            pytest.fail("OthelloGUI.run should not have been called in CLI mode.")


@patch("othello.__main__.OthelloGUI", autospec=True)
@patch("othello.__main__.display_config")
@patch("othello.__main__.logging")
@patch("othello.__main__.parser.parse_args")
@patch("othello.__main__.GameController", autospec=True)
def test_main_gui_mode(
    mock_GameController, mock_parse_args, mock_logging, mock_display_config, mock_GUI
):
    config = BASE_CONFIG.copy()
    config["gui"] = True
    mode = "normal"
    mock_parse_args.return_value = (mode, config)

    with patch("othello.__main__.OthelloCLI") as mock_CLI:
        fake_controller = MagicMock()
        fake_controller.is_blitz = False
        mock_GameController.return_value = fake_controller

        main()

        mock_display_config.assert_called_once_with(config)
        mock_GUI.return_value.run.assert_called_once()
        mock_CLI.assert_not_called()


@patch("othello.__main__.parser.parse_args")
@patch("othello.__main__.logging")
def test_main_file_not_found(mock_logging, mock_parse_args):
    config = BASE_CONFIG.copy()
    config["filename"] = "nonexistent.sav"
    mode = "normal"
    mock_parse_args.return_value = (mode, config)
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            main()


@patch("othello.__main__.OthelloCLI", autospec=True)
@patch("othello.__main__.display_config")
@patch("othello.__main__.logging")
@patch("othello.__main__.parser.parse_args")
@patch("othello.__main__.GameController", autospec=True)
def test_main_blitz_mode(
    mock_GameController, mock_parse_args, mock_logging, mock_display_config, mock_CLI
):
    config = BASE_CONFIG.copy()
    config["blitz_time"] = 20
    mode = "blitz"
    mock_parse_args.return_value = (mode, config)

    fake_controller = MagicMock()
    fake_controller.is_blitz.return_value = True
    mock_GameController.return_value = fake_controller

    main()

    mock_GameController.assert_called_once()
    print(mock_CLI)
    mock_CLI.assert_called_once_with(fake_controller, fake_controller.is_blitz())


@patch("othello.__main__.HumanPlayer", autospec=True)
@patch("othello.__main__.AIPlayer", autospec=True)
@patch("othello.__main__.OthelloCLI", autospec=True)
@patch("othello.__main__.display_config")
@patch("othello.__main__.logging")
@patch("othello.__main__.parser.parse_args")
@patch("othello.__main__.GameController", autospec=True)
def test_main_ai_mode(
    mock_GameController,
    mock_parse_args,
    mock_logging,
    mock_display_config,
    mock_CLI,
    mock_AIPlayer,
    mock_HumanPlayer,
):
    config = BASE_CONFIG.copy()
    config["ai_color"] = "X"
    mode = "ai"
    mock_parse_args.return_value = (mode, config)

    fake_controller = MagicMock()
    fake_controller.is_blitz.return_value = False
    mock_GameController.return_value = fake_controller

    main()

    assert mock_AIPlayer.call_count == 1, "Expected one AIPlayer instance for black."
    assert (
        mock_HumanPlayer.call_count >= 1
    ), "Expected at least one HumanPlayer instance for white."
    mock_CLI.assert_called_once_with(fake_controller, fake_controller.is_blitz())
