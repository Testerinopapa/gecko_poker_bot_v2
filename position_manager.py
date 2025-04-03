from typing import List, Dict, Set
from poker_enums import Position

class PositionManager:
    def __init__(self):
        # Initialize position-based ranges
        self.position_ranges = {
            Position.BUTTON: "22+,A2s+,K2s+,Q2s+,J6s+,T6s+,96s+,86s+,76s,65s,54s,A2o+,K7o+,Q8o+,J8o+,T8o+",
            Position.SMALL_BLIND: "22+,A2s+,K2s+,Q4s+,J6s+,T6s+,96s+,86s+,76s,65s,54s,A2o+,K8o+,Q9o+,J9o+",
            Position.BIG_BLIND: "22+,A2s+,K2s+,Q2s+,J4s+,T6s+,96s+,86s+,76s,65s,54s,A2o+,K6o+,Q8o+,J8o+"
        }
        
        # Ranges for specific situations
        self.vs_single_raiser_range = "22+,ATs+,KTs+,QTs+,JTs,T9s,98s,87s,76s,65s,AJo+,KQo"
        self.vs_multiple_raisers_range = "77+,AJs+,KQs,AQo+"
        self.squeeze_range = "TT+,AQs+,AKo"
        self.set_mining_range = "22-99"

    def hand_in_range(self, hand: str, position: Position) -> bool:
        """Check if a hand is in the opening range for a position"""
        if position not in self.position_ranges:
            return False
        return self._is_hand_in_range(hand, self.position_ranges[position])

    def hand_in_vs_single_raiser(self, hand: str) -> bool:
        """Check if a hand is playable vs a single raiser"""
        return self._is_hand_in_range(hand, self.vs_single_raiser_range)

    def hand_in_vs_multiple_raisers(self, hand: str) -> bool:
        """Check if a hand is playable vs multiple raisers"""
        return self._is_hand_in_range(hand, self.vs_multiple_raisers_range)

    def hand_in_squeeze_range(self, hand: str) -> bool:
        """Check if a hand is in the squeeze range"""
        return self._is_hand_in_range(hand, self.squeeze_range)

    def hand_in_set_mining_range(self, hand: str) -> bool:
        """Check if a hand is in the set mining range"""
        return self._is_hand_in_range(hand, self.set_mining_range)

    def _is_hand_in_range(self, hand: str, range_str: str) -> bool:
        """Helper method to check if a hand is in a range"""
        # Convert hand to standard format (e.g., "AKs" or "AKo")
        if not hand or len(hand) < 3:
            return False
            
        # Handle different input formats
        if len(hand) == 3:  # Already in correct format
            hand_str = hand
        else:  # Convert from card notation (e.g., "Ah Kh" to "AKs")
            rank1, suit1 = hand[0], hand[1]
            rank2, suit2 = hand[3], hand[4]
            suited = suit1 == suit2
            ranks = sorted([rank1, rank2], reverse=True)  # Higher rank first
            hand_str = ranks[0] + ranks[1] + ('s' if suited else 'o')
        
        # Parse range string
        hands = range_str.split(',')
        for range_hand in hands:
            # Handle pairs
            if len(range_hand) == 2 and range_hand[0] == range_hand[1]:
                if hand_str[0] == hand_str[1] == range_hand[0]:
                    return True
                    
            # Handle pair ranges (e.g., "22-99")
            elif '-' in range_hand:
                start, end = range_hand.split('-')
                if hand_str[0] == hand_str[1] and start[0] <= hand_str[0] <= end[0]:
                    return True
                    
            # Handle suited/offsuit hands
            elif len(range_hand) == 3:
                if range_hand.endswith('s') and hand_str.endswith('o'):
                    continue
                if range_hand.endswith('o') and hand_str.endswith('s'):
                    continue
                if hand_str[0] == range_hand[0] and hand_str[1] == range_hand[1]:
                    return True
                    
            # Handle hand ranges (e.g., "A2s+")
            elif len(range_hand) == 4 and range_hand.endswith('+'):
                if range_hand.endswith('s+') and hand_str.endswith('o'):
                    continue
                if range_hand.endswith('o+') and hand_str.endswith('s'):
                    continue
                if hand_str[0] == range_hand[0] and hand_str[1] >= range_hand[1]:
                    return True
                    
        return False 