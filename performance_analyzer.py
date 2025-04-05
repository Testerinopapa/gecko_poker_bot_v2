#!/usr/bin/env python3
"""
GeckoBot Poker - Performance Analyzer
This module analyzes the bot's decision-making patterns and performance.
"""

import os
import json
import glob
import csv
from typing import Dict, List, Any, Optional
from collections import defaultdict

class PerformanceAnalyzer:
    """
    Analyzes the bot's decision-making patterns and performance
    """
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.sessions = self._load_sessions()
        
    def _load_sessions(self) -> List[Dict[str, Any]]:
        """Load all available session data"""
        sessions = []
        data_files = glob.glob(os.path.join(self.log_dir, "*_data.json"))
        
        for file_path in data_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Add file path to the data
                    data['file_path'] = file_path
                    sessions.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        # Sort by timestamp (most recent first)
        sessions.sort(key=lambda x: x.get('session_id', ''), reverse=True)
        return sessions
    
    def analyze_decision_patterns(self, session_index: int = 0) -> Dict[str, Any]:
        """Analyze the bot's decision patterns"""
        if not self.sessions:
            return {"error": "No sessions available"}
            
        if session_index >= len(self.sessions):
            session_index = 0
            
        session = self.sessions[session_index]
        hands = session.get('hands', [])
        
        if not hands:
            return {
                "session_id": session.get('session_id', 'Unknown'),
                "error": "No hand data available"
            }
        
        # Analyze decision patterns by street, position, and hand strength
        patterns = {
            "by_street": defaultdict(lambda: defaultdict(int)),
            "by_position": defaultdict(lambda: defaultdict(int)),
            "by_hand_strength": defaultdict(lambda: defaultdict(int)),
            "by_pot_odds": defaultdict(lambda: defaultdict(int)),
            "by_stack_depth": defaultdict(lambda: defaultdict(int))
        }
        
        for hand in hands:
            # Get position
            position = "Unknown"
            if hand.get('small_blind') is not None and hand.get('big_blind') is not None:
                sb = hand.get('small_blind')
                bb = hand.get('big_blind')
                hero_stack = hand.get('hero_stack', 0)
                
                if hero_stack == sb:
                    position = "SB"
                elif hero_stack == bb:
                    position = "BB"
                else:
                    position = "BTN"
            
            # Get hand strength category
            hole_cards = hand.get('hole_cards', [])
            hand_strength = self._categorize_hand_strength(hole_cards)
            
            # Analyze decisions by street
            for street, street_data in hand.get('streets', {}).items():
                for action in street_data.get('actions', []):
                    if action.get('player') == 'Bot':
                        action_type = action.get('action', 'unknown')
                        
                        # Count by street
                        patterns["by_street"][street][action_type] += 1
                        
                        # Count by position
                        patterns["by_position"][position][action_type] += 1
                        
                        # Count by hand strength
                        patterns["by_hand_strength"][hand_strength][action_type] += 1
                        
                        # Calculate pot odds and count by pot odds range
                        pot_size = hand.get('pot_size', 0)
                        amount = action.get('amount')
                        
                        if pot_size > 0 and amount is not None and amount > 0:
                            pot_odds = amount / (pot_size + amount)
                            pot_odds_range = self._categorize_pot_odds(pot_odds)
                            patterns["by_pot_odds"][pot_odds_range][action_type] += 1
                        
                        # Calculate stack depth and count by stack depth range
                        hero_stack = hand.get('hero_stack', 0)
                        if hero_stack > 0 and hand.get('big_blind') is not None and hand.get('big_blind') > 0:
                            stack_depth = hero_stack / hand.get('big_blind')
                            stack_depth_range = self._categorize_stack_depth(stack_depth)
                            patterns["by_stack_depth"][stack_depth_range][action_type] += 1
        
        # Convert defaultdicts to regular dicts for JSON serialization
        result = {
            "session_id": session.get('session_id', 'Unknown'),
            "by_street": {k: dict(v) for k, v in patterns["by_street"].items()},
            "by_position": {k: dict(v) for k, v in patterns["by_position"].items()},
            "by_hand_strength": {k: dict(v) for k, v in patterns["by_hand_strength"].items()},
            "by_pot_odds": {k: dict(v) for k, v in patterns["by_pot_odds"].items()},
            "by_stack_depth": {k: dict(v) for k, v in patterns["by_stack_depth"].items()}
        }
        
        return result
    
    def analyze_performance_metrics(self, session_index: int = 0) -> Dict[str, Any]:
        """Analyze the bot's performance metrics"""
        if not self.sessions:
            return {"error": "No sessions available"}
            
        if session_index >= len(self.sessions):
            session_index = 0
            
        session = self.sessions[session_index]
        hands = session.get('hands', [])
        
        if not hands:
            return {
                "session_id": session.get('session_id', 'Unknown'),
                "error": "No hand data available"
            }
        
        # Calculate performance metrics
        metrics = {
            "session_id": session.get('session_id', 'Unknown'),
            "hands_played": len(hands),
            "win_rate": 0,
            "bb_per_hand": 0,
            "showdown_win_rate": 0,
            "non_showdown_win_rate": 0,
            "continuation_bet_success": 0,
            "bluff_success": 0,
            "value_bet_success": 0
        }
        
        # Calculate win rate and BB/hand
        win_count = 0
        total_profit = 0
        big_blind = hands[0].get('big_blind', 1) if hands else 1
        
        for i in range(len(hands) - 1):
            current_stack = hands[i].get('hero_stack', 0)
            next_stack = hands[i + 1].get('hero_stack', 0)
            profit = next_stack - current_stack
            
            if profit > 0:
                win_count += 1
                
            total_profit += profit
            
        if len(hands) > 1:
            metrics["win_rate"] = win_count / (len(hands) - 1)
            metrics["bb_per_hand"] = total_profit / ((len(hands) - 1) * big_blind)
        
        # Calculate showdown and non-showdown win rates
        showdown_hands = 0
        showdown_wins = 0
        non_showdown_hands = 0
        non_showdown_wins = 0
        
        for i in range(len(hands) - 1):
            current_hand = hands[i]
            next_hand = hands[i + 1]
            profit = next_hand.get('hero_stack', 0) - current_hand.get('hero_stack', 0)
            
            # Check if hand went to showdown (reached river)
            if 'RIVER' in current_hand.get('streets', {}):
                showdown_hands += 1
                if profit > 0:
                    showdown_wins += 1
            else:
                non_showdown_hands += 1
                if profit > 0:
                    non_showdown_wins += 1
                    
        metrics["showdown_win_rate"] = showdown_wins / showdown_hands if showdown_hands > 0 else 0
        metrics["non_showdown_win_rate"] = non_showdown_wins / non_showdown_hands if non_showdown_hands > 0 else 0
        
        # Calculate continuation bet success rate
        c_bet_attempts = 0
        c_bet_success = 0
        
        for hand in hands:
            streets = hand.get('streets', {})
            
            # Check if bot raised preflop
            preflop_raised = False
            if 'PREFLOP' in streets:
                for action in streets['PREFLOP'].get('actions', []):
                    if action.get('player') == 'Bot' and action.get('action') == 'raises':
                        preflop_raised = True
                        break
            
            # Check if bot made continuation bet on flop
            if preflop_raised and 'FLOP' in streets:
                for action in streets['FLOP'].get('actions', []):
                    if action.get('player') == 'Bot' and action.get('action') == 'bets':
                        c_bet_attempts += 1
                        
                        # Check if continuation bet was successful (all opponents folded)
                        success = True
                        for opponent_action in streets['FLOP'].get('actions', []):
                            if opponent_action.get('player') != 'Bot' and opponent_action.get('action') == 'calls':
                                success = False
                                break
                                
                        if success:
                            c_bet_success += 1
                            
                        break
                        
        metrics["continuation_bet_success"] = c_bet_success / c_bet_attempts if c_bet_attempts > 0 else 0
        
        # Calculate bluff success rate
        bluff_attempts = 0
        bluff_success = 0
        
        for hand in hands:
            for street, street_data in hand.get('streets', {}).items():
                win_prob = street_data.get('win_probability', 0)
                
                # Consider it a bluff if win probability is less than 30%
                if win_prob < 0.3:
                    for action in street_data.get('actions', []):
                        if action.get('player') == 'Bot' and action.get('action') in ['bets', 'raises']:
                            bluff_attempts += 1
                            
                            # Check if bluff was successful (all opponents folded)
                            success = True
                            for opponent_action in street_data.get('actions', []):
                                if opponent_action.get('player') != 'Bot' and opponent_action.get('action') == 'calls':
                                    success = False
                                    break
                                    
                            if success:
                                bluff_success += 1
                                
                            break
                            
        metrics["bluff_success"] = bluff_success / bluff_attempts if bluff_attempts > 0 else 0
        
        # Calculate value bet success rate
        value_bet_attempts = 0
        value_bet_success = 0
        
        for hand in hands:
            for street, street_data in hand.get('streets', {}).items():
                win_prob = street_data.get('win_probability', 0)
                
                # Consider it a value bet if win probability is greater than 70%
                if win_prob > 0.7:
                    for action in street_data.get('actions', []):
                        if action.get('player') == 'Bot' and action.get('action') in ['bets', 'raises']:
                            value_bet_attempts += 1
                            
                            # Check if value bet was called
                            called = False
                            for opponent_action in street_data.get('actions', []):
                                if opponent_action.get('player') != 'Bot' and opponent_action.get('action') == 'calls':
                                    called = True
                                    break
                                    
                            if called:
                                value_bet_success += 1
                                
                            break
                            
        metrics["value_bet_success"] = value_bet_success / value_bet_attempts if value_bet_attempts > 0 else 0
        
        return metrics
    
    def export_decision_data(self, output_file: str, session_index: int = 0) -> bool:
        """Export decision data to CSV for further analysis"""
        if not self.sessions:
            print("Error: No sessions available")
            return False
            
        if session_index >= len(self.sessions):
            session_index = 0
            
        session = self.sessions[session_index]
        hands = session.get('hands', [])
        
        if not hands:
            print(f"Error: No hand data available for session {session.get('session_id', 'Unknown')}")
            return False
        
        # Prepare data for export
        decision_data = []
        
        for hand in hands:
            hole_cards = hand.get('hole_cards', [])
            hand_strength = self._categorize_hand_strength(hole_cards)
            
            for street, street_data in hand.get('streets', {}).items():
                win_prob = street_data.get('win_probability', 0)
                community_cards = street_data.get('cards', [])
                
                for action in street_data.get('actions', []):
                    if action.get('player') == 'Bot':
                        action_type = action.get('action', 'unknown')
                        amount = action.get('amount')
                        
                        # Calculate pot odds
                        pot_size = hand.get('pot_size', 0)
                        pot_odds = amount / (pot_size + amount) if pot_size > 0 and amount is not None and amount > 0 else None
                        
                        # Calculate stack depth
                        hero_stack = hand.get('hero_stack', 0)
                        stack_depth = hero_stack / hand.get('big_blind') if hero_stack > 0 and hand.get('big_blind') is not None and hand.get('big_blind') > 0 else None
                        
                        # Add decision data
                        decision_data.append({
                            "hand_id": hand.get('hand_id', 0),
                            "street": street,
                            "hole_cards": " ".join(hole_cards),
                            "community_cards": " ".join(community_cards),
                            "hand_strength": hand_strength,
                            "win_probability": win_prob,
                            "action": action_type,
                            "amount": amount,
                            "pot_size": pot_size,
                            "pot_odds": pot_odds,
                            "stack_depth": stack_depth
                        })
        
        # Write to CSV
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=decision_data[0].keys())
                writer.writeheader()
                writer.writerows(decision_data)
                
            print(f"Decision data exported to {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting decision data: {e}")
            return False
    
    def _categorize_hand_strength(self, hole_cards: List[str]) -> str:
        """Categorize hand strength based on hole cards"""
        if len(hole_cards) != 2:
            return "Unknown"
            
        # Extract ranks and suited status
        ranks = [card[0] for card in hole_cards]
        suited = hole_cards[0][-1] == hole_cards[1][-1]
        
        # Normalize ranks
        ranks = [rank.replace('T', '10').replace('J', '11').replace('Q', '12').replace('K', '13').replace('A', '14') for rank in ranks]
        try:
            ranks = [int(rank) for rank in ranks]
            ranks.sort(reverse=True)
        except ValueError:
            return "Unknown"
            
        # Categorize hand
        if (ranks == [14, 14] or  # AA
            ranks == [13, 13] or  # KK
            ranks == [12, 12] or  # QQ
            (ranks == [14, 13] and suited)):  # AKs
            return "Premium"
        elif (ranks == [11, 11] or  # JJ
              ranks == [10, 10] or  # TT
              (ranks == [14, 12] and suited) or  # AQs
              (ranks == [14, 11] and suited) or  # AJs
              (ranks == [14, 13] and not suited)):  # AKo
            return "Strong"
        elif (ranks == [9, 9] or  # 99
              ranks == [8, 8] or  # 88
              (ranks == [14, 10] and suited) or  # ATs
              (ranks == [13, 12] and suited) or  # KQs
              (ranks == [14, 12] and not suited)):  # AQo
            return "Medium"
        else:
            return "Weak"
    
    def _categorize_pot_odds(self, pot_odds: float) -> str:
        """Categorize pot odds into ranges"""
        if pot_odds < 0.2:
            return "0-20%"
        elif pot_odds < 0.3:
            return "20-30%"
        elif pot_odds < 0.4:
            return "30-40%"
        elif pot_odds < 0.5:
            return "40-50%"
        else:
            return "50%+"
    
    def _categorize_stack_depth(self, stack_depth: float) -> str:
        """Categorize stack depth into ranges"""
        if stack_depth < 20:
            return "Short (< 20 BB)"
        elif stack_depth < 50:
            return "Medium (20-50 BB)"
        elif stack_depth < 100:
            return "Deep (50-100 BB)"
        else:
            return "Very Deep (100+ BB)"

