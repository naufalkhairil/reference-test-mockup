# Professional Exam: Building a New-Employee FAQ Bot with an LLM — API Usage, How LLMs Work, and Context Engineering

Choose the single best answer for each question.

> Source: `2_1_Building_FAQ_Bot_with_LLM.ipynb` (Alibaba Cloud LLM ACP course, Section 2.1). All items are answerable from that notebook alone.

## Question 1

A developer on your team has written the Model Studio (Bailian) API Key directly into the FAQ bot's source code, which the team shares through a common repository. According to the section on configuring the API Key, what are the two main problems with this practice?

A. Hardcoded keys prevent the OpenAI-compatible SDK from switching the base URL.

B. Hardcoded keys force the model into stochastic sampling mode.

C. It is easy to leak the key when sharing code, and after rotating the key you would have to edit every hardcoded copy.

D. Hardcoded keys exhaust the free-tier call quota faster than environment variables.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — It is easy to leak the key when sharing code, and after rotating the key you would have to edit every hardcoded copy.**

The source states directly: "Writing the API Key directly into your code is a bad habit — it's easy to leak the key when sharing code, and after rotating the key you'd have to edit every hardcoded copy," and recommends storing the key in an environment variable instead. The stem describes exactly the code-sharing scenario the source warns about.

Options A, B, and D invent technical consequences (base-URL switching, decoding behavior, quota consumption) that the source never associates with hardcoding; the key's storage location does not change model behavior or billing.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "1.3 Configure the API Key" (first paragraph), plus the `load_key()` code cell that loads the key from a config file into the `DASHSCOPE_API_KEY` environment variable.
</details>

## Question 2

In the LLM text-generation workflow described in the lesson, what is produced by Stage 1 (tokenization) and why must Stage 2 (token vectorization) follow it?

A. Stage 1 produces semantic vectors; Stage 2 compresses them so the sequence fits the context window.

B. Stage 1 produces the probability distribution over the vocabulary; Stage 2 selects the next token from it.

C. Stage 1 produces the hidden state; Stage 2 maps it through a linear projection to logits.

D. Stage 1 produces token IDs whose numeric values carry no inherent meaning; Stage 2 looks each ID up in the Embedding matrix to obtain a vector rich in semantic information.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Stage 1 produces token IDs whose numeric values carry no inherent meaning; Stage 2 looks each ID up in the Embedding matrix to obtain a vector rich in semantic information.**

The source explains that tokenization converts input text into tokens, each "correspond[ing] to an integer ID in the vocabulary," but "the numeric values of these IDs have no inherent meaning (e.g. ID 500 doesn't mean it's semantically 'more important'... than ID 50)." Vectorization therefore converts the discrete IDs into semantic vectors via a lookup in the "huge table called the Embedding matrix" (with positional encoding added so the model can distinguish word order).

Option C is the most tempting alternative because it also uses vocabulary from the workflow, but it describes Stage 3 (LLM inference): the hidden state of the last token is mapped to logits there — not in Stages 1–2. Options A and B misassign the outputs of later stages to Stage 1.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "2.1 The LLM's text-generation workflow," Stage 1: Tokenization and Stage 2: Token vectorization.
</details>

## Question 3

Your FAQ bot answers "What tool should our company use for project management?" correctly. A user then asks "So how do I apply for an account for this tool?" in a separate API call, and the bot replies with a generic account-application process that never mentions the tool. According to the lesson's explanation of multi-turn conversation, what is the correct fix?

A. Keep the prior conversation history — both user questions and model answers — in the `messages` list passed with each call, alongside the system message.

B. Enable streaming output so the model can reference earlier turns while generating.

C. Lower the temperature so the model reliably "remembers" earlier content.

D. Send the system prompt twice, with the previous answer appended to the second copy.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Keep the prior conversation history — both user questions and model answers — in the `messages` list passed with each call, alongside the system message.**

The source explains that "the LLM generates its reply based on all messages in the messages list, so you need to keep the prior conversation history (both user questions and model answers) in this list," and the `multi_turn_chat()` example appends each user question and each assistant reply to `conversation_history` before the next call. If the follow-up call omits the earlier exchange, the model has no way to know what "this tool" refers to — exactly the failure in the stem.

Option B is tempting for developers who associate responsiveness with streaming, but the source is explicit that streaming "only changes how content is displayed; the model's reasoning and the final answer quality remain unchanged" — it cannot restore missing history. Option C confuses output randomness with memory: temperature controls sampling, not what the model can see. Option D is a partial, malformed imitation of A that still drops the multi-turn structure the source prescribes.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "1.5 Multi-turn conversation" ("How multi-turn conversation works") and the `multi_turn_chat()` code cell.
</details>

## Question 4

Users of the FAQ bot complain that after submitting a question they stare at a blank screen for about 20 seconds before the full reply appears. Your team wants to improve the interactive experience without degrading answer quality. According to the lesson, what should you do — and what property of that change makes it safe?

