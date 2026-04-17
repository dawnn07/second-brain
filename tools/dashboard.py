"""Textual-based dashboard for wiki vault state.

Usage:
    python -m tools.dashboard [--wiki PATH]

Launches a three-tab TUI:
  - Health: article count, avg effective confidence, stale/orphan lists
  - Graph: outline of typed relationships per topic
  - Activity: recent wiki/log.md entries
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools._vault_state import VaultState, collect_vault_state
from tools._wiki_io import iter_articles


def _health_lines(state: VaultState) -> list[str]:
    avg = state.average_effective_confidence
    avg_str = f"{avg:.2f}" if avg is not None else "n/a"
    stale = [a for a in state.articles if a.effective_confidence is not None and a.effective_confidence < 0.4]
    lines = [
        f"Articles:  {state.article_count}",
        f"Topics:    {state.topic_count} ({', '.join(state.topics) or '—'})",
        f"Avg conf:  {avg_str}",
        f"Stale:     {len(stale)}",
        f"Orphans:   {len(state.orphans)}",
    ]
    if stale:
        lines.append("")
        lines.append("Stale articles:")
        for a in stale:
            lines.append(f"  {a.topic}/{a.path.name}  conf={a.effective_confidence:.2f}")
    if state.orphans:
        lines.append("")
        lines.append("Orphans:")
        for node in state.orphans:
            lines.append(f"  {node}")
    return lines


def _graph_lines(wiki_root: Path) -> list[str]:
    lines: list[str] = []
    for art in iter_articles(wiki_root):
        lines.append(f"{art.topic}/{art.slug}")
        for rel_type, link in art.relationships:
            lines.append(f"  --{rel_type}--> {link}")
        if not art.relationships:
            lines.append("  (no relationships)")
    return lines or ["(empty vault)"]


def _activity_lines(state: VaultState) -> list[str]:
    return state.recent_log or ["(no log entries)"]


def _launch_tui(wiki_root: Path) -> int:
    try:
        from textual.app import App, ComposeResult
        from textual.widgets import Footer, Header, Static, TabbedContent, TabPane
    except Exception as exc:
        print(f"textual not installed: {exc}", file=sys.stderr)
        return 1

    state = collect_vault_state(wiki_root)

    class DashboardApp(App):
        TITLE = "wiki dashboard"

        def compose(self) -> ComposeResult:
            yield Header()
            with TabbedContent():
                with TabPane("Health", id="health"):
                    yield Static("\n".join(_health_lines(state)))
                with TabPane("Graph", id="graph"):
                    yield Static("\n".join(_graph_lines(wiki_root)))
                with TabPane("Activity", id="activity"):
                    yield Static("\n".join(_activity_lines(state)))
            yield Footer()

    DashboardApp().run()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.dashboard")
    parser.add_argument("--wiki", default="wiki")
    args = parser.parse_args(argv)
    return _launch_tui(Path(args.wiki).resolve())


if __name__ == "__main__":
    sys.exit(main())
