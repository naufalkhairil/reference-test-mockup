# Professional Exam: 4.4 Building an Unbreakable AI Application: Security and Compliance

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

Your AI application recently came under a flood of requests, exhausting its GPU resources and causing frequent service interruptions. What category of attack is this? Which layer of defense should you prioritize strengthening?

A. A prompt-injection attack — you should strengthen the AI model-security layer.

B. A data-poisoning attack — you should strengthen the AI infrastructure-security layer.

C. A DDoS attack — you should strengthen the AI application-security layer.

D. A model-extraction attack — you should strengthen the AI model-security layer.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — A DDoS attack — you should strengthen the AI application-security layer.**

- It's a DDoS attack, and you should strengthen the AI application-security layer. Using high-compute-cost requests to exhaust GPU resources is an application-layer DDoS attack targeting the AI service. Defend at the application layer — for example, using DDoS Protection (Advanced) and a WAF for traffic scrubbing and access control.

**Source:** `4_4_LLM_Security_Compliance_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 2

The AI assistant you built has a feature that lets it "read a document the user uploaded and answer questions about it." During testing, the security team discovers that after uploading a carefully crafted PDF, the AI assistant ignores the user's actual question and instead executes a hidden instruction embedded inside the PDF. Which of the following defenses would most directly mitigate this threat?

A. Deploy a keyword blocklist filter on the user-input side, blocking requests containing phrases like "ignore the instructions"

B. Mark external document content as "data context" rather than "instructions," forbidding the model from promoting it to an executable instruction

C. Limit how many uploads a user can make per minute, using rate control to prevent an attacker from making bulk attempts to bypass the defense

D. Replace the current model with one that has more parameters, relying on stronger comprehension to automatically identify malicious content

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Mark external document content as "data context" rather than "instructions," forbidding the model from promoting it to an executable instruction**

This is a classic indirect prompt-injection attack — the attack instruction isn't in the user's input, but hidden inside an external document the Agent reads. A keyword blocklist can't stop this, because a malicious instruction can be phrased in an endless number of ways, and the attack surface is the document, not the user's input. Rate limiting defends against DDoS, not injection. A larger model doesn't automatically gain the ability to distinguish instructions from data. The right core defense is to architecturally separate "user instructions" from "external data content," ensuring external content can never be promoted into an executable instruction.

**Source:** `4_4_LLM_Security_Compliance_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 3

When building a complete AI-application security system, which combinations of the following products or technologies make sense? (Select all that apply)

A. Using AI Guardrails alone is enough — it can solve every problem.

B. Using RAM for permission control is part of AI infrastructure security.

C. Using a WAF (Web Application Firewall) alone can effectively defend against prompt-injection attacks targeting a large model.

D. Combining AI Guardrails and DDoS Protection (Advanced), to handle model-level attacks and application-level attacks respectively.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Using RAM for permission control is part of AI infrastructure security.**

- A is incorrect — a single tool can't handle every threat.
- C is incorrect — a traditional WAF mainly defends against web attacks like SQL injection and XSS, and has limited ability to defend against prompt-injection attacks that require understanding semantics; you need a tool like AI Guardrails, purpose-built for the semantics and logic of models, to provide deep protection.
- B, D, and E each correctly reflect a sound protection approach at the infrastructure, application, and data layers, respectively.

**Source:** `4_4_LLM_Security_Compliance_EN.ipynb` — embedded lesson quiz and its explanation.

</details>
