#!/usr/bin/env python3
"""
GeckoBot Poker - Analysis Suite
This script provides a unified interface to all the analysis tools.
"""

import os
import argparse
import webbrowser
from data_dashboard import DashboardGenerator
from data_summary import DataSummary
from performance_analyzer import PerformanceAnalyzer

def main():
    """Main function to run the analysis suite"""
    parser = argparse.ArgumentParser(description='GeckoBot Poker Analysis Suite')
    parser.add_argument('--log-dir', default='logs', help='Directory containing log files')
    parser.add_argument('--session', type=int, default=0, help='Session index to analyze (0 = most recent)')
    parser.add_argument('--dashboard', action='store_true', help='Generate interactive dashboard')
    parser.add_argument('--summary', action='store_true', help='Generate text summary')
    parser.add_argument('--metrics', action='store_true', help='Show performance metrics')
    parser.add_argument('--patterns', action='store_true', help='Show decision patterns')
    parser.add_argument('--export', help='Export decision data to CSV file')
    parser.add_argument('--list', action='store_true', help='List available sessions')
    parser.add_argument('--all', action='store_true', help='Run all analysis tools')
    
    args = parser.parse_args()
    
    # If no specific tool is selected, show help
    if not any([args.dashboard, args.summary, args.metrics, args.patterns, args.export, args.list, args.all]):
        parser.print_help()
        return
    
    # List available sessions
    if args.list:
        summary = DataSummary(args.log_dir)
        sessions = summary._load_sessions()
        print(f"Found {len(sessions)} sessions:")
        for i, session in enumerate(sessions):
            print(f"{i}: {session.get('session_id', 'Unknown')} - {session.get('hands_played', 0)} hands, P/L: {session.get('profit_loss', 0)}")
        return
    
    # Generate dashboard
    if args.dashboard or args.all:
        print("Generating interactive dashboard...")
        generator = DashboardGenerator(args.log_dir)
        output_path = generator.generate_dashboard(args.session)
        print(f"Dashboard generated: {output_path}")
        
        # Open in browser
        try:
            webbrowser.open(f"file://{os.path.abspath(output_path)}")
            print("Dashboard opened in browser")
        except:
            print(f"Please open the dashboard manually: {output_path}")
    
    # Generate text summary
    if args.summary or args.all:
        print("\nGenerating text summary...")
        summary = DataSummary(args.log_dir)
        report = summary.generate_text_report(args.session)
        print(report)
    
    # Show performance metrics
    if args.metrics or args.all:
        print("\nAnalyzing performance metrics...")
        analyzer = PerformanceAnalyzer(args.log_dir)
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
    
    # Show decision patterns
    if args.patterns or args.all:
        print("\nAnalyzing decision patterns...")
        analyzer = PerformanceAnalyzer(args.log_dir)
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
    
    # Export decision data
    if args.export or args.all:
        print("\nExporting decision data...")
        analyzer = PerformanceAnalyzer(args.log_dir)
        output_file = args.export if args.export else os.path.join(args.log_dir, "decision_data.csv")
        analyzer.export_decision_data(output_file, args.session)

if __name__ == "__main__":
    main()
