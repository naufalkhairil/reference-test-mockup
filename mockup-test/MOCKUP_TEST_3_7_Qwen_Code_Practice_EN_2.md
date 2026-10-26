# Professional Exam: Hands-On with Qwen Code — The Coding Agent's Daily Workflow

Choose the single best answer for each question. This is a source-grounded practice exam based on the course notebook `3_7_Qwen_Code_Practice_EN.ipynb` (Alibaba Cloud ACP LLM course, Lesson 3.7); it is not a validated or official certification instrument.

## Question 1

In Qwen Code, the project configuration written in the `QWEN.md` file stays in effect persistently, surviving session restarts. According to the concept-mapping table in Section 1, which earlier Agent concept does this behavior implement, and what is it really?

A. Session memory (3.4) — short-term memory stored in the context window.

B. Persistent memory (3.4) — writing key information to a file so it survives across sessions.

C. Plan & Execute (3.2) — generating a full plan first, then executing it step by step.

D. SubAgent (3.3) — the main Agent dispatching temporary sub-agents for independent subtasks.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Persistent memory (3.4) — writing key information to a file so it survives across sessions.**

Section 1's mapping table pairs "Project configuration in the QWEN.md file staying in effect persistently" with **Persistent memory (3.4)**, defined as "writing key information to a file so it survives across sessions." Section 4 reinforces this: QWEN.md "is Qwen Code's concrete implementation of persistent memory," a classic case of procedural, project-level knowledge. Option A is the most tempting distractor because both are memory: session memory is the short-term memory that lives in the context window and disappears on `/clear` or terminal close — precisely what QWEN.md exists to overcome.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 1 table ("The Qwen Code behavior you observe / corresponding Agent concept / what it really is"), QWEN.md row; see also Section 4.1.
</details>

## Question 2

During the Explore stage of the EPCC workflow, the recommended prompt ends with "Please only analyze — don't write any code yet." According to Section 2.2, why is this constraint key?

A. It keeps token consumption low so the analysis fits in the context window.

B. Plan Mode forbids writing code, so the sentence simply restates the mode's built-in restriction.

C. Without it, Qwen Code's ReAct loop will naturally move into the "Action" stage and start writing code once the analysis is done, which is not what the Explore stage wants.

D. It forces the Agent to produce a reproducible structured analysis report instead of free-form text.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Without it, Qwen Code's ReAct loop will naturally move into the "Action" stage and start writing code once the analysis is done, which is not what the Explore stage wants.**

Section 2.2 calls this sentence "the key constraint of the Explore stage" and explains the mechanism verbatim: "Without it, Qwen Code's ReAct loop will naturally move into the 'Action' stage and start writing code once the analysis is done." The Explore stage's single goal is understanding the current state before deciding how to change it. Option B is tempting but wrong on the facts: Explore as described happens before switching to Plan Mode, and Plan Mode's restriction is a property of the mode, not of this sentence; the constraint here is about steering the agent's ReAct behavior in an ordinary session.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 2.2, "Explore: Understand Before You Act" (paragraph on the "only analyze" constraint).
</details>

## Question 3

You need to add docstrings to roughly 40 files in a project. The edits are mechanical and low-risk, and you expect to run almost no shell commands. Following the notebook's "least privilege" principle for approval modes, which mode fits this task best?

A. auto-edit — it automatically approves file edits while commands still need confirmation, which the notebook lists as suited to bulk code-modification scenarios.

B. default — it asks for confirmation before every file modification and command, which is the recommended mode for all everyday development.

C. yolo — it approves everything automatically, maximizing throughput for a task this mechanical.

D. plan — it only analyzes and plans, guaranteeing no unintended modification during a bulk operation.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — auto-edit — it automatically approves file edits while commands still need confirmation, which the notebook lists as suited to bulk code-modification scenarios.**

Section 3.1's mode table describes auto-edit as "Read + write — automatically modifies files; only confirm command execution," suitable for "bulk edits (e.g. adding docstrings everywhere)" — the stem's task almost verbatim. Least privilege means giving "just enough autonomy to complete the current task, no more and no less": auto-edit removes the per-file confirmation burden while retaining the command gate. Option B is the everyday default but under-privileges this specific bulk task (40 individual confirmations); Option C over-privileges it — the notebook warns yolo's apparent efficiency can cost far more time in tracking down and rolling back mistakes; Option D cannot perform the edits at all.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Sections 2.3 and 3.1 approval-mode tables; Section 3.1 "least privilege" paragraph and yolo caution tip.
</details>

## Question 4

Midway through a multi-step feature task, `/context` shows usage above 70%, and you will soon need the exact parameter names of a function analyzed earlier in the session. According to Section 3.3, what should you do?

A. Run `/compress` and then ask the Agent to recall the parameter names — the rolling summary retains all facts discussed so far.

B. Write the key details you'll need later into QWEN.md (or another persistent location) before running `/compress`, because compression keeps a summary of key decisions and conclusions while fine details like specific parameter names are usually lost.

C. Run `/clear` instead, since clearing preserves a compact digest of the session while resetting token usage completely.

