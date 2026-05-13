# Cross-link map

What references what. Verify cross-link integrity at the end of each phase by running `find` / `grep` against the listed targets.

## Cross-link graph

```
README.md (repo root)
  → brand/MANIFESTO.md
  → brand/PRICING.md (when exists)
  → brand/BRAND.md
  → brand/COPY.md
  → brand/BIOS.md
  → CONTRIBUTING.md
  → SECURITY.md
  → CODE_OF_CONDUCT.md
  → LICENSE

CONTRIBUTING.md
  → README.md
  → brand/COPY.md (for brand voice)
  → CODE_OF_CONDUCT.md
  → SECURITY.md

SECURITY.md
  → (no inbound brand cross-links; just contact email)

CODE_OF_CONDUCT.md
  → contributor-covenant.org/version/2/1 (canonical adopted-by-reference)
  → enforcement contact email

brand/BRAND.md
  → brand/COPY.md (top-of-file pointer for language)
  → brand/MANIFESTO.md (top-of-file pointer for long-form positioning)
  → brand/BIOS.md
  → brand/FAQ.md
  → brand/GLOSSARY.md
  → brand/TONE.md
  → brand/PRICING.md (when exists)

brand/COPY.md
  → brand/BRAND.md (companion doc)
  → brand/MANIFESTO.md (long-form context)
  → brand/BIOS.md ("Topics covered elsewhere" table)
  → brand/FAQ.md ("Topics covered elsewhere")
  → brand/GLOSSARY.md ("Topics covered elsewhere")
  → brand/TONE.md ("Topics covered elsewhere")
  → brand/PRICING.md ("Topics covered elsewhere")

brand/MANIFESTO.md
  → brand/PRICING.md (cross-link from "pricing-argument" section to numbers doc)

brand/BIOS.md
  → brand/COPY.md (top-of-file pointer for vocabulary constraints)
  → brand/MANIFESTO.md (top-of-file pointer for long-form)

brand/FAQ.md
  → brand/MANIFESTO.md (every answer that anchors on a manifesto section)
  → brand/COPY.md (top-of-file)
  → brand/GLOSSARY.md (top-of-file)
  → brand/PRICING.md (pricing answer)

brand/GLOSSARY.md
  → brand/COPY.md (top-of-file)
  → brand/FAQ.md (top-of-file)

brand/TONE.md
  → brand/COPY.md (top-of-file, "Voice and register" reference)
  → brand/GLOSSARY.md (top-of-file)
  → brand/FAQ.md (top-of-file)

brand/PRICING.md
  → brand/MANIFESTO.md (anchor argument)
  → brand/FAQ.md (predictable Q&A)
  → docs/development/.../wave-1-pricing-and-entitlements.md (or equivalent internal doc)

brand/press/README.md
  → brand/BRAND.md (full color system)
  → brand/COPY.md (vocabulary)
  → brand/MANIFESTO.md (positioning)
  → brand/FAQ.md (canonical Q&A)
  → ../LICENSE
```

## Pre-launch handling

Pre-launch state often means certain target docs don't exist yet. Handle each gracefully:

- **PRICING.md may not exist when other docs are authored** — when authoring FAQ in Phase 3, reference PRICING.md in the pricing answer; when PRICING.md ships in a later phase, the link resolves. If PRICING.md is omitted entirely (free product), just state pricing facts inline and don't link.
- **MANIFESTO.md may exist but be a stub** — early manifesto stubs are fine; FAQ answers can reference sections that haven't been written yet (the link will be a broken anchor, but the file exists). Add a TODO marker at the section heading so it's obvious to the user.
- **External public site doesn't exist** — `{{DOMAIN}}/manifesto`, `{{DOMAIN}}/pricing`, `{{DOMAIN}}/press` URLs aren't live. Don't bake them into brand assets until they are; reference the GitHub URL of the doc for now and document the URL convention so when the public site lands, the swap is one find-and-replace.

## Verification script

Run after each phase:

```bash
# Find every target referenced in the brand docs
grep -rEho '\[`?[^]]+`?\]\([^)]+\.md[^)]*\)' brand/ README.md CONTRIBUTING.md SECURITY.md CODE_OF_CONDUCT.md 2>/dev/null \
  | grep -oE '\([^)]+\)' \
  | tr -d '()' \
  | sort -u \
  | while read target; do
      # Resolve relative paths and check existence
      [[ -f "$target" ]] || echo "MISSING: $target"
    done
```

Any output means a cross-link points to a file that doesn't exist. Fix or remove.

## "Topics covered elsewhere" table in COPY.md

This is the primary index for "what doc covers what." Keep it updated as docs are added. Format:

```markdown
| Topic | Lives in | What it covers |
|---|---|---|
| Reusable bios | [`BIOS.md`](BIOS.md) | 50w/100w/250w founder + company; social profile bios |
| Predictable Q&A | [`FAQ.md`](FAQ.md) | 10 canonical answers, 50-150w each |
| Term definitions | [`GLOSSARY.md`](GLOSSARY.md) | Brand vocabulary with cross-references |
| Tone by surface | [`TONE.md`](TONE.md) | Register guide for support / release / tweet / blog / email |
| Pricing language | [`PRICING.md`](PRICING.md) | $X / pass-or-subscription / window / refund |
| Anti-positioning | [`MANIFESTO.md`](MANIFESTO.md) | Long-form positioning argument |
```

When a doc is *(planned)* but not yet shipped, mark with the annotation:

```markdown
| Pricing language | `PRICING.md` *(planned)* | $X / pass / window / refund |
```

When the doc ships, drop the annotation and add the link. Verify all *(planned)* annotations resolve before declaring the brand library complete.
