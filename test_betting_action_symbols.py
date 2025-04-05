"""
Test suite for the BettingActionSymbols class.
"""

import unittest
from betting_action_symbols import BettingActionSymbols
from poker_enums import Street, Position, Action

class TestBettingActionSymbols(unittest.TestCase):
    """Test cases for the BettingActionSymbols class."""
    
    def setUp(self):
        """Set up a new BettingActionSymbols instance for each test."""
        self.symbols = BettingActionSymbols()
        
    def test_bot_raised_before_flop(self):
        """Test the bot_raised_before_flop method."""
        # Initially, the bot has not raised preflop
        self.assertFalse(self.symbols.bot_raised_before_flop())
        
        # Record a preflop raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)
        
        # Now the bot has raised preflop
        self.assertTrue(self.symbols.bot_raised_before_flop())
        
    def test_bot_is_last_raiser(self):
        """Test the bot_is_last_raiser method."""
        # Initially, the bot is not the last raiser
        self.assertFalse(self.symbols.bot_is_last_raiser())
        
        # Record a preflop raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)
        
        # Now the bot is the last raiser
        self.assertTrue(self.symbols.bot_is_last_raiser())
        
        # Record a preflop raise by an opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent", Action.RAISE, 60, is_bot=False)
        
        # Now the bot is not the last raiser
        self.assertFalse(self.symbols.bot_is_last_raiser())
        
    def test_continuation_bet(self):
        """Test the is_continuation_bet method."""
        # Initially, it's not a continuation bet situation
        self.assertFalse(self.symbols.is_continuation_bet())
        
        # Record a preflop raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)
        
        # Record a flop bet by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.RAISE, 30, is_bot=True)
        
        # Now it's a continuation bet situation
        self.assertTrue(self.symbols.is_continuation_bet())
        
    def test_check_raise(self):
        """Test the is_check_raise method."""
        # Initially, it's not a check-raise situation
        self.assertFalse(self.symbols.is_check_raise())
        
        # Record a check by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.CHECK, None, is_bot=True)
        
        # Record a bet by an opponent
        self.symbols.record_action(Street.FLOP, "Opponent", Action.RAISE, 30, is_bot=False)
        
        # Record a raise by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.RAISE, 90, is_bot=True)
        
        # Now it's a check-raise situation
        self.assertTrue(self.symbols.is_check_raise())
        
    def test_three_bet(self):
        """Test the is_three_bet method."""
        # Initially, it's not a 3-bet situation
        self.assertFalse(self.symbols.is_three_bet())
        
        # Record a raise by an opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent", Action.RAISE, 20, is_bot=False)
        
        # Record a re-raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 60, is_bot=True)
        
        # Now it's a 3-bet situation
        self.assertTrue(self.symbols.is_three_bet())
        
    def test_four_bet(self):
        """Test the is_four_bet method."""
        # Initially, it's not a 4-bet situation
        self.assertFalse(self.symbols.is_four_bet())
        
        # Record a raise by an opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent1", Action.RAISE, 20, is_bot=False)
        
        # Record a re-raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 60, is_bot=True)
        
        # Record a re-re-raise by another opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent2", Action.RAISE, 180, is_bot=False)
        
        # Now it's a 4-bet situation
        self.assertTrue(self.symbols.is_four_bet())
        
    def test_no_betting_on_flop(self):
        """Test the no_betting_on_flop method."""
        # Initially, there's no betting on the flop
        self.assertTrue(self.symbols.no_betting_on_flop())
        
        # Record a check by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.CHECK, None, is_bot=True)
        
        # Record a check by an opponent
        self.symbols.record_action(Street.FLOP, "Opponent", Action.CHECK, None, is_bot=False)
        
        # Still no betting on the flop
        self.assertTrue(self.symbols.no_betting_on_flop())
        
        # Record a bet by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.RAISE, 30, is_bot=True)
        
        # Now there is betting on the flop
        self.assertFalse(self.symbols.no_betting_on_flop())
        
    def test_raises_since_last_play(self):
        """Test the raises_since_last_play method."""
        # Initially, there are no raises since last play
        self.assertEqual(self.symbols.raises_since_last_play(Street.PREFLOP), 0)
        
        # Record a raise by an opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent1", Action.RAISE, 20, is_bot=False)
        
        # Before the bot acts, this counts as raises before first action
        self.assertEqual(self.symbols.raises_since_last_play(Street.PREFLOP), 1)
        
        # Record a call by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.CALL, 20, is_bot=True)
        
        # After the bot acts, there are no raises since last play
        self.assertEqual(self.symbols.raises_since_last_play(Street.PREFLOP), 0)
        
        # Record a raise by another opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent2", Action.RAISE, 60, is_bot=False)
        
        # Now there is one raise since last play
        self.assertEqual(self.symbols.raises_since_last_play(Street.PREFLOP), 1)
        
    def test_calls_since_last_play(self):
        """Test the calls_since_last_play method."""
        # Initially, there are no calls since last play
        self.assertEqual(self.symbols.calls_since_last_play(Street.PREFLOP), 0)
        
        # Record a raise by an opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent1", Action.RAISE, 20, is_bot=False)
        
        # Record a call by another opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent2", Action.CALL, 20, is_bot=False)
        
        # Before the bot acts, this counts as calls before first action
        self.assertEqual(self.symbols.calls_since_last_play(Street.PREFLOP), 1)
        
        # Record a raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 60, is_bot=True)
        
        # After the bot acts, there are no calls since last play
        self.assertEqual(self.symbols.calls_since_last_play(Street.PREFLOP), 0)
        
        # Record a call by another opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent3", Action.CALL, 60, is_bot=False)
        
        # Now there is one call since last play
        self.assertEqual(self.symbols.calls_since_last_play(Street.PREFLOP), 1)

if __name__ == '__main__':
    unittest.main()
