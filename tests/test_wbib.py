#!/usr/bin/env python

"""Tests for `wbib` package."""
import unittest
from wbib import wbib, queries
import yaml


class TestWbib(unittest.TestCase):
    """Tests for `wbib` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_format_with_prefix(self):
        qids = ["Q35185544", "Q34555562", "Q21284234"]
        result = "{ wd:Q35185544 wd:Q34555562 wd:Q21284234 }"
        test = queries.format_with_prefix(qids)
        assert result == test

    def test_doi_to_qid(self):
        dois = ["10.3897/RIO.2.E9342", "10.3389/fimmu.2019.02736", "wrong"]
        result = {"missing": set(["wrong"]), "qids": set(["Q61654697", "Q92072015"])}
        test = wbib.convert_doi_to_qid(dois)
        assert result["missing"] == test["missing"]
        assert result["qids"] == test["qids"]

    def test_advanced_rendering(self):
        with open("tests/config.yaml") as f2:
            config = yaml.load(f2, Loader=yaml.FullLoader)

        html = wbib.render_dashboard(config, mode="advanced")

        with open("tests/advanced.html", "w") as f:
            f.write(html)

        assert "Advanced Wikidata Bib" in html

    def test_basic_rendering(self):
        qids = ["Q35185544", "Q34555562", "Q21284234"]

        html = wbib.render_dashboard(info=qids, mode="basic")
        assert "Demonstration" in html
        with open("tests/basic.html", "w") as f:
            f.write(html)

    def test_error_in_advanced_rendering(self):
        qids = ["Q35185544", "Q34555562", "Q21284234"]
        with self.assertRaises(TypeError):
            with open("tests/config.yaml") as f2:
                config = yaml.load(f2, Loader=yaml.FullLoader)

            wbib.render_dashboard(qids, mode="advanced")
