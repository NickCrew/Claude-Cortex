---
name: dataset-curator
description: Use this skill when designing, cleaning, deduplicating, or documenting datasets for model training and evaluation including schema design, class imbalance handling, and train/val/test splits. Not for running model training or hyperparameter tuning. Not for real-time data pipeline engineering.
version: 1.0.0
author: community
tags:
  - ai
  - dataset
  - machine-learning
  - data-curation
license: MIT
keywords:
  - dataset curation
  - data cleaning
  - train test split
  - class imbalance
  - dataset
  - curator
  - dataset curator
---

# Dataset Curator

## Overview
This skill covers the full lifecycle of dataset creation and curation for machine learning and LLM tasks. It addresses dataset schema design, data collection strategies, quality filtering, deduplication, class imbalance mitigation, stratified train/val/test splits, annotation guideline writing, and dataset card documentation. Good datasets are the foundation of reliable models — this skill helps teams avoid the most common data quality pitfalls that lead to poor generalization, evaluation leakage, and biased models.

## When to Use
- Designing a new dataset schema for a classification, extraction, or generation task
- Cleaning and deduplicating a raw dataset before model training
- Planning annotation guidelines for human labelers or LLM-assisted labeling
- Addressing class imbalance in a training set (oversampling, undersampling, weighting)
- Creating stratified train/val/test splits without leakage between splits
- Writing a dataset card (model card for data) for reproducibility and documentation
- Auditing an existing dataset for quality, coverage, and potential biases
- Combining multiple data sources into a single unified dataset

## When NOT to Use
- Training or fine-tuning a model (use model training skills)
- Running SQL or analytical queries on a production database (use data analysis skills)
- Building real-time data pipelines or streaming ETL (use data engineering skills)
- Designing evaluation suites for deployed LLMs (use eval-designer skill)
- Web scraping or data collection from APIs (use data collection skills)

## Quick Reference
| Task | Approach |
|------|----------|
| Define dataset schema | List fields, types, required vs optional, allowed values, and examples |
| Remove duplicates | Hash-based exact dedup + MinHash/LSH for near-duplicate detection |
| Fix class imbalance | Oversample minority (SMOTE) or undersample majority; adjust loss weights |
| Create train/val/test splits | Stratified split by label; ensure no overlap of entities across splits |
| Document the dataset | Write a dataset card with provenance, schema, statistics, and limitations |
| Validate annotation quality | Compute inter-annotator agreement (Cohen's kappa or Krippendorff's alpha) |
| Handle missing values | Decide per-field: impute, drop row, or add "unknown" category |
| Detect label noise | Use confident learning (cleanlab) or cross-validation outlier detection |

## Instructions

1. **Define the task and schema** — Before collecting any data, write the schema: every field name, data type, allowed values, and whether it is required. For classification datasets, enumerate all valid labels and their definitions. Ambiguous schemas cause inconsistent annotations and training failures.

2. **Establish collection strategy** — Determine the data source: human-annotated, LLM-generated, web-scraped, synthetic, or a combination. Document collection date, source URLs, licenses, and any sampling decisions. Ensure the collection covers the full input distribution the model will encounter in production.

3. **Write annotation guidelines** — Create a guideline document for labelers that defines every label, provides positive and negative examples for each, and includes decision rules for edge cases. Pilot the guidelines with 2–3 annotators on a sample of 50 items and iterate before full annotation begins.

4. **Run quality filtering** — Remove items that are too short, too long, contain encoding errors, are in the wrong language, or fail domain-specific quality checks. Log how many items were removed at each filter step and why. Preserve a raw snapshot before filtering.

5. **Deduplicate the dataset** — Apply exact deduplication first (hash the text or key fields). Then apply near-duplicate detection using MinHash + LSH (e.g., `datasketch` library) or sentence embedding cosine similarity. Aim to remove items with >80% overlap. Keep the highest-quality copy when deduplicating.

6. **Assess and address class imbalance** — Compute class distribution. If any class has less than 5% of the majority class count, consider: (a) collecting more data for minority classes, (b) oversampling with augmentation, (c) applying class weights in the loss function, or (d) using stratified sampling. Document the chosen approach and its rationale.

7. **Create stratified splits** — Split data into train/val/test sets preserving class distribution in each split. Use an 80/10/10 or 70/15/15 ratio as a starting point. For datasets with identifiable entities (users, documents, companies), ensure the same entity never appears in multiple splits to prevent leakage. Test set must remain untouched until final evaluation.

8. **Measure annotation quality** — For human-labeled data, compute inter-annotator agreement on a sample (at least 10% of the dataset labeled by 2+ annotators). Cohen's kappa > 0.7 is acceptable; < 0.6 indicates guideline issues. Resolve disagreements through adjudication, not random selection.

9. **Audit for biases and coverage gaps** — Analyze the dataset across demographic attributes, time periods, domains, and edge cases. Identify over-represented and under-represented slices. Document known limitations in the dataset card. If possible, compare distribution to real production data.

10. **Write the dataset card** — Document: dataset name, version, task, schema, collection methodology, source licenses, size (rows and tokens), class distribution, split sizes, known limitations and biases, and citation. Use the Hugging Face dataset card format for compatibility with the ecosystem.

## Examples

### Example 1: Text Classification Dataset Design for Customer Intent Detection
**Input:** A support team wants to train a model to classify customer emails into 8 intent categories: billing, refund, technical-issue, account-access, product-question, cancellation, complaint, and other.

**Output:**

**Schema definition:**
```json
{
  "id": "string (UUID)",
  "text": "string (customer email body, min 10 chars, max 2000 chars)",
  "label": "enum: [billing, refund, technical-issue, account-access, product-question, cancellation, complaint, other]",
  "confidence": "float 0.0–1.0 (annotator confidence)",
  "annotator_id": "string",
  "annotation_date": "ISO 8601 date",
  "source": "enum: [zendesk, email-archive, synthetic]"
}
```

