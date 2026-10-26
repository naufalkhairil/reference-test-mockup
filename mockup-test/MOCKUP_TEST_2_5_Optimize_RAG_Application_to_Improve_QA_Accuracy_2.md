# Professional Exam: Optimizing RAG Applications to Improve QA Accuracy

Choose the single best answer for each question. This is a source-grounded practice exam based exclusively on the course notebook `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb`; it is a draft for study purposes, not a validated or official certification exam.

## Question 1

A Q&A bot fails to answer "What does Michael Johnson do?" because the correct chunk is not retrieved with the default `similarity_top_k=2`. A developer raises `similarity_top_k` to 5 and the bot starts answering. A reviewer objects that simply increasing the number of recalled chunks "is not a good solution." According to the notebook, which set of reasons supports the reviewer's objection?

A. Raising `similarity_top_k` disables streaming responses and degrades the user experience in production chatbots

B. Recalling more chunks always lowers the Ragas context_recall score because additional chunks dilute the ground-truth statements

C. Recalling far more chunks can exceed the LLM's input length limit and reduce response efficiency and accuracy through excessive irrelevant information, while ambiguity — such as multiple employees sharing the queried name — remains unresolved

D. Values of `similarity_top_k` above the default of 2 require rebuilding the vector index with a different chunking strategy before they take effect

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Recalling far more chunks can exceed the LLM's input length limit and reduce response efficiency and accuracy through excessive irrelevant information, while ambiguity — such as multiple employees sharing the queried name — remains unresolved**

Section 2.1.1 gives precisely these reasons: if recalling more chunks solved the problem, "why not recall the entire knowledge base?... this would not only exceed the LLM's input length limit, but also reduce the efficiency and accuracy of the model's responses due to excessive irrelevant information." It then adds that with several colleagues named Michael Johnson, "simply increasing the number of recalls might retrieve information about multiple Michael Johnsons, but the system would still be unable to accurately decide which one's information to return."

Option B is the tempting alternative for anyone conflating the metrics: more chunks do not "always" lower context_recall — in the notebook's own Ragas evaluation the top-5 run still missed relevant information and produced poor scores for a different reason (irrelevant content mixed in, relevant content not fully recalled). A and D describe constraints the notebook never states.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "2.1.1 Adjusting the code" and the discussion following it (input-length limits, efficiency/accuracy loss from irrelevant information, unresolved name ambiguity), plus "2.1.2 Evaluate improvement effectiveness."
</details>

## Question 2

A company creates a new "Data Analysis Department." No document in the RAG knowledge base mentions it yet. When users ask about the new department, the bot produces confident, fabricated descriptions. According to the notebook's intent-space/knowledge-space framework for the document preparation stage, how should this be diagnosed and fixed?

A. It is uncovered intent space: the knowledge base lacks supporting content for a real user need, so the LLM tends to hallucinate; proactively supplement the missing knowledge and continually track changes in the user intent space

B. It is unused knowledge space: irrelevant content is being recalled and interfering with responses; optimize the recall algorithm and remove content from the knowledge base

C. It is a chunking defect: chunks are too short and truncate the department information; increase chunk length so complete departments fit in one chunk

D. It is a generation-parameter defect: lowering the temperature will stop the model from inventing departments that are absent from the corpus

<details>
<summary>Show answer and rationale</summary>

**Answer: A — It is uncovered intent space: the knowledge base lacks supporting content for a real user need, so the LLM tends to hallucinate; proactively supplement the missing knowledge and continually track changes in the user intent space**

Section 4.1 uses this exact example: "if the company has added a new 'Data Analysis Department,' but there are no related documents in the knowledge base, no matter how much you improve the engineering algorithms, the RAG chatbot will not be able to accurately answer this question. What you need to do is proactively supplement the missing knowledge, and continually track changes in the user intent space." The user need exists (intent space) but has no counterpart in the knowledge space.

