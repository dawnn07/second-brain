# second-brain

An [Agent Skill](https://agentskills.io) for maintaining a personal LLM-powered knowledge base. Inspired by [Andrej Karpathy's LLM wiki idea](https://x.com/karpathy/status/1834497018094227501): **the LLM writes and maintains the wiki; the human reads and asks questions.**

Sources go into `raw/`. The skill compiles them into articles under `wiki/`. The agent orchestrates ingest, compile, query, lint, migration, and vault-health reporting. Python helpers in `tools/` provide search (BM25 + FAISS), graph traversal (NetworkX), a Textual TUI dashboard, and a watchdog-based auto-ingest daemon.

Works with any skill-compatible agent (Claude Code, Cursor, Gemini CLI, OpenCode, Goose, and [many others](https://agentskills.io)).

## Install

**Recommended — via [skills.sh](https://skills.sh):**

```bash
npx add-skill dawnn07/second-brain
```

**Manual install (Claude Code):**

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/dawnn07/second-brain ~/.claude/skills/second-brain
```

**Install Python helpers** (required for search, graph, dashboard, watcher):

```bash
cd ~/.claude/skills/second-brain
pip install -e .
# or, for dev with pytest:
pip install -e ".[dev]"
```

## Quick start

1. **Open a project in your agent and ingest a source:**

   ```
   ingest https://example.com/some-article
   ```

   The skill creates `raw/<topic>/<slug>.md`, compiles it into `wiki/<topic>/<article>.md`, and updates `wiki/index.md` and `wiki/log.md`.

2. **Ask questions:**

   ```
   What do I know about attention mechanisms?
   ```

   The skill searches the wiki and answers with citations.

For the full hands-on walkthrough, see [USAGE.md](USAGE.md).

## Architecture

Three layers, all under your project root:

- **`raw/`** — Immutable source material. The skill reads, never modifies.
- **`wiki/`** — Compiled knowledge articles. The skill owns these.
- **`SKILL.md`** + **`references/`** — The schema layer. Defines structure and workflow.

Helpers under `tools/` are optional — small wikis work without them:

| Tool                 | Purpose                                                   |
| -------------------- | --------------------------------------------------------- |
| `tools/search.py`    | BM25 + optional FAISS retrieval, JSON output              |
| `tools/graph.py`     | NetworkX typed-relationship traversal + Textual graph viz |
| `tools/dashboard.py` | Three-tab vault health TUI                                |
| `tools/watcher.py`   | Watchdog daemon that auto-ingests new `raw/` files        |

## Feature tour

- **Ingest**: Fetch source → save to `raw/` → compile to `wiki/`. One command, cascade-updates related articles automatically.
- **Query**: Natural-language questions answered from wiki content, with citations. Small wikis read `index.md` directly; larger ones call `tools/search.py`.
- **Typed relationships**: Articles declare `supports` / `contradicts` / `supersedes` / `caused-by` / `related-to` edges. `tools/graph.py` traverses them.
- **Lint**: Deterministic checks (index consistency, broken links, orphan detection) auto-fix. Heuristic checks (contradictions, stale claims) report-only.
- **Confidence + decay**: Every article carries a confidence score that decays on a per-article schedule (`slow`/`medium`/`fast`). Low-confidence articles get flagged during queries.
- **Schema versioning**: `Schema: 1.0.0` on every file. Migrations are driven by the skill — dry-run first, then apply.
- **Vault health**: `What is my vault status?` prints totals, confidence distribution, stale articles, orphans, and recent activity.
- **Hooks**: Filesystem watcher and git post-commit template for auto-ingest.

See [`SKILL.md`](SKILL.md) for the full workflow specification.

## FAQ

**Do I need an API key?** No. The skill runs inside your agent (Claude Code, Cursor, etc.); you use whatever subscription or local model the agent provides. Python helpers do not call any LLM API.

**Does this work with Obsidian?** Yes. The vault is plain markdown. Relationships live in frontmatter; links are standard markdown, so Obsidian renders them. `tools/graph.py viz --format dot` exports to Graphviz format if you prefer an external graph view.

**What if I don't want to use Python?** Small wikis (<50 articles) work with just `SKILL.md` + `references/` — the Python helpers are for scale.

**How do I upgrade when the schema changes?** Ask: `Migrate my wiki`. The skill compares each file's `Schema` field against the current version and dry-runs a report. Say `apply` to rewrite.

**Where do I report bugs or request features?** See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
