# Professional Exam: Using Memory to Let the Agent Accumulate Experience

Source: `3_4_Using_Memory_to_Accumulate_Experience.ipynb` (Alibaba Cloud ACP LLM course, Lesson 3.4). This is a source-grounded draft practice exam, not an official or validated certification assessment.

Choose the single best answer for each question.

## Question 1

A course-writing agent handled a conversation yesterday in which the user set a teaching style. Today, in a fresh session, the user says "based on the teaching style we discussed last time, make part two more vivid," and the agent asks what style was discussed — even though it is the same agent. According to the lesson, what is the root cause?

A. `InMemoryMemory` stores only the most recent N messages by default, so yesterday's style instruction has already been evicted.

B. The LLM is stateless: each Agent reply is essentially an independent API call, and once a call ends — or the session's context is cleared — the model retains nothing about past conversations, preferences, or requirements.

C. The agent's system prompt did not include an instruction to remember style preferences across conversations.

D. The model API discards conversation history between requests for privacy reasons, so no client-side design can recover it.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — The LLM is stateless: each Agent reply is essentially an independent API call, and once a call ends — or the session's context is cleared — the model retains nothing about past conversations, preferences, or requirements.**

The lesson's "Further reading: the LLM's core characteristic — Stateless" box explains that the LLM "won't remember who you are, what you talked about before, or any of your preferences," and that "each `reply` of the Agent is essentially an independent API call, so it naturally inherits this statelessness"; the preface adds that closing the window or clearing the context resets the agent to zero. A mischaracterizes `InMemoryMemory`, which the source presents as holding the full conversation list and resending it — its failure mode is across sessions and unbounded growth, not a default N-message cap; C misses the point that no prompt can substitute for resending or retrieving history; D is fabricated — the lesson shows client-side memory designs that do exactly this recovery.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 1 "Establishing Short-Term Memory" (the Stateless further-reading box and the `InMemoryMemory` two-conversation demo `run_stateless_test`), plus the Preface.
</details>

## Question 2

A team keeps resending the entire conversation history with every call. Token budgets cover the cost and the history still fits inside the model's context window, yet output quality degrades in long sessions. According to the lesson's analysis of the naive full-history approach, what explains this degradation?

A. Resent history triggers server-side rate limiting, which times out attention computation on long inputs.

B. The model compresses long histories lossily on its own, discarding whatever it judges least important.

C. Duplicate content across calls activates deduplication, dropping the earliest copy of each repeated message.

D. Attention dilution raises the probability that the model forgets context details as length grows, and "lost in the middle" means information in the middle of a long context is easily ignored while the beginning (primacy) and end (recency) are remembered.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Attention dilution raises the probability that the model forgets context details as length grows, and "lost in the middle" means information in the middle of a long context is easily ignored while the beginning (primacy) and end (recency) are remembered.**

Section 2 lists three problems with the naive approach — window limits, sharply rising cost, and performance degradation — and specifies the third exactly as in D: "Attention dilution: as the context length grows, the probability that the model forgets context details gradually increases," and "Lost in the middle: within a context of the same length, the LLM can often clearly remember information at the beginning (primacy effect) and the end (recency effect), but easily ignores key details located in the middle sections." The stem deliberately rules out the first two problems (budget and window), leaving performance degradation. A, B, and C invent server-side or model-side mechanisms the source never describes.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 2 "Information Refinement" (problem 3, "Performance degradation: Attention Dilution and 'Lost in the Middle'").
</details>

## Question 3

You are building a casual chit-chat companion bot. Old conversational details rarely matter later — information value decays quickly over time — and the team wants the simplest, lowest-overhead way to keep context length within a controllable range and avoid errors and unbounded cost growth. According to the lesson, which strategy fits best?

A. Fixed-window context truncation: keep only the most recent N rounds or N tokens and discard the oldest when the limit is exceeded.

B. Rolling summary: call the LLM to distill the earliest portion of the history into a short summary and replace the originals with it.

C. Vector-based long-term memory: embed every round into a vector database and retrieve the most relevant fragments per question.

D. Agent-controlled memory: give the agent `record_to_memory` and `retrieve_from_memory` tools and let it decide what to keep.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Fixed-window context truncation: keep only the most recent N rounds or N tokens and discard the oldest when the limit is exceeded.**

