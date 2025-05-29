"""
Graphic interface to play the Othello game, inherits from __main__.py
"""

# pylint: disable=arguments-differ
import logging
import math
import threading
import time
from typing import Any
from collections.abc import Callable
import cairo

from gi import require_version

require_version("Gtk", "4.0")
# disabling wrong import position as it is thrown because of require_version
# yet we need to call it before gi.repository imports
from gi.repository import Gtk, GLib  # pylint: disable=wrong-import-position

import othello  # pylint: disable=wrong-import-position
from othello.controllers import GameController  # pylint: disable=wrong-import-position
from othello.othello_board import (  # pylint: disable=wrong-import-position
    Color,  # pylint: disable=wrong-import-position
    IllegalMoveException,  # pylint: disable=wrong-import-position
)  # pylint: disable=wrong-import-position

logger = logging.getLogger("Othello")


class ListBoxWithLength(Gtk.ListBox):
    """
    A subclass of Gtk.ListBox that tracks its own length (number of children).
    This makes it easier to limit the history display to a fixed number of entries.
    """

    def __init__(self):
        """
        Initializes a ListBoxWithLength object.

        A ListBoxWithLength is a subclass of a Gtk.ListBox that has an additional
        `length` attribute, which is the number of children currently in the list
        box. This attribute is updated whenever items are added or removed from the
        list box.

        :return: A new ListBoxWithLength instance.
        :rtype: ListBoxWithLength
        """
        super().__init__()
        self.length = 0
        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.set_size_request(160, -1)

    def prepend(self, child: Gtk.Widget) -> None:
        """
        Prepends a child widget to the list box and increments the length attribute.

        :param child: The widget to prepend to the list box.
        :type child: Gtk.Widget
        """
        super().prepend(child)
        self.length += 1

    def append(self, child: Gtk.Widget) -> None:
        """
        Appends a child widget to the list box and increments the length attribute.

        :param child: The widget to append to the list box.
        :type child: Gtk.Widget
        """
        super().append(child)
        self.length += 1

    def remove(self, child: Gtk.Widget) -> None:
        """
        Removes a child widget from the list box and decrements the length attribute.

        :param child: The widget to remove from the list box.
        :type child: Gtk.Widget
        """
        super().remove(child)
        self.length -= 1

    def __len__(self) -> int:
        """
        Returns the number of children currently in the list box.

        :return: The length of the list box.
        :rtype: int
        """
        return self.length


class OthelloGUI(Gtk.Application):
    """
    Main application class for the Othello GUI.
    Handles the application lifecycle and creates the main window.
    """

    PLAYS_IN_HISTORY = 15

    def __init__(self, controller: GameController):
        """
        Initialize the Othello GUI application.

        :param controller: The Othello game controller
        :param time_limit: Optional time limit for blitz mode
        """
        logger.debug(
            "Graphic User Interface is in use. Entering GUI initialization "
            "function from gui.py."
        )
        super().__init__(application_id="fr.ubx.othello")
        GLib.set_application_name("othello")
        self.controller = controller
        logger.debug("Game initialized with controller:\n%s", self.controller)

    def do_activate(self, *args: Any, **kwargs: Any) -> None:
        """
        Called when the application is activated.
        Creates and presents the main application window.
        """
        logger.debug("Entering do_activate function from gui.py.")
        window = OthelloWindow(self, self.controller)
        window.present()


