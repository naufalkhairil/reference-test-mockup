# Professional Exam: Automated Evaluation of FAQ Bot Performance (Ragas Metrics and Evaluation Operations)

Choose the single best answer for each question. This is a source-grounded practice exam based exclusively on the course notebook `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb`; it is a draft for study purposes, not a validated or official certification exam.

## Question 1

A team is instrumenting its RAG Q&A bot with Ragas. It wants a metric that answers two questions at once: "Do the retrieved context chunks contain a high proportion of information relevant to the correct answer?" and "Are the most relevant chunks ranked near the top of the retrieved list?" It also needs to know which pipeline phase this metric evaluates. Which choice correctly identifies the metric and its phase?

A. Answer relevance — it evaluates the generation phase by measuring whether retrieved contexts are relevant to the question

B. Context recall — it evaluates the retrieval phase by measuring whether relevant contexts are ranked highly

C. Context precision — it evaluates the retrieval phase by measuring the proportion and ranking of relevant information in the retrieved contexts

D. Faithfulness — it evaluates the generation phase by measuring the signal-to-noise ratio of the retrieved contexts

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Context precision — it evaluates the retrieval phase by measuring the proportion and ranking of relevant information in the retrieved contexts**

The notebook lists context precision under "Retrieval phase evaluation" and defines it as assessing "whether the retrieved context contains a high proportion of relevant information related to the correct answer"; section 2.2.1 adds that it measures whether relevant information "is ranked highly and makes up a large proportion (signal-to-noise ratio)." Both parts of the stem (proportion and ranking) map directly onto this metric.

The most tempting alternative is B: context recall also evaluates retrieval, but it measures how many of the relevant reference materials are successfully retrieved (coverage of the ground truth), not whether relevant chunks are ranked highly or make up a large proportion. A and D misplace generation-phase metrics onto a retrieval-phase question.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "2. Using Ragas to evaluate application performance" (metrics list: retrieval phase evaluation) and "2.2.1 Quick start" (definitions of Context Precision and Context Recall). The metric-to-phase mapping and the ranking/proportion definition are stated directly in these passages.
</details>

## Question 2

A team prototypes its own automated evaluator. Function `test_answer` prompts an LLM to reply only "Valid response" or "Invalid response" for a question–answer pair. When the bot answers "Michael Johnson is in the IT Infrastructure Department..." — a confident reply that is not supported by the source documents, which place the relevant Michael Johnson in the Course Development Department — `test_answer` returns "Valid response." According to the notebook's assessment of this homemade approach, what limitation does this outcome demonstrate?

A. The judge model (qwen-max) is too small to detect factual errors, so a larger judge model would resolve the false positive

B. `test_answer` checks only whether the answer effectively responds to the question, so confident hallucinations can pass as valid, producing false positives in evaluation

C. The judge was not given the retrieved contexts, which are a required input for every Ragas metric, so the verdict cannot be trusted

D. Single question–answer pairs cannot be judged reliably; LLM judges require batch datasets of at least three responses per question

<details>
<summary>Show answer and rationale</summary>

**Answer: B — `test_answer` checks only whether the answer effectively responds to the question, so confident hallucinations can pass as valid, producing false positives in evaluation**

Section 1.3.3 lists exactly this as a limitation of the prototype: "LLMs can generate responses that sound confident and plausible but are not factually accurate. The `test_answer` method, as currently implemented, may not be able to effectively detect such hallucinations, leading to false positives in evaluation." The scenario in the stem mirrors the notebook's Michael Johnson case, where the answer was fluent and on-topic but factually ungrounded.

Option C is the most tempting alternative but fails on the source: the notebook's own companion check (`test_contexts`) does feed reference materials to the judge, and Ragas' answer_correctness metric requires only question and ground_truth — contexts are not "required for every Ragas metric." The stated defect of `test_answer` is its inability to detect hallucination, which is precisely why the notebook recommends moving to a mature framework like Ragas.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "1.3.3 Summary of evaluation logic" (limitations: Hallucination Detection, false positives) and "1.3.1 Validating answer quality using LLMs" (the `test_answer` code example).
</details>

## Question 3

Ragas computes the factual-accuracy component of answer correctness by having an LLM build assertion lists for the answer and the ground truth, then classifying assertions into TP, FP, and FN. For one evaluated response, the comparison yields TP = 2, FP = 1, and FN = 1. Using the formula given in the notebook, `f1 score = tp / (tp + 0.5 * (fp + fn))`, what is the factual accuracy score?

