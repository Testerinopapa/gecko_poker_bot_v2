from typing import Dict, List, Optional, Tuple
from poker_enums import Position, Street, Action
from dataclasses import dataclass

@dataclass
class Player:
    stack: float
    position: Position
    has_position: bool
    in_hand: bool
    last_action: Optional[Action] = None
    last_bet_size: float = 0.0

class TableState:
    def __init__(self):
        self.players: Dict[int, Player] = {}
        self.hero_seat: int = -1
        self.button_seat: int = -1
        self.pot_size: float = 0.0
        self.current_street: Street = Street.PREFLOP
        self.community_cards: List[str] = []
        self.hero_cards: Tuple[str, str] = ('', '')
        self.current_bet: float = 0.0
        self.min_raise: float = 0.0
        self.last_aggressor: Optional[int] = None
        self.total_players: int = 0
        self.active_players: int = 0
        self.hero_stack: float = 0.0  # Hero's current stack
        self.bb_size: float = 20.0  # Big blind size

    def update_player(self, seat: int, stack: float, position: Position, 
                     in_hand: bool, last_action: Optional[Action] = None,
                     last_bet_size: float = 0.0):
        has_position = position in [Position.BUTTON, Position.CO]
        self.players[seat] = Player(stack, position, has_position, 
                                  in_hand, last_action, last_bet_size)
        if seat == self.hero_seat:
            self.hero_stack = stack

    def get_hero_position(self) -> Position:
        return self.players[self.hero_seat].position if self.hero_seat in self.players else None

    def get_pot_odds(self, call_amount: float) -> float:
        return call_amount / (self.pot_size + call_amount) if call_amount > 0 else 0.0

    def get_spr(self, seat: int) -> float:
        """Calculate Stack to Pot Ratio"""
        if seat not in self.players or self.pot_size == 0:
            return float('inf')
        return self.players[seat].stack / self.pot_size

    def get_active_players_count(self) -> int:
        return sum(1 for p in self.players.values() if p.in_hand)

    def is_heads_up(self) -> bool:
        return self.get_active_players_count() == 2

    def is_multiway(self) -> bool:
        return self.get_active_players_count() > 2

    def get_effective_stack(self) -> float:
        """Get the smallest stack among active players"""
        active_stacks = [p.stack for p in self.players.values() if p.in_hand]
        return min(active_stacks) if active_stacks else 0.0

    def get_position_relative_to_button(self, seat: int) -> int:
        """Get position relative to button (button = 0)"""
        if seat not in self.players or self.button_seat == -1:
            return -1
        return (seat - self.button_seat) % len(self.players)

    def is_in_position(self, seat: int) -> bool:
        """Check if player is in position relative to active players"""
        if seat not in self.players:
            return False
        return self.players[seat].has_position 