def main():
    """Main function to run the performance analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze GeckoBot performance and decision patterns')
    parser.add_argument('--log-dir', default='logs', help='Directory containing log files')
    parser.add_argument('--session', type=int, default=0, help='Session index to analyze (0 = most recent)')
    parser.add_argument('--export', help='Export decision data to CSV file')
    parser.add_argument('--metrics', action='store_true', help='Show performance metrics')
    parser.add_argument('--patterns', action='store_true', help='Show decision patterns')
    parser.add_argument('--list', action='store_true', help='List available sessions')
    
    args = parser.parse_args()
    
    # Create performance analyzer
    analyzer = PerformanceAnalyzer(args.log_dir)
    
    # List sessions if requested
    if args.list:
        sessions = analyzer._load_sessions()
        print(f"Found {len(sessions)} sessions:")
        for i, session in enumerate(sessions):
            print(f"{i}: {session.get('session_id', 'Unknown')} - {session.get('hands_played', 0)} hands, P/L: {session.get('profit_loss', 0)}")
        return
    
    # Show performance metrics if requested
    if args.metrics:
        metrics = analyzer.analyze_performance_metrics(args.session)
        if "error" in metrics:
            print(f"Error: {metrics['error']}")
        else:
            print(f"=== Performance Metrics for Session {metrics['session_id']} ===")
            print(f"Hands Played: {metrics['hands_played']}")
            print(f"Win Rate: {metrics['win_rate']:.2%}")
            print(f"BB/Hand: {metrics['bb_per_hand']:.2f}")
            print(f"Showdown Win Rate: {metrics['showdown_win_rate']:.2%}")
            print(f"Non-Showdown Win Rate: {metrics['non_showdown_win_rate']:.2%}")
            print(f"Continuation Bet Success: {metrics['continuation_bet_success']:.2%}")
            print(f"Bluff Success: {metrics['bluff_success']:.2%}")
            print(f"Value Bet Success: {metrics['value_bet_success']:.2%}")
    
    # Show decision patterns if requested
    if args.patterns:
        patterns = analyzer.analyze_decision_patterns(args.session)
        if "error" in patterns:
            print(f"Error: {patterns['error']}")
        else:
            print(f"=== Decision Patterns for Session {patterns['session_id']} ===")
            
            print("\n== By Street ==")
            for street, actions in patterns["by_street"].items():
                print(f"{street}:")
                for action, count in actions.items():
                    print(f"  {action}: {count}")
            
            print("\n== By Position ==")
            for position, actions in patterns["by_position"].items():
                print(f"{position}:")
                for action, count in actions.items():
                    print(f"  {action}: {count}")
            
            print("\n== By Hand Strength ==")
            for strength, actions in patterns["by_hand_strength"].items():
                print(f"{strength}:")
                for action, count in actions.items():
                    print(f"  {action}: {count}")
            
            print("\n== By Pot Odds ==")
            for odds, actions in patterns["by_pot_odds"].items():
                print(f"{odds}:")
                for action, count in actions.items():
                    print(f"  {action}: {count}")
            
            print("\n== By Stack Depth ==")
            for depth, actions in patterns["by_stack_depth"].items():
                print(f"{depth}:")
                for action, count in actions.items():
                    print(f"  {action}: {count}")
    
    # Export decision data if requested
    if args.export:
        analyzer.export_decision_data(args.export, args.session)

if __name__ == "__main__":
    main()