Section 3.1 states truncation's applicable scenarios are exactly "scenarios where information value decays quickly over time, such as a chit-chat bot or simple customer-service Q&A," with advantages "extremely simple to implement, low compute overhead, effectively guaranteeing the context length always stays within a controllable range, avoiding errors and unbounded cost growth" — matching every constraint in the stem. B is the most tempting alternative because it preserves more information, but it adds summarization API cost and complexity that the source reserves for tasks needing long-term goal consistency, not rapidly-decaying chit-chat; C carries "the highest system complexity" plus a new tech stack; D adds tool-decision inference on top of C's stack. Both are over-engineered against the stem's "simplest, lowest-overhead" criterion.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 3.1 "Strategy one: simple 'forgetting' — Context Truncation" (Idea, Relative advantage, Applicable scenarios bullets).
</details>

## Question 4

An engineer configures the truncating formatter with `max_tokens` set just below the model's maximum context window, reasoning: "nothing important is ever lost, and we never exceed the window." According to the lesson's discussion of truncation, what is the flaw in this configuration choice?

A. When the limit is exceeded, the formatter discards the newest messages instead of the oldest, so the agent loses the current question.

B. Setting `max_tokens` near the model limit disables the token counter, so truncation never actually triggers.

C. Truncating only when the window is nearly full means the agent works with a near-limit long context for extended periods, and attention dilution degrades its performance on complex tasks even without exceeding the window.

D. Near-limit contexts are billed at a higher token rate by the model API, so this configuration silently doubles cost.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Truncating only when the window is nearly full means the agent works with a near-limit long context for extended periods, and attention dilution degrades its performance on complex tasks even without exceeding the window.**

Section 3.1's "Performance risk" bullet describes precisely this: "even without exceeding the maximum window limit, only truncating when the window is nearly full means the Agent works with a near-limit long context for a long time. Because of attention dilution, this degrades the model's ability to handle complex tasks." The engineer's reasoning only guards against hard window errors, ignoring the quality dimension. A reverses the mechanism (the source says the oldest conversation is discarded — the demo shows "Rule A" being forgotten); B is fabricated — the code example notes a token counter must be provided for truncation to trigger, but nothing about near-limit values disabling it; D invents a pricing tier the source never mentions.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 3.1 "Strategy one" (the "Performance risk" bullet) and the truncation code example (`truncated_formatter = DashScopeChatFormatter(token_counter=..., max_tokens=40)` with the Rule A–Rule D demo).
</details>

## Question 5

A long-form course-creation project spans dozens of rounds; the team needs the agent to maintain consistency with the core goal and earlier decisions, and accepts extra LLM calls for compression. They choose the rolling-summary strategy. Which statement correctly pairs the strategy's mechanism with its boundary condition as given in the lesson?

A. Mechanism: keep only the most recent N rounds verbatim. Boundary: if the early core goal is truncated, conversation logic breaks.

B. Mechanism: when history is about to fill the window, call the LLM to distill the earliest portion (e.g., the first 50%) into a short summary that replaces the verbose originals, preserving core information for long-term coherence. Boundary: it introduces additional API-call cost for generating the summary, and summary quality directly affects the subsequent conversation.

C. Mechanism: embed each round into a vector database and retrieve by similarity. Boundary: there is no way to persist decisions across sessions.

D. Mechanism: automatically save and retrieve memory around each reply. Boundary: the agent cannot decide for itself when to record.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Mechanism: when history is about to fill the window, call the LLM to distill the earliest portion (e.g., the first 50%) into a short summary that replaces the verbose originals, preserving core information for long-term coherence. Boundary: it introduces additional API-call cost for generating the summary, and summary quality directly affects the subsequent conversation.**