D. Continue without compressing until the task finishes, then compress — usage percentage alone never warrants action.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Write the key details you'll need later into QWEN.md (or another persistent location) before running `/compress`, because compression keeps a summary of key decisions and conclusions while fine details like specific parameter names are usually lost.**

Section 3.3's decision table says usage over 70% with an unfinished task calls for `/compress` — but its prediction exercise asks exactly the stem's question (recalling "the second parameter of `export_history`" after compression) and answers "most likely not": `/compress` generates a rolling summary of key information, and "fine-grained details… may be lost after compression. If you'll need to reference those details later, you need to record them manually before compressing — for example, by writing them into QWEN.md." Option A contradicts this information-loss warning; Option C is worse — `/clear` loses *all* conversation history and analysis; Option D ignores the recommended >70% action point and risks the "forgetting" the notebook describes as an inherent context-window limitation.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 3.3, "/compress and /clear: Managing Context" (prediction exercise; scenario table; "compression involves information loss" paragraph).
</details>

## Question 5

You are curating the project's QWEN.md. According to Section 4.2's include/don't-include guidance, which entry belongs in the file?

A. The API key value itself, so the Agent can configure LLM calls without asking.

B. The complete LlamaIndex API documentation, so the Agent never needs to search for it.

C. General Python programming common sense, such as what PEP 8 means, so the Agent follows conventions.

D. A recurring mistake and its fix — e.g., "LlamaIndex 0.12's import path has changed to `llama_index.core`; don't use the old path" — together with tech-stack version constraints.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — A recurring mistake and its fix — e.g., "LlamaIndex 0.12's import path has changed to `llama_index.core`; don't use the old path" — together with tech-stack version constraints.**