A. Add `stream=True` to the API call; streaming shortens the model's reasoning time and produces more concise answers.

B. Add `stream=True` to the API call; streaming only changes how content is displayed — the model's reasoning and the final answer quality remain unchanged.

C. Lower `top_p` so the model generates fewer tokens and therefore responds faster.

D. Split each user question into smaller sub-questions and answer them in sequence.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Add `stream=True` to the API call; streaming only changes how content is displayed — the model's reasoning and the final answer quality remain unchanged.**

The source describes exactly this symptom (the default API "waits until the model has generated all content before returning it all at once," about 20 seconds) and prescribes streaming: "the model outputs as it 'thinks,' like a human typing, so the user sees part of the reply immediately." Its tip confirms the safety property: "streaming output only changes how content is displayed; the model's reasoning and the final answer quality remain unchanged. You can safely use this feature."

Option A recommends the same parameter but with a false justification — streaming does not shorten reasoning or make answers more concise; conflating display behavior with generation behavior is the diagnostic error here. Options C and D change what the model generates rather than how delivery is displayed, and neither is supported by the source as a latency remedy.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "1.6 Streaming output" (narrative, 💡 Tip, and the `get_qwen_stream_response` code cell using `stream=True`).
</details>

## Question 5

You are configuring the FAQ bot for a task that needs clear, stable answers — the lesson cites news drafts and code generation as examples. Based on the source's summary of `top_p` effects, which configuration choice is best supported?

A. Use a larger `top_p` to broaden the candidate range.

B. Adjust `temperature` and `top_p` together in opposite directions to balance stability and diversity.

C. Set `top_p` to an extremely small value such as 0.0001 to guarantee byte-identical output on every call.

D. Use a smaller `top_p` to narrow the candidate range so the output is more stable.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Use a smaller `top_p` to narrow the candidate range so the output is more stable.**

The source's `top_p` summary states: "Smaller value: narrower candidate range, more stable output — suitable for scenarios needing clear answers like news drafts and code generation." The stem's task matches that description, so a smaller `top_p` is the directly supported choice.

Option C is the most tempting alternative because an extremely small `top_p` (e.g. 0.0001) does make the model "in theory... only pick[] the highest-probability token," but the source immediately warns that "identical output every time isn't guaranteed" due to factors like distributed systems and output post-processing — so the word "guarantee" makes C indefensible. Option A moves in the wrong direction (more diversity), and Option B violates the source's recommendation "not adjusting top_p and temperature at the same time," which "may make the output unpredictable."

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "2.2.2 top_p: controlling the sampling range of the candidate token set" (effect summary bullets) and "2.2.3 Summary" (do not adjust both parameters at once).
</details>

## Question 6

Your team needs maximally reproducible FAQ answers, so it sets `temperature=0`, `top_p=0.0001`, and passes the same `seed` on every call, keeping all other parameters unchanged. Occasionally the same question still yields slightly different text. According to the lesson, what is the best explanation?

A. The `seed` parameter takes effect only when `top_p` is set to 1.

B. Complex factors such as the LLM running on a distributed system and optimizations applied to the model output can still introduce subtle randomness, so identical results every time cannot be guaranteed.

C. Setting `temperature=0` disables the seed, since greedy decoding ignores all determinism controls.

D. Residual randomness appears only in multi-turn conversations, where history changes between calls.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Complex factors such as the LLM running on a distributed system and optimizations applied to the model output can still introduce subtle randomness, so identical results every time cannot be guaranteed.**

The source addresses precisely this configuration: "Even with temperature set to 0, top_p set to an extremely small value (e.g. 0.0001), and the same seed, the generation for the same question may still be inconsistent. This is because some complex factors can introduce subtle randomness — for example, the LLM runs on a distributed system, or optimizations are applied to the model output," illustrated by the bread-slicing-on-different-machines analogy.

Options A, C, and D each invent an interaction or precondition between the determinism controls that the source never states; the seed's documented behavior is only that the model "will try its best to return the same result" without a guarantee.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "2.2.3 Summary," passage "Why is there still randomness even after setting temperature, top_p, and seed?" (and the "Knowledge extension: seed" note).
</details>

## Question 7

Before adding any company knowledge, you ask the bot "What tool should our company use for project management?" It gives sensible suggestions centered on general tools like Jira, Trello, and Asana — none of which reflect your company's actual toolchain. According to Section 3 of the lesson, what is the root cause?

A. The LLM's knowledge comes from its training data — usually public internet information — which does not contain the company's internal documents, policies, or processes.

B. The company's question exceeds the model's context window, so the relevant part is dropped.

C. Streaming output truncates the beginning of the answer, hiding the company-specific recommendations.

D. The default temperature adds enough noise that the model overlooks information it actually possesses.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — The LLM's knowledge comes from its training data — usually public internet information — which does not contain the company's internal documents, policies, or processes.**

