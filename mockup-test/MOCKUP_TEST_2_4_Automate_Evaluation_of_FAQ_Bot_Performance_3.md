# Professional Exam: Automated Evaluation of RAG Applications

Choose the single best answer for each question.

## Question 1

A chatbot answers that Michael Johnson works in IT Infrastructure. The retrieved passages clearly identify Michael Johnson with Course Development, while a separate passage names Michael Chen as an IT Infrastructure leader. Which failure should the team investigate first?

A. Retrieval recall, because the passages do not contain any department information.

B. Ground-truth authoring, because there is no known correct answer for the test case.

C. Generation grounding, because the answer combined details that the retrieved evidence does not support for Michael Johnson.

D. Context precision, because every retrieved passage must be relevant before an answer can be generated.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Generation grounding, because the answer combined details that the retrieved evidence does not support for Michael Johnson.**

The retrieved context contains the correct department, so the evidence was available. The generated answer instead combines details from different people. The first investigation should therefore focus on why generation failed to remain grounded in the available passages. This does not prove that retrieval will always be reliable; it identifies the failure in this case.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “1.1 Issues with the Q&A Bot” and “1.2. Inspecting Retrieval Results for Diagnosis.” The example presents the unsupported IT Infrastructure answer and then identifies Course Development evidence in the retrieved context.
</details>

## Question 2

A prototype evaluator receives only a question and an answer. It marks a confident but incorrect department claim as valid because the answer appears responsive. What is the most direct improvement to the evaluation design?

A. Add a verified ground truth or reference context and evaluate whether the answer is supported by it.

B. Ask the same evaluator to judge the answer repeatedly and use the majority result.

C. Replace binary labels with a wider rating scale while retaining the same inputs.

D. Increase the answer model’s temperature so it produces a less confident response.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Add a verified ground truth or reference context and evaluate whether the answer is supported by it.**

The prototype `test_answer` asks whether an answer effectively responds to the question, which can miss a plausible hallucination. Adding evidence makes factual support assessable. Repeating an evidence-free evaluation or expanding its rating scale does not address the missing basis for judging correctness.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “1.3.1 Validating answer quality using LLMs,” “1.3.2 Validating context relevance,” and “1.3.3 Summary of evaluation logic.” The notebook identifies false positives in the simple answer check and introduces reference-context validation.
</details>

## Question 3

An answer accurately states a fact found in the retrieved passages, but it does not answer the user’s question. Which metric pattern best captures these two properties?

A. Low faithfulness and high answer relevance.

B. High context recall and low context precision.

C. High faithfulness and low answer relevance.

D. Low answer correctness and high context recall, necessarily.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — High faithfulness and low answer relevance.**

Faithfulness measures whether the answer is factually consistent with the retrieved reference material. Answer relevance measures whether it is relevant to the user’s question. In this scenario, the answer is grounded but fails to address the query. The retrieval metrics do not describe that distinction between the answer and its supporting passages.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2. Using Ragas to evaluate application performance.” The metric overview defines Faithfulness against retrieved materials and Answer Relevance against the user’s question.
</details>

## Question 4

A team is evaluating three generated responses to one question against an answer verified by domain experts. Which fields should its dataset include for the Answer Correctness comparison shown in the notebook?

A. Question, retrieved contexts, and model name.

B. Question, generated answer, and known ground truth.

C. Generated answer, model name, and a ground truth inferred from the highest-scoring output.

D. Retrieved contexts, ground truth, and a relevance label, but no generated answer.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Question, generated answer, and known ground truth.**

Answer Correctness compares the model’s generated response with a correct answer that is already known. The example dataset contains the question, each generated answer, and the ground truth. Contexts are used for retrieval-focused measures such as Context Recall and Context Precision; they do not replace these fields for the comparison described here.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2.1.1 Quick start,” including the sample dataset. The prose describes the known ground truth, and the example data includes `question`, `answer`, and `ground_truth`.
</details>

## Question 5

For one answer, assertion comparison yields TP = 2, FP = 1, and FN = 1. Its semantic similarity score is 0.80. Using the notebook’s formula and weighting, what Answer Correctness score results?

A. 0.60

B. 0.67

C. 0.70

D. 0.80

<details>
<summary>Show answer and rationale</summary>

**Answer: C — 0.70.**

Factual accuracy is `TP / (TP + 0.5 × (FP + FN))`, so it is `2 / (2 + 0.5 × (1 + 1)) = 2/3`. Answer Correctness is `0.25 × semantic similarity + 0.75 × factual accuracy`, giving `0.25 × 0.80 + 0.75 × 2/3 = 0.70`. Factual accuracy carries three times the weight of semantic similarity in this formula.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2.1.2 Understanding How Answer Correctness Is Calculated,” including the TP/FP/FN formula and “Final Score Calculation.”
</details>

