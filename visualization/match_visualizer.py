import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict
from dataclasses import dataclass
from poker_enums import Street, Position, Action

@dataclass
class HandData:
    """Data structure to store per-hand information"""
    hand_id: int
    hole_cards: tuple
    position: Position
    initial_stack: float
    final_stack: float
    win_probability: Dict[Street, float]
    actions: Dict[Street, List[Action]]
    community_cards: Dict[Street, List[str]]
    pot_sizes: Dict[Street, float]
    final_pot: float
    result: float  # Profit/loss for this hand
    outs_count: Dict[Street, float] = None  # Number of outs by street
    equity_from_outs: Dict[Street, float] = None  # Equity from outs by street

class MatchVisualizer:
    def __init__(self):
        self.hand_history: List[HandData] = []

    def add_hand(self, hand_data: HandData):
        """Add a hand to the visualization history"""
        self.hand_history.append(hand_data)

    def plot_stack_progression(self):
        """Plot stack size over time"""
        stacks = [h.final_stack for h in self.hand_history]
        hands = range(1, len(stacks) + 1)

        plt.figure(figsize=(12, 6))
        plt.plot(hands, stacks, marker='o')
        plt.title('Stack Progression Over Time')
        plt.xlabel('Hand Number')
        plt.ylabel('Stack Size')
        plt.grid(True)
        plt.savefig('stack_progression.png')
        plt.close()

    def plot_win_probabilities(self):
        """Plot win probabilities by street"""
        data = []
        streets = [Street.PREFLOP, Street.FLOP, Street.TURN, Street.RIVER]

        for hand in self.hand_history:
            for street in streets:
                if street in hand.win_probability:
                    data.append({
                        'Hand': hand.hand_id,
                        'Street': street.name,
                        'Win Probability': hand.win_probability[street]
                    })

        df = pd.DataFrame(data)
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='Street', y='Win Probability', data=df)
        plt.title('Win Probabilities by Street')
        plt.savefig('win_probabilities.png')
        plt.close()

    def plot_position_performance(self):
        """Plot performance by position"""
        position_results = {}
        for hand in self.hand_history:
            if hand.position not in position_results:
                position_results[hand.position] = []
            position_results[hand.position].append(hand.result)

        positions = list(position_results.keys())
        avg_results = [sum(results)/len(results) for results in position_results.values()]

        plt.figure(figsize=(10, 6))
        sns.barplot(x=[p.name for p in positions], y=avg_results)
        plt.title('Average Profit/Loss by Position')
        plt.ylabel('BB/hand')
        plt.savefig('position_performance.png')
        plt.close()

    def plot_action_frequencies(self):
        """Plot action frequencies by street"""
        data = []
        for hand in self.hand_history:
            for street, actions in hand.actions.items():
                for action in actions:
                    data.append({
                        'Street': street.name,
                        'Action': action.name,
                        'Count': 1
                    })

        if not data:  # No actions recorded
            plt.figure(figsize=(12, 8))
            plt.text(0.5, 0.5, 'No actions recorded yet',
                    horizontalalignment='center',
                    verticalalignment='center')
            plt.title('Action Frequencies by Street')
            plt.savefig('action_frequencies.png')
            plt.close()
            return

        df = pd.DataFrame(data)
        # Group by Street and Action to get frequencies
        freq_df = df.groupby(['Street', 'Action'])['Count'].sum().reset_index()
        total_actions = df.groupby('Street')['Count'].sum().reset_index()
        freq_df = freq_df.merge(total_actions, on='Street', suffixes=('', '_total'))
        freq_df['Frequency'] = freq_df['Count'] / freq_df['Count_total']

        plt.figure(figsize=(12, 8))
        sns.barplot(data=freq_df, x='Street', y='Frequency', hue='Action')
        plt.title('Action Frequencies by Street')
        plt.savefig('action_frequencies.png')
        plt.close()

    def generate_summary_dashboard(self):
        """Generate a comprehensive dashboard of all visualizations"""
        plt.figure(figsize=(20, 15))

        # Stack progression
        plt.subplot(2, 2, 1)
        self.plot_stack_progression()

        # Win probabilities
        plt.subplot(2, 2, 2)
        self.plot_win_probabilities()

        # Position performance
        plt.subplot(2, 2, 3)
        self.plot_position_performance()

        # Action frequencies
        plt.subplot(2, 2, 4)
        self.plot_action_frequencies()

        plt.tight_layout()
        plt.savefig('poker_dashboard.png')
        plt.close()

    def generate_text_summary(self) -> str:
        """Generate a text summary of the session"""
        total_hands = len(self.hand_history)
        total_profit = sum(h.result for h in self.hand_history)
        win_rate = len([h for h in self.hand_history if h.result > 0]) / total_hands

        return f"""
Session Summary:
---------------
Total Hands: {total_hands}
Total Profit: {total_profit:.2f} BB
Win Rate: {win_rate:.2%}
Average Profit per Hand: {(total_profit/total_hands):.2f} BB
        """