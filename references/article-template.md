# Wiki Article Template

Use this format for all articles in `wiki/<topic>/`.

## File naming

Name the file after the concept, not the raw source. Kebab-case, e.g., `attention-mechanisms.md`.

## Format

```
---
Title: Article Title
Sources: Author/Org (YYYY-MM-DD); Another Author (YYYY-MM-DD)
Raw: [source-slug](../../raw/topic/YYYY-MM-DD-source-slug.md)
Updated: YYYY-MM-DD
Confidence: 0.85
Decay: slow
Relationships: supports:[Other Article](../topic/other.md); contradicts:[Rival Claim](rival.md)
Schema: 1.0.0
---

## Summary

[2-3 sentence overview of the concept]

## Key Points

[Detailed content compiled from sources. Every claim must be attributable to a specific raw source. When multiple sources cover the same point, synthesize — don't duplicate.]

## See Also

- [Related Article](related-article.md)
```

## Field rules

- **Title**: The concept name. Sentence case.
- **Sources**: Semicolon-separated. Format: `Author or Organization (YYYY-MM-DD)`. Use `Unknown` for missing dates.
- **Raw**: Semicolon-separated markdown links to raw/ files. Paths are relative from `wiki/<topic>/` — use `../../raw/<topic>/<file>.md` (two levels up to project root).
- **Updated**: The date the article's knowledge content last changed. Not the file system timestamp — the date a human or LLM meaningfully updated the content.
- **Summary**: 2-3 sentences. A reader should understand the core concept from this alone.
- **Key Points**: The body of compiled knowledge. Break into subsections with `###` if the article covers multiple facets.
- **See Also**: Links to related articles in the same or other topic directories. Use relative paths from the current file.
- **Confidence**: Score from 0.0 to 1.0. Set based on: number of independent sources (more = higher), source quality and specificity, contradiction signals (contradictions lower it), recency of sources relative to the topic's change rate. Defaults: single reputable source on a stable topic → 0.7; multiple corroborating sources → 0.85-0.95; single source on a fast-changing topic → 0.5.
- **Decay**: How fast the confidence score decays with time. One of `slow` (stable facts, decays ~5% per year), `medium` (evolving fields, decays ~10% per 6 months), `fast` (current events, decays ~20% per 3 months). Choose based on the topic's rate of change, not the source date.
- **Relationships**: Semicolon-separated typed edges to other wiki articles. Each edge is `<type>:<markdown link>`. Allowed types: `supports` (new article reinforces the target's claim), `contradicts` (new article argues against the target), `supersedes` (new article replaces the target), `caused-by` (target is a causal ancestor), `related-to` (loose association — prefer a stronger type when one fits). Paths are relative from the current article's directory. Omit the field entirely when an article has no typed relationships; do not leave it blank. `See Also` is for untyped navigation; `Relationships` is for machine-readable reasoning — a single pair of articles may appear in both.
- **Schema**: Semver string matching the current schema version declared in `SKILL.md`. Defaults to the current version on new articles. Preserved verbatim on existing articles until a migration rewrites them.
