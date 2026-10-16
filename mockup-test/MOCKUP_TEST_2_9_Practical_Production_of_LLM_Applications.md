# Mockup Test: 2 9 Practical Production of LLM Applications

Choose the single best answer for each question.

## Question 1

What is the first step in the lesson’s production planning approach?

A. Understand the business context and define requirements.

B. Select a GPU before identifying the task.

C. Choose a benchmark unrelated to the application.

D. Start by maximizing output tokens.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Production planning begins with business context, followed by functional and non-functional requirements.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “1. Business requirements analysis”.
</details>

## Question 2

Which statement distinguishes functional from non-functional requirements?

A. Functional requirements define what the model does; non-functional requirements describe how well it performs.

B. Functional requirements describe latency only.

C. Non-functional requirements define the model’s task.

D. They are interchangeable terms.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson explicitly contrasts task capabilities with quality and operational characteristics.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “1.1 Functional requirements” and “1.2 Non-functional requirements”.
</details>

## Question 3

A product must classify images. What model-selection guidance does the lesson give?

A. Use a dedicated vision model for vision tasks.

B. Use any text-only general LLM by default.

C. Chain unrelated models for every image.

D. Fine-tune a speech model.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson says vision tasks typically need dedicated vision models rather than general LLMs.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “1.1 Functional requirements of the model” — Vision tasks.
</details>

## Question 4

A team wants faster inference for a simple use case. Which option is consistent with the lesson?

A. Choose a smaller model or use compression methods such as quantization.

B. Increase the model size.

C. Add more irrelevant context.

D. Always run on CPUs instead of GPUs.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Smaller models and compression can reduce inference requirements.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “2.1.1 Faster Request Processing”.
</details>

## Question 5

Which description of context caching is correct?

A. Reuse computation for common input prefixes across requests.

B. Cache final outputs regardless of the question.

C. Store only model weights in a vector database.

D. Replace the need for conversation context.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Context Cache reduces redundant computation when requests share prefix content.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “2.1.2 Reducing Request Volume and Computation”.
</details>

## Question 6

Why is prompt guidance often preferable to a strict `max_tokens` cap for concise but complete messages?

A. The model can adapt its response while preserving meaning; a hard cap may cut it off mid-sentence.

B. Prompt guidance always costs zero tokens.

C. `max_tokens` increases answer accuracy.

D. A hard cap guarantees a complete sentence.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson presents prompt constraints as the first choice for semantic completeness and max_tokens as a safety limit.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “2.1.3 Reducing Token Input and Output”.
</details>

## Question 7

Why are GPUs well suited to LLM inference?

A. Their many cores handle large parallel matrix operations efficiently.

B. They are optimized mainly for complex sequential branching.

C. They eliminate memory requirements.

D. They are always cheaper than CPUs.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

LLM inference involves large matrix operations, which align with GPU parallelism.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “2.1.4 Parallel Processing”.
</details>

## Question 8

A task is simple and rules-based. Should an application automatically use an LLM?

A. No; the lesson recommends considering simpler classical methods when they are faster and less complex.

B. Yes; every task benefits from generation.

C. Only if the model has a larger context window.

D. Only after converting rules into images.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson warns against defaulting to LLMs when simpler methods fit better.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “2.1.5 Don’t Default to LLMs”.
</details>

## Question 9

The backend takes several seconds to respond. Which design can reduce perceived waiting time?

A. Stream partial output and show task progress.

B. Hide all status until completion.

C. Increase the output length.

D. Remove error messages.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Streaming and visible progress improve perceived responsiveness even when backend time remains.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “2.2 User-Perceived optimization” — Streaming output and Display task progress.
</details>

## Question 10

Traffic varies widely across the day. What stability measure does the lesson recommend?

A. Automated scaling based on traffic, with monitoring and alerts.

B. Provision for peak traffic permanently without monitoring.

C. Disable all error reporting.

D. Use a fixed number of instances regardless of demand.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Autoscaling helps meet demand without overprovisioning, while monitoring detects anomalies.

**Source:** `2_9_Practical_Production_of_LLM_Applications.ipynb` — “4. Stability enhancement”.
</details>
