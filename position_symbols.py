"""
Position Symbols for OpenPPL implementation.

This module implements the advanced position symbols from OpenPPL.
"""

from typing import List, Dict, Optional, Set, Tuple
from poker_enums import Position, Street, Action
from collections import Counter

class PositionSymbols:
    """
    Implementation of OpenPPL position symbols.
    """
    
    def __init__(self):
        """Initialize the position symbols."""
        self.reset()
        
    def reset(self):
        """Reset all symbols."""
        self._hero_seat: int = -1
        self._button_seat: int = -1
        self._sb_seat: int = -1
        self._bb_seat: int = -1
        self._utg_seat: int = -1
        self._total_players: int = 0
        self._active_players: int = 0
        self._current_street: Street = Street.PREFLOP
        self._last_aggressor: int = -1
        self._first_caller: int = -1
        self._last_caller: int = -1
        self._first_raiser: int = -1
        self._last_raiser: int = -1
        self._player_positions: Dict[int, Position] = {}
        self._player_actions: Dict[int, Action] = {}
        self._player_bet_sizes: Dict[int, float] = {}
        self._player_in_hand: Dict[int, bool] = {}
        self._player_bet_positions: Dict[int, int] = {}  # Position in betting order
        
    def update_table_state(self, hero_seat: int, button_seat: int, sb_seat: int, bb_seat: int, 
                          total_players: int, active_players: int, current_street: Street,
                          player_positions: Dict[int, Position], player_in_hand: Dict[int, bool]):
        """
        Update the table state.
        
        Args:
            hero_seat: Hero's seat number
            button_seat: Button's seat number
            sb_seat: Small blind's seat number
            bb_seat: Big blind's seat number
            total_players: Total number of players at the table
            active_players: Number of active players in the hand
            current_street: Current street
            player_positions: Dictionary mapping seat numbers to positions
            player_in_hand: Dictionary mapping seat numbers to whether they're in the hand
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
        
        # Calculate UTG seat
        self._utg_seat = (self._bb_seat + 1) % self._total_players
        
    def record_action(self, seat: int, action: Action, bet_size: float, bet_position: int):
        """
        Record a player action.
        
        Args:
            seat: Player's seat number
            action: Action taken
            bet_size: Size of the bet/raise
            bet_position: Position in betting order
        """
        self._player_actions[seat] = action
        self._player_bet_sizes[seat] = bet_size
        self._player_bet_positions[seat] = bet_position
        
        # Update aggressor, callers, and raisers
        if action == Action.RAISE:
            self._last_aggressor = seat
            
            # Update first/last raiser
            if self._first_raiser == -1:
                self._first_raiser = seat
            self._last_raiser = seat
                
        elif action == Action.CALL:
            # Update first/last caller
            if self._first_caller == -1:
                self._first_caller = seat
            self._last_caller = seat
            
        elif action == Action.FOLD:
            self._player_in_hand[seat] = False
            self._active_players -= 1
            
    def get_hero_position(self) -> Position:
        """
        Get hero's position.
        
        Returns:
            Hero's position
        """
        return self._player_positions.get(self._hero_seat, None)
    
    # ---- Relative Position Symbols ----
    
    def is_early_position(self) -> bool:
        """
        Check if hero is in early position.
        
        Returns:
            True if hero is in early position, False otherwise
        """
        hero_pos = self.get_hero_position()
        return hero_pos in [Position.UTG, Position.MP]
    
    def is_middle_position(self) -> bool:
        """
        Check if hero is in middle position.
        
        Returns:
            True if hero is in middle position, False otherwise
        """
        hero_pos = self.get_hero_position()
        return hero_pos == Position.CO
    
    def is_late_position(self) -> bool:
        """
        Check if hero is in late position.
        
        Returns:
            True if hero is in late position, False otherwise
        """
        hero_pos = self.get_hero_position()
        return hero_pos in [Position.BUTTON, Position.SMALL_BLIND]
    
    def is_in_the_blinds(self) -> bool:
        """
        Check if hero is in the blinds.
        
        Returns:
            True if hero is in the blinds, False otherwise
        """
        hero_pos = self.get_hero_position()
        return hero_pos in [Position.SMALL_BLIND, Position.BIG_BLIND]
    
    def get_position_relative_to_button(self) -> int:
        """
        Get hero's position relative to the button (button = 0).
        
        Returns:
            Hero's position relative to the button
        """
        if self._hero_seat == -1 or self._button_seat == -1:
            return -1
        return (self._hero_seat - self._button_seat) % self._total_players
    
    # ---- First/Last to Act Symbols ----
    
    def is_first_to_act(self) -> bool:
        """
        Check if hero is first to act.
        
        Returns:
            True if hero is first to act, False otherwise
        """
        if self._current_street == Street.PREFLOP:
            # UTG is first to act preflop
            return self._hero_seat == self._utg_seat
        else:
            # SB is first to act postflop if still in hand, otherwise next player
            if self._player_in_hand.get(self._sb_seat, False):
                return self._hero_seat == self._sb_seat
            
            # Find the first active player after SB
            seat = (self._sb_seat + 1) % self._total_players
            while seat != self._sb_seat:
                if self._player_in_hand.get(seat, False):
                    return self._hero_seat == seat
                seat = (seat + 1) % self._total_players
                
            return False
    
    def is_last_to_act(self) -> bool:
        """
        Check if hero is last to act.
        
        Returns:
            True if hero is last to act, False otherwise
        """
        if self._current_street == Street.PREFLOP:
            # BB is last to act preflop
            return self._hero_seat == self._bb_seat
        else:
            # Button is last to act postflop if still in hand, otherwise previous player
            if self._player_in_hand.get(self._button_seat, False):
                return self._hero_seat == self._button_seat
            
            # Find the last active player before Button
            seat = (self._button_seat - 1) % self._total_players
            while seat != self._button_seat:
                if self._player_in_hand.get(seat, False):
                    return self._hero_seat == seat
                seat = (seat - 1) % self._total_players
                
            return False
    
    def get_bet_position(self) -> int:
        """
        Get hero's bet position (1 = first, n = last).
        
        Returns:
            Hero's bet position
        """
        return self._player_bet_positions.get(self._hero_seat, -1)
    
    def is_first(self) -> bool:
        """
        Check if hero is first to act in current betting round.
        
        Returns:
            True if hero is first to act, False otherwise
        """
        return self.get_bet_position() == 1
    
    def is_middle(self) -> bool:
        """
        Check if hero is in the middle of the betting order.
        
        Returns:
            True if hero is in the middle, False otherwise
        """
        bet_pos = self.get_bet_position()
        return bet_pos > 1 and bet_pos < self._active_players
    
    def is_last(self) -> bool:
        """
        Check if hero is last to act in current betting round.
        
        Returns:
            True if hero is last to act, False otherwise
        """
        return self.get_bet_position() == self._active_players
    
    # ---- Position vs Aggressor Symbols ----
    
    def get_last_aggressor(self) -> int:
        """
        Get the seat number of the last aggressor.
        
        Returns:
            Seat number of the last aggressor
        """
        return self._last_aggressor
    
    def is_in_position_vs_aggressor(self) -> bool:
        """
        Check if hero is in position versus the last aggressor.
        
        Returns:
            True if hero is in position versus the last aggressor, False otherwise
        """
        if self._last_aggressor == -1 or self._hero_seat == -1:
            return False
            
        # In position means hero acts after the aggressor
        if self._current_street == Street.PREFLOP:
            # Special case for preflop: position is relative to button
            hero_rel_pos = self.get_position_relative_to_button()
            aggressor_rel_pos = (self._last_aggressor - self._button_seat) % self._total_players
            return hero_rel_pos < aggressor_rel_pos
        else:
            # Postflop: position is clockwise from SB
            hero_rel_pos = (self._hero_seat - self._sb_seat) % self._total_players
            aggressor_rel_pos = (self._last_aggressor - self._sb_seat) % self._total_players
            return hero_rel_pos > aggressor_rel_pos
    
    def is_aggressor(self) -> bool:
        """
        Check if hero is the last aggressor.
        
        Returns:
            True if hero is the last aggressor, False otherwise
        """
        return self._hero_seat == self._last_aggressor
    
    # ---- Position vs Callers Symbols ----
    
    def get_first_caller(self) -> int:
        """
        Get the seat number of the first caller.
        
        Returns:
            Seat number of the first caller
        """
        return self._first_caller
    
    def get_last_caller(self) -> int:
        """
        Get the seat number of the last caller.
        
        Returns:
            Seat number of the last caller
        """
        return self._last_caller
    
    def get_first_raiser(self) -> int:
        """
        Get the seat number of the first raiser.
        
        Returns:
            Seat number of the first raiser
        """
        return self._first_raiser
    
    def get_last_raiser(self) -> int:
        """
        Get the seat number of the last raiser.
        
        Returns:
            Seat number of the last raiser
        """
        return self._last_raiser
    
    def get_first_caller_position(self) -> Position:
        """
        Get the position of the first caller.
        
        Returns:
            Position of the first caller
        """
        if self._first_caller == -1:
            return None
        return self._player_positions.get(self._first_caller, None)
    
    def get_last_caller_position(self) -> Position:
        """
        Get the position of the last caller.
        
        Returns:
            Position of the last caller
        """
        if self._last_caller == -1:
            return None
        return self._player_positions.get(self._last_caller, None)
    
    def get_first_raiser_position(self) -> Position:
        """
        Get the position of the first raiser.
        
        Returns:
            Position of the first raiser
        """
        if self._first_raiser == -1:
            return None
        return self._player_positions.get(self._first_raiser, None)
    
    def get_last_raiser_position(self) -> Position:
        """
        Get the position of the last raiser.
        
        Returns:
            Position of the last raiser
        """
        if self._last_raiser == -1:
            return None
        return self._player_positions.get(self._last_raiser, None)
    
    def is_in_position_vs_callers(self) -> bool:
        """
        Check if hero is in position versus all callers.
        
        Returns:
            True if hero is in position versus all callers, False otherwise
        """
        if self._hero_seat == -1:
            return False
            
        # Get all callers
        callers = [seat for seat, action in self._player_actions.items() 
                  if action == Action.CALL and self._player_in_hand.get(seat, False)]
        
        if not callers:
            return True  # No callers, so hero is in position by default
            
        # In position means hero acts after all callers
        if self._current_street == Street.PREFLOP:
            # Special case for preflop: position is relative to button
            hero_rel_pos = self.get_position_relative_to_button()
            for caller in callers:
                caller_rel_pos = (caller - self._button_seat) % self._total_players
                if hero_rel_pos >= caller_rel_pos:
                    return False
            return True
        else:
            # Postflop: position is clockwise from SB
            hero_rel_pos = (self._hero_seat - self._sb_seat) % self._total_players
            for caller in callers:
                caller_rel_pos = (caller - self._sb_seat) % self._total_players
                if hero_rel_pos <= caller_rel_pos:
                    return False
            return True
