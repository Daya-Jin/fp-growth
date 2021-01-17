#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyfpgrowth
----------------------------------

Tests for pyfpgrowth` module.
"""

import unittest
from pyfpgrowth import FPNode, FPTree


class FPNodeTests(unittest.TestCase):
    """
    Tests for the FPNode class.
    """

    def setUp(self):
        """
        Build a node then test the features of it.
        """
        self.node = FPNode(1, 2, None)
        self.node.add_child(2)

    def test_has_child(self):
        """
        Create a root node and test that it has no parent.
        """
        self.assertEqual(self.node.has_child(3), False)
        self.assertEqual(self.node.has_child(2), True)

    def test_get_child(self):
        """
        Test that getChild() returns a node for a valid value
        and None for an invalid value.
        """
        self.assertNotEqual(self.node.get_child(2), None)
        self.assertEqual(self.node.get_child(5), None)

    def test_add_child(self):
        """
        Test that addChild() successfully adds a child node.
        """
        self.assertEqual(self.node.get_child(3), None)
        self.node.add_child(3)
        self.assertNotEqual(self.node.get_child(3), None)
        self.assertEqual(type(self.node.get_child(3)), type(self.node))


class FPGrowthTests(unittest.TestCase):
    """
    Tests everything together.
    """
    support_threshold = 2
    transactions = [['A', 'B', 'C', 'E', 'F', 'O'],
                    ['A', 'C', 'G'],
                    ['E', 'I'],
                    ['A', 'C', 'D', 'E', 'G'],
                    ['A', 'C', 'E', 'G', 'L'],
                    ['E', 'J'],
                    ['A', 'B', 'C', 'E', 'F', 'P'],
                    ['A', 'C', 'D'],
                    ['A', 'C', 'E', 'G', 'M'],
                    ['A', 'C', 'E', 'G', 'N']]

    def test_find_frequent_patterns(self):
        patterns = fp_growth(self.transactions, self.support_threshold)

        expected = {(1, 2): 4, (1, 2, 3): 2, (1, 3): 4, (1,): 6, (2,): 7, (2, 4): 2,
                    (1, 5): 2, (5,): 2, (2, 3): 4, (2, 5): 2, (4,): 2, (1, 2, 5): 2}
        self.assertEqual(patterns, expected)

    def test_generate_association_rules(self):
        patterns = fp_growth(self.transactions, self.support_threshold)
        rules = generate_association_rules(patterns, 0.7)

        expected = {(1, 5): ((2,), 1.0),
                    (5,): ((1, 2), 1.0),
                    (2, 5): ((1,), 1.0),
                    (4,): ((2,), 1.0)}
        self.assertEqual(rules, expected)


if __name__ == '__main__':
    import sys

    sys.exit(unittest.main())
