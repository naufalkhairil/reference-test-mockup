# Professional Exam: Teaching the Agent to Plan and Execute

Source: `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` (Alibaba Cloud ACP LLM course, Lesson 3.2). This is a source-grounded draft practice exam, not an official or validated certification assessment.

Choose the single best answer for each question.

## Question 1

A team uses an LLM bot to polish Jupyter Notebook course material. To stop the bot from touching code, an engineer adds to the system prompt: "**Important: absolutely do not modify any content inside code blocks, including variable names, parameter names, and function calls.**" Despite this, in some runs the bot renames a parameter `usr_id` to `user_id` in the function definition but not at the call sites, breaking the example. According to the lesson, why is this instruction-only safeguard unreliable?

A. The restriction is applied only to the first model call of a session, so later calls in the same conversation proceed without it.

B. The LLM hallucinates and lacks an inherent verification-and-correction mechanism, so each generation can probabilistically introduce new "helpful" errors, and listing prohibitions can never cover every scenario.

C. Instruction-tuned models cannot parse negative commands such as "do not modify," so the rule must be rephrased as a positive instruction to take effect.

D. When the polishing objective conflicts with code preservation, the model systematically resolves the conflict in favor of language quality in every run.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — The LLM hallucinates and lacks an inherent verification-and-correction mechanism, so each generation can probabilistically introduce new "helpful" errors, and listing prohibitions can never cover every scenario.**

The lesson states that adding warnings to the system prompt "doesn't work well, because you can't cover every possible scenario by listing prohibitions. Even if you explicitly forbid certain modifications, the LLM still has some probability of 'helpfully' changing originally-correct content into something wrong," and attributes this to hallucination plus the absence of an inherent verification mechanism. Option D is the most tempting alternative, but the source describes a probabilistic failure ("some probability"), not a systematic trade-off that happens in every run; A and C invent mechanisms the source never claims.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 1.2 "The LLM's hallucination" (passage on why the "absolutely do not modify" system-prompt warning fails, and the `usr_id` → `user_id` example in Sections 1.1–1.2).
</details>

## Question 2

You maintain a polishing workflow for an interactive course notebook containing dozens of code examples. A writer agent and a reviewer agent already compare the original and polished texts and flag unintended code edits. Management now wants a guarantee that every code example still actually runs after polishing. According to the lesson, which addition is most effective?

A. Add multiple specialized self-review agents — fact, logic, style, and security review — to increase the comprehensiveness of the textual comparison.

B. Strengthen the writer's prompt with a more explicit list of code identifiers that must never be renamed.

C. Let the reviewer agent rewrite suspect code itself, so fixes do not wait for a second writer pass.

D. Add an external feedback loop: extract the code blocks, run them with a code-execution tool such as AgentScope's `execute_python_code`, and feed execution results or error messages back to the agent for correction.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Add an external feedback loop: extract the code blocks, run them with a code-execution tool such as AgentScope's `execute_python_code`, and feed execution results or error messages back to the agent for correction.**

The lesson is explicit that self-feedback "is better suited to static, text-level comparison... but when you need to verify whether code actually runs, this mode performs poorly," because the LLM cannot execute code, see run logs, catch exceptions, or perceive dependency and environment issues. External feedback — putting the generated result into a real environment and feeding grounded facts back — is the prescribed remedy, demonstrated with `execute_python_code` registered via `toolkit.register_tool_function`. Option A is tempting because the source does endorse multiple specialized reviewers, but that stays inside self-feedback, which cannot establish that code runs; B repeats the instruction-only approach shown to be unreliable; C violates the reviewer's "find problems, don't rewrite" boundary and still never executes anything.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Sections 1.3.1.3 "The flaw of self-feedback" and 1.3.2.1 "Using tools to verify results," plus the AgentScope reflection example (`create_writer_agent` registering `execute_python_code`).
</details>

## Question 3

While implementing a two-step "generate-feedback" review, your reviewer agent has just identified several problems in the writer's polished draft. According to the lesson's guidance, how should the workflow handle them?

A. The reviewer should only report the identified problems; the review result is fed back to the writing agent, which revises the draft — forming a generate-feedback loop.

B. The reviewer should rewrite the flagged passages directly, closing the loop in a single call and improving fidelity faster.

C. The reviewer should issue only an overall Pass/Fail verdict without details, so the writer does not overfit to reviewer comments.

