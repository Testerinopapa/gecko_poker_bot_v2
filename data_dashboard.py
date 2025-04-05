#!/usr/bin/env python3
"""
GeckoBot Poker - Data Dashboard Generator
This module creates interactive visualizations from the poker bot's log data.
"""

import os
import json
import glob
from datetime import datetime
import webbrowser
from typing import Dict, List, Any, Optional

# Try to import optional dependencies
try:
    import pandas as pd
except ImportError:
    pd = None

class DashboardGenerator:
    """
    Generates interactive dashboards from GeckoBot log data
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

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions with summary info"""
        return [
            {
                'session_id': session.get('session_id', 'Unknown'),
                'hands_played': session.get('hands_played', 0),
                'profit_loss': session.get('profit_loss', 0),
                'duration': session.get('duration', 0),
                'file_path': session.get('file_path', '')
            }
            for session in self.sessions
        ]

    def generate_dashboard(self, session_index: int = 0, output_path: Optional[str] = None) -> str:
        """Generate an interactive dashboard for the specified session"""
        if not self.sessions:
            return "No sessions available"

        if session_index >= len(self.sessions):
            session_index = 0

        session = self.sessions[session_index]

        if output_path is None:
            output_path = os.path.join(self.log_dir, f"dashboard_{session.get('session_id', 'unknown')}.html")

        # Generate HTML content
        html_content = self._generate_html(session)

        # Write to file
        with open(output_path, 'w') as f:
            f.write(html_content)

        return output_path

    def _generate_html(self, session: Dict[str, Any]) -> str:
        """Generate HTML content for the dashboard"""
        session_id = session.get('session_id', 'Unknown')
        hands = session.get('hands', [])

        # Extract hand data for visualization
        hand_data = []
        for hand in hands:
            hand_data.append({
                'hand_id': hand.get('hand_id', 0),
                'hole_cards': ' '.join(hand.get('hole_cards', [])),
                'community_cards': ' '.join(hand.get('community_cards', [])),
                'pot_size': hand.get('pot_size', 0),
                'hero_stack': hand.get('hero_stack', 0),
                'actions': len(hand.get('actions', [])),
                'win_probability': self._get_final_win_probability(hand),
                'streets': list(hand.get('streets', {}).keys()),
                'duration': hand.get('end_time', 0) - hand.get('start_time', 0) if 'end_time' in hand and 'start_time' in hand else 0
            })

        # Generate decision data
        decision_data = self._extract_decision_data(hands)

        # Generate HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeckoBot Poker Dashboard - Session {session_id}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
            margin-bottom: 20px;
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
            margin-bottom: 20px;
        }}
        .card-header {{
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 15px;
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stat-card {{
            background-color: #f9f9f9;
            border-radius: 5px;
            padding: 15px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
            color: #2980b9;
        }}
        .stat-label {{
            font-size: 14px;
            color: #7f8c8d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .chart-container {{
            position: relative;
            height: 300px;
            margin-top: 15px;
        }}
        .tabs {{
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 15px;
        }}
        .tab {{
            padding: 10px 15px;
            cursor: pointer;
            background-color: #f2f2f2;
            border: 1px solid #ddd;
            border-bottom: none;
            margin-right: 5px;
            border-radius: 5px 5px 0 0;
        }}
        .tab.active {{
            background-color: white;
            border-bottom: 1px solid white;
            margin-bottom: -1px;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .hand-card {{
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 15px;
            margin-bottom: 15px;
        }}
        .hand-header {{
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }}
        .hand-title {{
            font-weight: bold;
            font-size: 16px;
        }}
        .hand-result {{
            font-weight: bold;
        }}
        .hand-result.win {{
            color: #27ae60;
        }}
        .hand-result.loss {{
            color: #e74c3c;
        }}
        .hand-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 10px;
        }}
        .hand-detail {{
            font-size: 14px;
        }}
        .hand-detail-label {{
            font-weight: bold;
            color: #7f8c8d;
            margin-bottom: 5px;
        }}
        .hand-actions {{
            margin-top: 10px;
        }}
        .action-item {{
            padding: 5px 0;
            border-bottom: 1px solid #f5f5f5;
            font-size: 14px;
        }}
        .action-player {{
            font-weight: bold;
            margin-right: 5px;
        }}
        .action-type {{
            color: #7f8c8d;
        }}
        .action-amount {{
            float: right;
            color: #e74c3c;
        }}
        .card-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 5px;
        }}
        .playing-card {{
            width: 40px;
            height: 60px;
            background-color: white;
            border-radius: 5px;
            border: 1px solid #ddd;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            font-size: 16px;
            position: relative;
        }}
        .playing-card.hearts, .playing-card.diamonds {{
            color: #e74c3c;
        }}
        .playing-card.clubs, .playing-card.spades {{
            color: #2c3e50;
        }}
        .playing-card::after {{
            position: absolute;
            bottom: 5px;
            right: 5px;
            font-size: 12px;
        }}
        .playing-card.hearts::after {{
            content: "♥";
        }}
        .playing-card.diamonds::after {{
            content: "♦";
        }}
        .playing-card.clubs::after {{
            content: "♣";
        }}
        .playing-card.spades::after {{
            content: "♠";
        }}
        .pagination {{
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }}
        .pagination-button {{
            padding: 8px 15px;
            background-color: #2c3e50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 5px;
        }}
        .pagination-button:disabled {{
            background-color: #95a5a6;
            cursor: not-allowed;
        }}
        .search-bar {{
            margin-bottom: 20px;
        }}
        .search-input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GeckoBot Poker Dashboard</h1>
        <p>Session: {session_id} - {len(hands)} Hands Played</p>
    </div>

    <div class="container">
        <!-- Session Summary -->
        <div class="card">
            <div class="card-header">Session Summary</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Hands Played</div>
                    <div class="stat-value">{session.get('hands_played', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Starting Stack</div>
                    <div class="stat-value">{session.get('starting_stack', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Ending Stack</div>
                    <div class="stat-value">{session.get('ending_stack', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Profit/Loss</div>
                    <div class="stat-value" style="color: {'#27ae60' if session.get('profit_loss', 0) >= 0 else '#e74c3c'}">
                        {session.get('profit_loss', 0)}
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Duration</div>
                    <div class="stat-value">{session.get('duration', 0):.2f}s</div>
                </div>
            </div>
        </div>

        <!-- Dashboard Grid -->
        <div class="dashboard-grid">
            <!-- Stack Progression -->
            <div class="card">
                <div class="card-header">Stack Progression</div>
                <div class="chart-container">
                    <canvas id="stackChart"></canvas>
                </div>
            </div>

            <!-- Win Probabilities -->
            <div class="card">
                <div class="card-header">Win Probabilities</div>
                <div class="chart-container">
                    <canvas id="winProbChart"></canvas>
                </div>
            </div>

            <!-- Decision Analysis -->
            <div class="card">
                <div class="card-header">Decision Analysis</div>
                <div class="chart-container">
                    <canvas id="decisionChart"></canvas>
                </div>
            </div>

            <!-- Action Distribution -->
            <div class="card">
                <div class="card-header">Action Distribution</div>
                <div class="chart-container">
                    <canvas id="actionChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Hand History -->
        <div class="card">
            <div class="card-header">Hand History</div>
            <div class="search-bar">
                <input type="text" class="search-input" id="handSearch" placeholder="Search hands...">
            </div>
            <div id="handContainer">
                <!-- Hand cards will be inserted here by JavaScript -->
            </div>
            <div class="pagination">
                <button class="pagination-button" id="prevPage" disabled>Previous</button>
                <span id="pageInfo">Page 1 of 1</span>
                <button class="pagination-button" id="nextPage" disabled>Next</button>
            </div>
        </div>
    </div>

    <script>
        // Hand data from Python
        const handData = {json.dumps(hand_data)};
        const sessionData = {json.dumps({
            'hands_played': session.get('hands_played', 0),
            'starting_stack': session.get('starting_stack', 0),
            'ending_stack': session.get('ending_stack', 0),
            'profit_loss': session.get('profit_loss', 0),
            'duration': session.get('duration', 0)
        })};
        const decisionData = {json.dumps(decision_data)};

        // Stack progression chart
        const stackCtx = document.getElementById('stackChart').getContext('2d');
        const stackChart = new Chart(stackCtx, {{
            type: 'line',
            data: {{
                labels: handData.map(hand => `Hand ${hand.hand_id}`),
                datasets: [{{
                    label: 'Stack Size',
                    data: handData.map(hand => hand.hero_stack),
                    borderColor: '#2980b9',
                    backgroundColor: 'rgba(41, 128, 185, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: false
                    }}
                }}
            }}
        }});

        // Win probability chart
        const winProbCtx = document.getElementById('winProbChart').getContext('2d');
        const winProbChart = new Chart(winProbCtx, {{
            type: 'line',
            data: {{
                labels: handData.map(hand => `Hand ${hand.hand_id}`),
                datasets: [{{
                    label: 'Win Probability',
                    data: handData.map(hand => hand.win_probability),
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1,
                        ticks: {{
                            callback: function(value) {{
                                return (value * 100) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Decision analysis chart
        const decisionCtx = document.getElementById('decisionChart').getContext('2d');
        const decisionLabels = Object.keys(decisionData.by_probability);
        const decisionDatasets = [];

        const actionTypes = [...new Set(Object.values(decisionData.by_probability).flatMap(Object.keys))];
        const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c'];

        actionTypes.forEach((action, index) => {{
            const data = decisionLabels.map(prob => decisionData.by_probability[prob][action] || 0);
            decisionDatasets.push({{
                label: action,
                data: data,
                backgroundColor: colors[index % colors.length]
            }});
        }});

        const decisionChart = new Chart(decisionCtx, {{
            type: 'bar',
            data: {{
                labels: decisionLabels.map(label => label + ' Win Prob'),
                datasets: decisionDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        stacked: true
                    }},
                    y: {{
                        stacked: true,
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // Action distribution chart
        const actionCtx = document.getElementById('actionChart').getContext('2d');
        const actionChart = new Chart(actionCtx, {{
            type: 'pie',
            data: {{
                labels: Object.keys(decisionData.by_action),
                datasets: [{{
                    data: Object.values(decisionData.by_action),
                    backgroundColor: colors.slice(0, Object.keys(decisionData.by_action).length)
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right'
                    }}
                }}
            }}
        }});

        // Hand history pagination
        const handsPerPage = 5;
        let currentPage = 1;
        const totalPages = Math.ceil(handData.length / handsPerPage);

        function renderHands(page, filterText = '') {{
            const handContainer = document.getElementById('handContainer');
            handContainer.innerHTML = '';

            const filteredHands = filterText
                ? handData.filter(hand =>
                    hand.hole_cards.toLowerCase().includes(filterText.toLowerCase()) ||
                    hand.community_cards.toLowerCase().includes(filterText.toLowerCase()) ||
                    hand.hand_id.toString().includes(filterText)
                )
                : handData;

            const startIndex = (page - 1) * handsPerPage;
            const endIndex = Math.min(startIndex + handsPerPage, filteredHands.length);

            if (filteredHands.length === 0) {{
                handContainer.innerHTML = '<p>No hands match your search criteria.</p>';
                return;
            }}

            for (let i = startIndex; i < endIndex; i++) {{
                const hand = filteredHands[i];
                const handCard = document.createElement('div');
                handCard.className = 'hand-card';

                // Determine if hand was a win or loss
                const isLastHand = i === filteredHands.length - 1;
                const nextHand = !isLastHand ? filteredHands[i + 1] : null;
                const stackChange = nextHand ? nextHand.hero_stack - hand.hero_stack : 0;
                const resultClass = stackChange > 0 ? 'win' : stackChange < 0 ? 'loss' : '';

                handCard.innerHTML = `
                    <div class="hand-header">
                        <div class="hand-title">Hand #${hand.hand_id}</div>
                        <div class="hand-result ${resultClass}">
                            ${stackChange > 0 ? '+' + stackChange : stackChange}
                        </div>
                    </div>
                    <div class="hand-details">
                        <div class="hand-detail">
                            <div class="hand-detail-label">Hole Cards</div>
                            <div class="card-grid">
                                ${renderCards(hand.hole_cards)}
                            </div>
                        </div>
                        <div class="hand-detail">
                            <div class="hand-detail-label">Community Cards</div>
                            <div class="card-grid">
                                ${renderCards(hand.community_cards)}
                            </div>
                        </div>
                        <div class="hand-detail">
                            <div class="hand-detail-label">Win Probability</div>
                            ${(hand.win_probability * 100).toFixed(2)}%
                        </div>
                        <div class="hand-detail">
                            <div class="hand-detail-label">Pot Size</div>
                            ${hand.pot_size}
                        </div>
                    </div>
                `;

                handContainer.appendChild(handCard);
            }}

            // Update pagination
            document.getElementById('prevPage').disabled = page === 1 || filteredHands.length === 0;
            document.getElementById('nextPage').disabled = page >= Math.ceil(filteredHands.length / handsPerPage) || filteredHands.length === 0;
            document.getElementById('pageInfo').textContent = `Page ${page} of ${Math.max(1, Math.ceil(filteredHands.length / handsPerPage))}`;
        }}

        function renderCards(cardString) {{
            if (!cardString) return '';

            const cards = cardString.split(' ');
            let html = '';

            cards.forEach(card => {{
                if (!card) return;

                const rank = card.slice(0, -1);
                const suit = card.slice(-1).toLowerCase();

                let suitClass = '';
                switch (suit) {{
                    case 'h': suitClass = 'hearts'; break;
                    case 'd': suitClass = 'diamonds'; break;
                    case 'c': suitClass = 'clubs'; break;
                    case 's': suitClass = 'spades'; break;
                }}

                html += `<div class="playing-card ${suitClass}">${rank}</div>`;
            }});

            return html;
        }}

        // Initialize hand display
        renderHands(currentPage);

        // Pagination event listeners
        document.getElementById('prevPage').addEventListener('click', () => {{
            if (currentPage > 1) {{
                currentPage--;
                renderHands(currentPage, document.getElementById('handSearch').value);
            }}
        }});

        document.getElementById('nextPage').addEventListener('click', () => {{
            if (currentPage < totalPages) {{
                currentPage++;
                renderHands(currentPage, document.getElementById('handSearch').value);
            }}
        }});

        // Search functionality
        document.getElementById('handSearch').addEventListener('input', (e) => {{
            currentPage = 1;
            renderHands(currentPage, e.target.value);
        }});
    </script>
</body>
</html>
        """

        return html

    def _get_final_win_probability(self, hand: Dict[str, Any]) -> float:
        """Get the final win probability from the hand data"""
        streets = hand.get('streets', {})

        # Check streets in order: RIVER, TURN, FLOP, PREFLOP
        for street in ['RIVER', 'TURN', 'FLOP', 'PREFLOP']:
            if street in streets and 'win_probability' in streets[street]:
                return streets[street]['win_probability']

        return 0.0

    def _extract_decision_data(self, hands: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract decision data for visualization"""
        by_action = {}
        by_probability = {
            '0-20%': {},
            '20-40%': {},
            '40-60%': {},
            '60-80%': {},
            '80-100%': {}
        }

        for hand in hands:
            for action in hand.get('actions', []):
                if action.get('player') == 'Bot':
                    # Count by action type
                    action_type = action.get('action', 'unknown')
                    by_action[action_type] = by_action.get(action_type, 0) + 1

                    # Find the street this action was made on
                    for street, street_data in hand.get('streets', {}).items():
                        if action in street_data.get('actions', []):
                            # Get win probability for this street
                            win_prob = street_data.get('win_probability', 0)

                            # Determine probability bucket
                            prob_bucket = '0-20%' if win_prob < 0.2 else \
                                         '20-40%' if win_prob < 0.4 else \
                                         '40-60%' if win_prob < 0.6 else \
                                         '60-80%' if win_prob < 0.8 else \
                                         '80-100%'

                            # Count by probability and action
                            if action_type not in by_probability[prob_bucket]:
                                by_probability[prob_bucket][action_type] = 0
                            by_probability[prob_bucket][action_type] += 1

                            break

        return {
            'by_action': by_action,
            'by_probability': by_probability
        }

def main():
    """Main function to run the dashboard generator"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate interactive dashboards from GeckoBot log data')
    parser.add_argument('--log-dir', default='logs', help='Directory containing log files')
    parser.add_argument('--session', type=int, default=0, help='Session index to visualize (0 = most recent)')
    parser.add_argument('--output', help='Output file path for the dashboard')
    parser.add_argument('--list', action='store_true', help='List available sessions')

    args = parser.parse_args()

    # Create dashboard generator
    generator = DashboardGenerator(args.log_dir)

    # List sessions if requested
    if args.list:
        sessions = generator.list_sessions()
        print(f"Found {len(sessions)} sessions:")
        for i, session in enumerate(sessions):
            print(f"{i}: {session['session_id']} - {session['hands_played']} hands, P/L: {session['profit_loss']}")
        return

    # Generate dashboard
    output_path = generator.generate_dashboard(args.session, args.output)
    print(f"Dashboard generated: {output_path}")

    # Open in browser
    try:
        webbrowser.open(f"file://{os.path.abspath(output_path)}")
        print("Dashboard opened in browser")
    except:
        print(f"Please open the dashboard manually: {output_path}")

if __name__ == "__main__":
    main()