Section 3.2 defines rolling summary exactly this way — "distill the earliest portion of the conversation (e.g. the first 50%) into a short summary... replace the verbose original conversation record with this condensed 'memory summary'" — with the advantage of maximally preserving core information for long-term coherence (its applicable scenarios include "long-form content creation"), and the boundary condition "additional API-call cost (for generating the summary), and the summary quality directly affects subsequent conversation." A pairs truncation's mechanism and boundary; C misdescribes vector retrieval and falsely denies cross-session persistence (that is its strength); D describes `static_control` mode of long-term memory, not summarization.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 3.2 "Strategy two: distilling the key points — Rolling Summary" (Idea, Relative advantage, Applicable scenarios, Boundary condition bullets) and the `SummaryMemory` conceptual implementation (`buffer_size`, `summary_ratio`).
</details>

## Question 6

According to the lesson's description of vector-based retrieval memory, what happens when the user asks a new question?

A. The full conversation history is resent with the question, and the model itself selects the relevant parts to attend to.

B. A standing summary of the entire conversation is prepended to the question, and the model answers from that summary.

C. All stored memory fragments are merged into the prompt in chronological order so nothing relevant is missed.

D. The question is converted into a vector and similarity-searched against the stored conversation vectors; the few most relevant memory fragments are then combined with the latest question into a concise context that is sent to the LLM.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — The question is converted into a vector and similarity-searched against the stored conversation vectors; the few most relevant memory fragments are then combined with the latest question into a concise context that is sent to the LLM.**

Section 3.3 lays out the three-step loop — Ingestion (embed each round and store it with the original text in a vector database), Retrieval ("when the user asks a new question, you first convert this question into a vector too, then do a similarity search in the database to find the few historical conversation records most relevant to the current question"), and Composition ("combine the retrieved 'relevant memories' and the user's 'latest question' into a concise, efficient context, then send it to the LLM"). A is the naive full-history approach Section 2 criticizes; B is rolling summary; C is exactly the "linear, undifferentiated" processing of all history that Section 3.3 says this strategy replaces with retrieve-on-demand.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 3.3 "Strategy three: building a knowledge base — Vector-based Retrieval" (the Ingestion / Retrieval / Composition numbered steps).
</details>

## Question 7

You want the memory system to save and retrieve memories automatically around every agent reply, with no per-call decision by the agent itself. In AgentScope's `Mem0LongTermMemory`, which mode provides this, and how does the alternative mode differ?

A. `agent_control` provides automatic save-and-retrieve around each reply; `static_control` instead exposes memory tools the agent must call explicitly.

B. `passive_mode` provides system-managed memory; `active_mode` provides tool-based memory that the agent schedules itself.

C. `static_control` automatically and passively saves and retrieves memory before and after each Agent reply; `agent_control` instead gives the Agent the tools `record_to_memory` and `retrieve_from_memory` so the Agent itself decides when to record and when to recall.

D. `summary_mode` compresses memory into a running summary after each reply; `retrieval_mode` searches the vector store before each reply, and the two must be enabled together.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — `static_control` automatically and passively saves and retrieves memory before and after each Agent reply; `agent_control` instead gives the Agent the tools `record_to_memory` and `retrieve_from_memory` so the Agent itself decides when to record and when to recall.**

Section 3.3 names the two working modes of `Mem0LongTermMemory` exactly this way: "`static_control`: automatically and passively save and retrieve memory before and after each Agent reply. `agent_control`: give the Agent tools to actively manage memory (`record_to_memory`, `retrieve_from_memory`), letting the Agent decide for itself when to record and when to recall" — echoed in Section 3.4, which notes that `agent_control` mode makes the `ReActAgent` gain those two tools automatically and needs system-prompt guidance to use them. A swaps the two mode names; B and D invent mode names not present in the source.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 3.3 (the two working modes of `Mem0LongTermMemory`) and Section 3.4 with its `ltm_agent_active` code example (`long_term_memory_mode="agent_control"`).
</details>

## Question 8

An `agent_control` agent has been running for weeks, recording everything it deems noteworthy. Now `retrieve_from_memory` increasingly returns cluttered, low-value fragments that distract its answers, and important memories are harder to surface. According to the lesson's memory-usage suggestions, what is the appropriate remedy?

A. Establish an admission mechanism for memory writes — record only when the user explicitly asks (e.g., "please remember...") or when the information's importance exceeds a threshold — because accumulating low-value or noisy information interferes with subsequent retrieval.

B. Switch the agent to `static_control` so that saving becomes deterministic and uniform across replies.

