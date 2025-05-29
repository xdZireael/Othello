"""implementation of AI algorithms used for AIPlayer"""

from collections.abc import Callable
import random
from copy import deepcopy
import logging

from othello.othello_board import OthelloBoard, Color

logger = logging.getLogger("Othello")


def get_player_at(board: OthelloBoard, x_coord: int, y_coord: int) -> Color:
    """Helper function to determine which player occupies a given board position."""
    if board.black.get(x_coord, y_coord):
        return Color.BLACK
    if board.white.get(x_coord, y_coord):
        return Color.WHITE
    return Color.EMPTY


def minimax(
    board: OthelloBoard, depth: int, max_player: Color, heuristic: Callable
) -> float:
    """
    Evaluate the best move for the current player using the Minimax algorithm.

    The Minimax algorithm is a recursive algorithm used for decision making in
    games like Othello. It works by simulating all possible moves and their
    consequences, and then choosing the best move based on a heuristic function.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param depth: The maximum depth of the search tree.
    :type depth: int
    :param max_player: The color of the player to maximize the score for.
    :type max_player: Color
    :param heuristic: The heuristic used
    :return: The heuristic value of the best move found from the current board state.
    """
    logger.debug(
        "Starting minimax evaluation with depth: %d, player: %s.",
        depth,
        max_player.name,
    )

    if not depth or board.is_game_over():
        return heuristic(board, max_player)

    if not (
        valid_moves := board.line_cap_move(board.current_player).hot_bits_coordinates()
    ):
        return minimax(board, depth - 1, max_player, heuristic)

    logger.debug("   Valid moves at depth %d: %s.", depth, valid_moves)
    if max_player == board.current_player:
        evaluation = float("-inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            evaluation_score = minimax(board, depth - 1, max_player, heuristic)
            evaluation = max(evaluation, evaluation_score)
            board.pop()
    else:
        evaluation = float("inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            evaluation_score = minimax(board, depth - 1, max_player, heuristic)
            evaluation = min(evaluation, evaluation_score)
            board.pop()

    logger.debug(
        "   Minimax evaluationuation at depth %d returning score: %d.",
        depth,
        evaluation,
    )
    return evaluation


def alphabeta(
    board: OthelloBoard,
    depth: int,
    alpha: int,
    beta: int,
    max_player: Color,
    heuristic: Callable,
) -> float:
    """
    Evaluate the best move for the current player using the Alpha-Beta Pruning algorithm.

    The Alpha-Beta Pruning algorithm is a search algorithm that seeks to decrease the
    number of nodes to be evaluated in the search tree by eliminating branches that
    will not affect the final decision. It works by maintaining two values, alpha and
    beta, which represent the best possible score for the maximizing player and the
    minimizing player respectively. If the score of a node is outside of the alpha-beta
    window, it will not affect the final decision and can be pruned.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param depth: The maximum depth of the search tree.
    :type depth: int
    :param alpha: The best possible score for the maximizing player.
    :type alpha: int
    :param beta: The best possible score for the minimizing player.
    :type beta: int
    :param max_player: The color of the player to maximize the score for.
    :type max_player: Color
    :param heuristic: The heuristic used
    :return: The heuristic value of the best move found from the current board state.
    :rtype: int
    """
    logger.debug(
        "Starting alphabeta evaluation with depth: %d, player: %s, alpha: %f, beta: %f.",
        depth,
        max_player.name,
        alpha,
        beta,
    )

    if not depth or board.is_game_over():
        return heuristic(board, max_player)

    if not (
        valid_moves := board.line_cap_move(board.current_player).hot_bits_coordinates()
    ):
        return minimax(board, depth - 1, max_player, heuristic)

    logger.debug("   Valid moves at depth %d: %s.", depth, valid_moves)
    if max_player == board.current_player:
        evaluation = float("-inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            evaluation_score = alphabeta(
                board, depth - 1, alpha, beta, max_player, heuristic
            )
            evaluation = max(evaluation, evaluation_score)
            board.pop()
            alpha = int(max(alpha, evaluation))
            if beta <= alpha:
                logger.debug(
                    "   Alpha-Beta pruning occurred at depth %d (alpha: %f, beta: %f).",
                    depth,
                    alpha,
                    beta,
                )
                break
    else:
        evaluation = float("inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            evaluation_score = alphabeta(
                board, depth - 1, alpha, beta, max_player, heuristic
            )
            evaluation = min(evaluation, evaluation_score)
            board.pop()
            if (beta := int(min(beta, evaluation))) <= alpha:
                logger.debug(
                    "   Alpha-Beta pruning occurred at depth %d (alpha: %f, beta: %f).",
                    depth,
                    alpha,
                    beta,
                )
                break

    logger.debug(
        "   Alphabeta evaluationuation at depth %d returning score: %d.",
        depth,
        evaluation,
    )
    return evaluation


def find_best_move(
    board: OthelloBoard,
    depth: int = 3,
    max_player: Color = Color.BLACK,
    search_algo: str = "minimax",
    heuristic: str = "corners_captured",
    benchmark: bool = False,
) -> tuple[int, int]:
    """
    Determine the best move for the current player on the Othello board.

    This function evaluates possible moves using a specified search algorithm
    (minimax or alphabeta) and heuristic to find the best move for the given
    player. If no valid moves are available or the depth is zero, it returns
    (-1, -1) indicating no move.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param depth: The maximum depth of the search tree.
    :type depth: int
    :param max_player: The color of the player to maximize the score for.
    :type max_player: Color
    :param maximizing: A Boolean indicating whether the current step is maximizing or
        minimizing the score.
    :type maximizing: bool
    :param search_algo: The search algorithm to use, either "minimax" or "alphabeta".
    :type search_algo: str
    :param heuristic: The heuristic function to evaluate board states.
    :type heuristic: str
    :return: The coordinates of the best move for the current player.
    :rtype: tuple[int, int]
    """
    logger.debug(
        "Finding best move using %s search at depth %d for %s player.",
        search_algo,
        depth,
        max_player.name,
    )

    if depth == 0 or board.is_game_over():
        return (-1, -1)

    if heuristic == "coin_parity":
        heuristic_function = coin_parity_heuristic
    elif heuristic == "corners_captured":
        heuristic_function = corners_captured_heuristic
    elif heuristic == "mobility":
        heuristic_function = mobility_heuristic
    else:
        heuristic_function = all_in_one_heuristic

    valid_moves = board.line_cap_move(board.current_player).hot_bits_coordinates()
    logger.debug("   Evaluating %d possible moves: %s.", len(valid_moves), valid_moves)

    best_move = (-1, -1)
    best_score = float("-inf") if max_player == board.current_player else float("inf")
    for move_x, move_y in valid_moves:
        new_board = deepcopy(board)

        new_board.play(move_x, move_y)
        if search_algo == "minimax":
            score = minimax(new_board, depth - 1, max_player, heuristic_function)
        else:
            score = alphabeta(
                new_board,
                depth - 1,
                float("-inf"),
                float("inf"),
                max_player,
                heuristic_function,
            )
        logger.debug("   Move (%d, %d) evaluated with score: %f", move_x, move_y, score)
        if score > best_score:
            best_score = score
            best_move = (move_x, move_y)

    if benchmark:
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")

    return best_move


def random_move(board: OthelloBoard) -> tuple[int, int]:
    """
    Select a random valid move for the current player on the Othello board.

    This function retrieves all possible moves for the current player and
    selects one at random. It assumes the game is not over and there are
    available moves.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :return: The coordinates of a randomly selected valid move.
    :rtype: tuple[int, int]
    """
    valid_moves = board.line_cap_move(board.current_player).hot_bits_coordinates()
    logger.debug(
        "Selecting random move from %d options: %s", len(valid_moves), valid_moves
    )
    return random.choice(valid_moves)


def corners_captured_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Calculate the heuristic score based on the number of corners captured.

    This heuristic evaluates the board by calculating the difference between
    the number of corners occupied by the max player and the opponent. The
    score is a percentage reflecting the advantage of the max player in terms
    of corner occupation. If no corners are occupied, the score is zero.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param max_player: The color of the player to maximize the score for.
    :type max_player: Color
    :return: An integer score representing the corner occupation advantage.
    :rtype: int
    """
    logger.debug("Calculating %s heuristic for %s", "corners_captured", max_player.name)
    corners = [
        (0, 0),
        (board.size.value - 1, 0),
        (0, board.size.value - 1),
        (board.size.value - 1, board.size.value - 1),
    ]

    max_corners = sum(1 for x, y in corners if get_player_at(board, x, y) == max_player)
    min_corners = sum(
        1 for x, y in corners if get_player_at(board, x, y) == ~max_player
    )

    if max_corners + min_corners:
        return int(100 * (max_corners - min_corners) / (max_corners + min_corners))
    return 0


def coin_parity_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Calculate the heuristic score based on coin parity between players.

    This heuristic evaluates the board by calculating the difference between
    the number of discs owned by the max player and the opponent. The score
    is a percentage reflecting the advantage of the max player in terms of
    the number of discs. If the max player has more discs, a positive score
    is returned; otherwise, a negative score is returned. If there are no
    discs on the board, the function returns Color.EMPTY.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param max_player: The color of the player to maximize the score for.
    :type max_player: Color
    :return: An integer score representing the coin parity advantage.
    :rtype: int
    """
    logger.debug("Calculating %s heuristic for %s", "coin_parity", max_player.name)

    black_count = board.black.popcount()
    white_count = board.white.popcount()

    if max_player == Color.BLACK:
        return int(100 * (black_count - white_count) / (black_count + white_count))
    if max_player == Color.WHITE:
        return int(100 * (white_count - black_count) / (white_count + black_count))
    return Color.EMPTY


def mobility_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Calculate the heuristic score based on the number of moves available for each player.

    This heuristic evaluates the board by calculating the difference between
    the number of moves available for the max player and the opponent. The
    score is a percentage reflecting the advantage of the max player in terms
    of mobility. If the max player has more moves available, a positive score
    is returned; otherwise, a negative score is returned. If there are no
    moves available for either player, the function returns Color.EMPTY.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param max_player: The color of the player to maximize the score for.
    :type max_player: Color
    :return: An integer score representing the mobility advantage.
    :rtype: int
    """
    logger.debug("Calculating %s heuristic for %s", "mobility", max_player.name)

    black_move_count = board.line_cap_move(board.black).popcount()
    white_move_count = board.line_cap_move(board.white).popcount()

    if black_move_count + white_move_count:
        if max_player == Color.BLACK:
            return int(
                100
                * (black_move_count - white_move_count)
                / (black_move_count + white_move_count)
            )
        if max_player == Color.WHITE:
            return int(
                100
                * (white_move_count - black_move_count)
                / (white_move_count + black_move_count)
            )
        return Color.EMPTY
    return 0


def all_in_one_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Performs all the heuristics at once
    """
    logger.debug("Calculating %s heuristic for %s", "all_in_one", max_player.name)
    w_corners = 10
    w_mobility = 4
    w_coins = 1

    return (
        w_corners * corners_captured_heuristic(board, max_player)
        + w_mobility * mobility_heuristic(board, max_player)
        + w_coins * coin_parity_heuristic(board, max_player)
    )
