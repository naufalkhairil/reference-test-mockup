# Professional Exam: Automated Evaluation of RAG Applications

Choose the single best answer for each question. Assume the evaluation data and metric outputs described in each scenario are reliable unless the question asks you to assess their limitations.

## Question 1

A RAG chatbot answers a question about an employee by combining the department of one person with the job title and manager of another person who has the same name. The answer sounds coherent, but the source documents contain multiple people with that name. What is the strongest next diagnostic step before changing the language model?

A. Increase the answer relevance score threshold and suppress all answers below it.
B. Compare only the generated answer with a reference answer and leave retrieval unexamined.
C. Inspect the retrieved chunks and determine whether they identify the right person and support each claim in the answer.
D. Add more documents about the employee without checking which chunks were retrieved.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Inspect the retrieved chunks and determine whether they identify the right person and support each claim in the answer.**

The failure may involve ambiguous entities, misleading retrieved context, or the model combining facts from separate records. Reviewing the context passed into generation helps locate the failure before selecting an optimization. A fluent, specific answer is not evidence that its claims are grounded. Comparing only the final answer may establish that it is wrong, but it does not reveal where the RAG pipeline failed.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “1.1 Issues with the Q&A Bot” and “1.2. Inspecting Retrieval Results for Diagnosis.” The chapter identifies the mixed-person answer as misleading and recommends inspecting retrieved context before generation.
</details>

## Question 2

A team’s prototype evaluator receives only the user’s question and the generated answer. It labels a confident but factually wrong answer “valid” because the answer appears to address the question. Which change most directly addresses this evaluator’s blind spot?

A. Provide evidence such as retrieved context or a verified ground truth and evaluate factual support, rather than judging responsiveness alone.
B. Require the evaluator to return a longer explanation while keeping the same two inputs.
C. Run the same question-answer pair through the evaluator several times and accept the majority label.
D. Replace the evaluator’s binary labels with a larger set of labels, without adding evidence.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Provide evidence such as retrieved context or a verified ground truth and evaluate factual support, rather than judging responsiveness alone.**

The prototype `test_answer` checks whether the answer effectively responds to the question; by itself, that test can miss a plausible hallucination. Evaluating support against reference material addresses the grounding question. Repeating an evidence-free judgment or expanding its label set does not supply the missing facts.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “1.3.1 Validating answer quality using LLMs,” “1.3.2 Validating context relevance,” and “1.3.3 Summary of evaluation logic.” The notebook says the simple answer check may produce false positives and introduces reference-context validation as a separate check.
</details>

## Question 3

For a test case, the chatbot’s answer accurately repeats information found in the retrieved passages, but it does not address what the user asked. Which pair of metric outcomes best describes this case?

A. Low faithfulness and high answer relevance.
B. High context recall and low context precision.
C. Low answer correctness and high context precision, necessarily.
D. High faithfulness and low answer relevance.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — High faithfulness and low answer relevance.**

Faithfulness concerns whether the answer is factually consistent with the retrieved reference material. Answer relevance concerns whether the answer responds to the user’s question. The scenario separates those properties: the answer is grounded in the passages but fails to address the query. Retrieval metrics do not measure this generation-stage distinction.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2. Using Ragas to evaluate application performance.” The metric overview defines Faithfulness in relation to retrieved materials and Answer Relevance in relation to the question.
</details>

## Question 4

A team wants to compare three generated answers to the same question against an expert-approved answer using Ragas Answer Correctness. Which dataset design matches the notebook’s example?

A. Store the question, retrieved contexts, and ground truth, but omit each generated answer.
B. Store the question, each generated answer, and the known ground truth for that case.
C. Store the generated answer and model name, then use the question as the ground truth.
D. Store the retrieved contexts and generated answer, then infer the ground truth from the highest scoring output.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Store the question, each generated answer, and the known ground truth for that case.**

The evaluation compares the model’s answer with a correct answer already known to the team. In the example dataset, `question`, `answer`, and `ground_truth` are all present. Contexts are needed for retrieval-oriented metrics such as context recall and context precision, but they do not replace the generated answer or ground truth for this comparison.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2.1.1 Quick start,” including the sample dataset code. The prose identifies the question and ground truth, and the code supplies the generated answer as the third evaluation field.
</details>

## Question 5

In the notebook’s Answer Correctness method, an answer produces 2 true-positive assertions, 1 false-positive assertion, and 1 false-negative assertion. Its semantic similarity score is 0.80. Using the notebook’s stated weights and formula, what is the final score?

A. 0.60
B. 0.67
C. 0.70
D. 0.80

<details>
<summary>Show answer and rationale</summary>

**Answer: C — 0.70.**

Factual accuracy is calculated as `TP / (TP + 0.5 × (FP + FN))`, so it is `2 / (2 + 0.5 × (1 + 1)) = 2/3`. The final score is `0.25 × semantic similarity + 0.75 × factual accuracy`, giving `0.25 × 0.80 + 0.75 × 2/3 = 0.70`. The calculation gives factual accuracy three times the weight of semantic similarity.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2.1.2 Understanding How Answer Correctness Is Calculated,” the TP/FP/FN F1 formula and “Final Score Calculation.”
</details>

