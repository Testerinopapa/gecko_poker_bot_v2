"""
Outs Calculator for OpenPPL implementation.

This module implements the outs calculation from OpenPPL.
"""

from typing import List, Dict, Optional, Set, Tuple
from poker_enums import Rank, Suit, Card, Street
from collections import Counter
from board_texture_symbols import BoardTextureSymbols
from hand_strength_symbols import HandStrengthSymbols

class OutsCalculator:
    """
    Implementation of OpenPPL outs calculation.
    """
    
    def __init__(self):
        """Initialize the outs calculator."""
        self.reset()
        
    def reset(self):
        """Reset all variables."""
        self._hole_cards: List[Card] = []
        self._board_cards: List[Card] = []
        self._current_street: Street = Street.PREFLOP
        self._board_texture_symbols = BoardTextureSymbols()
        self._hand_strength_symbols = HandStrengthSymbols()
        
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
        
        # Update board texture symbols
        self._board_texture_symbols.update_board(board_cards, street)
        
        # Update hand strength symbols
        self._hand_strength_symbols.update_cards(hole_cards, board_cards, street)
    
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
    
    def calculate_total_outs(self) -> float:
        """
        Calculate the total number of outs.
        
        Returns:
            Total number of outs (can be fractional for backdoor draws)
        """
        if self._current_street == Street.PREFLOP:
            return 0.0  # No outs on preflop
            
        if self._current_street == Street.RIVER:
            return 0.0  # No outs on river
            
        # Calculate outs based on current street
        if self._current_street == Street.FLOP:
            return self.calculate_flop_outs()
        else:  # Turn
            return self.calculate_turn_outs()
    
    def calculate_flop_outs(self) -> float:
        """
        Calculate the number of outs on the flop.
        
        Returns:
            Number of outs on the flop (can be fractional for backdoor draws)
        """
        outs = 0.0
        
        # Add outs for made hands that can improve
        outs += self._calculate_made_hand_improvement_outs()
        
        # Add outs for flush draws
        outs += self._calculate_flush_draw_outs()
        
        # Add outs for straight draws
        outs += self._calculate_straight_draw_outs()
        
        # Add outs for overcards
        outs += self._calculate_overcard_outs()
        
        # Add outs for backdoor draws
        outs += self._calculate_backdoor_draw_outs()
        
        # Apply discounts for dangerous boards
        outs -= self._calculate_outs_discount()
        
        # Ensure outs is not negative
        return max(0.0, outs)
    
    def calculate_turn_outs(self) -> float:
        """
        Calculate the number of outs on the turn.
        
        Returns:
            Number of outs on the turn
        """
        outs = 0.0
        
        # Add outs for made hands that can improve
        outs += self._calculate_made_hand_improvement_outs()
        
        # Add outs for flush draws
        outs += self._calculate_flush_draw_outs()
        
        # Add outs for straight draws
        outs += self._calculate_straight_draw_outs()
        
        # Add outs for overcards
        outs += self._calculate_overcard_outs()
        
        # Apply discounts for dangerous boards
        outs -= self._calculate_outs_discount()
        
        # Ensure outs is not negative
        return max(0.0, outs)
    
    def _calculate_made_hand_improvement_outs(self) -> float:
        """
        Calculate outs for improving made hands (pairs to sets, etc.).
        
        Returns:
            Number of outs for improving made hands
        """
        outs = 0.0
        
        # Pair to set outs
        if self._hand_strength_symbols.have_set_redraw():
            outs += 2.0  # 2 outs to make a set with a pocket pair
        
        # One pair to two pair or trips outs
        if self._hand_strength_symbols.have_top_pair() or self._hand_strength_symbols.have_second_top_pair():
            # Count how many cards on the board are paired with our hole cards
            paired_cards = 0
            for hole_card in self._hole_cards:
                for board_card in self._board_cards:
                    if hole_card.rank == board_card.rank:
                        paired_cards += 1
            
            # If we have one pair, we have 3 outs to make trips
            if paired_cards == 1:
                outs += 2.0  # 2 more cards of the same rank
            
            # Outs to make two pair with our kicker
            kicker_card = next((card for card in self._hole_cards if not any(card.rank == board_card.rank for board_card in self._board_cards)), None)
            if kicker_card:
                outs += 3.0  # 3 cards of the same rank as our kicker
        
        return outs
    
    def _calculate_flush_draw_outs(self) -> float:
        """
        Calculate outs for completing a flush draw.
        
        Returns:
            Number of outs for completing a flush draw
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return 0.0
            
        # Count suits
        suits = [card.suit for card in self._hole_cards + self._board_cards]
        suit_counter = Counter(suits)
        
        # Check for flush draw (4 cards of the same suit)
        for suit, count in suit_counter.items():
            if count == 4:
                # Calculate how many cards of this suit are left in the deck
                remaining_cards = 13 - count
                
                # Check if we have the nut flush draw (ace of the suit)
                has_ace = any(card.rank == Rank.ACE and card.suit == suit for card in self._hole_cards)
                
                # Adjust outs based on whether we have the nut flush draw
                if has_ace:
                    return 9.0  # 9 outs for nut flush draw
                else:
                    # Check how many cards higher than our highest card are left
                    highest_card = max((card for card in self._hole_cards if card.suit == suit), key=lambda c: c.rank.value, default=None)
                    if highest_card:
                        higher_cards = sum(1 for r in range(highest_card.rank.value + 1, Rank.ACE.value + 1))
                        if higher_cards <= 4:
                            return 9.0  # 9 outs if few higher cards left
                        else:
                            return 8.0  # 8 outs if many higher cards left
                    
                    return 8.0  # 8 outs for non-nut flush draw
        
        return 0.0
    
    def _calculate_straight_draw_outs(self) -> float:
        """
        Calculate outs for completing a straight draw.
        
        Returns:
            Number of outs for completing a straight draw
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return 0.0
            
        # Get all ranks
        ranks = sorted([card.rank.value for card in self._hole_cards + self._board_cards])
        
        # Remove duplicates
        unique_ranks = sorted(list(set(ranks)))
        
        # Check for open-ended straight draw (4 consecutive cards)
        for i in range(len(unique_ranks) - 3):
            if unique_ranks[i+3] - unique_ranks[i] == 3:  # 4 consecutive cards
                # Check if this is a Broadway straight draw (TJQKA)
                if unique_ranks[i+3] == Rank.ACE.value:
                    return 8.0  # 8 outs for Broadway straight draw
                
                # Check if this is a wheel straight draw (A2345)
                if unique_ranks[i] == 2 and Rank.ACE.value in unique_ranks:
                    return 9.0  # 9 outs for wheel straight draw (includes A)
                
                return 8.0  # 8 outs for open-ended straight draw
        
        # Check for gutshot straight draw (4 cards with one gap)
        for i in range(len(unique_ranks) - 2):
            if unique_ranks[i+2] - unique_ranks[i] == 3:  # 3 cards with one gap
                return 4.0  # 4 outs for gutshot straight draw
                
        # Check for double gutshot straight draw
        double_gutshot = False
        for i in range(len(unique_ranks) - 3):
            if unique_ranks[i+3] - unique_ranks[i] == 4:  # 4 cards with two gaps
                # Check if the gaps are in different places
                if unique_ranks[i+1] - unique_ranks[i] > 1 and unique_ranks[i+3] - unique_ranks[i+2] > 1:
                    double_gutshot = True
                    break
        
        if double_gutshot:
            return 8.0  # 8 outs for double gutshot straight draw
                
        return 0.0
    
    def _calculate_overcard_outs(self) -> float:
        """
        Calculate outs for pairing an overcard.
        
        Returns:
            Number of outs for pairing an overcard
        """
        if not self._board_cards or len(self._hole_cards) != 2:
            return 0.0
            
        # Check if we have overcards
        highest_board_rank = max(card.rank.value for card in self._board_cards)
        overcard_count = sum(1 for card in self._hole_cards if card.rank.value > highest_board_rank)
        
        # No overcards
        if overcard_count == 0:
            return 0.0
            
        # Check if we have a pair
        if self._hole_cards[0].rank == self._hole_cards[1].rank:
            return 0.0  # No overcard outs for a pocket pair
            
        # Calculate outs based on number of opponents and board texture
        opponents_count = 1  # Default to 1 opponent
        
        # Adjust outs based on board texture and opponent count
        if self._board_texture_symbols.is_dry_board():
            if opponents_count == 1:
                return overcard_count * 3.0  # 3 outs per overcard vs 1 opponent on dry board
            else:
                return overcard_count * 2.0  # 2 outs per overcard vs multiple opponents on dry board
        else:
            # Wet board reduces overcard value
            if opponents_count == 1:
                return overcard_count * 2.0  # 2 outs per overcard vs 1 opponent on wet board
            else:
                return overcard_count * 1.0  # 1 out per overcard vs multiple opponents on wet board
    
    def _calculate_backdoor_draw_outs(self) -> float:
        """
        Calculate outs for completing backdoor draws.
        
        Returns:
            Number of outs for completing backdoor draws (fractional)
        """
        if self._current_street != Street.FLOP or not self._board_cards or len(self._hole_cards) != 2:
            return 0.0
            
        backdoor_outs = 0.0
        
        # Backdoor flush draw (3 cards of the same suit)
        suits = [card.suit for card in self._hole_cards + self._board_cards]
        suit_counter = Counter(suits)
        
        for suit, count in suit_counter.items():
            if count == 3:
                # Check if we have at least one hole card of this suit
                hole_suit_count = sum(1 for card in self._hole_cards if card.suit == suit)
                if hole_suit_count > 0:
                    # Check if we have the ace of this suit
                    has_ace = any(card.rank == Rank.ACE and card.suit == suit for card in self._hole_cards)
                    if has_ace:
                        backdoor_outs += 1.5  # 1.5 outs for backdoor flush draw with ace
                    else:
                        backdoor_outs += 1.0  # 1 out for backdoor flush draw
        
        # Backdoor straight draw (3 consecutive cards)
        ranks = sorted([card.rank.value for card in self._hole_cards + self._board_cards])
        unique_ranks = sorted(list(set(ranks)))
        
        for i in range(len(unique_ranks) - 2):
            if unique_ranks[i+2] - unique_ranks[i] == 2:  # 3 consecutive cards
                # Check if we have at least one hole card in this straight
                hole_ranks = [card.rank.value for card in self._hole_cards]
                if any(rank in hole_ranks for rank in unique_ranks[i:i+3]):
                    # Check if our lowest hole card is higher than the highest board card
                    lowest_hole_rank = min(hole_ranks)
                    highest_board_rank = max(card.rank.value for card in self._board_cards)
                    if lowest_hole_rank > highest_board_rank:
                        backdoor_outs += 1.5  # 1.5 outs for backdoor straight draw with high cards
                    else:
                        backdoor_outs += 1.0  # 1 out for backdoor straight draw
        
        return backdoor_outs
    
    def _calculate_outs_discount(self) -> float:
        """
        Calculate discount to apply to outs based on board danger.
        
        Returns:
            Discount to apply to outs
        """
        discount = 0.0
        
        # Discount for paired board
        if self._board_texture_symbols.is_paired_board():
            # Count pairs on board
            ranks = [card.rank for card in self._board_cards]
            rank_counter = Counter(ranks)
            pairs_count = sum(1 for count in rank_counter.values() if count >= 2)
            
            if pairs_count == 1:
                discount += 3.5  # Discount for one pair on board
            elif pairs_count >= 2:
                discount += 10.0  # Discount for two pairs on board
        
        # Discount for flush-possible board
        if self._board_texture_symbols.flush_possible():
            if not self._hand_strength_symbols.have_flush_redraw():
                discount += 2.0  # Discount for flush-possible board without flush draw
        
        # Discount for straight-possible board
        if self._board_texture_symbols.straight_possible():
            if not self._hand_strength_symbols.have_straight_redraw():
                discount += 2.0  # Discount for straight-possible board without straight draw
        
        return discount
    
    def calculate_equity_from_outs(self) -> float:
        """
        Calculate equity from outs using the rule of 2 and 4.
        
        Returns:
            Equity percentage (0-1)
        """
        outs = self.calculate_total_outs()
        
        if self._current_street == Street.FLOP:
            return min(outs * 0.04, 0.95)  # Rule of 4 on flop (4% per out), max 95%
        elif self._current_street == Street.TURN:
            return min(outs * 0.02, 0.95)  # Rule of 2 on turn (2% per out), max 95%
        else:
            return 0.0  # No outs on preflop or river
    
    def get_outs_description(self) -> str:
        """
        Get a description of the outs.
        
        Returns:
            Description of the outs
        """
        outs = self.calculate_total_outs()
        if outs == 0:
            return "No outs"
            
        descriptions = []
        
        # Flush draw outs
        flush_outs = self._calculate_flush_draw_outs()
        if flush_outs > 0:
            descriptions.append(f"{flush_outs:.0f} flush draw outs")
        
        # Straight draw outs
        straight_outs = self._calculate_straight_draw_outs()
        if straight_outs > 0:
            if straight_outs >= 8:
                descriptions.append(f"{straight_outs:.0f} open-ended straight draw outs")
            else:
                descriptions.append(f"{straight_outs:.0f} gutshot straight draw outs")
        
        # Overcard outs
        overcard_outs = self._calculate_overcard_outs()
        if overcard_outs > 0:
            descriptions.append(f"{overcard_outs:.0f} overcard outs")
        
        # Made hand improvement outs
        made_hand_outs = self._calculate_made_hand_improvement_outs()
        if made_hand_outs > 0:
            descriptions.append(f"{made_hand_outs:.0f} made hand improvement outs")
        
        # Backdoor draw outs
        backdoor_outs = self._calculate_backdoor_draw_outs()
        if backdoor_outs > 0:
            descriptions.append(f"{backdoor_outs:.1f} backdoor draw outs")
        
        # Discount
        discount = self._calculate_outs_discount()
        if discount > 0:
            descriptions.append(f"minus {discount:.1f} for dangerous board")
        
        return ", ".join(descriptions) + f" (total: {outs:.1f})"
