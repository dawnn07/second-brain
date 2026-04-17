from __future__ import annotations

from pathlib import Path

from tools.watcher import DebounceQueue, build_ingest_command


def test_build_ingest_command_uses_relative_path(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    raw = vault / "raw" / "ml" / "2026-04-17-paper.md"
    raw.parent.mkdir(parents=True)
    raw.write_text("hi", encoding="utf-8")

    cmd = build_ingest_command(raw, vault_root=vault)

    assert cmd[0] == "claude"
    assert "-p" in cmd
    prompt_index = cmd.index("-p") + 1
    assert cmd[prompt_index] == "ingest raw/ml/2026-04-17-paper.md"


def test_debounce_queue_coalesces_repeat_events(tmp_path: Path) -> None:
    queue = DebounceQueue(window_seconds=0.05)
    path = tmp_path / "x.md"

    queue.enqueue(path, now=0.00)
    queue.enqueue(path, now=0.02)
    queue.enqueue(path, now=0.04)

    # Still inside window → nothing ready
    assert queue.drain_ready(now=0.04) == []
    # Past window since last touch → ready
    assert queue.drain_ready(now=0.10) == [path]
    # Drained; no repeat
    assert queue.drain_ready(now=0.20) == []


def test_debounce_queue_flushes_distinct_paths_independently(tmp_path: Path) -> None:
    queue = DebounceQueue(window_seconds=0.05)
    a = tmp_path / "a.md"
    b = tmp_path / "b.md"

    queue.enqueue(a, now=0.00)
    queue.enqueue(b, now=0.03)

    assert queue.drain_ready(now=0.06) == [a]
    assert queue.drain_ready(now=0.10) == [b]
