"""Comprehensive unit tests for scripts/profile_updater.py."""

import json
import pathlib
import sys
import tempfile
import textwrap
import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

# Ensure the repo root is on the path so the import works from any CWD.
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from scripts.profile_updater import (
    build_blog_md,
    build_projects_md,
    fetch_medium_posts_feed,
    fetch_top_repos,
    replace_block,
    update_last_updated_and_quote,
    update_readme,
)


# ---------------------------------------------------------------------------
# replace_block
# ---------------------------------------------------------------------------

class TestReplaceBlock(unittest.TestCase):
    def test_replaces_content_between_markers(self):
        src = "<!--BLOG_START-->old content<!--BLOG_END-->"
        result = replace_block("BLOG", "new content", src)
        self.assertEqual(result, "<!--BLOG_START-->new content<!--BLOG_END-->")

    def test_replaces_multiline_content(self):
        src = "<!--BLOG_START-->\nline1\nline2\n<!--BLOG_END-->"
        result = replace_block("BLOG", "replaced", src)
        self.assertEqual(result, "<!--BLOG_START-->replaced<!--BLOG_END-->")

    def test_no_match_returns_original(self):
        src = "no markers here"
        result = replace_block("BLOG", "content", src)
        self.assertEqual(result, src)

    def test_replaces_only_matching_tag(self):
        src = (
            "<!--BLOG_START-->blog<!--BLOG_END-->"
            "<!--PROJECTS_START-->projects<!--PROJECTS_END-->"
        )
        result = replace_block("BLOG", "new blog", src)
        self.assertIn("<!--BLOG_START-->new blog<!--BLOG_END-->", result)
        self.assertIn("<!--PROJECTS_START-->projects<!--PROJECTS_END-->", result)

    def test_replaces_empty_content(self):
        src = "<!--BLOG_START--><!--BLOG_END-->"
        result = replace_block("BLOG", "hello", src)
        self.assertEqual(result, "<!--BLOG_START-->hello<!--BLOG_END-->")

    def test_inserts_empty_replacement(self):
        src = "<!--BLOG_START-->old<!--BLOG_END-->"
        result = replace_block("BLOG", "", src)
        self.assertEqual(result, "<!--BLOG_START--><!--BLOG_END-->")

    def test_tag_with_special_regex_chars(self):
        """Tag names should be treated as literals, not regex patterns."""
        src = "<!--LAST.UPDATED_START-->old<!--LAST.UPDATED_END-->"
        # The dot in tag name must be escaped; no match expected for a safe tag.
        result = replace_block("LAST.UPDATED", "new", src)
        self.assertEqual(result, "<!--LAST.UPDATED_START-->new<!--LAST.UPDATED_END-->")

    def test_multiple_blocks_same_tag_replaces_all(self):
        src = (
            "<!--X_START-->a<!--X_END--> text <!--X_START-->b<!--X_END-->"
        )
        result = replace_block("X", "z", src)
        self.assertEqual(result, "<!--X_START-->z<!--X_END--> text <!--X_START-->z<!--X_END-->")


# ---------------------------------------------------------------------------
# update_last_updated_and_quote
# ---------------------------------------------------------------------------

class TestUpdateLastUpdatedAndQuote(unittest.TestCase):
    _TEMPLATE = (
        "<!--LAST_UPDATED-->OLD_DATE<!--/LAST_UPDATED--> • "
        "<!--RANDOM_QUOTE-->OLD_QUOTE<!--/RANDOM_QUOTE-->"
    )

    def test_last_updated_is_replaced(self):
        result = update_last_updated_and_quote(self._TEMPLATE, quote="q")
        self.assertNotIn("OLD_DATE", result)
        self.assertIn("IST", result)

    def test_quote_is_replaced_with_provided_quote(self):
        result = update_last_updated_and_quote(self._TEMPLATE, quote="My quote")
        self.assertIn("My quote", result)
        self.assertNotIn("OLD_QUOTE", result)

    def test_random_quote_selected_when_none_provided(self):
        from scripts.profile_updater import QUOTES
        result = update_last_updated_and_quote(self._TEMPLATE)
        replaced_quote_found = any(q in result for q in QUOTES)
        self.assertTrue(replaced_quote_found)

    def test_timestamp_format(self):
        """Timestamp should match YYYY-MM-DD HH:MM IST."""
        import re
        result = update_last_updated_and_quote(self._TEMPLATE, quote="q")
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} IST")

    def test_no_markers_returns_src_unchanged_for_markers(self):
        src = "no markers at all"
        result = update_last_updated_and_quote(src, quote="q")
        self.assertEqual(result, src)

    def test_multiline_old_value_replaced(self):
        src = "<!--LAST_UPDATED-->\nsome\nmulti\nline\n<!--/LAST_UPDATED-->"
        result = update_last_updated_and_quote(src, quote="q")
        self.assertNotIn("multi", result)
        self.assertIn("IST", result)


