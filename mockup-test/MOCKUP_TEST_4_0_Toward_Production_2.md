# Professional Exam: Toward Production — Preparing an AI System for Company-Wide Launch

**Source:** `4_0_Toward_Production.ipynb` (Alibaba Cloud ACP LLM course, Stage 4 section introduction)

Choose the single best answer for each question.

> **Source-coverage note:** The reference for this exam is a short section introduction (roughly one page). It frames the move from a stable development-environment system to company-wide production use, names three challenge areas (cost, deployment, security & compliance), and provides the Stage 4 lesson roadmap table. The source cannot support 10 rigorous, non-repetitive items; the 5 questions below are the strongest supportable set, without padding or speculation. They assess the stage's framing and roadmap rather than detailed technical procedures, which are covered in lessons 4.1–4.4.

## Question 1

Leadership has decided to launch your team's AI system — which runs stably in the development environment — for daily use by the whole company. According to the section introduction, which three challenge areas ("mountains") lie between "it works on your computer" and "the whole company uses it every day"?

A. Data annotation, model pre-training, and benchmarking

B. Cost, deployment, and security & compliance

C. Hiring, marketing, and legal review

D. Prompt engineering, retrieval tuning, and agent orchestration

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Cost, deployment, and security & compliance**

The introduction presents exactly three bolded challenges that must be overcome before production: **Cost** (every LLM API call costs money; a company-wide user base raises the monthly token bill), **Deployment** (the system runs only on a laptop; IT asks about servers, high availability, and monitoring), and **Security & compliance** (input leakage, inappropriate output, industry compliance requirements). Option D lists techniques from earlier stages (RAG, agents, prompts) that, per the source, have already been polished in the development environment; options A and C are not mentioned in the source at all.

**Source:** `4_0_Toward_Production.ipynb` — "# 4.0 Toward Production" introduction (the paragraphs beginning "**Cost**:", "**Deployment**:", and "**Security & compliance**:"). The three named challenges map directly to the correct option.
</details>

## Question 2

The introduction's cost challenge raises the question of the monthly token bill when many employees use the system simultaneously. Which technical approach does the source explicitly float as a possible way to cut cost and boost speed at the same time?

A. Negotiating an enterprise volume discount with the API provider

B. Caching all bot responses in a shared database

C. Fine-tuning a smaller model

D. Limiting the number of employees who can access the system concurrently

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Fine-tuning a smaller model**

The Cost paragraph asks: "Could you cut cost and boost speed by fine-tuning a smaller model?" — the only mitigation the source names for the cost challenge, foreshadowing lesson 4.1 (distillation). Options A, B, and D are generic cost-control measures that might be plausible in general practice but appear nowhere in this source; the exam assesses what the reference actually proposes.

**Source:** `4_0_Toward_Production.ipynb` — "# 4.0 Toward Production," Cost paragraph ("Every LLM API call costs money… Could you cut cost and boost speed by fine-tuning a smaller model?").
</details>

## Question 3

When the IT department weighs in on the deployment challenge, which set of questions does the source attribute to them?

A. How to reduce the monthly token bill, how to budget for GPU purchases, and how to charge departments for usage

B. How to fine-tune a smaller model, how to evaluate its accuracy, and how to filter its training data

C. How to size the database, how to plan network bandwidth, and how to schedule maintenance windows

D. How to deploy the system to a server, how to ensure high availability, and how to monitor its status

<details>
<summary>Show answer and rationale</summary>

**Answer: D — How to deploy the system to a server, how to ensure high availability, and how to monitor its status**

The Deployment paragraph states that the system only runs on a laptop and that the IT department asks exactly these three questions: server deployment, high availability, and status monitoring. Option A restates cost-challenge concerns, B restates the model-training direction from the cost challenge (lesson 4.1 territory), and C lists plausible infrastructure planning topics that the source does not attribute to the IT department.

**Source:** `4_0_Toward_Production.ipynb` — "# 4.0 Toward Production," Deployment paragraph ("The IT department asks you — how do you deploy it to a server? How do you ensure high availability? How do you monitor its status?").
</details>

## Question 4

The security team raises concerns about the company-wide launch. Which set of concerns matches the source?

A. Could user input leak sensitive information, could the model output inappropriate content, and does the system meet industry compliance requirements

B. Could the server crash under load, could the network disconnect, and could backups fail

C. Could the API provider rate-limit the service, could the GPU run out of memory, and could latency spike

D. Could the vendor raise prices, could the model be deprecated, and could key staff leave

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Could user input leak sensitive information, could the model output inappropriate content, and does the system meet industry compliance requirements**

The Security & compliance paragraph lists precisely these three questions from the security team: sensitive-information leakage via user input, inappropriate model output, and industry compliance requirements. The most tempting alternative, B, describes availability and infrastructure failure modes — those belong to the deployment challenge's territory (high availability), not the security team's stated concerns. C mixes performance/capacity issues and D lists vendor/business risks; none appear in the source.

**Source:** `4_0_Toward_Production.ipynb` — "# 4.0 Toward Production," Security & compliance paragraph ("could user input leak sensitive information? Could the model output inappropriate content? Does the system meet industry compliance requirements?").
</details>

## Question 5

Using the "Lessons in this stage" roadmap table, a team member is assigned to study model deployment and inference services before the launch review. Which lesson covers that topic?

A. Lesson 4.3 — Production Practices for LLM Applications

B. Lesson 4.4 — Security & Compliance for LLM Applications

C. Lesson 4.2 — Deploying Models

D. Lesson 4.1 — Using Distillation to Give a Small Model Professional Capabilities

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Lesson 4.2 — Deploying Models**

The roadmap table pairs lesson 4.2 "Deploying Models" with the note "Model deployment & inference services." The other lessons cover different topics per the same table: 4.1 is "Model distillation in practice" (option D), 4.3 is "Production-environment best practices" (option A), and 4.4 is "Security protection & compliance requirements" (option B).

**Source:** `4_0_Toward_Production.ipynb` — "Lessons in this stage" table (rows for lessons 4.1–4.4 with their Titles and Notes columns).
</details>
