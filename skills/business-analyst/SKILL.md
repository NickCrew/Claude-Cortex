---
name: business-analyst
description: "Use this skill when gathering and documenting business requirements, mapping processes, performing gap analysis, writing business requirements documents (BRDs), or modeling stakeholder impact. Trigger phrases: 'write a business requirements document', 'map this process', 'gather requirements for', 'gap analysis for', 'AS-IS TO-BE process'. Not for writing user stories (use product-manager skill), conducting user research (use ux-researcher), or financial modeling."
version: 1.0.0
author: community
tags: [business, analysis, requirements, process]
license: MIT
---

# Business Analyst

## Overview
This skill covers the structured practice of business analysis—translating business problems into clear requirements, mapping current and future-state processes, identifying gaps, managing stakeholder alignment, and producing the documentation (BRDs, use cases, process maps) that enables successful project delivery. It bridges the gap between business needs and technical or operational solutions.

## When to Use
- You need to document what a system or process must do (requirements gathering)
- You're mapping a current business process to find inefficiencies
- You need to perform a gap analysis between current and desired state
- You're building a Business Requirements Document (BRD)
- You need to identify and manage project stakeholders
- Writing use cases or functional specifications

## When NOT to Use
- Writing user stories and sprint backlog items (use product-manager skill)
- Conducting qualitative UX research (use ux-researcher skill)
- Technical architecture or system design
- Financial modeling or ROI calculations (use a finance skill)
- Project scheduling and resource planning (use a PM tool)

## Quick Reference
| Task | Technique | Output |
|------|-----------|--------|
| Elicit requirements | Interviews, workshops, observation | Requirements list |
| Document requirements | BRD template | Business Requirements Document |
| Map current state | Swimlane diagram, flowchart | AS-IS process map |
| Design future state | TO-BE process map | Process redesign |
| Find gaps | Gap analysis matrix | Gap analysis report |
| Manage stakeholders | RACI / Power-Interest grid | Stakeholder register |
| Document user interactions | Use case format | Use Case document |
| Prioritize requirements | MoSCoW method | Prioritized requirements |
| Validate requirements | Walkthrough, prototype review | Sign-off document |

## Instructions

### Step 1: Stakeholder Identification and Management

**Stakeholder register:**
| Stakeholder | Role | Interest Level | Influence Level | Stance | Engagement Strategy |
|-------------|------|---------------|-----------------|--------|---------------------|
| VP Operations | Executive sponsor | High | High | Champion | Weekly status briefing |
| IT Director | Technical owner | High | High | Neutral | Bi-weekly architecture review |
| Customer Service Mgr | Process owner | High | Medium | Skeptic | Involve in requirements workshop |
| End users | Operators | Medium | Low | Unaware | Survey + demo sessions |

**Power-Interest grid:**
- High Power + High Interest → **Manage closely** (key decision makers)
- High Power + Low Interest → **Keep satisfied** (executive sponsors)
- Low Power + High Interest → **Keep informed** (operational users)
- Low Power + Low Interest → **Monitor** (peripheral stakeholders)

**RACI matrix for project roles:**
| Activity | Business Sponsor | BA | IT Lead | Process Owner |
|----------|-----------------|-----|---------|---------------|
| Define requirements | A | R | C | C |
| Approve BRD | A | R | I | I |
| Design solution | I | C | R | C |
| Test & validate | I | C | R | A |
| Sign off to launch | A | C | C | R |
(R=Responsible, A=Accountable, C=Consulted, I=Informed)

### Step 2: Requirements Gathering Techniques

**Technique 1 — Structured Interviews:**
Run 45–60 minute sessions with key stakeholders. Use open-ended questions:
- "Walk me through how you currently handle X from start to finish."
- "What are the biggest pain points with the current process?"
- "What would have to be true for this to be considered a success?"
- "If you could change one thing, what would it be?"
- "What constraints do we need to work within (regulatory, technical, budget)?"

**Technique 2 — Requirements Workshop (JAD session):**
- Invite 6–10 stakeholders representing all affected groups
- 2–4 hour structured session with a facilitator
- Use whiteboards or collaborative tools (Miro, Mural)
- Activities: process walkthroughs, affinity mapping, scenario walkthroughs

**Technique 3 — Observation (Process Shadowing):**
- Spend 1–2 hours observing end users performing the actual process
- Note what they do, workarounds they use, and pain points
- Often reveals requirements that no one thinks to mention in interviews

**Technique 4 — Document Analysis:**
- Review existing SOPs, training materials, system documentation
- Analyze reports, dashboards, and data that support the current process
- Review help desk tickets for common user problems

### Step 3: Business Requirements Document (BRD) Template

---
**Document Title:** [Project Name] Business Requirements Document
**Version:** 1.0 | **Date:** [Date] | **Status:** Draft / In Review / Approved
**Author:** [BA Name] | **Sponsor:** [Name]

