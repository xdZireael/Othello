import subprocess
import csv
import time
import os
from concurrent.futures import ProcessPoolExecutor
import re

from matplotlib import pyplot as plt
from numpy import mean


def run_game(
    white_ai_mode,
    white_ai_depth,
    white_ai_heuristic,
    black_ai_mode,
    black_ai_depth,
    black_ai_heuristic,
    board_size=6,
    debug=False,
):
    """Run a single game of Othello with the specified parameters"""
    cmd = ["othello", "-a", "A", "--size", str(board_size), "--benchmark"]

    # Configure white AI
    cmd.extend(["--white-ai-mode", white_ai_mode])
    cmd.extend(["--white-ai-depth", str(white_ai_depth)])
    cmd.extend(["--white-ai-heuristic", white_ai_heuristic])

    # Configure black AI (using the general AI options)
    cmd.extend(["--ai-mode", black_ai_mode])
    cmd.extend(["--ai-depth", str(black_ai_depth)])
    cmd.extend(["--ai-heuristic", black_ai_heuristic])

    if debug:
        cmd.append("--debug")

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    total_runtime = end_time - start_time

    output = result.stdout

    # Parse the output to extract relevant information
    black_score = white_score = 0
    winner = "Draw"

    # Use regex to extract scores from the output
    score_match = re.search(r"Final score - Black: (\d+), White: (\d+)", output)
    if score_match:
        black_score = int(score_match.group(1))
        white_score = int(score_match.group(2))

        if black_score > white_score:
            winner = "Black"
        elif white_score > black_score:
            winner = "White"

    # Extract all turn information
    turns_matches = re.findall(r"=== turn (\d+) ===", output)
    total_turns = int(turns_matches[-1]) if turns_matches else 0

    # Find all execution time entries - these are the algorithm's thinking times
    execution_times = re.findall(r"Execution time: ([\d.]+) seconds", output)
    execution_times = [float(t) for t in execution_times]

    # Separate black and white execution times
    # Black player moves on odd turns (1, 3, 5...)
    # White player moves on even turns (2, 4, 6...)
    black_execution_times = [
        execution_times[i]
        for i in range(0, len(execution_times), 2)
        if i < len(execution_times)
    ]
    white_execution_times = [
        execution_times[i]
        for i in range(1, len(execution_times), 2)
        if i < len(execution_times)
    ]

    # Calculate average execution times
    avg_black_time = mean(black_execution_times) if black_execution_times else 0
    avg_white_time = mean(white_execution_times) if white_execution_times else 0

    # Determine which algorithm is faster
    if black_ai_mode == white_ai_mode:
        faster_algorithm = "Same algorithm"
    else:
        if avg_black_time < avg_white_time:
            faster_algorithm = black_ai_mode
        else:
            faster_algorithm = white_ai_mode

    return {
        "black_ai_mode": black_ai_mode,
        "black_ai_depth": black_ai_depth,
        "black_ai_heuristic": black_ai_heuristic,
        "white_ai_mode": white_ai_mode,
        "white_ai_depth": white_ai_depth,
        "white_ai_heuristic": white_ai_heuristic,
        "black_score": black_score,
        "white_score": white_score,
        "winner": winner,
        "total_turns": total_turns,
        "avg_black_execution_time": avg_black_time,
        "avg_white_execution_time": avg_white_time,
        "total_runtime": total_runtime,
        "faster_algorithm": faster_algorithm,
    }


