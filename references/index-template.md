# Index Template

Use this format for `wiki/index.md`. One row per article, grouped by topic.

## Format

```
# Knowledge Base Index

## Topic Name

One-line description of this topic area.

| Article | Summary | Updated |
|---------|---------|---------|
| [Article Title](topic/article.md) | Brief summary of the article | YYYY-MM-DD |
```

## Rules

- Group articles under `## Topic Name` headings matching the topic subdirectory name.
- When adding a new topic section, include a one-line description after the heading.
- Each article gets one row: link, summary (under 80 characters), and Updated date.
- Article links are relative from `wiki/` — use `topic/article.md` (one level deep).
- Updated date reflects when the article's knowledge content last changed.
- Archive pages: prefix the Summary with `[Archived]`.
- Alphabetize articles within each topic section.
