# Professional Exam: Using Skills to Solidify Capabilities into Reusable Processes

Choose the single best answer for each question. This is a source-grounded practice exam based on the course notebook `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` (Alibaba Cloud ACP LLM course, Lesson 3.5); it is not a validated or official certification instrument.

## Question 1

A team equips a fully functional ReActAgent with a `read_file` tool and asks it, in one sentence, to review a ~300-cell Jupyter Notebook tutorial and judge whether it can be published. The agent returns advice such as "add code comments" and "add exception handling," but misses defects that are specific to this tutorial — for example, the notebook ends with `pd.ExcelWriter(..., engine='openpyxl')` while the environment-setup section never installs `openpyxl`, and the text says missing `city`/`gender` values are filled with the mode while the code fills them with `"unknown"`. According to the notebook, what is the underlying reason for this result?

A. The agent's underlying model is not capable enough for professional review tasks, so a stronger model is required.

B. The notebook is too long for the context window, so the agent's reading was truncated before it reached the defective cells.

C. The agent reviewed against a generic review standard; the team's fine-grained professional standards (dependency completeness, text–code consistency, style rules) live only in the team's experience and were never provided.

D. The prompt did not specify an output format, so the agent defaulted to high-level summaries instead of itemized findings.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The agent reviewed against a generic review standard; the team's fine-grained professional standards live only in the team's experience and were never provided.**

The notebook states the problem "isn't that the Agent's capability is insufficient, but that it doesn't know what your standard is." With a generic prompt the agent applies a generalized understanding of course quality and produces "correct nonsense" — advice that would hold for any tutorial — while missing problems that hold true only for this one (the un-installed `openpyxl` dependency, the mode-vs-`"unknown"` text/code mismatch, wisecracks). Option A contradicts the source's explicit diagnosis. Option B is tempting because the notebook later discusses long-notebook truncation, but that is presented as a separate practical problem in Section 2.3, not as the cause of the generic advice here.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 1, "Reviewing a Tutorial with a Prompt" (the passage listing the three missed real problems and the four team-specific review standards).
</details>

## Question 2

An instructional designer maintains a detailed review prompt containing her team's four review standards, the `.ipynb` JSON parsing hints, and a required output format. Over several months she encounters these problems: she must dig the prompt out of chat history for each new review; she and a colleague maintain divergent versions, so their review results are not comparable; and she cannot remember which version added the rule "terms need explanation on first appearance." According to the notebook, what is the root cause of all these problems?

A. Prompts written in plain text cannot express checklists and output formats as precisely as a structured Markdown file can.

B. The prompt is session-level: it only takes effect in the current conversation, so it cannot be stored, version-managed, or shared by the team as an independent resource.

C. The prompt has grown long enough to crowd the model's context window, degrading the quality of every review that uses it.

D. A prompt-based agent cannot invoke file-reading tools, so the review standards can never be applied to the actual notebook content.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — The prompt is session-level: it only takes effect in the current conversation, so it cannot be stored, version-managed, or shared by the team as an independent resource.**

The notebook names this directly: "The root of these problems is: the Prompt is session-level… It's not an independent resource that can be stored, version-managed, and shared by a team," comparing it to writing operating procedures on a sticky note. The three symptoms in the stem (finding it, aligning wording, tracking changes) are exactly the four practical problems the source lists. Option A is a partial truth — file-ization does help — but the source attributes the failure to the session-scoped, unmanaged nature of the prompt, not to plain text being unable to express the content (the prompt in the source already contains the full checklist).

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 1, closing discussion ("the Prompt is session-level," sticky-note analogy) leading into Section 2, "Precipitating Review Experience."
</details>

## Question 3

An agent platform team is choosing mechanisms for two needs. Need 1: the agent must answer questions using current product parameters from a large, frequently updated product documentation corpus. Need 2: when asked to audit training material, the agent must follow the team's multi-step audit procedure, including its anti-pattern list and output template. According to the notebook's comparison of Skill and RAG, which assignment is correct?

A. Use RAG for both needs, since both amount to supplementing the agent with information it does not have.

