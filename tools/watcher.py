"""Watchdog-based auto-ingest daemon for raw/ sources.

Usage:
    python -m tools.watcher [--vault PATH] [--debounce SECONDS]

Watches <vault>/raw/ recursively. When a new .md or .pdf file appears and
has been stable for the debounce window, invokes:

    claude -p "ingest raw/<topic>/<file>"

from the vault root. The skill's Ingest section handles everything else.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path


INGESTIBLE_SUFFIXES = {".md", ".pdf", ".txt"}


def build_ingest_command(path: Path, vault_root: Path) -> list[str]:
    """Return the claude CLI command to ingest `path` from `vault_root`."""
    rel = path.resolve().relative_to(vault_root.resolve())
    return ["claude", "-p", f"ingest {rel.as_posix()}"]


@dataclass
class DebounceQueue:
    window_seconds: float = 1.5
    _last_touch: dict[Path, float] = field(default_factory=dict)

    def enqueue(self, path: Path, now: float | None = None) -> None:
        self._last_touch[path] = time.monotonic() if now is None else now

    def drain_ready(self, now: float | None = None) -> list[Path]:
        current = time.monotonic() if now is None else now
        ready = [p for p, t in self._last_touch.items() if current - t >= self.window_seconds]
        for p in ready:
            self._last_touch.pop(p, None)
        return ready


def _ingest(path: Path, vault_root: Path) -> int:
    cmd = build_ingest_command(path, vault_root)
    print(f"[watcher] ingesting {path}", file=sys.stderr)
    return subprocess.call(cmd, cwd=vault_root)


def _watch(vault_root: Path, debounce: float) -> int:
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except Exception as exc:
        print(f"watchdog not installed: {exc}", file=sys.stderr)
        return 1

    raw_root = vault_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)
    queue = DebounceQueue(window_seconds=debounce)

    class Handler(FileSystemEventHandler):
        def on_created(self, event) -> None:  # noqa: ANN001
            if event.is_directory:
                return
            path = Path(event.src_path)
            if path.suffix.lower() in INGESTIBLE_SUFFIXES:
                queue.enqueue(path)

        def on_modified(self, event) -> None:  # noqa: ANN001
            if event.is_directory:
                return
            path = Path(event.src_path)
            if path.suffix.lower() in INGESTIBLE_SUFFIXES:
                queue.enqueue(path)

    observer = Observer()
    observer.schedule(Handler(), str(raw_root), recursive=True)
    observer.start()
    print(f"[watcher] watching {raw_root} (debounce={debounce}s)", file=sys.stderr)
    try:
        while True:
            time.sleep(debounce / 2)
            for path in queue.drain_ready():
                if path.exists():
                    _ingest(path, vault_root)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.watcher")
    parser.add_argument("--vault", default=".")
    parser.add_argument("--debounce", type=float, default=1.5)
    args = parser.parse_args(argv)
    return _watch(Path(args.vault).resolve(), args.debounce)


if __name__ == "__main__":
    sys.exit(main())
