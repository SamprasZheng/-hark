"""Tests for the RSS parser (pure; no network)."""

from __future__ import annotations

from sharks.news_fetch import parse_rss_xml

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<title>Feed</title>
<item><title>Fed holds rates steady</title><link>http://a/1</link></item>
<item><title>Nasdaq hits record</title><link>http://a/2</link></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Nvidia earnings beat</title><link href="http://b/1"/></entry>
</feed>"""


class TestParseRss:
    def test_rss(self):
        rows = parse_rss_xml(RSS)
        assert ("Fed holds rates steady", "http://a/1") in rows
        assert len(rows) == 2

    def test_atom_link_href(self):
        rows = parse_rss_xml(ATOM)
        assert rows[0][0] == "Nvidia earnings beat"
        assert rows[0][1] == "http://b/1"

    def test_garbage_safe(self):
        assert parse_rss_xml(b"<<not xml") == []

    def test_empty_safe(self):
        assert parse_rss_xml(b"<rss><channel></channel></rss>") == []