B. Use a Skill for both needs, since both require the agent to select and expand the right knowledge on demand.

C. Use RAG for the audit procedure and a Skill for the product parameters, matching each mechanism to the larger corpus.

D. Use RAG for the product parameters and a Skill for the audit procedure, because RAG solves "the model doesn't know a fact" while a Skill solves "the model doesn't know how to do something."

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Use RAG for the product parameters and a Skill for the audit procedure, because RAG solves "the model doesn't know a fact" while a Skill solves "the model doesn't know how to do something."**

The notebook's tip draws exactly this distinction: RAG addresses missing facts (document content, product parameters) via "retrieve-inject" — slice, semantically retrieve, stuff the top fragments into context — while a Skill addresses missing procedures via "select-expand" — the agent sees all Skill descriptions, chooses one based on the task, then reads its details progressively. Option A is the most tempting wrong answer because both mechanisms do supplement the agent, but the source insists the problems they solve differ: a retrieved fact fragment cannot carry a workflow, anti-patterns, and an output template that must be executed step by step.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 3.1, tip box "The difference between Skill and RAG" (retrieve-inject vs. select-expand).
</details>

## Question 4

You are writing the YAML frontmatter `description` for a new Skill that reviews course content. The agent will carry dozens of Skills and must pick the right one from user instructions alone. According to the notebook's guidance in Section 3.2, which description is best?

A. "Review the technical accuracy, code correctness, and teaching quality of course content. Use this skill when the user asks to review, audit, or evaluate an existing course or training material."

B. "Handle course-related tasks."

C. "This skill bundles a review checklist, a deprecated-API table, an output template, and two helper scripts under `scripts/`."

D. "course-review: the team's official, version-managed quality gate for all instructional content."

<details>
<summary>Show answer and rationale</summary>

**Answer: A — "Review the technical accuracy, code correctness, and teaching quality of course content. Use this skill when the user asks to review, audit, or evaluate an existing course or training material."**

The notebook states a good description must answer two questions: what the Skill does (function) and when it should be triggered (trigger conditions). Option A does both, and is the source's own "clear description" example. Option B is the source's "vague description" counterexample — writing, reviewing, and translating a course all "handle course-related tasks," so the agent cannot judge whether to trigger. Option C describes internal structure, which is body material, not selection metadata; Option D describes organizational status without stating function or trigger conditions.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 3.2, "The structure of a Skill" (the ❌ vague / ✅ clear `description` examples).
</details>

## Question 5

Applying the notebook's Step 1 criteria ("judge whether it's worth doing"), for which task is encapsulating a Skill clearly justified?

A. A one-time migration of a legacy configuration file that will be discarded after the migration.

B. A weekly operation that a GUI completes in three steps and that requires no expert judgment.

C. Reviewing about 20 course notebooks every week, where senior instructional designers instantly spot problems (e.g., "this code example is too complex for a beginner") that novices routinely miss.

D. Translating a short paragraph of release notes into English when a translation is needed.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Reviewing about 20 course notebooks every week, where senior instructional designers instantly spot problems that novices routinely miss.**

Step 1 requires all three questions to be answered "yes": the task involves expert intuition/tacit knowledge, it is complex enough, and it will be executed repeatedly. Option C satisfies all three — the source uses exactly this case ("if your team has to review 20 courses every week, then spending a day polishing a CourseReviewSkill is very worthwhile"). Option A fails the repetition test (one-off tasks have a very low input-output ratio); Option B fails the complexity test — the source quotes the rule "operations that can be completed via GUI within 3 steps are strictly forbidden from being encapsulated as a Skill"; Option D is the source's example of a task simple enough to just describe in natural language.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 3.3, "Step 1: judge whether it's worth doing" (three questions and the 3-step-GUI prohibition).
</details>

## Question 6

You are writing two Skills: one that performs production database migrations, and one that performs exploratory code reviews. According to the notebook's "freedom matching" principle, how should the instruction precision differ?

A. Both Skills should use high freedom (text instructions), because over-constraining the model limits its capability in every task.

B. Both Skills should use low freedom (precise scripts), because any agent-executed operation carries production risk.

