---
name: fact-checker
description: "Use this skill when verifying factual claims, checking accuracy of statements, or assessing the credibility of information. Trigger phrases: 'fact-check this', 'is this true', 'verify this claim', 'check if this is accurate'. Do NOT use for subjective opinions, legal or medical advice, or claims requiring real-time data or breaking news."
version: 1.0.0
author: community
tags: [research, fact-checking, verification, credibility]
license: MIT
---

# Fact Checker

## Overview
This skill provides a structured approach to evaluating factual claims—assessing whether a statement is accurate, partially accurate, misleading, or false, and explaining *why* with evidence and reasoning. Good fact-checking goes beyond a binary true/false verdict: it identifies the precise claim being made, locates the best available evidence, accounts for context and nuance, and rates confidence appropriately. The output is a clear, evidence-backed assessment that helps readers understand not just whether something is accurate, but why it matters.

## When to Use
- Verifying statistics, quotes, or factual assertions in articles or documents
- Checking whether a viral social media claim holds up to scrutiny
- Assessing whether historical facts cited in writing are accurate
- Auditing factual claims in a draft before publication
- Evaluating whether scientific findings are being accurately reported
- Confirming whether attributed quotes are real and in context
- Vetting claims in speeches, presentations, or marketing copy

## When NOT to Use
- Evaluating subjective opinions or value judgments ("X policy is better than Y")
- Providing legal advice or legal interpretations of statutes
- Providing medical diagnoses or treatment recommendations
- Verifying real-time data such as live stock prices, current weather, or breaking news
- Assessing internal business claims that require proprietary data access
- Deciding which of two contested scientific theories is definitively correct (use `literature-reviewer` skill for contested scientific debates)

## Quick Reference
| Task | Approach |
|------|----------|
| Identify the claim | Isolate the precise factual assertion—strip out opinion and framing |
| Primary sources | Seek original studies, official records, or direct quotes over secondary reports |
| Verdict labels | True / Mostly True / Mixed / Mostly False / False / Unverifiable |
| Context matters | Accurate statistics can still mislead if context is stripped away |
| Quotes | Check original source; confirm attribution, date, and surrounding context |
| Statistics | Verify source, date, sample size, and whether the stat is being applied correctly |
| Confidence level | State confidence (High / Medium / Low) based on source quality and evidence volume |

## Instructions

1. **Isolate the precise claim.** Restate the claim in neutral, specific terms before evaluating it. Many claims contain embedded assumptions or vague language that must be unpacked. "Studies show coffee causes cancer" is not a single claim—it bundles together a specific substance, a causal mechanism, and a category of disease. Break compound claims into individual checkable assertions.

2. **Assess the claim type.** Determine whether this is:
   - A **factual assertion** (a specific, verifiable statement about the world)
   - A **statistical claim** (requires checking source, date, methodology, and applicability)
   - A **quote attribution** (requires locating the original source and verifying wording and context)
   - A **causal claim** (requires evaluating whether evidence supports causation or only correlation)
   - A **historical claim** (requires consulting authoritative historical records)

3. **Identify the best sources.** Rank sources by reliability:
   - **Tier 1:** Peer-reviewed research, official government data, primary documents
   - **Tier 2:** Established news organizations with editorial standards, expert consensus statements
   - **Tier 3:** Reputable secondary sources, encyclopedias, expert interviews
   - **Avoid:** Anonymous posts, sites with known bias and no editorial accountability, single-source claims without corroboration

4. **Evaluate the evidence.** Apply these checks:
   - Does the original source actually say what the claim implies?
   - Is the data current and applicable to the specific context?
   - Are there important caveats or limitations the claim omits?
   - Do other independent sources corroborate or contradict this?

5. **Assess context and framing.** A claim can be technically true but deeply misleading. Check: Is the statistic cherry-picked from a broader dataset? Is the quote taken out of context? Does the claim imply causation from a correlation? Does it generalize from a narrow study to a broad population?

