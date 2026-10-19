# Professional Exam: 3.7 Hands-On with Qwen Code: Mastering the Coding Agent's Daily Workflow

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

Regarding the "understand first, then plan, then code, then commit" workflow, which of the following is the most sensible practice

A. Always strictly follow all four E → P → C → C stages every time, without skipping any of them

B. For a simple single-file change, you can skip Explore and Plan and go straight to the Code stage

C. Once the Agent generates a plan in the Plan stage, execute it directly without human review

D. In the Commit stage, just let the Agent commit directly, without checking the list of staged files

<details>
<summary>Show answer and rationale</summary>

**Answer: B — For a simple single-file change, you can skip Explore and Plan and go straight to the Code stage**

This workflow is a flexible framework, not a rigid process. For simple tasks, just tell the Agent what to do directly; but for complex tasks involving multiple files and multiple steps, understanding and planning first significantly reduces rework. Option C is wrong: the plan must be reviewed by a human. Option D is wrong: you must check the list of staged files before committing.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 2

Every new session, the Agent writes DashScope's API address as the OpenAI default address, and you've already corrected it three times. What's the most sensible way to fix this

A. Manually remind the Agent at the start of every session

B. Write the correct API address and an example of the mistake into the "Common Pitfalls" section of QWEN.md

C. Create a custom command `/fix-url` and trigger it manually whenever you spot the error

D. Create a Skill that has the Agent automatically check the API address while writing code

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Write the correct API address and an example of the mistake into the "Common Pitfalls" section of QWEN.md**

This is a project constraint that holds true across every session, and it's a specific mistake the Agent keeps repeating — this fits QWEN.md's principle of "writing memory in response to failure" exactly. Once written in, the Agent loads it every time it starts. Option C is a remedy after the fact, not prevention. Option D is overkill for this.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 3

While developing a Gradio UI, /context shows context usage at 75%. What's the most sensible action to take now

A. Immediately run `/clear` to wipe out all context

B. Run `/compress` to compress the conversation history, then continue with the current task

C. Ignore the usage level and keep developing until the Agent starts noticeably forgetting things

D. Close the terminal and restart Qwen Code

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Run `/compress` to compress the conversation history, then continue with the current task**

When context usage is high but the task isn't finished yet, `/compress` keeps the key information and compresses redundant history, freeing up space to keep working. Option A is too drastic — you lose all session context and have to re-explain the current task to the Agent. Option C is risky — once the context overflows, the Agent may lose its memory of important constraints.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 4

Which extension mechanism should each of the following four needs use?① Checking for hardcoded API keys before every commit② Looking up the latest LlamaIndex documentation while writing code③ The project must follow the PEP 8 convention④ Automatically checking instructional-writing conventions when reviewing course content

A. ① Skill ② MCP ③ QWEN.md ④ Custom command

B. ① Custom command ② MCP ③ QWEN.md ④ Skill

C. ① Custom command ② Skill ③ QWEN.md ④ MCP

D. ① QWEN.md ② MCP ③ Skill ④ Custom command

<details>
<summary>Show answer and rationale</summary>

**Answer: B — ① Custom command ② MCP ③ QWEN.md ④ Skill**

Using the decision tree from section 5.4 — ① is a fixed check process, manually triggered → custom command. ② requires calling an external service, with the Agent deciding on its own when to consult it → MCP. ③ is a project constraint that holds true across every session → QWEN.md. ④ is domain-expert knowledge that should load automatically when the Agent recognizes a relevant task → Skill.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 5

Which of the following counts as the "committing without verifying" anti-pattern

A. After the Agent modifies rag.py, you run the existing test cases, confirm they pass, and commit

B. After the Agent generates app.py, you start the Gradio app, manually test three scenarios, and then commit

C. After the Agent modifies evaluate.py, you check the diff, decide the change looks reasonable, and commit directly

D. After the Agent creates a new .gitignore file, you check its contents to confirm Key.json is included, and commit

<details>
<summary>Show answer and rationale</summary>

**Answer: C — After the Agent modifies evaluate.py, you check the diff, decide the change looks reasonable, and commit directly**

Option C only checks that the diff "looks reasonable," without actually running the code to verify the change is correct. evaluate.py involves RAGAS evaluation logic, and reviewing the diff alone can't catch problems that only surface at runtime (like a parameter type mismatch). The core problem with "committing without verifying" isn't "not looking at the diff" — it's "assuming the code is correct without running or testing it."

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 6

Regarding QWEN.md's three-level configuration hierarchy, which statement is correct

A. A directory-level QWEN.md's content completely overrides a project-level QWEN.md's content

B. A global QWEN.md is a good place to put a specific project's tech stack and module structure information

C. The three levels load in the order "global → project → directory," and the more specific level has higher priority

D. If the project-level and directory-level QWEN.md files conflict, the Agent will prompt the user to choose

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The three levels load in the order "global → project → directory," and the more specific level has higher priority**

The three-level configuration is designed to go "from general to specific," with more specific configuration taking priority. A is wrong: the directory level adds to and overrides the project level — it doesn't replace it entirely. B is wrong: global configuration is for content that's general across projects (like personal coding preferences). D is wrong: configuration conflicts are resolved automatically by priority — the user doesn't need to choose manually.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 7

Regarding the five-step method for writing a Skill, which step is most critical

A. Step 3: writing the first draft of the Skill — the more complete the rules, the better

B. Step 1: have the Agent run unaided once, and record the failure cases as a baseline

C. Step 5: iterate repeatedly until the Skill perfectly covers every scenario

D. Step 4: verify with a new session — make sure the Agent has loaded the Skill

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Step 1: have the Agent run unaided once, and record the failure cases as a baseline**

Step 1 (establishing a baseline) is the foundation of the whole method. Without a baseline, you can't tell whether the Skill actually improved the Agent's behavior — you're just going on a "feeling" that it got better. Skipping step 1 and writing the Skill directly often produces rules that "look reasonable but don't actually solve the problem." The problem with option A is chasing completeness instead of targeting — a Skill should first cover the most critical failure scenarios, not attempt to be an encyclopedia.

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 8

From a Harness Engineering perspective, what role should QWEN.md play

A. The project's complete technical documentation — the more detailed, the better

B. A directory and navigation aid for project knowledge — stay lean, and point to more detailed sources of information

C. The Agent's sole source of knowledge — every rule must be written in QWEN.md

D. A configuration file written once, with no need for further updates

<details>
<summary>Show answer and rationale</summary>

**Answer: B — A directory and navigation aid for project knowledge — stay lean, and point to more detailed sources of information**

QWEN.md is better suited to serving as a table of contents for project knowledge, not an encyclopedia. It should stay lean, providing only project background and pointers to "where to find more detailed information." Detailed design docs, coding conventions, and architectural decisions belong in separate files, which the Agent reads on demand. Option A crowds out context. Option C ignores the role that Skills and standalone docs play. Option D violates the principle of "updating continuously in response to problems."

**Source:** `3_7_Qwen_Code_Practice_EN.ipynb` — embedded lesson quiz and its explanation.

</details>
