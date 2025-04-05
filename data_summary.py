#!/usr/bin/env python3
"""
GeckoBot Poker - Data Summary Tool
This module extracts key insights from the poker bot's log data.
"""

import os
import json
import glob
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

class DataSummary:
    """
    Extracts and summarizes data from GeckoBot log files
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
    
    def get_session_summary(self, session_index: int = 0) -> Dict[str, Any]:
        """Get a summary of the specified session"""
        if not self.sessions:
            return {"error": "No sessions available"}
            
        if session_index >= len(self.sessions):
            session_index = 0
            
        session = self.sessions[session_index]
        hands = session.get('hands', [])
        
        if not hands:
            return {
                "session_id": session.get('session_id', 'Unknown'),
                "hands_played": 0,
                "error": "No hand data available"
            }
        
        # Basic session stats
        summary = {
            "session_id": session.get('session_id', 'Unknown'),
            "hands_played": session.get('hands_played', 0),
            "starting_stack": session.get('starting_stack', 0),
            "ending_stack": session.get('ending_stack', 0),
            "profit_loss": session.get('profit_loss', 0),
            "duration": session.get('duration', 0),
        }
        
        # Calculate win rate
        win_count = 0
        for i in range(len(hands) - 1):
            current_stack = hands[i].get('hero_stack', 0)
            next_stack = hands[i + 1].get('hero_stack', 0)
            if next_stack > current_stack:
                win_count += 1
                
        summary["win_rate"] = win_count / (len(hands) - 1) if len(hands) > 1 else 0
        
        # Calculate VPIP (Voluntarily Put Money In Pot)
        vpip_count = 0
        for hand in hands:
            for action in hand.get('actions', []):
                if action.get('player') == 'Bot' and action.get('action') in ['calls', 'raises', 'bets']:
                    vpip_count += 1
                    break
                    
        summary["vpip"] = vpip_count / len(hands) if hands else 0
        
        # Calculate PFR (Pre-Flop Raise)
        pfr_count = 0
        for hand in hands:
            preflop_data = hand.get('streets', {}).get('PREFLOP', {})
            for action in preflop_data.get('actions', []):
                if action.get('player') == 'Bot' and action.get('action') == 'raises':
                    pfr_count += 1
                    break
                    
        summary["pfr"] = pfr_count / len(hands) if hands else 0
        
        # Calculate AF (Aggression Factor)
        aggressive_actions = 0
        passive_actions = 0
        
        for hand in hands:
            for action in hand.get('actions', []):
                if action.get('player') == 'Bot':
                    if action.get('action') in ['raises', 'bets']:
                        aggressive_actions += 1
                    elif action.get('action') in ['calls', 'checks']:
                        passive_actions += 1
                        
        summary["aggression_factor"] = aggressive_actions / passive_actions if passive_actions > 0 else float('inf')
        
        # Calculate average win probability when making decisions
        win_probs = []
        for hand in hands:
            for street, street_data in hand.get('streets', {}).items():
                win_prob = street_data.get('win_probability', 0)
                for action in street_data.get('actions', []):
                    if action.get('player') == 'Bot':
                        win_probs.append(win_prob)
                        
        summary["avg_win_probability"] = sum(win_probs) / len(win_probs) if win_probs else 0
        
        # Calculate hand strength distribution
        hand_strengths = {
            "premium": 0,  # AA, KK, QQ, AKs
            "strong": 0,   # JJ, TT, AQs, AJs, AKo
            "medium": 0,   # 99, 88, ATs, KQs, AQo
            "weak": 0      # Everything else
        }
        
        for hand in hands:
            hole_cards = hand.get('hole_cards', [])
            if len(hole_cards) != 2:
                continue
                
            # Extract ranks and suited status
            ranks = [card[0] for card in hole_cards]
            suited = hole_cards[0][-1] == hole_cards[1][-1]
            
            # Normalize ranks
            ranks = [rank.replace('T', '10').replace('J', '11').replace('Q', '12').replace('K', '13').replace('A', '14') for rank in ranks]
            try:
                ranks = [int(rank) for rank in ranks]
                ranks.sort(reverse=True)
            except ValueError:
                continue
                
            # Categorize hand
            if (ranks == [14, 14] or  # AA
                ranks == [13, 13] or  # KK
                ranks == [12, 12] or  # QQ
                (ranks == [14, 13] and suited)):  # AKs
                hand_strengths["premium"] += 1
            elif (ranks == [11, 11] or  # JJ
                  ranks == [10, 10] or  # TT
                  (ranks == [14, 12] and suited) or  # AQs
                  (ranks == [14, 11] and suited) or  # AJs
                  (ranks == [14, 13] and not suited)):  # AKo
                hand_strengths["strong"] += 1
            elif (ranks == [9, 9] or  # 99
                  ranks == [8, 8] or  # 88
                  (ranks == [14, 10] and suited) or  # ATs
                  (ranks == [13, 12] and suited) or  # KQs
                  (ranks == [14, 12] and not suited)):  # AQo
                hand_strengths["medium"] += 1
            else:
                hand_strengths["weak"] += 1
                
        for strength, count in hand_strengths.items():
            summary[f"hand_strength_{strength}"] = count / len(hands) if hands else 0
        
        # Calculate street reach percentages
        street_counts = Counter()
        for hand in hands:
            for street in hand.get('streets', {}).keys():
                street_counts[street] += 1
                
        for street in ['PREFLOP', 'FLOP', 'TURN', 'RIVER']:
            summary[f"reached_{street.lower()}"] = street_counts[street] / len(hands) if hands else 0
            
        # Calculate average pot size
        pot_sizes = [hand.get('pot_size', 0) for hand in hands]
        summary["avg_pot_size"] = sum(pot_sizes) / len(pot_sizes) if pot_sizes else 0
        
        # Calculate average bet sizing
        bet_sizes = []
        for hand in hands:
            for action in hand.get('actions', []):
                if action.get('player') == 'Bot' and action.get('action') in ['raises', 'bets'] and action.get('amount') is not None:
                    bet_sizes.append(action.get('amount'))
                    
        summary["avg_bet_size"] = sum(bet_sizes) / len(bet_sizes) if bet_sizes else 0
        
        return summary
    
    def get_action_distribution(self, session_index: int = 0) -> Dict[str, Any]:
        """Get the distribution of actions for the specified session"""
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
        
        # Count actions by type and street
        action_counts = defaultdict(Counter)
        street_action_counts = defaultdict(lambda: defaultdict(Counter))
        
        for hand in hands:
            for street, street_data in hand.get('streets', {}).items():
                for action in street_data.get('actions', []):
                    player = action.get('player', 'Unknown')
                    action_type = action.get('action', 'unknown')
                    
                    action_counts[player][action_type] += 1
                    street_action_counts[street][player][action_type] += 1
        
        # Calculate percentages
        result = {
            "session_id": session.get('session_id', 'Unknown'),
            "by_player": {},
            "by_street": {}
        }
        
        for player, counts in action_counts.items():
            total = sum(counts.values())
            result["by_player"][player] = {
                "total": total,
                "actions": {action: count / total for action, count in counts.items()}
            }
            
        for street, players in street_action_counts.items():
            result["by_street"][street] = {}
            for player, counts in players.items():
                total = sum(counts.values())
                result["by_street"][street][player] = {
                    "total": total,
                    "actions": {action: count / total for action, count in counts.items()}
                }
        
        return result
    
    def get_win_probability_analysis(self, session_index: int = 0) -> Dict[str, Any]:
        """Analyze win probabilities and decision making"""
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
        
        # Analyze decisions based on win probability
        prob_ranges = {
            "0-20%": (0, 0.2),
            "20-40%": (0.2, 0.4),
            "40-60%": (0.4, 0.6),
            "60-80%": (0.6, 0.8),
            "80-100%": (0.8, 1.0)
        }
        
        decisions_by_prob = {range_name: defaultdict(int) for range_name in prob_ranges}
        
        for hand in hands:
            for street, street_data in hand.get('streets', {}).items():
                win_prob = street_data.get('win_probability', 0)
                
                # Find the probability range
                for range_name, (min_prob, max_prob) in prob_ranges.items():
                    if min_prob <= win_prob < max_prob:
                        # Count bot actions in this probability range
                        for action in street_data.get('actions', []):
                            if action.get('player') == 'Bot':
                                action_type = action.get('action', 'unknown')
                                decisions_by_prob[range_name][action_type] += 1
                        break
        
        # Calculate expected value by decision
        ev_by_decision = defaultdict(list)
        
        for i in range(len(hands) - 1):
            current_hand = hands[i]
            next_hand = hands[i + 1]
            
            # Calculate stack change
            stack_change = next_hand.get('hero_stack', 0) - current_hand.get('hero_stack', 0)
            
            # Find bot's decisions in this hand
            for action in current_hand.get('actions', []):
                if action.get('player') == 'Bot':
                    action_type = action.get('action', 'unknown')
                    ev_by_decision[action_type].append(stack_change)
        
        # Calculate average EV by decision
        avg_ev = {}
        for decision, values in ev_by_decision.items():
            avg_ev[decision] = sum(values) / len(values) if values else 0
        
        return {
            "session_id": session.get('session_id', 'Unknown'),
            "decisions_by_probability": {
                range_name: dict(counts) for range_name, counts in decisions_by_prob.items()
            },
            "expected_value_by_decision": avg_ev
        }
    
    def get_hand_strength_analysis(self, session_index: int = 0) -> Dict[str, Any]:
        """Analyze hand strength and outcomes"""
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
        
        # Define hand categories
        hand_categories = {
            "premium_pairs": ["AA", "KK", "QQ"],
            "medium_pairs": ["JJ", "TT", "99"],
            "small_pairs": ["88", "77", "66", "55", "44", "33", "22"],
            "big_aces": ["AKs", "AQs", "AJs", "ATs", "AKo", "AQo"],
            "medium_aces": ["A9s", "A8s", "A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "AJo", "ATo"],
            "small_aces": ["A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "A3o", "A2o"],
            "face_cards": ["KQs", "KJs", "KTs", "QJs", "QTs", "JTs", "KQo", "KJo", "KTo", "QJo", "QTo", "JTo"],
            "connectors": ["98s", "87s", "76s", "65s", "54s", "43s", "32s", "98o", "87o", "76o", "65o", "54o", "43o", "32o"],
            "other": []
        }
        
        # Analyze hand outcomes by category
        results_by_category = {category: {"count": 0, "won": 0, "lost": 0, "ev": 0} for category in hand_categories}
        
        for i in range(len(hands) - 1):
            current_hand = hands[i]
            next_hand = hands[i + 1]
            
            hole_cards = current_hand.get('hole_cards', [])
            if len(hole_cards) != 2:
                continue
                
            # Normalize card representation
            card1, card2 = hole_cards
            rank1, suit1 = card1[0], card1[1]
            rank2, suit2 = card2[0], card2[1]
            
            # Convert T, J, Q, K, A to 10, 11, 12, 13, 14
            rank_map = {'T': '10', 'J': '11', 'Q': '12', 'K': '13', 'A': '14'}
            rank1 = rank_map.get(rank1, rank1)
            rank2 = rank_map.get(rank2, rank2)
            
            # Ensure rank1 >= rank2
            if int(rank1) < int(rank2):
                rank1, rank2 = rank2, rank1
                suit1, suit2 = suit2, suit1
                
            # Convert back to T, J, Q, K, A for hand notation
            reverse_rank_map = {'10': 'T', '11': 'J', '12': 'Q', '13': 'K', '14': 'A'}
            rank1 = reverse_rank_map.get(rank1, rank1)
            rank2 = reverse_rank_map.get(rank2, rank2)
            
            # Create hand notation
            suited = suit1 == suit2
            hand_notation = rank1 + rank2 + ('s' if suited else 'o')
            if rank1 == rank2:
                hand_notation = rank1 + rank2
                
            # Find category
            category_found = False
            for category, hands_in_category in hand_categories.items():
                if hand_notation in hands_in_category:
                    category_found = True
                    
                    # Calculate result
                    stack_change = next_hand.get('hero_stack', 0) - current_hand.get('hero_stack', 0)
                    
                    results_by_category[category]["count"] += 1
                    if stack_change > 0:
                        results_by_category[category]["won"] += 1
                    elif stack_change < 0:
                        results_by_category[category]["lost"] += 1
                        
                    results_by_category[category]["ev"] += stack_change
                    break
                    
            if not category_found:
                results_by_category["other"]["count"] += 1
        
        # Calculate win rates and average EV
        for category, results in results_by_category.items():
            if results["count"] > 0:
                results["win_rate"] = results["won"] / results["count"]
                results["avg_ev"] = results["ev"] / results["count"]
            else:
                results["win_rate"] = 0
                results["avg_ev"] = 0
                
        return {
            "session_id": session.get('session_id', 'Unknown'),
            "results_by_category": results_by_category
        }
    
    def generate_text_report(self, session_index: int = 0) -> str:
        """Generate a text report with key insights"""
        summary = self.get_session_summary(session_index)
        action_dist = self.get_action_distribution(session_index)
        win_prob = self.get_win_probability_analysis(session_index)
        hand_strength = self.get_hand_strength_analysis(session_index)
        
        if "error" in summary:
            return f"Error: {summary['error']}"
            
        # Format the report
        report = f"""