# ---------------------------------------------------------------------------
# build_blog_md
# ---------------------------------------------------------------------------

class TestBuildBlogMd(unittest.TestCase):
    def test_empty_list_returns_loading_message(self):
        result = build_blog_md([])
        self.assertIn("Loading latest posts...", result)

    def test_single_post(self):
        result = build_blog_md([("My Post", "https://example.com/post")])
        self.assertIn("- [My Post](https://example.com/post)", result)

    def test_multiple_posts(self):
        posts = [
            ("Post A", "https://a.com"),
            ("Post B", "https://b.com"),
            ("Post C", "https://c.com"),
        ]
        result = build_blog_md(posts)
        for title, link in posts:
            self.assertIn(f"- [{title}]({link})", result)

    def test_output_starts_and_ends_with_newline(self):
        result = build_blog_md([("T", "https://x.com")])
        self.assertTrue(result.startswith("\n"))
        self.assertTrue(result.endswith("\n"))

    def test_post_with_special_markdown_chars(self):
        result = build_blog_md([("Title [special]", "https://x.com")])
        self.assertIn("Title [special]", result)


# ---------------------------------------------------------------------------
# fetch_medium_posts_feed
# ---------------------------------------------------------------------------

RSS_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>Post One</title>
      <link>https://medium.com/post-one</link>
    </item>
    <item>
      <title>Post Two</title>
      <link>https://medium.com/post-two</link>
    </item>
    <item>
      <title>Post Three</title>
      <link>https://medium.com/post-three</link>
    </item>
    <item>
      <title>Post Four</title>
      <link>https://medium.com/post-four</link>
    </item>
  </channel>
</rss>"""


class TestFetchMediumPostsFeed(unittest.TestCase):
    def _mock_urlopen(self, data: bytes):
        cm = MagicMock()
        cm.__enter__ = MagicMock(return_value=MagicMock(read=MagicMock(return_value=data)))
        cm.__exit__ = MagicMock(return_value=False)
        return cm

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_returns_up_to_limit_posts(self, mock_open):
        mock_open.return_value = self._mock_urlopen(RSS_SAMPLE)
        posts = fetch_medium_posts_feed("https://fake.feed", limit=3)
        self.assertEqual(len(posts), 3)

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_returns_all_when_limit_exceeds_items(self, mock_open):
        mock_open.return_value = self._mock_urlopen(RSS_SAMPLE)
        posts = fetch_medium_posts_feed("https://fake.feed", limit=10)
        self.assertEqual(len(posts), 4)

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_post_titles_and_links_correct(self, mock_open):
        mock_open.return_value = self._mock_urlopen(RSS_SAMPLE)
        posts = fetch_medium_posts_feed("https://fake.feed", limit=2)
        self.assertEqual(posts[0], ("Post One", "https://medium.com/post-one"))
        self.assertEqual(posts[1], ("Post Two", "https://medium.com/post-two"))

    @patch("scripts.profile_updater.urllib.request.urlopen", side_effect=Exception("network error"))
    def test_returns_empty_on_network_error(self, _mock):
        posts = fetch_medium_posts_feed("https://fake.feed")
        self.assertEqual(posts, [])

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_returns_empty_when_no_channel(self, mock_open):
        no_channel_rss = b"<?xml version='1.0'?><rss version='2.0'></rss>"
        mock_open.return_value = self._mock_urlopen(no_channel_rss)
        posts = fetch_medium_posts_feed("https://fake.feed")
        self.assertEqual(posts, [])

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_skips_items_with_missing_title_or_link(self, mock_open):
        partial_rss = b"""<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item><title>Good</title><link>https://x.com</link></item>
  <item><link>https://no-title.com</link></item>
  <item><title>No Link</title></item>
