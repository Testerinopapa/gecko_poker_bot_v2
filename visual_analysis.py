#!/usr/bin/env python3
"""
GeckoBot Poker - Visual Analysis Tool
This script provides a visual analysis of the poker bot's log data.
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

def generate_ascii_chart(data: Dict[str, int], title: str, width: int = 50):
    """Generate an ASCII bar chart"""
    if not data:
        return f"{title}\n(No data available)"
        
    max_value = max(data.values())
    max_label_length = max(len(str(label)) for label in data.keys())
    
    chart = f"{title}\n"
    chart += "=" * len(title) + "\n"
    
    for label, value in data.items():
        bar_length = int((value / max_value) * width) if max_value > 0 else 0
        chart += f"{label.ljust(max_label_length)} | {('#' * bar_length).ljust(width)} | {value}\n"
    
    return chart

def generate_ascii_table(data: List[Dict[str, Any]], columns: List[str], title: str):
    """Generate an ASCII table"""
    if not data:
        return f"{title}\n(No data available)"
        
    # Calculate column widths
    col_widths = {col: max(len(col), max(len(str(row.get(col, ''))) for row in data)) for col in columns}
    
    # Generate header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    separator = "-+-".join("-" * col_widths[col] for col in columns)
    
    table = f"{title}\n"
    table += "=" * len(title) + "\n"
    table += header + "\n"
    table += separator + "\n"
    
    # Generate rows
    for row in data:
        table += " | ".join(str(row.get(col, '')).ljust(col_widths[col]) for col in columns) + "\n"
    
    return table

def generate_ascii_cards(cards: List[str]):
    """Generate ASCII art for playing cards"""
    if not cards:
        return "(No cards)"
        
    # Define card symbols
    symbols = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
    
    # Generate top row
    top_row = " ".join("┌───┐" for _ in cards)
    
    # Generate rank row
    rank_row = ""
    for card in cards:
        if len(card) < 2:
            rank_row += "│   │ "
            continue
            
        rank = card[0].upper()
        if rank == 'T':
            rank = '10'
            
        rank_row += f"│{rank.ljust(3)}│ "
    
    # Generate suit row
    suit_row = ""
    for card in cards:
        if len(card) < 2:
            suit_row += "│   │ "
            continue
            
        suit = card[-1].lower()
        symbol = symbols.get(suit, ' ')
        suit_row += f"│ {symbol} │ "
    
    # Generate bottom row
    bottom_row = " ".join("└───┘" for _ in cards)
    
    return f"{top_row}\n{rank_row}\n{suit_row}\n{bottom_row}"

def analyze_session(session_index: int = 0, log_dir: str = "logs"):
    """Analyze a specific session with visual output"""
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
    
    # Generate session header
    header = f"GeckoBot Poker Analysis - Session {session.get('session_id', 'Unknown')}"
    print("=" * len(header))
    print(header)
    print("=" * len(header))
    print()
    
    # Generate session summary
    summary = [
        {"Metric": "Hands Played", "Value": session.get('hands_played', 0)},
        {"Metric": "Starting Stack", "Value": session.get('starting_stack', 0)},
        {"Metric": "Ending Stack", "Value": session.get('ending_stack', 0)},
        {"Metric": "Profit/Loss", "Value": session.get('profit_loss', 0)}
    ]
    
    # Calculate win rate
    win_count = 0
    for i in range(len(hands) - 1):
        current_stack = hands[i].get('hero_stack', 0)
        next_stack = hands[i + 1].get('hero_stack', 0)
        if next_stack > current_stack:
            win_count += 1
            
    win_rate = win_count / (len(hands) - 1) if len(hands) > 1 else 0
    summary.append({"Metric": "Win Rate", "Value": f"{win_rate:.2%}"})
    
    print(generate_ascii_table(summary, ["Metric", "Value"], "Session Summary"))
    print()
    
    # Analyze actions
    action_counts = Counter()
    for hand in hands:
        for action in hand.get('actions', []):
            if action.get('player') == 'Bot':
                action_counts[action.get('action', 'unknown')] += 1
    
    print(generate_ascii_chart(action_counts, "Bot Actions"))
    print()
    
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
    
    print("Decisions by Win Probability")
    print("===========================")
    for range_name, decisions in decisions_by_prob.items():
        if decisions:
            print(f"\n{range_name}:")
            print(generate_ascii_chart(decisions, f"Actions with {range_name} Win Probability", 30))
    print()
    
    # Analyze decisions by street
    decisions_by_street = defaultdict(lambda: defaultdict(int))
    
    for hand in hands:
        for street, street_data in hand.get('streets', {}).items():
            for action in street_data.get('actions', []):
                if action.get('player') == 'Bot':
                    action_type = action.get('action', 'unknown')
                    decisions_by_street[street][action_type] += 1
    
    print("Decisions by Street")
    print("==================")
    for street, decisions in decisions_by_street.items():
        if decisions:
            print(f"\n{street}:")
            print(generate_ascii_chart(decisions, f"Actions on {street}", 30))
    print()
    
    # Analyze hand details
    print("Hand Details")
    print("============")
    for i in range(min(5, len(hands))):  # Show details for up to 5 hands
        hand = hands[i]
        print(f"\nHand {hand.get('hand_id', 0)}:")
        
        # Show hole cards
        hole_cards = hand.get('hole_cards', [])
        print("Hole Cards:")
        print(generate_ascii_cards(hole_cards))
        
        # Show community cards
        community_cards = hand.get('community_cards', [])
        print("\nCommunity Cards:")
        print(generate_ascii_cards(community_cards))
        
        # Show pot and stack
        print(f"\nFinal Pot: {hand.get('pot_size', 0)}")
        print(f"Hero Stack: {hand.get('hero_stack', 0)}")
        
        # Show actions
        actions = []
        for action in hand.get('actions', []):
            player = action.get('player', 'Unknown')
            action_type = action.get('action', 'unknown')
            amount = action.get('amount')
            
            if amount is not None:
                actions.append({"Player": player, "Action": action_type, "Amount": amount})
            else:
                actions.append({"Player": player, "Action": action_type, "Amount": ""})
        
        print("\nActions:")
        print(generate_ascii_table(actions, ["Player", "Action", "Amount"], ""))
        print("-" * 50)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visual analysis of GeckoBot log data')
    parser.add_argument('--log-dir', default='logs', help='Directory containing log files')
    parser.add_argument('--session', type=int, default=0, help='Session index to analyze (0 = most recent)')
    parser.add_argument('--list', action='store_true', help='List available sessions')
    
    args = parser.parse_args()
    
    if args.list:
        sessions = load_sessions(args.log_dir)
        print(f"Found {len(sessions)} sessions:")
        for i, session in enumerate(sessions):
            print(f"{i}: {session.get('session_id', 'Unknown')} - {session.get('hands_played', 0)} hands, P/L: {session.get('profit_loss', 0)}")
    else:
        analyze_session(args.session, args.log_dir)

if __name__ == "__main__":
    main()
