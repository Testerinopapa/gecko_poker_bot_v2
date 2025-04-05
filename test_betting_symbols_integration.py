#!/usr/bin/env python3
"""
Test script for the BettingActionSymbols integration with GeckoBot.
"""

from table_state import TableState
from poker_enums import Street, Position, Action
from betting_action_symbols import BettingActionSymbols

def test_betting_symbols():
    """Test the BettingActionSymbols integration."""
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
    
    # Hero 3-bets
    table_state.record_action(1, Action.RAISE, 180)
    print(f"Hero 3-bets to 180")
    
    # Check if it's a 3-bet situation
    is_three_bet = table_state.betting_symbols.is_three_bet()
    print(f"Is 3-bet situation: {is_three_bet}")
    
    # Big blind 4-bets
    table_state.record_action(2, Action.RAISE, 540)
    print(f"Big blind 4-bets to 540")
    
    # Check if it's a 4-bet situation
    is_four_bet = table_state.betting_symbols.is_four_bet()
    print(f"Is 4-bet situation: {is_four_bet}")
    
    # Hero calls
    table_state.record_action(1, Action.CALL, 360)
    print(f"Hero calls 360")
    
    # Button folds
    table_state.record_action(0, Action.FOLD)
    print(f"Button folds")
    
    # Test flop actions
    print("\n=== Testing Flop Actions ===")
    
    # Move to flop
    table_state.new_street(Street.FLOP)
    print(f"Moving to flop")
    
    # Big blind checks
    table_state.record_action(2, Action.CHECK)
    print(f"Big blind checks")
    
    # Hero bets (continuation bet)
    table_state.record_action(1, Action.RAISE, 300)
    print(f"Hero bets 300")
    
    # Check if it's a continuation bet
    is_cbet = table_state.betting_symbols.is_continuation_bet()
    print(f"Is continuation bet: {is_cbet}")
    
    # Big blind check-raises
    table_state.record_action(2, Action.RAISE, 900)
    print(f"Big blind check-raises to 900")
    
    # Check if it's a check-raise
    is_check_raise = table_state.betting_symbols.is_check_raise()
    print(f"Is check-raise: {is_check_raise}")
    
    # Test turn actions
    print("\n=== Testing Turn Actions ===")
    
    # Hero calls
    table_state.record_action(1, Action.CALL, 600)
    print(f"Hero calls 600")
    
    # Move to turn
    table_state.new_street(Street.TURN)
    print(f"Moving to turn")
    
    # Big blind checks
    table_state.record_action(2, Action.CHECK)
    print(f"Big blind checks")
    
    # Hero bets (float bet)
    table_state.record_action(1, Action.RAISE, 1200)
    print(f"Hero bets 1200")
    
    # Check if it's a float bet
    is_float = table_state.betting_symbols.is_float_bet()
    print(f"Is float bet: {is_float}")
    
    # Test river actions
    print("\n=== Testing River Actions ===")
    
    # Big blind folds
    table_state.record_action(2, Action.FOLD)
    print(f"Big blind folds")
    
    # Move to river
    table_state.new_street(Street.RIVER)
    print(f"Moving to river")
    
    # Test new hand
    print("\n=== Testing New Hand ===")
    
    # Reset for new hand
    table_state.new_hand()
    print(f"Starting new hand")
    
    # Check if betting symbols were reset
    is_three_bet = table_state.betting_symbols.is_three_bet()
    is_four_bet = table_state.betting_symbols.is_four_bet()
    is_cbet = table_state.betting_symbols.is_continuation_bet()
    is_check_raise = table_state.betting_symbols.is_check_raise()
    is_float = table_state.betting_symbols.is_float_bet()
    
    print(f"After reset:")
    print(f"Is 3-bet situation: {is_three_bet}")
    print(f"Is 4-bet situation: {is_four_bet}")
    print(f"Is continuation bet: {is_cbet}")
    print(f"Is check-raise: {is_check_raise}")
    print(f"Is float bet: {is_float}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_betting_symbols()