Option D is the most tempting alternative — an anti-fabrication prompt (section 4.5) can make the bot admit ignorance, but the notebook's diagnosis for this scenario is that no engineering or algorithmic improvement can produce a correct answer while the knowledge is missing; the substantive fix is supplementing the knowledge base. B mislabels the region (unused knowledge space concerns recalled-but-irrelevant content), and C invents a chunking cause the stem does not support.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.1 Document preparation stage" (the three regions — overlapping area, uncovered intent space with the Data Analysis Department example, and unused knowledge space).
</details>

## Question 3

A RAG application's chunks are individually on-topic, but users complain that answers miss crucial background: the sentence immediately before or after a retrieved sentence often carries the explanation or the consequence that the answer needs. The notebook notes that adjacent chunks frequently have semantic connections. Which technique does the notebook recommend for this situation?

A. Switch to token chunking with a smaller `chunk_size` so that each chunk fits the model's context more precisely

B. Switch to semantic chunking with a lower `breakpoint_percentile_threshold` so that topics split more aggressively

C. Add a reranking postprocessor so the most relevant existing chunks are ordered first

D. Use sentence window retrieval, where each chunk carries surrounding sentences as a context window that a metadata replacement postprocessor restores at query time

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Use sentence window retrieval, where each chunk carries surrounding sentences as a context window that a metadata replacement postprocessor restores at query time**

Section 4.2.3.3 describes sentence window retrieval as "Each chunk includes surrounding sentences as the context window," and the accompanying code pairs `SentenceWindowNodeParser.from_defaults(window_size=3, window_metadata_key="window", ...)` with `MetadataReplacementPostProcessor(target_metadata_key="window")`, noting it "requires a special post-processor." The retrieval-phase table in section 4.4 reinforces the diagnosis: "After retrieving a chunk, supplement it with several adjacent chunks before and after... adjacent chunks often have semantic connections, and looking at a single chunk might lose important information." The chunking guidance also routes "long documents, need to maintain context" to sentence window retrieval.

The tempting alternatives fail: A and B change how boundaries are cut but still isolate sentences — smaller or more aggressive chunks make the lost-adjacent-context problem worse, not better. C reorders chunks that were retrieved; it does not restore the neighboring context that was never included.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.2.3.3 Sentence window Retrieval" (description and the `SentenceWindowNodeParser` + `MetadataReplacementPostProcessor` code example), "4.4 Retrieval recall phase" table (Sliding Window Retrieval row), and the chunking-selection guidance at the end of "4.2.3."
</details>

## Question 4

A team is choosing between `text-embedding-v3` and `text-embedding-v4` for an enterprise RAG system whose knowledge base contains many records with heavy keyword overlap (identical employee names and addresses, differing roles). In similarity tests, v3 produces closely clustered scores across records, while v4 produces a distinct gap between the correct record and the noise. According to the notebook, which observation is the stronger indicator of retrieval precision, and which model does it recommend when the application must distinguish "similar" from "relevant"?

A. Higher absolute similarity scores for the top hit indicate precision; choose text-embedding-v3 because it is the newer, more discerning model

B. A distinct gap between the correct record and the noise records indicates precision; choose text-embedding-v4, which is designed for semantic discernment and disambiguation in complex, keyword-overlapping data

C. Higher context_recall in a pipeline evaluation indicates precision; choose text-embedding-v3 because its broad retrieval guarantees fewer misses

D. Embedding throughput indicates precision; either model is equivalent once batch size is tuned

<details>
<summary>Show answer and rationale</summary>

**Answer: B — A distinct gap between the correct record and the noise records indicates precision; choose text-embedding-v4, which is designed for semantic discernment and disambiguation in complex, keyword-overlapping data**

The notebook's "Key Insight" states: "In RAG, do not just chase high absolute scores. A distinct gap between the correct answer and the 'noise' is a much stronger indicator of a model's retrieval precision." Its Phase 1 analysis shows v4 producing exactly that gap (e.g., ~0.58 vs ~0.33 for role matching) while v3 is "distracted" by the shared name, and its final advice is to "Transition to v4 when your application requires the semantic rigor to distinguish between 'similar' and 'relevant,' especially when dealing with complex entities like employee records..."

