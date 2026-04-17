# Archive Page Template

Use this format when archiving a query answer to the wiki. Archive pages are point-in-time snapshots — they are never cascade-updated.

## File naming

Name after the query topic, e.g., `transformer-architectures-overview.md`. Place in the most relevant topic directory.

## Format

```
---
Title: Query Answer Title
Sources: [Article A](../topic/article-a.md); [Article B](../other/article-b.md)
Archived: YYYY-MM-DD
Schema: 1.0.0
---

## Query

[The original question, verbatim]

## Answer

[Synthesized answer. Cite wiki articles with relative markdown links.]

## Sources

- [Article A](../topic/article-a.md) — what it contributed to the answer
- [Article B](../other/article-b.md) — what it contributed to the answer
```

## Field rules

- **Title**: Descriptive title for the archived answer. Sentence case.
- **Sources**: Semicolon-separated markdown links to the wiki articles cited in the answer. Paths relative from the archive file's location.
- **Archived**: Today's date.
- **No Raw field**: Archive pages cite wiki articles, not raw sources. The provenance chain is: archive → article → raw.
- **Sources section**: Each source gets a one-line explanation of what it contributed. This is not a bibliography — it explains the connection.
- **Schema**: Semver string matching the current schema version declared in `SKILL.md`. Archive pages are point-in-time snapshots — do not migrate them; the version records the schema that was current when the answer was archived.