</channel></rss>"""
        mock_open.return_value = self._mock_urlopen(partial_rss)
        posts = fetch_medium_posts_feed("https://fake.feed", limit=5)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0][0], "Good")

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_default_limit_is_three(self, mock_open):
        mock_open.return_value = self._mock_urlopen(RSS_SAMPLE)
        posts = fetch_medium_posts_feed("https://fake.feed")
        self.assertLessEqual(len(posts), 3)


# ---------------------------------------------------------------------------
# fetch_top_repos
# ---------------------------------------------------------------------------

def _make_repo(name, stars=0, pushed="2024-01-01", fork=False, lang="Python", desc="desc"):
    return {
        "name": name,
        "full_name": f"JET609/{name}",
        "fork": fork,
        "stargazers_count": stars,
        "pushed_at": pushed,
        "language": lang,
        "description": desc,
        "html_url": f"https://github.com/JET609/{name}",
    }


class TestFetchTopRepos(unittest.TestCase):
    def _patch_urlopen(self, repos_json):
        data = json.dumps(repos_json).encode()
        cm = MagicMock()
        inner = MagicMock()
        inner.__enter__ = MagicMock(return_value=inner)
        inner.__exit__ = MagicMock(return_value=False)
        inner.read = MagicMock(return_value=data)
        # json.load reads from the file-like object; mock it directly
        cm.__enter__ = MagicMock(return_value=cm)
        cm.__exit__ = MagicMock(return_value=False)
        cm.read = MagicMock(return_value=data)
        return cm

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_excludes_forks(self, mock_open):
        repos = [_make_repo("MyRepo"), _make_repo("ForkRepo", fork=True)]
        mock_open.return_value.__enter__ = MagicMock(
            return_value=MagicMock(
                read=MagicMock(return_value=json.dumps(repos).encode())
            )
        )
        mock_open.return_value.__exit__ = MagicMock(return_value=False)

        with patch("scripts.profile_updater.json.load", return_value=repos):
            result = fetch_top_repos("JET609")
        names = [r["name"] for r in result]
        self.assertNotIn("ForkRepo", names)

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_excludes_username_and_profile_repo(self, mock_open):
        repos = [
            _make_repo("JET609"),
            _make_repo("JET609.github.io"),
            _make_repo("GoodRepo"),
        ]
        with patch("scripts.profile_updater.json.load", return_value=repos):
            result = fetch_top_repos("JET609")
        names = [r["name"] for r in result]
        self.assertNotIn("JET609", names)
        self.assertNotIn("JET609.github.io", names)
        self.assertIn("GoodRepo", names)

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_excludes_repos_starting_with_test(self, mock_open):
        repos = [_make_repo("test-repo"), _make_repo("TestRepo"), _make_repo("RealRepo")]
        with patch("scripts.profile_updater.json.load", return_value=repos):
            result = fetch_top_repos("JET609")
        names = [r["name"] for r in result]
        self.assertNotIn("test-repo", names)
        self.assertNotIn("TestRepo", names)
        self.assertIn("RealRepo", names)

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_sorts_by_stars_descending(self, mock_open):
        repos = [
            _make_repo("Low", stars=1),
            _make_repo("High", stars=100),
            _make_repo("Mid", stars=10),
        ]
        with patch("scripts.profile_updater.json.load", return_value=repos):
            result = fetch_top_repos("JET609", limit=3)
        self.assertEqual(result[0]["name"], "High")
        self.assertEqual(result[1]["name"], "Mid")
        self.assertEqual(result[2]["name"], "Low")

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_respects_limit(self, mock_open):
        repos = [_make_repo(f"Repo{i}", stars=i) for i in range(10)]
        with patch("scripts.profile_updater.json.load", return_value=repos):
            result = fetch_top_repos("JET609", limit=4)
        self.assertEqual(len(result), 4)

    @patch("scripts.profile_updater.urllib.request.urlopen", side_effect=Exception("timeout"))
    def test_returns_empty_on_error(self, _mock):
        result = fetch_top_repos("JET609")
        self.assertEqual(result, [])

    @patch("scripts.profile_updater.urllib.request.urlopen")
    def test_default_limit_is_four(self, mock_open):
        repos = [_make_repo(f"Repo{i}", stars=i) for i in range(10)]
        with patch("scripts.profile_updater.json.load", return_value=repos):
            result = fetch_top_repos("JET609")
        self.assertLessEqual(len(result), 4)


# ---------------------------------------------------------------------------
# build_projects_md
# ---------------------------------------------------------------------------

class TestBuildProjectsMd(unittest.TestCase):
    def test_empty_returns_placeholder(self):
        result = build_projects_md([])
        self.assertIn("Highlighting key projects soon...", result)

    def test_single_repo(self):
        repo = _make_repo("CoolProject", stars=5, lang="Python", desc="A cool project")
        repo["html_url"] = "https://github.com/JET609/CoolProject"
        result = build_projects_md([repo])
        self.assertIn("[CoolProject](https://github.com/JET609/CoolProject)", result)
        self.assertIn("A cool project", result)
        self.assertIn("⭐ 5", result)
        self.assertIn("*Python*", result)

    def test_missing_description_uses_fallback(self):
        repo = _make_repo("NoDesc")
        repo["description"] = None
        result = build_projects_md([repo])
        self.assertIn("No description yet.", result)

    def test_missing_language_uses_tech_fallback(self):
        repo = _make_repo("NoLang")
        repo["language"] = None
        result = build_projects_md([repo])
        self.assertIn("*Tech*", result)

    def test_multiple_repos_all_listed(self):
        repos = [_make_repo(f"Repo{i}", stars=i) for i in range(3)]
        result = build_projects_md(repos)
        for i in range(3):
            self.assertIn(f"Repo{i}", result)

    def test_output_starts_and_ends_with_newline(self):
        result = build_projects_md([_make_repo("X")])
        self.assertTrue(result.startswith("\n"))
        self.assertTrue(result.endswith("\n"))

    def test_zero_stars_shown(self):
        repo = _make_repo("ZeroStars", stars=0)
        result = build_projects_md([repo])
        self.assertIn("⭐ 0", result)


# ---------------------------------------------------------------------------
# update_readme (integration-style, file I/O mocked)
# ---------------------------------------------------------------------------

_README_TEMPLATE = textwrap.dedent("""\
    <!--LAST_UPDATED-->OLD<!--/LAST_UPDATED-->
    <!--RANDOM_QUOTE-->OLD_QUOTE<!--/RANDOM_QUOTE-->
    <!--BLOG_START-->old blog<!--BLOG_END-->
    <!--PROJECTS_START-->old projects<!--PROJECTS_END-->
