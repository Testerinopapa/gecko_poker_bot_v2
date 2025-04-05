#!/usr/bin/env python3
"""
Test script for the OpponentModeling class.
"""

import unittest
from opponent_modeling import OpponentModeling, PlayerType
from poker_enums import Position, Street, Action

class TestOpponentModeling(unittest.TestCase):
    """Test cases for the OpponentModeling class."""

    def setUp(self):
        """Set up the test case."""
        self.modeling = OpponentModeling()

        # Set up player positions
        self.player_positions = {
            0: Position.BUTTON,
            1: Position.SMALL_BLIND,
            2: Position.BIG_BLIND,
            3: Position.UTG,
            4: Position.MP,
            5: Position.CO
        }

        # Initialize a new hand
        self.modeling.new_hand(self.player_positions)

    def test_player_type_classification(self):
        """Test player type classification."""
        # Simulate a tight-passive player
        for _ in range(10):
            self.modeling.new_hand(self.player_positions)
            self.modeling.record_action(0, Action.FOLD, Position.BUTTON)

        # Player 0 should be classified as a nit or rock with our current implementation
        # In a real implementation, we'd want more hands before classifying
        player_type = self.modeling.get_player_type(0)
        self.assertTrue(player_type in [PlayerType.NIT, PlayerType.ROCK])

        # Simulate more hands to get enough data
        for _ in range(90):
            self.modeling.new_hand(self.player_positions)
            self.modeling.record_action(0, Action.FOLD, Position.BUTTON)

        # Player 0 should now be classified as a nit or rock
        player_type = self.modeling.get_player_type(0)
        self.assertTrue(player_type in [PlayerType.NIT, PlayerType.ROCK])

        # Simulate a loose-aggressive player
        for _ in range(100):
            self.modeling.new_hand(self.player_positions)
            self.modeling.record_action(1, Action.RAISE, Position.SMALL_BLIND)

        # Player 1 should be classified as loose-aggressive or maniac
        player_type = self.modeling.get_player_type(1)
        self.assertTrue(player_type in [PlayerType.LOOSE_AGGRESSIVE, PlayerType.MANIAC])

    def test_vpip_calculation(self):
        """Test VPIP calculation."""
        # Simulate 10 hands where player 0 voluntarily puts money in pot 5 times
        for i in range(10):
            self.modeling.new_hand(self.player_positions)
            if i < 5:
                self.modeling.record_action(0, Action.CALL, Position.BUTTON)
            else:
                self.modeling.record_action(0, Action.FOLD, Position.BUTTON)

        # VPIP should be 50%
        self.assertAlmostEqual(self.modeling.get_player_vpip(0), 0.5)

    def test_pfr_calculation(self):
        """Test PFR calculation."""
        # Simulate 10 hands where player 0 raises preflop 3 times
        for i in range(10):
            self.modeling.new_hand(self.player_positions)
            if i < 3:
                self.modeling.record_action(0, Action.RAISE, Position.BUTTON)
            else:
                self.modeling.record_action(0, Action.FOLD, Position.BUTTON)

        # PFR should be 30%
        self.assertAlmostEqual(self.modeling.get_player_pfr(0), 0.3)

    def test_af_calculation(self):
        """Test AF calculation."""
        # Simulate a player with 5 aggressive actions and 10 passive actions
        self.modeling.new_hand(self.player_positions)

        # 5 aggressive actions (raises)
        for _ in range(5):
            self.modeling.record_action(0, Action.RAISE, Position.BUTTON)

        # 10 passive actions (calls)
        for _ in range(10):
            self.modeling.record_action(0, Action.CALL, Position.BUTTON)

        # AF should be 0.5
        self.assertAlmostEqual(self.modeling.get_player_af(0), 0.5)

    def test_cbet_frequency(self):
        """Test continuation bet frequency calculation."""
        # Simulate 10 hands where player 0 has 5 c-bet opportunities and c-bets 3 times
        for i in range(5):
            self.modeling.new_hand(self.player_positions)
            self.modeling.record_action(0, Action.RAISE, Position.BUTTON)  # Preflop raise
            self.modeling.new_street(Street.FLOP)
            if i < 3:
                self.modeling.record_action(0, Action.RAISE, Position.BUTTON)  # C-bet
            else:
                self.modeling.record_action(0, Action.CHECK, Position.BUTTON)  # Check

        # C-bet frequency should be 60%
        self.assertAlmostEqual(self.modeling.get_player_cbet_frequency(0), 0.6)

    def test_position_based_stats(self):
        """Test position-based stats calculation."""
        # Simulate 10 hands where player 0 is on the button and VPIPs 5 times
        for i in range(10):
            self.modeling.new_hand(self.player_positions)
            if i < 5:
                self.modeling.record_action(0, Action.CALL, Position.BUTTON)
            else:
                self.modeling.record_action(0, Action.FOLD, Position.BUTTON)

        # Button VPIP should be 50%
        self.assertAlmostEqual(self.modeling.get_player_position_vpip(0, Position.BUTTON), 0.5)

    def test_fold_equity_calculation(self):
        """Test fold equity calculation."""
        # Simulate a player who folds to c-bets 70% of the time
        for i in range(10):
            self.modeling.new_hand(self.player_positions)
            self.modeling.record_action(0, Action.CALL, Position.BUTTON)  # Preflop call
            self.modeling.new_street(Street.FLOP)
            if i < 3:
                self.modeling.record_action(0, Action.CALL, Position.BUTTON)  # Call c-bet
            else:
                self.modeling.record_action(0, Action.FOLD, Position.BUTTON)  # Fold to c-bet

        # Fold equity on flop should be 70%
        self.assertAlmostEqual(self.modeling.calculate_fold_equity(0, Street.FLOP), 0.7)

    def test_optimal_bet_size(self):
        """Test optimal bet size calculation."""
        # Simulate a tight-passive player
        for _ in range(100):
            self.modeling.new_hand(self.player_positions)
            self.modeling.record_action(0, Action.FOLD, Position.BUTTON)

        # Force player type to tight-passive for testing
        self.modeling._player_profiles[0].player_type = PlayerType.TIGHT_PASSIVE

        # Optimal bet size with strong hand should be 75% of pot
        self.assertAlmostEqual(self.modeling.calculate_optimal_bet_size(0, Street.FLOP, 0.8), 0.75)

        # Optimal bet size with weak hand should be 50% of pot
        self.assertAlmostEqual(self.modeling.calculate_optimal_bet_size(0, Street.FLOP, 0.3), 0.5)

    def test_should_bluff(self):
        """Test bluffing decision."""
        # Simulate a tight-passive player
        for _ in range(100):
            self.modeling.new_hand(self.player_positions)
            self.modeling.record_action(0, Action.FOLD, Position.BUTTON)

        # Force player type to tight-passive for testing
        self.modeling._player_profiles[0].player_type = PlayerType.TIGHT_PASSIVE

        # Should bluff against tight-passive players
        self.assertTrue(self.modeling.should_bluff(0, Street.FLOP))

        # Simulate a calling station
        for _ in range(100):
            self.modeling.new_hand(self.player_positions)
            self.modeling.record_action(1, Action.CALL, Position.SMALL_BLIND)

        # Force player type to calling station for testing
        self.modeling._player_profiles[1].player_type = PlayerType.CALLING_STATION

        # Should not bluff against calling stations
        self.assertFalse(self.modeling.should_bluff(1, Street.FLOP))

if __name__ == '__main__':
    unittest.main()