Option A is the tempting alternative because v3 can score higher in a full pipeline run — but the notebook explains that as the "wide net" effect (broad retrieval that includes noise), and explicitly warns against chasing absolute scores. C mislabels recall as precision; D cites throughput, which the passage never treats as a precision signal.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.3.2 Selecting the Appropriate Embedding Model," Phase 1 ("Analysis of Similarity Results" and the "Key Insight" callout) and the "Final Advice" paragraph.
</details>

## Question 5

After migrating a production RAG pipeline from `text-embedding-v3` to `text-embedding-v4`, Ragas shows context_precision improved substantially, but context_recall dropped because some relevant records no longer appear in the top 5 retrieved chunks. The top-ranked fragments are near-perfect hits with the noise filtered out. According to the notebook's engineering verdict, what is the most appropriate response?

A. Roll back to v3, because recall contributes more to final answer quality than precision does

B. Add a HyDE query transform to synthesize the missing contexts before retrieval

C. Reduce chunk size so that more fragments cover the facts that were missed

D. Increase `similarity_top_k` (for example, from 5 to 10), because v4's superior ranking can surface the missing data without bringing in the distractor fragments that v3 would retrieve

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Increase `similarity_top_k` (for example, from 5 to 10), because v4's superior ranking can surface the missing data without bringing in the distractor fragments that v3 would retrieve**

The notebook addresses this exact metric pattern under "Recall is Tunable": "v4 has superior ranking capability. If your recall is low, you can simply increase your `similarity_top_k` (e.g., from 5 to 10). v4 will likely find the missing data without bringing in the 'distractor' fragments that v3 would." The recommendation preserves v4's precision advantage ("Precision Prevents Hallucination") while recovering coverage.

Option A is the tempting alternative — v3 did score higher recall in the demonstration — but the notebook attributes that to v3's undisciplined "wide net," whose noise "can lead to LLM confusion, increased costs, or context-limit errors" at enterprise scale, and it does not recommend rolling back. B and C introduce heavier machinery (hypothetical-document generation, re-indexing) where the source prescribes a simple retrieval-width adjustment.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.3.2 Selecting the Appropriate Embedding Model," Phase 2 ("Analyzing the Evaluation Results" and "Engineering Verdict & Recommendation," lessons 1–2).
</details>

## Question 6

A startup prototyped its RAG bot with LlamaIndex's built-in in-memory vector index. It now moves to production: the corpus will grow well beyond prototype size, traffic varies, the team has no staff to operate databases, and it wants managed monitoring plus pay-as-you-go billing. According to the notebook's vector-storage recommendations, which option fits best?

A. Keep the in-memory vector index, because it integrates with LlamaIndex without additional configuration

B. Self-host an open-source vector database such as Milvus or Qdrant, because self-hosting provides automatic scaling without operations work

C. Use a cloud vector storage service such as DashVector, which provides automatic scaling, no operations burden, monitoring and management tools, pay-as-you-go cost control, and hybrid vector-plus-scalar retrieval

D. Self-host Qdrant, because cloud vector services do not support filtering retrieval results by scalar metadata fields

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Use a cloud vector storage service such as DashVector, which provides automatic scaling, no operations burden, monitoring and management tools, pay-as-you-go cost control, and hybrid vector-plus-scalar retrieval**

Section 4.3.3 gives a staged recommendation — in-memory for development and testing, local databases for small-scale applications, and "For production environments, it is recommended to use cloud services" — and lists the cloud advantages that match every constraint in the stem: "automatic scaling, there's no need to worry about operations and maintenance," "comprehensive monitoring and management tools," "pay-as-you-go, with better cost control," and "hybrid retrieval of vectors + scalars."

Option A is tempting only if the prototype habit carries over: the notebook explicitly lists in-memory disadvantages — "data cannot be persisted, and it is limited by memory size" — and assigns it to development and testing. B misstates self-hosting's trade-off (the notebook says local databases "require self-hosting and maintenance"), and D is contradicted by the listed cloud support for hybrid vector+scalar retrieval.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.3.3 Choosing the right vector database," subsections 4.3.3.1–4.3.3.3 (in-memory trade-offs; local database trade-offs; cloud options and the numbered Recommendations list).
</details>

