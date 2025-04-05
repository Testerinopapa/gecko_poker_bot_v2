#!/usr/bin/env python3
"""
Test script for the HistorySymbols integration with GeckoBot.
"""

from table_state import TableState
from poker_enums import Street, Position, Action
from history_symbols import HistorySymbols

def test_history_symbols():
    """Test the HistorySymbols integration."""
    # Create a table state
    table_state = TableState()
    
    # Initialize players
    table_state.hero_seat = 1
    table_state.button_seat = 0
    table_state.total_players = 3
    
    # Initialize player stacks
    for seat in range(3):
        position = Position.BUTTON if seat == 0 else \
                  Position.SMALL_BLIND if seat == 1 else \
                  Position.BIG_BLIND
        table_state.update_player(
            seat=seat,
            stack=30000,
            position=position,
            in_hand=True
        )
    
    # Test preflop actions
    print("=== Testing Preflop Actions ===")
    
    # Button raises
    table_state.record_action(0, Action.RAISE, 60)
    print(f"Button raises to 60")
    
    # Hero calls
    table_state.record_action(1, Action.CALL, 60)
    print(f"Hero calls 60")
    
    # Big blind folds
    table_state.record_action(2, Action.FOLD)
    print(f"Big blind folds")
    
    # Check history symbols
    print(f"Bot's last action: {table_state.history_symbols.get_bots_last_action()}")
    print(f"Bot's last preflop action: {table_state.history_symbols.get_bots_last_preflop_action()}")
    print(f"Opponent's last action: {table_state.history_symbols.get_opponents_last_action()}")
    print(f"Number of raises preflop: {table_state.history_symbols.get_number_of_raises_before_flop()}")
    print(f"Preflop action history: {table_state.history_symbols.get_preflop_action_history()}")
    
    # Test flop actions
    print("\n=== Testing Flop Actions ===")
    
    # Move to flop
    table_state.new_street(Street.FLOP)
    print(f"Moving to flop")
    
    # Button checks
    table_state.record_action(0, Action.CHECK)
    print(f"Button checks")
    
    # Hero bets
    table_state.record_action(1, Action.RAISE, 100)
    print(f"Hero bets 100")
    
    # Button calls
    table_state.record_action(0, Action.CALL, 100)
    print(f"Button calls 100")
    
    # Check history symbols
    print(f"Bot's last action: {table_state.history_symbols.get_bots_last_action()}")
    print(f"Bot's last flop action: {table_state.history_symbols.get_bots_last_flop_action()}")
    print(f"Opponent's last action: {table_state.history_symbols.get_opponents_last_action()}")
    print(f"Number of raises on flop: {table_state.history_symbols.get_number_of_raises_on_flop()}")
    print(f"Flop action history: {table_state.history_symbols.get_flop_action_history()}")
    
    # Test turn actions
    print("\n=== Testing Turn Actions ===")
    
    # Move to turn
    table_state.new_street(Street.TURN)
    print(f"Moving to turn")
    
    # Button bets
    table_state.record_action(0, Action.RAISE, 200)
    print(f"Button bets 200")
    
    # Hero raises
    table_state.record_action(1, Action.RAISE, 600)
    print(f"Hero raises to 600")
    
    # Button folds
    table_state.record_action(0, Action.FOLD)
    print(f"Button folds")
    
    # Check history symbols
    print(f"Bot's last action: {table_state.history_symbols.get_bots_last_action()}")
    print(f"Bot's last turn action: {table_state.history_symbols.get_bots_last_turn_action()}")
    print(f"Opponent's last action: {table_state.history_symbols.get_opponents_last_action()}")
    print(f"Number of raises on turn: {table_state.history_symbols.get_number_of_raises_on_turn()}")
    print(f"Turn action history: {table_state.history_symbols.get_turn_action_history()}")
    
    # Test new hand
    print("\n=== Testing New Hand ===")
    
    # Reset for new hand
    table_state.new_hand()
    print(f"Starting new hand")
    
    # Check if history symbols were reset
    print(f"Bot's last action: {table_state.history_symbols.get_bots_last_action()}")
    print(f"Opponent's last action: {table_state.history_symbols.get_opponents_last_action()}")
    print(f"Number of raises preflop: {table_state.history_symbols.get_number_of_raises_before_flop()}")
    print(f"Preflop action history: {table_state.history_symbols.get_preflop_action_history()}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_history_symbols()
