from enum import Enum, auto, IntEnum
from typing import List, Tuple

class Position(Enum):
    BUTTON = auto()
    SMALL_BLIND = auto()
    BIG_BLIND = auto()
    UTG = auto()
    MP = auto()
    CO = auto()

class Street(IntEnum):
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4

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
    TRIPS = 73
    SET = 75
    SECOND_SET = 77
    TOP_SET = 80

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
    SECOND_NUT_FLUSH_DRAW = 71

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

    # Advanced hand categories
    SECOND_TOP_PAIR_GOOD_KICKER = 37
    SECOND_TOP_PAIR_BAD_KICKER = 33
    THIRD_TOP_PAIR_GOOD_KICKER = 27
    THIRD_TOP_PAIR_BAD_KICKER = 23

    # Redraw hands
    PAIR_WITH_FLUSH_REDRAW = 53
    PAIR_WITH_STRAIGHT_REDRAW = 49
    SET_WITH_FLUSH_REDRAW = 83
    SET_WITH_STRAIGHT_REDRAW = 82

    # Blocker-related hands
    BLUFF_WITH_BLOCKER = 7
    SEMI_BLUFF_WITH_BLOCKER = 17

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

class Rank(IntEnum):
    """Card ranks."""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @classmethod
    def from_char(cls, char: str) -> 'Rank':
        """Convert a character to a rank."""
        if char == 'A':
            return cls.ACE
        elif char == 'K':
            return cls.KING
        elif char == 'Q':
            return cls.QUEEN
        elif char == 'J':
            return cls.JACK
        elif char == 'T':
            return cls.TEN
        else:
            return cls(int(char))

class Suit(Enum):
    """Card suits."""
    CLUBS = 'c'
    DIAMONDS = 'd'
    HEARTS = 'h'
    SPADES = 's'

    @classmethod
    def from_char(cls, char: str) -> 'Suit':
        """Convert a character to a suit."""
        if char == 'c':
            return cls.CLUBS
        elif char == 'd':
            return cls.DIAMONDS
        elif char == 'h':
            return cls.HEARTS
        elif char == 's':
            return cls.SPADES
        else:
            raise ValueError(f"Invalid suit: {char}")

class Card:
    """A playing card."""
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    @classmethod
    def from_string(cls, card_str: str) -> 'Card':
        """Create a card from a string (e.g., 'Ah')."""
        rank_char = card_str[0].upper()
        suit_char = card_str[1].lower()
        return cls(Rank.from_char(rank_char), Suit.from_char(suit_char))

    def __str__(self) -> str:
        rank_str = {
            Rank.ACE: 'A',
            Rank.KING: 'K',
            Rank.QUEEN: 'Q',
            Rank.JACK: 'J',
            Rank.TEN: 'T'
        }.get(self.rank, str(self.rank.value))
        return f"{rank_str}{self.suit.value}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

class BoardTexture(Enum):
    """Board texture classifications."""
    DRY = auto()       # Few draws, uncoordinated
    SEMI_WET = auto()  # Some draws, somewhat coordinated
    WET = auto()       # Many draws, coordinated
    VERY_WET = auto()  # Extremely draw-heavy, highly coordinated