## Question 7

A retrieval team wants to improve recall for queries whose wording diverges sharply from the indexed documents. It does not want to decompose questions into sub-questions or rewrite them into different phrasings; instead it wants the system to first assume what a plausible answer document would look like. Which notebook technique matches, and how does it work?

A. Multi-step querying: `StepDecomposeQueryTransform` breaks the question into sequential sub-questions that `MultiStepQueryEngine` answers one by one

B. Tag extraction: an LLM extracts structured JSON tags from the query, and tag filtering narrows the vector search

C. Re-ranking: a larger candidate set is retrieved and a rerank model reorders it before the top fragments are kept

D. HyDE: the LLM generates a hypothetical answer document from the question, that hypothetical document is used for vector retrieval, and the retrieved real documents then generate the actual answer

<details>
<summary>Show answer and rationale</summary>

**Answer: D — HyDE: the LLM generates a hypothetical answer document from the question, that hypothetical document is used for vector retrieval, and the retrieved real documents then generate the actual answer**

Section 4.4.1, Method 3 describes Hypothetical Document Embeddings exactly this way: "1. First, have the LLM generate a 'hypothetical answer document' based on the question. 2. Use this hypothetical document to retrieve real documents. 3. Finally, use the retrieved real documents to generate an actual answer," with the library-book analogy and the `HyDEQueryTransform` / `TransformQueryEngine` code example. The stem's constraint — assume a possible answer rather than adjust the question itself — is HyDE's defining characteristic ("The previous methods have all been about adjusting the question itself. Now, let's try a different approach: what if we first assume a possible answer?").

The alternatives are real techniques from the same section but excluded by the stem: A is question decomposition, B is query-side tag filtering, and C operates after retrieval rather than changing what is used as the retrieval query.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.4.1 Question rewriting," Method 3: "Enhance retrieval with HyDE" (three-step mechanism and the `HyDEQueryTransform` code example).
</details>

## Question 8

A support bot must answer ambiguous, multi-entity queries such as "Find Michael Johnson" when three employees share that name. The team considers `MultiStepQueryEngine` with `StepDecomposeQueryTransform`, but the bot has a tight per-request latency budget. According to the notebook's stated benefits and considerations, what trade-off should the team expect?

A. Fewer LLM calls because sub-questions are cached after the first decomposition, at the cost of requiring a reranker model

B. Improved accuracy and better handling of ambiguity, at the cost of increased token consumption — since each step may call the LLM — and longer processing time due to multiple sequential calls

C. Improved latency because each sub-question retrieves fewer chunks, at the cost of degraded accuracy on common-name queries

D. No measurable cost, because the decomposition happens inside a single retrieval call against the vector index

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Improved accuracy and better handling of ambiguity, at the cost of increased token consumption — since each step may call the LLM — and longer processing time due to multiple sequential calls**

The notebook's "Benefits of multi-step querying" lists improved accuracy, better handling of ambiguity ("Especially useful for queries involving common names"), and logical flow; its "Considerations" list exactly the two costs in the key: "Increased LLM Usage: Since each step may involve calling an LLM, this method consumes more tokens than a single-query approach" and "Longer Processing Time: Due to multiple sequential calls, the overall response time may be longer." For a latency-budgeted service, this is the trade-off to weigh — the notebook concludes it is "often worth it" for complex or ambiguous queries, which is a judgment the team must make against its budget.

Option C is the tempting inversion: multi-step querying improves accuracy on common-name queries but increases, not decreases, response time. A and D describe mechanics the notebook does not claim.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.4.1 Question rewriting," Method 2: "Rewriting a single query into multi-Step queries" (`StepDecomposeQueryTransform`, `MultiStepQueryEngine`, and the "Benefits"/"Considerations" lists).
</details>

## Question 9

