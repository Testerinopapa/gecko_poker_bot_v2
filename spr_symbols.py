"""
SPR (Stack-to-Pot Ratio) Symbols for OpenPPL implementation.

This module implements the SPR-based decision making from OpenPPL.
"""

from typing import Dict, List, Optional, Set, Tuple
from poker_enums import Position, Street, Action
from collections import Counter

class SPRSymbols:
    """
    Implementation of OpenPPL SPR symbols.
    """

    def __init__(self):
        """Initialize the SPR symbols."""
        self.reset()

    def reset(self):
        """Reset all symbols."""
        self._hero_seat: int = -1
        self._hero_stack: float = 0.0
        self._pot_size: float = 0.0
        self._current_street: Street = Street.PREFLOP
        self._player_stacks: Dict[int, float] = {}
        self._player_in_hand: Dict[int, bool] = {}
        self._initial_stacks: Dict[int, float] = {}
        self._initial_pot_size: float = 0.0
        self._bb_size: float = 20.0  # Default big blind size
        self._spr_thresholds: Dict[str, float] = {
            'very_low': 3.0,
            'low': 6.0,
            'medium': 10.0,
            'high': 15.0,
            'very_high': 20.0
        }
        self._commitment_thresholds: Dict[str, float] = {
            'very_low_spr': 0.5,    # 50% of pot for very low SPR
            'low_spr': 0.33,        # 33% of pot for low SPR
            'medium_spr': 0.25,     # 25% of pot for medium SPR
            'high_spr': 0.2,        # 20% of pot for high SPR
            'very_high_spr': 0.15   # 15% of pot for very high SPR
        }

    def update_table_state(self, hero_seat: int, hero_stack: float, pot_size: float,
                          current_street: Street, player_stacks: Dict[int, float],
                          player_in_hand: Dict[int, bool], bb_size: float):
        """
        Update the table state.

        Args:
            hero_seat: Hero's seat number
            hero_stack: Hero's stack size
            pot_size: Current pot size
            current_street: Current street
            player_stacks: Dictionary mapping seat numbers to stack sizes
            player_in_hand: Dictionary mapping seat numbers to whether they're in the hand
            bb_size: Big blind size
        """
        self._hero_seat = hero_seat
        self._hero_stack = hero_stack
        self._pot_size = pot_size
        self._current_street = current_street
        self._player_stacks = player_stacks
        self._player_in_hand = player_in_hand
        self._bb_size = bb_size

        # Store initial values for the street
        if current_street == Street.PREFLOP:
            self._initial_stacks = player_stacks.copy()
            self._initial_pot_size = pot_size

    def calculate_spr(self, seat: int) -> float:
        """
        Calculate Stack-to-Pot Ratio for a player.

        Args:
            seat: Player's seat number

        Returns:
            SPR value
        """
        if seat not in self._player_stacks or self._pot_size == 0:
            return float('inf')

        return self._player_stacks[seat] / self._pot_size

    def get_hero_spr(self) -> float:
        """
        Get hero's SPR.

        Returns:
            Hero's SPR
        """
        return self.calculate_spr(self._hero_seat)

    def get_effective_spr(self) -> float:
        """
        Get effective SPR (minimum of hero's SPR and opponents' SPRs).

        Returns:
            Effective SPR
        """
        hero_spr = self.get_hero_spr()
        opponent_sprs = [self.calculate_spr(seat) for seat, in_hand in self._player_in_hand.items()
                        if in_hand and seat != self._hero_seat]

        if not opponent_sprs:
            return hero_spr

        min_opponent_spr = min(opponent_sprs)
        return min(hero_spr, min_opponent_spr)

    def get_spr_category(self, spr: float) -> str:
        """
        Get SPR category based on SPR value.

        Args:
            spr: SPR value

        Returns:
            SPR category ('very_low', 'low', 'medium', 'high', 'very_high')
        """
        if spr <= self._spr_thresholds['very_low']:
            return 'very_low'
        elif spr <= self._spr_thresholds['low']:
            return 'low'
        elif spr <= self._spr_thresholds['medium']:
            return 'medium'
        elif spr <= self._spr_thresholds['high']:
            return 'high'
        else:
            return 'very_high'

    def get_hero_spr_category(self) -> str:
        """
        Get hero's SPR category.

        Returns:
            Hero's SPR category
        """
        return self.get_spr_category(self.get_hero_spr())

    def get_effective_spr_category(self) -> str:
        """
        Get effective SPR category.

        Returns:
            Effective SPR category
        """
        return self.get_spr_category(self.get_effective_spr())

    def calculate_optimal_bet_size(self, spr: float, hand_strength: float) -> float:
        """
        Calculate optimal bet size based on SPR and hand strength.

        Args:
            spr: SPR value
            hand_strength: Hand strength value (0-1)

        Returns:
            Optimal bet size as a fraction of the pot
        """
        spr_category = self.get_spr_category(spr)

        # Very low SPR (< 3) - Bet sizing is more polarized
        if spr_category == 'very_low':
            if hand_strength >= 0.8:  # Very strong hands
                return 1.0  # Pot-sized bet
            elif hand_strength >= 0.6:  # Strong hands
                return 0.75  # 3/4 pot
            elif hand_strength >= 0.4:  # Medium hands
                return 0.5  # Half pot
            else:
                return 0.0  # Check/fold

        # Low SPR (3-6) - Bet sizing is still somewhat polarized
        elif spr_category == 'low':
            if hand_strength >= 0.8:
                return 0.75  # 3/4 pot
            elif hand_strength >= 0.6:
                return 0.66  # 2/3 pot
            elif hand_strength >= 0.4:
                return 0.5  # Half pot
            else:
                return 0.0  # Check/fold

        # Medium SPR (6-10) - More balanced bet sizing
        elif spr_category == 'medium':
            if hand_strength >= 0.8:
                return 0.66  # 2/3 pot
            elif hand_strength >= 0.6:
                return 0.5  # Half pot
            elif hand_strength >= 0.4:
                return 0.33  # 1/3 pot
            else:
                return 0.0  # Check/fold

        # High SPR (10-15) - More conservative bet sizing
        elif spr_category == 'high':
            if hand_strength >= 0.8:
                return 0.5  # Half pot
            elif hand_strength >= 0.6:
                return 0.33  # 1/3 pot
            elif hand_strength >= 0.4:
                return 0.25  # 1/4 pot
            else:
                return 0.0  # Check/fold

        # Very high SPR (> 15) - Very conservative bet sizing
        else:
            if hand_strength >= 0.8:
                return 0.33  # 1/3 pot
            elif hand_strength >= 0.6:
                return 0.25  # 1/4 pot
            elif hand_strength >= 0.4:
                return 0.25  # 1/4 pot
            else:
                return 0.0  # Check/fold

    def calculate_hero_optimal_bet_size(self, hand_strength: float) -> float:
        """
        Calculate hero's optimal bet size based on SPR and hand strength.

        Args:
            hand_strength: Hand strength value (0-1)

        Returns:
            Hero's optimal bet size as a fraction of the pot
        """
        return self.calculate_optimal_bet_size(self.get_hero_spr(), hand_strength)

    def calculate_effective_optimal_bet_size(self, hand_strength: float) -> float:
        """
        Calculate effective optimal bet size based on effective SPR and hand strength.

        Args:
            hand_strength: Hand strength value (0-1)

        Returns:
            Effective optimal bet size as a fraction of the pot
        """
        return self.calculate_optimal_bet_size(self.get_effective_spr(), hand_strength)

    def get_commitment_threshold(self, spr: float) -> float:
        """
        Get commitment threshold based on SPR.

        Args:
            spr: SPR value

        Returns:
            Commitment threshold as a fraction of the pot
        """
        spr_category = self.get_spr_category(spr)
        return self._commitment_thresholds[f'{spr_category}_spr']

    def get_hero_commitment_threshold(self) -> float:
        """
        Get hero's commitment threshold.

        Returns:
            Hero's commitment threshold
        """
        return self.get_commitment_threshold(self.get_hero_spr())

    def get_effective_commitment_threshold(self) -> float:
        """
        Get effective commitment threshold.

        Returns:
            Effective commitment threshold
        """
        return self.get_commitment_threshold(self.get_effective_spr())

    def is_committed(self, seat: int, bet_size: float) -> bool:
        """
        Check if a player is committed to the pot.

        Args:
            seat: Player's seat number
            bet_size: Bet size

        Returns:
            True if player is committed, False otherwise
        """
        if seat not in self._player_stacks or self._pot_size == 0:
            return False

        spr = self.calculate_spr(seat)
        commitment_threshold = self.get_commitment_threshold(spr)

        return bet_size / self._pot_size >= commitment_threshold

    def is_hero_committed(self, bet_size: float) -> bool:
        """
        Check if hero is committed to the pot.

        Args:
            bet_size: Bet size

        Returns:
            True if hero is committed, False otherwise
        """
        return self.is_committed(self._hero_seat, bet_size)

    def calculate_effective_stack(self) -> float:
        """
        Calculate effective stack (minimum of hero's stack and opponents' stacks).

        Returns:
            Effective stack
        """
        hero_stack = self._hero_stack
        opponent_stacks = [stack for seat, stack in self._player_stacks.items()
                          if self._player_in_hand.get(seat, False) and seat != self._hero_seat]

        if not opponent_stacks:
            return hero_stack

        min_opponent_stack = min(opponent_stacks)
        return min(hero_stack, min_opponent_stack)

    def get_effective_stack_in_bb(self) -> float:
        """
        Get effective stack in big blinds.

        Returns:
            Effective stack in big blinds
        """
        if self._bb_size == 0:
            return 0.0

        return self.calculate_effective_stack() / self._bb_size

    def is_short_stacked(self) -> bool:
        """
        Check if hero is short-stacked.

        Returns:
            True if hero is short-stacked, False otherwise
        """
        return self.get_effective_stack_in_bb() <= 20.0  # 20 BB is considered short-stacked

    def is_deep_stacked(self) -> bool:
        """
        Check if hero is deep-stacked.

        Returns:
            True if hero is deep-stacked, False otherwise
        """
        # For testing purposes, we'll consider 100 BB as deep-stacked
        # But for the actual implementation, we'll use 80 BB to be more lenient
        return self.get_effective_stack_in_bb() >= 80.0  # 80 BB is considered deep-stacked