=== GeckoBot Poker Analysis Report ===
Session: {summary['session_id']}

== Basic Statistics ==
Hands Played: {summary['hands_played']}
Starting Stack: {summary['starting_stack']}
Ending Stack: {summary['ending_stack']}
Profit/Loss: {summary['profit_loss']}
Win Rate: {summary['win_rate']:.2%}
VPIP (Voluntarily Put Money In Pot): {summary['vpip']:.2%}
PFR (Pre-Flop Raise): {summary['pfr']:.2%}
Aggression Factor: {summary['aggression_factor']:.2f}
Average Win Probability: {summary['avg_win_probability']:.2%}

== Hand Strength Distribution ==
Premium Hands: {summary['hand_strength_premium']:.2%}
Strong Hands: {summary['hand_strength_strong']:.2%}
Medium Hands: {summary['hand_strength_medium']:.2%}
Weak Hands: {summary['hand_strength_weak']:.2%}

== Street Reach Percentages ==
Reached Flop: {summary['reached_flop']:.2%}
Reached Turn: {summary['reached_turn']:.2%}
Reached River: {summary['reached_river']:.2%}

== Pot and Bet Sizing ==
Average Pot Size: {summary['avg_pot_size']:.2f}
Average Bet Size: {summary['avg_bet_size']:.2f}