Section 3 states the root cause directly: "the LLM's knowledge comes from its training data, which is usually public internet information and does not contain any specific company's internal documents, policies, or processes," with the analogy of a supercomputer whose hard drive (model weights) is "blank" for your company's internal materials. The observation in Section 1.7 — generic Jira/Trello/Asana suggestions despite the answer existing in `docs/Content Development Engineer Job Guide.pdf` — is the motivating example.

Options B, C, and D attribute the failure to window limits, streaming, or sampling noise, but the question is short, streaming does not remove content, and no temperature setting can surface knowledge that was never in the model's weights.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "⚙️ 3. Enabling the LLM to Answer Private-Knowledge Questions" (opening paragraphs), with the motivating observation in "1.7 Observations and reflection."
</details>

## Question 8

A teammate proposes a quick fix for private-knowledge Q&A: paste the entire dozens-of-pages employee handbook and hundreds of pages of technical specs into the System Prompt of every request. Setting aside the hard context-window limit, what "hidden" problems does the lesson say this blunt cramming approach brings?

A. The model automatically converts the pasted documents into vectors, losing the original wording.

B. Long prompts force the model into near-deterministic decoding, reducing answer diversity.

C. Low efficiency (longer contexts take longer to process, increasing user waiting time), high cost (most models bill by input/output text amount), and information interference (irrelevant content interferes with the model's judgment and degrades answer quality).

D. The pasted text permanently modifies the model weights for other users of the same model.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Low efficiency (longer contexts take longer to process, increasing user waiting time), high cost (most models bill by input/output text amount), and information interference (irrelevant content interferes with the model's judgment and degrades answer quality).**

Section 3.3 lists exactly these three problems with "bluntly cramming information into the context": "1. Low efficiency... 2. High cost... 3. Information interference: if the context contains lots of information irrelevant to the current question, it's like giving an exam-taker a textbook for the wrong subject during an open-book exam." This motivates the lesson's conclusion that success depends on "how precisely you feed" the model, not how much — i.e., Context Engineering.

Options A, B, and D describe mechanisms the source never claims: prompt text is not converted to vectors in a lossy way, prompt length does not switch the decoding strategy, and nothing in a prompt modifies model weights.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "3.3 The solution: Context Engineering" (numbered list of hidden problems) and "3.2 The core bottleneck: the limited context window."
</details>

## Question 9

The lesson introduces Context Engineering as the systematic practice of designing, building, and optimizing what goes into the context window. Which set correctly names its four core techniques as presented in the concept diagram?

A. RAG (retrieval-augmented generation), Prompt (prompt engineering), Tool (tool use), and Memory (memory mechanisms).

B. Tokenization, Embedding, Decoding, and Autoregression.

C. Fine-tuning, Distillation, Quantization, and Pruning.

D. Indexing, Chunking, Reranking, and Generation.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — RAG (retrieval-augmented generation), Prompt (prompt engineering), Tool (tool use), and Memory (memory mechanisms).**

The "Core techniques of Context Engineering" box lists exactly these four: RAG to retrieve information from an external knowledge base; Prompt to guide the model with carefully designed instructions; Tool to let the model call external tools for real-time information or tasks; and Memory to give the model short- and long-term memory across a continuous conversation.

Option B is the most tempting alternative because its terms also appear in the lesson — but they are stages of the LLM's text-generation workflow (Section 2.1), not context-engineering techniques. Option D lists steps within RAG specifically, a subset of one technique rather than the four-technique map. Option C names model-training methods the lesson never presents.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "3.3 The solution: Context Engineering," "💡 Core techniques of Context Engineering" table box.
</details>

## Question 10

You are building the FAQ bot's RAG pipeline. One stage of your code splits company documents into fragments, converts the fragments into multi-dimensional vectors with a dedicated Embedding model, and writes them to a vector store. Which RAG phase does this stage belong to, and why?

A. Retrieval and generation, because vectors are what get compared with the user's question at answer time.

B. Context engineering, because it decides what enters the context window for each request.

C. Decoding and autoregression, because it prepares the probability distribution over the vocabulary.

D. Indexing, because it converts private-knowledge documents into a form that can be retrieved efficiently later.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Indexing, because it converts private-knowledge documents into a form that can be retrieved efficiently later.**

Section 3.4.1 defines Phase 1 (Indexing) as converting "private-knowledge documents or fragments into a form that can be retrieved efficiently. By splitting file content and converting it into multi-dimensional vectors (using a dedicated Embedding model), and combining with a vector store to preserve the text's semantic information, similarity computation becomes convenient." Every operation in the stem — splitting, embedding, storing — is listed there.

Option A is the most tempting alternative because the vectors are indeed used for comparison during retrieval; but retrieval and generation (Phase 2) is the runtime act of matching the question's vector and feeding retrieved fragments to the LLM — the offline preparation described in the stem is Phase 1. Option B names the umbrella methodology, not one of the two RAG build phases the source defines, and Option C borrows unrelated generation-workflow stages.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — "3.4.1 Phase 1: Indexing" and "3.4.2 Phase 2: Retrieval and generation."
</details>
