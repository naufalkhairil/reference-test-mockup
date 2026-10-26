# Professional Exam: Expanding the Knowledge Scope of the FAQ Bot — RAG Workflow, LlamaIndex, and Multi-Turn Retrieval

Choose the single best answer for each question.

> Source: `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` (Alibaba Cloud LLM ACP course, Section 2.2). All items are answerable from that notebook alone.

## Question 1

The lesson describes the RAG indexing phase as four steps: Document Parsing, Text Chunking, Text Embedding, and Index Storage. Which step converts parsed text chunks into numerical vectors that capture the semantic meaning of the text, preparing them for later similarity comparisons?

A. Text Embedding

B. Document Parsing

C. Text Chunking

D. Index Storage

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Text Embedding**

The source defines step 3, Text Embedding, as "Using an embedding model to convert text chunks (or paragraphs) into numerical representations (vectors). These vectors capture the semantic meaning of the text, preparing them for future similarity comparisons" — matching the stem word for word.

The tempting confusions are the neighboring steps: Text Chunking (C) only segments parsed documents into smaller chunks "for faster retrieval" without producing vectors, and Index Storage (D) merely stores the already-computed vectors in a vector database. Document Parsing (B) is the earlier conversion of documents into LLM-processable text.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "1.1 Indexing," numbered steps 1–4 (step 3, Text Embedding).
</details>

## Question 2

After text chunks are embedded, the resulting vectors are stored in a specialized vector database. According to the lesson, what is the stated purpose of this Index Storage step?

A. To compress the chunks so they fit within the LLM's context window at answer time.

B. To allow the LLM to fine-tune itself on the company's documents.

C. To encrypt the company's policy documents while they are at rest.

D. To make the vectors efficiently searchable and avoid reprocessing the documents for every query.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — To make the vectors efficiently searchable and avoid reprocessing the documents for every query.**

The source states that in Index Storage, "The resulting vectors are stored in a specialized database (a vector database) to make them efficiently searchable and avoid reprocessing the documents for every query." The index is built once and reused across all queries — the efficiency rationale the stem asks about.

Option A is the most tempting alternative because context-window fit is a real RAG concern elsewhere in the course, but chunking (not storage) is what the source credits with making retrieval fast, and storage's stated purpose is searchability and reuse. Options B and C attribute capabilities (fine-tuning, encryption) to the vector database that the source never mentions.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "1.1 Indexing," step 4 (Index Storage).
</details>

## Question 3

You are reviewing a RAG implementation in which the query-time code embeds the user's question with a different (newer) embedding model than the one used to embed the stored document chunks. According to the lesson's description of the Retrieval stage, what is the correct design?

A. Compare the question's raw text against the chunks' raw text with keyword matching, avoiding embeddings at query time.

B. Convert the question into a vector using the same embedding model that processed the documents, then perform a similarity search against the stored chunk vectors.

C. Re-embed the entire vector database with the query-time model before every question.

D. Send the question directly to the LLM and let it choose relevant chunks from the database by title.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Convert the question into a vector using the same embedding model that processed the documents, then perform a similarity search against the stored chunk vectors.**

The Retrieval stage is specified exactly this way: "First, the question is converted into a vector using the same embedding model that processed the documents. Then, the system performs a similarity search, comparing the question's vector against the vectors of the document chunks stored in the database. The chunks with the highest similarity scores are identified as the most relevant content." Similarity comparison is only meaningful when both sides live in the same vector space, which is why the source requires the same model.

Option C is the most tempting alternative — re-embedding everything with the new model would restore a common vector space — but the source's design keeps one embedding model consistent across indexing and retrieval rather than reprocessing the corpus per query, which would defeat the "avoid reprocessing the documents for every query" purpose of Index Storage. Options A and D bypass vector similarity search entirely, contradicting the described mechanism.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "1.2 Retrieval and Generation," step 1 (Retrieval); see also "1.1 Indexing," step 4 for the reuse rationale.
</details>

## Question 4

Your RAG chatbot retrieves plausible-looking chunks but the final answers are still off target, and management asks where to invest first. According to the lesson, which part of a RAG application is "the most critical," and which techniques does the source suggest (besides powerful embedding models) to improve its accuracy?

A. Generation; switching to a larger LLM for the answer step.

B. Chunking; increasing the chunk size to preserve more context.

C. Retrieval; applying techniques such as reranking and sentence window retrieval.

