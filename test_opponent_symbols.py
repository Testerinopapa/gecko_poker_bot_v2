#!/usr/bin/env python3
"""
Test script for the OpponentSymbols class.
"""

import unittest
from opponent_symbols import OpponentSymbols
from poker_enums import Position, Street, Action

class TestOpponentSymbols(unittest.TestCase):
    """Test cases for the OpponentSymbols class."""
    
    def setUp(self):
        """Set up the test case."""
        self.symbols = OpponentSymbols()
        
        # Set up a 6-player table
        self.hero_seat = 0
        self.button_seat = 5
        self.sb_seat = 0
        self.bb_seat = 1
        self.total_players = 6
        self.active_players = 6
        self.current_street = Street.PREFLOP
        
        # Set up player positions
        self.player_positions = {
            0: Position.SMALL_BLIND,  # Hero
            1: Position.BIG_BLIND,
            2: Position.UTG,
            3: Position.MP,
            4: Position.CO,
            5: Position.BUTTON
        }
        
        # Set up player in hand status
        self.player_in_hand = {
            0: True,  # Hero
            1: True,
            2: True,
            3: True,
            4: True,
            5: True
        }
        
        # Set up player stacks
        self.player_stacks = {
            0: 1000.0,  # Hero
            1: 800.0,
            2: 1200.0,
            3: 600.0,
            4: 1500.0,
            5: 900.0
        }
        
        # Set up player all-in status
        self.player_allin = {
            0: False,  # Hero
            1: False,
            2: False,
            3: False,
            4: False,
            5: False
        }
        
        # Update table state
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
    def test_opponents_left(self):
        """Test opponents left calculation."""
        # All 6 players are in the hand, so 5 opponents left
        self.assertEqual(self.symbols.get_opponents_left(), 5)
        
        # Simulate player 2 folding
        self.player_in_hand[2] = False
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # Now 4 opponents left
        self.assertEqual(self.symbols.get_opponents_left(), 4)
        
    def test_opponents_at_table(self):
        """Test opponents at table calculation."""
        # 6 players at the table, so 5 opponents
        self.assertEqual(self.symbols.get_opponents_at_table(), 5)
        
    def test_opponent_allin(self):
        """Test opponent all-in detection."""
        # No opponents are all-in
        self.assertFalse(self.symbols.is_opponent_allin())
        
        # Simulate player 3 going all-in
        self.player_allin[3] = True
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # Now an opponent is all-in
        self.assertTrue(self.symbols.is_opponent_allin())
        
    def test_number_of_opponents_allin(self):
        """Test number of opponents all-in calculation."""
        # No opponents are all-in
        self.assertEqual(self.symbols.get_number_of_opponents_allin(), 0)
        
        # Simulate players 3 and 4 going all-in
        self.player_allin[3] = True
        self.player_allin[4] = True
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # Now 2 opponents are all-in
        self.assertEqual(self.symbols.get_number_of_opponents_allin(), 2)
        
    def test_opponents_on_streets(self):
        """Test opponents on different streets."""
        # Move to flop with all players
        self.current_street = Street.FLOP
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # 5 opponents on flop
        self.assertEqual(self.symbols.get_opponents_on_flop(), 5)
        
        # Simulate players 2 and 3 folding
        self.player_in_hand[2] = False
        self.player_in_hand[3] = False
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # Move to turn with remaining players
        self.current_street = Street.TURN
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # 3 opponents on turn
        self.assertEqual(self.symbols.get_opponents_on_turn(), 3)
        
    def test_opponents_with_lower_stack(self):
        """Test opponents with lower stack calculation."""
        # Hero has 1000.0, players 1, 3, and 5 have lower stacks
        self.assertEqual(self.symbols.get_opponents_with_lower_stack(), 3)
        
        # Simulate player 1 folding
        self.player_in_hand[1] = False
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # Now only players 3 and 5 have lower stacks and are in the hand
        self.assertEqual(self.symbols.get_opponents_with_lower_stack(), 2)
        
    def test_is_hand_headsup(self):
        """Test hand heads-up detection."""
        # 6 players in the hand, not heads-up
        self.assertFalse(self.symbols.is_hand_headsup())
        
        # Simulate all but player 5 folding
        self.player_in_hand[1] = False
        self.player_in_hand[2] = False
        self.player_in_hand[3] = False
        self.player_in_hand[4] = False
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # Now the hand is heads-up
        self.assertTrue(self.symbols.is_hand_headsup())
        
    def test_is_table_headsup(self):
        """Test table heads-up detection."""
        # 6 players at the table, not heads-up
        self.assertFalse(self.symbols.is_table_headsup())
        
        # Simulate a heads-up table
        self.total_players = 2
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=self.current_street,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand,
            player_stacks=self.player_stacks,
            player_allin=self.player_allin
        )
        
        # Now the table is heads-up
        self.assertTrue(self.symbols.is_table_headsup())

if __name__ == '__main__':
    unittest.main()