class OthelloWindow(Gtk.ApplicationWindow):
    """
    Main window for the Othello game.
    Contains the game board, controls, and displays game state.
    """

    def __init__(self, application: Gtk.Application, controller: GameController):
        """
        Initialize the Othello game window.

        :param application: The parent application
        :param controller: The Othello game controller
        """
        logger.debug("Entering initialization function for game window from gui.py.")
        super().__init__(application=application, title="Othello")
        self.quit = application.quit
        self.set_default_size(800, 600)
        self.over = False
        self.over_message = None

        self.controller: GameController = controller
        self.is_blitz = self.controller.is_blitz()
        self.grid_size = controller.size.value
        self.cell_size = 50

        self.drawing_area: Gtk.DrawingArea = Gtk.DrawingArea()
        self.black_timer_label: Gtk.Label | None = None
        self.white_timer_label: Gtk.Label | None = None
        self.blitz_thread: threading.Thread | None = None
        self.blitz_loser: Color | None = None
        self.current_player: Gtk.Label = Gtk.Label()
        self.plays_list: ListBoxWithLength = ListBoxWithLength()
        self.black_nb_pieces: Gtk.Label = Gtk.Label()
        self.white_nb_pieces: Gtk.Label = Gtk.Label()
        self.forfeit_button: Gtk.Button = Gtk.Button()
        self.save_quit_button: Gtk.Button = Gtk.Button()
        self.restart_button: Gtk.Button = Gtk.Button()
        self.save_history_button: Gtk.Button = Gtk.Button()

        self.logger = logging.getLogger("Othello")

        controller.post_play_callback = self.__update_game_state

        self.__init_game(controller)
        self.load_history()

    def load_history(self):
        history = self.controller.get_history()
        for history_entry in history[: -OthelloGUI.PLAYS_IN_HISTORY]:
            self._add_to_history(history_entry)

    def __init_game(self, controller: GameController) -> None:
        """
        Initialize the game components and UI.

        :param controller: The Othello game controller
        """
        logger.debug("Initializing game components and UI")
        self.controller = controller
        self.is_blitz = self.controller.is_blitz()
        self.grid_size = controller.size.value

        self._initialize_ui_components()
        self._create_layout()
        self._connect_signals()
        self.controller.next_move()

    @staticmethod
    def create_ascii_art_label() -> Gtk.Label:
        """Create a label with ASCII art."""
        label = Gtk.Label()
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        label.set_halign(Gtk.Align.CENTER)
        label.set_markup(f"<span font_desc='monospace'>{othello.__ascii_art__}</span>")
        return label

    def _initialize_ui_components(self) -> None:
        """Initialize UI components like buttons, labels, and the drawing area."""
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw)
        self.drawing_area.set_content_width(self.grid_size * self.cell_size)
        self.drawing_area.set_content_height(self.grid_size * self.cell_size)

        if self.is_blitz:
            self.black_timer_label = Gtk.Label()
            self.white_timer_label = Gtk.Label()
            self.blitz_thread = threading.Thread(target=self._update_timers_thread)
            self.blitz_thread.daemon = True
            self.blitz_thread.start()
        self.plays_list = ListBoxWithLength()
        self.current_player = Gtk.Label(label="Current Player: black")
        self.black_nb_pieces = Gtk.Label(label="Black has 2 pieces")
        self.white_nb_pieces = Gtk.Label(label="White has 2 pieces")

        self.forfeit_button = Gtk.Button(label="forfeit")
        self.save_quit_button = Gtk.Button(label="save and quit")
        self.restart_button = Gtk.Button(label="restart")
        self.save_history_button = Gtk.Button(label="save history")

    def _connect_signals(self) -> None:
        """Connect UI elements to their event handlers."""
        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self.board_click)
        self.drawing_area.add_controller(click_gesture)
        self.forfeit_button.connect("clicked", self.forfeit_handler)
        self.save_quit_button.connect("clicked", self.save_and_quit_handler)
        self.restart_button.connect("clicked", self.restart_handler)
        self.save_history_button.connect("clicked", self.save_history_handler)

    def _create_layout(self) -> None:
        """Create and arrange the UI layout."""
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        self.set_child(main_box)
        main_box.append(OthelloWindow.create_ascii_art_label())

        main_grid = Gtk.Grid(column_spacing=20, row_spacing=20)
        main_box.append(main_grid)

        current_player_box = Gtk.Box(spacing=20)
        current_player_box.append(self.current_player)
        main_grid.attach(current_player_box, 1, 0, 1, 1)

        if self.is_blitz and self.black_timer_label and self.white_timer_label:
            timer_box = Gtk.Box(spacing=10)
            timer_box.append(self.black_timer_label)
            timer_box.append(self.white_timer_label)
            main_grid.attach(timer_box, 0, 0, 1, 1)
            main_grid.attach(Gtk.Label(label=""), 1, 0, 1, 1)

        board_container = Gtk.Grid()
        main_grid.attach(board_container, 0, 1, 1, 1)
        col_labels_grid = Gtk.Grid(column_homogeneous=True)
        col_labels_grid.set_size_request(self.grid_size * self.cell_size, 20)
        for col in range(self.grid_size):
            label = Gtk.Label(label=chr(ord("A") + col))
            label.set_halign(Gtk.Align.CENTER)
            col_labels_grid.attach(label, col, 0, 1, 1)
        board_container.attach(col_labels_grid, 1, 0, 1, 1)

        row_labels_grid = Gtk.Grid(row_homogeneous=True)
        row_labels_grid.set_size_request(20, self.grid_size * self.cell_size)
        for row in range(self.grid_size):
            label = Gtk.Label(label=str(row + 1))
            label.set_valign(Gtk.Align.CENTER)
            row_labels_grid.attach(label, 0, row, 1, 1)
        board_container.attach(row_labels_grid, 0, 1, 1, 1)

        board_container.attach(self.drawing_area, 1, 1, 1, 1)

        nb_pieces_box = Gtk.Box(spacing=10)
        nb_pieces_box.append(self.black_nb_pieces)
        nb_pieces_box.append(self.white_nb_pieces)
        main_grid.attach(nb_pieces_box, 0, 2, 1, 1)

        plays_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        plays_box.append(Gtk.Label(label=f"Last {OthelloGUI.PLAYS_IN_HISTORY} Plays"))
        plays_box.append(self.plays_list)
        main_grid.attach(plays_box, 1, 1, 1, 1)

        buttons_grid = Gtk.Grid(row_spacing=5, column_spacing=5)
        buttons_grid.attach(self.forfeit_button, 0, 0, 1, 1)
        buttons_grid.attach(self.save_quit_button, 1, 0, 1, 1)
        buttons_grid.attach(self.restart_button, 0, 1, 1, 1)
        buttons_grid.attach(self.save_history_button, 1, 1, 1, 1)
        main_grid.attach(buttons_grid, 0, 3, 1, 1)

    def __update_game_state(self) -> None:
        """Update the game state after a move or game state change."""
        if self.controller.is_game_over:
            black_score = self.controller.popcount(Color.BLACK)
            white_score = self.controller.popcount(Color.WHITE)
            logger.debug("Final score - Black: %s, White: %s", black_score, white_score)
            self.show_error_dialog(
                f"Final score - Black: {black_score}, White: {white_score}"
            )
            self.show_error_dialog(self.controller.game_over_message)

        self.drawing_area.queue_draw()
        self._update_nb_pieces()
        self.current_player.set_label(
            f"Current Player: {self.controller.get_current_player()}"
        )
        self._update_play_history()
        if not self.controller.is_game_over:
            GLib.idle_add(self.controller.next_move)

    def _update_nb_pieces(self) -> None:
        """Update the piece count labels."""
        self.black_nb_pieces.set_label(
            f"Black has {self.controller.get_pieces_count(Color.BLACK)} pieces"
        )
        self.white_nb_pieces.set_label(
            f"White has {self.controller.get_pieces_count(Color.WHITE)} pieces"
        )

    def _update_timers_thread(self) -> None:
        """
        Background thread to update timer displays and check for time-outs.
        """
        while not self.controller.is_game_over:  # its an event loop so its ok
            GLib.idle_add(self._update_timers)
            time.sleep(1)

    def _update_timers(self) -> None:
        """Update the timer display labels."""
        if self.black_timer_label:
            self.black_timer_label.set_text(
                f"Black: {self.controller.display_time_player(Color.BLACK)}"
            )
        if self.white_timer_label:
            self.white_timer_label.set_text(
                f"White: {self.controller.display_time_player(Color.WHITE)}"
            )

    def _update_play_history(self) -> None:
        """Update the play history list with the latest move."""
        if (last_play := self.controller.get_last_play()) is None:
            return
        self._add_to_history(last_play)

    def _add_to_history(self, play):
        new_move = Gtk.Label(
            label=f"{play[4]} placed a piece at {chr(ord('A') + play[2])}{play[3] + 1}"
        )
        self.plays_list.prepend(new_move)
        if len(self.plays_list) > OthelloGUI.PLAYS_IN_HISTORY:
            self.plays_list.remove(self.plays_list.get_last_child())

    def draw(
        self,
        _area: Gtk.DrawingArea,
        cairo_context: cairo.Context,  # pylint: disable=no-member
        _width: int,
        _height: int,
    ) -> None:
        """
        Master drawing function called by the DrawingArea.

        :param cairo_context: Cairo context for drawing
        """
        OthelloWindow.draw_board(cairo_context)
        self.draw_grid(cairo_context)
        self.draw_pieces(cairo_context)
        self.draw_legal_moves(cairo_context)

    @staticmethod
    def draw_board(cairo_context: cairo.Context) -> None:  # pylint: disable=no-member
        """Draws the green board background."""
        board_color = (0.2, 0.6, 0.2)
        cairo_context.set_source_rgb(*board_color)
        cairo_context.paint()

    def draw_grid(
        self, cairo_context: cairo.Context
    ) -> None:  # pylint: disable=no-member
        """Draws the grid lines on the board."""
        grid_color = (0.1, 0.4, 0.1)
        cairo_context.set_line_width(1)
        cairo_context.set_source_rgb(*grid_color)

        for col in range(self.grid_size + 1):
            cairo_context.move_to(col * self.cell_size, 0)
            cairo_context.line_to(col * self.cell_size, self.grid_size * self.cell_size)

        for row in range(self.grid_size + 1):
            cairo_context.move_to(0, row * self.cell_size)
            cairo_context.line_to(self.grid_size * self.cell_size, row * self.cell_size)

        cairo_context.stroke()

    def draw_legal_moves(
        self, cairo_context: cairo.Context
    ) -> None:  # pylint: disable=no-member
        """Draws semi-transparent indicators for legal moves."""
        black_piece_color = (0, 0, 0, 0.3)
        white_piece_color = (1, 1, 1, 0.3)
        legal_moves = self.controller.get_possible_moves(
            self.controller.get_current_player()
        )

        color = (
            black_piece_color
            if self.controller.get_current_player() == Color.BLACK
            else white_piece_color
        )
        cairo_context.set_source_rgba(*color)

        for col in range(self.grid_size):
            for row in range(self.grid_size):
                if legal_moves.get(col, row):
                    center_x = col * self.cell_size + self.cell_size // 2
                    center_y = row * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 2 - 2
                    cairo_context.arc(center_x, center_y, radius, 0, 2 * math.pi)
                    cairo_context.fill()

    def draw_pieces(
        self, cairo_context: cairo.Context
    ) -> None:  # pylint: disable=no-member
        """Draws all game pieces (black and white) on the board."""
        black_piece_color = (0, 0, 0)
        white_piece_color = (1, 1, 1)

        for col in range(self.grid_size):
            for row in range(self.grid_size):
                if not (
                    self.controller.get_position(Color.BLACK, col, row)
                    or self.controller.get_position(Color.WHITE, col, row)
                ):
                    continue

                center_x = col * self.cell_size + self.cell_size // 2
                center_y = row * self.cell_size + self.cell_size // 2
                radius = self.cell_size // 2 - 2

                if self.controller.get_position(Color.BLACK, col, row):
                    cairo_context.set_source_rgb(*black_piece_color)
                else:
                    cairo_context.set_source_rgb(*white_piece_color)

                cairo_context.arc(center_x, center_y, radius, 0, 2 * math.pi)
                cairo_context.fill()

    def board_click(
        self, _gesture: Gtk.GestureClick, _n_press: int, click_x: float, click_y: float
    ) -> None:
        """
        Handle clicks on the game board.

        :param click_x: X coordinate of the click
        :param click_y: Y coordinate of the click
        """
        if (
            self.controller.is_game_over
            or not self.controller.current_player_is_human()
        ):
            return
        board_x = int(click_x / self.cell_size)
        board_y = int(click_y / self.cell_size)
        if 0 <= board_x < self.grid_size and 0 <= board_y < self.grid_size:
            try:
                self.controller.play(board_x, board_y)
            except IllegalMoveException as err:
                self.logger.debug(err)

    def forfeit_handler(self, _button: Gtk.Button) -> None:
        """Handle forfeit button click."""
        self.show_confirm_dialog(
            "Are you sure? This will close the program and your "
            "progression will be lost!",
            self.forfeit_handler_callback,
        )

    def forfeit_handler_callback(self, response: int) -> None:
        """Handle forfeit confirmation response."""
        if response == -5:  # OK button
            self.show_confirm_dialog(
                f"{(~self.controller.get_current_player()).name} wins the game",
                lambda _: self.quit(),
            )

    def restart_handler(self, _button: Gtk.Button) -> None:
        """Handle restart button click."""
        self.show_confirm_dialog(
            "Are you sure you want to restart the game?", self.restart_handler_callback
        )

    def restart_handler_callback(self, confirmation: int) -> None:
        """Handle restart confirmation response."""
        if confirmation == -5:  # OK button
            self.over = True
            if self.blitz_thread is not None:
                self.blitz_thread.join(timeout=1.0)
            self.controller.restart()
            for _ in range(len(self.plays_list)):
                self.plays_list.remove(self.plays_list.get_last_child())
            self._update_nb_pieces()
            self.over = False
            self.__init_game(self.controller)

    def file_chooser(
        self,
        callback: Callable,
        default_file_name: str,
        file_extension: str,
    ) -> None:
        """
        Show a file chooser dialog.

        :param callback: Function to call with the dialog result
        :param default_file_name: Default file name suggestion
        :param file_extension: File extension to filter by
        """
        dialog = Gtk.FileChooserDialog(
            title="Save Game",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.ACCEPT)
        dialog.set_modal(True)
        dialog.set_current_name(f"{default_file_name}.{file_extension}")
        filter_sav = Gtk.FileFilter()
        filter_sav.set_name("Othello Save Files")
        filter_sav.add_pattern(f"*.{file_extension}")
        dialog.add_filter(filter_sav)
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All Files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)
        dialog.connect("response", callback)
        dialog.present()

    def save_and_quit_handler(self, _button: Gtk.Button) -> None:
        """Handle save and quit button click."""
        self.file_chooser(self.on_save_dialog_response, "my_game", "sav")

    def on_save_dialog_response(self, dialog: Gtk.Dialog, response: int) -> None:
        """
        Handle save dialog response.

        :param dialog: The dialog widget
        :param response: Dialog response value
        """
        if response == Gtk.ResponseType.ACCEPT:
            if (file_obj := dialog.get_file()) is not None:
                file_path = file_obj.get_path()
                if (file_path := file_obj.get_path()) is not None:
                    self.save_game_to_file(file_path)
                    self.close()
        dialog.destroy()

    def save_game_to_file(self, file_path: str) -> None:
        """
        Save the current game state to a file.

        :param file_path: Path to save the game
        """
        with open(file_path, "w", encoding="utf-8") as file:
            game_data = self.controller.export()
            file.write(game_data)
        logger.info("Game saved to %s", file_path)

    def save_history_handler(self, _button: Gtk.Button) -> None:
        """Handle save history button click."""
        self.file_chooser(self.on_save_history_dialog_response, "my_hist", "hist")

    def on_save_history_dialog_response(
        self, dialog: Gtk.Dialog, response: int
    ) -> None:
        """
        Handle save history dialog response.

        :param dialog: The dialog widget
        :param response: Dialog response value
        """
        if response == Gtk.ResponseType.ACCEPT:
            if (file_obj := dialog.get_file()) is not None:
                file_path = file_obj.get_path()
                if (file_path := file_obj.get_path()) is not None:
                    self.save_history_to_file(file_path)
        dialog.destroy()

    def save_history_to_file(self, file_path: str) -> None:
        """
        Save the game history to a file.

        :param file_path: Path to save the game history
        """
        with open(file_path, "w", encoding="utf-8") as file:
            game_data = self.controller.export_history()
            file.write(game_data)
        logger.info("Game history saved to %s", file_path)

    def show_confirm_dialog(self, message: str, callback: Callable) -> None:
        """
        Show a confirmation dialog.

        :param message: The message to display
        :param callback: Function to call with the dialog result
        """

        def call_cb(dialog: Gtk.Dialog, response: int) -> None:
            dialog.destroy()
            callback(response)

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=message,
        )
        dialog.connect("response", call_cb)
        dialog.present()

    def show_error_dialog(self, message: str) -> None:
        """
        Display an error dialog with a given message.

        :param message: The error message to display in the dialog
        """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=str(message),
        )
        dialog.connect("response", lambda d, _: d.destroy())
        dialog.present()