""")


class TestUpdateReadme(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        )
        self.tmp.write(_README_TEMPLATE)
        self.tmp.close()
        self.readme = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.readme.unlink(missing_ok=True)

    @patch("scripts.profile_updater.fetch_medium_posts_feed", return_value=[("T", "https://x.com")])
    @patch("scripts.profile_updater.fetch_top_repos", return_value=[_make_repo("MyRepo")])
    def test_file_is_updated(self, _repos, _posts):
        changed = update_readme(self.readme)
        self.assertTrue(changed)
        content = self.readme.read_text(encoding="utf-8")
        self.assertNotIn("old blog", content)
        self.assertNotIn("old projects", content)
        self.assertIn("IST", content)

    @patch("scripts.profile_updater.fetch_medium_posts_feed", return_value=[])
    @patch("scripts.profile_updater.fetch_top_repos", return_value=[])
    def test_returns_true_when_content_changes(self, _r, _p):
        changed = update_readme(self.readme)
        # Even with empty results the timestamp changes, so file should change.
        self.assertTrue(changed)

    @patch("scripts.profile_updater.fetch_medium_posts_feed", return_value=[("T", "https://x.com")])
    @patch("scripts.profile_updater.fetch_top_repos", return_value=[])
    def test_blog_section_replaced(self, _r, _p):
        update_readme(self.readme)
        content = self.readme.read_text(encoding="utf-8")
        self.assertIn("<!--BLOG_START-->", content)
        self.assertIn("[T](https://x.com)", content)

    @patch("scripts.profile_updater.fetch_medium_posts_feed", return_value=[])
    @patch("scripts.profile_updater.fetch_top_repos", return_value=[_make_repo("Proj", stars=3)])
    def test_projects_section_replaced(self, _r, _p):
        update_readme(self.readme)
        content = self.readme.read_text(encoding="utf-8")
        self.assertIn("Proj", content)
        self.assertNotIn("old projects", content)


if __name__ == "__main__":
    unittest.main()
