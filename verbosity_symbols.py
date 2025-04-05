"""
Verbosity Symbols for OpenPPL implementation.

This module implements the verbosity-related symbols from OpenPPL.
"""

from typing import Dict, List, Optional, Tuple
from poker_enums import Street

class VerbositySymbols:
    """
    Implementation of OpenPPL verbosity symbols.
    
    This class implements the verbosity-related symbols from OpenPPL,
    providing more readable names for various poker concepts.
    """
    
    def __init__(self):
        """Initialize the verbosity symbols."""
        self.reset()
        
    def reset(self):
        """Reset all symbols."""
        self._current_street: Street = Street.PREFLOP
        self._hero_cards: Tuple[str, str] = ('', '')
        self._community_cards: List[str] = []
        self._made_hand_ranks: List[int] = []
        
    def update_table_state(self, current_street: Street, hero_cards: Tuple[str, str], 
                          community_cards: List[str], made_hand_ranks: List[int] = None):
        """
        Update the table state.
        
        Args:
            current_street: Current street
            hero_cards: Hero's hole cards
            community_cards: Community cards
            made_hand_ranks: Ranks of cards in the made hand (optional)
        """
        self._current_street = current_street
        self._hero_cards = hero_cards
        self._community_cards = community_cards
        self._made_hand_ranks = made_hand_ranks or []
    
    # Street identification
    def is_preflop(self) -> bool:
        """Check if the current street is preflop."""
        return self._current_street == Street.PREFLOP
    
    def is_flop(self) -> bool:
        """Check if the current street is flop."""
        return self._current_street == Street.FLOP
    
    def is_turn(self) -> bool:
        """Check if the current street is turn."""
        return self._current_street == Street.TURN
    
    def is_river(self) -> bool:
        """Check if the current street is river."""
        return self._current_street == Street.RIVER
    
    def is_postflop(self) -> bool:
        """Check if the current street is postflop."""
        return self._current_street != Street.PREFLOP
    
    # Hole card ranks
    def get_rank_of_first_hole_card(self) -> str:
        """Get the rank of the first hole card."""
        if not self._hero_cards or len(self._hero_cards) < 1:
            return ''
        return self._hero_cards[0][0]
    
    def get_rank_of_second_hole_card(self) -> str:
        """Get the rank of the second hole card."""
        if not self._hero_cards or len(self._hero_cards) < 2:
            return ''
        return self._hero_cards[1][0]
    
    # Hole card suits
    def get_first_hole_card_suit(self) -> str:
        """Get the suit of the first hole card."""
        if not self._hero_cards or len(self._hero_cards) < 1:
            return ''
        return self._hero_cards[0][1]
    
    def get_second_hole_card_suit(self) -> str:
        """Get the suit of the second hole card."""
        if not self._hero_cards or len(self._hero_cards) < 2:
            return ''
        return self._hero_cards[1][1]
    
    # Community card ranks
    def get_rank_of_first_flop_card(self) -> str:
        """Get the rank of the first flop card."""
        if not self._community_cards or len(self._community_cards) < 1:
            return ''
        return self._community_cards[0][0]
    
    def get_rank_of_second_flop_card(self) -> str:
        """Get the rank of the second flop card."""
        if not self._community_cards or len(self._community_cards) < 2:
            return ''
        return self._community_cards[1][0]
    
    def get_rank_of_third_flop_card(self) -> str:
        """Get the rank of the third flop card."""
        if not self._community_cards or len(self._community_cards) < 3:
            return ''
        return self._community_cards[2][0]
    
    def get_rank_of_turn_card(self) -> str:
        """Get the rank of the turn card."""
        if not self._community_cards or len(self._community_cards) < 4:
            return ''
        return self._community_cards[3][0]
    
    def get_rank_of_river_card(self) -> str:
        """Get the rank of the river card."""
        if not self._community_cards or len(self._community_cards) < 5:
            return ''
        return self._community_cards[4][0]
    
    # Community card suits
    def get_suit_of_first_flop_card(self) -> str:
        """Get the suit of the first flop card."""
        if not self._community_cards or len(self._community_cards) < 1:
            return ''
        return self._community_cards[0][1]
    
    def get_suit_of_second_flop_card(self) -> str:
        """Get the suit of the second flop card."""
        if not self._community_cards or len(self._community_cards) < 2:
            return ''
        return self._community_cards[1][1]
    
    def get_suit_of_third_flop_card(self) -> str:
        """Get the suit of the third flop card."""
        if not self._community_cards or len(self._community_cards) < 3:
            return ''
        return self._community_cards[2][1]
    
    def get_suit_of_turn_card(self) -> str:
        """Get the suit of the turn card."""
        if not self._community_cards or len(self._community_cards) < 4:
            return ''
        return self._community_cards[3][1]
    
    def get_suit_of_river_card(self) -> str:
        """Get the suit of the river card."""
        if not self._community_cards or len(self._community_cards) < 5:
            return ''
        return self._community_cards[4][1]
    
    # Made hand ranks
    def get_made_hand_third_card_rank(self) -> int:
        """Get the rank of the third card in the made hand."""
        if not self._made_hand_ranks or len(self._made_hand_ranks) < 3:
            return 0
        return self._made_hand_ranks[2]
    
    def get_made_hand_fourth_card_rank(self) -> int:
        """Get the rank of the fourth card in the made hand."""
        if not self._made_hand_ranks or len(self._made_hand_ranks) < 4:
            return 0
        return self._made_hand_ranks[3]
    
    def get_made_hand_fifth_card_rank(self) -> int:
        """Get the rank of the fifth card in the made hand."""
        if not self._made_hand_ranks or len(self._made_hand_ranks) < 5:
            return 0
        return self._made_hand_ranks[4]
    
    # Aliases
    def get_first_flop_card(self) -> str:
        """Alias for get_rank_of_first_flop_card."""
        return self.get_rank_of_first_flop_card()
    
    def get_second_flop_card(self) -> str:
        """Alias for get_rank_of_second_flop_card."""
        return self.get_rank_of_second_flop_card()
    
    def get_third_flop_card(self) -> str:
        """Alias for get_rank_of_third_flop_card."""
        return self.get_rank_of_third_flop_card()
    
    def get_turn_card(self) -> str:
        """Alias for get_rank_of_turn_card."""
        return self.get_rank_of_turn_card()
    
    def get_river_card(self) -> str:
        """Alias for get_rank_of_river_card."""
        return self.get_rank_of_river_card()
    
    def get_first_flop_suit(self) -> str:
        """Alias for get_suit_of_first_flop_card."""
        return self.get_suit_of_first_flop_card()
    
    def get_second_flop_suit(self) -> str:
        """Alias for get_suit_of_second_flop_card."""
        return self.get_suit_of_second_flop_card()
    
    def get_third_flop_suit(self) -> str:
        """Alias for get_suit_of_third_flop_card."""
        return self.get_suit_of_third_flop_card()
    
    def get_turn_suit(self) -> str:
        """Alias for get_suit_of_turn_card."""
        return self.get_suit_of_turn_card()
    
    def get_river_suit(self) -> str:
        """Alias for get_suit_of_river_card."""
        return self.get_suit_of_river_card()
    
    # Additional verbosity methods for our implementation
    def get_hand_description(self) -> str:
        """Get a human-readable description of the hero's hand."""
        if not self._hero_cards or len(self._hero_cards) < 2:
            return "Unknown hand"
        
        rank1 = self._hero_cards[0][0]
        rank2 = self._hero_cards[1][0]
        suit1 = self._hero_cards[0][1]
        suit2 = self._hero_cards[1][1]
        
        # Convert ranks to human-readable format
        rank_map = {'T': '10', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
        readable_rank1 = rank_map.get(rank1, rank1)
        readable_rank2 = rank_map.get(rank2, rank2)
        
        # Convert suits to human-readable format
        suit_map = {'h': 'Hearts', 'd': 'Diamonds', 'c': 'Clubs', 's': 'Spades'}
        readable_suit1 = suit_map.get(suit1, suit1)
        readable_suit2 = suit_map.get(suit2, suit2)
        
        # Check if it's a pocket pair
        if rank1 == rank2:
            return f"Pocket {readable_rank1}s"
        
        # Check if it's suited
        if suit1 == suit2:
            return f"{readable_rank1}-{readable_rank2} suited ({readable_suit1})"
        
        # Otherwise, it's offsuit
        return f"{readable_rank1}-{readable_rank2} offsuit"
    
    def get_board_description(self) -> str:
        """Get a human-readable description of the board."""
        if not self._community_cards:
            return "No community cards"
        
        # Convert ranks to human-readable format
        rank_map = {'T': '10', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
        
        # Convert suits to human-readable format
        suit_map = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
        
        # Format each card
        formatted_cards = []
        for card in self._community_cards:
            rank = card[0]
            suit = card[1]
            readable_rank = rank_map.get(rank, rank)
            readable_suit = suit_map.get(suit, suit)
            formatted_cards.append(f"{readable_rank}{readable_suit}")
        
        # Join the formatted cards
        return " ".join(formatted_cards)
    
    def get_street_description(self) -> str:
        """Get a human-readable description of the current street."""
        street_map = {
            Street.PREFLOP: "Preflop",
            Street.FLOP: "Flop",
            Street.TURN: "Turn",
            Street.RIVER: "River"
        }
        return street_map.get(self._current_street, "Unknown street")