## Question 6

Evaluation shows that retrieval usually includes the evidence needed to answer, but irrelevant passages often appear before relevant ones. Which metric and intervention best target this observed weakness?

A. Context Recall; add more answer statements to the reference dataset.

B. Answer Relevance; replace the retriever with a more concise generation model.

C. Faithfulness; increase the number of passages returned for each query.

D. Context Precision; rerank results so relevant passages appear earlier and reduce retrieval noise.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Context Precision; rerank results so relevant passages appear earlier and reduce retrieval noise.**

The necessary evidence is being retrieved, but its placement and the presence of irrelevant material are the problems. Context Precision focuses on whether relevant passages rank highly and on the signal-to-noise ratio. The chapter identifies reranking as a way to move related segments earlier. Context Recall instead focuses on relevant information that was missed.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2.2.1 Quick start,” “2.2.2 Understanding the calculation process of context recall and context precision,” and “3.3 Context Precision.”
</details>

## Question 7

The knowledge base contains the needed policy information, but employees often submit vague queries such as “Leave Request,” which retrieve poor results. Which change most directly addresses this cause?

A. Add duplicate copies of the existing policy documents to the knowledge base.

B. Fine-tune the answer model using responses to the existing policy questions.

C. Rewrite vague user queries into clearer questions using a prompt informed by common employee questions.

D. Lower the minimum Answer Correctness score accepted by the evaluation pipeline.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Rewrite vague user queries into clearer questions using a prompt informed by common employee questions.**

The source material is already present, so this is not primarily a knowledge-base gap. The problem is that vague query wording fails to retrieve useful segments. The chapter recommends query rewriting for ambiguous queries. Fine-tuning the answer model would not directly address this retrieval input problem.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “3.2 Context recall,” the “query rewriting” recommendation for vague or ambiguous queries.
</details>

## Question 8

After an optimization, Context Recall and Context Precision are high, but Answer Correctness is low. What is the most appropriate next diagnostic direction?

A. Treat generation as the likely issue and review prompts, generation parameters, or the model.

B. Assume the knowledge base lacks the required information and add more documents immediately.

C. Conclude that the business objective has been achieved because retrieval scores are high.

D. Discard the evaluation set because retrieval and answer metrics should always move together.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Treat generation as the likely issue and review prompts, generation parameters, or the model.**

The chapter interprets high retrieval metrics paired with low Answer Correctness as evidence that retrieval performs well on the evaluated cases while generation needs attention. Suggested responses include prompt optimization, adjusting generation parameters such as temperature, or trying a stronger model. Strong retrieval metrics alone do not demonstrate business success.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “3.4 Answer Correctness.”
</details>

## Question 9

An organization is building an evaluation set for an employee-support bot. Which approach best reflects the chapter’s recommendations for making the set representative and its answers authoritative?

A. Have the technical team invent likely questions and use chatbot outputs as ground truth.

B. Sample real user questions, tickets, and business scenarios, and have domain experts provide the ground truth.

C. Ask domain experts to write only high-frequency questions and let technical staff approve business correctness.

D. Use only questions with easily retrieved answers and exclude edge cases to stabilize scores.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Sample real user questions, tickets, and business scenarios, and have domain experts provide the ground truth.**

Real questions, feedback, tickets, and edge cases help the test set reflect business needs. Domain experts are needed to judge answers for correctness, completeness, and business compliance. Technical staff can assess whether retrieval found supporting information, but that does not replace domain judgment about the correct answer.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “4.1 Building a High-Quality Evaluation Dataset.”
</details>

## Question 10

A team wants to replace its embedding model after one disappointing case, without first establishing a baseline or checking whether the knowledge base contains the needed fact. Which sequence best follows the chapter’s evaluation-first strategy?

A. Choose an algorithm metric, optimize it immediately, and set a business target after results improve.

B. Replace the embedding model, then create a test set from whichever outputs seem best.

C. Freeze the current dataset permanently and avoid reviewing results with domain experts.

D. Define business goals, build a representative expert-grounded dataset, establish baseline scores, optimize diagnosed issues, and compare results.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Define business goals, build a representative expert-grounded dataset, establish baseline scores, optimize diagnosed issues, and compare results.**

Evaluation before optimization provides a baseline and helps determine whether a change improved performance or caused regressions. The chapter aligns algorithm metrics with business goals and recommends continuous evaluation operations as user needs change. Replacing a component after one case risks optimizing without evidence about the underlying issue.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “4.2 Evaluation-First Optimization Strategy,” “4.3 Aligning Business Metrics with Evaluation Metrics,” and “4.4 Continuous Operations of the Evaluation System.”
</details>