D. The reviewer should produce a full competing draft, and the system should publish whichever version scores higher on a style metric.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — The reviewer should only report the identified problems; the review result is fed back to the writing agent, which revises the draft — forming a generate-feedback loop.**

The lesson states: "let the review Agent be responsible only for 'finding problems,' not 'rewriting directly.' If you let it modify the content directly, it may damage the original's intended expression or introduce new errors," and recommends feeding `review_result` back to the writing agent to continue revising. Option B is the most tempting wrong answer because it looks faster, but it is exactly the practice the source warns against; C fails because the source's reviewer prompt requires a "Fail" answer to "point out exactly which content was accidentally modified," not a bare verdict; D describes a multi-model aggregation idea (MoA), not the reviewer's role in this loop.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 1.3.1.2 "Method two: two-step 'generate-feedback'" (the Writing Agent / Technical Review Agent prompt example and the paragraph immediately following it on the reviewer's responsibility boundary).
</details>

## Question 4

In your generate-feedback loop, the full original course document (dozens of code examples) is passed repeatedly — to the writer, then the reviewer, then the correction step — and token costs are climbing. According to the lesson's cost further-reading, how should you structure the prompts to cut this cost without removing the original document from any call?

A. Send the reviewer a condensed summary of the original document instead of the full text, reserving the full text for the writer.

B. Switch the reviewer agent to a cheaper, lightweight model so each repeated transfer costs less.

C. Place the identical original document at the start of every prompt as a stable prefix and put the per-call variable instructions after it, so Model Studio's Context Cache reuses the shared prefix and bills cache-hit tokens at 20% of the standard unit price.

D. Merge writing and review into a single-step reflection prompt so the document is transferred only once per revision cycle.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Place the identical original document at the start of every prompt as a stable prefix and put the per-call variable instructions after it, so Model Studio's Context Cache reuses the shared prefix and bills cache-hit tokens at 20% of the standard unit price.**

The further-reading box explains that the repeated transfer of the original document is the cost driver and prescribes exactly this structure: a "[Cached part — identical across all calls]" holding the original document, followed by a "[Variable part]" with the task-specific instruction; the first call pays the standard price and subsequent calls with the same prefix get the cache discount (20% of standard unit price). A violates the stem's constraint and would undermine the reviewer's job of comparing original vs. polished content precisely; B lowers unit price but does not address repeated transfer, and the source's differentiated-allocation guidance reserves capable models for critical judgment tasks; D reintroduces the single-step "self-justifying" bias described in Section 1.3.1.1.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 1.3.1.2, "Further reading: cost and optimization" box ("How to further reduce cost?" passage on Context Cache and the cached-prefix prompt structure).
</details>

## Question 5

A single agent is asked in one long prompt to verify all code, check technical facts, evaluate the difficulty gradient, and polish the style of a course. During the verification phase it correctly confirms that `super()` is valid Python; by the time it reaches polishing, it replaces `super()` with `parent()` because the word "super" looks colloquial, breaking the code. According to the lesson's failure analysis, which mechanism most directly explains this specific regression?

A. Cascading amplification of errors: an early fact-checking mistake became the "factual basis" for all later steps.

B. The attention mechanism's forgetting effect: as the generated sequence grows, attention to earlier verified details is diluted by intervening information, so the model "forgets" earlier constraints when revising later.

C. Missing external verification: without a code interpreter the agent had no way to discover that `parent()` is invalid Python.

D. Flattened understanding: the four requirements arrived as a flat token sequence, so the agent could not recognize that code checking and style checking are independent tasks.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — The attention mechanism's forgetting effect: as the generated sequence grows, attention to earlier verified details is diluted by intervening information, so the model "forgets" earlier constraints when revising later.**

Section 2.2.1 uses this exact `super()` → `parent()` example and attributes it to the forgetting effect of attention: "the model 'forgets' the constraints it verified earlier when revising later... the attention weights between tokens get diluted as the sequence length increases" — an inherent limitation of Transformer self-attention, not simple poor memory. Option A is the most tempting alternative, but cascading amplification (Section 2.2.2) describes an early error becoming the basis for later ones (the DataFrame-"built-in" example that led to deleting the pandas import); here the earlier verification was correct and the failure is dilution, not error propagation. C is an operational gap, not the source's explanation — the scenario says the agent had already verified the syntax; D describes Section 2.2.3, which explains poor decomposition of graph-structured requirements, not mid-task forgetting.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 2.2.1 "The forgetting effect of the attention mechanism" (the `super()`/`parent()` example), contrasted with Sections 2.2.2–2.2.3.
</details>

## Question 6

An "Intro to Python Data Analysis" course must pass four review dimensions — code execution, technical accuracy, difficulty gradient, and style compliance — before a same-day deadline. The four checks do not depend on each other's outputs. According to the lesson's workflow patterns, which design is the best fit?

A. Parallel execution: fan the four checks out to four specialized agents running simultaneously, then use an aggregation agent to merge the reports; total elapsed time is determined by the longest-running subtask.

B. Pipeline: chain the four checks in a fixed order, each consuming the previous check's report, to keep one auditable trail.

C. Branching: a routing agent selects which single check matters most for this course and runs only that expert branch.

D. Mixture-of-Agents: send the whole four-dimension review to several different LLMs and aggregate their answers for maximum quality.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Parallel execution: fan the four checks out to four specialized agents running simultaneously, then use an aggregation agent to merge the reports; total elapsed time is determined by the longest-running subtask.**

Section 2.3.3's own worked example is this exact scenario: Code Checker, Fact Checker, Pedagogy Evaluator, and Style Editor run via `fanout_pipeline`, then an "Editor-in-Chief" summarizer aggregates — valid because the subtasks are mutually independent, with the key advantage that total time equals the longest subtask rather than the sum. B serializes independent work against a deadline; pipelines are for fixed single-purpose sequences. C handles only "choose one of many" and, as the source notes, cannot serve a composite request of checking code while also doing the other dimensions. D applies multiple models to the same task to maximize quality at N-times cost; here there are four distinct tasks and the binding constraint is the deadline, so plain parallel execution is the suitable pattern.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 2.3.3 "Pattern three: Parallel Execution" (the four-expert course-review `fanout_pipeline` example and its efficiency premise), with pattern limits from Sections 2.3.2 and 2.3.4.
</details>

## Question 7

You are designing a largely automated course-production workflow. Following the lesson's guidance on Human-in-the-Loop (HITL) design, where should the human pause nodes go?

A. At every workflow node, because human oversight is the last line of defense against AI misoperation.

B. Wherever the model reports low confidence in a factual claim, so review happens only when the system feels uncertain.

C. After final delivery, as a periodic audit of published courses, keeping the workflow itself fully automated.

D. Only at absolutely necessary points — such as approval before publishing a course or deleting old versions — because human nodes significantly reduce the workflow's automation and execution speed.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Only at absolutely necessary points — such as approval before publishing a course or deleting old versions — because human nodes significantly reduce the workflow's automation and execution speed.**

Section 2.3.5 lists high-value operation approval (publishing course content, deleting old versions) as a canonical HITL scenario, and warns that introducing a human "significantly reduces the workflow's degree of automation and execution speed," so HITL nodes "need to be designed carefully, intervening only at absolutely necessary points and avoiding excessive manual intervention." A is the over-intervention the source explicitly cautions against; B relies on model-reported confidence, which the lesson's hallucination discussion (Section 1.2) undermines — the model can be confidently wrong — and it is not among the stated HITL criteria; C moves oversight after the irreversible action, losing the "last line of defense" function that motivates HITL approval nodes.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 2.3.5 "Pattern five: Human-in-the-Loop (HITL)" (advantages, "high-value operation approval" scenario, and the automation/speed caveat).
</details>

## Question 8

According to the lesson, for which kind of task is Mixture-of-Agents (MoA) the recommended pattern, and what is its main constraint?

A. Open-ended, high-value creative tasks with no unique standard answer — such as course slogans, promotional copy, or synthesized decision analyses; the main constraint is that N expert agents bring N-times compute cost and corresponding latency.

B. High-volume routine tasks such as format-checking many course units; the main constraint is that the subtasks must be mutually independent.

C. Tasks with a single verifiable answer, such as numeric computation exercises; the main constraint is that the aggregator must not simply pick one proposer's answer.

D. Fixed, fully specified processes such as document translation pipelines; the main constraint is that all proposer models must come from different vendors.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Open-ended, high-value creative tasks with no unique standard answer — such as course slogans, promotional copy, or synthesized decision analyses; the main constraint is that N expert agents bring N-times compute cost and corresponding latency.**

Section 2.3.4 states that MoA pursues "ultimate quality, robustness, and creativity" via model "Collaborativeness," is "suited to open-ended or creative tasks that have no unique standard answer, demand extremely high result quality, and carry huge value" (core copywriting, complex decision analysis, code generation/optimization), and that its main constraint is cost: "Calling N expert Agents brings N times the compute cost and corresponding latency... not suitable for routine, cost-sensitive daily tasks." B describes parallel execution's domain and is explicitly what MoA is not for; C's computation checking belongs to external feedback via a calculator/code interpreter (Section 1.3.2.2); D misstates the fit, and the source requires different LLMs for diversity, not different vendors.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 2.3.4 "Pattern four: Mixture-of-Agents (MoA)" (suitability list, "Advantages of MoA," and the cost-constraint paragraph).
</details>

## Question 9

An agent must execute a plan like: "analyze industry demand; then analyze the competitor course outline; if the competitor analysis fails because the site layout can't be parsed, search for a syllabus PDF instead and extract its text." Following Section 3.4, why is having the LLM generate code (Code as Action) preferable to emitting the plan as a simple JSON list of tool calls?

A. JSON plans cannot record the reasoning behind each step, so executors cannot audit the plan.

B. AgentScope's PlanNotebook can only execute plans expressed as Python code.

C. A simple JSON step list cannot express conditional logic like "if this fails, switch to that," whereas generated code can use conditionals, loops, variables, and third-party libraries to express complex plans.

D. JSON plans consume more input tokens than equivalent code for the same logic, raising the per-run cost.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — A simple JSON step list cannot express conditional logic like "if this fails, switch to that," whereas generated code can use conditionals, loops, variables, and third-party libraries to express complex plans.**

Section 3.4 presents the JSON plan format and then states its limit directly: "If the plan needs to include conditional logic like 'if competitor analysis fails, switch to Google search,' a simple JSON list can't handle it. To express more complex logic, you can have the LLM directly generate code (Code as Action)," leveraging a programming language's built-in capabilities (variables, conditionals, loops) and libraries. A is factually wrong — the shown JSON format includes a `thought` field per step; B is fabricated (the PlanNotebook example uses `create_plan` / `finish_subtask` / `finish_plan` tool calls, not Python-code-only execution); D is never claimed in the source.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 3.4 "Executing the plan the Agent generates" (the JSON plan example with `step`/`thought`/`tool_name`/`tool_params`, and the `execute_research_plan()` code-as-action example with the failure fallback).
</details>

## Question 10

You dispatched an autonomous planning agent to research an unfamiliar niche technology domain — a task whose process could not be predefined. After many exploratory runs, one path proved stable and had the highest success rate (crawl with tool A → clean with tool B → summarize with tool C), and the task must now run at scale in production every day. According to the lesson's production best practice, what should you do?

A. Keep the autonomous planning agent in production so it can re-plan adaptively whenever any step drifts.

B. Abstract and solidify the verified path into a fixed workflow for subsequent large-scale, repetitive production calls.

C. Patch the planner's prompt with a new exception branch for every failure mode observed during exploration.

D. Replace the planner with a human-in-the-loop workflow in which an operator selects the tool sequence for each run.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Abstract and solidify the verified path into a fixed workflow for subsequent large-scale, repetitive production calls.**

Section 3.6's "explore-then-solidify" hybrid mode prescribes exactly this two-phase practice: use the autonomous-planning agent in the exploration phase for new tasks with unclear processes, and once it "verified and summarized a stable, efficient solution path," abstract and solidify that path "into a reliable 'fixed workflow' for subsequent large-scale, repetitive production calls," building a continuously-optimizing positive loop. A is tempting because adaptability sounds safer, but the lesson's trade-off (Section 3.8 summary) assigns fixed workflows the job of guaranteeing stability and efficiency for core business once the path is known; C is the branch-patching anti-pattern criticized in Section 3.2 (you can never anticipate all accidents, and the workflow bloats); D adds human cost and latency to an already-verified deterministic path, contrary to the HITL "only absolutely necessary points" guidance.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — Section 3.6 "When to choose autonomous planning?" (the explore-then-solidify hybrid mode, phases 1–2), with supporting trade-off language in the Section 3.8 summary.
</details>
