"""
GeckoBot Poker - Log Analyzer
This module provides tools to analyze the logs generated by the GeckoBot poker bot.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# Try to import optional dependencies
try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

class LogAnalyzer:
    """
    Analyzes GeckoBot poker logs to extract insights and statistics
    """
    def __init__(self, log_dir: str = "logs", session_id: Optional[str] = None):
        self.log_dir = log_dir
        self.session_id = session_id
        self.data = None
        self.text_logs = None

        if session_id:
            self.load_session(session_id)
        else:
            # Load the most recent session
            self._load_most_recent_session()

    def _load_most_recent_session(self):
        """Load the most recent session data"""
        data_files = [f for f in os.listdir(self.log_dir) if f.endswith('_data.json')]
        if not data_files:
            print("No session data files found")
            return

        # Sort by timestamp in filename
        data_files.sort(reverse=True)
        # Extract session ID from filename (geckobot_SESSIONID_data.json)
        filename_parts = data_files[0].split('_')
        if len(filename_parts) >= 3:
            self.session_id = filename_parts[1]
        else:
            print(f"Unexpected filename format: {data_files[0]}")
            return

        self.load_session(self.session_id)

    def load_session(self, session_id: str):
        """Load a specific session by ID"""
        # Find all files that match the session ID pattern
        matching_files = [f for f in os.listdir(self.log_dir) if session_id in f]

        # Look for data file
        data_files = [f for f in matching_files if f.endswith('_data.json')]
        if data_files:
            data_file = os.path.join(self.log_dir, data_files[0])
            try:
                with open(data_file, 'r') as f:
                    self.data = json.load(f)
                    print(f"Loaded session data from {data_files[0]}")
            except Exception as e:
                print(f"Error loading data file: {e}")
        else:
            print(f"No data file found for session {session_id}")

        # Look for log file
        log_files = [f for f in matching_files if f.endswith('.log') and not f.endswith('_structured.log')]
        if log_files:
            log_file = os.path.join(self.log_dir, log_files[0])
            try:
                with open(log_file, 'r') as f:
                    self.text_logs = f.readlines()
                    print(f"Loaded text logs from {log_files[0]}")
            except Exception as e:
                print(f"Error loading log file: {e}")
        else:
            print(f"No log file found for session {session_id}")

    def list_available_sessions(self):
        """List all available sessions"""
        data_files = [f for f in os.listdir(self.log_dir) if f.endswith('_data.json')]
        sessions = []

        for file in data_files:
            # Extract session ID from filename
            parts = file.split('_')
            if len(parts) >= 3 and parts[0] == 'geckobot':
                session_id = parts[1]
                try:
                    with open(os.path.join(self.log_dir, file), 'r') as f:
                        data = json.load(f)
                        # Try to parse the date from the session ID
                        try:
                            date_str = datetime.strptime(session_id, "%Y%m%d").strftime("%Y-%m-%d")
                        except:
                            date_str = "Unknown date"

                        sessions.append({
                            "session_id": session_id,
                            "filename": file,
                            "hands_played": data.get("hands_played", 0),
                            "profit_loss": data.get("profit_loss", 0),
                            "date": date_str
                        })
                except Exception as e:
                    print(f"Error processing {file}: {e}")
                    continue

        # Return as list of dictionaries if pandas is not available
        try:
            import pandas as pd
            return pd.DataFrame(sessions)
        except ImportError:
            return sessions

    def get_session_summary(self):
        """Get a summary of the session"""
        if not self.data:
            return "No session data loaded"

        # Try to parse date from session ID
        try:
            if '_' in self.session_id:
                date_str = datetime.strptime(self.session_id, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = datetime.strptime(self.session_id, "%Y%m%d").strftime("%Y-%m-%d")
        except ValueError:
            date_str = "Unknown date"

        summary = {
            "Session ID": self.session_id,
            "Date": date_str,
            "Hands Played": self.data.get("hands_played", 0),
            "Starting Stack": self.data.get("starting_stack", 0),
            "Ending Stack": self.data.get("ending_stack", 0),
            "Profit/Loss": self.data.get("profit_loss", 0),
            "Duration (seconds)": self.data.get("duration", 0)
        }

        # Return as dict if pandas is not available
        if pd is None:
            return summary

        try:
            return pd.Series(summary)
        except Exception:
            return summary

    def get_hand_data(self, hand_id: Optional[int] = None):
        """Get data for a specific hand or all hands"""
        if not self.data or "hands" not in self.data:
            return "No hand data available"

        if hand_id is not None:
            for hand in self.data["hands"]:
                if hand.get("hand_id") == hand_id:
                    return hand
            return f"Hand {hand_id} not found"

        return self.data["hands"]

    def get_action_frequencies(self):
        """Get frequency of different actions taken by the bot"""
        if not self.data or "hands" not in self.data:
            return "No hand data available"

        actions = []
        for hand in self.data["hands"]:
            for action in hand.get("actions", []):
                if action.get("player") == "Bot":
                    actions.append(action.get("action"))

        if not actions:
            return "No bot actions found"

        return pd.Series(actions).value_counts()

    def plot_stack_progression(self):
        """Plot the progression of the hero's stack over time"""
        if not self.data or "hands" not in self.data:
            return "No hand data available"

        stacks = []
        hand_ids = []

        for hand in self.data["hands"]:
            hand_ids.append(hand.get("hand_id", 0))
            stacks.append(hand.get("hero_stack", 0))

        if not stacks:
            return "No stack data found"

        # Check if matplotlib is available
        if plt is None:
            return "Matplotlib not available. Stack data: " + str(list(zip(hand_ids, stacks)))

        try:
            plt.figure(figsize=(12, 6))
            plt.plot(hand_ids, stacks, marker='o')
            plt.title('Stack Progression Over Time')
            plt.xlabel('Hand Number')
            plt.ylabel('Stack Size')
            plt.grid(True)
            output_file = os.path.join(self.log_dir, f"stack_progression_{self.session_id}.png")
            plt.savefig(output_file)
            plt.close()

            return output_file
        except Exception as e:
            return f"Error generating plot: {e}"

    def plot_win_probabilities(self):
        """Plot the win probabilities across different streets"""
        if not self.data or "hands" not in self.data:
            return "No hand data available"

        preflop_probs = []
        flop_probs = []
        turn_probs = []
        river_probs = []
        hand_ids = []

        for hand in self.data["hands"]:
            hand_id = hand.get("hand_id", 0)
            hand_ids.append(hand_id)

            streets = hand.get("streets", {})
            preflop_probs.append(streets.get("PREFLOP", {}).get("win_probability", 0))
            flop_probs.append(streets.get("FLOP", {}).get("win_probability", 0))
            turn_probs.append(streets.get("TURN", {}).get("win_probability", 0))
            river_probs.append(streets.get("RIVER", {}).get("win_probability", 0))

        # Check if matplotlib is available
        if plt is None:
            return "Matplotlib not available. Win probability data available in raw format."

        try:
            plt.figure(figsize=(12, 6))
            plt.plot(hand_ids, preflop_probs, marker='o', label='Preflop')
            plt.plot(hand_ids, flop_probs, marker='s', label='Flop')
            plt.plot(hand_ids, turn_probs, marker='^', label='Turn')
            plt.plot(hand_ids, river_probs, marker='*', label='River')
            plt.title('Win Probabilities Across Streets')
            plt.xlabel('Hand Number')
            plt.ylabel('Win Probability')
            plt.legend()
            plt.grid(True)
            output_file = os.path.join(self.log_dir, f"win_probabilities_{self.session_id}.png")
            plt.savefig(output_file)
            plt.close()

            return output_file
        except Exception as e:
            return f"Error generating plot: {e}"

    def extract_hand_text(self, hand_id: int):
        """Extract the full text log for a specific hand"""
        if not self.text_logs:
            return "No text logs available"

        hand_start_pattern = re.compile(f"=== Hand {hand_id} Started ===")
        hand_end_pattern = re.compile(f"=== Hand {hand_id} Complete ===")

        in_hand = False
        hand_text = []

        for line in self.text_logs:
            if hand_start_pattern.search(line):
                in_hand = True
                hand_text.append(line)
            elif in_hand:
                hand_text.append(line)
                if hand_end_pattern.search(line):
                    break

        return "".join(hand_text)

    def analyze_decision_making(self):
        """Analyze the bot's decision making patterns"""
        if not self.data or "hands" not in self.data:
            return "No hand data available"

        decisions = []

        for hand in self.data["hands"]:
            for street, street_data in hand.get("streets", {}).items():
                for action in street_data.get("actions", []):
                    if action.get("player") == "Bot":
                        decisions.append({
                            "hand_id": hand.get("hand_id"),
                            "street": street,
                            "action": action.get("action"),
                            "amount": action.get("amount"),
                            "win_probability": street_data.get("win_probability", 0)
                        })

        if not decisions:
            return "No decision data found"

        # Check if pandas is available
        if pd is None:
            # Simple analysis without pandas
            action_counts = {}
            for decision in decisions:
                action = decision.get("action")
                prob = decision.get("win_probability", 0)
                prob_range = "0-20%" if prob < 0.2 else \
                             "20-40%" if prob < 0.4 else \
                             "40-60%" if prob < 0.6 else \
                             "60-80%" if prob < 0.8 else \
                             "80-100%"

                key = (prob_range, action)
                action_counts[key] = action_counts.get(key, 0) + 1

            return action_counts

        try:
            df = pd.DataFrame(decisions)

            # Group by action and win probability range
            df["win_prob_range"] = pd.cut(df["win_probability"],
                                         bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                         labels=["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"])

            action_by_prob = pd.crosstab(df["win_prob_range"], df["action"])

            return action_by_prob
        except Exception as e:
            return f"Error analyzing decisions: {e}"

    def generate_report(self, output_file: Optional[str] = None):
        """Generate a comprehensive analysis report"""
        if not self.data:
            return "No session data loaded"

        if output_file is None:
            output_file = os.path.join(self.log_dir, f"report_{self.session_id}.html")

        # Generate plots
        self.plot_stack_progression()
        self.plot_win_probabilities()

        # Create report content
        summary = self.get_session_summary()
        action_freq = self.get_action_frequencies()
        decision_analysis = self.analyze_decision_making()

        # Build HTML report
        html = f"""
        <html>
        <head>
            <title>GeckoBot Poker Analysis - Session {self.session_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .summary {{ display: flex; justify-content: space-between; }}
                .summary-item {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px; flex: 1; }}
                .chart {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>GeckoBot Poker Analysis Report</h1>
                <h2>Session Summary</h2>
                <div class="summary">
                    <div class="summary-item">
                        <h3>Session ID</h3>
                        <p>{summary['Session ID']}</p>
                    </div>
                    <div class="summary-item">
                        <h3>Date</h3>
                        <p>{summary['Date']}</p>
                    </div>
                    <div class="summary-item">
                        <h3>Hands Played</h3>
                        <p>{summary['Hands Played']}</p>
                    </div>
                    <div class="summary-item">
                        <h3>Profit/Loss</h3>
                        <p>{summary['Profit/Loss']}</p>
                    </div>
                </div>

                <h2>Stack Progression</h2>
                <div class="chart">
                    <img src="stack_progression_{self.session_id}.png" alt="Stack Progression" style="width: 100%;">
                </div>

                <h2>Win Probabilities</h2>
                <div class="chart">
                    <img src="win_probabilities_{self.session_id}.png" alt="Win Probabilities" style="width: 100%;">
                </div>

                <h2>Action Frequencies</h2>
                <table>
                    <tr>
                        <th>Action</th>
                        <th>Count</th>
                    </tr>
                    {"".join(f"<tr><td>{action}</td><td>{count}</td></tr>" for action, count in action_freq.items())}
                </table>

                <h2>Decision Analysis</h2>
                <table>
                    <tr>
                        <th>Win Probability</th>
                        {"".join(f"<th>{col}</th>" for col in decision_analysis.columns)}
                    </tr>
                    {"".join(f"<tr><td>{idx}</td>{''.join(f'<td>{val}</td>' for val in row)}</tr>" for idx, row in zip(decision_analysis.index, decision_analysis.values))}
                </table>

                <h2>Hand Details</h2>
                {"".join(f"<h3>Hand {hand['hand_id']}</h3><p>Hole cards: {' '.join(hand['hole_cards']) if hand.get('hole_cards') else 'N/A'}</p><p>Final pot: {hand.get('final_pot', 'N/A')}</p>" for hand in self.data['hands'])}
            </div>
        </body>
        </html>
        """

        with open(output_file, 'w') as f:
            f.write(html)

        return f"Report generated: {output_file}"

def main():
    """Command line interface for the log analyzer"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze GeckoBot poker logs")
    parser.add_argument("--log-dir", default="logs", help="Directory containing log files")
    parser.add_argument("--session", help="Specific session ID to analyze")
    parser.add_argument("--list", action="store_true", help="List available sessions")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    analyzer = LogAnalyzer(args.log_dir, args.session)

    if args.list:
        sessions = analyzer.list_available_sessions()
        print(sessions)
        return

    if args.report:
        report_path = analyzer.generate_report(args.output)
        print(f"Report generated: {report_path}")
        return

    # Default behavior: print session summary
    print(analyzer.get_session_summary())

if __name__ == "__main__":
    main()
