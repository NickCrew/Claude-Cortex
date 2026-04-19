---
name: terms-of-service
description: Use this skill when you need to draft Terms of Service, a Privacy Policy, or an End-User License Agreement (EULA) for a web application, SaaS product, or mobile app. Produces comprehensive, plain-English legal documents that cover user rights, data practices, liability limits, and dispute resolution. Not a substitute for a licensed attorney; have a lawyer review before publishing for a production product.
version: 1.0.0
author: community
tags:
  - legal
  - terms-of-service
  - privacy-policy
  - saas
license: MIT
keywords:
  - Terms of Service
  - Privacy Policy
  - EULA
  - terms
---

# Terms of Service

## Overview
This skill generates well-structured, comprehensive Terms of Service (ToS), Privacy Policies, and End-User License Agreements (EULAs) tailored to web applications, SaaS platforms, and mobile apps. The drafts cover the full range of standard legal topics: user eligibility and account terms, acceptable use, intellectual property, payment and subscription terms, data handling and privacy, disclaimers and limitation of liability, termination, and dispute resolution. Outputs are written in clear, modern language that is accessible to users while remaining legally substantive. All drafts should be reviewed and adapted by a licensed attorney before publication.

## When to Use
- Launching a new SaaS product, web app, or mobile app that requires user-facing legal agreements
- Updating outdated ToS to reflect new features, business models, or regulatory requirements (GDPR, CCPA, COPPA)
- Drafting a standalone Privacy Policy for a product that collects any user data
- Creating a EULA for downloadable software or a mobile application
- Developing an Acceptable Use Policy (AUP) for a platform with user-generated content
- Building a legal agreements page that consolidates ToS, Privacy Policy, and Cookie Policy

