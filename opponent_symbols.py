"""
Opponent Symbols for OpenPPL implementation.

This module implements the opponent-related symbols from OpenPPL.
"""

from typing import Dict, List, Optional, Tuple
from poker_enums import Position, Street, Action

class OpponentSymbols:
    """
    Implementation of OpenPPL opponent symbols.
    
    This class implements the opponent-related symbols from OpenPPL,
    focusing on basic opponent counting and tracking.
    """
    
    def __init__(self):
        """Initialize the opponent symbols."""
        self.reset()
        
    def reset(self):
        """Reset all symbols."""
        self._hero_seat: int = -1
        self._button_seat: int = -1
        self._sb_seat: int = -1
        self._bb_seat: int = -1
        self._total_players: int = 0
        self._active_players: int = 0
        self._current_street: Street = Street.PREFLOP
        self._player_positions: Dict[int, Position] = {}
        self._player_in_hand: Dict[int, bool] = {}
        self._player_stacks: Dict[int, float] = {}
        self._player_allin: Dict[int, bool] = {}
        self._players_on_street: Dict[Street, int] = {
            Street.PREFLOP: 0,
            Street.FLOP: 0,
            Street.TURN: 0,
            Street.RIVER: 0
        }
        
    def update_table_state(self, hero_seat: int, button_seat: int, sb_seat: int, bb_seat: int,
                          total_players: int, active_players: int, current_street: Street,
                          player_positions: Dict[int, Position], player_in_hand: Dict[int, bool],
                          player_stacks: Dict[int, float], player_allin: Dict[int, bool] = None):
        """
        Update the table state.
        
        Args:
            hero_seat: Hero's seat number
            button_seat: Button seat number
            sb_seat: Small blind seat number
            bb_seat: Big blind seat number
            total_players: Total number of players at the table
            active_players: Number of active players (not sitting out)
            current_street: Current street
            player_positions: Dictionary mapping seat numbers to positions
            player_in_hand: Dictionary mapping seat numbers to whether they're in the hand
            player_stacks: Dictionary mapping seat numbers to stack sizes
            player_allin: Dictionary mapping seat numbers to whether they're all-in
        """
        self._hero_seat = hero_seat
        self._button_seat = button_seat
        self._sb_seat = sb_seat
        self._bb_seat = bb_seat
        self._total_players = total_players
        self._active_players = active_players
        self._current_street = current_street
        self._player_positions = player_positions
        self._player_in_hand = player_in_hand
        self._player_stacks = player_stacks
        self._player_allin = player_allin or {}
        
        # Count players on current street
        self._players_on_street[current_street] = sum(1 for in_hand in player_in_hand.values() if in_hand)
    
    def record_action(self, seat: int, action: Action, amount: float, bet_position: int):
        """
        Record a player action.
        
        Args:
            seat: Player's seat number
            action: Action taken
            amount: Amount bet/raised
            bet_position: Position in the betting order
        """
        # Update player's in-hand status if they folded
        if action == Action.FOLD and seat in self._player_in_hand:
            self._player_in_hand[seat] = False
            
        # Update player's all-in status if they went all-in
        if action == Action.RAISE and seat in self._player_stacks and amount >= self._player_stacks[seat]:
            self._player_allin[seat] = True
    
    def get_opponents_left(self) -> int:
        """
        Get the number of opponents left in the hand.
        
        Returns:
            Number of opponents left
        """
        # Count players in hand excluding hero
        return sum(1 for seat, in_hand in self._player_in_hand.items() 
                  if in_hand and seat != self._hero_seat)
    
    def get_opponents_at_table(self) -> int:
        """
        Get the number of opponents at the table.
        
        Returns:
            Number of opponents at the table
        """
        # Total players minus hero
        return self._total_players - 1
    
    def is_opponent_allin(self) -> bool:
        """
        Check if any opponent is all-in.
        
        Returns:
            True if any opponent is all-in, False otherwise
        """
        return any(allin for seat, allin in self._player_allin.items() if seat != self._hero_seat)
    
    def get_number_of_opponents_allin(self) -> int:
        """
        Get the number of opponents who are all-in.
        
        Returns:
            Number of opponents all-in
        """
        return sum(1 for seat, allin in self._player_allin.items() 
                  if allin and seat != self._hero_seat)
    
    def get_opponents_on_flop(self) -> int:
        """
        Get the number of opponents on the flop.
        
        Returns:
            Number of opponents on the flop
        """
        return self._players_on_street[Street.FLOP] - 1 if self._players_on_street[Street.FLOP] > 0 else 0
    
    def get_opponents_on_turn(self) -> int:
        """
        Get the number of opponents on the turn.
        
        Returns:
            Number of opponents on the turn
        """
        return self._players_on_street[Street.TURN] - 1 if self._players_on_street[Street.TURN] > 0 else 0
    
    def get_opponents_on_river(self) -> int:
        """
        Get the number of opponents on the river.
        
        Returns:
            Number of opponents on the river
        """
        return self._players_on_street[Street.RIVER] - 1 if self._players_on_street[Street.RIVER] > 0 else 0
    
    def get_opponents_with_lower_stack(self) -> int:
        """
        Get the number of opponents with a lower stack than hero.
        
        Returns:
            Number of opponents with a lower stack
        """
        if self._hero_seat not in self._player_stacks:
            return 0
            
        hero_stack = self._player_stacks[self._hero_seat]
        return sum(1 for seat, stack in self._player_stacks.items() 
                  if stack < hero_stack and seat != self._hero_seat and self._player_in_hand.get(seat, False))
    
    def is_hand_headsup(self) -> bool:
        """
        Check if the hand is heads-up (only two players competing).
        
        Returns:
            True if the hand is heads-up, False otherwise
        """
        return sum(1 for in_hand in self._player_in_hand.values() if in_hand) == 2
    
    def is_table_headsup(self) -> bool:
        """
        Check if the table is heads-up (only two players at the table).
        
        Returns:
            True if the table is heads-up, False otherwise
        """
        return self._total_players == 2