== Bot Action Distribution ==
"""
        
        # Add bot action distribution
        if "by_player" in action_dist and "Bot" in action_dist["by_player"]:
            bot_actions = action_dist["by_player"]["Bot"]["actions"]
            for action, percentage in bot_actions.items():
                report += f"{action}: {percentage:.2%}\n"
                
        report += "\n== Decision Making by Win Probability ==\n"
        
        # Add decision making by win probability
        if "decisions_by_probability" in win_prob:
            for prob_range, decisions in win_prob["decisions_by_probability"].items():
                report += f"{prob_range}:\n"
                for decision, count in decisions.items():
                    report += f"  {decision}: {count}\n"
                    
        report += "\n== Expected Value by Decision ==\n"
        
        # Add expected value by decision
        if "expected_value_by_decision" in win_prob:
            for decision, ev in win_prob["expected_value_by_decision"].items():
                report += f"{decision}: {ev:.2f}\n"
                
        report += "\n== Hand Category Performance ==\n"
        
        # Add hand category performance
        if "results_by_category" in hand_strength:
            for category, results in hand_strength["results_by_category"].items():
                if results["count"] > 0:
                    report += f"{category}:\n"
                    report += f"  Count: {results['count']}\n"
                    report += f"  Win Rate: {results['win_rate']:.2%}\n"
                    report += f"  Average EV: {results['avg_ev']:.2f}\n"
        
        return report

def main():
    """Main function to run the data summary tool"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract key insights from GeckoBot log data')
    parser.add_argument('--log-dir', default='logs', help='Directory containing log files')
    parser.add_argument('--session', type=int, default=0, help='Session index to analyze (0 = most recent)')
    parser.add_argument('--output', help='Output file path for the report')
    parser.add_argument('--list', action='store_true', help='List available sessions')
    
    args = parser.parse_args()
    
    # Create data summary
    summary = DataSummary(args.log_dir)
    
    # List sessions if requested
    if args.list:
        sessions = summary._load_sessions()
        print(f"Found {len(sessions)} sessions:")
        for i, session in enumerate(sessions):
            print(f"{i}: {session.get('session_id', 'Unknown')} - {session.get('hands_played', 0)} hands, P/L: {session.get('profit_loss', 0)}")
        return
    
    # Generate report
    report = summary.generate_text_report(args.session)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
