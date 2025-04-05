#!/usr/bin/env python3
"""
Test script for the VerbositySymbols class.
"""

import unittest
from verbosity_symbols import VerbositySymbols
from poker_enums import Street

class TestVerbositySymbols(unittest.TestCase):
    """Test cases for the VerbositySymbols class."""
    
    def setUp(self):
        """Set up the test case."""
        self.symbols = VerbositySymbols()
        
        # Set up a sample table state
        self.current_street = Street.FLOP
        self.hero_cards = ('Ah', 'Kd')
        self.community_cards = ['Qc', 'Jd', 'Ts']
        self.made_hand_ranks = [14, 13, 12, 11, 10]  # A-K-Q-J-T straight
        
        # Update table state
        self.symbols.update_table_state(
            current_street=self.current_street,
            hero_cards=self.hero_cards,
            community_cards=self.community_cards,
            made_hand_ranks=self.made_hand_ranks
        )
        
    def test_street_identification(self):
        """Test street identification methods."""
        # Current street is flop
        self.assertFalse(self.symbols.is_preflop())
        self.assertTrue(self.symbols.is_flop())
        self.assertFalse(self.symbols.is_turn())
        self.assertFalse(self.symbols.is_river())
        self.assertTrue(self.symbols.is_postflop())
        
        # Change to preflop
        self.symbols.update_table_state(
            current_street=Street.PREFLOP,
            hero_cards=self.hero_cards,
            community_cards=[],
            made_hand_ranks=[]
        )
        
        self.assertTrue(self.symbols.is_preflop())
        self.assertFalse(self.symbols.is_flop())
        self.assertFalse(self.symbols.is_turn())
        self.assertFalse(self.symbols.is_river())
        self.assertFalse(self.symbols.is_postflop())
        
    def test_hole_card_ranks(self):
        """Test hole card rank methods."""
        self.assertEqual(self.symbols.get_rank_of_first_hole_card(), 'A')
        self.assertEqual(self.symbols.get_rank_of_second_hole_card(), 'K')
        
    def test_hole_card_suits(self):
        """Test hole card suit methods."""
        self.assertEqual(self.symbols.get_first_hole_card_suit(), 'h')
        self.assertEqual(self.symbols.get_second_hole_card_suit(), 'd')
        
    def test_community_card_ranks(self):
        """Test community card rank methods."""
        self.assertEqual(self.symbols.get_rank_of_first_flop_card(), 'Q')
        self.assertEqual(self.symbols.get_rank_of_second_flop_card(), 'J')
        self.assertEqual(self.symbols.get_rank_of_third_flop_card(), 'T')
        
        # Add turn and river cards
        community_cards = self.community_cards + ['9h', '8c']
        self.symbols.update_table_state(
            current_street=Street.RIVER,
            hero_cards=self.hero_cards,
            community_cards=community_cards,
            made_hand_ranks=self.made_hand_ranks
        )
        
        self.assertEqual(self.symbols.get_rank_of_turn_card(), '9')
        self.assertEqual(self.symbols.get_rank_of_river_card(), '8')
        
    def test_community_card_suits(self):
        """Test community card suit methods."""
        self.assertEqual(self.symbols.get_suit_of_first_flop_card(), 'c')
        self.assertEqual(self.symbols.get_suit_of_second_flop_card(), 'd')
        self.assertEqual(self.symbols.get_suit_of_third_flop_card(), 's')
        
        # Add turn and river cards
        community_cards = self.community_cards + ['9h', '8c']
        self.symbols.update_table_state(
            current_street=Street.RIVER,
            hero_cards=self.hero_cards,
            community_cards=community_cards,
            made_hand_ranks=self.made_hand_ranks
        )
        
        self.assertEqual(self.symbols.get_suit_of_turn_card(), 'h')
        self.assertEqual(self.symbols.get_suit_of_river_card(), 'c')
        
    def test_made_hand_ranks(self):
        """Test made hand rank methods."""
        self.assertEqual(self.symbols.get_made_hand_third_card_rank(), 12)  # Queen
        self.assertEqual(self.symbols.get_made_hand_fourth_card_rank(), 11)  # Jack
        self.assertEqual(self.symbols.get_made_hand_fifth_card_rank(), 10)  # Ten
        
    def test_aliases(self):
        """Test alias methods."""
        self.assertEqual(self.symbols.get_first_flop_card(), 'Q')
        self.assertEqual(self.symbols.get_second_flop_card(), 'J')
        self.assertEqual(self.symbols.get_third_flop_card(), 'T')
        
        # Add turn and river cards
        community_cards = self.community_cards + ['9h', '8c']
        self.symbols.update_table_state(
            current_street=Street.RIVER,
            hero_cards=self.hero_cards,
            community_cards=community_cards,
            made_hand_ranks=self.made_hand_ranks
        )
        
        self.assertEqual(self.symbols.get_turn_card(), '9')
        self.assertEqual(self.symbols.get_river_card(), '8')
        
        self.assertEqual(self.symbols.get_first_flop_suit(), 'c')
        self.assertEqual(self.symbols.get_second_flop_suit(), 'd')
        self.assertEqual(self.symbols.get_third_flop_suit(), 's')
        self.assertEqual(self.symbols.get_turn_suit(), 'h')
        self.assertEqual(self.symbols.get_river_suit(), 'c')
        
    def test_hand_description(self):
        """Test hand description method."""
        self.assertEqual(self.symbols.get_hand_description(), "Ace-King offsuit")
        
        # Test pocket pair
        self.symbols.update_table_state(
            current_street=self.current_street,
            hero_cards=('Ah', 'As'),
            community_cards=self.community_cards,
            made_hand_ranks=self.made_hand_ranks
        )
        
        self.assertEqual(self.symbols.get_hand_description(), "Pocket Aces")
        
        # Test suited hand
        self.symbols.update_table_state(
            current_street=self.current_street,
            hero_cards=('Qh', 'Jh'),
            community_cards=self.community_cards,
            made_hand_ranks=self.made_hand_ranks
        )
        
        self.assertEqual(self.symbols.get_hand_description(), "Queen-Jack suited (Hearts)")
        
    def test_board_description(self):
        """Test board description method."""
        self.assertEqual(self.symbols.get_board_description(), "Queen♣ Jack♦ 10♠")
        
        # Add turn and river cards
        community_cards = self.community_cards + ['9h', '8c']
        self.symbols.update_table_state(
            current_street=Street.RIVER,
            hero_cards=self.hero_cards,
            community_cards=community_cards,
            made_hand_ranks=self.made_hand_ranks
        )
        
        self.assertEqual(self.symbols.get_board_description(), "Queen♣ Jack♦ 10♠ 9♥ 8♣")
        
    def test_street_description(self):
        """Test street description method."""
        self.assertEqual(self.symbols.get_street_description(), "Flop")
        
        # Change to turn
        self.symbols.update_table_state(
            current_street=Street.TURN,
            hero_cards=self.hero_cards,
            community_cards=self.community_cards + ['9h'],
            made_hand_ranks=self.made_hand_ranks
        )
        
        self.assertEqual(self.symbols.get_street_description(), "Turn")

if __name__ == '__main__':
    unittest.main()