## Question 6

A retrieval test consistently finds the key passage needed to answer each question, but it also places unrelated passages among the retrieved results, ahead of some relevant passages. Which metric and intervention best target this issue?

A. Context precision; improve the ranking so relevant passages appear earlier and reduce irrelevant material.
B. Context recall; add more ground-truth statements to the generated answers.
C. Answer relevance; replace the retrieval algorithm with a more concise language model.
D. Faithfulness; increase the number of retrieved passages to ensure coverage.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Context precision; improve the ranking so relevant passages appear earlier and reduce irrelevant material.**

The scenario says the required evidence is being retrieved, so the main issue is the relevance and ordering of the retrieved results. Context precision addresses whether relevant information ranks highly and whether retrieval contains a strong signal-to-noise ratio. The notebook recommends reranking to move relevant passages earlier. Context recall instead focuses on whether relevant facts are missed.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “2.2.1 Quick start,” “2.2.2 Understanding the calculation process of context recall and context precision,” and “3.3 Context Precision.”
</details>

## Question 7

The knowledge base has been reviewed and contains the information needed to answer employee questions. However, users often submit vague phrases such as “Leave Request,” and those queries fail to retrieve useful passages. Which optimization is most directly aligned with the diagnosed problem?

A. Fine-tune the answer model on the existing responses before changing query handling.
B. Add more documents even though the needed information is already present.
C. Lower the answer correctness threshold so more generated answers pass evaluation.
D. Rewrite vague queries into clearer questions using a prompt informed by common employee questions.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Rewrite vague queries into clearer questions using a prompt informed by common employee questions.**

The knowledge base is already sufficient, while the query wording is too vague to retrieve useful segments. The chapter specifically recommends query rewriting for vague or ambiguous queries. Adding documents addresses a knowledge gap, and changing generation does not directly fix the described retrieval input problem.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “3.2 Context recall,” the “query rewriting” recommendation for vague employee queries.
</details>

## Question 8

After a release, a RAG system has strong context recall and context precision, but Answer Correctness remains low. Which diagnosis and next step best fit the notebook’s evaluation framework?

A. Retrieval is the primary failure; expand the knowledge base before reviewing answer generation.
B. Retrieval appears effective on these cases, so investigate generation choices such as the prompt, generation parameters, or model.
C. The business objective must be changed because strong retrieval scores prove user satisfaction.
D. The evaluation dataset is necessarily invalid because retrieval and answer metrics disagree.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Retrieval appears effective on these cases, so investigate generation choices such as the prompt, generation parameters, or model.**

High retrieval scores paired with low Answer Correctness point to a generation-stage problem in the chapter’s diagnostic model. The suggested responses include optimizing prompts, adjusting generation hyperparameters such as temperature, or trying a stronger model. The metric pattern does not establish user satisfaction or prove that the dataset is invalid.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “3.4 Answer Correctness.” The section links high retrieval metrics plus low answer correctness to generation and names prompt, parameter, and model changes as possible interventions.
</details>

## Question 9

An organization is building a production evaluation set for employee support questions. Which division of responsibilities best reflects the chapter’s recommendations?

A. Technical staff write all questions and ground truths; domain experts review only retrieval scores.
B. Domain experts select model parameters; technical staff decide whether answers meet business policy.
C. Sample questions from real user scenarios and have domain experts define correct answers; technical staff can assess retrieval evidence.
D. Use only questions with easy-to-automate answers and let the chatbot generate its own ground truths.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Sample questions from real user scenarios and have domain experts define correct answers; technical staff can assess retrieval evidence.**

The chapter recommends sampling real user questions, tickets, feedback, and business scenarios, including edge cases. It assigns ground-truth authorship to domain experts because correctness, completeness, and compliance require business knowledge; technical staff can assess whether retrieval found relevant material. A model-generated ground truth would not provide the independent standard the evaluation needs.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “4.1 Building a High-Quality Evaluation Dataset.”
</details>

## Question 10

A team proposes changing the embedding model immediately after one poor test result, then checking whether the result looks better. Which operating approach is most consistent with the chapter’s evaluation-first strategy?

A. Define business goals, build a representative expert-grounded set, establish a baseline, optimize against diagnosed issues, and compare results before and after.
B. Change one component at a time based on intuition, then build a test set from the outputs that improved.
C. Optimize whichever algorithm metric is easiest to raise, even if it is not linked to a business outcome.
D. Freeze the evaluation set permanently so changes in user needs cannot affect comparisons.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Define business goals, build a representative expert-grounded set, establish a baseline, optimize against diagnosed issues, and compare results before and after.**

The evaluation-first process defines measurable business goals, builds a representative dataset, establishes baseline scores, applies targeted optimization, and verifies changes against the baseline. This helps avoid blind optimization and regression. Algorithm metrics support decisions, but business outcomes such as user satisfaction remain the goal; the dataset should also be updated as user needs evolve.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — “4.2 Evaluation-First Optimization Strategy,” “4.3 Aligning Business Metrics with Evaluation Metrics,” and “4.4 Continuous Operations of the Evaluation System.”
</details>