A. 0.33

B. 0.50

C. 0.80

D. 0.67

<details>
<summary>Show answer and rationale</summary>

**Answer: D — 0.67**

Applying the notebook's formula directly: f1 = 2 / (2 + 0.5 × (1 + 1)) = 2 / 3 ≈ 0.67. This is a straightforward application of the stated formula to new counts.

Option B (0.50) is the most tempting alternative because it is the result of the notebook's own worked example, where TP = FP = FN = 1 (1 / (1 + 0.5 × 2) = 0.5); selecting it means recalling the example result instead of applying the formula to the stem's counts.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "2.1.2 Understanding How Answer Correctness Is Calculated," subsection "Factual accuracy" (the `f1 score = tp / (tp + 0.5 * (fp + fn))` formula and the TP=1, FP=1, FN=1 worked example).
</details>

## Question 4

An engineer evaluates a response where the answer states "Michael Johnson is a colleague in the Course Development Department responsible for big data direction" while the ground truth states he is "responsible for technical writer tasks." Embedding-based similarity alone scores the pair highly because most wording overlaps. According to the notebook, how does Ragas capture the factual conflict that similarity measures miss?

A. It uses an LLM to generate assertion lists for both the answer and the ground truth, classifies each assertion as matching (TP), unsupported (FP), or missing (FN), and scores factual accuracy from those counts

B. It applies the final weighting so that semantic similarity dominates the score, letting the shared department phrasing determine the outcome

C. It computes cosine, Euclidean, and Manhattan distances between the two texts and takes the minimum as the factual accuracy score

D. It re-embeds both texts with a domain-specific embedding model until the role difference becomes separable in vector space

<details>
<summary>Show answer and rationale</summary>

**Answer: A — It uses an LLM to generate assertion lists for both the answer and the ground truth, classifies each assertion as matching (TP), unsupported (FP), or missing (FN), and scores factual accuracy from those counts**

Section 2.1.2 uses this exact big-data-versus-technical-writer example and explains that such differences "are not easily captured through simple LLM or embedding model calls," so Ragas "uses an LLM to generate lists of assertions for both the answer and the ground truth, then compares these lists to identify matching and conflicting facts." The role conflict becomes an FP (from the answer) and an FN (from the ground truth), lowering the F1-based factual accuracy score.

Option B is the most instructive failure: the final score does combine components by weighting, but the weights are 0.25 × semantic similarity + 0.75 × factual accuracy — factual accuracy dominates, not similarity — and weighting alone only combines component scores; it is the assertion comparison that actually detects the conflicting fact. C confuses the similarity component's distance methods with factual accuracy; D proposes a fix the notebook does not describe and contradicts its point that embeddings struggle with this case.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "2.1.2 Understanding How Answer Correctness Is Calculated," subsections "Factual accuracy" (assertion lists, TP/FP/FN walkthrough) and "Final Score Calculation" (0.25/0.75 weighting).
</details>

## Question 5

A Ragas run on the question "Which department is Michael Johnson in?" returns context_recall = 1.0 and context_precision = 0.5 for one row. Inspection shows the retrieved contexts are ["Newton discovered the law of universal gravitation", "Michael Johnson, engineer in the Course Development Department..."]. According to the notebook's optimization guidance, what does this pattern indicate and what is the most targeted improvement?

A. Key relevant documents are being missed by retrieval; expand or supplement the knowledge base to raise coverage

B. The key fact is retrieved, but an irrelevant chunk is ranked above it; introduce reranking in the retrieval phase so the most relevant segments appear first

C. Retrieval is adequate and the generation phase is fabricating details; lower the LLM's temperature

D. A precision score of 0.5 is expected whenever more than one chunk is retrieved, because Ragas penalizes multi-chunk contexts; no action is required

<details>
<summary>Show answer and rationale</summary>

**Answer: B — The key fact is retrieved, but an irrelevant chunk is ranked above it; introduce reranking in the retrieval phase so the most relevant segments appear first**

The notebook walks through this exact row: context_recall is 1.0 because the chunk supporting the ground truth was retrieved, while context_precision is 0.5 because the irrelevant "Newton" chunk sits at position 1 (precision contributions 0/1 and 1/2, summed and divided by 1 relevant context). Section 3.3 then prescribes the fix for low context precision: "implement reranking during the retrieval phase to improve the ranking of related text segments and ensure that the most relevant information appears first."

