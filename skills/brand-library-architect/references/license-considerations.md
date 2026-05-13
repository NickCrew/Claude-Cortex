# License considerations

Which open-source convention files to ship and how CONTRIBUTING reads, per license choice. Reference for Phase 4 (repo conventions).

## License → conventions matrix

| License | README license badge | CONTRIBUTING | SECURITY | CODE_OF_CONDUCT |
|---|---|---|---|---|
| AGPL-3.0 | AGPL-3.0 | ✓ ship | ✓ ship | ✓ ship |
| GPL-3.0 | GPL-3.0 | ✓ ship | ✓ ship | ✓ ship |
| Apache-2.0 | Apache-2.0 | ✓ ship | ✓ ship | ✓ ship |
| MIT | MIT | ✓ ship | ✓ ship | ✓ ship |
| BSD-3-Clause | BSD-3-Clause | ✓ ship | ✓ ship | ✓ ship |
| Source-available | Source-available | ✗ skip | ✓ ship (adjust) | ✗ skip |
| Proprietary | (omit badge) | ✗ skip | ✓ ship (adjust) | ✗ skip |

## CONTRIBUTING.md license-specific stance

The "AGPL contribution stance" section of the template needs adapting per license. Replace `{{LICENSE_STANCE}}` with the appropriate text:

### AGPL-3.0 stance

```markdown
## AGPL contribution stance

By submitting a contribution to this repo, you agree:

- Your contribution is licensed under **AGPL-3.0** (the same license
  as the project).
- You have the right to license the contribution under AGPL — i.e.,
  it's your work, or you have permission from the rights-holder.
- You understand the AGPL's network-use clause: anyone running a
  modified version of the product as a service must make their
  modified source available to users of that service.

The AGPL is deliberate. {{PRODUCT_NAME}} is a tool that handles
{{DATA_SENSITIVITY_DESCRIPTION}}; we want everyone running modified
versions to be subject to the same data-ownership stance the upstream
takes.
```

### GPL-3.0 stance

```markdown
## GPL contribution stance

By submitting a contribution, you agree:

- Your contribution is licensed under **GPL-3.0** (the same license as the project).
- You have the right to license the contribution under GPL — i.e., it's your work, or you have permission from the rights-holder.
- You understand the GPL's copyleft clause: derivative works distributed must also be GPL-licensed.
```

### Apache-2.0 stance

```markdown
## Apache 2.0 contribution stance

By submitting a contribution, you agree:

- Your contribution is licensed under **Apache-2.0** (the same license as the project).
- You have the right to license the contribution under Apache-2.0 — i.e., it's your work, or you have permission from the rights-holder.
- The Apache license includes a patent grant — by contributing, you grant a patent license for your contribution.

If your employer has IP claims on your work, ensure they're aware and consenting before contributing.
```

### MIT / BSD stance

```markdown
## MIT contribution stance

By submitting a contribution, you agree:

- Your contribution is licensed under **MIT** (the same license as the project).
- You have the right to license the contribution under MIT — i.e., it's your work, or you have permission from the rights-holder.
```

### Source-available / proprietary

CONTRIBUTING.md should not be shipped for proprietary code unless there's a real CLA / contribution process. If it ships, make explicit that contributions are on an inbound-license basis (typically the company keeps the rights but the contributor retains attribution).

## CODE_OF_CONDUCT.md considerations

The Contributor Covenant 2.1 is the de facto standard. Ship it for any OSS project regardless of license. Adopt by reference (don't embed verbatim — the explicit harassment-type enumeration triggers content filtering on output).

For proprietary projects with a contribution process, an internal code-of-conduct may already exist; defer to it.

## SECURITY.md

Ship for any project with public exposure (OSS or proprietary). Tailor:

- **Open-source:** scope includes the codebase, deployed instances, AI proxy if any, CI/CD config in the repo.
- **Proprietary:** scope is the deployed product / API; codebase is internal. Reporting flow is the same.
- **Self-hosted-only OSS:** add a note that operator-deployed instances are operator's responsibility (though structural issues in the upstream code are reportable).

## License selection guidance

If the user is undecided on license, briefly elicit:

- **Aggressive copyleft (AGPL):** when the product's hosted version is the canonical version and SaaS forks shouldn't capture value without contributing back.
- **Standard copyleft (GPL):** when distribution-time copyleft is enough.
- **Commercial-friendly OSS (Apache-2.0):** when adoption depends on enterprise / commercial use being friction-free.
- **Maximally permissive (MIT / BSD):** when the goal is reach and downstream creativity, not reciprocity.
- **Source-available:** when source visibility matters but commercial protection matters more.
- **Proprietary:** when source isn't shared.

This is a real decision that affects business model viability. If the user is unsure, point them at choosealicense.com or surface that the answer depends on their commercial strategy.
