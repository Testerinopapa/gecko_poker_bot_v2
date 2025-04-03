from typing import List, Set
from poker_enums import HandStrength
from hand_evaluator import HandEvaluator

class BoardAnalyzer:
    def __init__(self):
        self.hand_evaluator = HandEvaluator()
        
    def analyze_board(self, board: List[str]) -> dict:
        """Analyze board texture and return characteristics"""
        if len(board) < 3:
            return {}
            
        result = {
            'is_paired': self._is_paired(board),
            'is_monotone': self._is_monotone(board),
            'is_connected': self._is_connected(board),
            'draw_density': self._calculate_draw_density(board),
            'highest_card': self._get_highest_card(board),
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
        
    def _classify_texture(self, analysis: dict) -> str:
        """Classify board texture based on analysis"""
        if analysis['is_monotone']:
            return 'VERY_WET'
            
        if analysis['is_paired'] and analysis['is_connected']:
            return 'VERY_WET'
            
        if analysis['draw_density'] > 0.7:
            return 'WET'
            
        if analysis['draw_density'] > 0.4:
            return 'MEDIUM'
            
        if analysis['is_paired'] and not analysis['is_connected']:
            return 'MEDIUM'
            
        return 'DRY' 