# Mockup Test: 2 2 Expand Knowledge Scope of FAQ Bot

Choose the single best answer for each question.

## Question 1

A model lacks a company’s internal policy because it was not in its training data. How does RAG address this?

A. Retrieve relevant reference material and provide it to the model with the question.

B. Fine-tune on every question at runtime.

C. Replace the model with a keyword matcher.

D. Ask users to include the entire policy manually.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

RAG supplies external context so the model can answer like an open-book exam.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1. How RAG works”.
</details>

## Question 2

Which sequence matches the lesson’s indexing workflow?

A. Parse documents, chunk text, embed chunks, store vectors.

B. Retrieve, generate, parse, fine-tune.

C. Chunk, generate, tokenize, deploy.

D. Store vectors, parse documents, generate, rerank.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Indexing prepares searchable material through parsing, chunking, embedding, and vector storage.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.1 Indexing”.
</details>

## Question 3

Why are documents split into chunks during indexing?

A. Smaller segments can be retrieved efficiently and used as focused references.

B. The model requires each document to contain one sentence.

C. Chunking converts text into API keys.

D. It eliminates the need for embeddings.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson describes chunking as segmenting parsed documents into smaller pieces for faster retrieval.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.1 Indexing” — Text Chunking.
</details>

## Question 4

What is the role of an embedding model in RAG indexing?

A. Convert text chunks into numerical vectors that capture semantic meaning.

B. Generate the final answer directly.

C. Split API credentials into safe parts.

D. Store the full conversation history.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Embeddings support semantic comparison by representing the text as vectors.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.1 Indexing” — Text Embedding.
</details>

## Question 5

How does retrieval find candidate context for a user question?

A. Embed the question with the same embedding model and compare it with stored chunk vectors.

B. Search only for exact character matches in the original files.

C. Ask the LLM to invent likely policy text.

D. Compare the question to model weights.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The question vector is compared against stored chunk vectors to find the most similar material.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.2 Retrieval and Generation” — Retrieval.
</details>

## Question 6

Why does the lesson call retrieval critical to RAG accuracy?

A. If the system finds the wrong material, the generated answer is likely to be inaccurate.

B. Retrieval determines the API key permissions.

C. Generation cannot use more than one text chunk.

D. The embedding model writes company policy.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The quality of the answer depends on retrieving relevant evidence.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.2 Retrieval and Generation” — Retrieval.
</details>

## Question 7

What happens during the generation stage?

A. A prompt combines the question with retrieved text, and the LLM produces a response using that context.

B. The vector database retrains the LLM.

C. The system converts the answer into document chunks.

D. The user question is discarded after retrieval.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Generation assembles retrieved segments and the query in a prompt template for the LLM.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.2 Retrieval and Generation” — Generation.
</details>

## Question 8

A team wants to avoid rebuilding a time-consuming index each time it restarts its application. What should it do?

A. Save the index locally and reload it when needed.

B. Repeat parsing and embedding on every question.

C. Cache only the model answer, not the index.

D. Increase the number of prompt examples.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson recommends saving and loading an index to avoid repeated construction.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “2.3 Saving and loading index”.
</details>

## Question 9

In multi-turn RAG, why is conversation history not simply the entire solution?

A. The current question still needs to be resolved against relevant knowledge during retrieval.

B. History is never passed to an LLM.

C. RAG cannot answer follow-up questions.

D. Conversation history replaces the vector index.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

RAG adds retrieval to multi-turn interaction; history helps resolve context, while retrieval supplies knowledge.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “2.4 Multi-turn conversation”.
</details>

## Question 10

Which library does the lesson use to build a RAG application with less implementation code?

A. LlamaIndex.

B. vLLM.

C. wrk.

D. OpenCV.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson introduces LlamaIndex as a way to implement RAG functionality with minimal code.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “2. Creating a RAG application”.
</details>
