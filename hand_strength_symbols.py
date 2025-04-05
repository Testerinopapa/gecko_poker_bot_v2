"""
Hand Strength Symbols for OpenPPL implementation.

This module implements the advanced hand strength symbols from OpenPPL.
"""

from typing import List, Dict, Optional, Set, Tuple
from poker_enums import HandStrength, Rank, Suit, Card, Street
from collections import Counter

class HandStrengthSymbols:
    """
    Implementation of OpenPPL hand strength symbols.
    """
    
    def __init__(self):
        """Initialize the hand strength symbols."""
        self.reset()
        
    def reset(self):
        """Reset all symbols."""
        self._hole_cards: List[Card] = []
        self._flop_cards: List[Card] = []
        self._turn_card: Optional[Card] = None
        self._river_card: Optional[Card] = None
        self._board_cards: List[Card] = []
        self._current_street: Street = Street.PREFLOP
        
        # Hand history tracking
        self._had_overpair_on_flop: bool = False
        self._had_top_pair_on_flop: bool = False
        self._had_second_top_pair_on_flop: bool = False
        self._had_set_on_flop: bool = False
        self._had_two_pair_on_flop: bool = False
        
        self._had_overpair_on_turn: bool = False
        self._had_top_pair_on_turn: bool = False
        self._had_set_on_turn: bool = False
        
    def update_cards(self, hole_cards: List[str], board_cards: List[str], street: Street):
        """
        Update the cards and current street.
        
        Args:
            hole_cards: List of hole card strings (e.g., ['Ah', 'Kd'])
            board_cards: List of board card strings (e.g., ['Qh', 'Jd', '2c'])
            street: Current street
        """
        self._current_street = street
        self._hole_cards = [self._parse_card(card) for card in hole_cards]
        self._board_cards = [self._parse_card(card) for card in board_cards]
        
        # Update street-specific cards
        if street >= Street.FLOP and len(board_cards) >= 3:
            self._flop_cards = [self._parse_card(card) for card in board_cards[:3]]
            
            # Track hand history on flop
            self._had_overpair_on_flop = self.have_overpair()
            self._had_top_pair_on_flop = self.have_top_pair()
            self._had_second_top_pair_on_flop = self.have_second_top_pair()
            self._had_set_on_flop = self.have_set()
            self._had_two_pair_on_flop = self.have_two_pair()
            
        if street >= Street.TURN and len(board_cards) >= 4:
            self._turn_card = self._parse_card(board_cards[3])
            
            # Track hand history on turn
            self._had_overpair_on_turn = self.have_overpair()
            self._had_top_pair_on_turn = self.have_top_pair()
            self._had_set_on_turn = self.have_set()
            
        if street >= Street.RIVER and len(board_cards) >= 5:
            self._river_card = self._parse_card(board_cards[4])
    
    def _parse_card(self, card_str: str) -> Card:
        """
        Parse a card string into a Card object.
        
        Args:
            card_str: Card string (e.g., 'Ah')
            
        Returns:
            Card object
        """
        rank_char = card_str[0].upper()
        suit_char = card_str[1].lower()
        
        # Convert rank character to Rank enum
        if rank_char == 'A':
            rank = Rank.ACE
        elif rank_char == 'K':
            rank = Rank.KING
        elif rank_char == 'Q':
            rank = Rank.QUEEN
        elif rank_char == 'J':
            rank = Rank.JACK
        elif rank_char == 'T':
            rank = Rank.TEN
        else:
            rank = Rank(int(rank_char))
            
        # Convert suit character to Suit enum
        if suit_char == 'h':
            suit = Suit.HEARTS
        elif suit_char == 'd':
            suit = Suit.DIAMONDS
        elif suit_char == 'c':
            suit = Suit.CLUBS
        elif suit_char == 's':
            suit = Suit.SPADES
        else:
            raise ValueError(f"Invalid suit: {suit_char}")
            
        return Card(rank, suit)
    
    # ---- Detailed Hand Categories ----
    
    def have_overpair(self) -> bool:
        """
        Check if we have an overpair (pocket pair higher than any board card).
        
        Returns:
            True if we have an overpair, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Check if hole cards are a pair
        if self._hole_cards[0].rank != self._hole_cards[1].rank:
            return False
            
        # Get hole pair rank and highest board rank
        hole_rank = self._hole_cards[0].rank.value
        max_board_rank = max(card.rank.value for card in self._board_cards)
        
        return hole_rank > max_board_rank
    
    def have_top_pair(self) -> bool:
        """
        Check if we have top pair (one hole card pairs the highest board card).
        
        Returns:
            True if we have top pair, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Get highest board rank
        max_board_rank = max(card.rank for card in self._board_cards)
        
        # Check if either hole card matches the highest board rank
        return any(card.rank == max_board_rank for card in self._hole_cards)
    
    def have_second_top_pair(self) -> bool:
        """
        Check if we have second top pair (one hole card pairs the second highest board card).
        
        Returns:
            True if we have second top pair, False otherwise
        """
        if not self._board_cards or len(self._board_cards) < 2 or len(self._hole_cards) != 2:
            return False
            
        # Get sorted board ranks
        board_ranks = sorted([card.rank for card in self._board_cards], reverse=True)
        
        # Check if either hole card matches the second highest board rank
        return any(card.rank == board_ranks[1] for card in self._hole_cards)
    
    def have_third_top_pair(self) -> bool:
        """
        Check if we have third top pair (one hole card pairs the third highest board card).
        
        Returns:
            True if we have third top pair, False otherwise
        """
        if not self._board_cards or len(self._board_cards) < 3 or len(self._hole_cards) != 2:
            return False
            
        # Get sorted board ranks
        board_ranks = sorted([card.rank for card in self._board_cards], reverse=True)
        
        # Check if either hole card matches the third highest board rank
        return any(card.rank == board_ranks[2] for card in self._hole_cards)
    
    def have_set(self) -> bool:
        """
        Check if we have a set (pocket pair that matches one board card).
        
        Returns:
            True if we have a set, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Check if hole cards are a pair
        if self._hole_cards[0].rank != self._hole_cards[1].rank:
            return False
            
        # Check if the pair matches any board card
        return any(card.rank == self._hole_cards[0].rank for card in self._board_cards)
    
    def have_top_set(self) -> bool:
        """
        Check if we have top set (pocket pair that matches the highest board card).
        
        Returns:
            True if we have top set, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Check if hole cards are a pair
        if self._hole_cards[0].rank != self._hole_cards[1].rank:
            return False
            
        # Get highest board rank
        max_board_rank = max(card.rank for card in self._board_cards)
        
        # Check if the pair matches the highest board card
        return self._hole_cards[0].rank == max_board_rank
    
    def have_second_top_set(self) -> bool:
        """
        Check if we have second top set (pocket pair that matches the second highest board card).
        
        Returns:
            True if we have second top set, False otherwise
        """
        if not self._board_cards or len(self._board_cards) < 2 or len(self._hole_cards) != 2:
            return False
            
        # Check if hole cards are a pair
        if self._hole_cards[0].rank != self._hole_cards[1].rank:
            return False
            
        # Get sorted board ranks
        board_ranks = sorted([card.rank for card in self._board_cards], reverse=True)
        
        # Check if the pair matches the second highest board card
        return self._hole_cards[0].rank == board_ranks[1]
    
    def have_two_pair(self) -> bool:
        """
        Check if we have two pair (both hole cards pair with different board cards).
        
        Returns:
            True if we have two pair, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Check if hole cards are different
        if self._hole_cards[0].rank == self._hole_cards[1].rank:
            return False
            
        # Check if both hole cards pair with board cards
        first_pairs = any(card.rank == self._hole_cards[0].rank for card in self._board_cards)
        second_pairs = any(card.rank == self._hole_cards[1].rank for card in self._board_cards)
        
        return first_pairs and second_pairs
    
    def have_top_two_pair(self) -> bool:
        """
        Check if we have top two pair (hole cards pair with the two highest board cards).
        
        Returns:
            True if we have top two pair, False otherwise
        """
        if not self._board_cards or len(self._board_cards) < 2 or len(self._hole_cards) != 2:
            return False
            
        # Check if hole cards are different
        if self._hole_cards[0].rank == self._hole_cards[1].rank:
            return False
            
        # Get sorted board ranks
        board_ranks = sorted([card.rank for card in self._board_cards], reverse=True)
        
        # Check if hole cards match the two highest board ranks
        hole_ranks = {card.rank for card in self._hole_cards}
        top_two_board_ranks = {board_ranks[0], board_ranks[1]}
        
        return hole_ranks == top_two_board_ranks
    
    def have_top_and_bottom_pair(self) -> bool:
        """
        Check if we have top and bottom pair (hole cards pair with highest and lowest board cards).
        
        Returns:
            True if we have top and bottom pair, False otherwise
        """
        if not self._board_cards or len(self._board_cards) < 2 or len(self._hole_cards) != 2:
            return False
            
        # Check if hole cards are different
        if self._hole_cards[0].rank == self._hole_cards[1].rank:
            return False
            
        # Get sorted board ranks
        board_ranks = sorted([card.rank for card in self._board_cards])
        
        # Check if hole cards match the highest and lowest board ranks
        hole_ranks = {card.rank for card in self._hole_cards}
        top_bottom_board_ranks = {board_ranks[0], board_ranks[-1]}
        
        return hole_ranks == top_bottom_board_ranks
    
    # ---- Hand History Symbols ----
    
    def had_overpair_on_flop(self) -> bool:
        """
        Check if we had an overpair on the flop.
        
        Returns:
            True if we had an overpair on the flop, False otherwise
        """
        return self._had_overpair_on_flop
    
    def had_overpair_on_turn(self) -> bool:
        """
        Check if we had an overpair on the turn.
        
        Returns:
            True if we had an overpair on the turn, False otherwise
        """
        return self._had_overpair_on_turn
    
    def had_top_pair_on_flop(self) -> bool:
        """
        Check if we had top pair on the flop.
        
        Returns:
            True if we had top pair on the flop, False otherwise
        """
        return self._had_top_pair_on_flop
    
    def had_second_top_pair_on_flop(self) -> bool:
        """
        Check if we had second top pair on the flop.
        
        Returns:
            True if we had second top pair on the flop, False otherwise
        """
        return self._had_second_top_pair_on_flop
    
    def had_top_pair_on_turn(self) -> bool:
        """
        Check if we had top pair on the turn.
        
        Returns:
            True if we had top pair on the turn, False otherwise
        """
        return self._had_top_pair_on_turn
    
    def had_set_on_flop(self) -> bool:
        """
        Check if we had a set on the flop.
        
        Returns:
            True if we had a set on the flop, False otherwise
        """
        return self._had_set_on_flop
    
    def had_set_on_turn(self) -> bool:
        """
        Check if we had a set on the turn.
        
        Returns:
            True if we had a set on the turn, False otherwise
        """
        return self._had_set_on_turn
    
    def had_two_pair_on_flop(self) -> bool:
        """
        Check if we had two pair on the flop.
        
        Returns:
            True if we had two pair on the flop, False otherwise
        """
        return self._had_two_pair_on_flop
    
    # ---- Blocker Symbols ----
    
    def have_ace_blocker(self) -> bool:
        """
        Check if we have an ace blocker (one ace in hole cards).
        
        Returns:
            True if we have an ace blocker, False otherwise
        """
        return any(card.rank == Rank.ACE for card in self._hole_cards)
    
    def have_king_blocker(self) -> bool:
        """
        Check if we have a king blocker (one king in hole cards).
        
        Returns:
            True if we have a king blocker, False otherwise
        """
        return any(card.rank == Rank.KING for card in self._hole_cards)
    
    def have_flush_blocker(self) -> bool:
        """
        Check if we have a flush blocker (one card of the flush suit).
        
        Returns:
            True if we have a flush blocker, False otherwise
        """
        if not self._board_cards:
            return False
            
        # Count suits on the board
        suit_counter = Counter(card.suit for card in self._board_cards)
        most_common_suit, count = suit_counter.most_common(1)[0]
        
        # Check if there's a potential flush draw
        if count < 3:
            return False
            
        # Check if we have a card of the most common suit
        return any(card.suit == most_common_suit for card in self._hole_cards)
    
    def have_straight_blocker(self) -> bool:
        """
        Check if we have a straight blocker (one card that blocks a potential straight).
        
        Returns:
            True if we have a straight blocker, False otherwise
        """
        if not self._board_cards:
            return False
            
        # Get all ranks on the board
        board_ranks = sorted([card.rank.value for card in self._board_cards])
        
        # Check for potential straights
        for i in range(10):  # 10 possible straight combinations (A-5 to 10-A)
            straight_ranks = set(range(i+1, i+6))  # 5 consecutive ranks
            board_straight_ranks = set(board_ranks) & straight_ranks
            
            # If board has 3 or 4 cards to a straight
            if len(board_straight_ranks) >= 3:
                missing_ranks = straight_ranks - board_straight_ranks
                hole_ranks = {card.rank.value for card in self._hole_cards}
                
                # Check if we have any of the missing ranks
                if hole_ranks & missing_ranks:
                    return True
                    
        return False
    
    # ---- Redraw Potential Symbols ----
    
    def have_flush_redraw(self) -> bool:
        """
        Check if we have a flush redraw (made hand plus flush draw).
        
        Returns:
            True if we have a flush redraw, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Check if we have at least a pair
        have_pair = (self.have_overpair() or self.have_top_pair() or 
                    self.have_second_top_pair() or self.have_third_top_pair())
        
        if not have_pair:
            return False
            
        # Check for flush draw
        suits = [card.suit for card in self._hole_cards + self._board_cards]
        suit_counter = Counter(suits)
        
        return suit_counter.most_common(1)[0][1] == 4
    
    def have_straight_redraw(self) -> bool:
        """
        Check if we have a straight redraw (made hand plus straight draw).
        
        Returns:
            True if we have a straight redraw, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Check if we have at least a pair
        have_pair = (self.have_overpair() or self.have_top_pair() or 
                    self.have_second_top_pair() or self.have_third_top_pair())
        
        if not have_pair:
            return False
            
        # Check for open-ended straight draw or gutshot
        all_ranks = sorted([card.rank.value for card in self._hole_cards + self._board_cards])
        
        # Remove duplicates
        unique_ranks = sorted(list(set(all_ranks)))
        
        # Check for 4 consecutive ranks (open-ended)
        for i in range(len(unique_ranks) - 3):
            if unique_ranks[i+3] - unique_ranks[i] == 3:  # 4 consecutive ranks
                return True
                
        # Check for 3 ranks with a gap (gutshot)
        for i in range(len(unique_ranks) - 2):
            if unique_ranks[i+2] - unique_ranks[i] == 3:  # 3 ranks with a 1-card gap
                return True
                
        return False
    
    def have_set_redraw(self) -> bool:
        """
        Check if we have a set redraw (pair with potential to improve to set).
        
        Returns:
            True if we have a set redraw, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Check if hole cards are a pair
        if self._hole_cards[0].rank != self._hole_cards[1].rank:
            return False
            
        # Check if the pair doesn't match any board card yet
        return not any(card.rank == self._hole_cards[0].rank for card in self._board_cards)
    
    # ---- Showdown Value Symbols ----
    
    def have_showdown_value(self) -> bool:
        """
        Check if we have showdown value (at least a pair).
        
        Returns:
            True if we have showdown value, False otherwise
        """
        return (self.have_overpair() or self.have_top_pair() or 
                self.have_second_top_pair() or self.have_third_top_pair() or
                self.have_set() or self.have_two_pair())
    
    def have_strong_showdown_value(self) -> bool:
        """
        Check if we have strong showdown value (overpair, top pair with good kicker, set, or better).
        
        Returns:
            True if we have strong showdown value, False otherwise
        """
        if self.have_overpair() or self.have_set() or self.have_two_pair():
            return True
            
        # Check for top pair with good kicker
        if self.have_top_pair():
            # Get the non-paired hole card
            top_board_rank = max(card.rank for card in self._board_cards)
            kicker = next((card for card in self._hole_cards if card.rank != top_board_rank), None)
            
            # Check if kicker is good (A, K, Q)
            return kicker and kicker.rank.value >= Rank.QUEEN.value
            
        return False
    
    def have_weak_showdown_value(self) -> bool:
        """
        Check if we have weak showdown value (middle or bottom pair).
        
        Returns:
            True if we have weak showdown value, False otherwise
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return False
            
        # Check if we have showdown value but not strong showdown value
        return self.have_showdown_value() and not self.have_strong_showdown_value()
    
    # ---- Hand vs Range Evaluation ----
    
    def hand_vs_range_equity(self, opponent_range: List[str] = None) -> float:
        """
        Calculate equity of our hand against opponent's range.
        
        Args:
            opponent_range: List of hands in opponent's range (e.g., ['AK', 'QQ+'])
            
        Returns:
            Equity percentage (0-1)
        """
        # Default to a tight range if none provided
        if not opponent_range:
            opponent_range = ['JJ+', 'AK']
            
        # This is a simplified implementation
        # In a real implementation, we would use a Monte Carlo simulation
        # to calculate equity against the range
        
        # For now, return a heuristic based on hand strength
        if self.have_set() or self.have_two_pair():
            return 0.8  # 80% equity
        elif self.have_overpair():
            return 0.7  # 70% equity
        elif self.have_top_pair() and self.have_strong_showdown_value():
            return 0.6  # 60% equity
        elif self.have_top_pair():
            return 0.5  # 50% equity
        elif self.have_second_top_pair() or self.have_third_top_pair():
            return 0.4  # 40% equity
        elif self.have_flush_redraw() or self.have_straight_redraw():
            return 0.45  # 45% equity
        else:
            return 0.3  # 30% equity
