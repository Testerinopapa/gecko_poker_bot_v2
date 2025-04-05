#!/usr/bin/env python3
"""
GeckoBot Poker - A Python-based poker bot
"""

import argparse
import logging
from typing import Optional
from game_runner import GameRunner
from gecko_bot import GeckoBot
from table_state import TableState
from hand_evaluator import HandEvaluator
from position_manager import PositionManager
from visualization.match_visualizer import MatchVisualizer
from logger import DebugLevel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_bot(config: Optional[dict] = None) -> GeckoBot:
    """
    Initialize the bot with optional configuration
    """
    bot = GeckoBot()
    if config:
        # TODO: Apply configuration options
        pass
    return bot

def run_simulation_mode(args):
    """
    Run the bot in simulation mode for testing strategies
    """
    # Set debug level
    debug_level = DebugLevel.NONE
    if args.verbose == 1:
        debug_level = DebugLevel.INFO
    elif args.verbose == 2:
        debug_level = DebugLevel.DEBUG
    elif args.verbose >= 3:
        debug_level = DebugLevel.TRACE

    logger.info(f"Starting simulation mode with debug level: {debug_level.name}")
    game = GameRunner(debug_level=debug_level)
    game.setup_game()

    num_hands = args.num_hands or float('inf')
    hands_played = 0

    try:
        while hands_played < num_hands:
            game.run_hand()
            hands_played += 1

            if not args.auto:
                response = input("\nPlay another hand? (y/n): ")
                if response.lower() != 'y':
                    break
    except KeyboardInterrupt:
        logger.info("\nSimulation stopped by user")
    finally:
        logger.info(f"Simulation complete. Hands played: {hands_played}")

        # Generate visualizations
        if hands_played > 0:
            logger.info("Generating performance visualizations...")
            game.visualizer.plot_stack_progression()
            game.visualizer.plot_win_probabilities()
            game.visualizer.plot_position_performance()
            game.visualizer.plot_action_frequencies()
            game.visualizer.generate_summary_dashboard()

            # Print text summary
            print("\n" + game.visualizer.generate_text_summary())

            logger.info("Visualizations saved to current directory")

def run_analysis_mode(args):
    """
    Analyze specific hands or situations
    """
    logger.info("Starting analysis mode")
    hand_evaluator = HandEvaluator()

    # Example hand analysis
    if args.hand:
        hole_cards = tuple(args.hand.split())
        if len(hole_cards) == 2:
            strength = hand_evaluator.evaluate_hand_strength(hole_cards, [])
            logger.info(f"Hand strength for {args.hand}: {strength}")

            # Calculate preflop equity
            equity = hand_evaluator.calculate_prwin(hole_cards, [], num_opponents=args.opponents or 1)
            logger.info(f"Preflop equity vs {args.opponents or 1} opponent(s): {equity:.2%}")

def main():
    print("Starting GeckoBot Poker...")
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='GeckoBot Poker')
    parser.add_argument('--auto', action='store_true', help='Run in automatic mode without user input')
    parser.add_argument('--num_hands', type=int, default=10, help='Number of hands to play (default: 10)')
    parser.add_argument('--simulation', action='store_true', help='Run in simulation mode')
    parser.add_argument('--analysis', action='store_true', help='Run in analysis mode')
    parser.add_argument('--hand', type=str, help='Hand to analyze (e.g., "Ah Kd")')
    parser.add_argument('--opponents', type=int, default=1, help='Number of opponents for analysis')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase verbosity level (can be used multiple times)')
    args = parser.parse_args()

    from game_runner import GameRunner
    from logger import get_logger
    import os

    # Set debug level
    debug_level = DebugLevel.NONE
    if args.verbose == 1:
        debug_level = DebugLevel.INFO
    elif args.verbose == 2:
        debug_level = DebugLevel.DEBUG
    elif args.verbose >= 3:
        debug_level = DebugLevel.TRACE

    # Get logger
    logger = get_logger(debug_level=debug_level)

    # Debug print
    print(f"Logger initialized with session ID: {logger.session_id}")
    print(f"Log directory: {logger.log_dir}")
    print(f"Log directory exists: {os.path.exists(logger.log_dir)}")

    # Create GameRunner with debug level
    runner = GameRunner(debug_level=debug_level)

    logger.info("=== Starting GeckoBot Poker Game ===")

    # Run the specified number of hands
    num_hands = args.num_hands
    for i in range(num_hands):
        logger.start_round(i+1)
        runner.setup_game()
        runner.run_hand()

        # If not in auto mode, ask user if they want to continue
        if not args.auto and i < num_hands - 1:
            response = input("\nPlay another hand? (y/n): ")
            if response.lower() != 'y':
                break

    logger.info("=== Game Complete ===")
    logger.info("Thanks for playing!")

    # Save session data for analysis
    logger.save_session_data()

    # Debug print
    print(f"Session data saved to: {os.path.join(logger.log_dir, f'geckobot_{logger.session_id}_data.json')}")
    print(f"File exists: {os.path.exists(os.path.join(logger.log_dir, f'geckobot_{logger.session_id}_data.json'))}")

if __name__ == "__main__":
    main()