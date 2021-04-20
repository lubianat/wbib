#!/usr/bin/env python

"""Tests for `wbib` package."""

import unittest
import wikidata2df
from wbib import wbib, queries



class TestWbib(unittest.TestCase):
    """Tests for `wbib` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_if_queries_run(self):
        query = ""
        df = wikidata2df(query)
        """Test something."""
