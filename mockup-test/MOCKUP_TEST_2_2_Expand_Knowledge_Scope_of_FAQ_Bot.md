# Mockup Test: 2 2 Expand Knowledge Scope of FAQ Bot

Choose the single best answer for each question.

## Question 1

A model lacks a company’s internal policy because it was not in its training data. How does RAG address this?

A. Fine-tune on every question at runtime.

B. Retrieve relevant reference material and provide it to the model with the question.

C. Ask users to include the entire policy manually.

D. Replace the model with a keyword matcher.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

RAG supplies external context so the model can answer like an open-book exam.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1. How RAG works”.
</details>

## Question 2

Which sequence matches the lesson’s indexing workflow?

A. Chunk, generate, tokenize, deploy.

B. Parse documents, chunk text, embed chunks, store vectors.

C. Store vectors, parse documents, generate, rerank.

D. Retrieve, generate, parse, fine-tune.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

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

A. Generate the final answer directly.

B. Convert text chunks into numerical vectors that capture semantic meaning.

C. Store the full conversation history.

D. Split API credentials into safe parts.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

Embeddings support semantic comparison by representing the text as vectors.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.1 Indexing” — Text Embedding.
</details>

## Question 5

How does retrieval find candidate context for a user question?

A. Compare the question to model weights.

B. Ask the LLM to invent likely policy text.

C. Embed the question with the same embedding model and compare it with stored chunk vectors.

D. Search only for exact character matches in the original files.

<details>
<summary>Show answer and explanation</summary>

**Answer: C**

The question vector is compared against stored chunk vectors to find the most similar material.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.2 Retrieval and Generation” — Retrieval.
</details>

## Question 6

Why does the lesson call retrieval critical to RAG accuracy?

A. Retrieval determines the API key permissions.

B. The embedding model writes company policy.

C. Generation cannot use more than one text chunk.

D. If the system finds the wrong material, the generated answer is likely to be inaccurate.

<details>
<summary>Show answer and explanation</summary>

**Answer: D**

The quality of the answer depends on retrieving relevant evidence.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.2 Retrieval and Generation” — Retrieval.
</details>

## Question 7

What happens during the generation stage?

A. A prompt combines the question with retrieved text, and the LLM produces a response using that context.

B. The user question is discarded after retrieval.

C. The system converts the answer into document chunks.

D. The vector database retrains the LLM.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Generation assembles retrieved segments and the query in a prompt template for the LLM.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “1.2 Retrieval and Generation” — Generation.
</details>

## Question 8

A team wants to avoid rebuilding a time-consuming index each time it restarts its application. What should it do?

A. Repeat parsing and embedding on every question.

B. Cache only the model answer, not the index.

C. Save the index locally and reload it when needed.

D. Increase the number of prompt examples.

<details>
<summary>Show answer and explanation</summary>

**Answer: C**

The lesson recommends saving and loading an index to avoid repeated construction.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “2.3 Saving and loading index”.
</details>

## Question 9

In multi-turn RAG, why is conversation history not simply the entire solution?

A. Conversation history replaces the vector index.

B. History is never passed to an LLM.

C. RAG cannot answer follow-up questions.

D. The current question still needs to be resolved against relevant knowledge during retrieval.

<details>
<summary>Show answer and explanation</summary>

**Answer: D**

RAG adds retrieval to multi-turn interaction; history helps resolve context, while retrieval supplies knowledge.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “2.4 Multi-turn conversation”.
</details>

## Question 10

Which library does the lesson use to build a RAG application with less implementation code?

A. LlamaIndex.

B. wrk.

C. vLLM.

D. OpenCV.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson introduces LlamaIndex as a way to implement RAG functionality with minimal code.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — “2. Creating a RAG application”.
</details>