**Collection plan:**
- Export 5,000 historical support tickets from Zendesk (past 12 months)
- Strip PII: replace names with `[NAME]`, emails with `[EMAIL]`, account numbers with `[ACCT]`
- Target distribution: at least 300 examples per class (aim for balanced; use augmentation for rare classes)

**Annotation guidelines excerpt:**
```
Label: "refund"
Definition: Customer is requesting money back for a purchase.
Positive examples:
  - "I'd like a refund for my order from last week"
  - "Please return the charge to my credit card"
Negative examples (do NOT label as refund):
  - "I want to exchange my item" → label as product-question
  - "Why was I charged twice?" → label as billing
Edge case: "I want to cancel and get my money back" → label as cancellation (intent is to cancel)
```

**Deduplication approach:**
```python
from datasketch import MinHash, MinHashLSH

def get_minhash(text, num_perm=128):
    m = MinHash(num_perm=num_perm)
    for word in text.lower().split():
        m.update(word.encode('utf8'))
    return m

lsh = MinHashLSH(threshold=0.8, num_perm=128)
# Add items and query for near-duplicates; keep only one per cluster
```

**Split strategy:**
```
Total: 5,200 items (after dedup and filtering)
Train: 4,160 (80%) — stratified by label
Val:   520  (10%) — stratified by label
Test:  520  (10%) — stratified by label; set aside immediately, not used for development
```

### Example 2: Image Dataset Curation Plan for Defect Detection
**Input:** A manufacturing team wants to train a binary classifier to detect product defects from camera images. They have 10,000 raw images, but only ~400 are defective.

**Output:**

**Schema definition:**
```
image_id:    string (factory_line + timestamp)
image_path:  string (relative path to image file)
label:       enum: [defective, non-defective]
defect_type: enum: [scratch, dent, discoloration, missing-component, none] (sub-type for defective)
image_width: int (pixels)
image_height: int (pixels)
capture_date: ISO 8601 date
production_line: string
annotated_by: string (annotator ID or "automated")
```

**Quality filtering rules:**
- Remove images where the product is not centered (bounding box check)
- Remove blurry images (Laplacian variance < 100 threshold)
- Remove images with wrong resolution (must be 1280×960 ± 10%)
- Remove duplicates from the same second on the same camera (likely duplicate frames)

**Class imbalance strategy:**
```
Original: 9,600 non-defective, 400 defective (24:1 imbalance)

Option 1 — Data augmentation for minority class:
  Apply: horizontal flip, ±15° rotation, brightness ±20%, add Gaussian noise
  Target: 2,000 defective images (5× augmentation)
  Result: 9,600 non-defective, 2,000 defective (4.8:1 ratio) — more manageable

Option 2 — Class weighting (simpler, use if augmentation is not feasible):
  class_weight = {0: 1.0, 1: 24.0}  # inverse frequency weighting
  Apply in model training loss function

Recommendation: Use both — augment to 2,000 AND apply 4.8:1 class weight
```

**Dataset card excerpt:**
```yaml
Dataset Name: Manufacturing Defect Detection v1.2
Task: Binary image classification (defective / non-defective)
Size: 11,600 images (9,600 non-defective, 2,000 defective after augmentation)
Source: Factory line cameras, Line A and Line B, 2024-01 to 2024-06
License: Internal use only (proprietary)
Known Limitations:
  - Only covers Lines A and B; Line C has different lighting conditions
  - Defective samples over-represent scratches (60% of defects)
  - No samples from night shift (different ambient light)
Split: Train 80% / Val 10% / Test 10% (stratified by label and production line)
```

## Best Practices
- Always freeze the test set before any experimentation — never iterate on test set performance
- Document the data collection date and source version — datasets drift over time
- Use UUIDs for item IDs, not sequential integers — they are stable across merges and re-runs
- Store the raw data alongside the processed data — you will need to reprocess with new filters
- Measure and report inter-annotator agreement before training — low agreement means low ceiling
- For NLP tasks, ensure your tokenizer sees the dataset's actual vocabulary before finalizing splits
- Use a random seed and record it — reproducibility is critical for debugging dataset issues
- When using LLM-generated labels, always validate a sample with human reviewers

## Common Mistakes
- Mixing entities across splits (e.g., same user in train and test) — causes evaluation leakage
- Forgetting to normalize text before deduplication (lowercasing, whitespace) — misses duplicates
- Applying augmentation before splitting — augmented versions of train items may leak into test
- Treating "50% accuracy" as a failure without checking if the majority class is 50% of data
- Using accuracy as the only metric for imbalanced datasets — use F1, precision-recall curves
- Labeling with only one annotator and assuming perfect quality — always do agreement checks
- Not versioning the dataset — future model iterations can't be compared fairly

## Tips & Tricks
- Use `cleanlab` to automatically detect likely mislabeled examples in existing datasets
- For text deduplication at scale, MinHash LSH is far faster than pairwise cosine similarity
- Hugging Face `datasets` library handles streaming, caching, and map operations efficiently for large datasets
- Add a `data_source` field to every item — it's invaluable when debugging distribution shift
- Always visualize your dataset: class distribution histograms, length distributions, temporal trends
- When augmenting, ensure augmented items are marked with an `augmented: true` flag for traceability
- For annotation, use Label Studio or Prodigy for efficient tooling with built-in agreement metrics

## Related Skills
- [prompt-engineer](../prompt-engineer/SKILL.md)
- [eval-designer](../eval-designer/SKILL.md)
- [model-comparator](../model-comparator/SKILL.md)
