#!/usr/bin/env python

"""Tests for `wbib` package."""
import unittest
from wbib import wbib, queries


class TestWbib(unittest.TestCase):
    """Tests for `wbib` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_if_queries_run(self):
        qids = ["Q35185544", "Q34555562", "Q21284234" ]
        html = wbib.render_dashboard(qids)
        assert "Demonstration" in html

    def test_format_with_prefix(self):
        qids = ["Q35185544", "Q34555562", "Q21284234" ]
        result = "{ wd:Q35185544 wd:Q34555562 wd:Q21284234 }"
        test = wbib.format_with_prefix(qids)
        assert  result == test