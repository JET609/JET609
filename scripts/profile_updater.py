"""profile_updater.py — Updates dynamic sections in README.md.

Functions:
    replace_block          — Replace content between <!--TAG_START--> markers.
    update_last_updated_and_quote — Refresh timestamp + random motivational quote.
    fetch_medium_posts_feed — Retrieve latest posts from a Medium RSS feed.
    build_blog_md           — Render a Markdown list from (title, link) pairs.
    fetch_top_repos         — Query GitHub API for a user's top non-fork repos.
    build_projects_md       — Render a Markdown list from GitHub repo dicts.
    update_readme           — Orchestrate all updates and write README.md.
"""

import datetime
import json
import pathlib
import random
import re
import urllib.request
import xml.etree.ElementTree as ET

README_PATH = pathlib.Path("README.md")

QUOTES = [
    "Discipline compounds. Tiny steps, big outcomes.",
    "Code. Ship. Learn. Repeat.",
    "Consistency beats motivation.",
    "Build things that outlive the tutorial.",
    "Your GitHub is your portfolio. Treat it like one.",
    "Small progress daily becomes an unfair advantage.",
]


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def replace_block(tag: str, new_content: str, src: str) -> str:
    """Replace the content between ``<!--TAG_START-->`` and ``<!--TAG_END-->``."""
    pattern = rf"<!--{re.escape(tag)}_START-->(.*?)<!--{re.escape(tag)}_END-->"
    repl = f"<!--{tag}_START-->{new_content}<!--{tag}_END-->"
    return re.sub(pattern, repl, src, flags=re.DOTALL)


def update_last_updated_and_quote(src: str, quote: str | None = None) -> str:
    """Inject current IST timestamp and a motivational quote into *src*."""
    ist = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    last_updated = ist.strftime("%Y-%m-%d %H:%M IST")

    chosen_quote = quote if quote is not None else random.choice(QUOTES)

    def _replace_inline(tag: str, val: str, s: str) -> str:
        pattern = rf"<!--{re.escape(tag)}-->(.*?)<!--/{re.escape(tag)}-->"
        new = f"<!--{tag}-->{val}<!--/{tag}-->"
        return re.sub(pattern, new, s, flags=re.DOTALL)

    src = _replace_inline("LAST_UPDATED", last_updated, src)
    src = _replace_inline("RANDOM_QUOTE", chosen_quote, src)
    return src


# ---------------------------------------------------------------------------
# Medium RSS feed
# ---------------------------------------------------------------------------

def fetch_medium_posts_feed(feed_url: str, limit: int = 3) -> list[tuple[str, str]]:
    """Return up to *limit* ``(title, link)`` pairs from a Medium RSS feed."""
    try:
        with urllib.request.urlopen(feed_url, timeout=10) as r:
            data = r.read()
        root = ET.fromstring(data)
        channel = root.find("channel")
        if channel is None:
            return []
        items = channel.findall("item")[:limit]
        posts: list[tuple[str, str]] = []
        for it in items:
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            if title and link:
                posts.append((title, link))
        return posts
    except Exception as exc:
        print("Medium fetch error:", exc)
        return []


def build_blog_md(posts: list[tuple[str, str]]) -> str:
    """Render Markdown from a list of ``(title, link)`` blog post tuples."""
    if not posts:
        return "\nLoading latest posts...\n"
    lines = ["\n"]
    for title, link in posts:
        lines.append(f"- [{title}]({link})")
    lines.append("\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# GitHub repos
# ---------------------------------------------------------------------------

def fetch_top_repos(user: str, limit: int = 4) -> list[dict]:
    """Return up to *limit* top non-fork repos for *user* via the GitHub API."""
    try:
        url = f"https://api.github.com/users/{user}/repos?per_page=100&sort=updated"
        with urllib.request.urlopen(url, timeout=10) as r:
            repos = json.load(r)
    except Exception as exc:
        print("GitHub API error:", exc)
        return []

    ignore = {user, f"{user}.github.io", "JET609"}
    clean = [
        r for r in repos
        if not r.get("fork")
        and r.get("name") not in ignore
        and not r.get("name", "").lower().startswith("test")
    ]

    clean.sort(
        key=lambda r: (r.get("stargazers_count", 0), r.get("pushed_at") or ""),
        reverse=True,
    )
    return clean[:limit]


def build_projects_md(repos: list[dict]) -> str:
    """Render Markdown from a list of GitHub repo dicts."""
    if not repos:
        return "\nHighlighting key projects soon...\n"
    lines = ["\n"]
    for r in repos:
        name = r["name"]
        desc = (r.get("description") or "No description yet.").strip()
        stars = r.get("stargazers_count", 0)
        lang = r.get("language") or "Tech"
        url = r.get("html_url")
        lines.append(
            f"- [{name}]({url}) — {desc} "
            f"· ⭐ {stars} · *{lang}*"
        )
    lines.append("\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def update_readme(readme_path: pathlib.Path = README_PATH) -> bool:
    """Run all updates against *readme_path*. Returns True if the file changed."""
    text = readme_path.read_text(encoding="utf-8")
    updated = text

    updated = update_last_updated_and_quote(updated)

    posts = fetch_medium_posts_feed("https://medium.com/feed/@jayanththomas2004")
    updated = replace_block("BLOG", build_blog_md(posts), updated)

    repos = fetch_top_repos("JET609")
    updated = replace_block("PROJECTS", build_projects_md(repos), updated)

    if updated != text:
        readme_path.write_text(updated, encoding="utf-8")
        print("README updated.")
        return True

    print("No changes made.")
    return False


if __name__ == "__main__":
    update_readme()
