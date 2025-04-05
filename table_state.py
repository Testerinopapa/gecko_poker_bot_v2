from typing import Dict, List, Optional, Tuple
from poker_enums import Position, Street, Action
from dataclasses import dataclass
from betting_action_symbols import BettingActionSymbols
from history_symbols import HistorySymbols
from board_texture_symbols import BoardTextureSymbols
from hand_strength_symbols import HandStrengthSymbols
from outs_calculator import OutsCalculator
from position_symbols import PositionSymbols
from spr_symbols import SPRSymbols
from opponent_modeling import OpponentModeling

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

        # Initialize betting action symbols tracker
        self.betting_symbols = BettingActionSymbols()

        # Initialize history symbols tracker
        self.history_symbols = HistorySymbols()

        # Initialize board texture symbols tracker
        self.board_texture_symbols = BoardTextureSymbols()

        # Initialize hand strength symbols tracker
        self.hand_strength_symbols = HandStrengthSymbols()

        # Initialize outs calculator
        self.outs_calculator = OutsCalculator()

        # Initialize position symbols
        self.position_symbols = PositionSymbols()

        # Initialize SPR symbols
        self.spr_symbols = SPRSymbols()

        # Initialize opponent modeling
        self.opponent_modeling = OpponentModeling()

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

    def record_action(self, seat: int, action: Action, amount: Optional[float] = None):
        """Record a player action and update the betting action symbols and history symbols."""
        if seat not in self.players:
            return

        # Update player's last action
        self.players[seat].last_action = action
        if amount is not None:
            self.players[seat].last_bet_size = amount

        # Update table state based on action
        if action == Action.FOLD:
            self.players[seat].in_hand = False
            self.active_players -= 1
        elif action == Action.RAISE or action == Action.ALL_IN:
            self.last_aggressor = seat
            if amount is not None:
                self.current_bet = amount

        # Record action in betting symbols tracker
        player_name = "Bot" if seat == self.hero_seat else f"Player_{seat}"
        is_bot = seat == self.hero_seat
        self.betting_symbols.record_action(self.current_street, player_name, action, amount, is_bot)

        # Record action in history symbols tracker
        stack_size = self.players[seat].stack
        self.history_symbols.record_action(self.current_street, player_name, action, amount, is_bot, stack_size)

        # Update position symbols
        # Get the bet position (index in the actions list for the current street)
        actions = self.betting_symbols.actions_by_street[self.current_street]
        bet_position = len(actions) - 1 if actions else 0
        self.position_symbols.record_action(seat, action, amount or 0.0, bet_position)

        # Update opponent modeling
        position = self.players[seat].position if seat in self.players else Position.BUTTON
        self.opponent_modeling.record_action(seat, action, position)

    def new_hand(self):
        """Reset state for a new hand."""
        self.pot_size = 0.0
        self.current_street = Street.PREFLOP
        self.community_cards = []
        self.hero_cards = ('', '')
        self.current_bet = 0.0
        self.min_raise = 0.0
        self.last_aggressor = None
        self.active_players = self.total_players

        # Reset betting action symbols
        self.betting_symbols.reset()

        # Reset history symbols
        self.history_symbols.reset()

        # Reset board texture symbols
        self.board_texture_symbols.reset()

        # Reset hand strength symbols
        self.hand_strength_symbols.reset()

        # Reset outs calculator
        self.outs_calculator.reset()

        # Reset position symbols
        self.position_symbols.reset()

        # Reset SPR symbols
        self.spr_symbols.reset()

        # Reset opponent modeling
        player_positions = {seat: player.position for seat, player in self.players.items()}
        self.opponent_modeling.new_hand(player_positions)

        # Set starting stack size in history symbols
        if self.hero_seat in self.players:
            self.history_symbols.set_starting_stack_size(self.players[self.hero_seat].stack)

        # Reset player actions
        for seat in self.players:
            self.players[seat].last_action = None
            self.players[seat].last_bet_size = 0.0
            self.players[seat].in_hand = True

    def new_street(self, street: Street):
        """Update state for a new betting street."""
        self.current_street = street
        self.current_bet = 0.0
        self.min_raise = 0.0

        # Update board texture symbols
        if len(self.community_cards) > 0:
            self.board_texture_symbols.update_board(self.community_cards, street)

        # Update hand strength symbols
        if self.hero_cards[0] and self.hero_cards[1]:
            self.hand_strength_symbols.update_cards([self.hero_cards[0], self.hero_cards[1]], self.community_cards, street)

            # Update outs calculator
            self.outs_calculator.update_cards([self.hero_cards[0], self.hero_cards[1]], self.community_cards, street)

        # Update position symbols
        player_positions = {seat: player.position for seat, player in self.players.items()}
        player_in_hand = {seat: player.in_hand for seat, player in self.players.items()}
        self.position_symbols.update_table_state(
            hero_seat=self.hero_seat,
            button_seat=self.button_seat,
            sb_seat=self.sb_seat,
            bb_seat=self.bb_seat,
            total_players=self.total_players,
            active_players=self.active_players,
            current_street=street,
            player_positions=player_positions,
            player_in_hand=player_in_hand
        )

        # Update SPR symbols
        player_stacks = {seat: player.stack for seat, player in self.players.items()}
        hero_stack = self.players[self.hero_seat].stack if self.hero_seat in self.players else 0.0
        self.spr_symbols.update_table_state(
            hero_seat=self.hero_seat,
            hero_stack=hero_stack,
            pot_size=self.pot_size,
            current_street=street,
            player_stacks=player_stacks,
            player_in_hand=player_in_hand,
            bb_size=self.bb_size
        )

        # Update opponent modeling
        self.opponent_modeling.new_street(street)

    def update_hero_cards(self, cards: Tuple[str, str]):
        """Update hero's hole cards."""
        self.hero_cards = cards

        # Update hand strength symbols
        if self.hero_cards[0] and self.hero_cards[1]:
            self.hand_strength_symbols.update_cards([self.hero_cards[0], self.hero_cards[1]], self.community_cards, self.current_street)

            # Update outs calculator
            self.outs_calculator.update_cards([self.hero_cards[0], self.hero_cards[1]], self.community_cards, self.current_street)

    def update_community_cards(self, cards: List[str]):
        """Update community cards."""
        self.community_cards = cards

        # Update board texture symbols
        if len(self.community_cards) > 0:
            self.board_texture_symbols.update_board(self.community_cards, self.current_street)

        # Update hand strength symbols
        if self.hero_cards[0] and self.hero_cards[1]:
            self.hand_strength_symbols.update_cards([self.hero_cards[0], self.hero_cards[1]], self.community_cards, self.current_street)

            # Update outs calculator
            self.outs_calculator.update_cards([self.hero_cards[0], self.hero_cards[1]], self.community_cards, self.current_street)

    def get_equity_from_outs(self) -> float:
        """Get equity from outs calculation."""
        return self.outs_calculator.calculate_equity_from_outs()

    def get_outs_description(self) -> str:
        """Get a description of the outs."""
        return self.outs_calculator.get_outs_description()

    # ---- Position Symbols Methods ----

    def is_early_position(self) -> bool:
        """Check if hero is in early position."""
        return self.position_symbols.is_early_position()

    def is_middle_position(self) -> bool:
        """Check if hero is in middle position."""
        return self.position_symbols.is_middle_position()

    def is_late_position(self) -> bool:
        """Check if hero is in late position."""
        return self.position_symbols.is_late_position()

    def is_in_the_blinds(self) -> bool:
        """Check if hero is in the blinds."""
        return self.position_symbols.is_in_the_blinds()

    def is_first_to_act(self) -> bool:
        """Check if hero is first to act."""
        return self.position_symbols.is_first_to_act()

    def is_last_to_act(self) -> bool:
        """Check if hero is last to act."""
        return self.position_symbols.is_last_to_act()

    def is_first(self) -> bool:
        """Check if hero is first to act in current betting round."""
        return self.position_symbols.is_first()

    def is_middle(self) -> bool:
        """Check if hero is in the middle of the betting order."""
        return self.position_symbols.is_middle()

    def is_last(self) -> bool:
        """Check if hero is last to act in current betting round."""
        return self.position_symbols.is_last()

    def is_in_position_vs_aggressor(self) -> bool:
        """Check if hero is in position versus the last aggressor."""
        return self.position_symbols.is_in_position_vs_aggressor()

    def is_aggressor(self) -> bool:
        """Check if hero is the last aggressor."""
        return self.position_symbols.is_aggressor()

    def is_in_position_vs_callers(self) -> bool:
        """Check if hero is in position versus all callers."""
        return self.position_symbols.is_in_position_vs_callers()

    def get_first_caller_position(self) -> Position:
        """Get the position of the first caller."""
        return self.position_symbols.get_first_caller_position()

    def get_last_caller_position(self) -> Position:
        """Get the position of the last caller."""
        return self.position_symbols.get_last_caller_position()

    def get_first_raiser_position(self) -> Position:
        """Get the position of the first raiser."""
        return self.position_symbols.get_first_raiser_position()

    def get_last_raiser_position(self) -> Position:
        """Get the position of the last raiser."""
        return self.position_symbols.get_last_raiser_position()

    # ---- SPR Symbols Methods ----

    def get_spr(self) -> float:
        """Get hero's SPR."""
        return self.spr_symbols.get_hero_spr()

    def get_effective_spr(self) -> float:
        """Get effective SPR."""
        return self.spr_symbols.get_effective_spr()

    def get_spr_category(self) -> str:
        """Get hero's SPR category."""
        return self.spr_symbols.get_hero_spr_category()

    def get_effective_spr_category(self) -> str:
        """Get effective SPR category."""
        return self.spr_symbols.get_effective_spr_category()

    def calculate_optimal_bet_size(self, hand_strength: float) -> float:
        """Calculate optimal bet size based on SPR and hand strength."""
        return self.spr_symbols.calculate_hero_optimal_bet_size(hand_strength)

    def calculate_effective_optimal_bet_size(self, hand_strength: float) -> float:
        """Calculate effective optimal bet size based on effective SPR and hand strength."""
        return self.spr_symbols.calculate_effective_optimal_bet_size(hand_strength)

    def get_commitment_threshold(self) -> float:
        """Get hero's commitment threshold."""
        return self.spr_symbols.get_hero_commitment_threshold()

    def is_committed(self, bet_size: float) -> bool:
        """Check if hero is committed to the pot."""
        return self.spr_symbols.is_hero_committed(bet_size)

    def get_effective_stack(self) -> float:
        """Calculate effective stack."""
        return self.spr_symbols.calculate_effective_stack()

    def get_effective_stack_in_bb(self) -> float:
        """Get effective stack in big blinds."""
        return self.spr_symbols.get_effective_stack_in_bb()

    def is_short_stacked(self) -> bool:
        """Check if hero is short-stacked."""
        return self.spr_symbols.is_short_stacked()

    def is_deep_stacked(self) -> bool:
        """Check if hero is deep-stacked."""
        return self.spr_symbols.is_deep_stacked()

    # ---- Opponent Modeling Methods ----

    def get_player_type(self, player_id: int) -> str:
        """Get the player type for a specific player."""
        return self.opponent_modeling.get_player_type(player_id)

    def get_player_vpip(self, player_id: int) -> float:
        """Get the VPIP for a specific player."""
        return self.opponent_modeling.get_player_vpip(player_id)

    def get_player_pfr(self, player_id: int) -> float:
        """Get the PFR for a specific player."""
        return self.opponent_modeling.get_player_pfr(player_id)

    def get_player_af(self, player_id: int) -> float:
        """Get the AF for a specific player."""
        return self.opponent_modeling.get_player_af(player_id)

    def get_player_cbet_frequency(self, player_id: int) -> float:
        """Get the continuation bet frequency for a specific player."""
        return self.opponent_modeling.get_player_cbet_frequency(player_id)

    def is_player_aggressive(self, player_id: int) -> bool:
        """Check if a player is aggressive."""
        return self.opponent_modeling.is_player_aggressive(player_id)

    def is_player_passive(self, player_id: int) -> bool:
        """Check if a player is passive."""
        return self.opponent_modeling.is_player_passive(player_id)

    def is_player_tight(self, player_id: int) -> bool:
        """Check if a player is tight."""
        return self.opponent_modeling.is_player_tight(player_id)

    def is_player_loose(self, player_id: int) -> bool:
        """Check if a player is loose."""
        return self.opponent_modeling.is_player_loose(player_id)

    def is_player_likely_to_fold_to_cbet(self, player_id: int) -> bool:
        """Check if a player is likely to fold to a continuation bet."""
        return self.opponent_modeling.is_player_likely_to_fold_to_cbet(player_id)

    def calculate_fold_equity(self, player_id: int, street: Street) -> float:
        """Calculate the fold equity against a specific player on a specific street."""
        return self.opponent_modeling.calculate_fold_equity(player_id, street)

    def calculate_optimal_bet_size_vs_opponent(self, player_id: int, street: Street, hand_strength: float) -> float:
        """Calculate the optimal bet size against a specific player on a specific street."""
        return self.opponent_modeling.calculate_optimal_bet_size(player_id, street, hand_strength)

    def should_bluff_opponent(self, player_id: int, street: Street) -> bool:
        """Determine if we should bluff against a specific player on a specific street."""
        return self.opponent_modeling.should_bluff(player_id, street)