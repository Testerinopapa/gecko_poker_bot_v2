"""
GeckoBot Poker - Betting Action Symbols
This module implements OpenPPL betting action symbols for the GeckoBot poker bot.
Based on OpenPPL_Library_Betting_Action_Symbols.ohf
"""

from typing import Dict, List, Optional, Tuple
from poker_enums import Street, Position, Action


class BettingActionSymbols:
    """
    Implementation of OpenPPL betting action symbols for tracking and analyzing betting patterns.
    """

    def __init__(self):
        """Initialize the betting action symbols tracker."""
        self.reset()

    def reset(self):
        """Reset all tracking variables."""
        # Track actions by street
        self.actions_by_street = {
            Street.PREFLOP: [],
            Street.FLOP: [],
            Street.TURN: [],
            Street.RIVER: []
        }

        # Track bot's actions by street
        self.bot_actions_by_street = {
            Street.PREFLOP: [],
            Street.FLOP: [],
            Street.TURN: [],
            Street.RIVER: []
        }

        # Track opponent actions by street
        self.opponent_actions_by_street = {
            Street.PREFLOP: [],
            Street.FLOP: [],
            Street.TURN: [],
            Street.RIVER: []
        }

        # Track last aggressor by street
        self.last_aggressor_by_street = {
            Street.PREFLOP: None,
            Street.FLOP: None,
            Street.TURN: None,
            Street.RIVER: None
        }

        # Track betting patterns
        self.is_continuation_bet_situation = False
        self.is_check_raise_situation = False
        self.is_three_bet_situation = False
        self.is_four_bet_situation = False
        self.is_donk_bet_situation = False
        self.is_probe_bet_situation = False
        self.is_float_bet_situation = False

        # Track raises on current street
        self.raises_current_street = 0
        self.calls_current_street = 0
        self.checks_current_street = 0

        # Track bot's last actions
        self.bot_last_action = None
        self.bot_last_action_by_street = {
            Street.PREFLOP: None,
            Street.FLOP: None,
            Street.TURN: None,
            Street.RIVER: None
        }

    def record_action(self, street: Street, player: str, action: Action,
                     amount: Optional[float] = None, is_bot: bool = False):
        """
        Record a betting action.

        Args:
            street: The current street (PREFLOP, FLOP, TURN, RIVER)
            player: The player making the action
            action: The action taken (FOLD, CHECK, CALL, RAISE, ALL_IN)
            amount: The bet amount (if applicable)
            is_bot: Whether this action was taken by the bot
        """
        # Record the action in the appropriate list
        action_data = {
            'player': player,
            'action': action,
            'amount': amount
        }

        self.actions_by_street[street].append(action_data)

        if is_bot:
            self.bot_actions_by_street[street].append(action_data)
            self.bot_last_action = action
            self.bot_last_action_by_street[street] = action
        else:
            self.opponent_actions_by_street[street].append(action_data)

        # Update counts
        if action == Action.RAISE or action == Action.ALL_IN:
            self.raises_current_street += 1
            self.last_aggressor_by_street[street] = player
        elif action == Action.CALL:
            self.calls_current_street += 1
        elif action == Action.CHECK:
            self.checks_current_street += 1

        # Update betting patterns
        self._update_betting_patterns(street, player, action, is_bot)

    def _update_betting_patterns(self, street: Street, player: str, action: Action, is_bot: bool):
        """Update betting pattern flags based on the current action."""
        # Continuation bet: Bot raised preflop and bets on the flop
        if (street == Street.FLOP and
            action == Action.RAISE and
            is_bot and
            self._bot_raised_preflop()):
            self.is_continuation_bet_situation = True

        # Check-raise: Player checked, someone bet, then player raised
        if (action == Action.RAISE and
            self._player_checked_this_street(player, street) and
            self._bet_after_player_checked(player, street)):
            self.is_check_raise_situation = True

        # 3-bet: There was a raise, then a re-raise
        if (action == Action.RAISE and
            self.raises_current_street >= 2):
            self.is_three_bet_situation = True

        # 4-bet: There was a raise, re-raise, and re-re-raise
        if (action == Action.RAISE and
            self.raises_current_street >= 3):
            self.is_four_bet_situation = True

        # Donk bet: Out of position player bets into previous street aggressor
        if (street != Street.PREFLOP and
            action == Action.RAISE and
            not is_bot and
            self._is_out_of_position(player) and
            self._was_bot_aggressor_previous_street(street)):
            self.is_donk_bet_situation = True

        # Probe bet: In position player bets after check from out of position player
        if (street != Street.PREFLOP and
            action == Action.RAISE and
            is_bot and
            not self._is_out_of_position(player) and
            self._opponent_checked_this_street(street)):
            self.is_probe_bet_situation = True

        # Float bet: Calling a bet on one street and betting on the next
        if (street != Street.PREFLOP and
            action == Action.RAISE and
            is_bot and
            self._bot_called_previous_street(street)):
            self.is_float_bet_situation = True

    def _bot_raised_preflop(self) -> bool:
        """Check if the bot raised preflop."""
        for action_data in self.bot_actions_by_street[Street.PREFLOP]:
            if action_data['action'] == Action.RAISE:
                return True
        return False

    def _player_checked_this_street(self, player: str, street: Street) -> bool:
        """Check if a player checked on this street before."""
        for action_data in self.actions_by_street[street]:
            if action_data['player'] == player and action_data['action'] == Action.CHECK:
                return True
        return False

    def _bet_after_player_checked(self, player: str, street: Street) -> bool:
        """Check if someone bet after the player checked."""
        player_checked = False
        for action_data in self.actions_by_street[street]:
            if action_data['player'] == player and action_data['action'] == Action.CHECK:
                player_checked = True
            elif player_checked and action_data['action'] == Action.RAISE:
                return True
        return False

    def _is_out_of_position(self, player: str) -> bool:
        """
        Determine if a player is out of position.
        This is a simplified version - in a real implementation, you would use
        the position manager to determine this.
        """
        # Placeholder - in a real implementation, use position manager
        return True

    def _was_bot_aggressor_previous_street(self, street: Street) -> bool:
        """Check if the bot was the aggressor on the previous street."""
        if street == Street.PREFLOP:
            return False

        # Map current street to previous street
        previous_street = None
        if street == Street.FLOP:
            previous_street = Street.PREFLOP
        elif street == Street.TURN:
            previous_street = Street.FLOP
        elif street == Street.RIVER:
            previous_street = Street.TURN

        if previous_street is None:
            return False

        return self.last_aggressor_by_street[previous_street] == "Bot"

    def _opponent_checked_this_street(self, street: Street) -> bool:
        """Check if any opponent checked on this street."""
        for action_data in self.opponent_actions_by_street[street]:
            if action_data['action'] == Action.CHECK:
                return True
        return False

    def _bot_called_previous_street(self, street: Street) -> bool:
        """Check if the bot called on the previous street."""
        if street == Street.PREFLOP:
            return False

        # Map current street to previous street
        previous_street = None
        if street == Street.FLOP:
            previous_street = Street.PREFLOP
        elif street == Street.TURN:
            previous_street = Street.FLOP
        elif street == Street.RIVER:
            previous_street = Street.TURN

        if previous_street is None:
            return False

        for action_data in self.bot_actions_by_street[previous_street]:
            if action_data['action'] == Action.CALL:
                return True
        return False

    # OpenPPL Betting Action Symbol implementations

    def bot_is_last_raiser(self) -> bool:
        """Check if the bot is the last raiser (aggressor)."""
        for street in reversed([Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]):
            if self.last_aggressor_by_street[street] == "Bot":
                return True
        return False

    def bot_raised_before_flop(self) -> bool:
        """Check if the bot raised before the flop."""
        return self._bot_raised_preflop()

    def bot_raised_on_flop(self) -> bool:
        """Check if the bot raised on the flop."""
        for action_data in self.bot_actions_by_street[Street.FLOP]:
            if action_data['action'] == Action.RAISE:
                return True
        return False

    def bot_raised_on_turn(self) -> bool:
        """Check if the bot raised on the turn."""
        for action_data in self.bot_actions_by_street[Street.TURN]:
            if action_data['action'] == Action.RAISE:
                return True
        return False

    def bot_raised_on_river(self) -> bool:
        """Check if the bot raised on the river."""
        for action_data in self.bot_actions_by_street[Street.RIVER]:
            if action_data['action'] == Action.RAISE:
                return True
        return False

    def bot_called_before_flop(self) -> bool:
        """Check if the bot called before the flop."""
        for action_data in self.bot_actions_by_street[Street.PREFLOP]:
            if action_data['action'] == Action.CALL:
                return True
        return False

    def bot_called_on_flop(self) -> bool:
        """Check if the bot called on the flop."""
        for action_data in self.bot_actions_by_street[Street.FLOP]:
            if action_data['action'] == Action.CALL:
                return True
        return False

    def bot_called_on_turn(self) -> bool:
        """Check if the bot called on the turn."""
        for action_data in self.bot_actions_by_street[Street.TURN]:
            if action_data['action'] == Action.CALL:
                return True
        return False

    def bot_called_on_river(self) -> bool:
        """Check if the bot called on the river."""
        for action_data in self.bot_actions_by_street[Street.RIVER]:
            if action_data['action'] == Action.CALL:
                return True
        return False

    def bot_checked_preflop(self) -> bool:
        """Check if the bot checked preflop."""
        for action_data in self.bot_actions_by_street[Street.PREFLOP]:
            if action_data['action'] == Action.CHECK:
                return True
        return False

    def bot_checked_on_flop(self) -> bool:
        """Check if the bot checked on the flop."""
        for action_data in self.bot_actions_by_street[Street.FLOP]:
            if action_data['action'] == Action.CHECK:
                return True
        return False

    def bot_checked_on_turn(self) -> bool:
        """Check if the bot checked on the turn."""
        for action_data in self.bot_actions_by_street[Street.TURN]:
            if action_data['action'] == Action.CHECK:
                return True
        return False

    def bot_checked_on_river(self) -> bool:
        """Check if the bot checked on the river."""
        for action_data in self.bot_actions_by_street[Street.RIVER]:
            if action_data['action'] == Action.CHECK:
                return True
        return False

    def bots_actions_on_this_round(self, street: Street) -> int:
        """Get the number of actions the bot has taken on this round."""
        return len(self.bot_actions_by_street[street])

    def no_betting_on_flop(self) -> bool:
        """Check if there was no betting on the flop."""
        for action_data in self.actions_by_street[Street.FLOP]:
            if action_data['action'] == Action.RAISE:
                return False
        return True

    def no_betting_on_turn(self) -> bool:
        """Check if there was no betting on the turn."""
        for action_data in self.actions_by_street[Street.TURN]:
            if action_data['action'] == Action.RAISE:
                return False
        return True

    def raises_since_last_play(self, street: Street) -> int:
        """Get the number of raises since the bot's last action."""
        if len(self.bot_actions_by_street[street]) == 0:
            return self.raises_current_street

        # Find the index of the bot's last action
        bot_actions = self.bot_actions_by_street[street]
        last_bot_action_index = -1
        for i, action_data in enumerate(self.actions_by_street[street]):
            if action_data['player'] == "Bot" and action_data == bot_actions[-1]:
                last_bot_action_index = i
                break

        # Count raises after the bot's last action
        raises_since_last_play = 0
        for i in range(last_bot_action_index + 1, len(self.actions_by_street[street])):
            if self.actions_by_street[street][i]['action'] == Action.RAISE:
                raises_since_last_play += 1

        return raises_since_last_play

    def calls_since_last_play(self, street: Street) -> int:
        """Get the number of calls since the bot's last action."""
        if len(self.bot_actions_by_street[street]) == 0:
            return self.calls_current_street

        # Find the index of the bot's last action
        bot_actions = self.bot_actions_by_street[street]
        last_bot_action_index = -1
        for i, action_data in enumerate(self.actions_by_street[street]):
            if action_data['player'] == "Bot" and action_data == bot_actions[-1]:
                last_bot_action_index = i
                break

        # Count calls after the bot's last action
        calls_since_last_play = 0
        for i in range(last_bot_action_index + 1, len(self.actions_by_street[street])):
            if self.actions_by_street[street][i]['action'] == Action.CALL:
                calls_since_last_play += 1

        return calls_since_last_play

    def is_continuation_bet(self) -> bool:
        """Check if the current situation is a continuation bet."""
        return self.is_continuation_bet_situation

    def is_check_raise(self) -> bool:
        """Check if the current situation is a check-raise."""
        return self.is_check_raise_situation

    def is_three_bet(self) -> bool:
        """Check if the current situation is a 3-bet."""
        return self.is_three_bet_situation

    def is_four_bet(self) -> bool:
        """Check if the current situation is a 4-bet."""
        return self.is_four_bet_situation

    def is_donk_bet(self) -> bool:
        """Check if the current situation is a donk bet."""
        return self.is_donk_bet_situation

    def is_probe_bet(self) -> bool:
        """Check if the current situation is a probe bet."""
        return self.is_probe_bet_situation

    def is_float_bet(self) -> bool:
        """Check if the current situation is a float bet."""
        return self.is_float_bet_situation
