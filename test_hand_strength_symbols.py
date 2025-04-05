#!/usr/bin/env python3
"""
Test script for the HandStrengthSymbols class.
"""

import unittest
from hand_strength_symbols import HandStrengthSymbols
from poker_enums import Street

class TestHandStrengthSymbols(unittest.TestCase):
    """Test cases for the HandStrengthSymbols class."""
    
    def setUp(self):
        """Set up the test case."""
        self.symbols = HandStrengthSymbols()
        
    def test_overpair(self):
        """Test overpair detection."""
        # Overpair
        self.symbols.update_cards(['Ah', 'Ad'], ['Kh', 'Qd', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_overpair())
        
        # Not an overpair
        self.symbols.update_cards(['Kh', 'Kd'], ['Ah', 'Qd', '2c'], Street.FLOP)
        self.assertFalse(self.symbols.have_overpair())
        
    def test_top_pair(self):
        """Test top pair detection."""
        # Top pair
        self.symbols.update_cards(['Ah', 'Kd'], ['Ad', 'Qh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_top_pair())
        
        # Not top pair
        self.symbols.update_cards(['Kh', 'Qd'], ['Ad', 'Jh', '2c'], Street.FLOP)
        self.assertFalse(self.symbols.have_top_pair())
        
    def test_second_top_pair(self):
        """Test second top pair detection."""
        # Second top pair
        self.symbols.update_cards(['Qh', 'Kd'], ['Ad', 'Qd', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_second_top_pair())
        
        # Not second top pair
        self.symbols.update_cards(['Kh', 'Jd'], ['Ad', 'Qh', '2c'], Street.FLOP)
        self.assertFalse(self.symbols.have_second_top_pair())
        
    def test_set(self):
        """Test set detection."""
        # Set
        self.symbols.update_cards(['Ah', 'Ad'], ['Ac', 'Kh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_set())
        
        # Not a set
        self.symbols.update_cards(['Ah', 'Kd'], ['Qc', 'Jh', '2c'], Street.FLOP)
        self.assertFalse(self.symbols.have_set())
        
    def test_top_set(self):
        """Test top set detection."""
        # Top set
        self.symbols.update_cards(['Ah', 'Ad'], ['Ac', 'Kh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_top_set())
        
        # Not top set
        self.symbols.update_cards(['Kh', 'Kd'], ['Ac', 'Kc', '2h'], Street.FLOP)
        self.assertFalse(self.symbols.have_top_set())
        
    def test_two_pair(self):
        """Test two pair detection."""
        # Two pair
        self.symbols.update_cards(['Ah', 'Kd'], ['Ac', 'Kh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_two_pair())
        
        # Not two pair
        self.symbols.update_cards(['Ah', 'Qd'], ['Ac', 'Kh', '2c'], Street.FLOP)
        self.assertFalse(self.symbols.have_two_pair())
        
    def test_top_two_pair(self):
        """Test top two pair detection."""
        # Top two pair
        self.symbols.update_cards(['Ah', 'Kd'], ['Ac', 'Kh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_top_two_pair())
        
        # Not top two pair
        self.symbols.update_cards(['Ah', 'Qd'], ['Ac', 'Kh', 'Qc'], Street.FLOP)
        self.assertFalse(self.symbols.have_top_two_pair())
        
    def test_hand_history(self):
        """Test hand history tracking."""
        # Set up flop
        self.symbols.update_cards(['Ah', 'Kd'], ['Ac', 'Qh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_top_pair())
        
        # Move to turn
        self.symbols.update_cards(['Ah', 'Kd'], ['Ac', 'Qh', '2c', 'Kc'], Street.TURN)
        self.assertTrue(self.symbols.have_two_pair())
        self.assertTrue(self.symbols.had_top_pair_on_flop())
        
    def test_blockers(self):
        """Test blocker detection."""
        # Ace blocker
        self.symbols.update_cards(['Ah', 'Kd'], ['Qc', 'Jh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_ace_blocker())
        
        # King blocker
        self.symbols.update_cards(['Qh', 'Kd'], ['Ac', 'Jh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_king_blocker())
        
        # Flush blocker
        self.symbols.update_cards(['Ah', 'Kd'], ['Qh', 'Jh', '2h'], Street.FLOP)
        self.assertTrue(self.symbols.have_flush_blocker())
        
    def test_redraw_potential(self):
        """Test redraw potential detection."""
        # Flush redraw
        self.symbols.update_cards(['Ah', 'Kh'], ['Ad', 'Qh', '2h'], Street.FLOP)
        self.assertTrue(self.symbols.have_flush_redraw())
        
        # Straight redraw
        self.symbols.update_cards(['Ah', 'Kd'], ['Ad', 'Qh', 'Jc'], Street.FLOP)
        self.assertTrue(self.symbols.have_straight_redraw())
        
    def test_showdown_value(self):
        """Test showdown value detection."""
        # Strong showdown value
        self.symbols.update_cards(['Ah', 'Kd'], ['Ad', 'Qh', '2c'], Street.FLOP)
        self.assertTrue(self.symbols.have_strong_showdown_value())
        
        # Weak showdown value
        self.symbols.update_cards(['Ah', '2d'], ['Ad', 'Kh', 'Qc'], Street.FLOP)
        self.assertTrue(self.symbols.have_showdown_value())
        self.assertFalse(self.symbols.have_strong_showdown_value())
        self.assertTrue(self.symbols.have_weak_showdown_value())
        
    def test_hand_vs_range(self):
        """Test hand vs range equity calculation."""
        # Strong hand vs range
        self.symbols.update_cards(['Ah', 'Ad'], ['Kd', 'Qh', '2c'], Street.FLOP)
        equity = self.symbols.hand_vs_range_equity()
        self.assertGreater(equity, 0.6)
        
        # Weak hand vs range
        self.symbols.update_cards(['2h', '3d'], ['Ad', 'Kh', 'Qc'], Street.FLOP)
        equity = self.symbols.hand_vs_range_equity()
        self.assertLess(equity, 0.4)

if __name__ == '__main__':
    unittest.main()
