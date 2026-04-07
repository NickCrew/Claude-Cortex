---
name: proofreader
description: "Use this skill when reviewing written content for grammar, spelling, punctuation, style consistency, and tone—before publishing, submitting, or sending. Trigger phrases: 'proofread this', 'check my writing', 'review this for errors', 'edit this email/report/essay'. Do NOT use when structural rewrites or content changes are needed—proofreading fixes surface errors, not substantive problems."
version: 1.0.0
author: community
tags: [writing, proofreading, editing, grammar]
license: MIT
---

# Proofreader

## Overview
This skill catches grammar errors, spelling mistakes, punctuation problems, inconsistent style, and tone mismatches in any written content—emails, reports, blog posts, essays, or marketing copy. It distinguishes between proofreading (surface-level errors) and copy editing (structural issues), applies common style guide rules, and flags commonly confused words. The output is a corrected version of the text with explanations of changes, or a marked-up list of issues depending on your preference.

## When to Use
- Final review before publishing a blog post or article
- Checking an important email before sending
- Reviewing a business report or proposal for errors
- Polishing an essay or academic paper
- Auditing marketing copy for consistency and tone
- Verifying consistency in longer documents (capitalization, hyphenation, terminology)

## When NOT to Use
- When the content needs to be restructured, reorganized, or substantially rewritten (that's developmental or copy editing)
- When the content is a rough draft that hasn't been reviewed by the author yet—proofread the near-final version
- For technical accuracy checking (confirming facts, code correctness, data)
- When you need a completely new version of the content

## Quick Reference
| Task | Approach |
|------|----------|
| Grammar | Check subject-verb agreement, tense consistency, dangling modifiers |
| Punctuation | Oxford comma, em dash usage, apostrophes, semicolons |
| Commonly confused | affect/effect, its/it's, their/there/they're, that/which, who/whom |
| Style consistency | Capitalization, hyphenation, number formatting, terminology |
| Tone check | Formal/casual match, second-person consistency, active/passive balance |
| Markup | Strikethrough deleted text, bold/bracket insertions |

## Instructions

1. **Clarify the style guide and tone.** Before proofreading, establish:
   - Style guide: AP, Chicago, MLA, APA, or house style?
   - Audience tone: formal, professional-casual, or informal?
   - Any document-specific conventions (e.g., always capitalize "Team" when referring to the product)?

2. **Read for meaning first, errors second.** On the first pass, read the entire piece to understand what it's trying to say. This prevents "correcting" deliberate stylistic choices.

3. **Check grammar systematically.** Focus on:
   - **Subject-verb agreement:** "The data show" (data is plural) vs. "The data shows"
   - **Tense consistency:** Don't switch between past and present within the same section
   - **Dangling modifiers:** "Having finished the report, the coffee was cold." (Who finished the report? Not the coffee.)
   - **Sentence fragments:** Incomplete sentences without a main verb
   - **Run-on sentences:** Two independent clauses joined without proper punctuation

4. **Check punctuation.**
   - **Oxford comma:** "We invited the manager, the developer, and the designer." (Use unless house style forbids it)
   - **Apostrophes:** Possessives (it's = it is; its = possessive), plurals never get apostrophes
   - **Em dashes vs. en dashes:** Em dash (—) for breaks in thought; en dash (–) for ranges (2019–2023)
   - **Semicolons:** Connect two complete, related independent clauses
   - **Comma splices:** "I finished the report, it looked great." → Use a period, semicolon, or conjunction

5. **Flag commonly confused words:**
   | Confused Pair | Rule |
   |---------------|------|
   | affect / effect | Affect = verb (to influence); Effect = noun (the result) |
   | its / it's | its = possessive; it's = it is |
   | their / there / they're | possessive / location / they are |
   | that / which | "that" restricts (no comma); "which" adds info (comma before it) |
   | who / whom | who = subject; whom = object |
   | fewer / less | fewer = countable; less = uncountable |
   | lay / lie | lay = to place something; lie = to recline |
   | complement / compliment | complement = completes; compliment = praise |
   | principal / principle | principal = main/head person; principle = rule/value |
   | further / farther | farther = physical distance; further = metaphorical |

6. **Check style consistency throughout the document:**
   - Capitalization: Is "Director" always capitalized? Or never?
   - Numbers: Spell out one through nine, numerals for 10+? Or always numerals?
   - Hyphenation: "email" or "e-mail"? "decision-maker" or "decision maker"?
   - Serial comma: used consistently throughout?
   - Terminology: Same word used for the same concept every time?

7. **Check tone and register.**
   - Does the formality level match the audience and context?
   - Is second-person ("you") used consistently where applicable?
   - Are there shifts from active to passive that weaken the writing?
   - Does the tone stay consistent, or does it veer between professional and overly casual?

8. **Output format.** Choose one:
   - **Corrected version:** Full rewritten text with all errors fixed (best for clean final copy)
   - **Marked-up version:** Original text with inline corrections using conventions (best for showing what changed)
   - **Error report:** Bulleted list of issues with original → corrected for each (best for learning/feedback)

## Examples

### Example 1: Proofreading a Business Report Paragraph

**Input:**
"The team have successfully completed the Q3 objectives, which was a significant achievement given the projects complexity. Going forward, we need to focus on improving our response times, their currently averaging 48 hours which effects customer satisfaction scores. Its important that each team member understand there role in achieving this target by years end."

**Output:**

**Corrected Version:**
"The team has successfully completed the Q3 objectives, which was a significant achievement given the project's complexity. Going forward, we need to focus on improving our response times—they're currently averaging 48 hours, which affects customer satisfaction scores. It's important that each team member understands their role in achieving this target by year's end."

**Changes Made:**
1. "have → has" — "team" is treated as a singular collective noun in American English
2. "projects → project's" — possessive requires apostrophe
3. "their → they're" — contraction of "they are"
4. "which effects → which affects" — "affects" (verb) is correct here; "effect" would be the noun
5. "Its → It's" — contraction of "it is"
6. "understand → understands" — subject "each team member" is singular
7. "there → their" — possessive pronoun for "their role"
8. "years end → year's end" — possessive requires apostrophe
9. Added em dash before "they're" to improve flow and separate the clause clearly

---

### Example 2: Proofreading a Professional Email

**Input:**
"Hi Marcus,

Thanks for meeting with myself and Sarah yesterday, we really enjoyed the conversation. Going forward I think theirs a real opportunity here for both our organizations. We would love to setup a more formal call to discuss the specifics of the proposal that was presented by you.

Looking forward to hearing your thoughts,
Jennifer"

**Output:**

**Corrected Version:**
"Hi Marcus,

Thanks for meeting with Sarah and me yesterday—we really enjoyed the conversation. Going forward, I think there's a real opportunity here for both of our organizations. We'd love to set up a more formal call to discuss the specifics of your proposal.

Looking forward to hearing your thoughts,
Jennifer"

**Changes Made:**
1. "myself and Sarah → Sarah and me" — "myself" is reflexive and only correct when the subject is "I" (e.g., "I did it myself"). "Me" is the object form. Conventionally, put yourself last.
2. "yesterday, we → yesterday—we" — Comma splice fixed with em dash for better flow
3. "Going forward I → Going forward, I" — Introductory phrase needs a comma
4. "theirs → there's" — Contraction of "there is"
5. "both our → both of our" — More natural phrasing
6. "setup → set up" — "setup" is a noun; the verb phrase is "set up"
7. "the proposal that was presented by you → your proposal" — Active voice; removes wordiness

---

## Best Practices
- Proofread in a different medium than you wrote—print it out, or change the font size; errors become more visible
- Read backwards (last sentence to first) to catch spelling errors your brain auto-corrects when reading for meaning
- Proofread in multiple focused passes: one for grammar, one for punctuation, one for style consistency
- Take a break between writing and proofreading—fresh eyes catch more
- For long documents, proofread in sections, not in one marathon session
- Use text-to-speech to hear the text; awkward phrasing is easier to detect by ear

## Common Mistakes
- **Correcting intentional style choices:** Some fragments and comma breaks are deliberate—confirm before "fixing"
- **Over-correcting to formal:** If the original tone is casual and appropriate, don't stiffly formalize it
- **Missing errors at page/section breaks:** Attention naturally resets; these transitions need extra scrutiny
- **Not checking headers and captions:** These are often proofread last (or not at all) and contain errors
- **Skipping numbers and data:** Wrong dates, percentages, and figures slip through when proofreaders focus on prose
- **Fixing the same error inconsistently:** If "e-mail" appears 10 times and you change it to "email", change all 10

## Tips & Tricks
- Use the "CMOS test" for who/whom: substitute he/him. If "he" sounds right, use "who"; if "him" sounds right, use "whom"
- For affect/effect: Remember "RAVEN" — Remember Affect Verb Effect Noun
- Check whether the document uses one space or two after periods—it should be consistent (one is the modern standard)
- Confirm that all headers are parallel in structure (all noun phrases, or all imperative verbs, not a mix)
- In formal documents, verify that all abbreviations are spelled out on first use: "artificial intelligence (AI)"
- Search-and-replace is your friend for consistency: find every instance of "email" to ensure uniform spelling

## Related Skills
- [blog-post](../../writing/blog-post/SKILL.md)
- [email-drafter](../../writing/email-drafter/SKILL.md)
- [academic-essay](../../writing/academic-essay/SKILL.md)
- [technical-writer](../../writing/technical-writer/SKILL.md)