Section 4.2's table lists as "Include": tech stack and version constraints, module responsibilities, coding conventions, "specific mistakes the Agent has repeatedly made, and how to fix them," and environment configuration like API addresses. The example QWEN.md's "Common Pitfalls" section contains the `llama_index.core` import-path entry verbatim. The governing test is "the Agent will get it wrong if it doesn't know this, and it holds true across every session." The other three options are all explicitly in the "Don't include" column: the API key itself (a security risk), complete API documentation/tutorials (too granular — the Agent can read docs itself), and general Python common sense (the Agent already knows what PEP 8 is).

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 4.2, "What to Write, and What Not to Write" (example QWEN.md "Common Pitfalls"; include/don't-include table).
</details>

## Question 6

A developer's global `~/.qwen/QWEN.md` says "use 4-space indentation." The current project's root `QWEN.md` says "use 2-space indentation." According to Section 4.3, what will the Agent do when working in this project?

A. Follow 2-space indentation: the three levels are loaded and merged in the order global → project → directory, and the more specific configuration takes priority.

B. Follow the global 4-space rule, because the user-level configuration sits closest to the Agent's system defaults.

C. Prompt the user to choose, because conflicting configuration across levels cannot be resolved automatically.

D. Ignore both files, because a conflict makes the configuration invalid for the session.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Follow 2-space indentation: the three levels are loaded and merged in the order global → project → directory, and the more specific configuration takes priority.**

Section 4.3 uses this exact indentation example: "if the global config says 'use 4-space indentation' but the project config says 'use 2-space indentation,' the Agent will follow 2-space indentation in that project." The three-level hierarchy (global for personal cross-project preferences, project for tech stack and constraints, directory for module-specific rules) merges from general to specific with the more specific winning. Options C and D invent failure modes the source does not describe — conflicts are resolved by priority, not by prompting or invalidation.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 4.3, "Three Levels of Configuration" (hierarchy table and merge-priority paragraph).
</details>

## Question 7

While the Agent writes code against a fast-moving framework, you want it to consult the latest external documentation on its own initiative whenever it hits an unfamiliar API — no manual trigger, and no reliance on knowledge baked into prompts. According to Sections 5.1–5.2 and 6.5, which mechanism should you use?

A. A custom command in `.qwen/commands/`, since it packages the documentation-lookup process for reuse.

B. A Skill in `.qwen/skills/`, since Skills load expert knowledge on demand whenever the task matches.

C. An MCP connection (e.g., adding a web-search server via `qwen mcp add`), since MCP provides tools the Agent can call autonomously to reach external services.

D. A QWEN.md entry containing the relevant documentation excerpts, since project memory is loaded into every session automatically.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — An MCP connection (e.g., adding a web-search server via `qwen mcp add`), since MCP provides tools the Agent can call autonomously to reach external services.**

Section 5.2 sets up exactly this scenario — "you might want the Agent to consult the latest LlamaIndex documentation in real time while writing code. That requires letting the Agent call an external service — that's MCP" — and states the fundamental distinction: "MCP provides tools the Agent can call autonomously, while a custom command is a fixed process you trigger manually." Option A fails the "no manual trigger" requirement; Option B is the most tempting alternative because Skills also load on the Agent's own initiative, but per Section 6.5 a Skill packages *expert knowledge* the team already has, not a live connection to an external service; Option D bakes static excerpts into always-loaded memory, which goes stale and contradicts the "latest documentation" requirement.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 5.2, "Hands-On with MCP" (`qwen mcp add web-search` example; autonomous-vs-manual distinction); Section 6.5 mechanism-comparison table.
</details>

## Question 8

A team's `course-review` Skill has the description "Review lesson 3.5." It loads correctly when a user asks to review lesson 3.5, but fails to trigger when the user asks to review lesson 3.6. According to Section 6.2, what is the correct diagnosis and remedy?

A. The Skill body should be kept resident in context so it applies to every lesson regardless of the description.

B. The Skill should be moved from `.qwen/skills/` to `~/.qwen/skills/` so it is visible in every project.

C. The description should be made even more specific, enumerating every lesson number the Skill covers.

D. The description names a specific instance instead of a task type; it should describe the type of task (e.g., "review course material / check instructional-content quality"), since a too-narrow description fails to trigger on similar tasks and a too-vague one loads when unneeded.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — The description names a specific instance instead of a task type; it should describe the type of task, since a too-narrow description fails to trigger on similar tasks and a too-vague one loads when unneeded.**

Section 6.2 explains the trigger mechanism: at startup Qwen Code injects only each Skill's `name` and `description` into the system prompt, and the Agent matches the current task against that description before reading the body. Its first practical implication is verbatim: "write it too narrowly (like 'review lesson 3.5') and the Agent may fail to trigger it when reviewing lesson 3.6. A good description should describe the type of task, not a specific instance." Option C doubles down on the diagnosed error; Option A contradicts the design ("the body doesn't stay resident in context" — that is a feature, not the bug); Option B changes scope, not trigger matching.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 6.2, "Designing a Skill's Structure and Trigger Conditions" (trigger-mechanism paragraph and implication 1).
</details>

## Question 9

You are building an evaluation set for a code-review Skill following Section 6.4's guidance (10–20 cases across three categories). Which composition conforms to the notebook's recommendation?

A. 16 positive-trigger cases, so every evaluation run measures the Skill's core behavior under maximum statistical load.

B. 10 positive triggers, 4 edge cases, and 2 negative controls, batch-run via headless mode (e.g., `qwen -p ... --output-format stream-json`) and compared against expected results.

C. 8 negative controls, 6 edge cases, and 2 positive triggers, since catching false activation matters more than correct execution.

D. 16 edge cases, because borderline situations are where a Skill's rules are most likely to break.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — 10 positive triggers, 4 edge cases, and 2 negative controls, batch-run via headless mode (e.g., `qwen -p ... --output-format stream-json`) and compared against expected results.**

Section 6.4 prescribes 10–20 test cases covering three categories with explicit ranges: positive triggers 8–12 cases, edge cases 3–5, negative controls 2–3 — and shows the headless `qwen -p` command for automatic batch running with outputs collected and compared against expected results. Option B's 10/4/2 split falls inside all three ranges; A, C, and D each violate the composition guidance (no edge or negative coverage, inverted emphasis, or edge-only), and none of the distortions is supported by the source.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 6.4, "Using Evaluation to Drive Skill Optimization" (evaluation-set categories with case counts; headless-mode command).
</details>

## Question 10

On a five-person team, key architectural decisions are discussed in team chat and meeting notes but never written into the repository. The Agent repeatedly generates code that violates those decisions, and each member re-explains the rules in every session. According to Section 7.2 ("Repository Knowledge Is the Agent's Source of Truth"), what is the right structural fix?

A. Persist the knowledge in the repository: write it down where the Agent can see it, keeping QWEN.md lean as a table of contents (what the project is, where the rules live, which files must not be touched) with detailed rules in Skills, docs, or dedicated convention files the Agent reads on demand.

B. Fix each session individually: paste the relevant decisions into the prompt whenever the Agent is about to touch the affected modules.

C. Write every rule into QWEN.md in full detail, so the Agent always has complete knowledge of all decisions in its system context.

D. Export the chat logs into the working directory before each session so the Agent can search the original discussions.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Persist the knowledge in the repository: keep QWEN.md lean as a table of contents, with detailed rules in Skills, docs, or dedicated convention files the Agent reads on demand.**

Section 7.2's core claim: "if none of it is written into the repository, none of it exists as far as the Agent is concerned." It then anticipates the tempting overcorrection — "then just write every rule into QWEN.md" — and rejects it (option C) for four reasons: context gets crowded out, too many rules lose focus, a large file quickly goes stale, and it is hard to audit. The prescribed shape is QWEN.md "as a table of contents… Detailed rules belong in a Skill, in docs, or in a dedicated conventions file, which the Agent reads on demand," mirroring a Skill's progressive disclosure. Option B recreates the per-session re-explanation problem the whole lesson's memory mechanisms exist to solve; Option D dumps unstructured history into context rather than curating durable rules.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — Section 7.2, "Repository Knowledge Is the Agent's Source of Truth" (source-of-truth claim; four failure reasons; "table of contents, not encyclopedia" prescription); see also Section 7.3 mapping table.
</details>
