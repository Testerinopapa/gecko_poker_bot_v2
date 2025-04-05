from typing import Dict, List, Optional, Tuple, Any
from poker_enums import Street, Position, Action
from table_state import TableState, Player
from gecko_bot import GeckoBot
from hand_evaluator import HandEvaluator
from visualization.match_visualizer import MatchVisualizer, HandData
from logger import get_logger, DebugLevel
from decision_explainer import DecisionExplainer
from verbosity_symbols import VerbositySymbols
import random
import time

class GameRunner:
    def __init__(self, debug_level: DebugLevel = DebugLevel.INFO):
        self.table_state = TableState()
        self.bot = GeckoBot(self.table_state)
        self.deck = self._create_deck()
        self.small_blind = 10
        self.big_blind = 20
        self.hand_evaluator = HandEvaluator()
        self.visualizer = MatchVisualizer()
        self.current_hand_data = None
        self.hand_counter = 0

        # Initialize logger
        self.logger = get_logger(debug_level=debug_level)

        # Initialize decision explainer
        self.decision_explainer = DecisionExplainer(verbosity_level=int(debug_level))

        # Initialize verbosity symbols
        self.verbosity_symbols = VerbositySymbols()

        # Performance tracking
        self.start_time = time.time()

    def _create_deck(self) -> List[str]:
        """Create a standard 52-card deck"""
        ranks = '23456789TJQKA'
        suits = 'hdcs'
        deck = [r + s for r in ranks for s in suits]
        random.shuffle(deck)
        return deck

    def setup_game(self):
        """Initialize a new game"""
        self.logger.info("=== New Game Started ===")

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

        # Reset betting action symbols
        self.table_state.new_hand()

    def run_hand(self):
        """Run a single hand of poker"""
        self.hand_counter += 1
        initial_stack = self.table_state.players[self.table_state.hero_seat].stack

        # Start logging for this hand
        self.logger.start_hand(self.hand_counter)

        # Initialize hand data collection
        self.current_hand_data = HandData(
            hand_id=self.hand_counter,
            hole_cards=None,  # Will be set in _deal_cards
            position=self.table_state.get_hero_position(),
            initial_stack=initial_stack,
            final_stack=initial_stack,  # Will be updated at end
            win_probability={},
            actions={street: [] for street in Street},
            community_cards={street: [] for street in Street},
            pot_sizes={street: 0.0 for street in Street},
            final_pot=0.0,
            result=0.0
        )

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

        # Update final hand data
        final_stack = self.table_state.players[self.table_state.hero_seat].stack
        self.current_hand_data.final_stack = final_stack
        self.current_hand_data.result = (final_stack - initial_stack) / self.big_blind
        self.current_hand_data.final_pot = self.table_state.pot_size

        # End logging for this hand
        result = (final_stack - initial_stack) / self.big_blind
        self.logger.end_hand(self.table_state.pot_size, final_stack, result)

        # Log decision explanation if in debug mode
        if self.logger.debug_level >= DebugLevel.DEBUG:
            # Calculate win probability for the final board state
            win_probability = self.hand_evaluator.calculate_prwin(
                self.table_state.hero_cards,
                self.table_state.community_cards,
                num_opponents=2,
                num_simulations=1000
            )

            hand_data = {
                'street': self.table_state.current_street,
                'hero_cards': self.table_state.hero_cards,
                'community_cards': self.table_state.community_cards,
                'position': self.table_state.players[self.table_state.hero_seat].position,
                'pot_size': self.table_state.pot_size,
                'win_probability': win_probability,
                'result': result
            }
            explanation = self.decision_explainer.explain_hand_decision(hand_data)
            self.logger.debug(f"Hand explanation:\n{explanation}", DebugLevel.DEBUG)

        # Add hand to visualizer
        self.visualizer.add_hand(self.current_hand_data)

    def _deal_cards(self):
        """Deal hole cards"""
        self.deck = self._create_deck()  # Reset and shuffle deck
        self.table_state.hero_cards = (self.deck.pop(), self.deck.pop())

        # Log hole cards
        self.logger.log_hole_cards(self.table_state.hero_cards)

        # Update hand data
        self.current_hand_data.hole_cards = self.table_state.hero_cards

        # Add Monte Carlo evaluation
        prwin = self.hand_evaluator.calculate_prwin(
            self.table_state.hero_cards,
            self.table_state.community_cards,
            num_opponents=2,  # Since we're playing 3-handed
            num_simulations=1000
        )

        # Log win probability
        self.logger.log_win_probability(Street.PREFLOP.name, prwin)

        # Update hand data
        self.current_hand_data.win_probability[Street.PREFLOP] = prwin

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

        # Log blinds
        self.logger.log_blinds(self.small_blind, self.big_blind)

        # Update hand data
        self.current_hand_data.pot_sizes[Street.PREFLOP] = self.table_state.pot_size

        # Log pot update
        self.logger.log_pot_update(self.table_state.pot_size)

    def _deal_flop(self):
        """Deal and display the flop"""
        # Burn one card
        self.deck.pop()

        # Deal flop
        flop_cards = [
            self.deck.pop(),
            self.deck.pop(),
            self.deck.pop()
        ]
        self.table_state.community_cards = flop_cards

        # Update table state to new street
        self.table_state.new_street(Street.FLOP)

        # Log community cards
        self.logger.log_community_cards(Street.FLOP.name, flop_cards)

        # Add Monte Carlo evaluation
        prwin = self.hand_evaluator.calculate_prwin(
            self.table_state.hero_cards,
            self.table_state.community_cards,
            num_opponents=2,
            num_simulations=1000
        )

        # Log win probability
        self.logger.log_win_probability(Street.FLOP.name, prwin)

        # Calculate and log outs information
        outs_count = self.table_state.outs_calculator.calculate_total_outs()
        outs_description = self.table_state.outs_calculator.get_outs_description()
        equity_from_outs = self.table_state.outs_calculator.calculate_equity_from_outs()
        self.logger.log_outs_information(Street.FLOP.name, outs_count, outs_description, equity_from_outs)

        # Update hand data
        self.current_hand_data.community_cards[Street.FLOP] = flop_cards.copy()
        self.current_hand_data.win_probability[Street.FLOP] = prwin
        self.current_hand_data.pot_sizes[Street.FLOP] = self.table_state.pot_size
        self.current_hand_data.outs_count = {Street.FLOP: outs_count}
        self.current_hand_data.equity_from_outs = {Street.FLOP: equity_from_outs}

    def _deal_turn(self):
        """Deal and display the turn"""
        # Burn one card
        self.deck.pop()

        # Deal turn
        turn_card = self.deck.pop()
        self.table_state.community_cards.append(turn_card)

        # Update table state to new street
        self.table_state.new_street(Street.TURN)

        # Log community cards
        self.logger.log_community_cards(Street.TURN.name, self.table_state.community_cards)

        # Add Monte Carlo evaluation
        prwin = self.hand_evaluator.calculate_prwin(
            self.table_state.hero_cards,
            self.table_state.community_cards,
            num_opponents=2,
            num_simulations=1000
        )

        # Log win probability
        self.logger.log_win_probability(Street.TURN.name, prwin)

        # Calculate and log outs information
        outs_count = self.table_state.outs_calculator.calculate_total_outs()
        outs_description = self.table_state.outs_calculator.get_outs_description()
        equity_from_outs = self.table_state.outs_calculator.calculate_equity_from_outs()
        self.logger.log_outs_information(Street.TURN.name, outs_count, outs_description, equity_from_outs)

        # Update hand data
        self.current_hand_data.community_cards[Street.TURN] = self.table_state.community_cards.copy()
        self.current_hand_data.win_probability[Street.TURN] = prwin
        self.current_hand_data.pot_sizes[Street.TURN] = self.table_state.pot_size
        if hasattr(self.current_hand_data, 'outs_count'):
            self.current_hand_data.outs_count[Street.TURN] = outs_count
        else:
            self.current_hand_data.outs_count = {Street.TURN: outs_count}

        if hasattr(self.current_hand_data, 'equity_from_outs'):
            self.current_hand_data.equity_from_outs[Street.TURN] = equity_from_outs
        else:
            self.current_hand_data.equity_from_outs = {Street.TURN: equity_from_outs}

    def _deal_river(self):
        """Deal and display the river"""
        # Burn one card
        self.deck.pop()

        # Deal river
        river_card = self.deck.pop()
        self.table_state.community_cards.append(river_card)

        # Update table state to new street
        self.table_state.new_street(Street.RIVER)

        # Log community cards
        self.logger.log_community_cards(Street.RIVER.name, self.table_state.community_cards)

        # Add Monte Carlo evaluation
        prwin = self.hand_evaluator.calculate_prwin(
            self.table_state.hero_cards,
            self.table_state.community_cards,
            num_opponents=2,
            num_simulations=1000
        )

        # Log win probability
        self.logger.log_win_probability(Street.RIVER.name, prwin)

        # Update hand data
        self.current_hand_data.community_cards[Street.RIVER] = self.table_state.community_cards.copy()
        self.current_hand_data.win_probability[Street.RIVER] = prwin
        self.current_hand_data.pot_sizes[Street.RIVER] = self.table_state.pot_size

    def _run_betting_round(self, street: Street) -> bool:
        """Run a betting round. Returns False if hand is over."""
        self.table_state.current_street = street

        # Start street logging
        self.logger.start_street(street.name)

        # Log current state
        self.logger.log_pot_update(self.table_state.pot_size)
        hero_stack = self.table_state.players[self.table_state.hero_seat].stack
        self.logger.info(f"Hero stack: {hero_stack}")

        # Simulate opponent actions
        if street == Street.PREFLOP:
            # Button calls or raises preflop
            if random.random() < 0.4:  # 40% chance to raise
                raise_size = self.big_blind * 3
                self.table_state.players[0].stack -= raise_size
                self.table_state.pot_size += raise_size
                self.table_state.current_bet = raise_size
                # Record action in table state
                self.table_state.record_action(0, Action.RAISE, raise_size)
                # Log action for display
                self.logger.log_action("Button", "raises", raise_size)
            else:
                self.table_state.players[0].stack -= self.big_blind
                self.table_state.pot_size += self.big_blind
                # Record action in table state
                self.table_state.record_action(0, Action.CALL, self.big_blind)
                # Log action for display
                self.logger.log_action("Button", "calls", self.big_blind)
        else:
            # Post-flop opponent actions
            if random.random() < 0.3:  # 30% chance to bet
                bet_size = self.table_state.pot_size * 0.5  # Half pot bet
                self.table_state.players[0].stack -= bet_size
                self.table_state.pot_size += bet_size
                self.table_state.current_bet = bet_size
                # Record action in table state
                self.table_state.record_action(0, Action.RAISE, bet_size)
                # Log action for display
                self.logger.log_action("Opponent", "bets", bet_size)
            else:
                # Record action in table state
                self.table_state.record_action(0, Action.CHECK)
                # Log action for display
                self.logger.log_action("Opponent", "checks")

        # Start decision tracking
        decision_node = self.decision_explainer.start_decision(
            f"{street.name} Decision",
            f"Making a decision on {street.name} with {self.table_state.hero_cards}"
        )

        # Get bot's action
        start_time = time.time()
        action, bet_size = self.bot.make_decision()
        execution_time = time.time() - start_time

        # End decision tracking
        decision_data = self.decision_explainer.end_decision((action, bet_size))

        # Log decision data
        if self.logger.debug_level >= DebugLevel.DEBUG:
            self.logger.log_decision(decision_data)

            # Update verbosity symbols
            self.verbosity_symbols.update_table_state(
                current_street=street,
                hero_cards=self.table_state.hero_cards,
                community_cards=self.table_state.community_cards
            )

            # Log detailed explanation
            hand_data = {
                'street': street,
                'hero_cards': self.table_state.hero_cards,
                'community_cards': self.table_state.community_cards,
                'position': self.table_state.players[self.table_state.hero_seat].position,
                'pot_size': self.table_state.pot_size,
                'decision': (action, bet_size),
                'decision_explanation': self.decision_explainer.explain_decision(decision_data)
            }

            explanation = self.decision_explainer.explain_hand_decision(hand_data)
            self.logger.debug(f"Decision explanation:\n{explanation}", DebugLevel.DEBUG)

        # Log and process bot's action
        if action == Action.FOLD:
            # Record action in table state
            self.table_state.record_action(self.table_state.hero_seat, Action.FOLD)
            # Log action for display
            self.logger.log_action("Bot", "folds")
            return False
        elif action == Action.CHECK:
            # Record action in table state
            self.table_state.record_action(self.table_state.hero_seat, Action.CHECK)
            # Log action for display
            self.logger.log_action("Bot", "checks")
        elif action == Action.CALL:
            # Record action in table state
            self.table_state.record_action(self.table_state.hero_seat, Action.CALL, bet_size)
            # Log action for display
            self.logger.log_action("Bot", "calls", bet_size)
            self.table_state.players[self.table_state.hero_seat].stack -= bet_size
            self.table_state.pot_size += bet_size
            self.table_state.hero_stack = self.table_state.players[self.table_state.hero_seat].stack
        elif action == Action.RAISE:
            # Record action in table state
            self.table_state.record_action(self.table_state.hero_seat, Action.RAISE, bet_size)
            # Log action for display
            self.logger.log_action("Bot", "raises", bet_size)
            self.table_state.players[self.table_state.hero_seat].stack -= bet_size
            self.table_state.pot_size += bet_size
            self.table_state.hero_stack = self.table_state.players[self.table_state.hero_seat].stack
        elif action == Action.ALL_IN:
            # Record action in table state
            self.table_state.record_action(self.table_state.hero_seat, Action.ALL_IN, bet_size)
            # Log action for display
            self.logger.log_action("Bot", "goes all-in", bet_size)
            self.table_state.players[self.table_state.hero_seat].stack -= bet_size
            self.table_state.pot_size += bet_size
            self.table_state.hero_stack = self.table_state.players[self.table_state.hero_seat].stack

        # Log updated pot size
        self.logger.log_pot_update(self.table_state.pot_size)

        return True

    def _show_results(self):
        """Show hand results"""
        self.logger.info("=== Hand Complete ===")
        self.logger.info(f"Final pot: {self.table_state.pot_size}")
        self.logger.info(f"Your final stack: {self.table_state.players[self.table_state.hero_seat].stack}")

def main():
    """Main game loop"""
    runner = GameRunner()
    logger = runner.logger

    logger.info("=== Starting GeckoBot Poker Game ===")

    for i in range(5):
        logger.start_round(i+1)
        runner.setup_game()
        runner.run_hand()

    logger.info("=== Game Complete ===")
    logger.info("Thanks for playing!")

    # Save session data for analysis
    logger.save_session_data()

if __name__ == "__main__":
    main()