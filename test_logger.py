#!/usr/bin/env python3
"""
Test script for the GeckoBot logger
"""

from logger import get_logger
import time
import os

def main():
    """Test the logger functionality"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Get logger
    logger = get_logger()
    
    # Log some messages
    logger.info("Starting logger test")
    
    # Simulate a game
    logger.start_round(1)
    
    # Simulate a hand
    logger.start_hand(1)
    logger.log_hole_cards(("Ah", "Kh"))
    logger.log_blinds(10, 20)
    
    # Simulate preflop
    logger.start_street("PREFLOP")
    logger.log_action("Button", "raises", 60)
    logger.log_action("Bot", "calls", 60)
    logger.log_pot_update(140)
    
    # Simulate flop
    logger.log_community_cards("FLOP", ["2h", "7d", "Jc"])
    logger.log_win_probability("FLOP", 0.42)
    logger.start_street("FLOP")
    logger.log_action("Button", "checks")
    logger.log_action("Bot", "bets", 70)
    logger.log_action("Button", "folds")
    logger.log_pot_update(210)
    
    # End hand
    logger.end_hand(210, 30000)
    
    # Save session data
    logger.save_session_data()
    
    # Check if files were created
    log_files = os.listdir('logs')
    print(f"Log files created: {log_files}")
    
    # Print success message
    print("Logger test completed successfully!")

if __name__ == "__main__":
    main()
