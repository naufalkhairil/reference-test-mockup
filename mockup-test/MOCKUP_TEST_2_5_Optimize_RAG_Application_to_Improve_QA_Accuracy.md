# Mockup Test: 2 5 Optimize RAG Application to Improve QA Accuracy

Choose the single best answer for each question.

## Question 1

A RAG answer is wrong because the retrieved passages are irrelevant. Which part should be investigated first?

A. The output streaming UI.

B. The model deployment port.

C. The API key display.

D. Retrieval quality.

<details>
<summary>Show answer and explanation</summary>

**Answer: D**

RAG generation depends on the context retrieved; irrelevant context is a retrieval failure.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “RAG application optimization” — retrieval versus generation diagnosis.
</details>

## Question 2

What is the purpose of reranking retrieved chunks?

A. Delete chunks that are semantically similar.

B. Reorder candidate passages by relevance after an initial retrieval step.

C. Rewrite the user’s question as an answer.

D. Convert answer text into an API key.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

Reranking refines the ordering of retrieved candidates so the most useful context is prioritized.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “Improve retrieval accuracy” — reranking.
</details>

## Question 3

How does sentence-window retrieval help when chunks are small?

A. Retrieve a focused matching sentence while supplying its surrounding context.

B. Replace embeddings with exact keyword search.

C. Store the entire corpus in the prompt every time.

D. Reduce the model’s output length.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Sentence-window retrieval can match a focused unit and expand the context around it.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “Improve retrieval accuracy” — sentence window retrieval.
</details>

## Question 4

A question uses different words from the policy but has the same meaning. Which retrieval representation helps match meaning?

A. Text embeddings.

B. The assistant role.

C. A response token cap.

D. A raw character count.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Embeddings support semantic similarity across differently phrased text.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “Retrieval optimization” — embedding-based similarity.
</details>

## Question 5

Why might query rewriting improve retrieval?

A. It changes the source documents automatically.

B. It prevents the LLM from seeing retrieved context.

C. It guarantees the query contains every policy detail.

D. It can make the user’s intent and key terms clearer for searching the knowledge base.

<details>
<summary>Show answer and explanation</summary>

**Answer: D**

A clearer search query can improve matching against indexed content.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “Query transformation / query rewriting”.
</details>

## Question 6

The retrieved material is relevant, but the answer ignores it and adds unsupported claims. What should be improved?

A. The notebook kernel selection.

B. The generation prompt’s grounding instructions and answer behavior.

C. The query embedding dimensions only.

D. The vector database’s storage capacity only.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

When context is good but the response is ungrounded, generation instructions are a likely point to improve.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “Generation optimization” — grounding response in retrieved context.
</details>

## Question 7

What is a useful way to assess whether a RAG change improved accuracy?

A. Run the same representative evaluation questions and inspect answer quality and retrieval evidence.

B. Use a single handpicked successful query.

C. Measure whether the prompt became longer.

D. Compare only the number of indexed files.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

A consistent evaluation set helps compare changes and isolate quality improvements.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “Evaluate RAG optimization”.
</details>

## Question 8

A document is too long and retrieval repeatedly returns mixed topics. What indexing adjustment could help?

A. Remove embeddings from the pipeline.

B. Set all answers to JSON.

C. Review chunking boundaries and size so chunks preserve coherent units.

D. Increase conversation history.

<details>
<summary>Show answer and explanation</summary>

**Answer: C**

Chunking controls the granularity and coherence of retrievable content.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “Indexing optimization” — text chunking.
</details>

## Question 9

Why can a larger top-k retrieval value sometimes hurt answer quality?

A. It prevents index persistence.

B. It may add irrelevant passages that distract or dilute useful context.

C. It removes all semantically similar chunks.

D. It forces deterministic decoding.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

More retrieved context is not always better; noisy passages can distract the model.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “Retrieval parameter tuning” — number of retrieved chunks.
</details>

## Question 10

What is the strongest diagnosis when retrieved passages omit the exact policy detail needed?

A. Turn on streaming.

B. Add more few-shot examples about unrelated topics.

C. Improve indexing or retrieval coverage before changing answer style.

D. Increase the response temperature.

<details>
<summary>Show answer and explanation</summary>

**Answer: C**

Missing evidence points to the retrieval/indexing side of the RAG pipeline.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — “RAG troubleshooting” — distinguish retrieval and generation issues.
</details>
