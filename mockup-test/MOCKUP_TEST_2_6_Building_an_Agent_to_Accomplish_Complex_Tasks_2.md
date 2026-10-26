# Professional Exam: Building Agents for Complex Tasks

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` (Alibaba Cloud ACP LLM course materials)

Choose the single best answer for each question. All items are answerable from the referenced notebook; no outside knowledge is required.

> This is a source-grounded draft exam. It is not validated, standardized, psychometrically reliable, or equivalent to a real certification exam.

---

## Question 1

A team has shipped several single-prompt LLM features and is now building an agent whose work spans multiple interactions and draws on several external information sources. The technical lead asks which framing should guide the design effort. According to the notebook's closing methodology discussion, which statement best captures the shift it describes?

A. Prompt engineering still applies unchanged; an agent simply reuses one well-crafted instruction at every step of a multi-step task.

B. Model choice becomes decisive, because a stronger model can compensate for missing context at each decision point.

C. The designer becomes an "information architect" who arranges processes and tool calls so each decision node receives precisely the context it needs.

D. Evaluation becomes unnecessary, because a sufficiently complete context makes the agent's output correct by construction.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The designer becomes an "information architect" who arranges processes and tool calls so each decision node receives precisely the context it needs.**

The notebook contrasts **Prompt Engineering**, whose core is getting the best output in a *single* interaction, with **Context Engineering**, which applies when tasks span *multiple* interactions and *multiple external information sources*. In that setting the focus shifts "from 'writing a good Prompt' to systematically providing the most sufficient and precise context for every decision the model makes," and the designer "is no longer just a 'questioner,' but an 'information architect'" whose job is to build an "information cocoon" containing everything needed — "no more and no less."

A misreads the scope of prompt engineering: the notebook describes a shift in discipline, not reuse of one instruction at every step. B is unsupported — the notebook attributes the capability ceiling to context, not to model strength ("The quality of the context directly determines the upper limit of the Agent's capabilities"). D is contradicted by the very next section, which makes evaluation the quality-assurance mechanism for the context you build.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §8.2 "Core methodology: Context engineering" (the prompt-vs-context engineering passage, the "information architect" / "information cocoon" framing, and the sentence stating that context quality determines the upper limit of the Agent's capabilities).
</details>

---

## Question 2

You implement tool routing by asking the model to emit a JSON object containing `tool_name` and `parameters`, and you validate each response against a Pydantic model. Roughly one call in six fails validation. Following the "guide–validate–retry" closed loop described in the notebook, what should the retry step do?

A. Append the model's failed output together with the validation error message to the conversation, and ask it to regenerate in the required format.

B. Resend the original prompt unchanged at a higher temperature so the model can escape the malformed pattern it fell into.

C. Stop requiring JSON and instead parse the tool name and arguments out of the model's natural-language reply with a regular expression.

D. Route the request to a larger model, because validation failure shows the current model cannot follow a schema.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Append the model's failed output together with the validation error message to the conversation, and ask it to regenerate in the required format.**

Step 3 of the loop, "Validate and retry," states that after validating with the same schema, "the program should capture the validation error message and send it, along with the model's previous erroneous output, back to the model as a correction clue, requesting it to regenerate." The accompanying `get_structured_output` example implements exactly this: on `JSONDecodeError` or `ValidationError` it extends `messages` with the assistant's `raw_output` and a user turn reading `"Format error: {e}. Please strictly re-output in JSON format."`

B runs against the notebook's use of `temperature=0` for deterministic routing decisions, and temperature adjustment is not part of the described loop. C restores the condition the loop exists to eliminate — §1.3.1 lists free-form replies such as `Okay, the tool is search_arxiv_paper` as precisely what is hard to parse. D substitutes model capacity for error feedback, which the loop does not call for.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §1.3.2 "Building a 'guide-validate-retry' closed loop" (step 3, and the `get_structured_output(user_request, max_retries=2)` code example's `except (json.JSONDecodeError, ValidationError)` branch).
</details>

---

## Question 3

Your team operates six agent applications, each of which embeds its own definition of the internal document-search tool. The tool's API gains a required parameter, and all six applications must be edited and redeployed. According to the notebook's analysis of tool reuse, what is the root cause of this cost, and what does adopting MCP change?

A. The six agents use different models, and MCP standardizes the model API so a single tool definition works across all of them.

B. The tool executes too slowly under concurrent load, and MCP caches provider results so applications no longer need current definitions.

C. Function calling is being deprecated, and MCP replaces it as the only supported mechanism for invoking tools from an agent.

D. Tool definitions are hardcoded into each consuming application, and MCP moves that responsibility to the provider so applications receive current definitions by connecting.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Tool definitions are hardcoded into each consuming application, and MCP moves that responsibility to the provider so applications receive current definitions by connecting.**

§1.5.1 names the root cause explicitly: "**tool definitions are hardcoded into the code of each 'consumer' (Agent application)**," so "if a parameter in a tool's API changes, you need to modify every Agent that depends on it." §1.5.2 states that MCP's "core idea is to shift the responsibility for defining tools from the 'consumer' to the 'provider'": with MCP, "the tool service provider ... 'broadcasts' its capability definitions," and applications "only need to connect to the service provider via the MCP protocol to automatically obtain the latest tool definitions, without hardcoding." The stem is a direct instance of that scenario.

A misattributes the cost to model heterogeneity, which the section does not raise. B imports caching — a cost-optimization strategy discussed elsewhere in the notebook — as MCP's purpose. C is contradicted by the notebook's own analogy, which presents function calling as the *internal bus* for one application and MCP as the *external USB interface* for cross-application reuse; they are complementary layers, not a replacement.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §1.5.1 "Challenges of tool reuse" and §1.5.2 "Decoupling concept of MCP" (the hardcoded-consumer root cause, the consumer→provider shift, and the "Related thinking: USB protocol" callout distinguishing function calling from MCP).
</details>

---

## Question 4

Your agent polishes interactive Jupyter Notebook courses, each containing dozens of runnable Python examples. A two-call "generate–feedback" review currently compares the original and polished text and reports Pass or Fail, yet published notebooks still contain examples that raise errors when a student executes them. Based on the notebook's account of reflection modes, which change addresses this gap?

A. Add more specialized review agents — factual, logical, style, and security — to the existing generate–feedback loop.

B. Add an external feedback step that runs the extracted code with a code-execution tool and returns the execution result or error message to the agent for correction.

C. Strengthen the writing agent's system prompt with an explicit prohibition on changing variable, function, and parameter names.

D. Merge generation and review into a single call so that the agent reflects while it produces the polished notebook.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Add an external feedback step that runs the extracted code with a code-execution tool and returns the execution result or error message to the agent for correction.**

The notebook states that self-reflection "is more suitable for static text-level comparisons (e.g., checking if code has been accidentally modified), but its effectiveness is poor when you need to verify if the code can run normally," because "the model cannot actually execute code—it cannot see runtime logs, catch error reports, or perceive library version conflicts." External feedback closes that gap: "execute the LLM's generated results in a real environment, then feed the execution results (success/failure, error messages, test reports, etc.) back to the model." The section's own decision guidance matches the stem almost verbatim: "if you are modifying an interactive course with dozens of code examples, then introducing an 'external feedback' loop based on a code interpreter is a necessary investment." AgentScope's built-in `execute_python_code` tool is the named implementation.

A fails because additional reviewers are still self-reflection — more text-level judgment, still no execution. C fails because §2.2 reports that adding prohibitions to the system prompt "doesn't work well, because you can't list prohibitions to cover all possible scenarios." D fails because single-step reflection invites the "self-verification trap": the model "carr[ies] the same cognitive bias into its self-assessment," so a rename of `usr_id` to `user_id` is judged a "standardization improvement" rather than an error.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §2.3.1.3 "Drawbacks of self-reflection," §2.3.2 "Mode two: External feedback" (the `execute_python_code` registration example), and the closing paragraph of §2.3 comparing a blog post with an interactive course containing dozens of code examples.
</details>

---

## Question 5

A designer submits one course for review with four requirements — all code examples must run, technical concepts must be sound, the difficulty gradient must suit beginners, and the language must follow the style guide — and needs the results by 3 PM. The four checks do not depend on one another, and each has a well-defined correct outcome. Which workflow pattern fits best, and why?

A. Parallel execution, because the independent subtasks run concurrently and total time depends on the longest subtask rather than on the sum of all subtask times.

B. Branching, because a router can classify the request and dispatch it to whichever single review expert matches the designer's intent.

C. Mixture-of-Agents, because three different LLMs reviewing the same request and an aggregator merging their answers removes the need to split the work.

D. A single sequential pipeline, because a fixed execution order makes the process predictable and easy to debug.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Parallel execution, because the independent subtasks run concurrently and total time depends on the longest subtask rather than on the sum of all subtask times.**

The stem supplies the two conditions §3.3.3 sets for parallel execution: subtasks that are "mutually independent" (no dependencies such as confirming core knowledge points before evaluating case relevance) and units that can each provide a "correct" answer. The pattern's stated advantage is exactly the deadline concern: "The total time taken for the workflow is no longer the sum of all subtask times, but depends on the longest subtask." The section's worked `fanout_pipeline` example is this same four-dimension course review — code checker, fact checker, pedagogy evaluator, style editor — followed by a summarizer that consolidates the reports.

B fails because branching is "essentially 'one of many choices,' and it is still sequential": it "cannot handle composite requests like 'checking code while polishing language,'" so a four-dimension request would need "multiple independent conversations." C fails because MoA has multiple *different LLMs* process the *same* task, targeting quality, robustness, and creativity on "open-ended or creative tasks that have no single standard answer," at N times the cost — whereas the stem describes four *different* subtasks with determinate outcomes under a time constraint. D names real pipeline strengths (§3.3.1 does cite simplicity, predictability, and ease of debugging), but a pipeline serializes four independent checks, forfeiting the concurrency that the deadline requires; it is the second-best fit, not the best.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §3.3.3 "Pattern three: Parallel execution" (advantage, prerequisite of mutually independent subtasks, and the `fanout_pipeline` course-review example), contrasted with §3.3.2 "Pattern two: Branching" and §3.3.4 "Pattern four: Mixture-of-Agents (MoA)."
</details>

---

## Question 6

You must produce the outline and core cases for a new course — an open-ended design problem with no single correct answer. The instructional designer, data scientist, and content writer need to react to and build on each other's ideas as they emerge, and the team wants to avoid the delays and distortions that arise when information is relayed through one coordinator. Which collaboration pattern does the notebook recommend here, and what is its main risk?

A. Hierarchical (team leader) pattern; the main risk is that member agents cannot be given clear, well-defined responsibilities.

B. Hierarchical (team leader) pattern; the main risk is that the leader aggregates results before the members have finished their subtasks.

C. Co-creation (blackboard) pattern; the main risk is that experts end up exchanging information only through the project manager.

D. Co-creation (blackboard) pattern; the main risk is that discussion diverges without converging, and constant synchronization raises communication costs.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Co-creation (blackboard) pattern; the main risk is that discussion diverges without converging, and constant synchronization raises communication costs.**

§5.2.2 describes a decentralized "brainstorming session" around a shared space in which agents run a "read-think-write" loop, and states that this "decentralized collaboration can maximize collective intelligence," being "especially suitable for solving open-ended, creative problems that have no single correct answer and require brainstorming." Its stated risks match option D: such a session "can easily diverge and fail to converge or get stuck in a deadlock," and because "all members need to constantly synchronize and process massive amounts of information from others," it "places higher demands on controlling communication costs." AgentScope implements this with `MsgHub`, where any agent's reply is automatically "heard" by the other participants.

A and B fail because the hierarchical pattern's documented strengths are the opposite of A — "clear structure and well-defined responsibilities" — and B invents a premature-aggregation risk the section does not name. C misplaces the limitation: exchanging information only through the project manager, with resulting "information delays or distortions," is the drawback of the *hierarchical* pattern, which is precisely what the stem asks the team to avoid.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §5.2.2 "Pattern two: Co-creation/blackboard pattern" (the four-step shared-space loop, the "1+1>2" advantage, and the divergence/deadlock and communication-cost risks), contrasted with §5.2.1 "Pattern one: Hierarchical/team leader pattern" (information relayed through the manager causing delays or distortions).
</details>

---

## Question 7

A course-project assistant runs across many separate sessions over several weeks. In the first session the user set the project's core requirement — "designed for beginners, with a humorous and engaging style." Later sessions begin with empty short-term memory, and the assistant must recall only the requirements relevant to the current question rather than replay weeks of transcripts. Which memory strategy does the notebook indicate, and what trade-off does it attach to that strategy?

A. Fixed window truncation; the trade-off is that each compression adds an LLM call to produce the summary.

B. Rolling summary; the trade-off is that it requires an embedding model and a vector database.

C. Fixed window truncation; the trade-off is that it carries the highest system complexity of the three strategies.

D. Vector-based retrieval into a long-term memory store; the trade-off is the highest system complexity, introducing embedding models and vector databases.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Vector-based retrieval into a long-term memory store; the trade-off is the highest system complexity, introducing embedding models and vector databases.**

§6.3.3 describes ingestion (convert each turn into an embedding and store it with the original text in a vector database), retrieval (embed the new question and similarity-search for the most relevant historical records), and composition (combine retrieved memories with the latest question). Its advantages are that it "fundamentally breaks free from the length constraints of the context window" and can "precisely 'recall' the most relevant content from massive amounts of information based on current intent." Its stated boundary condition is verbatim the trade-off in option D: "The system complexity is highest. It introduces new technology stacks such as Embedding models and vector databases." §6.3.5 confirms the fit: long-term memory "persistently store[s] critical information and support[s] intelligent retrieval across sessions," illustrated by "remembering that the core goal of the entire course project is 'to design for beginners, with a humorous and engaging style'" — the same requirement as in the stem. AgentScope implements this through `Mem0LongTermMemory`.

A and C both mispair the strategy with a trade-off and with the scenario: truncation is described as "extremely simple to implement, low computational overhead," and its boundary condition warns that discarding the earliest turn would drop exactly the first-session core goal, causing the agent to "forget" again. B names the right-cost trade-off for the wrong strategy — the extra API call for summaries belongs to rolling summary, while the embedding/vector stack belongs to retrieval; rolling summary also processes history linearly to preserve within-conversation coherence rather than providing cross-session, on-demand recall.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §6.3.3 "Strategy three: Building a knowledge base – vector-based retrieval" (idea, advantages, boundary conditions, and `Mem0LongTermMemory`), with §6.3.1 "fixed window truncation," §6.3.2 "rolling summary," and §6.3.5 "Building short-term and long-term memory systems" (the beginners/humorous-style long-term memory example).
</details>

---

## Question 8

While a single agent reviews a course, it wrongly "corrects" the text to state that a DataFrame is a built-in Python data structure. It then reasons that pandas need not be imported, removes import statements from the teaching examples, and every code example becomes invalid. Which failure mechanism does the notebook identify for this progression?

A. The forgetting effect of attention mechanisms, because attention weights between tokens are diluted as the sequence length increases.

B. Cascading error amplification, because an early error becomes the "factual basis" for later reasoning and propagates non-linearly.

C. Flattened understanding versus structured requirements, because a task graph was presented to the model as a flat sequence of tokens.

D. Fixed window truncation, because the earliest validated constraints were discarded from the context to stay within a token budget.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Cascading error amplification, because an early error becomes the "factual basis" for later reasoning and propagates non-linearly.**

§3.2.2 uses this exact case: an incorrect DataFrame definition "enter[s] the subsequent context," and "the model would continue reasoning based on this erroneous 'fact'" — "Since DataFrame is 'built-in,' there's no need to import pandas. Import statements would be removed from teaching examples. All code examples would become invalid." The section concludes that "this error propagation is not linear, but exponential—a small error can trigger a cascade of incorrect decisions."

A is a real mechanism from the same section, but §3.2.1 uses it to explain the model *dropping* an earlier constraint — for example replacing `super()` with `parent()` during language polishing because the earlier validation was diluted — not building new decisions on an established false premise. C explains why the model cannot recognize which subtasks are parallel, dependent, or global (§3.2.3), which is a different failure. D imports a memory-management strategy from §6.3.1 that the review scenario never invokes.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §3.2.2 "Cascading error amplification" (the DataFrame / pandas-import example), distinguished from §3.2.1 "Forgetting effect of attention mechanisms" (the `super()` → `parent()` example) and §3.2.3 "Flattened understanding vs. structured requirements."
</details>

---

## Question 9

Your "course preliminary research" bot runs a fixed workflow that analyzes industry demand, defines user personas, and analyzes competitor courses. After a competitor website redesign, the `analyze_competitor_course` tool starts returning a parse error and the bot stalls. Engineers propose adding an exception branch for each failure they encounter. Based on the notebook's analysis, what is the better course of action?

A. Let the agent plan against the user's goal so it can generate alternative tasks when one fails, then crystallize validated paths into fixed workflows for repetitive production calls.

B. Add a branch for each failure mode as it appears, because a complete set of handlers eventually makes the workflow reliable.

C. Keep the fixed workflow and escalate every tool failure to a human, because autonomous planning cannot be trusted in production.

D. Replace the fixed workflow with autonomous planning everywhere, because higher autonomy removes the need for stable processes.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Let the agent plan against the user's goal so it can generate alternative tasks when one fails, then crystallize validated paths into fixed workflows for repetitive production calls.**

§4.2 rejects the patch-on-demand proposal: "it's impossible to anticipate every possible failure mode. Predefining a handler for each exception leads to workflows that are overly complex, bloated, and hard to maintain. Worse, any unforeseen issue will still cause the entire system to stall." It names the root cause — the agent "is merely a faithful executor of a rigid process—not a problem solver," and "doesn't 'understand' that the user's ultimate goal is to 'complete the course preliminary research.'" The Goal-vs-Task callout adds that a planning agent "recognizes that one route is blocked and autonomously devises new tasks to continue progressing toward the objective," which the `PlanNotebook` demo shows by switching from the failing `analyze_competitor_course` to `google_search` plus `extract_text_from_pdf`. §4.6 then supplies the second half of option A: the "explore-crystallize" hybrid, in which an exploration phase uses autonomous planning to find a stable path and a crystallization phase abstracts that validated path "into a reliable 'fixed workflow' for subsequent large-scale, repetitive production calls."

B is the approach the section argues against. C is not the notebook's conclusion — human-in-the-loop is presented in §3.3.5 as a deliberate trust and approval pattern, not as a substitute for adaptability when tools fail. D overreaches: §4.6 states that "higher autonomy modes are not a silver bullet, and lower autonomy modes also have wide application scenarios," and §4.8 credits fixed workflows with ensuring "the stability and efficiency of core business."

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §4.2 "Naive solution: Adding new branches" and its "Further reading: Goal vs. Task" callout, §4.3 "Enabling agents to plan autonomously" (the `PlanNotebook` demo with `create_plan` / `finish_subtask`), and §4.6 "When to choose autonomous planning?" (the explore-crystallize hybrid mode).
</details>

---

## Question 10

Your course-writing agent contains separate "concept explanation" and "code generation" components. End-to-end scores on generated lessons have fallen, but the reports do not reveal whether the explanations or the code examples are responsible, and each investigation requires running the whole pipeline. Which evaluation approach does the notebook recommend, and what does it buy you?

A. More end-to-end runs over a larger test set, because averaging across many lessons removes the ambiguity about which component failed.

B. Manual expert scoring of the final lessons, because human evaluation is the reliable gold standard for subjective quality.

C. White-box evaluation with a separate evaluation system for each key component, giving unambiguous improvement signals and shorter verification cycles.

D. An LLM-as-a-Judge rubric applied to the final lesson, because automated scoring is cheaper and scales better than component testing.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — White-box evaluation with a separate evaluation system for each key component, giving unambiguous improvement signals and shorter verification cycles.**

§7.3.2 opens with the stem's situation: "your 'course writing Agent' might include a 'concept explanation' component and a 'code generation' component. If the final course score is not high, it's hard to tell whether the concept explanation was poor or the code examples were terrible." White-box evaluation "is designed to solve this problem" by "going deep inside the system to design a separate evaluation system for key components." Two of its three listed advantages map directly onto the stem's pain points: **clear signals** ("unambiguous improvement signals, allowing you to focus on the true bottlenecks") and **rapid iteration** ("only needs to test individual components, without running the entire complex process, greatly shortening the verification cycle"). The section's examples build a term-based test set for concept explanation and a task-description test set for code generation.

A fails because scale does not create attribution — the inability to localize the faulty component is the named drawback of end-to-end evaluation itself. B is source-true about manual evaluation being "the most reliable 'gold standard,'" but that passage also notes it is costly, slow, and hard to scale, and scoring final lessons keeps the evaluation end-to-end. D improves the scalability of subjective scoring yet still judges the finished lesson, so it inherits the same attribution problem — and the notebook separately warns that LLM judges carry style, length, "people-pleaser," and position biases.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — §7.3.2 "Evaluation method two: White-box evaluation" (the concept-explanation / code-generation motivation, the three core advantages, and the two component-level test-set examples), with §7.3.1.3 "Improving the stability of subjective evaluation" for the manual-evaluation and LLM-judge contrasts.
</details>

---

## Answer key summary

| Question | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Answer | C | A | D | B | A | D | C | B | A | C |