D. Index Storage; migrating from a vector database to a relational database.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Retrieval; applying techniques such as reranking and sentence window retrieval.**

The source states: "Retrieval is the most critical part of the RAG application. Just as finding the wrong material during an exam—your answer would be inaccurate. To improve retrieval accuracy, besides using powerful embedding models, techniques like reranking and sentence window retrieval can be applied." If the wrong chunks reach the LLM, no generation quality can rescue the answer — the open-book-exam analogy in the stem's situation.

Option A is tempting because generation produces the visible failure (the bad answer), but the source locates the decisive quality lever in retrieval, and never suggests model upsizing as the remedy. Options B and D name pipeline components the source does not identify as most critical, with techniques it does not endorse.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "1.2 Retrieval and Generation," step 1 (Retrieval), final paragraph.
</details>

## Question 5

In the Generation stage, after the relevant chunks are retrieved, what role does the prompt template play according to the lesson?

A. It converts the user's question into a vector before the answer is generated.

B. It splits retrieved documents into smaller chunks so they fit the context window.

C. It stores the generated answer in the vector database for reuse by later queries.

D. It combines the question and the retrieved text segments into the final prompt, so the LLM generates the response leveraging its summarization abilities rather than relying solely on its internal knowledge.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — It combines the question and the retrieved text segments into the final prompt, so the LLM generates the response leveraging its summarization abilities rather than relying solely on its internal knowledge.**

The source describes Generation as: "the RAG application generates the final prompt by combining the question and the retrieved text segments using a prompt template. The LLM then generates the response, leveraging its summarization abilities rather than relying solely on its internal knowledge," illustrated by the typical template "Please answer the user's question based on the following information: {retrieved text segments}. The user's question is: {question}."

Options A and B are tempting because vectorization and chunking are real RAG operations, but the source places them in the Retrieval and Indexing phases respectively — by Generation time both are already done. Option C invents an answer-caching behavior the source never describes.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "1.2 Retrieval and Generation," step 2 (Generation), including the typical prompt-template quote.
</details>

## Question 6

In the lesson's LlamaIndex code that builds the RAG chatbot over the `./docs` folder, which component performs the Document Parsing step of the indexing phase?

A. `VectorStoreIndex.from_documents(...)`, which loads and parses the files.

B. `SimpleDirectoryReader('./docs', required_exts=[...]).load_data()`, which loads files from the folder into document objects.

C. `index.as_query_engine(...)`, which prepares documents for querying.

D. `OpenAILikeEmbedding(...)`, which converts file contents into text.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — `SimpleDirectoryReader('./docs', required_exts=[...]).load_data()`, which loads files from the folder into document objects.**

The code cell's own comment identifies the mapping: "LlamaIndex provides the SimpleDirectoryReader method, which can directly load files from a specified folder into document objects, corresponding to the parsing process." It reads only the required formats (`.pdf`, `.docx`, `.md`) from the docs folder.

Option A is the most tempting alternative because `VectorStoreIndex.from_documents` is the next line and is closely associated with indexing — but the source notes it "includes slicing [chunking] and index creation steps," not parsing. Option C builds the query engine (retrieval-and-generation runtime), and Option D is the embedding model used for vectorization, not parsing.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "2.2 A simple RAG chatbot," the index-building code cell and its inline comments (`SimpleDirectoryReader`, `VectorStoreIndex.from_documents`).
</details>

## Question 7

The lesson saves the built index with `index.storage_context.persist("knowledge_base/test")` and later reloads it with `load_index_from_storage`. According to Section 2.3, what is the primary reason for saving and loading the index instead of rebuilding it each session?

A. Persisting the index improves the embedding model's vector accuracy over time.

B. Persisting the index is required before streaming output can be enabled.

C. Creating an index can be time-consuming; saving it locally and reloading it avoids rebuilding from scratch and improves response speed.

D. Persisting the index prevents the context window from overflowing during long conversations.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Creating an index can be time-consuming; saving it locally and reloading it avoids rebuilding from scratch and improves response speed.**

Section 2.3 states the rationale directly: "Creating an index can be time-consuming. To avoid repeating this process, you can save the index locally and reload it when needed. This improves response speed and avoids rebuilding the index from scratch." The reuse pattern reappears in Section 2.3's `chatbot.rag` wrapper ("The citations have been indexed in previous steps, so the index can be loaded directly here").