def run_experiment1(num_games=200):
    """
    Run experiment 1: minimax d6 corners_captured vs AB d6 corners_captured
    Measure runtime of games
    """
    print(f"Starting Experiment 1: minimax vs AB at depth 6 ({num_games} games)")
    results = []

    for i in range(num_games):
        print(f"Running game {i+1}/{num_games}")
        # First half: minimax is black, AB is white
        game_result = run_game(
            white_ai_mode="ab",
            white_ai_depth=7,
            white_ai_heuristic="corners_captured",
            black_ai_mode="minimax",
            black_ai_depth=7,
            black_ai_heuristic="corners_captured",
            board_size=6,
        )
        game_result["game_number"] = i + 1
        results.append(game_result)

    # Write results to CSV
    with open("experiment1_results.csv", "w", newline="") as csvfile:
        fieldnames = [
            "game_number",
            "black_ai_mode",
            "black_ai_depth",
            "black_ai_heuristic",
            "white_ai_mode",
            "white_ai_depth",
            "white_ai_heuristic",
            "black_score",
            "white_score",
            "winner",
            "total_turns",
            "avg_black_execution_time",
            "avg_white_execution_time",
            "total_runtime",
            "faster_algorithm",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result[field] for field in fieldnames})

    # Calculate and print summary statistics
    minimax_times = []
    ab_times = []

    for result in results:
        if result["black_ai_mode"] == "minimax":
            minimax_times.append(result["avg_black_execution_time"])
        elif result["black_ai_mode"] == "ab":
            ab_times.append(result["avg_black_execution_time"])

        if result["white_ai_mode"] == "minimax":
            minimax_times.append(result["avg_white_execution_time"])
        elif result["white_ai_mode"] == "ab":
            ab_times.append(result["avg_white_execution_time"])

    minimax_avg = mean(minimax_times) if minimax_times else 0
    ab_avg = mean(ab_times) if ab_times else 0

    print(f"\nSummary Statistics:")
    print(f"Average execution time for Minimax: {minimax_avg:.6f} seconds")
    print(f"Average execution time for Alpha-Beta: {ab_avg:.6f} seconds")
    print(
        f"Alpha-Beta is {minimax_avg/ab_avg:.2f}x faster than Minimax"
        if ab_avg > 0
        else ""
    )
    with open("experiment1_results.csv", "w", newline="") as csvfile:
        fieldnames = [
            "game_number",
            "black_ai_depth",
            "white_ai_depth",
            "black_ai_mode",
            "black_ai_heuristic",
            "white_ai_mode",
            "white_ai_heuristic",
            "black_score",
            "white_score",
            "winner",
            "total_turns",
            "avg_black_execution_time",
            "avg_white_execution_time",
            "total_runtime",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result[field] for field in fieldnames})

    return results


def run_experiment2():
    """
    Run experiment 2: AB heuristic1 depth x vs AB heuristic2 depth x
    10 games for each matchup
    """
    print("Starting Experiment 2: Heuristic comparisons")
    results = []
    game_count = 0

    heuristics = ["corners_captured", "coin_parity", "mobility", "all_in_one"]
    depths = [2, 3, 4, 5]

    # For each depth
    for depth in depths:
        # For each pair of heuristics
        for i, heuristic1 in enumerate(heuristics):
            for j, heuristic2 in enumerate(heuristics):
                if i >= j:  # Skip redundant matchups and same heuristic matchups
                    continue

                print(
                    f"Testing {heuristic1} vs {heuristic2} at depth {depth} (10 games)"
                )

                # Play 10 games (5 with each color)
                for game in range(10):
                    game_count += 1

                    # First 5 games: heuristic1 is black, heuristic2 is white
                    if game < 5:
                        game_result = run_game(
                            white_ai_mode="ab",
                            white_ai_depth=depth,
                            white_ai_heuristic=heuristic2,
                            black_ai_mode="ab",
                            black_ai_depth=depth,
                            black_ai_heuristic=heuristic1,
                            board_size=6,
                        )
                    # Next 5 games: heuristic2 is black, heuristic1 is white
                    else:
                        game_result = run_game(
                            white_ai_mode="ab",
                            white_ai_depth=depth,
                            white_ai_heuristic=heuristic1,
                            black_ai_mode="ab",
                            black_ai_depth=depth,
                            black_ai_heuristic=heuristic2,
                            board_size=6,
                        )

                    game_result["game_number"] = game_count
                    game_result["depth"] = depth
                    results.append(game_result)

    # Write results to CSV
    with open("experiment2_results.csv", "w", newline="") as csvfile:
        fieldnames = [
            "game_number",
            "depth",
            "black_ai_mode",
            "black_ai_heuristic",
            "white_ai_mode",
            "white_ai_heuristic",
            "black_score",
            "white_score",
            "winner",
            "turns",
            "execution_time",
            "total_runtime",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result[field] for field in fieldnames})

    return results


