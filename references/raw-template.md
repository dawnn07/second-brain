# Raw Source Template

Use this format when saving source material to `raw/<topic>/`.

## File naming

`YYYY-MM-DD-descriptive-slug.md`

- Slug from source title, kebab-case, max 60 characters.
- Published date unknown → omit the date prefix (e.g., `descriptive-slug.md`).
- Duplicate file name → append numeric suffix (e.g., `descriptive-slug-2.md`).

## Format

```
---
Source: [Title](URL)
Collected: YYYY-MM-DD
Published: YYYY-MM-DD
Schema: 1.0.0
---

[content]
```

## Field rules

- **Source**: For URLs, use `[Title](URL)`. For local files, use `Local file: original-filename.ext`.
- **Collected**: Today's date. Always present.
- **Published**: Date from the source. Use `Unknown` when unavailable.
- **Content**: Preserve original text. Clean formatting noise (extra whitespace, navigation elements, boilerplate). Do not rewrite opinions or rephrase arguments.
- **Schema**: Semver string matching the current schema version declared in `SKILL.md`. New files always use the current version. Older files keep their original version until migrated. See SKILL.md's Migration section.