6. **Assign a verdict with confidence level.** Use a clear rating:
   - **True:** Accurate and properly contextualized
   - **Mostly True:** Accurate in substance but missing important nuance or context
   - **Mixed:** Contains both accurate and inaccurate elements
   - **Mostly False:** Misleading framing or significant inaccuracies, though a kernel may be accurate
   - **False:** Contradicted by the best available evidence
   - **Unverifiable:** Cannot be confirmed or denied with available sources
   Also note your **confidence level** (High / Medium / Low) based on the quality and quantity of evidence.

7. **Write the fact-check clearly.** Structure the output as: (1) the claim as stated, (2) the verdict up front, (3) the evidence and reasoning, (4) any important caveats or context. Attribute every piece of evidence to a named source. Avoid weasel words—be direct about what the evidence does and does not show.

## Examples

### Example 1: Statistical Claim Fact-Check

**Input:** "Fact-check this claim: 'The Great Wall of China is the only man-made structure visible from space.'"

**Output:**

---

**Claim:** "The Great Wall of China is the only man-made structure visible from space."

**Verdict:** FALSE
**Confidence:** High

**Evidence and Reasoning:**

This is one of the most persistent myths in popular culture, but it is contradicted by direct observation, physics, and astronaut testimony.

**What astronauts actually report:** Multiple astronauts have specifically addressed this claim. Chinese astronaut Yang Liwei, the first Chinese person in space, stated after his 2003 mission that he could not see the Great Wall. NASA astronaut Ed Lu confirmed this in 2004. Far from supporting the myth, the people best positioned to verify it have consistently denied it.

**The physics:** The Great Wall is, on average, 5–8 meters wide—narrower than a human hair as seen from the International Space Station (roughly 400 km altitude). Visibility at that scale would require impossibly acute vision. NASA's Earth Observatory notes that the wall "would be as difficult to see as a human hair from two miles away."

**What IS visible:** Many man-made features are visible from low Earth orbit under good conditions, including highways, airports, cities, reservoirs, and agricultural fields—all of which are wider than the Wall. From the Moon (385,000 km away), no man-made structure of any kind is visible.

**Origin of the myth:** The claim appears as early as 1932 in Ripley's Believe It Or Not and was repeated in reference books for decades before being widely debunked.

**Sources:** NASA Earth Observatory; Chinese National Space Administration statements; Liu Yang and Yang Liwei mission reports (2003, 2012).

---

### Example 2: Quoted Statistic Fact-Check

**Input:** "Someone cited this statistic in a presentation: 'We only use 10% of our brains.' Is this true?"

**Output:**

---

**Claim:** "Humans only use 10% of their brains."

**Verdict:** FALSE
**Confidence:** High

**Evidence and Reasoning:**

This claim has no basis in neuroscience and is contradicted by multiple independent lines of evidence.

**Brain imaging data:** Functional MRI and PET scan studies show that virtually all brain regions are active over the course of a day. While not every neuron fires simultaneously (which would cause a seizure), there is no dormant 90% waiting to be unlocked. A 2014 University of Western Ontario study explicitly tested this myth and found activity throughout the brain during normal function.

**Evolutionary evidence:** The human brain accounts for approximately 2% of body weight but consumes 20% of the body's energy at rest. Evolution would not sustain such a metabolically expensive organ if 90% were unused.

**Clinical neurology:** Brain damage from strokes, tumors, or injury to virtually any region produces measurable deficits. If 90% were unused, damage to most areas should have no effect—which is not observed.

**The myth's origin:** No credible scientific source has been identified as the origin. It has been falsely attributed to Albert Einstein (no record of him saying it exists), and may derive from misunderstandings of early neuroscience research distinguishing glial cells from neurons, or from self-help literature of the early 20th century.

**The accurate picture:** Different regions are specialized for different functions, and humans use all of them—though not all simultaneously. Expertise and learning strengthen specific neural pathways, but this is optimization, not "unlocking" unused capacity.

**Sources:** Barry Beyerstein, "Whence Cometh the Myth that We Only Use 10% of our Brains?" (1999); Neuroimaging research, University of Western Ontario (2014); Scientific American (multiple articles).

