import pytest
from unittest.mock import MagicMock, Mock, patch
from othello.cli import OthelloCLI
from othello.command_parser import CommandKind
from othello.controllers import GameController
from othello.othello_board import Color


class TestBlitzMode:
    """Tests for blitz mode specific functionality"""

    @pytest.fixture
    def blitz_game(self):
        controller_mock = MagicMock(spec=GameController)
        game = OthelloCLI(controller=controller_mock, blitz_mode=True)
        game.controller = MagicMock()
        game.controller.get_current_player.return_value = Color.BLACK
        game.blitz_timer = MagicMock()
        return game

    @pytest.fixture
    def blitz_game_white_timer_over(self):
        mock_controller = MagicMock()
        mock_controller.get_current_player.return_value = Color.BLACK
        mock_controller.is_game_over.return_value = False

        game = OthelloCLI(mock_controller, blitz_mode=True)
        game.blitz_timer = MagicMock()
        game.blitz_timer.is_time_up.return_value = True  # Fixed this line
        game.blitz_timer.get_current_player.return_value = Color.WHITE

        return game

    def test_check_game_over_blitz(self, blitz_game_white_timer_over):
        assert blitz_game_white_timer_over.check_game_over(
            blitz_game_white_timer_over.controller.get_possible_moves(
                blitz_game_white_timer_over.controller.get_current_player()
            )
        )
