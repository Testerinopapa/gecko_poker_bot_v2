#!/usr/bin/env python3
"""
GeckoBot Poker - Simple Analysis Tool
This script provides a simple analysis of the poker bot's log data.
"""

import os
import json
import glob
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

def load_sessions(log_dir: str = "logs") -> List[Dict[str, Any]]:
    """Load all available session data"""
    sessions = []
    data_files = glob.glob(os.path.join(log_dir, "*_data.json"))
    
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

def list_sessions(log_dir: str = "logs"):
    """List all available sessions"""
    sessions = load_sessions(log_dir)
    print(f"Found {len(sessions)} sessions:")
    for i, session in enumerate(sessions):
        print(f"{i}: {session.get('session_id', 'Unknown')} - {session.get('hands_played', 0)} hands, P/L: {session.get('profit_loss', 0)}")

def analyze_session(session_index: int = 0, log_dir: str = "logs"):
    """Analyze a specific session"""
    sessions = load_sessions(log_dir)
    
    if not sessions:
        print("No sessions available")
        return
        
    if session_index >= len(sessions):
        session_index = 0
        
    session = sessions[session_index]
    hands = session.get('hands', [])
    
    if not hands:
        print(f"No hand data available for session {session.get('session_id', 'Unknown')}")
        return
    
    print(f"=== Analysis for Session {session.get('session_id', 'Unknown')} ===")
    print(f"Hands Played: {session.get('hands_played', 0)}")
    print(f"Starting Stack: {session.get('starting_stack', 0)}")
    print(f"Ending Stack: {session.get('ending_stack', 0)}")
    print(f"Profit/Loss: {session.get('profit_loss', 0)}")
    
    # Calculate win rate
    win_count = 0
    for i in range(len(hands) - 1):
        current_stack = hands[i].get('hero_stack', 0)
        next_stack = hands[i + 1].get('hero_stack', 0)
        if next_stack > current_stack:
            win_count += 1
            
    win_rate = win_count / (len(hands) - 1) if len(hands) > 1 else 0
    print(f"Win Rate: {win_rate:.2%}")
    
    # Analyze actions
    action_counts = Counter()
    for hand in hands:
        for action in hand.get('actions', []):
            if action.get('player') == 'Bot':
                action_counts[action.get('action', 'unknown')] += 1
    
    print("\n== Bot Actions ==")
    for action, count in action_counts.items():
        print(f"{action}: {count}")
    
    # Analyze decisions by win probability
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
    
    print("\n== Decisions by Win Probability ==")
    for range_name, decisions in decisions_by_prob.items():
        if decisions:
            print(f"{range_name}:")
            for action, count in decisions.items():
                print(f"  {action}: {count}")
    
    # Analyze decisions by street
    decisions_by_street = defaultdict(lambda: defaultdict(int))
    
    for hand in hands:
        for street, street_data in hand.get('streets', {}).items():
            for action in street_data.get('actions', []):
                if action.get('player') == 'Bot':
                    action_type = action.get('action', 'unknown')
                    decisions_by_street[street][action_type] += 1
    
    print("\n== Decisions by Street ==")
    for street, decisions in decisions_by_street.items():
        print(f"{street}:")
        for action, count in decisions.items():
            print(f"  {action}: {count}")
    
    # Analyze hand outcomes
    print("\n== Hand Details ==")
    for i in range(min(5, len(hands))):  # Show details for up to 5 hands
        hand = hands[i]
        print(f"\nHand {hand.get('hand_id', 0)}:")
        print(f"Hole Cards: {' '.join(hand.get('hole_cards', []))}")
        print(f"Community Cards: {' '.join(hand.get('community_cards', []))}")
        print(f"Final Pot: {hand.get('pot_size', 0)}")
        print(f"Hero Stack: {hand.get('hero_stack', 0)}")
        
        # Show actions
        print("Actions:")
        for action in hand.get('actions', []):
            player = action.get('player', 'Unknown')
            action_type = action.get('action', 'unknown')
            amount = action.get('amount')
            if amount is not None:
                print(f"  {player} {action_type} {amount}")
            else:
                print(f"  {player} {action_type}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple analysis of GeckoBot log data')
    parser.add_argument('--log-dir', default='logs', help='Directory containing log files')
    parser.add_argument('--session', type=int, default=0, help='Session index to analyze (0 = most recent)')
    parser.add_argument('--list', action='store_true', help='List available sessions')
    
    args = parser.parse_args()
    
    if args.list:
        list_sessions(args.log_dir)
    else:
        analyze_session(args.session, args.log_dir)

if __name__ == "__main__":
    main()
