"""
GeckoBot Poker - History Symbols
This module implements OpenPPL history symbols for the GeckoBot poker bot.
Based on OpenPPL_Library_History_Symbols.ohf
"""

from typing import Dict, List, Optional, Any
from poker_enums import Street, Position, Action


class HistorySymbols:
    """
    Implementation of OpenPPL history symbols for tracking action history.
    """

    def __init__(self):
        """Initialize the history symbols tracker."""
        self.reset()

    def reset(self):
        """Reset all tracking variables."""
        # Track bot's last actions by street
        self.bots_last_action = None
        self.bots_last_action_by_street = {
            Street.PREFLOP: None,
            Street.FLOP: None,
            Street.TURN: None,
            Street.RIVER: None
        }

        # Track action counts by street
        self.bets_by_street = {
            Street.PREFLOP: 0,
            Street.FLOP: 0,
            Street.TURN: 0,
            Street.RIVER: 0
        }

        self.calls_by_street = {
            Street.PREFLOP: 0,
            Street.FLOP: 0,
            Street.TURN: 0,
            Street.RIVER: 0
        }

        self.checks_by_street = {
            Street.PREFLOP: 0,
            Street.FLOP: 0,
            Street.TURN: 0,
            Street.RIVER: 0
        }

        self.raises_by_street = {
            Street.PREFLOP: 0,
            Street.FLOP: 0,
            Street.TURN: 0,
            Street.RIVER: 0
        }

        # Track action sequences
        self.preflop_action_sequence = []
        self.flop_action_sequence = []
        self.turn_action_sequence = []
        self.river_action_sequence = []

        # Track opponent actions
        self.opponents_last_action = None
        self.opponents_last_action_by_street = {
            Street.PREFLOP: None,
            Street.FLOP: None,
            Street.TURN: None,
            Street.RIVER: None
        }

        # Track stack sizes
        self.starting_stack_size = 0
        self.max_opponent_stack_size = 0
        self.min_opponent_stack_size = float('inf')

        # Track missing blinds
        self.missing_small_blind = False

    def record_action(self, street: Street, player: str, action: Action,
                     amount: Optional[float] = None, is_bot: bool = False,
                     stack_size: Optional[float] = None):
        """
        Record an action and update history symbols.

        Args:
            street: The current street (PREFLOP, FLOP, TURN, RIVER)
            player: The player making the action
            action: The action taken (FOLD, CHECK, CALL, RAISE, ALL_IN)
            amount: The bet amount (if applicable)
            is_bot: Whether this action was taken by the bot
            stack_size: The player's stack size after the action (if available)
        """
        # Record the action in the appropriate sequence
        action_data = {
            'player': player,
            'action': action,
            'amount': amount
        }

        if street == Street.PREFLOP:
            self.preflop_action_sequence.append(action_data)
        elif street == Street.FLOP:
            self.flop_action_sequence.append(action_data)
        elif street == Street.TURN:
            self.turn_action_sequence.append(action_data)
        elif street == Street.RIVER:
            self.river_action_sequence.append(action_data)

        # Update action counts
        if action == Action.RAISE or action == Action.ALL_IN:
            self.raises_by_street[street] += 1
        elif action == Action.CALL:
            self.calls_by_street[street] += 1
        elif action == Action.CHECK:
            self.checks_by_street[street] += 1

        # Update last actions
        if is_bot:
            self.bots_last_action = action
            self.bots_last_action_by_street[street] = action
        else:
            self.opponents_last_action = action
            self.opponents_last_action_by_street[street] = action

        # Update stack sizes
        if stack_size is not None and not is_bot:
            if stack_size > self.max_opponent_stack_size:
                self.max_opponent_stack_size = stack_size
            if stack_size < self.min_opponent_stack_size:
                self.min_opponent_stack_size = stack_size

    def set_starting_stack_size(self, stack_size: float):
        """Set the starting stack size."""
        self.starting_stack_size = stack_size

    def set_missing_small_blind(self, missing: bool):
        """Set whether the small blind is missing."""
        self.missing_small_blind = missing

    # OpenPPL History Symbol implementations

    def get_bots_last_action(self) -> Optional[Action]:
        """Get the bot's last action."""
        return self.bots_last_action

    def get_bots_last_preflop_action(self) -> Optional[Action]:
        """Get the bot's last preflop action."""
        return self.bots_last_action_by_street[Street.PREFLOP]

    def get_bots_last_flop_action(self) -> Optional[Action]:
        """Get the bot's last flop action."""
        return self.bots_last_action_by_street[Street.FLOP]

    def get_bots_last_turn_action(self) -> Optional[Action]:
        """Get the bot's last turn action."""
        return self.bots_last_action_by_street[Street.TURN]

    def get_bots_last_river_action(self) -> Optional[Action]:
        """Get the bot's last river action."""
        return self.bots_last_action_by_street[Street.RIVER]

    def get_opponents_last_action(self) -> Optional[Action]:
        """Get the opponent's last action."""
        return self.opponents_last_action

    def get_bets(self, street: Street) -> int:
        """Get the number of bets on the specified street."""
        return self.bets_by_street[street]

    def get_calls(self, street: Street) -> int:
        """Get the number of calls on the specified street."""
        return self.calls_by_street[street]

    def get_checks(self, street: Street) -> int:
        """Get the number of checks on the specified street."""
        return self.checks_by_street[street]

    def get_raises(self, street: Street) -> int:
        """Get the number of raises on the specified street."""
        return self.raises_by_street[street]

    def get_number_of_raises_before_flop(self) -> int:
        """Get the number of raises before the flop."""
        return self.raises_by_street[Street.PREFLOP]

    def get_number_of_raises_on_flop(self) -> int:
        """Get the number of raises on the flop."""
        return self.raises_by_street[Street.FLOP]

    def get_number_of_raises_on_turn(self) -> int:
        """Get the number of raises on the turn."""
        return self.raises_by_street[Street.TURN]

    def get_number_of_raises_on_river(self) -> int:
        """Get the number of raises on the river."""
        return self.raises_by_street[Street.RIVER]

    def has_raises_before_flop(self) -> bool:
        """Check if there were any raises before the flop."""
        return self.raises_by_street[Street.PREFLOP] > 0

    def has_raises_on_flop(self) -> bool:
        """Check if there were any raises on the flop."""
        return self.raises_by_street[Street.FLOP] > 0

    def has_raises_on_turn(self) -> bool:
        """Check if there were any raises on the turn."""
        return self.raises_by_street[Street.TURN] > 0

    def has_raises_on_river(self) -> bool:
        """Check if there were any raises on the river."""
        return self.raises_by_street[Street.RIVER] > 0

    def get_max_opponent_stack_size(self) -> float:
        """Get the maximum opponent stack size."""
        return self.max_opponent_stack_size

    def get_min_opponent_stack_size(self) -> float:
        """Get the minimum opponent stack size."""
        return self.min_opponent_stack_size if self.min_opponent_stack_size != float('inf') else 0

    def is_missing_small_blind(self) -> bool:
        """Check if the small blind is missing."""
        return self.missing_small_blind

    def get_starting_stack_size(self) -> float:
        """Get the starting stack size."""
        return self.starting_stack_size

    def get_preflop_action_history(self) -> List[Dict[str, Any]]:
        """Get the preflop action history."""
        return self.preflop_action_sequence

    def get_flop_action_history(self) -> List[Dict[str, Any]]:
        """Get the flop action history."""
        return self.flop_action_sequence

    def get_turn_action_history(self) -> List[Dict[str, Any]]:
        """Get the turn action history."""
        return self.turn_action_sequence

    def get_river_action_history(self) -> List[Dict[str, Any]]:
        """Get the river action history."""
        return self.river_action_sequence
