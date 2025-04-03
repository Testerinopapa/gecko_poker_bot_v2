from typing import List, Tuple, Optional, Dict
from poker_enums import HandStrength
from itertools import combinations
import random

class HandEvaluator:
    RANKS = '23456789TJQKA'
    SUITS = 'hdcs'

    def __init__(self):
        self._init_rank_values()
        self.rank_values = {rank: i for i, rank in enumerate(self.RANKS)}
        self.squeeze_range = self._parse_range("AA KK QQ")
        self.vs_multiple_raisers = self._parse_range("AA KK QQ")

    def _init_rank_values(self):
        self.rank_values = {rank: i for i, rank in enumerate(self.RANKS)}

    def _parse_range(self, range_str: str) -> set:
        """Parse a range string into a set of hands"""
        hands = set()
        for hand in range_str.split():
            if len(hand) == 2:  # Unpaired hands without suit qualifier
                hands.add(hand + 'o')  # Add offsuit version
                hands.add(hand + 's')  # Add suited version
            else:
                hands.add(hand)
        return hands

    def calculate_prwin(self, hole_cards: Tuple[str, str], 
                       board: List[str], 
                       num_opponents: int = 1,
                       num_simulations: int = 1000) -> float:
        """Calculate probability of winning using Monte Carlo simulation"""
        if not hole_cards[0] or not hole_cards[1]:
            return 0.0
            
        wins = 0
        deck = self._create_deck(hole_cards, board)
        
        for _ in range(num_simulations):
            # Deal remaining board cards
            remaining_board = board.copy()
            while len(remaining_board) < 5:
                remaining_board.append(deck[random.randint(0, len(deck)-1)])
                
            # Deal opponent hands
            opponent_hands = []
            for _ in range(num_opponents):
                opp_cards = (deck[random.randint(0, len(deck)-1)],
                           deck[random.randint(0, len(deck)-1)])
                opponent_hands.append(opp_cards)
                
            # Calculate scores
            hero_score = self._calculate_hand_score(list(hole_cards) + remaining_board)
            opponent_scores = [self._calculate_hand_score(list(opp) + remaining_board) 
                             for opp in opponent_hands]
                
            if hero_score > max(opponent_scores):
                wins += 1
            elif hero_score == max(opponent_scores):
                wins += 0.5
                
        return wins / num_simulations

    def have_nuts(self, hole_cards: Tuple[str, str], board: List[str]) -> bool:
        """Check if we have the nuts (best possible hand)"""
        if not board:
            return hole_cards[0][0] == hole_cards[1][0] == 'A'
            
        our_score = self._calculate_hand_score(list(hole_cards) + board)
        
        # Generate all possible two card combinations
        deck = self._create_deck(hole_cards, board)
        possible_hands = list(combinations(deck, 2))
        
        for hand in possible_hands:
            score = self._calculate_hand_score(list(hand) + board)
            if score > our_score:
                return False
        return True

    def have_overpair(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have an overpair"""
        # Convert hole_cards to list if it's a tuple
        if isinstance(hole_cards, tuple):
            hole_cards = list(hole_cards)
            
        if not board or len(hole_cards) != 2:
            return False
            
        # Check if hole cards are a pair
        if hole_cards[0][0] != hole_cards[1][0]:
            return False
            
        # Get hole pair rank and highest board rank
        hole_rank = self._rank_to_number(hole_cards[0][0])
        max_board_rank = max(self._rank_to_number(card[0]) for card in board)
        
        return hole_rank > max_board_rank

    def have_top_pair(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have top pair"""
        # Convert hole_cards to list if it's a tuple
        if isinstance(hole_cards, tuple):
            hole_cards = list(hole_cards)
            
        if not board:
            return False
            
        # Get hole card ranks and highest board rank
        hole_ranks = [card[0] for card in hole_cards]
        board_ranks = [card[0] for card in board]
        max_board_rank = max(board_ranks, key=lambda x: self._rank_to_number(x))
        
        # Check if we have the highest board rank
        return max_board_rank in hole_ranks

    def is_flush_possible(self, board: List[str]) -> bool:
        """Check if a flush is possible on the board"""
        if not board:
            return False
        suits = [card[1] for card in board]
        return any(suits.count(suit) >= 3 for suit in set(suits))

    def is_flush_draw_possible(self, board: List[str]) -> bool:
        """Check if a flush draw is possible on the board"""
        if not board:
            return False
        suits = [card[1] for card in board]
        return any(suits.count(suit) >= 2 for suit in set(suits))

    def is_straight_possible(self, board: List[str]) -> bool:
        """Check if a straight is possible on the board"""
        if len(board) < 3:
            return False
            
        # Convert ranks to numbers
        rank_map = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10}
        for i in range(2, 10):
            rank_map[str(i)] = i
            
        ranks = [rank_map.get(card[0], int(card[0])) for card in board]
        ranks.sort()
        
        # Check for wheel straight possibility (A-5)
        if 14 in ranks:  # If there's an Ace
            ranks.append(1)  # Add low Ace
            
        # Check for 3 consecutive cards
        for i in range(len(ranks)-2):
            if ranks[i+2] - ranks[i] <= 4:
                return True
                
        return False

    def has_double_gutshot(self, board: List[str]) -> bool:
        """Check if there's a double gutshot straight draw possible on the board"""
        if len(board) < 3:
            return False
            
        # Convert ranks to numbers
        rank_map = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10}
        for i in range(2, 10):
            rank_map[str(i)] = i
            
        ranks = [rank_map.get(card[0], int(card[0])) for card in board]
        ranks.sort()
        
        # Count gaps of size 1
        gaps = 0
        for i in range(len(ranks)-1):
            if ranks[i+1] - ranks[i] == 2:
                gaps += 1
                
        return gaps >= 2

    def has_wheel_draw(self, board: List[str]) -> bool:
        """Check if there are 4 cards to a wheel (A-5) on the board"""
        if len(board) < 3:
            return False
            
        wheel_ranks = {'A', '2', '3', '4', '5'}
        board_ranks = {card[0] for card in board}
        return len(wheel_ranks & board_ranks) >= 4

    def have_premium_backdoor_straight_draw(self, hole_cards: List[str], board_cards: List[str]) -> bool:
        """
        Check for premium backdoor straight draws (AKQJT, KQJT9, etc)
        Returns True if we have a premium backdoor straight draw
        """
        if not hole_cards or len(hole_cards) != 2 or not board_cards or len(board_cards) != 3:
            return False
        
        # Convert ranks to numbers (A=14, K=13, etc)
        rank_map = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10}
        for i in range(2, 10):
            rank_map[str(i)] = i
        
        # Get ranks as numbers
        hole_ranks = [rank_map.get(card[0], int(card[0])) for card in hole_cards]
        board_ranks = [rank_map.get(card[0], int(card[0])) for card in board_cards]
        
        all_ranks = sorted(hole_ranks + board_ranks, reverse=True)
        
        # Check for AKQJT-type draws (need 3 consecutive cards from the top 5)
        def has_three_consecutive(ranks):
            for i in range(len(ranks)-2):
                if ranks[i] - ranks[i+2] == 2:
                    # For premium draws, highest card should be ace or king
                    if ranks[i] >= 13:  # Ace or King
                        return True
            return False
        
        # Check if we're using both hole cards
        def using_both_hole_cards(ranks, hole_ranks):
            count = 0
            for i in range(len(ranks)-2):
                if ranks[i] - ranks[i+2] == 2:
                    consecutive = {ranks[i], ranks[i+1], ranks[i+2]}
                    hole_count = sum(1 for r in hole_ranks if r in consecutive)
                    if hole_count == 2:
                        return True
            return False
        
        return has_three_consecutive(all_ranks) and using_both_hole_cards(all_ranks, hole_ranks)

    def get_board_texture(self, board_cards: List[str]) -> dict:
        """Analyze board texture for draws and patterns"""
        if not board_cards:
            return {
                'flush_possible': False,
                'flush_draw_possible': False,
                'straight_possible': False,
                'straight_draw_possible': False,
                'double_gutshot': False,
                'paired_board': False,
                'three_to_wheel': False
            }
        
        # Get existing texture analysis
        texture = {
            'flush_possible': self.is_flush_possible(board_cards),
            'flush_draw_possible': self.is_flush_draw_possible(board_cards),
            'straight_possible': self.is_straight_possible(board_cards),
            'straight_draw_possible': self.have_premium_backdoor_straight_draw(board_cards, board_cards),
            'double_gutshot': self.has_double_gutshot(board_cards),
            'paired_board': self.is_flush_possible(board_cards) and len(set(card[0] for card in board_cards)) == 1,
            'three_to_wheel': self.has_wheel_draw(board_cards)
        }
        
        # Add OpenPPL-style texture analysis
        if len(board_cards) == 3:  # Flop specific
            ranks = [card[0] for card in board_cards]
            texture.update({
                'ace_present': 'A' in ranks,
                'king_present': 'K' in ranks,
                'high_card_heavy': sum(1 for r in ranks if r in 'AKQJ') >= 2,
                'connected': self._is_connected(board_cards),
                'monotone': all(card[1] == board_cards[0][1] for card in board_cards)
            })
        
        return texture

    def _is_connected(self, cards: List[str]) -> bool:
        """Check if board cards are connected (e.g. 789, JQK)"""
        if len(cards) < 2:
            return False
        
        rank_map = {'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10}
        for i in range(2, 10):
            rank_map[str(i)] = i
        
        ranks = sorted([rank_map.get(card[0], int(card[0])) for card in cards])
        
        # Check for any two adjacent ranks
        for i in range(len(ranks)-1):
            if ranks[i+1] - ranks[i] == 1:
                return True
        return False

    def _has_three_to_wheel(self, cards: List[str]) -> bool:
        """Check if board has three cards that could make a wheel (A2345)"""
        wheel_ranks = {'A', '2', '3', '4', '5'}
        board_ranks = {card[0] for card in cards}
        return len(wheel_ranks & board_ranks) >= 3

    def _convert_to_list(self, cards) -> List[str]:
        """Convert cards to list if they are a tuple"""
        return list(cards) if isinstance(cards, tuple) else cards

    def evaluate_hand_strength(self, hole_cards: List[str], board: List[str]) -> HandStrength:
        """Evaluate hand strength using OpenPPL categories"""
        # Convert hole_cards to list if it's a tuple
        if isinstance(hole_cards, tuple):
            hole_cards = list(hole_cards)
            
        # Preflop
        if not board:
            return self._evaluate_preflop(hole_cards)
            
        # Made hands
        made_hand = self._evaluate_made_hand(hole_cards, board)
        if made_hand.value >= HandStrength.TWO_PAIR_BOTTOM.value:
            return made_hand
            
        # Drawing hands
        draw_hand = self._evaluate_draws(hole_cards, board)
        if draw_hand and draw_hand.is_strong_draw:
            return draw_hand
            
        # Return the stronger of made hand or draw
        if draw_hand and draw_hand.value > made_hand.value:
            return draw_hand
        return made_hand

    def _evaluate_preflop(self, hole_cards: List[str]) -> HandStrength:
        """Evaluate preflop hand strength"""
        if not hole_cards or len(hole_cards) != 2:
            return HandStrength.HIGH_CARD
            
        ranks = [self._rank_to_number(card[0]) for card in hole_cards]
        suited = hole_cards[0][1] == hole_cards[1][1]
        
        # Pocket pairs
        if ranks[0] == ranks[1]:
            if ranks[0] >= 13:  # AA
                return HandStrength.OVERPAIR_STRONG
            if ranks[0] >= 11:  # KK, QQ
                return HandStrength.OVERPAIR_STRONG
            if ranks[0] >= 9:   # JJ, TT
                return HandStrength.OVERPAIR_WEAK
            return HandStrength.MIDDLE_PAIR_GOOD_KICKER
            
        # Non-paired hands
        high_rank = max(ranks)
        low_rank = min(ranks)
        gap = high_rank - low_rank
        
        if high_rank == 14:  # Ace
            if low_rank >= 12:  # AK
                return HandStrength.TOP_PAIR_GOOD_KICKER
            if low_rank >= 10:  # AQ, AJ
                return HandStrength.TOP_PAIR_WEAK_KICKER
            if suited and low_rank >= 8:  # AT+s
                return HandStrength.TOP_PAIR_WEAK_KICKER
            if suited:
                return HandStrength.FLUSH_DRAW
            return HandStrength.ACE_HIGH
            
        if high_rank == 13:  # King
            if low_rank >= 11:  # KQ
                return HandStrength.TOP_PAIR_WEAK_KICKER
            if suited and low_rank >= 9:  # KJ+s
                return HandStrength.FLUSH_DRAW
            return HandStrength.KING_HIGH
            
        if suited and gap <= 2 and low_rank >= 9:
            return HandStrength.FLUSH_DRAW
            
        return HandStrength.HIGH_CARD

    def _evaluate_made_hand(self, hole_cards: List[str], board: List[str]) -> HandStrength:
        """Evaluate made hand strength"""
        all_cards = hole_cards + board
        score = self._calculate_hand_score(all_cards)
        
        # Straight flush
        if score >= 8000000:
            return HandStrength.STRAIGHT_FLUSH
            
        # Four of a kind
        if score >= 7000000:
            return HandStrength.FOUR_OF_A_KIND
            
        # Full house
        if score >= 6000000:
            return HandStrength.FULL_HOUSE
            
        # Flush
        if score >= 5000000:
            return HandStrength.FLUSH
            
        # Straight
        if score >= 4000000:
            return HandStrength.STRAIGHT
            
        # Three of a kind
        if score >= 3000000:
            if self._made_with_hole_cards(hole_cards, board, 2):
                if self._is_top_set(hole_cards, board):
                    return HandStrength.TOP_SET
                return HandStrength.SET
            return HandStrength.TRIPS
            
        # Two pair
        if score >= 2000000:
            if self._is_top_two_pair(hole_cards, board):
                return HandStrength.TWO_PAIR_TOP
            if self._is_top_and_middle_pair(hole_cards, board):
                return HandStrength.TWO_PAIR_TOP_AND_MIDDLE
            if self._is_top_and_bottom_pair(hole_cards, board):
                return HandStrength.TWO_PAIR_TOP_AND_BOTTOM
            return HandStrength.TWO_PAIR_BOTTOM
            
        # One pair
        if score >= 1000000:
            if self._have_overpair(hole_cards, board):
                if self._rank_to_number(hole_cards[0][0]) >= 12:  # QQ+
                    return HandStrength.OVERPAIR_STRONG
                return HandStrength.OVERPAIR_WEAK
                
            if self._have_top_pair(hole_cards, board):
                if self._have_good_kicker(hole_cards, board):
                    return HandStrength.TOP_PAIR_GOOD_KICKER
                if self._have_medium_kicker(hole_cards, board):
                    return HandStrength.TOP_PAIR_WEAK_KICKER
                return HandStrength.TOP_PAIR_BAD_KICKER
                
            if self._have_middle_pair(hole_cards, board):
                if self._have_good_kicker(hole_cards, board):
                    return HandStrength.MIDDLE_PAIR_GOOD_KICKER
                return HandStrength.MIDDLE_PAIR_BAD_KICKER
                
            if self._have_good_kicker(hole_cards, board):
                return HandStrength.BOTTOM_PAIR_GOOD_KICKER
            return HandStrength.BOTTOM_PAIR_BAD_KICKER
            
        # High card
        if self._rank_to_number(hole_cards[0][0]) == 14:  # Ace
            return HandStrength.ACE_HIGH
        if self._rank_to_number(hole_cards[0][0]) == 13:  # King
            return HandStrength.KING_HIGH
        return HandStrength.HIGH_CARD

    def _evaluate_draws(self, hole_cards: List[str], board: List[str]) -> Optional[HandStrength]:
        """Evaluate drawing hand strength"""
        if len(board) >= 5:  # No draws on river
            return None
            
        # Flush draws
        flush_draw = self._evaluate_flush_draw(hole_cards, board)
        if flush_draw:
            if self._have_pair(hole_cards, board):
                return HandStrength.FLUSH_DRAW_WITH_PAIR
            if self._have_straight_draw(hole_cards, board):
                return HandStrength.FLUSH_DRAW_WITH_STRAIGHT_DRAW
            if self._have_overcard(hole_cards, board):
                return HandStrength.FLUSH_DRAW_WITH_OVERCARD
            if self._is_nut_flush_draw(hole_cards, board):
                return HandStrength.NUT_FLUSH_DRAW
            return HandStrength.FLUSH_DRAW
            
        # Straight draws
        if self._have_oesd(hole_cards, board):
            if self._have_overcards(hole_cards, board):
                return HandStrength.OVERCARDS_WITH_STRAIGHT_DRAW
            if self._have_pair(hole_cards, board):
                return HandStrength.PAIR_WITH_STRAIGHT_DRAW
            return HandStrength.OPEN_ENDED
            
        if self._have_gutshot(hole_cards, board):
            if self._have_double_gutshot(hole_cards, board):
                return HandStrength.DOUBLE_GUTSHOT
            if self._have_overcards(hole_cards, board):
                return HandStrength.OVERCARDS_WITH_GUTSHOT
            if self._have_pair(hole_cards, board):
                return HandStrength.PAIR_WITH_GUTSHOT
            return HandStrength.GUTSHOT
            
        # Backdoor draws
        if len(board) == 3:  # Only check backdoor draws on flop
            if self._have_backdoor_flush_draw(hole_cards, board):
                return HandStrength.BACKDOOR_FLUSH_DRAW
            if self._have_backdoor_straight_draw(hole_cards, board):
                return HandStrength.BACKDOOR_STRAIGHT_DRAW
            if self._have_backdoor_two_cards_straight(hole_cards, board):
                return HandStrength.BACKDOOR_TWO_CARDS_STRAIGHT
                
        # Overcards
        if self._have_overcards(hole_cards, board):
            return HandStrength.TWO_OVERCARDS
            
        return None

    def _have_pair(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have at least a pair"""
        ranks = [card[0] for card in hole_cards + board]
        return any(ranks.count(r) >= 2 for r in set(ranks))

    def _have_top_pair(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have top pair"""
        if not board:
            return False
        top_rank = max(card[0] for card in board)
        return any(card[0] == top_rank for card in hole_cards)

    def _have_middle_pair(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have middle pair"""
        if not board or len(board) < 2:
            return False
        board_ranks = sorted([self._rank_to_number(card[0]) for card in board])
        hole_ranks = [self._rank_to_number(card[0]) for card in hole_cards]
        if len(board_ranks) >= 3:
            return board_ranks[-2] in hole_ranks
        return board_ranks[-1] in hole_ranks

    def _have_good_kicker(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a good kicker (A, K, Q)"""
        kicker = max(self._rank_to_number(card[0]) for card in hole_cards 
                    if not any(card[0] == b[0] for b in board))
        return kicker >= 12

    def _have_medium_kicker(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a medium kicker (J, T)"""
        kicker = max(self._rank_to_number(card[0]) for card in hole_cards 
                    if not any(card[0] == b[0] for b in board))
        return 10 <= kicker <= 11

    def _is_top_set(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have top set"""
        if not board:
            return False
        top_rank = max(card[0] for card in board)
        return (hole_cards[0][0] == hole_cards[1][0] == top_rank)

    def _is_top_two_pair(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have top two pair"""
        if not board:
            return False
        board_ranks = sorted([self._rank_to_number(card[0]) for card in board])
        hole_ranks = [self._rank_to_number(card[0]) for card in hole_cards]
        return (max(board_ranks) in hole_ranks and 
                board_ranks[-2] in hole_ranks)

    def _is_top_and_middle_pair(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have top and middle pair"""
        if not board or len(board) < 3:
            return False
        board_ranks = sorted([self._rank_to_number(card[0]) for card in board])
        hole_ranks = [self._rank_to_number(card[0]) for card in hole_cards]
        return (max(board_ranks) in hole_ranks and 
                board_ranks[-2] in hole_ranks)

    def _is_top_and_bottom_pair(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have top and bottom pair"""
        if not board or len(board) < 2:
            return False
        board_ranks = sorted([self._rank_to_number(card[0]) for card in board])
        hole_ranks = [self._rank_to_number(card[0]) for card in hole_cards]
        return (max(board_ranks) in hole_ranks and 
                min(board_ranks) in hole_ranks)

    def _have_overcard(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have at least one overcard"""
        if not board:
            return False
        max_board = max(self._rank_to_number(card[0]) for card in board)
        return any(self._rank_to_number(card[0]) > max_board for card in hole_cards)

    def _have_overcards(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have two overcards"""
        if not board:
            return False
        max_board = max(self._rank_to_number(card[0]) for card in board)
        return all(self._rank_to_number(card[0]) > max_board for card in hole_cards)

    def _evaluate_flush_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a flush draw"""
        if len(board) >= 5:
            return False
        suits = [card[1] for card in hole_cards + board]
        return any(suits.count(s) >= 4 for s in set(suits))

    def _is_nut_flush_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have the nut flush draw"""
        if not self._evaluate_flush_draw(hole_cards, board):
            return False
        suit = next(s for s in 'hdcs' 
                   if [card[1] for card in hole_cards + board].count(s) >= 4)
        suited_cards = [card for card in hole_cards + board if card[1] == suit]
        return any(card[0] == 'A' for card in hole_cards 
                  if card[1] == suit)

    def _have_straight_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have any straight draw"""
        return (self._have_oesd(hole_cards, board) or 
                self._have_gutshot(hole_cards, board))

    def _have_backdoor_flush_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a backdoor flush draw"""
        if len(board) != 3:
            return False
        suits = [card[1] for card in hole_cards + board]
        return any(suits.count(s) == 3 for s in set(suits))

    def _have_backdoor_straight_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a backdoor straight draw"""
        if len(board) != 3:
            return False
        ranks = sorted([self._rank_to_number(card[0]) for card in hole_cards + board])
        gaps = sum(ranks[i+1] - ranks[i] - 1 for i in range(len(ranks)-1))
        return gaps <= 3

    def _have_backdoor_two_cards_straight(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have two cards to a straight"""
        if len(board) != 3:
            return False
        ranks = sorted([self._rank_to_number(card[0]) for card in hole_cards + board])
        for i in range(len(ranks)-1):
            if ranks[i+1] - ranks[i] <= 2:
                return True
        return False

    def _rank_to_number(self, rank: str) -> int:
        """Convert card rank to numeric value"""
        return self.rank_values.get(rank, 0)  # Return 0 for invalid ranks

    def _create_deck(self, hole_cards: Tuple[str, str], board: List[str]) -> List[str]:
        """Create a deck excluding known cards"""
        deck = [r + s for r in self.RANKS for s in self.SUITS]
        for card in hole_cards + tuple(board):
            if card in deck:
                deck.remove(card)
        return deck

    def _calculate_hand_score(self, cards: List[str]) -> int:
        """Calculate numerical score for a hand"""
        if len(cards) < 5:
            return 0
            
        best_score = 0
        for hand in combinations(cards, 5):
            score = self._score_five_card_hand(hand)
            best_score = max(best_score, score)
        return best_score

    def _score_five_card_hand(self, hand: Tuple[str, ...]) -> int:
        """Score a five card hand"""
        ranks = [card[0] for card in hand]
        suits = [card[1] for card in hand]
        
        # Check for flush
        is_flush = len(set(suits)) == 1
        
        # Convert ranks to values and sort
        values = sorted([self.rank_values[r] for r in ranks])
        is_straight = self._is_straight(values)
        
        if is_straight and is_flush:
            return 8000000 + max(values)  # Straight flush
            
        # Count rank frequencies
        rank_counts = {}
        for val in values:
            rank_counts[val] = rank_counts.get(val, 0) + 1
            
        # Four of a kind
        if 4 in rank_counts.values():
            rank = [r for r, c in rank_counts.items() if c == 4][0]
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return 7000000 + rank * 13 + kicker
            
        # Full house
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            three_rank = [r for r, c in rank_counts.items() if c == 3][0]
            two_rank = [r for r, c in rank_counts.items() if c == 2][0]
            return 6000000 + three_rank * 13 + two_rank
            
        if is_flush:
            return 5000000 + sum(values)  # Flush
            
        if is_straight:
            return 4000000 + max(values)  # Straight
            
        # Three of a kind
        if 3 in rank_counts.values():
            three_rank = [r for r, c in rank_counts.items() if c == 3][0]
            kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return 3000000 + three_rank * 169 + kickers[0] * 13 + kickers[1]
            
        # Two pair
        if list(rank_counts.values()).count(2) == 2:
            pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return 2000000 + pairs[0] * 169 + pairs[1] * 13 + kicker
            
        # One pair
        if 2 in rank_counts.values():
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return 1000000 + pair_rank * 2197 + kickers[0] * 169 + kickers[1] * 13 + kickers[2]
            
        # High card
        return sum(val * (13 ** i) for i, val in enumerate(reversed(values)))

    def _is_straight(self, values: List[int]) -> bool:
        """Check if the values form a straight"""
        if len(values) != 5:
            return False
        
        # Handle Ace-low straight
        if values == [0, 1, 2, 3, 12]:
            return True
            
        return values == list(range(min(values), max(values) + 1))

    def _made_with_hole_cards(self, hole_cards: tuple, board: list, count: int) -> bool:
        """Check if a hand was made using the specified number of hole cards"""
        hole_ranks = {card[0] for card in hole_cards}
        board_ranks = {card[0] for card in board}
        rank_counts = {}
        
        # Count ranks
        for rank in hole_ranks | board_ranks:
            rank_count = sum(1 for card in hole_cards + board if card[0] == rank)
            rank_counts[rank] = rank_count
            
        # Check if any rank appears count times and uses hole cards
        for rank in hole_ranks:
            if rank_counts[rank] == count:
                hole_count = sum(1 for card in hole_cards if card[0] == rank)
                if hole_count > 0:
                    return True
        return False
        
    def _is_top_two_pair(self, hole_cards: tuple, board: list) -> bool:
        """Check if we have top two pair"""
        board_ranks = sorted([self.rank_values[card[0]] for card in board])
        hole_ranks = {self.rank_values[card[0]] for card in hole_cards}
        
        # Need at least one hole card to pair with highest board card
        return (max(board_ranks) in hole_ranks and 
                any(r in hole_ranks for r in board_ranks[:-1]))
                
    def _is_top_pair(self, hole_cards: tuple, board: list) -> bool:
        """Check if we have top pair"""
        board_ranks = [self.rank_values[card[0]] for card in board]
        hole_ranks = {self.rank_values[card[0]] for card in hole_cards}
        return max(board_ranks) in hole_ranks
        
    def _is_top_two_pair(self, hole_cards: tuple, board: list) -> bool:
        """Check if we have top two pair"""
        board_ranks = sorted([self.rank_values[card[0]] for card in board])
        hole_ranks = {self.rank_values[card[0]] for card in hole_cards}
        
        # Need at least one hole card to pair with highest board card
        return (max(board_ranks) in hole_ranks and 
                any(r in hole_ranks for r in board_ranks[:-1]))
                
    def _is_top_pair(self, hole_cards: tuple, board: list) -> bool:
        """Check if we have top pair"""
        board_ranks = [self.rank_values[card[0]] for card in board]
        hole_ranks = {self.rank_values[card[0]] for card in hole_cards}
        return max(board_ranks) in hole_ranks
        
    def _have_flush_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a flush draw"""
        # Convert hole_cards to list if it's a tuple
        if isinstance(hole_cards, tuple):
            hole_cards = list(hole_cards)
        
        # Get all suits
        suits = [card[1] for card in hole_cards + board]
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
            
        # Check if we have 4 cards of any suit
        return any(count == 4 for count in suit_counts.values())
        
    def _have_nut_flush_draw(self, hole_cards: tuple, board: list) -> bool:
        """Check if we have the nut flush draw"""
        if not self._have_flush_draw(hole_cards, board):
            return False
            
        # Find the suit we have a draw to
        suits = [card[1] for card in hole_cards + board]
        draw_suit = next(suit for suit in set(suits) if suits.count(suit) == 4)
        
        # Get all cards of that suit
        suited_cards = [card for card in hole_cards + board if card[1] == draw_suit]
        suited_ranks = [self.rank_values[card[0]] for card in suited_cards]
        
        # Check if we have the highest card of that suit
        return max(suited_ranks) in [self.rank_values[card[0]] 
                                   for card in hole_cards 
                                   if card[1] == draw_suit]
                                   
    def _have_straight_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have an open-ended straight draw"""
        # Convert hole_cards to list if it's a tuple
        if isinstance(hole_cards, tuple):
            hole_cards = list(hole_cards)
            
        # Get all ranks and convert to numbers
        ranks = [self._rank_to_number(card[0]) for card in hole_cards + board]
        ranks = sorted(list(set(ranks)))  # Remove duplicates and sort
        
        # Check for 4 consecutive ranks
        for i in range(len(ranks) - 3):
            if ranks[i+3] - ranks[i] == 3:  # 4 consecutive ranks
                return True
                
        return False

    def _have_oesd(self, hole_cards: tuple, board: list) -> bool:
        """Check if we have an open-ended straight draw"""
        ranks = sorted([self.rank_values[card[0]] for card in hole_cards + board])
        # Check for wheel draw
        if 14 in ranks:  # Ace
            ranks.append(1)
            
        # Look for 4 consecutive cards
        for i in range(len(ranks)-3):
            if all(ranks[i+j] == ranks[i]+j for j in range(4)):
                # Check if we can complete the straight on both ends
                low_end = ranks[i] - 1
                high_end = ranks[i] + 4
                return low_end >= 1 and high_end <= 14
        return False

    def _have_gutshot(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a gutshot straight draw"""
        hole_cards = self._convert_to_list(hole_cards)
        board = self._convert_to_list(board)
        
        # Get all ranks and convert to numbers
        ranks = [self._rank_to_number(card[0]) for card in hole_cards + board]
        ranks = sorted(list(set(ranks)))  # Remove duplicates and sort
        
        # Check for 3 consecutive ranks with a gap
        for i in range(len(ranks) - 2):
            if ranks[i+2] - ranks[i] == 3:  # 3 ranks with a 1-card gap
                return True
            
        return False

    def _have_double_gutshot(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a double gutshot straight draw"""
        hole_cards = self._convert_to_list(hole_cards)
        board = self._convert_to_list(board)
        
        # Get all ranks and convert to numbers
        ranks = [self._rank_to_number(card[0]) for card in hole_cards + board]
        ranks = sorted(list(set(ranks)))  # Remove duplicates and sort
        
        # Count number of potential straights
        straight_draws = 0
        for i in range(len(ranks) - 2):
            if ranks[i+2] - ranks[i] == 3:  # 3 ranks with a 1-card gap
                straight_draws += 1
            
        return straight_draws >= 2

    def _have_overcard(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have at least one overcard"""
        if not board:
            return False
        max_board = max(self._rank_to_number(card[0]) for card in board)
        return any(self._rank_to_number(card[0]) > max_board for card in hole_cards)

    def _have_overcards(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have two overcards"""
        if not board:
            return False
        max_board = max(self._rank_to_number(card[0]) for card in board)
        return all(self._rank_to_number(card[0]) > max_board for card in hole_cards)

    def _have_backdoor_flush_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a backdoor flush draw"""
        if len(board) != 3:
            return False
        suits = [card[1] for card in hole_cards + board]
        return any(suits.count(s) == 3 for s in set(suits))

    def _have_backdoor_straight_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have a backdoor straight draw"""
        if len(board) != 3:
            return False
        ranks = sorted([self._rank_to_number(card[0]) for card in hole_cards + board])
        gaps = sum(ranks[i+1] - ranks[i] - 1 for i in range(len(ranks)-1))
        return gaps <= 3

    def _have_backdoor_two_cards_straight(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have two cards to a straight"""
        if len(board) != 3:
            return False
        ranks = sorted([self._rank_to_number(card[0]) for card in hole_cards + board])
        for i in range(len(ranks)-1):
            if ranks[i+1] - ranks[i] <= 2:
                return True
        return False

    def _have_overcards(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have two overcards"""
        if not board:
            return False
        max_board = max(self._rank_to_number(card[0]) for card in board)
        return all(self._rank_to_number(card[0]) > max_board for card in hole_cards)

    def _have_straight_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have an open-ended straight draw"""
        # Convert hole_cards to list if it's a tuple
        if isinstance(hole_cards, tuple):
            hole_cards = list(hole_cards)
            
        # Get all ranks and convert to numbers
        ranks = [self._rank_to_number(card[0]) for card in hole_cards + board]
        ranks = sorted(list(set(ranks)))  # Remove duplicates and sort
        
        # Check for 4 consecutive ranks
        for i in range(len(ranks) - 3):
            if ranks[i+3] - ranks[i] == 3:  # 4 consecutive ranks
                return True
                
        return False

    def _have_oesd(self, hole_cards: tuple, board: list) -> bool:
        """Check if we have an open-ended straight draw"""
        ranks = sorted([self.rank_values[card[0]] for card in hole_cards + board])
        # Check for wheel draw
        if 14 in ranks:  # Ace
            ranks.append(1)
            
        # Look for 4 consecutive cards
        for i in range(len(ranks)-3):
            if all(ranks[i+j] == ranks[i]+j for j in range(4)):
                # Check if we can complete the straight on both ends
                low_end = ranks[i] - 1
                high_end = ranks[i] + 4
                return low_end >= 1 and high_end <= 14
        return False

    def _is_nut_flush_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have the nut flush draw"""
        if not self._have_flush_draw(hole_cards, board):
            return False
        suit = next(s for s in 'hdcs' 
                   if [card[1] for card in hole_cards + board].count(s) >= 4)
        suited_cards = [card for card in hole_cards + board if card[1] == suit]
        return any(card[0] == 'A' for card in hole_cards 
                  if card[1] == suit)

    def _have_straight_draw(self, hole_cards: List[str], board: List[str]) -> bool:
        """Check if we have an open-ended straight draw"""
        # Convert hole_cards to list if it's a tuple
        if isinstance(hole_cards, tuple):
            hole_cards = list(hole_cards)
            
        # Get all ranks and convert to numbers
        ranks = [self._rank_to_number(card[0]) for card in hole_cards + board]
        ranks = sorted(list(set(ranks)))  # Remove duplicates and sort
        
        # Check for 4 consecutive ranks
        for i in range(len(ranks) - 3):
            if ranks[i+3] - ranks[i] == 3:  # 4 consecutive ranks
                return True
                
        return False

    def _have_oesd(self, hole_cards: tuple, board: list) -> bool:
        """Check if we have an open-ended straight draw"""
        ranks = sorted([self.rank_values[card[0]] for card in hole_cards + board])
        # Check for wheel draw
        if 14 in ranks:  # Ace
            ranks.append(1)
            
        # Look for 4 consecutive cards
        for i in range(len(ranks)-3):
            if all(ranks[i+j] == ranks[i]+j for j in range(4)):
                # Check if we can complete the straight on both ends
                low_end = ranks[i] - 1
                high_end = ranks[i] + 4
                return low_end >= 1 and high_end <= 14
        return False

    def _rank_to_number(self, rank: str) -> int:
        """Convert card rank to numeric value"""
        return self.rank_values.get(rank, 0)  # Return 0 for invalid ranks 