C. Increase the number of memory fragments retrieved per query so important ones statistically surface above the noise.

D. Disable long-term memory recording and enlarge the short-term truncation window so recent context dominates instead.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Establish an admission mechanism for memory writes — record only when the user explicitly asks (e.g., "please remember...") or when the information's importance exceeds a threshold — because accumulating low-value or noisy information interferes with subsequent retrieval.**

The "Remember selectively" suggestion states: "more memory isn't always better. Accumulating lots of low-value or noisy information interferes with subsequent retrieval. You should establish an admission mechanism for memory writes, e.g. writing only when the user explicitly asks... or when the information's importance exceeds a certain threshold. The `agent_control` mode is a good way to achieve this." The diagnosis in the stem is precisely the interference the source warns about, so the fix is at write time (the source's "Continuous governance" suggestion — cleaning outdated information and merging duplicates — complements it). B changes who decides, not how selectively things are written — static control would still save around every reply; C adds more noise per query rather than reducing it; D throws away the cross-session benefit that motivated the memory system.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 3.5 "Practical implementation and usage suggestions," part II "Memory-usage suggestions" ("Remember selectively" and "Continuous governance" bullets).
</details>

## Question 9

Following the lesson's "scenario-based application" guidance, which information is appropriate to record into the agent's long-term memory?

A. Personalized preferences encountered during a course-document workflow whose requirement is strict style consistency.

B. Verbatim transcripts of every session, so no potentially useful detail is ever lost.

C. The agent's own reasoning traces from each reply, retained for later auditability.

D. Product factual information such as API parameters and feature limits — recorded, then periodically reviewed for continued validity to ensure the accuracy of the agent's generated content.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Product factual information such as API parameters and feature limits — recorded, then periodically reviewed for continued validity to ensure the accuracy of the agent's generated content.**

The "Scenario-based application" bullet states: "for a product's factual information (such as API parameters, feature limits), you can record it and regularly review its validity to ensure the accuracy of the Agent's generated content," while explicitly warning that "in a course-document workflow that requires style consistency, personalized preferences shouldn't be recorded" — which rules out A. B contradicts the "Remember selectively" guidance (low-value bulk accumulation interferes with retrieval); C is never mentioned as a memory category in the source.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 3.5 "Practical implementation and usage suggestions," part II, "Scenario-based application" bullet.
</details>

## Question 10

In the lesson's hybrid short-term and long-term memory system, where do these two pieces of information belong: (i) the requirement just made in the current session — "Chapter 2's content needs one more case added" — and (ii) the course project's core goal — "designed for beginners, with a witty and humorous style"?

A. Both belong in short-term memory, because long-term memory should store only embeddings of objective facts, not user requirements.

B. (i) belongs in short-term memory — the conversation buffer managed by truncation or summary, whose job is maintaining the coherence of the current session; (ii) belongs in long-term memory — the vector database with tool-based calls, whose job is persistently storing key information for cross-session retrieval.

C. (ii) belongs in short-term memory, because it is referenced constantly within a session; (i) belongs in long-term memory, because chapter-level changes must survive session boundaries.

D. Both belong in long-term memory, because any requirement that should survive truncation must be persisted in the vector database.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — (i) belongs in short-term memory — the conversation buffer managed by truncation or summary, whose job is maintaining the coherence of the current session; (ii) belongs in long-term memory — the vector database with tool-based calls, whose job is persistently storing key information for cross-session retrieval.**

Section 3.5 divides the system exactly this way and uses these very examples: short-term memory ("based on a conversation buffer, managed through truncation or summary strategies... maintain the coherence of the current session. For example, remembering the specific requirement you just made about 'Chapter 2's content needs one more case added'") and long-term memory ("based on a vector database and tool-based calls... persistently store key information and support intelligent cross-session retrieval. For example, remembering that the entire course project's core goal is 'designed for beginners, with a witty and humorous style'"). C reverses the assignment; A and D collapse the two-tier design the source argues for, and A's "only embeddings of objective facts" restriction appears nowhere in the lesson.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — Section 3.5 "Building a short-term and long-term memory system" (the Short-term Memory and Long-term Memory bullets with their examples).
</details>