---

### Example 3: Nuanced/Mixed Verdict

**Input:** "Fact-check: 'Violent crime in the US has been increasing every year for the past decade.'"

**Output:**

---

**Claim:** "Violent crime in the US has been increasing every year for the past decade."

**Verdict:** MOSTLY FALSE
**Confidence:** Medium

**Evidence and Reasoning:**

The claim is contradicted by the overall trend but contains a kernel of truth related to recent years.

**The long-term trend:** FBI Uniform Crime Report data and Bureau of Justice Statistics victimization surveys both show that violent crime in the US peaked around 1991 and declined dramatically through the 2010s. In 2019, violent crime rates were near 30-year lows. The claim that crime has been *increasing every year for the past decade* is flatly wrong as a description of the 2013–2023 period.

**Where it gets complicated:** There were notable increases in homicide specifically in 2020 and 2021—likely related to COVID-19 pandemic disruptions—that drew significant media attention. Some cities also saw increases in certain crime categories. However, these were not "every year" and did not represent a consistent decade-long trend. Preliminary 2022–2023 data suggest homicides declined again in many cities.

**Measurement caveats:** Crime statistics are imperfect. The FBI's transition to a new reporting system (NIBRS) in 2021 created a gap in data from non-reporting agencies that complicates year-over-year comparisons. Reported crime and experienced crime (per victimization surveys) sometimes diverge based on reporting rates.

**Verdict summary:** The claim exaggerates recent increases and ignores the 30-year decline. Saying violent crime "has been increasing every year for the past decade" is not supported by the data. More accurate: violent crime fell steadily through the mid-2010s, spiked in 2020–2021 (particularly homicide), and has since partially reversed.

**Sources:** FBI Uniform Crime Report 2022; Bureau of Justice Statistics National Crime Victimization Survey 2022; Brennan Center for Justice crime data analysis.

---

## Best Practices
- Always restate the claim in precise, neutral terms before evaluating—many claims are vague or bundled
- Lead with the verdict, then provide the reasoning—don't make readers wade through evidence to find your conclusion
- Distinguish correlation from causation explicitly when the claim implies causation
- Use the most direct, primary source available—don't cite a news article if you can cite the study it covers
- Quantify your confidence—saying "High confidence" vs "Low confidence" signals important uncertainty to readers
- When a claim is partially true, explain exactly which part is true and which is not
- Be direct: avoid hedging so much that the verdict is unclear

## Common Mistakes
- **Fact-checking the wrong claim:** Evaluating a related but different claim than the one actually made
- **Stopping at "technically true":** A claim can be technically accurate but still deeply misleading—evaluate framing too
- **Single-source verification:** Confirming a claim from only one source, especially when that source is the same one cited in the original claim
- **False balance:** Treating fringe views as equivalent to scientific consensus in the name of "both sides"
- **Scope mismatch:** A study from a specific population or country doesn't verify a universal claim
- **Ignoring the date:** An accurate statistic from 10 years ago may be outdated and no longer accurate
- **Verdict without reasoning:** Stating a verdict without showing the evidence and logic behind it

## Tips & Tricks
- For quote attributions, search the exact phrase in quotation marks and look for the primary source, not secondary reports
- When checking statistics, always ask: who collected this data, when, from what population, using what methodology?
- The original study abstract (and especially limitations section) often reveals important caveats that secondary reports omit
- Use reverse image search for photos and videos being presented as evidence of recent events
- High-confidence verdicts require at least two independent, high-quality sources
- If a claim seems too perfectly suited to confirm someone's beliefs, apply extra scrutiny—motivated reasoning produces motivated evidence-seeking
- Document your sources as you go; reconstructing a citation trail after the fact is tedious and error-prone

## Related Skills
- [web-researcher](../../research/web-researcher/SKILL.md)
- [literature-reviewer](../../research/literature-reviewer/SKILL.md)
- [summarizer](../../research/summarizer/SKILL.md)
- [proofreader](../../writing/proofreader/SKILL.md)