---

**1. Executive Summary**
One paragraph: business problem, proposed solution, expected business value, and scope.

**2. Business Objectives**
| Objective | Success Metric | Target | Timeline |
|-----------|---------------|--------|----------|
| Reduce order processing time | Avg processing time | From 4 hours to 30 min | By Q3 |
| Eliminate manual data entry errors | Error rate | From 3.2% to <0.5% | By Q3 |

**3. Project Scope**
**In Scope:**
- [List what the project will address]

**Out of Scope:**
- [List what is explicitly excluded to prevent scope creep]

**4. Current State (AS-IS) Overview**
Brief description of how the process/system works today.
- Current pain points (supported by data where possible)
- Volume and frequency: "200 orders processed daily by 5 team members"

**5. Future State (TO-BE) Overview**
Description of the desired end state and how it differs from today.

**6. Business Requirements**
| ID | Requirement | Priority | Source | Notes |
|----|-------------|----------|--------|-------|
| BR-001 | System must validate order completeness before submission | Must Have | Operations Mgr | Reduce downstream errors |
| BR-002 | Automated email notification to customer upon order status change | Should Have | Customer Service | Reduce inbound call volume |
| BR-003 | Ability to generate weekly summary reports without IT involvement | Should Have | VP Operations | Currently takes 4 hours/week |

**7. Assumptions and Dependencies**
- Assumption: ERP system will provide API access for integration
- Dependency: IT infrastructure upgrade must complete before this project starts

**8. Constraints**
- Budget: $150,000 total project cost
- Timeline: Must launch before Q4 peak season
- Regulatory: Must comply with SOC 2 Type II requirements

**9. Risks**
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Data migration errors | High | High | Parallel run period of 4 weeks |
| User adoption resistance | Medium | Medium | Change management program |

**10. Approval**
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Sponsor | | | |
| IT Director | | | |

---

### Step 4: Process Mapping (AS-IS and TO-BE)

**AS-IS Process Map** — document the current state exactly as it is:
- Use swimlane diagrams (one lane per role/system)
- Map every step, decision point, and handoff
- Note pain points with 🔴 and workarounds with ⚠️
- Capture time and volume data at key steps

**Swimlane notation (text format):**
```
Customer → [Submit order form] → [Order lands in shared inbox] 
                                          ↓
Sales Rep → [Manually copy to ERP] → [Check inventory] 
                                          ↓ (if in stock)
Warehouse → [Pick and pack] → [Update ERP] → [Email customer]
                                          ↓ (if out of stock)
Sales Rep → [Call customer] → [Offer alternative] → [Cancel or modify]

Pain points: ⚠️ Manual ERP entry takes 15 min/order; 🔴 3.2% error rate on data entry
```

**TO-BE Process Map** — design the improved future state:
- Eliminate the waste/pain points identified in AS-IS
- Show automation, integration, and self-service where appropriate
- Include new systems or tools introduced

```
Customer → [Submit order on web portal] → [System auto-validates] 
                                                    ↓ (auto-routed)
ERP System → [Inventory check (real-time)] → [Confirmation email auto-sent]
                                                    ↓ (if in stock)
Warehouse → [Pick slip auto-generated] → [Scan to update status] → [Auto-notification]
                                                    ↓ (if out of stock)
ERP System → [Auto-email with alternatives] → [Customer self-serves]
```

### Step 5: Gap Analysis
A gap analysis identifies the distance between current state and desired state.

**Gap analysis matrix:**
| Capability Area | Current State | Desired State | Gap | Priority | Action Required |
|-----------------|---------------|---------------|-----|----------|-----------------|
| Order validation | Manual check by rep | System validates automatically | Process + system gap | High | Build validation rules in ERP |
| Customer notification | Manual email by rep | Automated trigger | Automation gap | High | Configure email workflow |
| Reporting | Manual Excel export | Self-serve dashboard | Capability gap | Medium | Implement BI tool integration |
| Inventory visibility | Updated day-end batch | Real-time | Data gap | High | API integration with warehouse system |

### Step 6: Writing Use Cases
A use case describes how a user achieves a goal through a system.

**Use Case Template:**
```
Use Case ID: UC-001
Use Case Name: Submit a New Customer Order
Actor: Sales Representative
Preconditions: Rep is logged into the system; Customer account exists
Trigger: Rep receives a customer purchase request

Main Success Scenario:
1. Rep selects "New Order" from the dashboard
2. System displays order form pre-populated with customer details
3. Rep enters product, quantity, and delivery date
4. System validates inventory availability in real time
5. Rep confirms and submits the order
6. System generates order confirmation number and emails customer
7. Use case ends

Alternative Flows:
4a. Product is out of stock:
   4a.1. System displays "Out of Stock" with expected restock date
   4a.2. Rep offers alternative or backorder option
   4a.3. If customer accepts backorder → continue step 5 with backorder flag

Exception Flows:
3a. Required fields missing:
   3a.1. System highlights missing fields with error message
   3a.2. Rep corrects and resubmits

Postconditions: Order is recorded in ERP; confirmation email sent to customer
```