def run_experiment3():
    """
    Run experiment 3: Test every possible matchup at depth 3 on both colors
    """
    print("Starting Experiment 3: All matchups at depth 3")
    results = []
    game_count = 0

    ai_modes = ["ab"]
    heuristics = ["corners_captured", "coin_parity", "mobility", "all_in_one"]

    # For every combination of AI mode and heuristic for black
    for black_mode in ai_modes:
        for black_heuristic in heuristics:
            # For every combination of AI mode and heuristic for white
            for white_mode in ai_modes:
                for white_heuristic in heuristics:
                    game_count += 1
                    print(
                        f"Game {game_count}: Black({black_mode}, {black_heuristic}) vs White({white_mode}, {white_heuristic})"
                    )

                    game_result = run_game(
                        white_ai_mode=white_mode,
                        white_ai_depth=3,
                        white_ai_heuristic=white_heuristic,
                        black_ai_mode=black_mode,
                        black_ai_depth=3,
                        black_ai_heuristic=black_heuristic,
                        board_size=6,
                    )

                    game_result["game_number"] = game_count
                    results.append(game_result)

    # Write results to CSV
    with open("experiment3_results.csv", "w", newline="") as csvfile:
        fieldnames = [
            "game_number",
            "black_ai_mode",
            "black_ai_heuristic",
            "white_ai_mode",
            "white_ai_heuristic",
            "black_score",
            "white_score",
            "winner",
            "turns",
            "execution_time",
            "total_runtime",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result[field] for field in fieldnames})

    return results


def run_experiment4():
    """Run experiments to compare execution time of different heuristics at various depths"""
    # Configuration
    board_size = 6
    depths = list(range(1, 5))  # From depth 1 to 10
    heuristics = ["corners_captured", "coin_parity", "mobility", "all_in_one"]
    trials_per_config = 5

    # Store results: {heuristic: {depth: avg_time}}
    time_results = {h: {d: 0 for d in depths} for h in heuristics}
    # Also store all raw results for CSV
    all_game_results = []
    game_number = 1

    for heuristic in heuristics:
        print(f"\nTesting heuristic: {heuristic}")
        for depth in depths:
            print(f"  Depth: {depth}", end=" ", flush=True)
            execution_times = []

            for trial in range(trials_per_config):
                print(".", end="", flush=True)
                game_result = run_game(
                    white_ai_mode="ab",
                    white_ai_depth=depth,
                    white_ai_heuristic=heuristic,
                    black_ai_mode="ab",
                    black_ai_depth=depth,
                    black_ai_heuristic=heuristic,
                    board_size=board_size,
                )

                # Store individual game results for CSV
                game_result["game_number"] = game_number
                game_result["depth"] = depth
                all_game_results.append(game_result)
                game_number += 1

                # Calculate average execution time (just the AI thinking time)
                avg_time = (
                    game_result["avg_black_execution_time"]
                    + game_result["avg_white_execution_time"]
                ) / 2
                execution_times.append(avg_time)

            # Store average across trials
            if execution_times:
                time_results[heuristic][depth] = mean(execution_times)
                print(f" avg: {time_results[heuristic][depth]:.2f}s")
            else:
                time_results[heuristic][depth] = 0
                print(" no valid results")

    # Save raw results to CSV
    with open("experiment4_results.csv", "w", newline="") as csvfile:
        fieldnames = [
            "game_number",
            "depth",
            "black_ai_mode",
            "black_ai_heuristic",
            "black_ai_depth",
            "white_ai_mode",
            "white_ai_heuristic",
            "black_score",
            "white_score",
            "white_ai_depth",
            "winner",
            "total_turns",
            "avg_black_execution_time",
            "avg_white_execution_time",
            "total_runtime",
            "faster_algorithm",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_game_results)

    return time_results

    # Plot results
    plt.figure(figsize=(10, 6))
    for heuristic in heuristics:
        depths_tested = list(results[heuristic].keys())
        times = [results[heuristic][d] for d in depths_tested]
        plt.plot(depths_tested, times, label=heuristic, marker="o")

    plt.title("Alpha-Beta Time by Depth")
    plt.xlabel("Depth")
    plt.ylabel("Time (s)")
    plt.legend()
    plt.grid(True)
    plt.savefig("alpha_beta_time_by_depth.png")
    plt.show()

    return results


def main():
    # Create output directory if it doesn't exist
    os.makedirs("results", exist_ok=True)

    # Run all experiments
    print("Starting Othello AI experiments...")

    # Experiment 1
    exp1_results = run_experiment1(num_games=1)
    print(f"Experiment 1 completed with {len(exp1_results)} games.")

    # Experiment 2
    # exp2_results = run_experiment2()
    # print(f"Experiment 2 completed with {len(exp2_results)} games.")

    # Experiment 3
    # exp3_results = run_experiment3()
    # print(f"Experiment 3 completed with {len(exp3_results)} games.")

    # Experiment 4
    # exp4_results = run_experiment4()
    # print(f"Experiment 4 completed with {len(exp4_results)} games.")

    print("All experiments completed! Run visualize.py to create appropriate graphs")


if __name__ == "__main__":
    main()
