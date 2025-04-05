"""
Test suite for the HistorySymbols class.
"""

import unittest
from history_symbols import HistorySymbols
from poker_enums import Street, Action

class TestHistorySymbols(unittest.TestCase):
    """Test cases for the HistorySymbols class."""

    def setUp(self):
        """Set up a new HistorySymbols instance for each test."""
        self.symbols = HistorySymbols()

    def test_bots_last_action(self):
        """Test the get_bots_last_action method."""
        # Initially, the bot has no last action
        self.assertIsNone(self.symbols.get_bots_last_action())

        # Record a preflop raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)

        # Now the bot's last action is RAISE
        self.assertEqual(self.symbols.get_bots_last_action(), Action.RAISE)

        # Record a flop check by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.CHECK, None, is_bot=True)

        # Now the bot's last action is CHECK
        self.assertEqual(self.symbols.get_bots_last_action(), Action.CHECK)

    def test_bots_last_street_actions(self):
        """Test the get_bots_last_preflop_action, get_bots_last_flop_action, etc. methods."""
        # Record a preflop raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)

        # Record a flop check by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.CHECK, None, is_bot=True)

        # Record a turn bet by the bot
        self.symbols.record_action(Street.TURN, "Bot", Action.RAISE, 40, is_bot=True)

        # Record a river call by the bot
        self.symbols.record_action(Street.RIVER, "Bot", Action.CALL, 80, is_bot=True)

        # Check that the last actions by street are correct
        self.assertEqual(self.symbols.get_bots_last_preflop_action(), Action.RAISE)
        self.assertEqual(self.symbols.get_bots_last_flop_action(), Action.CHECK)
        self.assertEqual(self.symbols.get_bots_last_turn_action(), Action.RAISE)
        self.assertEqual(self.symbols.get_bots_last_river_action(), Action.CALL)

    def test_action_counts(self):
        """Test the get_bets, get_calls, get_checks, and get_raises methods."""
        # Record a preflop raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)

        # Record a preflop call by an opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent1", Action.CALL, 20, is_bot=False)

        # Record a flop check by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.CHECK, None, is_bot=True)

        # Record a flop check by an opponent
        self.symbols.record_action(Street.FLOP, "Opponent1", Action.CHECK, None, is_bot=False)

        # Record a flop bet by another opponent
        self.symbols.record_action(Street.FLOP, "Opponent2", Action.RAISE, 40, is_bot=False)

        # Check that the action counts are correct
        self.assertEqual(self.symbols.get_raises(Street.PREFLOP), 1)
        self.assertEqual(self.symbols.get_calls(Street.PREFLOP), 1)
        self.assertEqual(self.symbols.get_checks(Street.FLOP), 2)
        self.assertEqual(self.symbols.get_raises(Street.FLOP), 1)

    def test_number_of_raises(self):
        """Test the get_number_of_raises_before_flop, get_number_of_raises_on_flop, etc. methods."""
        # Record a preflop raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)

        # Record a preflop re-raise by an opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent1", Action.RAISE, 60, is_bot=False)

        # Record a flop bet by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.RAISE, 40, is_bot=True)

        # Record a turn bet by an opponent
        self.symbols.record_action(Street.TURN, "Opponent1", Action.RAISE, 80, is_bot=False)

        # Check that the number of raises are correct
        self.assertEqual(self.symbols.get_number_of_raises_before_flop(), 2)
        self.assertEqual(self.symbols.get_number_of_raises_on_flop(), 1)
        self.assertEqual(self.symbols.get_number_of_raises_on_turn(), 1)
        self.assertEqual(self.symbols.get_number_of_raises_on_river(), 0)

        # Check the boolean methods
        self.assertTrue(self.symbols.has_raises_before_flop())
        self.assertTrue(self.symbols.has_raises_on_flop())
        self.assertTrue(self.symbols.has_raises_on_turn())
        self.assertFalse(self.symbols.has_raises_on_river())

    def test_stack_sizes(self):
        """Test the get_max_opponent_stack_size, get_min_opponent_stack_size, and get_starting_stack_size methods."""
        # Set the starting stack size
        self.symbols.set_starting_stack_size(1000)

        # Record actions with stack sizes
        self.symbols.record_action(Street.PREFLOP, "Opponent1", Action.RAISE, 20, is_bot=False, stack_size=800)
        self.symbols.record_action(Street.PREFLOP, "Opponent2", Action.CALL, 20, is_bot=False, stack_size=1200)
        self.symbols.record_action(Street.PREFLOP, "Opponent3", Action.FOLD, None, is_bot=False, stack_size=500)

        # Check that the stack sizes are correct
        self.assertEqual(self.symbols.get_starting_stack_size(), 1000)
        self.assertEqual(self.symbols.get_max_opponent_stack_size(), 1200)
        self.assertEqual(self.symbols.get_min_opponent_stack_size(), 500)

    def test_missing_small_blind(self):
        """Test the is_missing_small_blind method."""
        # Initially, the small blind is not missing
        self.assertFalse(self.symbols.is_missing_small_blind())

        # Set the small blind as missing
        self.symbols.set_missing_small_blind(True)

        # Now the small blind is missing
        self.assertTrue(self.symbols.is_missing_small_blind())

    def test_action_history(self):
        """Test the get_preflop_action_history, get_flop_action_history, etc. methods."""
        # Record a preflop raise by the bot
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)

        # Record a preflop call by an opponent
        self.symbols.record_action(Street.PREFLOP, "Opponent1", Action.CALL, 20, is_bot=False)

        # Record a flop check by the bot
        self.symbols.record_action(Street.FLOP, "Bot", Action.CHECK, None, is_bot=True)

        # Record a flop bet by an opponent
        self.symbols.record_action(Street.FLOP, "Opponent1", Action.RAISE, 40, is_bot=False)

        # Check that the action histories are correct
        preflop_history = self.symbols.get_preflop_action_history()
        flop_history = self.symbols.get_flop_action_history()

        self.assertEqual(len(preflop_history), 2)
        self.assertEqual(preflop_history[0]['player'], "Bot")
        self.assertEqual(preflop_history[0]['action'], Action.RAISE)
        self.assertEqual(preflop_history[0]['amount'], 20)
        self.assertEqual(preflop_history[1]['player'], "Opponent1")
        self.assertEqual(preflop_history[1]['action'], Action.CALL)
        self.assertEqual(preflop_history[1]['amount'], 20)

        self.assertEqual(len(flop_history), 2)
        self.assertEqual(flop_history[0]['player'], "Bot")
        self.assertEqual(flop_history[0]['action'], Action.CHECK)
        self.assertIsNone(flop_history[0]['amount'])
        self.assertEqual(flop_history[1]['player'], "Opponent1")
        self.assertEqual(flop_history[1]['action'], Action.RAISE)
        self.assertEqual(flop_history[1]['amount'], 40)

    def test_reset(self):
        """Test the reset method."""
        # Record some actions
        self.symbols.record_action(Street.PREFLOP, "Bot", Action.RAISE, 20, is_bot=True)
        self.symbols.record_action(Street.PREFLOP, "Opponent1", Action.CALL, 20, is_bot=False)

        # Reset the symbols
        self.symbols.reset()

        # Check that everything is reset
        self.assertIsNone(self.symbols.get_bots_last_action())
        self.assertIsNone(self.symbols.get_bots_last_preflop_action())
        self.assertEqual(self.symbols.get_raises(Street.PREFLOP), 0)
        self.assertEqual(self.symbols.get_calls(Street.PREFLOP), 0)
        self.assertEqual(len(self.symbols.get_preflop_action_history()), 0)

if __name__ == '__main__':
    unittest.main()
