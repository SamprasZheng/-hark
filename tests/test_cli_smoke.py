"""Phase 1 smoke tests for the Sharks CLI.

These verify the CLI is callable and exits 0 on the stub commands.
Real behaviour tests arrive in Phase 2+ alongside the implementation.
"""

from __future__ import annotations

import pytest

from sharks.cli import build_parser, main


class TestParserConstruction:
    def test_parser_builds(self):
        parser = build_parser()
        assert parser.prog == "sharks"

    def test_pick_subcommand_exists(self):
        parser = build_parser()
        # Should parse without raising
        ns = parser.parse_args(["pick"])
        assert ns.command == "pick"
        assert ns.mode == "auto"  # default

    def test_pick_mode_choices(self):
        parser = build_parser()
        for mode in ["low", "high", "auto"]:
            ns = parser.parse_args(["pick", "--mode", mode])
            assert ns.mode == mode

    def test_pick_mode_rejects_invalid(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["pick", "--mode", "ultrafast"])

    def test_pick_dry_run_flag(self):
        parser = build_parser()
        ns = parser.parse_args(["pick", "--dry-run"])
        assert ns.dry_run is True

    def test_ingest_requires_source(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["ingest"])  # missing --source

    def test_ingest_with_source(self):
        parser = build_parser()
        ns = parser.parse_args(["ingest", "--source", "raw/macro/test.md"])
        assert ns.source == "raw/macro/test.md"

    def test_wiki_lint_exists(self):
        parser = build_parser()
        ns = parser.parse_args(["wiki", "lint"])
        assert ns.command == "wiki"
        assert ns.wiki_command == "lint"


class TestMainExitCodes:
    """Phase 1: all stub commands exit 0."""

    def test_pick_low(self, capsys):
        assert main(["pick", "--mode", "low"]) == 0
        captured = capsys.readouterr()
        assert "stub" in captured.out.lower()

    def test_pick_high(self, capsys):
        assert main(["pick", "--mode", "high"]) == 0

    def test_pick_auto(self, capsys):
        assert main(["pick", "--mode", "auto"]) == 0

    def test_ingest(self, capsys):
        assert main(["ingest", "--source", "raw/macro/test.md"]) == 0
        captured = capsys.readouterr()
        assert "phase 2" in captured.out.lower()

    def test_wiki_lint(self, capsys):
        assert main(["wiki", "lint"]) == 0


class TestDataClientStubs:
    """Phase 1: every data client raises NotImplementedError with a clear Phase 2 reference."""

    def test_yfinance_client_stub(self):
        from sharks.data.yfinance_client import YFinanceClient
        client = YFinanceClient()  # no key needed
        with pytest.raises(NotImplementedError, match="Phase 2"):
            from datetime import date
            client.get_eod("NVDA", date(2026, 1, 1), date(2026, 5, 1))

    def test_polygon_client_stub(self):
        from sharks.data.polygon_client import PolygonClient
        with pytest.raises(NotImplementedError, match="Phase 2"):
            PolygonClient(api_key="dummy")

    def test_finnhub_client_stub(self):
        from sharks.data.finnhub_client import FinnhubClient
        with pytest.raises(NotImplementedError, match="Phase 2"):
            FinnhubClient(api_key="dummy")

    def test_finviz_client_stub(self):
        from sharks.data.finviz_client import FinvizClient
        with pytest.raises(NotImplementedError, match="Phase 2"):
            FinvizClient()

    def test_ccxt_client_stub(self):
        from sharks.data.ccxt_client import CcxtClient
        with pytest.raises(NotImplementedError, match="Phase 2"):
            CcxtClient()
