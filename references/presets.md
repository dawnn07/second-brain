# Schema Presets

Alternative schema flavors built on top of the default templates in this directory. A preset is an **additive override** — it keeps every field defined in the base template and adds or re-specifies a few fields to fit a domain. When a user adopts a preset, Claude Code references both the base template and the preset catalog entry below.

All presets use the same `Schema` version as the base templates. Switching between presets is not a migration — it is a metadata convention change.

## research

For academic literature, citation-heavy vaults. Additive fields on articles:

- **Citation**: BibTeX key or DOI string. Lets tools cross-reference with external citation managers.
- **Peer-reviewed**: `true` / `false` / `preprint`. Defaults to `false`.
- **Evidence-level**: `meta-analysis` / `rct` / `observational` / `theoretical` / `opinion`. Used by lint to flag unsupported claims.

Decay defaults shift: `slow` is rare in research vaults. Default `medium` for active fields, `fast` for clinical/experimental topics.

## engineering

For software engineering notes, architecture decisions, debugging logs. Additive fields on articles:

- **System**: Name of the system this article is about (e.g., `auth-service`, `billing-pipeline`). Lets graph queries filter by system.
- **Status**: `proposed` / `adopted` / `deprecated` / `historical`. Drives the same signal as `supersedes` relationships.
- **Runbook**: Link to a runbook or operational doc. Optional.

`Relationships` gains one soft convention: `caused-by` is preferred for incident post-mortems (target is the root-cause event).

## personal

For personal knowledge, daily notes, reading highlights. Additive fields on articles:

- **Mood**: Optional free-text tag. Aids recall ("what was I reading when anxious?").
- **Source-type**: `book` / `article` / `podcast` / `conversation` / `own-thought`. Drives retrieval filters.
- **Re-read**: `true` when the article is worth revisiting. Boolean.

Confidence defaults to `0.7` for own-thoughts (introspection is single-source). Decay defaults to `slow`.

## How to adopt a preset

Tell the skill: "Adopt the research preset" (or engineering / personal). From that point on, new articles include the preset's additive fields with sensible defaults. Existing articles are untouched unless the user runs an explicit migration.

Mixing presets in one vault is allowed but discouraged — the additive fields are preset-specific and tools may not interpret them cross-preset.
