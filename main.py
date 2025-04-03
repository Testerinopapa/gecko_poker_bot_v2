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
    logger.info("Starting simulation mode")
    game = GameRunner()
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
    """
    Main entry point for the GeckoBot poker program
    """
    parser = argparse.ArgumentParser(description="GeckoBot Poker - A Python-based poker bot")
    
    # Mode selection
    parser.add_argument('--mode', choices=['simulate', 'analyze'], default='simulate',
                      help='Operating mode (simulate or analyze)')
    
    # Simulation mode options
    parser.add_argument('--auto', action='store_true',
                      help='Run simulation automatically without prompting')
    parser.add_argument('--num-hands', type=int,
                      help='Number of hands to simulate (default: infinite)')
    
    # Analysis mode options
    parser.add_argument('--hand', type=str,
                      help='Specific hand to analyze (e.g., "Ah Kh")')
    parser.add_argument('--opponents', type=int,
                      help='Number of opponents for equity calculation')
    
    # General options
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.mode == 'simulate':
            run_simulation_mode(args)
        elif args.mode == 'analyze':
            run_analysis_mode(args)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 