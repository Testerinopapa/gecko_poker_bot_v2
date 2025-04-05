#!/usr/bin/env python3
"""
Test script for the PositionSymbols class.
"""

import unittest
from position_symbols import PositionSymbols
from poker_enums import Position, Street, Action

class TestPositionSymbols(unittest.TestCase):
    """Test cases for the PositionSymbols class."""
    
    def setUp(self):
        """Set up the test case."""
        self.symbols = PositionSymbols()
        
        # Set up a 6-player table
        self.button_seat = 0
        self.sb_seat = 1
        self.bb_seat = 2
        self.utg_seat = 3
        self.mp_seat = 4
        self.co_seat = 5
        
        # Set up player positions
        self.player_positions = {
            0: Position.BUTTON,
            1: Position.SMALL_BLIND,
            2: Position.BIG_BLIND,
            3: Position.UTG,
            4: Position.MP,
            5: Position.CO
        }
        
        # Set up player in hand status
        self.player_in_hand = {
            0: True,
            1: True,
            2: True,
            3: True,
            4: True,
            5: True
        }
        
    def test_relative_position(self):
        """Test relative position symbols."""
        # Hero is UTG
        self.symbols.update_table_state(
            hero_seat=self.utg_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertTrue(self.symbols.is_early_position())
        self.assertFalse(self.symbols.is_middle_position())
        self.assertFalse(self.symbols.is_late_position())
        self.assertFalse(self.symbols.is_in_the_blinds())
        
        # Hero is CO
        self.symbols.update_table_state(
            hero_seat=self.co_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertFalse(self.symbols.is_early_position())
        self.assertTrue(self.symbols.is_middle_position())
        self.assertFalse(self.symbols.is_late_position())
        self.assertFalse(self.symbols.is_in_the_blinds())
        
        # Hero is Button
        self.symbols.update_table_state(
            hero_seat=self.button_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertFalse(self.symbols.is_early_position())
        self.assertFalse(self.symbols.is_middle_position())
        self.assertTrue(self.symbols.is_late_position())
        self.assertFalse(self.symbols.is_in_the_blinds())
        
        # Hero is SB
        self.symbols.update_table_state(
            hero_seat=self.sb_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertFalse(self.symbols.is_early_position())
        self.assertFalse(self.symbols.is_middle_position())
        self.assertTrue(self.symbols.is_late_position())
        self.assertTrue(self.symbols.is_in_the_blinds())
        
        # Hero is BB
        self.symbols.update_table_state(
            hero_seat=self.bb_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertFalse(self.symbols.is_early_position())
        self.assertFalse(self.symbols.is_middle_position())
        self.assertFalse(self.symbols.is_late_position())
        self.assertTrue(self.symbols.is_in_the_blinds())
        
    def test_first_last_to_act(self):
        """Test first/last to act symbols."""
        # Hero is UTG (first to act preflop)
        self.symbols.update_table_state(
            hero_seat=self.utg_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertTrue(self.symbols.is_first_to_act())
        self.assertFalse(self.symbols.is_last_to_act())
        
        # Hero is BB (last to act preflop)
        self.symbols.update_table_state(
            hero_seat=self.bb_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertFalse(self.symbols.is_first_to_act())
        self.assertTrue(self.symbols.is_last_to_act())
        
        # Hero is SB (first to act postflop)
        self.symbols.update_table_state(
            hero_seat=self.sb_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.FLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertTrue(self.symbols.is_first_to_act())
        self.assertFalse(self.symbols.is_last_to_act())
        
        # Hero is Button (last to act postflop)
        self.symbols.update_table_state(
            hero_seat=self.button_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.FLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertFalse(self.symbols.is_first_to_act())
        self.assertTrue(self.symbols.is_last_to_act())
        
    def test_position_vs_aggressor(self):
        """Test position vs aggressor symbols."""
        # Set up a scenario where UTG raises
        self.symbols.update_table_state(
            hero_seat=self.button_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        # UTG raises
        self.symbols.record_action(
            seat=self.utg_seat,
            action=Action.RAISE,
            bet_size=2.0,
            bet_position=1
        )
        
        # Hero is Button (in position vs UTG)
        self.assertTrue(self.symbols.is_in_position_vs_aggressor())
        self.assertFalse(self.symbols.is_aggressor())
        
        # Hero is UTG (aggressor)
        self.symbols.update_table_state(
            hero_seat=self.utg_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertFalse(self.symbols.is_in_position_vs_aggressor())
        self.assertTrue(self.symbols.is_aggressor())
        
    def test_position_vs_callers(self):
        """Test position vs callers symbols."""
        # Set up a scenario where UTG and MP call
        self.symbols.update_table_state(
            hero_seat=self.button_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        # UTG calls
        self.symbols.record_action(
            seat=self.utg_seat,
            action=Action.CALL,
            bet_size=1.0,
            bet_position=1
        )
        
        # MP calls
        self.symbols.record_action(
            seat=self.mp_seat,
            action=Action.CALL,
            bet_size=1.0,
            bet_position=2
        )
        
        # Hero is Button (in position vs all callers)
        self.assertTrue(self.symbols.is_in_position_vs_callers())
        
        # First caller is UTG
        self.assertEqual(self.symbols.get_first_caller(), self.utg_seat)
        self.assertEqual(self.symbols.get_first_caller_position(), Position.UTG)
        
        # Last caller is MP
        self.assertEqual(self.symbols.get_last_caller(), self.mp_seat)
        self.assertEqual(self.symbols.get_last_caller_position(), Position.MP)
        
        # Hero is UTG (not in position vs all callers)
        self.symbols.update_table_state(
            hero_seat=self.utg_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=6,
            active_players=6,
            current_street=Street.PREFLOP,
            player_positions=self.player_positions,
            player_in_hand=self.player_in_hand
        )
        
        self.assertFalse(self.symbols.is_in_position_vs_callers())

if __name__ == '__main__':
    unittest.main()
