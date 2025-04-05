#!/usr/bin/env python3
"""
Test script for the DecisionExplainer class.
"""

import unittest
from decision_explainer import DecisionExplainer, DecisionNode
from poker_enums import Street, Action, Position

class TestDecisionExplainer(unittest.TestCase):
    """Test cases for the DecisionExplainer class."""
    
    def setUp(self):
        """Set up the test case."""
        self.explainer = DecisionExplainer(verbosity_level=3)
        
    def test_decision_node(self):
        """Test the DecisionNode class."""
        # Create a root node
        root = DecisionNode("Root", "Root description")
        
        # Add children
        child1 = root.add_child("Child 1", "Child 1 description")
        child2 = root.add_child("Child 2", "Child 2 description")
        
        # Add grandchildren
        grandchild1 = child1.add_child("Grandchild 1", "Grandchild 1 description")
        
        # Set results
        grandchild1.set_result("Grandchild 1 result")
        child2.set_result("Child 2 result")
        root.set_result("Root result")
        
        # Check parent-child relationships
        self.assertEqual(child1.parent, root)
        self.assertEqual(child2.parent, root)
        self.assertEqual(grandchild1.parent, child1)
        
        # Check results
        self.assertEqual(grandchild1.result, "Grandchild 1 result")
        self.assertEqual(child2.result, "Child 2 result")
        self.assertEqual(root.result, "Root result")
        
        # Check execution times
        self.assertGreaterEqual(root.get_execution_time(), 0)
        self.assertGreaterEqual(child1.get_execution_time(), 0)
        self.assertGreaterEqual(child2.get_execution_time(), 0)
        self.assertGreaterEqual(grandchild1.get_execution_time(), 0)
        
        # Check dictionary conversion
        root_dict = root.to_dict()
        self.assertEqual(root_dict['name'], "Root")
        self.assertEqual(root_dict['description'], "Root description")
        self.assertEqual(root_dict['result'], "Root result")
        self.assertEqual(len(root_dict['children']), 2)
        
    def test_decision_explainer(self):
        """Test the DecisionExplainer class."""
        # Start a decision
        decision = self.explainer.start_decision("Test decision", "Test description")
        
        # Add children
        child1 = decision.add_child("Child 1", "Child 1 description")
        child2 = decision.add_child("Child 2", "Child 2 description")
        
        # Add grandchildren
        grandchild1 = child1.add_child("Grandchild 1", "Grandchild 1 description")
        
        # Set results
        grandchild1.set_result("Grandchild 1 result")
        child2.set_result("Child 2 result")
        
        # End the decision
        decision_dict = self.explainer.end_decision("Test result")
        
        # Check the decision dictionary
        self.assertEqual(decision_dict['name'], "Test decision")
        self.assertEqual(decision_dict['description'], "Test description")
        self.assertEqual(decision_dict['result'], "Test result")
        self.assertEqual(len(decision_dict['children']), 2)
        
        # Check the decision history
        history = self.explainer.get_decision_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['name'], "Test decision")
        
        # Clear the decision history
        self.explainer.clear_decision_history()
        self.assertEqual(len(self.explainer.get_decision_history()), 0)
        
    def test_explain_decision(self):
        """Test the explain_decision method."""
        # Start a decision
        decision = self.explainer.start_decision("Test decision", "Test description")
        
        # Add children
        child1 = decision.add_child("Child 1", "Child 1 description")
        child2 = decision.add_child("Child 2", "Child 2 description")
        
        # Add grandchildren
        grandchild1 = child1.add_child("Grandchild 1", "Grandchild 1 description")
        
        # Set results
        grandchild1.set_result("Grandchild 1 result")
        child2.set_result("Child 2 result")
        
        # End the decision
        decision_dict = self.explainer.end_decision("Test result")
        
        # Explain the decision
        explanation = self.explainer.explain_decision(decision_dict)
        
        # Check the explanation
        self.assertIn("Decision: Test decision", explanation)
        self.assertIn("Description: Test description", explanation)
        self.assertIn("Result: Test result", explanation)
        self.assertIn("Decision path:", explanation)
        self.assertIn("- Child 1", explanation)
        self.assertIn("- Child 2", explanation)
        self.assertIn("- Grandchild 1", explanation)
        
    def test_explain_hand_decision(self):
        """Test the explain_hand_decision method."""
        # Create hand data
        hand_data = {
            'street': Street.FLOP,
            'hero_cards': ('Ah', 'Kd'),
            'community_cards': ['Qc', 'Jd', 'Ts'],
            'position': Position.BUTTON,
            'pot_size': 100,
            'win_probability': 0.75,
            'decision': (Action.RAISE, 50),
            'decision_explanation': "Raising with a strong hand"
        }
        
        # Explain the hand decision
        explanation = self.explainer.explain_hand_decision(hand_data)
        
        # Check the explanation
        self.assertIn("Hand: Ace-King offsuit", explanation)
        self.assertIn("Board: Queen♣ Jack♦ 10♠", explanation)
        self.assertIn("Street: Flop", explanation)
        self.assertIn("Position: Button", explanation)
        self.assertIn("Pot size: 100", explanation)
        self.assertIn("Win probability: 75.00%", explanation)
        self.assertIn("Decision: Raise 50", explanation)
        self.assertIn("Explanation: Raising with a strong hand", explanation)
        
    def test_verbosity_level(self):
        """Test the verbosity level."""
        # Set verbosity level to 0
        self.explainer.set_verbosity_level(0)
        self.assertEqual(self.explainer.verbosity_level, 0)
        
        # Set verbosity level to 3
        self.explainer.set_verbosity_level(3)
        self.assertEqual(self.explainer.verbosity_level, 3)
        
        # Try to set verbosity level to -1 (should be clamped to 0)
        self.explainer.set_verbosity_level(-1)
        self.assertEqual(self.explainer.verbosity_level, 0)
        
        # Try to set verbosity level to 4 (should be clamped to 3)
        self.explainer.set_verbosity_level(4)
        self.assertEqual(self.explainer.verbosity_level, 3)

if __name__ == '__main__':
    unittest.main()