C. The migration Skill should use high freedom so the agent can adapt to schema variations; the review Skill should use low freedom so its findings stay consistent.

D. The migration Skill should use low freedom — a precise script the agent must not modify — while the review Skill should use high freedom, since multiple review paths all reach the destination.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — The migration Skill should use low freedom — a precise script the agent must not modify — while the review Skill should use high freedom, since multiple review paths all reach the destination.**

The freedom-matching principle says the degree of constraint must match the task's risk: low freedom (precise script) for fragile operations that must be strictly followed — the source's examples are database migration and deployment scripts, with the "narrow bridge + cliff" analogy and a literal `python scripts/migrate.py --verify --backup` "do not modify" instruction; high freedom (text instructions) where multiple methods work — the source's examples are code review and content analysis ("open field"). Option C inverts the mapping. Options A and B each apply one level uniformly, which the source says produces either accidents (too loose where strictness is needed) or a hobbled model (too rigid where flexibility is needed).

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 3.3, "Step 3: write good instructions," subsection "Freedom matching" (High/Medium/Low table, narrow-bridge vs. open-field analogy, low- and high-freedom examples).
</details>

## Question 7

A Skill is organized as `SKILL.md → config.md → rules/code_quality.md`: the entry file points to `config.md`, which in turn says the rule definitions live in the `rules/` directory. In testing, the agent reads `SKILL.md` and `config.md` but never applies the detailed code-quality rules. According to the notebook, what is the most likely cause and the recommended fix?

A. The rules file is too large for the context window; split it into smaller chunks and link each one separately.

B. The reference chain is too deep — the model may only preview an intermediate file (e.g., `head -100`) so key information is lost in the passing chain; keep a flat structure where SKILL.md directly links every resource.

C. The `description` in the frontmatter lacks trigger conditions, so the Skill is never fully activated; rewrite the description.

D. The rules are written in natural language instead of JSON; convert them to structured data so the model can parse them.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — The reference chain is too deep — the model may only preview an intermediate file (e.g., `head -100`) so key information is lost in the passing chain; keep a flat structure where SKILL.md directly links every resource.**

Step 3's progressive-disclosure guidance adds the practical rule "keep a flat structure, avoid deep nesting," with exactly this ❌ pattern (SKILL.md → config.md → rules/) and the explanation that with too many levels the model may preview an intermediate file rather than reading it fully, losing key information. The ✅ pattern has SKILL.md link each resource directly so any needed file is "one step" away. Option C is tempting but misdiagnoses: a description problem would prevent the Skill from being selected at all, whereas here the agent demonstrably activated it and read two levels. The source prescribes no JSON conversion (D) or chunk-splitting (A) for this failure.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 3.3, "Step 3: write good instructions," subsection "Progressive disclosure: keep the main file lean, load details on demand" (deep-nesting vs. flat-structure example).
</details>

## Question 8

You are designing the workflow section of a Skill that lets an agent batch-modify files across a repository. The notebook contrasts a "feedback loop" (run → check → fix → repeat) with a "validate the plan before executing" pattern. Which design does the notebook recommend for this high-risk operation, and why?

A. Generate a change plan as JSON, run a validation script over it (no deletions, target paths exist, changes reversible), and execute only after validation passes — errors are intercepted before execution rather than discovered after.

B. Apply the changes and then run the validator in a loop, fixing whatever it reports — this gives the agent a chance to self-correct with real error messages.

C. Have the agent list the risks of each change in free text and proceed if no risk is rated severe — this keeps the workflow lightweight.

D. Log every change to an audit file and let a human reverse unwanted changes after the run — reversibility makes pre-execution validation unnecessary.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Generate a change plan as JSON, run a validation script over it (no deletions, target paths exist, changes reversible), and execute only after validation passes — errors are intercepted before execution rather than discovered after.**