With `similarity_top_k=3`, the bot misses one Michael Johnson record and answers incorrectly. The notebook demonstrates a fix that still passes only three reference fragments to the LLM, yet answers accurately. What is that fix?

A. Set `similarity_top_k=20` permanently and pass all 20 retrieved chunks to the LLM so nothing relevant can be missed

B. Rebuild the index with token chunking so that each employee record occupies its own precisely sized chunk

C. Switch the generation model from qwen-plus to a larger model that can infer the missing record from the retrieved ones

D. Retrieve a larger candidate set (for example, `similarity_top_k=20`), then apply a rerank postprocessor to keep the top 3 most relevant nodes, followed by a similarity-cutoff filter

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Retrieve a larger candidate set (for example, `similarity_top_k=20`), then apply a rerank postprocessor to keep the top 3 most relevant nodes, followed by a similarity-cutoff filter**

Section 4.4.3 walks through precisely this change: "first retrieve 20 document chunks from the vector database, then use the text rerank provided by Alibaba Cloud Model Studio to re-rank them, and filter out the three most relevant reference pieces of information. After running the code, you will notice that, with the same three reference pieces of information, the LLM is now able to answer the question accurately." The code example configures `similarity_top_k=20` with `node_postprocessors=[OpenAILikeRerankPostprocessor(rerank_client=..., top_n=3), SimilarityPostprocessor(similarity_cutoff=0.2)]`.

Option A is the tempting alternative — it also retrieves 20 candidates — but it skips the reranking step that is the point of the demonstration and floods the generation prompt with low-relevance chunks, the noise problem the retrieval-phase table warns about ("the retrieved chunks may contain items with low relevance"). B and C change other pipeline stages without addressing the ranking failure.

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.4.3 Re-ranking" (narrative and the `similarity_top_k=20` + `OpenAILikeRerankPostprocessor(top_n=3)` + `SimilarityPostprocessor(similarity_cutoff=0.2)` code example), with the "After Retrieval: reranking + Filtering" row of the section 4.4 table.
</details>

## Question 10

A RAG bot's knowledge base is complete and retrieval usually works, but for a few edge questions nothing relevant is retrieved — and in those cases the bot fabricates a plausible answer instead of admitting it cannot respond. According to the notebook's answer-generation guidance, which is the most direct prompt-level fix?

A. Increase the temperature so the model explores safer, more hedged responses when context is missing

B. Lower `max_tokens` so that any fabricated answer is truncated before it can mislead users

C. Add an explicit prompt requirement that when the provided information is insufficient, the bot must state "Based on the available information, I cannot answer this question" and must not fabricate answers

D. Replace the generation model with a larger-parameter LLM, which hallucinates less often on edge questions

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Add an explicit prompt requirement that when the provided information is insufficient, the bot must state "Based on the available information, I cannot answer this question" and must not fabricate answers**

Section 4.5 lists hallucination on empty retrieval as the first answer-generation issue and gives this remedy verbatim under "Fully optimize the prompt template — Clearly request no fabrication of answers": "You can reduce the likelihood of LLM hallucinations by requiring in the prompt: 'If the provided information is insufficient to answer the question, please explicitly state "Based on the available information, I cannot answer this question." Do not fabricate answers.'" This is the most direct fix because it targets the observed failure mode at the generation stage.

Option D is the tempting alternative — the section does recommend model upgrades for capability gaps — but the stem says retrieval, not model capacity, is the trigger, and the notebook's prescribed anti-fabrication control is the prompt requirement. A misuses temperature (the notebook ties lower temperature to factual queries, and higher temperature to creativity, not safety), and B truncates output without preventing fabrication; the notebook warns that too-low `max_tokens` "may lead to truncated output."

**Source:** `2_5_Optimize_RAG_Application_to_Improve_QA_Accuracy.ipynb` — "4.5 Answer generation phase" (issue list item 1 and the "Clearly request no fabrication of answers" bullet, including the quoted fallback sentence; parameter guidance for temperature and `max_tokens`).
</details>
