from typing import Optional, Tuple, Dict, List
from poker_enums import Action, HandStrength, Position, Street
from table_state import TableState, Player
from hand_evaluator import HandEvaluator
from board_analyzer import BoardAnalyzer
from position_manager import PositionManager
import random

class GeckoBot:
    def __init__(self, table_state: TableState):
        self.table_state = table_state
        self.position_manager = PositionManager()
        self.hand_evaluator = HandEvaluator()
        self.board_analyzer = BoardAnalyzer()

        # We'll keep the action_history for backward compatibility,
        # but we'll primarily use the betting_symbols for decision making
        self.action_history = {
            Street.PREFLOP: [],
            Street.FLOP: [],
            Street.TURN: [],
            Street.RIVER: []
        }

    def make_decision(self) -> Tuple[Action, float]:
        """Main decision point - routes to appropriate street logic"""
        if self.table_state.current_street == Street.PREFLOP:
            return self._make_preflop_decision()
        elif self.table_state.current_street == Street.FLOP:
            return self._make_flop_decision()
        elif self.table_state.current_street == Street.TURN:
            return self._make_turn_decision()
        else:
            return self._make_river_decision()

    def _make_preflop_decision(self) -> Tuple[Action, float]:
        """Preflop decision logic matching OpenPPL"""
        hand_strength = self.hand_evaluator.evaluate_hand_strength(
            self.table_state.hero_cards,
            []  # Empty board for preflop
        )

        hero_pos = self.table_state.get_hero_position()
        hand = self._get_hand_string()

        # Get betting action symbols and history symbols
        betting_symbols = self.table_state.betting_symbols
        history_symbols = self.table_state.history_symbols

        # Check for 3-bet and 4-bet situations
        is_three_bet = betting_symbols.is_three_bet()
        is_four_bet = betting_symbols.is_four_bet()
        raises_since_last_play = betting_symbols.raises_since_last_play(Street.PREFLOP)

        # Get history information
        num_raises_preflop = history_symbols.get_number_of_raises_before_flop()
        bots_last_action = history_symbols.get_bots_last_preflop_action()
        opponents_last_action = history_symbols.get_opponents_last_action()

        # Get SPR category
        spr_category = self.table_state.get_spr_category()
        is_short_stacked = self.table_state.is_short_stacked()
        is_deep_stacked = self.table_state.is_deep_stacked()

        # Premium hands
        if hand_strength in [HandStrength.OVERPAIR_STRONG]:
            if self._facing_raise():
                if self._multiple_raisers():
                    # Adjust based on stack depth
                    if is_short_stacked:
                        return self._raise_decision(1.0)  # All-in or close to it
                    elif spr_category in ['very_low', 'low']:
                        return self._raise_decision(4.5)  # More aggressive with low SPR
                    else:
                        return self._raise_decision(4)  # 4x reraise vs multiple
                # Single raiser
                if is_short_stacked:
                    return self._raise_decision(1.0)  # All-in or close to it
                elif spr_category in ['very_low', 'low']:
                    return self._raise_decision(3.5)  # More aggressive with low SPR
                else:
                    return self._raise_decision(3)  # 3x reraise vs single
            # Opening
            if is_short_stacked:
                return self._raise_decision(1.0)  # All-in or close to it
            elif is_deep_stacked:
                return self._raise_decision(2.0)  # More conservative with deep stacks
            else:
                return self._raise_decision(2.5)  # 2.5x open

        # Strong hands
        if hand_strength in [HandStrength.OVERPAIR_WEAK, HandStrength.TOP_PAIR_GOOD_KICKER]:
            if self._facing_raise():
                if self._multiple_raisers():
                    if self._getting_good_odds():
                        return (Action.CALL, self.table_state.current_bet)
                    return (Action.FOLD, 0.0)
                return self._raise_decision(3)
            return self._raise_decision(2.5)

        # Medium hands
        if hand_strength in [HandStrength.TOP_PAIR_WEAK_KICKER, HandStrength.MIDDLE_PAIR_GOOD_KICKER]:
            if self._facing_raise():
                if self._getting_good_odds() and not self._multiple_raisers():
                    return (Action.CALL, self.table_state.current_bet)
                return (Action.FOLD, 0.0)
            if self.table_state.is_late_position() or self.table_state.is_last_to_act():
                return self._raise_decision(2.5)
            if self.table_state.is_middle_position() and not self.table_state.is_first_to_act():
                return (Action.CALL, self.table_state.current_bet)
            return (Action.FOLD, 0.0)

        # Speculative hands
        if hand_strength.is_draw:
            if self._facing_raise():
                if (self._getting_good_odds() and
                    self._good_implied_odds() and
                    not self._multiple_raisers()):
                    return (Action.CALL, self.table_state.current_bet)
                return (Action.FOLD, 0.0)
            if self.table_state.is_late_position() or self.table_state.is_last_to_act():
                return self._raise_decision(2.5)
            if self.table_state.is_middle_position() and self.table_state.is_in_position_vs_callers():
                return (Action.CALL, self.table_state.current_bet)
            return (Action.FOLD, 0.0)

        return (Action.FOLD, 0.0)

    def _make_flop_decision(self) -> Tuple[Action, float]:
        """Flop decision logic matching OpenPPL"""
        hand_strength = self.hand_evaluator.evaluate_hand_strength(
            self.table_state.hero_cards,
            self.table_state.community_cards
        )

        board_texture = self.board_analyzer.analyze_board(self.table_state.community_cards)

        # Get history symbols
        history_symbols = self.table_state.history_symbols

        # Get history information
        bots_last_preflop_action = history_symbols.get_bots_last_preflop_action()
        bots_last_flop_action = history_symbols.get_bots_last_flop_action()
        num_raises_preflop = history_symbols.get_number_of_raises_before_flop()
        num_raises_flop = history_symbols.get_number_of_raises_on_flop()

        # Get SPR information
        spr_category = self.table_state.get_spr_category()
        is_short_stacked = self.table_state.is_short_stacked()
        is_deep_stacked = self.table_state.is_deep_stacked()
        is_committed = self.table_state.is_committed(self.table_state.pot_size * 0.5)  # Check if committed with half pot bet

        # First to act
        if not self._facing_bet():
            # Strong hands always bet
            if hand_strength.is_strong_made_hand:
                # Calculate optimal bet size based on SPR and hand strength
                optimal_bet_size = self.table_state.calculate_optimal_bet_size(0.8)  # Strong hand = 0.8 strength

                # If we're committed, be more aggressive
                if is_committed:
                    return self._raise_decision(optimal_bet_size * 1.2)  # 20% larger than optimal

                # If we're short stacked, be more aggressive
                if is_short_stacked:
                    return self._raise_decision(1.0)  # Pot-sized bet

                # Adjust bet size based on board texture
                if board_texture['texture'] == 'DRY':
                    return self._raise_decision(optimal_bet_size * 0.8)  # Smaller bet on dry boards
                else:
                    return self._raise_decision(optimal_bet_size * 1.1)  # Larger bet on wet boards

            # Medium hands bet in position or on dry boards
            if hand_strength.is_medium_made_hand:
                # Calculate optimal bet size based on SPR and hand strength
                optimal_bet_size = self.table_state.calculate_optimal_bet_size(0.6)  # Medium hand = 0.6 strength

                # If we're deep stacked, be more conservative
                if is_deep_stacked:
                    optimal_bet_size *= 0.8  # 20% smaller than optimal

                # If we're in position or the board is dry, bet
                if (self.table_state.is_late_position() or
                    self.table_state.is_last_to_act() or
                    board_texture['texture'] == 'DRY'):
                    return self._raise_decision(optimal_bet_size)

                # Otherwise, check
                return (Action.CHECK, 0.0)

            # Strong draws bet on wet boards in position
            if hand_strength.is_strong_draw:
                if ((self.table_state.is_late_position() or self.table_state.is_last_to_act()) and
                    board_texture['texture'] != 'DRY'):
                    return self._raise_decision(0.5)
                if self.table_state.is_in_position_vs_aggressor() and self.table_state.is_in_position_vs_callers():
                    return self._raise_decision(0.5)
                return (Action.CHECK, 0.0)

            return (Action.CHECK, 0.0)

        # Facing a bet
        if self._facing_donk_bet():
            if hand_strength.is_strong_made_hand:
                return self._raise_decision(3)  # Punish donk bets
            if hand_strength.is_medium_made_hand:
                if board_texture['texture'] == 'DRY':
                    return (Action.CALL, self.table_state.current_bet)
                if self._in_position():
                    return self._raise_decision(2.5)
                return (Action.CALL, self.table_state.current_bet)
            if hand_strength.is_strong_draw and self._getting_odds():
                return (Action.CALL, self.table_state.current_bet)
            return (Action.FOLD, 0.0)

        if self._facing_cbet():
            # Defend wider vs c-bets
            if hand_strength.is_strong_made_hand:
                if board_texture['texture'] == 'DRY':
                    return self._raise_decision(2.5)
                return self._raise_decision(3)
            if hand_strength.is_medium_made_hand:
                if board_texture['texture'] == 'DRY':
                    return (Action.CALL, self.table_state.current_bet)
                if self._in_position():
                    return self._raise_decision(2.5)
                return (Action.CALL, self.table_state.current_bet)
            if (hand_strength.is_strong_draw or
                (hand_strength.is_medium_draw and self._in_position())):
                if self._getting_odds():
                    if board_texture['texture'] != 'DRY':
                        return self._raise_decision(2.5)
                    return (Action.CALL, self.table_state.current_bet)
            return (Action.FOLD, 0.0)

        return (Action.FOLD, 0.0)

    def _make_turn_decision(self) -> Tuple[Action, float]:
        """Turn decision logic matching OpenPPL"""
        hand_strength = self.hand_evaluator.evaluate_hand_strength(
            self.table_state.hero_cards,
            self.table_state.community_cards
        )

        board_texture = self.board_analyzer.analyze_board(self.table_state.community_cards)

        # Get history symbols
        history_symbols = self.table_state.history_symbols

        # Get history information
        bots_last_flop_action = history_symbols.get_bots_last_flop_action()
        bots_last_turn_action = history_symbols.get_bots_last_turn_action()
        num_raises_flop = history_symbols.get_number_of_raises_on_flop()
        num_raises_turn = history_symbols.get_number_of_raises_on_turn()

        # First to act
        if not self._facing_bet():
            if hand_strength.is_strong_made_hand:
                if board_texture['texture'] == 'DRY':
                    return self._raise_decision(0.66)  # 2/3 pot on dry boards
                return self._raise_decision(0.75)  # 3/4 pot on wet boards

            if hand_strength.is_medium_made_hand and self._in_position():
                if board_texture['texture'] == 'DRY':
                    return self._raise_decision(0.5)
                return (Action.CHECK, 0.0)

            if hand_strength.is_strong_draw and self._in_position():
                if board_texture['texture'] != 'DRY':
                    return self._raise_decision(0.5)
                return (Action.CHECK, 0.0)

            return (Action.CHECK, 0.0)

        # Facing a bet
        if hand_strength.is_strong_made_hand:
            if board_texture['texture'] == 'DRY':
                return self._raise_decision(2.5)
            return self._raise_decision(3)

        if hand_strength.is_medium_made_hand:
            if board_texture['texture'] == 'DRY':
                return (Action.CALL, self.table_state.current_bet)
            if self._in_position():
                return self._raise_decision(2.5)
            return (Action.CALL, self.table_state.current_bet)

        if hand_strength.is_strong_draw:
            if self._getting_odds():
                if board_texture['texture'] != 'DRY':
                    return self._raise_decision(2.5)
                return (Action.CALL, self.table_state.current_bet)

        return (Action.FOLD, 0.0)

    def _make_river_decision(self) -> Tuple[Action, float]:
        """River decision logic matching OpenPPL"""
        hand_strength = self.hand_evaluator.evaluate_hand_strength(
            self.table_state.hero_cards,
            self.table_state.community_cards
        )

        board_texture = self.board_analyzer.analyze_board(self.table_state.community_cards)

        # Get history symbols
        history_symbols = self.table_state.history_symbols

        # Get history information
        bots_last_turn_action = history_symbols.get_bots_last_turn_action()
        bots_last_river_action = history_symbols.get_bots_last_river_action()
        num_raises_turn = history_symbols.get_number_of_raises_on_turn()
        num_raises_river = history_symbols.get_number_of_raises_on_river()

        # First to act
        if not self._facing_bet():
            if hand_strength.value >= HandStrength.TWO_PAIR_TOP.value:
                if board_texture['texture'] == 'DRY':
                    return self._raise_decision(0.75)
                return self._raise_decision(1.0)  # Pot-sized bet

            if hand_strength.value >= HandStrength.TOP_PAIR_GOOD_KICKER.value:
                if board_texture['texture'] == 'DRY' and self._in_position():
                    return self._raise_decision(0.5)
                return (Action.CHECK, 0.0)

            return (Action.CHECK, 0.0)

        # Facing a bet
        if hand_strength.value >= HandStrength.SET.value:
            if board_texture['texture'] == 'DRY':
                return self._raise_decision(2.5)
            return self._raise_decision(3)

        if hand_strength.value >= HandStrength.TWO_PAIR_TOP_AND_MIDDLE.value:
            if board_texture['texture'] == 'DRY':
                return (Action.CALL, self.table_state.current_bet)
            if self._in_position():
                return self._raise_decision(2.5)
            return (Action.CALL, self.table_state.current_bet)

        if (hand_strength.value >= HandStrength.TOP_PAIR_GOOD_KICKER.value and
            board_texture['texture'] == 'DRY' and
            self._getting_good_odds()):
            return (Action.CALL, self.table_state.current_bet)

        return (Action.FOLD, 0.0)

    # Helper methods
    def _getting_odds(self) -> bool:
        """Check if we're getting the right pot odds"""
        pot_odds = self.table_state.get_pot_odds(self.table_state.current_bet)

        # Calculate equity from outs
        equity_from_outs = self.table_state.get_equity_from_outs()

        # If we have a good draw, compare pot odds to equity from outs
        if self._have_good_draw():
            return pot_odds <= equity_from_outs or pot_odds >= 0.2  # Need 20% equity for draws

        return pot_odds >= 0.3  # Need 30% equity for calls

    def _getting_good_odds(self) -> bool:
        """Check if we're getting good pot odds"""
        pot_odds = self.table_state.get_pot_odds(self.table_state.current_bet)

        # Calculate equity from outs
        equity_from_outs = self.table_state.get_equity_from_outs()

        # Compare pot odds to equity from outs
        return pot_odds <= equity_from_outs or pot_odds >= 0.25  # Need 25% equity for good odds

    def _in_position(self) -> bool:
        """Check if we're in position"""
        pos = self.table_state.get_hero_position()
        if self.table_state.total_players == 3:
            # In 3-handed play, SB is in position against BB and Button
            return pos in [Position.BUTTON, Position.SMALL_BLIND]
        # In 6-max or full ring, Button and CO are in position
        return pos in [Position.BUTTON, Position.CO]

    def _facing_action(self) -> bool:
        """Check if facing any action"""
        return self.table_state.current_bet > 0

    def _facing_raise(self) -> bool:
        """Check if facing a raise"""
        # Use betting action symbols to check if there are any raises on the current street
        return self.table_state.betting_symbols.raises_since_last_play(self.table_state.current_street) > 0

    def _facing_bet(self) -> bool:
        """Check if facing a bet"""
        return self.table_state.current_bet > 0

    def _facing_donk_bet(self) -> bool:
        """Check if facing a donk bet"""
        if not self._facing_bet():
            return False
        # Use betting action symbols to check if we're facing a donk bet
        return self.table_state.betting_symbols.is_donk_bet()

    def _facing_cbet(self) -> bool:
        """Check if facing a continuation bet"""
        if not self._facing_bet():
            return False
        # Use betting action symbols to check if we're facing a continuation bet
        return self.table_state.betting_symbols.is_continuation_bet()

    def _multiple_raisers(self) -> bool:
        """Check if there are multiple preflop raisers"""
        # Use betting action symbols to check if there are multiple raises on the current street
        street = self.table_state.current_street
        # Count raises on the current street
        raise_count = 0
        for action_data in self.table_state.betting_symbols.actions_by_street[street]:
            if action_data['action'] == Action.RAISE:
                raise_count += 1
        return raise_count >= 2

    def _good_implied_odds(self) -> bool:
        """Check if we have good implied odds"""
        effective_stack = min(p.stack for p in self.table_state.players.values() if p.in_hand)
        return effective_stack >= 15 * self.table_state.current_bet

    def _have_good_draw(self) -> bool:
        """Check if we have a good drawing hand"""
        # First check using hand strength
        hand_strength = self.hand_evaluator.evaluate_hand_strength(
            self.table_state.hero_cards,
            self.table_state.community_cards
        )

        # Then check using outs calculator
        equity_from_outs = self.table_state.get_equity_from_outs()

        # Consider it a good draw if either condition is met
        return (hand_strength.is_strong_draw or
                hand_strength.is_medium_draw or
                equity_from_outs >= 0.25)  # 25% equity from outs is a good draw

    def _get_hand_string(self) -> str:
        """Convert hole cards to standard notation"""
        if not self.table_state.hero_cards[0] or not self.table_state.hero_cards[1]:
            return ""

        card1, card2 = self.table_state.hero_cards
        rank1, rank2 = card1[0], card2[0]
        suited = card1[1] == card2[1]

        if rank1 == rank2:
            return rank1 + rank2
        else:
            ranks = sorted([rank1, rank2], reverse=True)
            return ranks[0] + ranks[1] + ('s' if suited else 'o')

    def _raise_decision(self, multiplier: float) -> Tuple[Action, float]:
        """Calculate raise size based on pot, current bet, and SPR"""
        min_raise = self.table_state.min_raise
        pot_size = self.table_state.pot_size

        # Get SPR category and adjust multiplier if needed
        spr_category = self.table_state.get_spr_category()

        # Adjust multiplier based on SPR category
        if spr_category == 'very_low':
            # More aggressive with very low SPR
            multiplier = min(multiplier * 1.5, 1.0)  # Cap at pot-sized bet
        elif spr_category == 'low':
            # Slightly more aggressive with low SPR
            multiplier = min(multiplier * 1.2, 0.75)  # Cap at 3/4 pot
        elif spr_category == 'high':
            # More conservative with high SPR
            multiplier = multiplier * 0.8
        elif spr_category == 'very_high':
            # Very conservative with very high SPR
            multiplier = multiplier * 0.6

        # Calculate the raise size
        raise_size = max(
            min_raise,
            min(
                pot_size * multiplier,
                self.table_state.get_effective_stack()
            )
        )

        return (Action.RAISE, raise_size)

    def _bot_called_before_flop(self) -> bool:
        """Check if we called preflop"""
        return Action.CALL in self.action_history[Street.PREFLOP]

    def _bot_checked_preflop(self) -> bool:
        """Check if we checked preflop"""
        return Action.CHECK in self.action_history[Street.PREFLOP]

    def _bot_raised_before_flop(self) -> bool:
        """Check if we raised preflop"""
        return Action.RAISE in self.action_history[Street.PREFLOP]

    def _bot_actions_on_street(self, street: Street) -> int:
        """Count number of actions we've made on this street"""
        return len(self.action_history[street])

    def _bot_is_last_raiser(self) -> bool:
        """Check if we were the last player to raise"""
        return (self.last_action == Action.RAISE and
                all(p.last_action != Action.RAISE
                    for p in self.table_state.players.values()
                    if p.seat != self.table_state.hero_seat))

    def _bot_is_aggressor(self) -> bool:
        """Check if we're the aggressor on this street"""
        return any(action == Action.RAISE
                  for action in self.action_history[self.table_state.current_street])

    def _facing_float_bet(self) -> bool:
        """Check if facing a float bet (opponent bets after calling previous street)"""
        if self.table_state.current_street == Street.PREFLOP:
            return False

        # Get the players who called last street
        callers = [p for p in self.table_state.players.values()
                  if p.previous_action == Action.CALL]

        # Check if any of them are betting now
        return any(p.last_action == Action.RAISE for p in callers)

    def _facing_cbet(self) -> bool:
        """Check if facing a continuation bet"""
        if self.table_state.current_street == Street.PREFLOP:
            return False

        # Use betting action symbols to check if we're facing a continuation bet
        return self.table_state.betting_symbols.is_continuation_bet()

    def _get_preflop_raisers(self) -> List[Player]:
        """Get a list of players who raised preflop"""
        # Use history symbols to check for preflop raises
        preflop_history = self.table_state.history_symbols.get_preflop_action_history()
        preflop_raisers = []

        # Find players who raised preflop
        for action_data in preflop_history:
            if action_data['action'] == Action.RAISE:
                player_name = action_data['player']
                # Find the player in the table state
                for seat, player in self.table_state.players.items():
                    if (player_name == "Bot" and seat == self.table_state.hero_seat) or \
                       (player_name == f"Player_{seat}"):
                        preflop_raisers.append(player)
                        break

        return preflop_raisers

    def _get_preflop_callers(self) -> List[Player]:
        """Get a list of players who called preflop"""
        # Use history symbols to check for preflop calls
        preflop_history = self.table_state.history_symbols.get_preflop_action_history()
        preflop_callers = []

        # Find players who called preflop
        for action_data in preflop_history:
            if action_data['action'] == Action.CALL:
                player_name = action_data['player']
                # Find the player in the table state
                for seat, player in self.table_state.players.items():
                    if (player_name == "Bot" and seat == self.table_state.hero_seat) or \
                       (player_name == f"Player_{seat}"):
                        preflop_callers.append(player)
                        break

        return preflop_callers

    def _get_preflop_folders(self) -> List[Player]:
        """Get a list of players who folded preflop"""
        # Use history symbols to check for preflop folds
        preflop_history = self.table_state.history_symbols.get_preflop_action_history()
        preflop_folders = []

        # Find players who folded preflop
        for action_data in preflop_history:
            if action_data['action'] == Action.FOLD:
                player_name = action_data['player']
                # Find the player in the table state
                for seat, player in self.table_state.players.items():
                    if (player_name == "Bot" and seat == self.table_state.hero_seat) or \
                       (player_name == f"Player_{seat}"):
                        preflop_folders.append(player)
                        break

        return preflop_folders

    def _get_preflop_checkers(self) -> List[Player]:
        """Get a list of players who checked preflop"""
        # Use history symbols to check for preflop checks
        preflop_history = self.table_state.history_symbols.get_preflop_action_history()
        preflop_checkers = []

        # Find players who checked preflop
        for action_data in preflop_history:
            if action_data['action'] == Action.CHECK:
                player_name = action_data['player']
                # Find the player in the table state
                for seat, player in self.table_state.players.items():
                    if (player_name == "Bot" and seat == self.table_state.hero_seat) or \
                       (player_name == f"Player_{seat}"):
                        preflop_checkers.append(player)
                        break

        return preflop_checkers

    def _get_preflop_all_in_players(self) -> List[Player]:
        """Get a list of players who went all-in preflop"""
        # Use history symbols to check for preflop all-ins
        preflop_history = self.table_state.history_symbols.get_preflop_action_history()
        preflop_all_in_players = []

        # Find players who went all-in preflop
        for action_data in preflop_history:
            if action_data['action'] == Action.ALL_IN:
                player_name = action_data['player']
                # Find the player in the table state
                for seat, player in self.table_state.players.items():
                    if (player_name == "Bot" and seat == self.table_state.hero_seat) or \
                       (player_name == f"Player_{seat}"):
                        preflop_all_in_players.append(player)
                        break

        return preflop_all_in_players

    def _get_preflop_active_players(self) -> List[Player]:
        """Get a list of players who are still in the hand preflop"""
        # Get all players who are still in the hand
        active_players = []
        for seat, player in self.table_state.players.items():
            if player.in_hand:
                active_players.append(player)
        return active_players

    def _get_preflop_aggressors(self) -> List[Player]:
        """Get a list of players who raised or went all-in preflop"""
        # Combine the lists of preflop raisers and all-in players
        preflop_raisers = self._get_preflop_raisers()
        preflop_all_in_players = self._get_preflop_all_in_players()

        # Combine the lists, avoiding duplicates
        preflop_aggressors = list(set(preflop_raisers + preflop_all_in_players))

        return preflop_aggressors

    def _get_preflop_passive_players(self) -> List[Player]:
        """Get a list of players who called or checked preflop"""
        # Combine the lists of preflop callers and checkers
        preflop_callers = self._get_preflop_callers()
        preflop_checkers = self._get_preflop_checkers()

        # Combine the lists, avoiding duplicates
        preflop_passive_players = list(set(preflop_callers + preflop_checkers))

        return preflop_passive_players

    def _get_preflop_3betters(self) -> List[Player]:
        """Get a list of players who 3-bet preflop"""
        # Use betting action symbols to check for 3-bet situations
        if not self.table_state.betting_symbols.is_three_bet():
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 3-bet situation, the last raiser is the 3-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_4betters(self) -> List[Player]:
        """Get a list of players who 4-bet preflop"""
        # Use betting action symbols to check for 4-bet situations
        if not self.table_state.betting_symbols.is_four_bet():
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 4-bet situation, the last raiser is the 4-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_5betters(self) -> List[Player]:
        """Get a list of players who 5-bet preflop"""
        # Check if there are at least 5 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 4:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 5-bet situation, the last raiser is the 5-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_6betters(self) -> List[Player]:
        """Get a list of players who 6-bet preflop"""
        # Check if there are at least 6 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 5:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 6-bet situation, the last raiser is the 6-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_7betters(self) -> List[Player]:
        """Get a list of players who 7-bet preflop"""
        # Check if there are at least 7 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 6:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 7-bet situation, the last raiser is the 7-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_8betters(self) -> List[Player]:
        """Get a list of players who 8-bet preflop"""
        # Check if there are at least 8 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 7:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 8-bet situation, the last raiser is the 8-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_9betters(self) -> List[Player]:
        """Get a list of players who 9-bet preflop"""
        # Check if there are at least 9 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 8:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 9-bet situation, the last raiser is the 9-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_10betters(self) -> List[Player]:
        """Get a list of players who 10-bet preflop"""
        # Check if there are at least 10 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 9:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 10-bet situation, the last raiser is the 10-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_11betters(self) -> List[Player]:
        """Get a list of players who 11-bet preflop"""
        # Check if there are at least 11 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 10:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 11-bet situation, the last raiser is the 11-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_12betters(self) -> List[Player]:
        """Get a list of players who 12-bet preflop"""
        # Check if there are at least 12 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 11:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 12-bet situation, the last raiser is the 12-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_13betters(self) -> List[Player]:
        """Get a list of players who 13-bet preflop"""
        # Check if there are at least 13 raises preflop
        if self.table_state.history_symbols.get_number_of_raises_before_flop() < 12:
            return []

        # Get preflop raisers
        preflop_raisers = self._get_preflop_raisers()

        # In a 13-bet situation, the last raiser is the 13-better
        if preflop_raisers and self.table_state.last_aggressor is not None:
            for seat, player in self.table_state.players.items():
                if seat == self.table_state.last_aggressor and player in preflop_raisers:
                    return [player]

        return []

    def _get_preflop_14betters(self) -> List[Player]:
        """Get a list of players who 14-bet preflop"""
        preflop_14betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 13:
                preflop_14betters.append(player)
        return preflop_14betters

    def _get_preflop_15betters(self) -> List[Player]:
        """Get a list of players who 15-bet preflop"""
        preflop_15betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 14:
                preflop_15betters.append(player)
        return preflop_15betters

    def _get_preflop_16betters(self) -> List[Player]:
        """Get a list of players who 16-bet preflop"""
        preflop_16betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 15:
                preflop_16betters.append(player)
        return preflop_16betters

    def _get_preflop_17betters(self) -> List[Player]:
        """Get a list of players who 17-bet preflop"""
        preflop_17betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 16:
                preflop_17betters.append(player)
        return preflop_17betters

    def _get_preflop_18betters(self) -> List[Player]:
        """Get a list of players who 18-bet preflop"""
        preflop_18betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 17:
                preflop_18betters.append(player)
        return preflop_18betters

    def _get_preflop_19betters(self) -> List[Player]:
        """Get a list of players who 19-bet preflop"""
        preflop_19betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 18:
                preflop_19betters.append(player)
        return preflop_19betters

    def _get_preflop_20betters(self) -> List[Player]:
        """Get a list of players who 20-bet preflop"""
        preflop_20betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 19:
                preflop_20betters.append(player)
        return preflop_20betters

    def _get_preflop_21betters(self) -> List[Player]:
        """Get a list of players who 21-bet preflop"""
        preflop_21betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 20:
                preflop_21betters.append(player)
        return preflop_21betters

    def _get_preflop_22betters(self) -> List[Player]:
        """Get a list of players who 22-bet preflop"""
        preflop_22betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 21:
                preflop_22betters.append(player)
        return preflop_22betters

    def _get_preflop_23betters(self) -> List[Player]:
        """Get a list of players who 23-bet preflop"""
        preflop_23betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 22:
                preflop_23betters.append(player)
        return preflop_23betters

    def _get_preflop_24betters(self) -> List[Player]:
        """Get a list of players who 24-bet preflop"""
        preflop_24betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 23:
                preflop_24betters.append(player)
        return preflop_24betters

    def _get_preflop_25betters(self) -> List[Player]:
        """Get a list of players who 25-bet preflop"""
        preflop_25betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 24:
                preflop_25betters.append(player)
        return preflop_25betters

    def _get_preflop_26betters(self) -> List[Player]:
        """Get a list of players who 26-bet preflop"""
        preflop_26betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 25:
                preflop_26betters.append(player)
        return preflop_26betters

    def _get_preflop_27betters(self) -> List[Player]:
        """Get a list of players who 27-bet preflop"""
        preflop_27betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 26:
                preflop_27betters.append(player)
        return preflop_27betters

    def _get_preflop_28betters(self) -> List[Player]:
        """Get a list of players who 28-bet preflop"""
        preflop_28betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 27:
                preflop_28betters.append(player)
        return preflop_28betters

    def _get_preflop_29betters(self) -> List[Player]:
        """Get a list of players who 29-bet preflop"""
        preflop_29betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 28:
                preflop_29betters.append(player)
        return preflop_29betters

    def _get_preflop_30betters(self) -> List[Player]:
        """Get a list of players who 30-bet preflop"""
        preflop_30betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 29:
                preflop_30betters.append(player)
        return preflop_30betters

    def _get_preflop_31betters(self) -> List[Player]:
        """Get a list of players who 31-bet preflop"""
        preflop_31betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 30:
                preflop_31betters.append(player)
        return preflop_31betters

    def _get_preflop_32betters(self) -> List[Player]:
        """Get a list of players who 32-bet preflop"""
        preflop_32betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 31:
                preflop_32betters.append(player)
        return preflop_32betters

    def _get_preflop_33betters(self) -> List[Player]:
        """Get a list of players who 33-bet preflop"""
        preflop_33betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 32:
                preflop_33betters.append(player)
        return preflop_33betters

    def _get_preflop_34betters(self) -> List[Player]:
        """Get a list of players who 34-bet preflop"""
        preflop_34betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 33:
                preflop_34betters.append(player)
        return preflop_34betters

    def _get_preflop_35betters(self) -> List[Player]:
        """Get a list of players who 35-bet preflop"""
        preflop_35betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 34:
                preflop_35betters.append(player)
        return preflop_35betters

    def _get_preflop_36betters(self) -> List[Player]:
        """Get a list of players who 36-bet preflop"""
        preflop_36betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 35:
                preflop_36betters.append(player)
        return preflop_36betters

    def _get_preflop_37betters(self) -> List[Player]:
        """Get a list of players who 37-bet preflop"""
        preflop_37betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 36:
                preflop_37betters.append(player)
        return preflop_37betters

    def _get_preflop_38betters(self) -> List[Player]:
        """Get a list of players who 38-bet preflop"""
        preflop_38betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 37:
                preflop_38betters.append(player)
        return preflop_38betters

    def _get_preflop_39betters(self) -> List[Player]:
        """Get a list of players who 39-bet preflop"""
        preflop_39betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 38:
                preflop_39betters.append(player)
        return preflop_39betters

    def _get_preflop_40betters(self) -> List[Player]:
        """Get a list of players who 40-bet preflop"""
        preflop_40betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 39:
                preflop_40betters.append(player)
        return preflop_40betters

    def _get_preflop_41betters(self) -> List[Player]:
        """Get a list of players who 41-bet preflop"""
        preflop_41betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 40:
                preflop_41betters.append(player)
        return preflop_41betters

    def _get_preflop_42betters(self) -> List[Player]:
        """Get a list of players who 42-bet preflop"""
        preflop_42betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 41:
                preflop_42betters.append(player)
        return preflop_42betters

    def _get_preflop_43betters(self) -> List[Player]:
        """Get a list of players who 43-bet preflop"""
        preflop_43betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 42:
                preflop_43betters.append(player)
        return preflop_43betters

    def _get_preflop_44betters(self) -> List[Player]:
        """Get a list of players who 44-bet preflop"""
        preflop_44betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 43:
                preflop_44betters.append(player)
        return preflop_44betters

    def _get_preflop_45betters(self) -> List[Player]:
        """Get a list of players who 45-bet preflop"""
        preflop_45betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 44:
                preflop_45betters.append(player)
        return preflop_45betters

    def _get_preflop_46betters(self) -> List[Player]:
        """Get a list of players who 46-bet preflop"""
        preflop_46betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 45:
                preflop_46betters.append(player)
        return preflop_46betters

    def _get_preflop_47betters(self) -> List[Player]:
        """Get a list of players who 47-bet preflop"""
        preflop_47betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 46:
                preflop_47betters.append(player)
        return preflop_47betters

    def _get_preflop_48betters(self) -> List[Player]:
        """Get a list of players who 48-bet preflop"""
        preflop_48betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 47:
                preflop_48betters.append(player)
        return preflop_48betters

    def _get_preflop_49betters(self) -> List[Player]:
        """Get a list of players who 49-bet preflop"""
        preflop_49betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 48:
                preflop_49betters.append(player)
        return preflop_49betters

    def _get_preflop_50betters(self) -> List[Player]:
        """Get a list of players who 50-bet preflop"""
        preflop_50betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 49:
                preflop_50betters.append(player)
        return preflop_50betters

    def _get_preflop_51betters(self) -> List[Player]:
        """Get a list of players who 51-bet preflop"""
        preflop_51betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 50:
                preflop_51betters.append(player)
        return preflop_51betters

    def _get_preflop_52betters(self) -> List[Player]:
        """Get a list of players who 52-bet preflop"""
        preflop_52betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 51:
                preflop_52betters.append(player)
        return preflop_52betters

    def _get_preflop_53betters(self) -> List[Player]:
        """Get a list of players who 53-bet preflop"""
        preflop_53betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 52:
                preflop_53betters.append(player)
        return preflop_53betters

    def _get_preflop_54betters(self) -> List[Player]:
        """Get a list of players who 54-bet preflop"""
        preflop_54betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 53:
                preflop_54betters.append(player)
        return preflop_54betters

    def _get_preflop_55betters(self) -> List[Player]:
        """Get a list of players who 55-bet preflop"""
        preflop_55betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 54:
                preflop_55betters.append(player)
        return preflop_55betters

    def _get_preflop_56betters(self) -> List[Player]:
        """Get a list of players who 56-bet preflop"""
        preflop_56betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 55:
                preflop_56betters.append(player)
        return preflop_56betters

    def _get_preflop_57betters(self) -> List[Player]:
        """Get a list of players who 57-bet preflop"""
        preflop_57betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 56:
                preflop_57betters.append(player)
        return preflop_57betters

    def _get_preflop_58betters(self) -> List[Player]:
        """Get a list of players who 58-bet preflop"""
        preflop_58betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 57:
                preflop_58betters.append(player)
        return preflop_58betters

    def _get_preflop_59betters(self) -> List[Player]:
        """Get a list of players who 59-bet preflop"""
        preflop_59betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 58:
                preflop_59betters.append(player)
        return preflop_59betters

    def _get_preflop_60betters(self) -> List[Player]:
        """Get a list of players who 60-bet preflop"""
        preflop_60betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 59:
                preflop_60betters.append(player)
        return preflop_60betters

    def _get_preflop_61betters(self) -> List[Player]:
        """Get a list of players who 61-bet preflop"""
        preflop_61betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 60:
                preflop_61betters.append(player)
        return preflop_61betters

    def _get_preflop_62betters(self) -> List[Player]:
        """Get a list of players who 62-bet preflop"""
        preflop_62betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 61:
                preflop_62betters.append(player)
        return preflop_62betters

    def _get_preflop_63betters(self) -> List[Player]:
        """Get a list of players who 63-bet preflop"""
        preflop_63betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 62:
                preflop_63betters.append(player)
        return preflop_63betters

    def _get_preflop_64betters(self) -> List[Player]:
        """Get a list of players who 64-bet preflop"""
        preflop_64betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 63:
                preflop_64betters.append(player)
        return preflop_64betters

    def _get_preflop_65betters(self) -> List[Player]:
        """Get a list of players who 65-bet preflop"""
        preflop_65betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 64:
                preflop_65betters.append(player)
        return preflop_65betters

    def _get_preflop_66betters(self) -> List[Player]:
        """Get a list of players who 66-bet preflop"""
        preflop_66betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 65:
                preflop_66betters.append(player)
        return preflop_66betters

    def _get_preflop_67betters(self) -> List[Player]:
        """Get a list of players who 67-bet preflop"""
        preflop_67betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 66:
                preflop_67betters.append(player)
        return preflop_67betters

    def _get_preflop_68betters(self) -> List[Player]:
        """Get a list of players who 68-bet preflop"""
        preflop_68betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 67:
                preflop_68betters.append(player)
        return preflop_68betters

    def _get_preflop_69betters(self) -> List[Player]:
        """Get a list of players who 69-bet preflop"""
        preflop_69betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 68:
                preflop_69betters.append(player)
        return preflop_69betters

    def _get_preflop_70betters(self) -> List[Player]:
        """Get a list of players who 70-bet preflop"""
        preflop_70betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 69:
                preflop_70betters.append(player)
        return preflop_70betters

    def _get_preflop_71betters(self) -> List[Player]:
        """Get a list of players who 71-bet preflop"""
        preflop_71betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 70:
                preflop_71betters.append(player)
        return preflop_71betters

    def _get_preflop_72betters(self) -> List[Player]:
        """Get a list of players who 72-bet preflop"""
        preflop_72betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 71:
                preflop_72betters.append(player)
        return preflop_72betters

    def _get_preflop_73betters(self) -> List[Player]:
        """Get a list of players who 73-bet preflop"""
        preflop_73betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 72:
                preflop_73betters.append(player)
        return preflop_73betters

    def _get_preflop_74betters(self) -> List[Player]:
        """Get a list of players who 74-bet preflop"""
        preflop_74betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 73:
                preflop_74betters.append(player)
        return preflop_74betters

    def _get_preflop_75betters(self) -> List[Player]:
        """Get a list of players who 75-bet preflop"""
        preflop_75betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 74:
                preflop_75betters.append(player)
        return preflop_75betters

    def _get_preflop_76betters(self) -> List[Player]:
        """Get a list of players who 76-bet preflop"""
        preflop_76betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 75:
                preflop_76betters.append(player)
        return preflop_76betters

    def _get_preflop_77betters(self) -> List[Player]:
        """Get a list of players who 77-bet preflop"""
        preflop_77betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 76:
                preflop_77betters.append(player)
        return preflop_77betters

    def _get_preflop_78betters(self) -> List[Player]:
        """Get a list of players who 78-bet preflop"""
        preflop_78betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 77:
                preflop_78betters.append(player)
        return preflop_78betters

    def _get_preflop_79betters(self) -> List[Player]:
        """Get a list of players who 79-bet preflop"""
        preflop_79betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 78:
                preflop_79betters.append(player)
        return preflop_79betters

    def _get_preflop_80betters(self) -> List[Player]:
        """Get a list of players who 80-bet preflop"""
        preflop_80betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 79:
                preflop_80betters.append(player)
        return preflop_80betters

    def _get_preflop_81betters(self) -> List[Player]:
        """Get a list of players who 81-bet preflop"""
        preflop_81betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 80:
                preflop_81betters.append(player)
        return preflop_81betters

    def _get_preflop_82betters(self) -> List[Player]:
        """Get a list of players who 82-bet preflop"""
        preflop_82betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 81:
                preflop_82betters.append(player)
        return preflop_82betters

    def _get_preflop_83betters(self) -> List[Player]:
        """Get a list of players who 83-bet preflop"""
        preflop_83betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 82:
                preflop_83betters.append(player)
        return preflop_83betters

    def _get_preflop_84betters(self) -> List[Player]:
        """Get a list of players who 84-bet preflop"""
        preflop_84betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 83:
                preflop_84betters.append(player)
        return preflop_84betters

    def _get_preflop_85betters(self) -> List[Player]:
        """Get a list of players who 85-bet preflop"""
        preflop_85betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 84:
                preflop_85betters.append(player)
        return preflop_85betters

    def _get_preflop_86betters(self) -> List[Player]:
        """Get a list of players who 86-bet preflop"""
        preflop_86betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 85:
                preflop_86betters.append(player)
        return preflop_86betters

    def _get_preflop_87betters(self) -> List[Player]:
        """Get a list of players who 87-bet preflop"""
        preflop_87betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 86:
                preflop_87betters.append(player)
        return preflop_87betters

    def _get_preflop_88betters(self) -> List[Player]:
        """Get a list of players who 88-bet preflop"""
        preflop_88betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 87:
                preflop_88betters.append(player)
        return preflop_88betters

    def _get_preflop_89betters(self) -> List[Player]:
        """Get a list of players who 89-bet preflop"""
        preflop_89betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 88:
                preflop_89betters.append(player)
        return preflop_89betters

    def _get_preflop_90betters(self) -> List[Player]:
        """Get a list of players who 90-bet preflop"""
        preflop_90betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 89:
                preflop_90betters.append(player)
        return preflop_90betters

    def _get_preflop_91betters(self) -> List[Player]:
        """Get a list of players who 91-bet preflop"""
        preflop_91betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 90:
                preflop_91betters.append(player)
        return preflop_91betters

    def _get_preflop_92betters(self) -> List[Player]:
        """Get a list of players who 92-bet preflop"""
        preflop_92betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 91:
                preflop_92betters.append(player)
        return preflop_92betters

    def _get_preflop_93betters(self) -> List[Player]:
        """Get a list of players who 93-bet preflop"""
        preflop_93betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 92:
                preflop_93betters.append(player)
        return preflop_93betters

    def _get_preflop_94betters(self) -> List[Player]:
        """Get a list of players who 94-bet preflop"""
        preflop_94betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 93:
                preflop_94betters.append(player)
        return preflop_94betters

    def _get_preflop_95betters(self) -> List[Player]:
        """Get a list of players who 95-bet preflop"""
        preflop_95betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 94:
                preflop_95betters.append(player)
        return preflop_95betters

    def _get_preflop_96betters(self) -> List[Player]:
        """Get a list of players who 96-bet preflop"""
        preflop_96betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 95:
                preflop_96betters.append(player)
        return preflop_96betters

    def _get_preflop_97betters(self) -> List[Player]:
        """Get a list of players who 97-bet preflop"""
        preflop_97betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 96:
                preflop_97betters.append(player)
        return preflop_97betters

    def _get_preflop_98betters(self) -> List[Player]:
        """Get a list of players who 98-bet preflop"""
        preflop_98betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 97:
                preflop_98betters.append(player)
        return preflop_98betters

    def _get_preflop_99betters(self) -> List[Player]:
        """Get a list of players who 99-bet preflop"""
        preflop_99betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 98:
                preflop_99betters.append(player)
        return preflop_99betters

    def _get_preflop_100betters(self) -> List[Player]:
        """Get a list of players who 100-bet preflop"""
        preflop_100betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 99:
                preflop_100betters.append(player)
        return preflop_100betters

    def _get_preflop_101betters(self) -> List[Player]:
        """Get a list of players who 101-bet preflop"""
        preflop_101betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 100:
                preflop_101betters.append(player)
        return preflop_101betters

    def _get_preflop_102betters(self) -> List[Player]:
        """Get a list of players who 102-bet preflop"""
        preflop_102betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 101:
                preflop_102betters.append(player)
        return preflop_102betters

    def _get_preflop_103betters(self) -> List[Player]:
        """Get a list of players who 103-bet preflop"""
        preflop_103betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 102:
                preflop_103betters.append(player)
        return preflop_103betters

    def _get_preflop_104betters(self) -> List[Player]:
        """Get a list of players who 104-bet preflop"""
        preflop_104betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 103:
                preflop_104betters.append(player)
        return preflop_104betters

    def _get_preflop_105betters(self) -> List[Player]:
        """Get a list of players who 105-bet preflop"""
        preflop_105betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 104:
                preflop_105betters.append(player)
        return preflop_105betters

    def _get_preflop_106betters(self) -> List[Player]:
        """Get a list of players who 106-bet preflop"""
        preflop_106betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 105:
                preflop_106betters.append(player)
        return preflop_106betters

    def _get_preflop_107betters(self) -> List[Player]:
        """Get a list of players who 107-bet preflop"""
        preflop_107betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 106:
                preflop_107betters.append(player)
        return preflop_107betters

    def _get_preflop_108betters(self) -> List[Player]:
        """Get a list of players who 108-bet preflop"""
        preflop_108betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 107:
                preflop_108betters.append(player)
        return preflop_108betters

    def _get_preflop_109betters(self) -> List[Player]:
        """Get a list of players who 109-bet preflop"""
        preflop_109betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 108:
                preflop_109betters.append(player)
        return preflop_109betters

    def _get_preflop_110betters(self) -> List[Player]:
        """Get a list of players who 110-bet preflop"""
        preflop_110betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 109:
                preflop_110betters.append(player)
        return preflop_110betters

    def _get_preflop_111betters(self) -> List[Player]:
        """Get a list of players who 111-bet preflop"""
        preflop_111betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 110:
                preflop_111betters.append(player)
        return preflop_111betters

    def _get_preflop_112betters(self) -> List[Player]:
        """Get a list of players who 112-bet preflop"""
        preflop_112betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 111:
                preflop_112betters.append(player)
        return preflop_112betters

    def _get_preflop_113betters(self) -> List[Player]:
        """Get a list of players who 113-bet preflop"""
        preflop_113betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 112:
                preflop_113betters.append(player)
        return preflop_113betters

    def _get_preflop_114betters(self) -> List[Player]:
        """Get a list of players who 114-bet preflop"""
        preflop_114betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 113:
                preflop_114betters.append(player)
        return preflop_114betters

    def _get_preflop_115betters(self) -> List[Player]:
        """Get a list of players who 115-bet preflop"""
        preflop_115betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 114:
                preflop_115betters.append(player)
        return preflop_115betters

    def _get_preflop_116betters(self) -> List[Player]:
        """Get a list of players who 116-bet preflop"""
        preflop_116betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 115:
                preflop_116betters.append(player)
        return preflop_116betters

    def _get_preflop_117betters(self) -> List[Player]:
        """Get a list of players who 117-bet preflop"""
        preflop_117betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 116:
                preflop_117betters.append(player)
        return preflop_117betters

    def _get_preflop_118betters(self) -> List[Player]:
        """Get a list of players who 118-bet preflop"""
        preflop_118betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 117:
                preflop_118betters.append(player)
        return preflop_118betters

    def _get_preflop_119betters(self) -> List[Player]:
        """Get a list of players who 119-bet preflop"""
        preflop_119betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 118:
                preflop_119betters.append(player)
        return preflop_119betters

    def _get_preflop_120betters(self) -> List[Player]:
        """Get a list of players who 120-bet preflop"""
        preflop_120betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 119:
                preflop_120betters.append(player)
        return preflop_120betters

    def _get_preflop_121betters(self) -> List[Player]:
        """Get a list of players who 121-bet preflop"""
        preflop_121betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 120:
                preflop_121betters.append(player)
        return preflop_121betters

    def _get_preflop_122betters(self) -> List[Player]:
        """Get a list of players who 122-bet preflop"""
        preflop_122betters = []
        for player in self.table_state.players:
            if player.last_action == Action.RAISE and player.preflop_action_count == 121:
                preflop_122betters.append(player)
        return preflop_122betters

    def _in_position(self) -> bool:
        """Check if we're in position"""
        # Use the position symbols to determine if we're in position
        return self.table_state.is_late_position() or self.table_state.is_last_to_act()