# Mockup Test: 2 4 Automate Evaluation of FAQ Bot Performance

Choose the single best answer for each question.

## Question 1

What is the main purpose of automatically evaluating an FAQ bot?

A. Measure answer quality consistently across a set of representative questions.

B. Replace the knowledge base with a benchmark.

C. Guarantee that every user answer is correct.

D. Avoid collecting any test cases.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Automated evaluation supports repeatable quality measurement; it cannot guarantee perfection.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “1. Evaluating RAG application performance” — the lesson’s evaluation workflow.
</details>

## Question 2

Why create an evaluation dataset that reflects the intended application?

A. It tests the system on the kinds of questions and expected behavior it will face in use.

B. It ensures the model memorizes the test answers.

C. It avoids specifying any quality criteria.

D. It makes retrieval unnecessary.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson emphasizes representative questions and reference answers so measured quality matches the use case.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “4.1 Building a High-Quality Evaluation Dataset”.
</details>

## Question 3

What does a reference answer provide to an evaluator?

A. A target answer against which the generated response can be judged.

B. A list of API credentials.

C. A replacement system prompt.

D. A vector index checksum.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Reference answers establish the expected content for comparing model responses.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “1.3 Implementing an Automated Evaluation Mechanism” — answer quality validation.
</details>

## Question 4

A response contains correct facts but is difficult to read. Which evaluation approach can capture this distinction?

A. Score against multiple explicit criteria, such as correctness and clarity.

B. Use only response length.

C. Check only whether the API call succeeded.

D. Count the number of retrieved chunks.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Evaluation criteria should reflect different dimensions of answer quality rather than a single proxy.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2.1 Evaluating the response quality of RAG applications” — answer correctness metrics.
</details>

## Question 5

Why is exact string matching often insufficient for evaluating generated answers?

A. Semantically equivalent answers may use different wording.

B. It cannot compare numbers.

C. It requires a GPU.

D. It evaluates retrieval instead of generation.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Generated language can vary while preserving meaning, so lexical identity alone is a weak quality test.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2.1.2 Understanding How Answer Correctness Is Calculated” — semantic similarity and factual accuracy.
</details>

## Question 6

What is a practical role for an LLM-as-judge in an automated evaluation pipeline?

A. Apply a defined rubric to assess generated answers at scale.

B. Create the source documents at runtime.

C. Authenticate the deployed model.

D. Increase retrieval recall automatically.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson introduces an evaluator model to apply criteria consistently to generated responses.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “1.3.1 Validating answer quality using LLMs”.
</details>

## Question 7

How can judge output be made easier for downstream analysis?

A. Request a structured result with named scores or fields.

B. Ask for an unbounded essay only.

C. Remove the scoring rubric.

D. Return just the source passage.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Structured output lets the evaluation pipeline parse and aggregate results.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “1.3.1 Validating answer quality using LLMs” — automated evaluation implementation.
</details>

## Question 8

Why should evaluation combine automated metrics with human review?

A. Automated scores can miss nuance, so human inspection helps validate the results.

B. Human review makes the dataset unnecessary.

C. Metrics cannot be repeated.

D. An LLM judge always has access to ground truth.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Automated evaluation is useful but should be checked for judgment quality and edge cases.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “4.2 Evaluation-First Optimization Strategy” — use evaluation to guide iteration.
</details>

## Question 9

A new prompt version improves scores on the examples used to tune it but performs worse on held-out cases. What is the concern?

A. Overfitting to the development examples.

B. An improvement in generalization.

C. A vector storage failure.

D. A decrease in API latency.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

A gap between development and held-out results signals that optimization may not generalize.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “4.1 Building a High-Quality Evaluation Dataset” — representative evaluation data.
</details>

## Question 10

What should a team do after discovering poor scores on a category of FAQ questions?

A. Inspect failures, identify whether retrieval or generation caused them, and improve the relevant part.

B. Increase all scores manually.

C. Discard the evaluation cases.

D. Change the reference answers to match outputs.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Evaluation is useful when it guides diagnosis and targeted iteration rather than score manipulation.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “3. How to optimize based on ragas metrics”.
</details>