Option A is the tempting alternative but is ruled out by the stem's own data: a recall of 1.0 means no relevant ground-truth information was missed, so knowledge-base expansion addresses the wrong metric. C misreads the signal — precision is a retrieval-phase metric, not evidence about generation.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "2.2.1 Quick start" (interpretation of the recall 1.0 / precision 0.5 row), "2.2.2 ... context precision" (step-by-step calculation), and "3.3 Context Precision" (reranking recommendation).
</details>

## Question 6

An internal Q&A bot shows consistently low context_recall on production traffic. An audit confirms the knowledge base already contains content sufficient to answer the sampled questions. Query logs show that users typically submit terse keyword-style queries such as "Leave Request" or "Course Development Department." According to the notebook's guidance for improving a low context recall score, which optimization most directly targets the diagnosed cause?

A. Replace the embedding model with a higher-quality model that better captures deep semantic meaning

B. Add a reranking step so that relevant segments are ordered before irrelevant ones

C. Use an LLM with a designed prompt template to rewrite users' vague queries into complete, detailed questions before retrieval

D. Fine-tune the generation LLM so it copes better with ambiguous, incomplete questions

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Use an LLM with a designed prompt template to rewrite users' vague queries into complete, detailed questions before retrieval**

Section 3.2 lists query rewriting for exactly this situation: users submit "vague or ambiguous queries such as: 'Course Development Department,' 'Leave Request'... If these questions are directly input into a RAG application, they are unlikely to retrieve relevant and effective text segments. To address this, you can design a prompt template... and use LLMs to rewrite the queries, improving the accuracy of the retrieval process." The stem's audit matches the notebook's precondition — the knowledge base is already sufficient — so the gap is in how queries are expressed, not in the corpus.

Option A is the most tempting alternative because replacing the embedding model is also a listed remedy for low recall; however, the notebook positions it for cases where surface wording differs from the corpus despite comprehensive content, whereas the diagnosed root cause here is vague, under-specified user queries, which the notebook explicitly assigns to query rewriting. B targets context precision (ranking), not recall, and D addresses generation rather than retrieval.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "3.2 Context recall" (the "Check the Knowledge Base," "Replace the Embedding Model," and "query rewriting" bullets, including the 'Leave Request' example).
</details>

## Question 7

After several iterations, a RAG system's Ragas report shows high context_recall and high context_precision, but answer_correctness remains low across the test set. According to the notebook's decision rule for this metric pattern, what is the correct diagnosis and the recommended course of action?

A. The retrieval phase is underperforming; replace the embedding model or expand the knowledge base until answer correctness rises

B. The evaluation dataset must contain mislabeled ground truth; have experts relabel it before changing the system

C. The retrieved contexts are poorly ranked; add reranking to lift relevant chunks to the top

D. Retrieval is working but the generation phase has issues; optimize prompts, adjust generation hyperparameters such as temperature, consider a more powerful LLM, or fine-tune the model

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Retrieval is working but the generation phase has issues; optimize prompts, adjust generation hyperparameters such as temperature, consider a more powerful LLM, or fine-tune the model**

Section 3.4 states the rule verbatim in substance: "If this metric [answer correctness] has a low score while the previous two metrics have high scores, it indicates that the RAG system performs well in the retrieval phase but encounters issues in the generation phase. You can try... optimizing prompts, adjusting hyperparameters (such as temperature) of LLMs generation, or replacing with a more powerful LLM, and even fine-tuning the LLM."

Options A and C are tempting only if the metric pattern is misread: both prescribe retrieval-side fixes, but the stem establishes that both retrieval metrics are already high. B speculates dataset error, which the notebook's decision rule does not support for this pattern.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "3.4 Answer Correctness" (diagnosis of low answer correctness with high context metrics, and the listed generation-side remedies).
</details>

## Question 8

To eliminate retrieval misses entirely, an engineer proposes "cramming everything into the LLM": for every question, pass the whole knowledge base as context and let the model find the answer. According to the notebook's discussion of context quality, why is this rejected?

A. It would exceed the embedding model's maximum input length and cause indexing to fail

B. Even when the key clue is present, the LLM may overlook it when it is buried in irrelevant information ("Lost in the Middle"); the knowledge concentration of the context determines the upper limit of RAG accuracy

C. It forces the LLM to refuse to answer because it cannot verify which portion of the context is authoritative

D. It prevents Ragas from computing context recall, because ground-truth statements cannot be matched against an unbounded context

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Even when the key clue is present, the LLM may overlook it when it is buried in irrelevant information ("Lost in the Middle"); the knowledge concentration of the context determines the upper limit of RAG accuracy**