Step 4 explicitly reserves the "validate the plan before executing" pattern for high-risk operations, naming batch file modifications and database migrations, with the exact three-step flow (`plan_changes.py --output changes.json` → `validate_plan.py` checking no deletions / paths exist / changes reversible → `apply_changes.py`). The source states the core difference from the feedback loop: "errors are intercepted before execution, rather than discovered after." Option B describes the feedback loop correctly but applies it to the wrong case — it is the source's pattern for validation-style tasks, and for destructive batch edits the source insists on the pre-execution gate. C and D have no basis in the source.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 3.3, "Step 4: configure good tools," subsection "High-risk operations: validate the plan before executing" (batch-update workflow example).
</details>

## Question 9

A teammate plans to accelerate Skill development: "I'll have `skill-creator` generate a draft from my requirement right away, then we'll see how it does." According to the notebook's Step 5 ("validate and iterate"), what should the team do first, and why?

A. Have Agent A (the designer) refine the Skill's instruction structure and output template before any task is run, so the draft starts from a strong structure.

B. Have Agent A complete a real task with no Skill at all, record where it failed or needed repeated correction, and pick the 3 most typical failure scenarios as evaluation cases — evaluation must exist before the Skill is written, otherwise all later optimization relies on "feeling."

C. Have Agent B load the generated draft in a brand-new session and run it on live work, since real usage is the only meaningful test.

D. Collect every team member's preferences for the Skill's format into a checklist, so the draft satisfies the widest possible audience.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Have Agent A complete a real task with no Skill at all, record where it failed or needed repeated correction, and pick the 3 most typical failure scenarios as evaluation cases — evaluation must exist before the Skill is written, otherwise all later optimization relies on "feeling."**

Stage 1 of the dual-Agent development flow is "establish an evaluation baseline": run the task unaided, record mistakes and repeated corrections, and select the 3 most typical failure scenarios as evaluation cases — "Have the evaluation first, then write the Skill." Section 4.2 reinforces this for auto-generated drafts: skill-creator only solves "write it out"; whether it is "written correctly" still requires the evaluation-driven dual-Agent flow (Agent A designer, Agent B user testing in a fresh session against the Stage-1 cases). Option C skips the baseline, so there would be nothing objective to compare Agent B's results against; Option A inverts the prescribed order.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Section 3.3, "Step 5: validate and iterate" ("dual-Agent" pattern, Stages 1–3) and Section 4.2 tip on validating generated drafts.
</details>

## Question 10

An individual's `CourseReviewSkill` worked well for her, so she sent the SKILL.md file to her 10-person team's group chat. A month later: three colleagues are still running an old version, producing contradictory review conclusions; an intern unilaterally relaxed a rule, and the damage went unnoticed for three weeks. According to Sections 5.2–5.4 of the notebook, what is the recommended structural fix?

A. Move the Skill file to a shared drive so everyone always downloads the same copy, with edit permission open to the whole team.

B. Route every modification through the Skill's original author, who approves or rejects each change request personally.

C. Distribute a detailed usage-instruction document alongside the Skill so team members stop making configuration mistakes.

D. Manage the Skill as code: assign domain-team ownership (e.g., instructional-design team) recorded in frontmatter metadata and/or CODEOWNERS, and require changes to pass PR review plus CI evaluation before merging.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Manage the Skill as code: assign domain-team ownership (e.g., instructional-design team) recorded in frontmatter metadata and/or CODEOWNERS, and require changes to pass PR review plus CI evaluation before merging.**

Section 5.2 analyzes exactly options A, B, and C as "naive patches" that fail: a shared drive leaves no one responsible (anyone's casual tweak affects everyone); a single approver becomes a bottleneck and is not an expert in every domain; a separate instruction document goes stale as the Skill iterates. The source's answer is that a Skill is "an executable asset encapsulating expert knowledge" needing clear ownership and an engineered lifecycle — domain-team ownership (the team with the most measurement capability, made explicit via `owner`/`maintainers`/`version`/`last-reviewed` frontmatter and `.github/CODEOWNERS`) plus the Skills-as-Code lifecycle (local iteration → PR/Review → CI evaluation → deployment → feedback), which institutionally prevents both the version chaos and the unauthorized modification described in the stem.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — Sections 5.2 "Naive patching," 5.3 "Domain-team ownership" (metadata + CODEOWNERS tip), and 5.4 "Skills-as-Code" (lifecycle and GitHub Actions example).
</details>
