from typing import Dict, List, Optional
from poker_enums import Street, Position, Action
from table_state import TableState, Player
from gecko_bot import GeckoBot
from hand_evaluator import HandEvaluator
import random

class GameRunner:
    def __init__(self):
        self.table_state = TableState()
        self.bot = GeckoBot(self.table_state)
        self.deck = self._create_deck()
        self.small_blind = 10
        self.big_blind = 20
        self.hand_evaluator = HandEvaluator()
        
    def _create_deck(self) -> List[str]:
        """Create a standard 52-card deck"""
        ranks = '23456789TJQKA'
        suits = 'hdcs'
        deck = [r + s for r in ranks for s in suits]
        random.shuffle(deck)
        return deck
        
    def setup_game(self):
        """Initialize a new game"""
        print("\n=== New Game Started ===\n")
        
        # Reset table state
        self.table_state = TableState()
        self.bot = GeckoBot(self.table_state)
        
        # Set up players
        self.table_state.hero_seat = 1
        self.table_state.button_seat = 0
        self.table_state.total_players = 3
        
        # Initialize player stacks (1500 bb starting stack)
        for seat in range(3):
            position = Position.BUTTON if seat == 0 else \
                      Position.SMALL_BLIND if seat == 1 else \
                      Position.BIG_BLIND
            self.table_state.update_player(
                seat=seat,
                stack=30000,  # 1500 bb
                position=position,
                in_hand=True
            )
            
        # Reset other state
        self.table_state.pot_size = 0.0
        self.table_state.current_bet = 0.0
        self.table_state.min_raise = self.big_blind
        self.table_state.last_aggressor = None
        self.table_state.community_cards = []
        self.table_state.current_street = Street.PREFLOP
        
    def run_hand(self):
        """Run a single hand of poker"""
        self._deal_cards()
        self._post_blinds()
        
        # Run betting rounds
        if self._run_betting_round(Street.PREFLOP):
            self._deal_flop()
            if self._run_betting_round(Street.FLOP):
                self._deal_turn()
                if self._run_betting_round(Street.TURN):
                    self._deal_river()
                    self._run_betting_round(Street.RIVER)
                    
        self._show_results()
        
    def _deal_cards(self):
        """Deal hole cards"""
        self.deck = self._create_deck()  # Reset and shuffle deck
        self.table_state.hero_cards = (self.deck.pop(), self.deck.pop())
        print("\n=== Hole Cards ===")
        print(f"Your hand: {self.table_state.hero_cards[0]} {self.table_state.hero_cards[1]}")
        
        # Add Monte Carlo evaluation
        prwin = self.hand_evaluator.calculate_prwin(
            self.table_state.hero_cards, 
            self.table_state.community_cards,
            num_opponents=2,  # Since we're playing 3-handed
            num_simulations=1000
        )
        print(f"Monte Carlo win probability: {prwin:.2%}")
        
    def _post_blinds(self):
        """Post small and big blinds"""
        # Small blind
        sb_seat = (self.table_state.button_seat + 1) % 3
        self.table_state.players[sb_seat].stack -= self.small_blind
        self.table_state.pot_size += self.small_blind
        
        # Big blind
        bb_seat = (self.table_state.button_seat + 2) % 3
        self.table_state.players[bb_seat].stack -= self.big_blind
        self.table_state.pot_size += self.big_blind
        self.table_state.current_bet = self.big_blind
        
        print("\n=== Blinds Posted ===")
        print(f"Small Blind: {self.small_blind}")
        print(f"Big Blind: {self.big_blind}")
        
    def _deal_flop(self):
        """Deal and display the flop"""
        # Burn one card
        self.deck.pop()
        
        # Deal flop
        self.table_state.community_cards = [
            self.deck.pop(),
            self.deck.pop(),
            self.deck.pop()
        ]
        
        print("\n=== Flop ===")
        print(" ".join(self.table_state.community_cards))
        
        # Add Monte Carlo evaluation
        prwin = self.hand_evaluator.calculate_prwin(
            self.table_state.hero_cards, 
            self.table_state.community_cards,
            num_opponents=2,
            num_simulations=1000
        )
        print(f"Monte Carlo win probability: {prwin:.2%}")
        
    def _deal_turn(self):
        """Deal and display the turn"""
        # Burn one card
        self.deck.pop()
        
        # Deal turn
        self.table_state.community_cards.append(self.deck.pop())
        
        print("\n=== Turn ===")
        print(" ".join(self.table_state.community_cards))
        
        # Add Monte Carlo evaluation
        prwin = self.hand_evaluator.calculate_prwin(
            self.table_state.hero_cards, 
            self.table_state.community_cards,
            num_opponents=2,
            num_simulations=1000
        )
        print(f"Monte Carlo win probability: {prwin:.2%}")
        
    def _deal_river(self):
        """Deal and display the river"""
        # Burn one card
        self.deck.pop()
        
        # Deal river
        self.table_state.community_cards.append(self.deck.pop())
        
        print("\n=== River ===")
        print(" ".join(self.table_state.community_cards))
        
        # Add Monte Carlo evaluation
        prwin = self.hand_evaluator.calculate_prwin(
            self.table_state.hero_cards, 
            self.table_state.community_cards,
            num_opponents=2,
            num_simulations=1000
        )
        print(f"Monte Carlo win probability: {prwin:.2%}")
        
    def _run_betting_round(self, street: Street) -> bool:
        """Run a betting round. Returns False if hand is over."""
        self.table_state.current_street = street
        print(f"\n=== {street.name} Betting Round ===")
        
        # Display current state
        print(f"Pot: {self.table_state.pot_size}")
        print(f"Your stack: {self.table_state.players[self.table_state.hero_seat].stack}")
        
        # Simulate opponent actions
        if street == Street.PREFLOP:
            # Button calls or raises preflop
            if random.random() < 0.4:  # 40% chance to raise
                raise_size = self.big_blind * 3
                self.table_state.players[0].stack -= raise_size
                self.table_state.pot_size += raise_size
                self.table_state.current_bet = raise_size
                print(f"Button raises to {raise_size}")
            else:
                self.table_state.players[0].stack -= self.big_blind
                self.table_state.pot_size += self.big_blind
                print("Button calls")
        else:
            # Post-flop opponent actions
            if random.random() < 0.3:  # 30% chance to bet
                bet_size = self.table_state.pot_size * 0.5  # Half pot bet
                self.table_state.players[0].stack -= bet_size
                self.table_state.pot_size += bet_size
                self.table_state.current_bet = bet_size
                print(f"Opponent bets {bet_size}")
            else:
                print("Opponent checks")
        
        # Get bot's action
        action, bet_size = self.bot.make_decision()
        
        # Display and process bot's action
        if action == Action.FOLD:
            print("Bot folds")
            return False
        elif action == Action.CHECK:
            print("Bot checks")
        elif action == Action.CALL:
            print(f"Bot calls {bet_size}")
            self.table_state.players[self.table_state.hero_seat].stack -= bet_size
            self.table_state.pot_size += bet_size
            self.table_state.hero_stack = self.table_state.players[self.table_state.hero_seat].stack
        elif action == Action.RAISE:
            print(f"Bot raises to {bet_size}")
            self.table_state.players[self.table_state.hero_seat].stack -= bet_size
            self.table_state.pot_size += bet_size
            self.table_state.hero_stack = self.table_state.players[self.table_state.hero_seat].stack
        elif action == Action.ALL_IN:
            print(f"Bot goes all-in for {bet_size}")
            self.table_state.players[self.table_state.hero_seat].stack -= bet_size
            self.table_state.pot_size += bet_size
            self.table_state.hero_stack = self.table_state.players[self.table_state.hero_seat].stack
            
        return True
        
    def _show_results(self):
        """Show hand results"""
        print("\n=== Hand Complete ===")
        print(f"Final pot: {self.table_state.pot_size}")
        print(f"Your final stack: {self.table_state.players[self.table_state.hero_seat].stack}")
        
def main():
    """Main game loop"""
    runner = GameRunner()
    for i in range(5):
        print(f"\n=== Round {i+1} ===")
        runner.setup_game()
        runner.run_hand()
    print("\nThanks for playing!")

if __name__ == "__main__":
    main() 