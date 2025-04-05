"""
Decision Explainer for GeckoBot.

This module provides detailed explanations of the bot's decisions.
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from poker_enums import Street, Action, Position
from verbosity_symbols import VerbositySymbols

class DecisionNode:
    """A node in the decision tree."""
    
    def __init__(self, name: str, description: str = "", parent = None):
        """
        Initialize a decision node.
        
        Args:
            name: Name of the node
            description: Description of the node
            parent: Parent node
        """
        self.name = name
        self.description = description
        self.parent = parent
        self.children = []
        self.result = None
        self.start_time = time.time()
        self.end_time = None
        
    def add_child(self, name: str, description: str = "") -> 'DecisionNode':
        """
        Add a child node.
        
        Args:
            name: Name of the child node
            description: Description of the child node
            
        Returns:
            The child node
        """
        child = DecisionNode(name, description, self)
        self.children.append(child)
        return child
    
    def set_result(self, result: Any):
        """
        Set the result of the node.
        
        Args:
            result: Result of the node
        """
        self.result = result
        self.end_time = time.time()
    
    def get_execution_time(self) -> float:
        """
        Get the execution time of the node.
        
        Returns:
            Execution time in seconds
        """
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node to a dictionary.
        
        Returns:
            Dictionary representation of the node
        """
        return {
            'name': self.name,
            'description': self.description,
            'result': str(self.result) if self.result is not None else None,
            'execution_time': self.get_execution_time(),
            'children': [child.to_dict() for child in self.children]
        }

class DecisionExplainer:
    """
    Class to explain the bot's decisions.
    """
    
    def __init__(self, verbosity_level: int = 1):
        """
        Initialize the decision explainer.
        
        Args:
            verbosity_level: Level of verbosity (0-3)
        """
        self.verbosity_level = verbosity_level
        self.verbosity_symbols = VerbositySymbols()
        self.current_decision_tree = None
        self.decision_history = []
        
    def start_decision(self, name: str, description: str = "") -> DecisionNode:
        """
        Start a new decision.
        
        Args:
            name: Name of the decision
            description: Description of the decision
            
        Returns:
            The decision node
        """
        self.current_decision_tree = DecisionNode(name, description)
        return self.current_decision_tree
    
    def end_decision(self, result: Any) -> Dict[str, Any]:
        """
        End the current decision.
        
        Args:
            result: Result of the decision
            
        Returns:
            Dictionary representation of the decision tree
        """
        if self.current_decision_tree is None:
            return {}
            
        self.current_decision_tree.set_result(result)
        decision_dict = self.current_decision_tree.to_dict()
        self.decision_history.append(decision_dict)
        self.current_decision_tree = None
        return decision_dict
    
    def explain_decision(self, decision_dict: Dict[str, Any]) -> str:
        """
        Generate a human-readable explanation of a decision.
        
        Args:
            decision_dict: Dictionary representation of a decision
            
        Returns:
            Human-readable explanation
        """
        explanation = []
        
        # Add decision name and description
        explanation.append(f"Decision: {decision_dict['name']}")
        if decision_dict['description']:
            explanation.append(f"Description: {decision_dict['description']}")
        
        # Add result
        if decision_dict['result'] is not None:
            explanation.append(f"Result: {decision_dict['result']}")
        
        # Add execution time
        explanation.append(f"Execution time: {decision_dict['execution_time']:.6f} seconds")
        
        # Add children recursively
        if decision_dict['children'] and self.verbosity_level > 1:
            explanation.append("\nDecision path:")
            self._add_children_explanation(explanation, decision_dict['children'], 1)
        
        return "\n".join(explanation)
    
    def _add_children_explanation(self, explanation: List[str], children: List[Dict[str, Any]], depth: int):
        """
        Add children explanations recursively.
        
        Args:
            explanation: List of explanation lines
            children: List of children dictionaries
            depth: Current depth in the tree
        """
        for child in children:
            indent = "  " * depth
            explanation.append(f"{indent}- {child['name']}")
            
            if child['description'] and self.verbosity_level > 2:
                explanation.append(f"{indent}  Description: {child['description']}")
                
            if child['result'] is not None:
                explanation.append(f"{indent}  Result: {child['result']}")
                
            if self.verbosity_level > 2:
                explanation.append(f"{indent}  Time: {child['execution_time']:.6f} seconds")
                
            if child['children'] and self.verbosity_level > 1:
                self._add_children_explanation(explanation, child['children'], depth + 1)
    
    def explain_hand_decision(self, hand_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable explanation of a hand decision.
        
        Args:
            hand_data: Dictionary containing hand data
            
        Returns:
            Human-readable explanation
        """
        explanation = []
        
        # Update verbosity symbols
        self.verbosity_symbols.update_table_state(
            current_street=hand_data.get('street', Street.PREFLOP),
            hero_cards=hand_data.get('hero_cards', ('', '')),
            community_cards=hand_data.get('community_cards', []),
            made_hand_ranks=hand_data.get('made_hand_ranks', [])
        )
        
        # Add hand description
        explanation.append(f"Hand: {self.verbosity_symbols.get_hand_description()}")
        
        # Add board description if available
        if hand_data.get('community_cards'):
            explanation.append(f"Board: {self.verbosity_symbols.get_board_description()}")
        
        # Add street
        explanation.append(f"Street: {self.verbosity_symbols.get_street_description()}")
        
        # Add position if available
        if 'position' in hand_data:
            position_map = {
                Position.BUTTON: "Button",
                Position.SMALL_BLIND: "Small Blind",
                Position.BIG_BLIND: "Big Blind",
                Position.UTG: "Under the Gun",
                Position.MP: "Middle Position",
                Position.CO: "Cut-off"
            }
            position = position_map.get(hand_data['position'], str(hand_data['position']))
            explanation.append(f"Position: {position}")
        
        # Add pot size if available
        if 'pot_size' in hand_data:
            explanation.append(f"Pot size: {hand_data['pot_size']}")
        
        # Add win probability if available
        if 'win_probability' in hand_data:
            explanation.append(f"Win probability: {hand_data['win_probability']:.2%}")
        
        # Add decision if available
        if 'decision' in hand_data:
            action, amount = hand_data['decision']
            action_map = {
                Action.FOLD: "Fold",
                Action.CHECK: "Check",
                Action.CALL: "Call",
                Action.RAISE: "Raise"
            }
            action_str = action_map.get(action, str(action))
            
            if action in [Action.CALL, Action.RAISE] and amount is not None:
                explanation.append(f"Decision: {action_str} {amount}")
            else:
                explanation.append(f"Decision: {action_str}")
        
        # Add decision explanation if available
        if 'decision_explanation' in hand_data:
            explanation.append(f"\nExplanation: {hand_data['decision_explanation']}")
        
        return "\n".join(explanation)
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """
        Get the decision history.
        
        Returns:
            List of decision dictionaries
        """
        return self.decision_history
    
    def clear_decision_history(self):
        """Clear the decision history."""
        self.decision_history = []
    
    def set_verbosity_level(self, level: int):
        """
        Set the verbosity level.
        
        Args:
            level: Verbosity level (0-3)
        """
        self.verbosity_level = max(0, min(3, level))  # Clamp to 0-3
