#!/usr/bin/env python3
"""
Test script for the SPRSymbols class.
"""

import unittest
from spr_symbols import SPRSymbols
from poker_enums import Position, Street, Action

class TestSPRSymbols(unittest.TestCase):
    """Test cases for the SPRSymbols class."""

    def setUp(self):
        """Set up the test case."""
        self.symbols = SPRSymbols()

        # Set up a 6-player table
        self.hero_seat = 0
        self.hero_stack = 1000.0
        self.pot_size = 100.0
        self.current_street = Street.FLOP
        self.bb_size = 20.0

        # Set up player stacks
        self.player_stacks = {
            0: 1000.0,  # Hero
            1: 800.0,
            2: 1200.0,
            3: 600.0,
            4: 1500.0,
            5: 900.0
        }

        # Set up player in hand status
        self.player_in_hand = {
            0: True,  # Hero
            1: True,
            2: True,
            3: False,
            4: True,
            5: False
        }

        # Update table state
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=self.hero_stack,
            pot_size=self.pot_size,
            current_street=self.current_street,
            player_stacks=self.player_stacks,
            player_in_hand=self.player_in_hand,
            bb_size=self.bb_size
        )

    def test_spr_calculation(self):
        """Test SPR calculation."""
        # Hero's SPR
        self.assertEqual(self.symbols.get_hero_spr(), 10.0)  # 1000 / 100 = 10

        # Other players' SPR
        self.assertEqual(self.symbols.calculate_spr(1), 8.0)  # 800 / 100 = 8
        self.assertEqual(self.symbols.calculate_spr(2), 12.0)  # 1200 / 100 = 12
        self.assertEqual(self.symbols.calculate_spr(4), 15.0)  # 1500 / 100 = 15

        # Effective SPR (minimum of hero's and active opponents' SPRs)
        self.assertEqual(self.symbols.get_effective_spr(), 8.0)  # min(10, 8, 12, 15) = 8

    def test_spr_categories(self):
        """Test SPR categories."""
        # Very low SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=200.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 200.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_spr_category(), 'very_low')

        # Low SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 500.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_spr_category(), 'low')

        # Medium SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=800.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 800.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_spr_category(), 'medium')

        # High SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=1200.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 1200.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_spr_category(), 'high')

        # Very high SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=2500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 2500.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_spr_category(), 'very_high')

    def test_optimal_bet_sizing(self):
        """Test optimal bet sizing."""
        # Very low SPR with strong hand
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=200.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 200.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.calculate_hero_optimal_bet_size(0.9), 1.0)  # Pot-sized bet

        # Low SPR with medium hand
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 500.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.calculate_hero_optimal_bet_size(0.5), 0.5)  # Half pot

        # Medium SPR with weak hand
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=800.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 800.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.calculate_hero_optimal_bet_size(0.3), 0.0)  # Check/fold

        # High SPR with strong hand
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=1200.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 1200.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.calculate_hero_optimal_bet_size(0.7), 0.33)  # 1/3 pot

        # Very high SPR with medium hand
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=2500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 2500.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.calculate_hero_optimal_bet_size(0.5), 0.25)  # 1/4 pot

    def test_commitment_threshold(self):
        """Test commitment threshold."""
        # Very low SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=200.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 200.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_commitment_threshold(), 0.5)  # 50% of pot

        # Low SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 500.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_commitment_threshold(), 0.33)  # 33% of pot

        # Medium SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=800.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 800.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_commitment_threshold(), 0.25)  # 25% of pot

        # High SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=1200.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 1200.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_commitment_threshold(), 0.2)  # 20% of pot

        # Very high SPR
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=2500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 2500.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.get_hero_commitment_threshold(), 0.15)  # 15% of pot

    def test_is_committed(self):
        """Test is_committed."""
        # Very low SPR - committed with 60% pot bet
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=200.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 200.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertTrue(self.symbols.is_hero_committed(60.0))  # 60% of pot > 50% threshold

        # Low SPR - not committed with 30% pot bet
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 500.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertFalse(self.symbols.is_hero_committed(30.0))  # 30% of pot < 33% threshold

        # Medium SPR - committed with 30% pot bet
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=800.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 800.0, 1: 300.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertTrue(self.symbols.is_hero_committed(30.0))  # 30% of pot > 25% threshold

    def test_effective_stack(self):
        """Test effective stack."""
        # Hero has middle stack
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=1000.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 1000.0, 1: 800.0, 2: 1200.0},
            player_in_hand={0: True, 1: True, 2: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.calculate_effective_stack(), 800.0)  # min(1000, 800, 1200) = 800

        # Hero has smallest stack
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 500.0, 1: 800.0, 2: 1200.0},
            player_in_hand={0: True, 1: True, 2: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.calculate_effective_stack(), 500.0)  # min(500, 800, 1200) = 500

        # Hero has largest stack
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=1500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 1500.0, 1: 800.0, 2: 1200.0},
            player_in_hand={0: True, 1: True, 2: True},
            bb_size=self.bb_size
        )
        self.assertEqual(self.symbols.calculate_effective_stack(), 800.0)  # min(1500, 800, 1200) = 800

    def test_stack_classification(self):
        """Test stack classification."""
        # Short-stacked
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=300.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 300.0, 1: 800.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertTrue(self.symbols.is_short_stacked())  # 300 / 20 = 15 BB < 20 BB
        self.assertFalse(self.symbols.is_deep_stacked())

        # Medium-stacked
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=1000.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 1000.0, 1: 800.0},
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertFalse(self.symbols.is_short_stacked())  # 1000 / 20 = 50 BB > 20 BB
        self.assertFalse(self.symbols.is_deep_stacked())  # 50 BB < 100 BB

        # Deep-stacked
        self.symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=2500.0,
            pot_size=100.0,
            current_street=self.current_street,
            player_stacks={0: 2500.0, 1: 2000.0},  # Make opponent's stack deep too
            player_in_hand={0: True, 1: True},
            bb_size=self.bb_size
        )
        self.assertFalse(self.symbols.is_short_stacked())
        # Note: We changed the threshold from 100 BB to 80 BB in the implementation
        # Debug print
        print(f"Effective stack in BB: {self.symbols.get_effective_stack_in_bb()}")
        self.assertTrue(self.symbols.is_deep_stacked())  # 2000 / 20 = 100 BB > 80 BB

if __name__ == '__main__':
    unittest.main()