## Examples

### Example 1: Write a Business Requirements Document for Order Processing Automation

**Input:** "Our order processing team manually enters 200 orders per day into our ERP. It takes 15 minutes per order, has a 3.2% error rate, and team members work overtime every peak season. We want to automate this."

**BRD Executive Summary:**
> The Order Processing Automation project will eliminate manual order entry by integrating the customer-facing web portal directly with the ERP system. Currently, 200 daily orders require 15 minutes of manual data entry each, resulting in $180,000/year in processing labor cost and a 3.2% error rate that causes customer complaints and re-work. The automated system will reduce processing time to under 2 minutes per order, target a <0.5% error rate, and free 3 FTEs for higher-value work. Project scope includes web portal API integration, ERP workflow configuration, and automated customer notification. Out of scope: mobile app, EDI for supplier orders.

**Key Business Requirements:**
- BR-001: System shall automatically import all orders submitted via web portal into ERP within 60 seconds — Must Have
- BR-002: System shall validate required fields and inventory availability before order confirmation — Must Have
- BR-003: Customer shall receive automated order confirmation email with order number within 2 minutes — Must Have
- BR-004: System shall flag and route orders with validation errors to a supervisor queue — Must Have
- BR-005: Reports shall be auto-generated every Monday 8am without IT involvement — Should Have

---

### Example 2: Map a Customer Onboarding Process

**Input:** "New customers take 3 weeks to become active. We want to understand why and fix it."

**AS-IS discovery (from interviews + observation):**
- Step 1: Customer signs contract (Day 0) → sent to sales rep via email
- Step 2: Sales rep manually emails implementation team (Day 1–2) — ⚠️ delay: emails buried
- Step 3: Implementation team schedules kickoff (Day 3–7) — 🔴 bottleneck: team at capacity
- Step 4: Kickoff call → IT team creates account (Day 8) — ⚠️ manual account creation = 24–48 hrs
- Step 5: Customer given credentials; begins setup (Day 10–14) — no guidance = high dropout
- Step 6: Training session scheduled (Day 15–21) — 🔴 bottleneck: only 2 trainers available

**Gap identified:** 7 days of delay from manual handoffs and queue waits; no self-service during setup.

**TO-BE redesign:**
- Contract signed → auto-triggers CRM workflow → implementation team auto-notified + calendar invite auto-sent (eliminates 1–2 day delay)
- Account provisioned automatically via API (eliminates 24–48 hr delay)
- Self-guided setup wizard with in-app tooltips (customer can start before training)
- On-demand training video library (reduces dependency on 2 live trainers)
- Target: 3 weeks → 5 business days

**Gap analysis output:**
| Gap | Priority | Solution |
|-----|----------|---------|
| Manual sales → implementation handoff | High | CRM workflow automation |
| Manual account creation | High | API provisioning |
| No self-service setup | Medium | In-app onboarding wizard |
| Training capacity constraint | Medium | Video library + recorded sessions |

## Best Practices
- Document the AS-IS process before designing the TO-BE — you cannot improve what you don't understand
- Get sign-off on requirements before solution design begins — changing requirements mid-build is 10× more expensive
- Write requirements as behaviors ("System shall…") not as solutions ("System will have a button that…")
- Trace requirements back to business objectives — if a requirement doesn't support an objective, question it
- Use "shall" for mandatory requirements and "should" for desirable ones
- Walk through requirements with end users, not just management — managers often don't know the actual workflow

## Common Mistakes
- Jumping to solution design before understanding the problem
- Writing vague requirements: "The system should be user-friendly" (untestable)
- Ignoring non-functional requirements (performance, security, availability)
- Getting scope creep from "nice to have" requests presented as requirements
- Skipping stakeholder identification and then facing surprises at sign-off
- Treating the BRD as a one-time artifact — requirements change; version and update it

## Tips & Tricks
- Use "what, not how" as your mantra: requirements describe what the system must do, not how to build it
- The best requirement elicitation question: "And then what happens?" — keeps uncovering steps
- Silent workflow walk-through: ask stakeholders to do their job while you observe without interrupting, then ask questions at the end
- A one-page process map on a whiteboard is worth 10 pages of text description
- Prototype or mockup + structured walkthrough surfaces more requirements than any document review

## Related Skills
- [product-manager](../../business/product-manager/SKILL.md)
- [ux-researcher](../../business/ux-researcher/SKILL.md)
- [okr-planner](../../business/okr-planner/SKILL.md)
- [meeting-facilitator](../../business/meeting-facilitator/SKILL.md)
