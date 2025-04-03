from enum import Enum, auto
from typing import List

class Position(Enum):
    BUTTON = auto()
    SMALL_BLIND = auto()
    BIG_BLIND = auto()
    UTG = auto()
    MP = auto()
    CO = auto()

class Street(Enum):
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()

class Action(Enum):
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    RAISE = auto()
    ALL_IN = auto()

class HandStrength(Enum):
    # No made hand
    HIGH_CARD = 0
    ACE_HIGH = 5
    KING_HIGH = 3
    
    # One pair hands
    BOTTOM_PAIR_BAD_KICKER = 10
    BOTTOM_PAIR_GOOD_KICKER = 15
    MIDDLE_PAIR_BAD_KICKER = 20
    MIDDLE_PAIR_GOOD_KICKER = 25
    TOP_PAIR_BAD_KICKER = 30
    TOP_PAIR_WEAK_KICKER = 35
    TOP_PAIR_GOOD_KICKER = 40
    OVERPAIR_WEAK = 45
    OVERPAIR_STRONG = 50
    
    # Two pair hands
    TWO_PAIR_BOTTOM = 55
    TWO_PAIR_TOP_AND_BOTTOM = 60
    TWO_PAIR_TOP_AND_MIDDLE = 65
    TWO_PAIR_TOP = 70
    
    # Three of a kind
    SET = 75
    TOP_SET = 80
    TRIPS = 73
    
    # Straight and better
    STRAIGHT = 85
    FLUSH = 90
    FULL_HOUSE = 100
    FOUR_OF_A_KIND = 110
    STRAIGHT_FLUSH = 120
    
    # Drawing hands
    GUTSHOT = 12
    DOUBLE_GUTSHOT = 22
    OPEN_ENDED = 32
    FLUSH_DRAW = 42
    FLUSH_DRAW_WITH_OVERCARD = 44
    FLUSH_DRAW_WITH_PAIR = 52
    FLUSH_DRAW_WITH_STRAIGHT_DRAW = 62
    NUT_FLUSH_DRAW = 72
    
    # Combo draws
    TWO_OVERCARDS = 8
    OVERCARDS_WITH_GUTSHOT = 18
    OVERCARDS_WITH_STRAIGHT_DRAW = 38
    PAIR_WITH_GUTSHOT = 28
    PAIR_WITH_STRAIGHT_DRAW = 48
    
    # Backdoor draws
    BACKDOOR_FLUSH_DRAW = 6
    BACKDOOR_STRAIGHT_DRAW = 4
    BACKDOOR_TWO_CARDS_STRAIGHT = 2
    
    @property
    def is_made_hand(self) -> bool:
        return self.value >= self.BOTTOM_PAIR_BAD_KICKER.value and not self.is_draw
        
    @property
    def is_draw(self) -> bool:
        return self in [
            self.GUTSHOT,
            self.DOUBLE_GUTSHOT,
            self.OPEN_ENDED,
            self.FLUSH_DRAW,
            self.FLUSH_DRAW_WITH_OVERCARD,
            self.FLUSH_DRAW_WITH_PAIR,
            self.FLUSH_DRAW_WITH_STRAIGHT_DRAW,
            self.NUT_FLUSH_DRAW,
            self.TWO_OVERCARDS,
            self.OVERCARDS_WITH_GUTSHOT,
            self.OVERCARDS_WITH_STRAIGHT_DRAW,
            self.BACKDOOR_FLUSH_DRAW,
            self.BACKDOOR_STRAIGHT_DRAW,
            self.BACKDOOR_TWO_CARDS_STRAIGHT
        ]
        
    @property
    def is_strong_made_hand(self) -> bool:
        return self.value >= self.TWO_PAIR_TOP_AND_BOTTOM.value and not self.is_draw
        
    @property
    def is_medium_made_hand(self) -> bool:
        return (self.value >= self.TOP_PAIR_GOOD_KICKER.value and 
                self.value < self.TWO_PAIR_TOP_AND_BOTTOM.value and 
                not self.is_draw)
        
    @property
    def is_weak_made_hand(self) -> bool:
        return (self.value >= self.BOTTOM_PAIR_BAD_KICKER.value and 
                self.value < self.TOP_PAIR_GOOD_KICKER.value and 
                not self.is_draw)
                
    @property
    def is_strong_draw(self) -> bool:
        return self in [
            self.FLUSH_DRAW_WITH_PAIR,
            self.FLUSH_DRAW_WITH_STRAIGHT_DRAW,
            self.NUT_FLUSH_DRAW,
            self.OVERCARDS_WITH_STRAIGHT_DRAW
        ]
        
    @property
    def is_medium_draw(self) -> bool:
        return self in [
            self.FLUSH_DRAW,
            self.FLUSH_DRAW_WITH_OVERCARD,
            self.OPEN_ENDED,
            self.DOUBLE_GUTSHOT,
            self.OVERCARDS_WITH_GUTSHOT
        ]
        
    @property
    def is_weak_draw(self) -> bool:
        return self in [
            self.GUTSHOT,
            self.TWO_OVERCARDS,
            self.BACKDOOR_FLUSH_DRAW,
            self.BACKDOOR_STRAIGHT_DRAW,
            self.BACKDOOR_TWO_CARDS_STRAIGHT
        ]

# Constants for decision making
MINIMUM_RAISE_MULTIPLIER = 2.0
DEFAULT_POT_COMMITMENT_THRESHOLD = 0.33  # 33% of stack
MINIMUM_DEFENSE_FREQUENCY = 0.3  # 30% defense frequency
MAX_PLAYERS = 6

# Position weights for decision making
POSITION_WEIGHTS = {
    Position.BUTTON: 1.0,
    Position.SMALL_BLIND: 0.7,
    Position.BIG_BLIND: 0.8,
    Position.UTG: 0.5,
    Position.MP: 0.6,
    Position.CO: 0.9
} 