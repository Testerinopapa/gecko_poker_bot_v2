from typing import List, Set, Dict, Optional
from poker_enums import HandStrength, BoardTexture, Card, Rank, Suit, Street
from hand_evaluator import HandEvaluator
from board_texture_symbols import BoardTextureSymbols

class BoardAnalyzer:
    def __init__(self):
        self.hand_evaluator = HandEvaluator()
        self.texture_symbols = BoardTextureSymbols()
        self.current_street = Street.PREFLOP

    def analyze_board(self, board: List[str], street: Street = None) -> dict:
        """Analyze board texture and return characteristics"""
        if len(board) < 3:
            return {}

        # Update current street if provided
        if street is not None:
            self.current_street = street
        else:
            # Infer street from board length
            if len(board) == 3:
                self.current_street = Street.FLOP
            elif len(board) == 4:
                self.current_street = Street.TURN
            elif len(board) == 5:
                self.current_street = Street.RIVER

        # Update board texture symbols
        self.texture_symbols.update_board(board, self.current_street)

        result = {
            # Basic board properties
            'is_paired': self.texture_symbols.is_paired_board(),
            'is_monotone': self.texture_symbols.is_monotone_board(),
            'is_connected': self.texture_symbols.is_connected_board(),
            'is_very_connected': self.texture_symbols.is_very_connected_board(),
            'draw_density': self._calculate_draw_density(board),
            'highest_card': self._get_highest_card(board),

            # Connectedness
            'connectedness': self.texture_symbols.board_connectedness(),

            # Suitedness
            'is_rainbow': self.texture_symbols.is_rainbow_board(),
            'is_two_tone': self.texture_symbols.is_two_tone_board(),
            'suits_on_board': self.texture_symbols.suits_on_board(),
            'flush_possible': self.texture_symbols.flush_possible(),
            'flush_draw_possible': self.texture_symbols.flush_draw_possible(),

            # Paired board
            'is_trips_on_board': self.texture_symbols.is_trips_on_board(),
            'is_two_pair_on_board': self.texture_symbols.is_two_pair_on_board(),
            'is_full_house_on_board': self.texture_symbols.is_full_house_on_board(),
            'is_quads_on_board': self.texture_symbols.is_quads_on_board(),

            # Texture changes
            'flop_texture_changed_on_turn': self.texture_symbols.flop_texture_changed_on_turn() if self.current_street >= Street.TURN else False,
            'turn_texture_changed_on_river': self.texture_symbols.turn_texture_changed_on_river() if self.current_street >= Street.RIVER else False,

            # Draw possibilities
            'straight_possible': self.texture_symbols.straight_possible(),
            'open_ended_straight_draw_possible': self.texture_symbols.open_ended_straight_draw_possible(),
            'gut_shot_straight_draw_possible': self.texture_symbols.gut_shot_straight_draw_possible(),
            'number_of_straight_possibilities': self.texture_symbols.number_of_straight_possibilities(),

            # Board danger level
            'danger_level': self.texture_symbols.board_danger_level(),
            'is_dry_board': self.texture_symbols.is_dry_board(),
            'is_wet_board': self.texture_symbols.is_wet_board(),
            'is_semi_wet_board': self.texture_symbols.is_semi_wet_board(),

            # Legacy analysis for backward compatibility
            'potential_straights': self._count_straight_possibilities(board),
            'flush_possibilities': self._count_flush_possibilities(board)
        }

        # Add texture classification
        result['texture'] = self._classify_texture(result)
        return result

    def _is_paired(self, board: List[str]) -> bool:
        """Check if board is paired"""
        ranks = [card[0] for card in board]
        return len(set(ranks)) < len(ranks)

    def _is_monotone(self, board: List[str]) -> bool:
        """Check if board is all one suit"""
        suits = [card[1] for card in board]
        return len(set(suits)) == 1

    def _is_connected(self, board: List[str]) -> bool:
        """Check if board has connected cards"""
        ranks = sorted([self.hand_evaluator._rank_to_number(card[0]) for card in board])
        for i in range(len(ranks)-1):
            if ranks[i+1] - ranks[i] == 1:
                return True
        return False

    def _calculate_draw_density(self, board: List[str]) -> float:
        """Calculate draw density (0-1 scale)"""
        score = 0.0

        # Check for flush draws
        suits = [card[1] for card in board]
        max_suit_count = max(suits.count(suit) for suit in set(suits))
        if max_suit_count >= 3:
            score += 0.3

        # Check for straight draws
        ranks = sorted([self.hand_evaluator._rank_to_number(card[0]) for card in board])
        gaps = sum(ranks[i+1] - ranks[i] - 1 for i in range(len(ranks)-1))
        if gaps <= 2:
            score += 0.3

        # Add texture points
        if self._is_paired(board):
            score += 0.2
        if self._is_connected(board):
            score += 0.2

        return min(score, 1.0)

    def _get_highest_card(self, board: List[str]) -> str:
        """Get highest card on board"""
        return max(board, key=lambda x: self.hand_evaluator._rank_to_number(x[0]))

    def _count_straight_possibilities(self, board: List[str]) -> int:
        """Count number of possible straights"""
        ranks = set(self.hand_evaluator._rank_to_number(card[0]) for card in board)
        count = 0

        # Check each possible 5-card straight
        for i in range(1, 11):  # Ace-low to Ace-high
            straight = set(range(i, i+5))
            overlap = len(ranks & straight)
            if overlap >= 3:  # Board has 3+ cards to straight
                count += 1

        return count

    def _count_flush_possibilities(self, board: List[str]) -> dict:
        """Count flush possibilities by suit"""
        suits = [card[1] for card in board]
        return {suit: suits.count(suit) for suit in set(suits)}

    def _classify_texture(self, analysis: dict) -> BoardTexture:
        """Classify board texture based on analysis"""
        # Use the board texture symbols to classify the texture
        if analysis['is_wet_board']:
            if analysis['is_monotone'] or analysis['is_very_connected'] or analysis['is_full_house_on_board']:
                return BoardTexture.VERY_WET
            return BoardTexture.WET
        elif analysis['is_semi_wet_board']:
            return BoardTexture.SEMI_WET
        else:
            return BoardTexture.DRY