## When NOT to Use
- As a final, legally reviewed document without attorney review for any production product
- For highly regulated industries (healthcare/HIPAA, financial services/FINRA, children's products/COPPA) without specialized legal counsel
- When you need jurisdiction-specific compliance advice (e.g., EU GDPR Data Processing Agreements, CCPA service provider addenda)
- To document agreements between businesses (B2B contracts) — use a services agreement or MSA instead
- For open-source software licenses (use established SPDX licenses instead)

## Quick Reference
| Document | Purpose | Key Sections |
|----------|---------|--------------|
| Terms of Service | Governs user relationship with the service | Eligibility, acceptable use, IP, payment, liability, termination, disputes |
| Privacy Policy | Explains data collection, use, and user rights | Data collected, legal basis, third-party sharing, retention, user rights, contact |
| EULA | Governs license to use software | License grant, restrictions, IP ownership, warranty disclaimer, termination |
| Acceptable Use Policy | Defines prohibited user behaviors | Prohibited content/actions, enforcement, reporting |
| Cookie Policy | Explains cookie use and consent | Cookie types, purpose, opt-out mechanism |

## Instructions

1. **Gather product context before drafting** — Collect: product name, company name and jurisdiction, product type (SaaS, mobile app, marketplace, API), data collected from users, subscription/payment model (free, freemium, paid tiers), target audience (consumers, businesses, children?), and key features that may have specific legal implications (AI/ML, UGC, payments, health data).

2. **Draft the Terms of Service using this standard structure:**
   - **Acceptance of Terms** — How users agree (clickwrap, browsewrap); age/eligibility requirements
   - **Description of Service** — What the product does; scope of service
   - **Account Registration and Security** — Account creation, credential responsibility, account suspension
   - **Acceptable Use Policy** — Prohibited conduct, prohibited content, enforcement rights
   - **Intellectual Property** — Company IP ownership; license grant to users; user-generated content license back to company
   - **Payment and Subscription Terms** — Pricing, billing cycles, auto-renewal, refund policy, price changes
   - **Privacy** — Reference to Privacy Policy; GDPR/CCPA compliance statement if applicable
   - **Disclaimers of Warranties** — "As-is" disclaimer; no guarantee of uptime or results
   - **Limitation of Liability** — Liability cap (typically fees paid in last 12 months); exclusion of consequential damages
   - **Indemnification** — User indemnifies company for user's misuse or content
   - **Termination** — Grounds for termination; effect of termination; data export window
   - **Dispute Resolution** — Arbitration clause, class-action waiver, governing law, jurisdiction
   - **Changes to Terms** — How changes are communicated; continued use = acceptance
   - **Contact Information** — Legal contact email/address

3. **Draft the Privacy Policy using this standard structure:**
   - **Information Collected** — Categories: account data, usage data, device data, cookies, third-party data
   - **Legal Basis for Processing** (required for GDPR) — Consent, contract performance, legitimate interest
   - **How Information Is Used** — Service delivery, analytics, marketing, legal compliance
   - **Information Sharing** — Service providers, analytics vendors, payment processors; no selling of personal data (or disclose if sold per CCPA)
   - **Data Retention** — How long data is kept; deletion policy
   - **Security** — Reasonable security measures; breach notification commitment
   - **User Rights** — Access, correction, deletion (right to be forgotten), portability, objection, opt-out of sale
   - **Children's Privacy** — COPPA compliance; no knowing collection from users under 13
   - **International Transfers** — Standard contractual clauses or other mechanisms for cross-border transfers
   - **Contact / DPO Information** — How to exercise rights; Data Protection Officer if applicable

4. **Draft the EULA (if applicable) covering:**
   - License grant (personal, non-exclusive, non-transferable, revocable)
   - License restrictions (no reverse engineering, no sublicensing, no commercial use if free tier)
   - IP ownership (all rights reserved to licensor)
   - Updates and support terms
   - Warranty disclaimer and limitation of liability
   - Termination on breach

5. **Tailor for jurisdiction and audience** — Add GDPR-specific sections (legal basis, DPO, data subject rights) for EU users; add CCPA-specific sections (right to know, opt-out of sale, non-discrimination) for California users; add COPPA language if any users may be under 13.

6. **Apply plain-language principles** — Use short sentences. Avoid Latin phrases. Define jargon on first use. Use "you" for the user and "we" or "[Company Name]" for the company. Use active voice.

7. **Add version control and effective dates** — Every legal document must include a version number and effective date at the top. Include a changelog or "last updated" date. Explain how users will be notified of changes.

8. **Review for completeness against a checklist** — Confirm the ToS includes all 14 sections listed in step 2; the Privacy Policy includes all 10 sections in step 3; the EULA includes all 7 items in step 4.

9. **Add a prominent disclaimer at the top of the draft** — Note that the document is a template draft requiring attorney review before publication.

10. **Recommend legal review triggers** — Flag specific circumstances that require mandatory attorney review: collecting health data (HIPAA), financial data (GLBA), operating in the EU (GDPR DPA), serving children under 13 (COPPA), processing payments (PCI DSS), or operating in highly regulated industries.

## Examples

### Example 1: Terms of Service for a B2C SaaS Project Management App
**Input:**
"Draft a Terms of Service for 'Taskflow,' a SaaS project management app. Company: Taskflow Inc., incorporated in Delaware. Users are adults (18+), primarily individual professionals and small business teams. Free tier and $12/month paid tier. Users create projects, tasks, and can share files. We store user data on AWS US-East. No AI features. Governing law: Delaware."

**Output (excerpt — key sections):**

---
**TASKFLOW TERMS OF SERVICE**
*Effective Date: [DATE] | Version 1.0*

> ⚠️ **Draft Template** — This document requires review by a licensed attorney before publication.

**1. Acceptance of Terms**
By creating an account or using Taskflow ("Service"), you ("User") agree to these Terms of Service ("Terms") and our Privacy Policy. If you are using the Service on behalf of a business, you represent that you have authority to bind that business to these Terms. You must be at least 18 years old to use the Service.

**2. Description of Service**
Taskflow provides a cloud-based project and task management platform that allows users to create projects, assign tasks, collaborate with team members, and store and share files. We reserve the right to modify, suspend, or discontinue any feature of the Service at any time with reasonable notice.

**3. Account Registration and Security**
You must provide accurate information when creating your account. You are responsible for maintaining the confidentiality of your login credentials and for all activity under your account. Notify us immediately at security@taskflow.com if you suspect unauthorized access.

**4. Acceptable Use**
You agree not to: (a) use the Service for any unlawful purpose; (b) upload or transmit malicious code, spam, or unauthorized advertising; (c) attempt to gain unauthorized access to any part of the Service or other users' accounts; (d) use the Service to store, process, or transmit sensitive personal data (health records, financial account numbers, government IDs) without our prior written consent.

**5. Intellectual Property**
Taskflow Inc. retains all rights, title, and interest in the Service, including all software, designs, and trademarks. You retain ownership of all content you upload to the Service ("User Content"). By uploading User Content, you grant Taskflow Inc. a limited, non-exclusive license to store, display, and process your User Content solely to provide the Service to you.

**6. Subscription and Payment**
*Free Tier:* Available at no charge subject to usage limits described at taskflow.com/pricing. *Pro Tier ($12/month):* Billed monthly in advance. Subscriptions auto-renew unless cancelled at least 24 hours before the renewal date. No refunds for partial months. We reserve the right to change pricing with 30 days' notice; continued use after the effective date constitutes acceptance of new pricing.

**7. Limitation of Liability**
TO THE MAXIMUM EXTENT PERMITTED BY LAW, TASKFLOW INC.'S TOTAL LIABILITY TO YOU FOR ANY CLAIM ARISING FROM THESE TERMS OR YOUR USE OF THE SERVICE SHALL NOT EXCEED THE GREATER OF (A) THE FEES YOU PAID IN THE 12 MONTHS PRECEDING THE CLAIM OR (B) $100. IN NO EVENT SHALL TASKFLOW INC. BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES.

**8. Dispute Resolution**
These Terms are governed by the laws of the State of Delaware. Any dispute shall be resolved by binding arbitration administered by the American Arbitration Association under its Commercial Arbitration Rules, conducted in Delaware. **YOU WAIVE THE RIGHT TO A JURY TRIAL AND TO PARTICIPATE IN CLASS-ACTION PROCEEDINGS.**

---

### Example 2: Privacy Policy for a Mobile App (Consumer, Ad-Supported)
**Input:**
"Draft a Privacy Policy for 'FitTrack,' a free fitness tracking mobile app (iOS and Android). Company: FitTrack LLC, California. We collect: name, email, age, workout data, GPS location (during workouts), and device identifiers. We share data with: Firebase Analytics, Stripe (if premium upgrade), and advertising partners. We do not sell data. Governed by California law. Some users may be 13–17 years old."

**Output (excerpt — key sections):**

---
**FITTRACK PRIVACY POLICY**
*Effective Date: [DATE] | Last Updated: [DATE]*

> ⚠️ **Draft Template** — Review by a licensed attorney is required before publication, particularly given CCPA, COPPA, and GDPR implications.

**Information We Collect**

| Category | Examples | Why We Collect It |
|----------|----------|-------------------|
| Account Data | Name, email address, date of birth | Account creation and age verification |
| Health & Fitness Data | Workout logs, steps, calories, exercise type | Core app functionality |
| Location Data | GPS coordinates during active workouts | Route tracking feature (opt-in) |
| Device Data | Device ID, OS version, IP address | Security, analytics, crash reporting |
| Usage Data | Features used, session duration, in-app clicks | Product improvement |

**How We Use Your Information**
We use your information to: (1) provide, operate, and improve the FitTrack app; (2) personalize your experience and fitness recommendations; (3) display interest-based advertising through our advertising partners; (4) communicate with you about your account and service updates; (5) comply with legal obligations.

**Information Sharing**
We share information with: (a) **Firebase Analytics** (Google) — usage analytics; (b) **Stripe** — payment processing for premium upgrades (we do not store your full payment card number); (c) **Advertising Partners** — device identifiers and interest segments for ad targeting. **We do not sell your personal information** as defined under the California Consumer Privacy Act (CCPA).

**Children's Privacy (COPPA)**
The app is not directed to children under 13. We do not knowingly collect personal information from children under 13. If you believe we have inadvertently collected information from a child under 13, contact us at privacy@fittrack.com and we will delete it promptly. Users between 13 and 17 may use the app only with verifiable parental consent. We obtain parental consent through email confirmation: a parent or guardian must confirm from the account registration email address before the minor's account is activated. Health and fitness data of minors is treated with heightened protection and is not shared with advertising partners.

**Your California Privacy Rights (CCPA)**
California residents have the right to: (1) know what personal information we collect and how it is used; (2) request deletion of your personal information; (3) opt out of the sale of personal information (we do not sell personal data); (4) non-discrimination for exercising these rights. To exercise these rights, email privacy@fittrack.com or visit [fittrack.com/privacy-rights].

**Your Rights (GDPR — EU Users)**
If you are located in the European Economic Area, you have rights to: access, rectification, erasure, restriction of processing, data portability, and objection. Our legal basis for processing is contract performance (account data), legitimate interest (analytics), and consent (location, advertising). To exercise your rights, contact dpo@fittrack.com.

**Contact Us**
FitTrack LLC | 123 Market Street, San Francisco, CA 94105 | privacy@fittrack.com

---

## Best Practices
- Always include an effective date and version number — users and regulators need to know which version applies to them
- Use a clickwrap acceptance mechanism (explicit checkbox + "I agree") rather than browsewrap (passive "by using the site you agree") — clickwrap is far more legally defensible
- Keep the Privacy Policy and ToS as separate documents — bundling them makes each less readable and can cause compliance issues
- For GDPR compliance, document your legal basis for each category of data processing — consent is not always the right basis
- Review and update legal documents whenever you: add a major new feature, change your data sharing practices, change your pricing model, or enter a new jurisdiction
- Store records of when users accepted each version of your Terms — this is critical evidence if a dispute arises

## Common Mistakes
- Using a generic template without customizing for your actual data practices — a Privacy Policy that doesn't match reality creates liability
- Omitting the arbitration clause or making it non-mutual — courts are increasingly scrutinizing unfair arbitration provisions
- Failing to address user-generated content rights — if users can post content, you need a license to display and store it
- Not including a data retention / deletion section — required under GDPR and CCPA and important for user trust
- Setting the liability cap too low (e.g., $5) — courts sometimes void unconscionably low caps, undermining the entire clause
- Publishing a Privacy Policy that mentions GDPR or CCPA compliance without actually implementing the required operational practices

## Tips & Tricks
- Link to your Privacy Policy and ToS in your app store listing, registration page, footer, and any marketing emails — this creates a clear acceptance record
- Use a "summary table" at the top of your Privacy Policy (e.g., "What we collect | Why | How long") to improve readability and demonstrate good faith to regulators
- For cookie consent (GDPR), use a consent management platform (CMP) rather than trying to hand-code the consent flow — the technical requirements are complex
- Version your legal documents with semantic versioning (1.0.0, 1.1.0) and maintain an archive — you may need to prove what a user agreed to at a specific point in time
- Add a "plain-language summary" section at the top of your ToS — it doesn't replace the legal text but significantly improves user trust and reduces disputes

## Related Skills
- [contract-reviewer](../contract-reviewer/SKILL.md)
- [legal-summarizer](../legal-summarizer/SKILL.md)