Options A, B, and D attach persistence to unrelated concerns — embedding accuracy, streaming support, and context-window management — none of which the source connects to saving/loading the index.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "2.3 Saving and loading index" (narrative plus the `persist` / `load_index_from_storage` code cells).
</details>

## Question 8

A RAG chatbot answers the first turn "Where is Jimmy Peterson's workstation?" correctly. On the second turn the user asks "Who is his supervisor?" and the bot retrieves content about an unrelated person. According to Section 2.4, what is the most likely cause?

A. The condense-question prompt rewrote the second question with the wrong chat history.

B. The retrieval system used only the user's latest input for similarity comparison, so it could not know who "his" refers to.

C. Streaming mode dropped the first turn's context before the second retrieval ran.

D. The vector database evicted the chunks about Jimmy Peterson between turns.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — The retrieval system used only the user's latest input for similarity comparison, so it could not know who "his" refers to.**

The source uses this exact scenario: "if the system only uses the user's latest input for retrieval, it can lose important context from the conversation history, leading to inaccurate results. For example, a user asks 'Where is Jimmy Peterson's workstation?' in the first turn, then asks 'Who is his supervisor?' in the second turn. The retrieval system may not know who 'he' refers to if it only compares the second question with the text segments. This could lead to retrieving incorrect content."

Option A is tempting only if a condense engine were already in place — but the failure described is precisely what happens *without* query rewriting; the lesson introduces `CondenseQuestionChatEngine` as the fix, not as a failure source here. Options C and D invent mechanisms (streaming dropping context, vector eviction) that the source never associates with multi-turn retrieval failures.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "2.4 Multi-turn conversation," the Jimmy Peterson example paragraph.
</details>

## Question 9

A natural idea for fixing multi-turn retrieval is to concatenate the entire historical dialogue with the new question and embed the whole thing as the query. According to Section 2.4, why does the source consider this problematic?

A. The combined text becomes long, and embedding models perform worse on long texts than on short ones, so the retrieval system may struggle.

B. The history contains assistant-role messages, which embedding models cannot encode at all.

C. The vector database rejects queries longer than a single sentence.

D. Full-history queries bypass any reranking stage configured in the pipeline.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — The combined text becomes long, and embedding models perform worse on long texts than on short ones, so the retrieval system may struggle.**

The source states: "If both the full historical dialogue and the question are input into the retrieval system, the retrieval system may struggle due to the text length, (embedding models perform worse on long texts than on short ones)." This is why the lesson presents query rewriting — not full-history embedding — as the common industry solution.

Option B overstates the problem into an impossibility: the source's concern is degraded quality with length, not an inability to encode assistant messages. Options C and D assert hard limits and pipeline interactions the source never mentions.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "2.4 Multi-turn conversation," paragraph beginning "If both the full historical dialogue and the question are input into the retrieval system...".
</details>

## Question 10

Given the problems with both latest-query-only retrieval and full-history retrieval, what is the common industry solution for multi-turn conversation in RAG applications, as implemented by LlamaIndex's `CondenseQuestionChatEngine` in the lesson?

A. Reuse the text chunks recalled in the previous turn as context for the new question.

B. Concatenate all conversation turns and embed the combined text as the query.

C. Skip retrieval on follow-up turns and answer them from the LLM's internal knowledge.

D. Use the LLM to rewrite the query based on the historical dialogue, incorporating key context, then run the rewritten query through the original retrieval-and-generation process.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Use the LLM to rewrite the query based on the historical dialogue, incorporating key context, then run the rewritten query through the original retrieval-and-generation process.**

The source presents this as the two-step industry solution: "1. Use the LLM to rewrite the query based on the historical dialogue, incorporating key information from the conversation. 2. Use the rewritten query to follow the original retrieval and generation process." The demo confirms the behavior: the follow-up "What are the core responsibilities?" is rewritten to "What are the core responsibilities of content development engineers..." using the chat history, and answered correctly.

Options A and B are the two rejected alternatives: reusing previous-turn chunks risks irrelevance to the new query, and full-history embedding degrades because embedding models perform worse on long texts. Option C abandons the private-knowledge grounding RAG exists to provide.

**Source:** `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` — "2.4 Multi-turn conversation," the numbered industry-solution list and the `CondenseQuestionChatEngine` code cell with its "Querying with:" output.
</details>