Section 3.1 addresses this proposal directly: "even if a key clue exists within a large volume of data, the LLM may 'overlook' it if it is buried in a sea of irrelevant information. This is known as the 'Lost in the Middle' phenomenon," and concludes that "the bottleneck of RAG accuracy often lies not in whether the LLM is 'smart' enough, but in the 'Knowledge Concentration' of the context provided... the quality of the context you provide directly determines the upper limit of your RAG system."

The alternatives invent failure modes the notebook does not cite: A misattributes the problem to the embedding model's indexing limit rather than the generation context; C and D describe refusal behavior and metric computation issues that the passage does not claim.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "3.1 Context is the lifeline of RAG" (the "cramming everything into the LLM" discussion, "Lost in the Middle," and "Knowledge Concentration").
</details>

## Question 9

A company is building its first serious evaluation dataset for a customer-service RAG bot. Questions will be sampled from real production traffic. The team must now decide who authors the ground-truth answers. According to the notebook, who should provide the ground truth, and why?

A. The engineers who built the RAG pipeline, because they understand what the retrieval system can and cannot surface

B. Real users sampled from production, because they submitted the original questions and know what they meant

C. The LLM judge itself, because it can generate reference answers at scale and stay consistent with automated scoring

D. Domain experts, because only they know which answers are correct, good, and compliant with business standards; technical staff can judge retrieval relevance but not business correctness

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Domain experts, because only they know which answers are correct, good, and compliant with business standards; technical staff can judge retrieval relevance but not business correctness**

Section 4.1 is explicit: "The ground truth in the evaluation dataset must be provided by domain experts... Only domain experts know 'what answers are correct, good, and compliant with business standards,'" while "Technical staff can judge 'whether the system retrieved relevant content,' but cannot judge 'whether the answer is correct, complete, and compliant from a business perspective.'" The notebook's key insight pairs real-user questions with expert-written answers so that evaluation reflects real business performance.

Option B is the most tempting alternative because real users do belong in the pipeline — but the notebook assigns them the role of supplying questions (sampling, tickets, feedback), not authoring ground truth. A assigns the ground-truth role to exactly the group the notebook says cannot judge business correctness, and C contradicts the requirement for expert-provided answers.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "4.1 Building a High-Quality Evaluation Dataset" ("Where do the questions... come from?" and "Where does the Ground Truth come from?" with the Key insight callout).
</details>

## Question 10

A team launches a Q&A bot and immediately begins a series of optimizations — swapping embedding models, rewriting prompts, and changing chunk sizes. Each change "feels better" anecdotally, but nobody can say whether overall quality improved, and some changes appear to regress other question types (a seesaw effect). According to the notebook, which practice should the team have established before optimizing, and what does it protect against?

A. An evaluation baseline first: build the evaluation dataset from real user questions with expert-written ground truth, configure automated evaluation to obtain baseline scores, then compare metrics before and after each optimization

B. An immediate upgrade to a more powerful LLM, because a stronger model reduces the need for measurement-driven tuning

C. Postponing evaluation until several optimization cycles have completed and user satisfaction surveys have accumulated

D. Letting the evaluation LLM generate the ground-truth answers automatically so that metric computation can begin sooner

<details>
<summary>Show answer and rationale</summary>

**Answer: A — An evaluation baseline first: build the evaluation dataset from real user questions with expert-written ground truth, configure automated evaluation to obtain baseline scores, then compare metrics before and after each optimization**

Section 4.2 states the principle: "evaluation should come before optimization, not 'optimize first, then evaluate to see the results,'" and lists exactly the failure modes in the stem — "Avoid blind optimization: Without an evaluation baseline, you don't know if optimization is actually effective," "Quantify improvement: From 'feels better' to 'metrics improved by 15%),'" and "Prevent seesaw effect: One optimization may cause regression elsewhere; evaluation reveals overall improvement." The phase table sequences "Establish automated evaluation → obtain baseline scores" before "Targeted optimization" and "Evaluation verification."

The most tempting alternative, C, inverts the required order — the notebook's whole point is that evaluation precedes optimization, not follows it. D undermines dataset quality by removing the expert-authored ground truth required in section 4.1, and B substitutes a model upgrade for the measurement discipline the scenario lacks.

**Source:** `2_4_Automate_Evaluation_of_FAQ_Bot_Performance.ipynb` — "4.2 Evaluation-First Optimization Strategy" (phase table and the "Why 'evaluation first'?" bullets).
</details>
