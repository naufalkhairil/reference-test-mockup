# Professional Exam: Multi-Agent Team Collaboration

Source: `3_3_Multi_Agent_Team_Collaboration.ipynb` (Alibaba Cloud ACP LLM course, Lesson 3.3). This is a source-grounded draft practice exam, not an official or validated certification assessment.

Choose the single best answer for each question.

## Question 1

In the hierarchical planning (Leader-Worker) pattern described in the lesson, how are responsibilities divided?

A. The Leader executes the most technically demanding subtask while the members critique its output and vote on the final deliverable.

B. The Leader and the members discuss freely as peers in a shared channel until the team converges on a final deliverable.

C. The Leader receives and understands the top-level task, decomposes it into concrete subtasks, assigns them to suitable members, tracks overall progress, and aggregates the results; members focus on executing their assigned subtasks and report back when done.

D. The Leader inspects each incoming request and routes it to exactly one preset processing path, which the members then run end to end.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The Leader receives and understands the top-level task, decomposes it into concrete subtasks, assigns them to suitable members, tracks overall progress, and aggregates the results; members focus on executing their assigned subtasks and report back when done.**

Section 2.1 defines the pattern as a "centralized star structure" with exactly these two roles: the Team Leader (e.g., the "course project supervisor") handles understanding, decomposition, assignment, progress tracking, and final aggregation; Team Members (instructional designer, data scientist, content writer) execute their assigned subtasks and report to the Leader. B describes the co-creation (blackboard) pattern, which is decentralized; D describes a branching router from the workflow lesson, not a Leader decomposing and aggregating work; A invents a critique-and-vote dynamic the source never describes for this pattern.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 2.1 "Pattern one: Hierarchical Planning (Hierarchical/Team Leader Pattern)" (role definitions of Team Leader and Team Members).
</details>

## Question 2

According to the lesson, how is the hierarchical planning pattern implemented in AgentScope?

A. Through the handoff mechanism: the Leader Agent treats domain experts as tools, with task assignment and reporting implemented as tool calls; asynchronous tool calls and dynamic tool extension allow experts to run concurrently and let the Leader create expert Agents in real time as needed.

B. Through `MsgHub`: every message is broadcast to all participants, and the Leader emerges as the most active speaker.

C. Through `PlanNotebook`: the Leader compiles its decomposition into a fixed workflow that members execute without further planning.

D. Through `fanout_pipeline`: all members always run in parallel on the same message and their outputs are gathered automatically.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Through the handoff mechanism: the Leader Agent treats domain experts as tools, with task assignment and reporting implemented as tool calls; asynchronous tool calls and dynamic tool extension allow experts to run concurrently and let the Leader create expert Agents in real time as needed.**

Section 2.1 states: "In AgentScope, you can implement the hierarchical-planning pattern using the handoff mechanism. In this pattern, the Leader Agent treats domain experts as tools, and assigning tasks and hearing reports are implemented in the form of tool calls," and notes support for asynchronous tool calls and dynamic tool extension. The code example registers `invoke_designer_li`, `invoke_scientist_wang`, and `invoke_writer_zhang` on the Leader's `Toolkit`. B describes the co-creation implementation (`MsgHub`), a different pattern; C and D borrow constructs from other lessons and are not the mechanism the source names for this pattern.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 2.1 (handoff paragraph) and the accompanying hierarchical-planning code example (`leader_toolkit.register_tool_function(invoke_designer_li)` etc.).
</details>

## Question 3

In the lesson's hierarchical course-development example, `LEADER_PROMPT` requires calling the designer first, then passing the designer's outline to `invoke_scientist_wang` via its `context` argument, then passing the merged outputs to `invoke_writer_zhang`. What does the `context` parameter accomplish in this design?

A. It gives every expert read access to the full team discussion transcript, as in a shared whiteboard.

B. It lets the Leader verify each expert's output against a stored baseline before the next call.

C. It lets downstream experts write their results directly into the upstream experts' memory.

D. It passes prior work products (such as the designer's outline) to the downstream expert so each stage builds on the previous one — the upstream-downstream dependency is mediated by the Leader relaying outputs between tool calls.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — It passes prior work products (such as the designer's outline) to the downstream expert so each stage builds on the previous one — the upstream-downstream dependency is mediated by the Leader relaying outputs between tool calls.**

The tool docstrings define `context` as "optional. Pass prior work products such as the course outline, so he can build on them," and `LEADER_PROMPT` enforces the sequence: designer → scientist (outline as `context`) → writer (merged outputs as `context`) → Leader integration. Because members "usually don't communicate directly, but pass information through the project supervisor," the Leader's relaying of `context` is how the dependency chain is realized. A describes MsgHub-style shared visibility, which this pattern deliberately does not have; B and C invent capabilities not present in the example.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 2.1 code example (`LEADER_PROMPT` steps 1–4 and the `invoke_*` function docstrings for the `context` argument).
</details>

## Question 4

From the context-engineering perspective given in the lesson, why does decomposing a course project across specialized sub-agents improve output quality compared with one agent handling everything?

A. The Leader model is typically stronger than the member models, so its supervision raises the average quality of member outputs.

B. Each sub-agent has an independent context window and only needs to focus on the part of the task it owns, undisturbed by irrelevant information from other stages — more focused input and more precise output, each expert working in its own "focus space."

C. Tool-call formatting compresses each expert's output before it reaches the Leader, so the final aggregation runs on a shorter, cleaner context.

D. Running members concurrently shortens total elapsed time, which gives the model more compute budget per subtask.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Each sub-agent has an independent context window and only needs to focus on the part of the task it owns, undisturbed by irrelevant information from other stages — more focused input and more precise output, each expert working in its own "focus space."**

The lesson states this directly: "from a context-engineering perspective, each sub-agent has an independent context window; it only needs to focus on the part of the task it's responsible for, without being disturbed by irrelevant information from other stages. This means each sub-agent's input is more focused and its output more precise... each producing local content in its own 'focus space,' so quality is naturally higher." A assumes a model-strength hierarchy the source never claims (the example uses one uniformly configured model); C invents a compression benefit; D confuses latency with quality — and in this example the stages are sequential, not concurrent.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 2.1, the advantages paragraph after the hierarchical-planning code example ("clear structure, clear division of responsibility" and the independent-context/"focus space" argument).
</details>

## Question 5

While writing course code, the data scientist realizes a theory point would be clearer if the instructional designer used a simpler example. Within the hierarchical pattern as described, what structural consequence does the lesson identify?

A. The scientist must report the suggestion to the supervisor, who relays it to the designer; this relay may involve information delay or distortion, and the finished modules — though individually high quality — may combine stiffly, lacking a seamless, integrated flow because experts lack direct, real-time collision of ideas.

B. The scientist messages the designer directly through the shared hub, and the supervisor is notified only after the change is agreed.

C. The supervisor automatically detects the cross-domain conflict at aggregation time and re-plans the affected subtasks.

D. The workflow pauses for a human decision, because cross-role changes are a high-risk operation in this pattern.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — The scientist must report the suggestion to the supervisor, who relays it to the designer; this relay may involve information delay or distortion, and the finished modules — though individually high quality — may combine stiffly, lacking a seamless, integrated flow because experts lack direct, real-time collision of ideas.**

This is the lesson's stated limitation, using this exact example: members "usually don't communicate directly, but pass information through the project supervisor... This process may involve information delay or distortion. In the end, although each module of the course is completed with high quality, combined together they may feel a bit stiff, lacking a seamless, integrated flow. Because the experts lack direct, real-time collision of ideas." B describes the decentralized co-creation pattern, not the star structure; C attributes automatic conflict detection that the source never claims; D imports a human-in-the-loop mechanism from another lesson that is not part of this pattern's description.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 2.1, the limitations paragraph beginning "But this pattern's limitations also stem from its structure" (data-scientist/designer relay example).
</details>

## Question 6

In the lesson's co-creation example, three expert agents hold two rounds of discussion inside a `MsgHub` opened with an announcement. How is the final deliverable produced?

A. The expert who spoke last in the final round consolidates the discussion into the course outline draft.

B. The three experts each submit their own outline and vote to merge the versions they prefer.

C. A separate "meeting secretary" agent reads the full discussion transcript and generates the course outline draft in a defined Markdown structure (module title, learning objectives, core concepts, core case, code examples, homework exercise).

D. The `MsgHub` announcement is updated iteratively until it contains the merged outline, which becomes the deliverable.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — A separate "meeting secretary" agent reads the full discussion transcript and generates the course outline draft in a defined Markdown structure (module title, learning objectives, core concepts, core case, code examples, homework exercise).**

After the discussion rounds, the code builds an aggregation stage: a "meeting secretary" agent with a `secretary_prompt` receives the complete transcript (collected via `designer_li.memory.get_memory()` and formatted as `[name]: content` lines) and produces the outline draft with the six specified parts. A, B, and D all invent mechanisms absent from the example — the source shows no voting, no last-speaker consolidation, and the announcement only opens the meeting ("starting with instructional designer Teacher Li").

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 2 co-creation code example (the `MsgHub` block, the "Aggregation stage" comments, `secretary_prompt`, and `final_output_msg`).
</details>

## Question 7

A team runs a decentralized brainstorm of agents on an open-ended design problem. After several rounds, the discussion keeps diverging, over-optimizes details of one module while losing sight of the overall goal, and shows no sign of converging. According to the lesson, what is the most likely diagnosis?

A. The member models are too weak for creative work; co-creation requires top-tier models in every seat.

B. The discussion transcript grew too long, so the secretary agent should have been invoked after the first round.

C. The opening announcement should have contained the complete target outline in advance to anchor the discussion.

D. This is the pattern's characteristic risk: without good facilitation, and with no centralized decision-maker, a brainstorm can diverge for a long time or deadlock, over-optimize details, and lose sight of the overall goal.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — This is the pattern's characteristic risk: without good facilitation, and with no centralized decision-maker, a brainstorm can diverge for a long time or deadlock, over-optimize details, and lose sight of the overall goal.**

The lesson states these risks verbatim for co-creation collaboration: "A brainstorm without good facilitation may well fail to converge for a long time because the discussion diverges, or fall into a deadlock. Since there's no centralized decision-maker, the team may over-optimize some details while losing sight of the overall goal." The observed symptoms match this diagnosis exactly. A, B, and C propose causes the source never identifies; C would also defeat the purpose of open brainstorming, and B mistakes the aggregation step for a convergence control. The source does add that this pattern places "higher demands on controlling communication cost" because all members constantly process each other's information — consistent with D, not with the other options.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 2, the co-creation risks paragraph after the MsgHub example ("fail to converge... deadlock... over-optimize some details while losing sight of the overall goal").
</details>

## Question 8

Your team must develop a new course with clear requirements and strict upstream-downstream dependencies: the instructional designer produces the outline, then the technical expert fills in code examples based on that outline, and finally the editor writes the learner-facing text. The deliverable and the process are both clearly defined. Which collaboration pattern does the lesson indicate, and why?

A. Co-creation collaboration, because sequential writing work benefits from continuous mutual inspiration among the three experts.

B. Hierarchical planning, because the goal is clear and decomposes cleanly into ordered subtasks; a Leader can assign them in sequence, pass each stage's output forward, track progress, and aggregate the final document with clear responsibility.

C. A single all-purpose agent playing the three roles in turn within one context window, avoiding inter-agent coordination overhead.

D. Three agents each drafting the complete course independently, with a human selecting the best draft as the finished product.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Hierarchical planning, because the goal is clear and decomposes cleanly into ordered subtasks; a Leader can assign them in sequence, pass each stage's output forward, track progress, and aggregate the final document with clear responsibility.**

The lesson states the hierarchical pattern "is very suitable for scenarios with a clear goal that can be cleanly decomposed into multiple... subtasks," with clear structure and responsibility and easy progress tracking — and its worked example is precisely the outline → technical content → text chain mediated by the supervisor. A applies the co-creation pattern, which the source reserves for open-ended problems with no single correct answer; on a clearly defined process it "easily diverges and fails to converge." C contradicts the source's context-engineering argument (each sub-agent's independent, focused context is why quality is higher) and the monolithic-agent limitation in the summary; D is parallel redundancy rather than collaboration — it wastes compute and forgoes the specialized division of labor.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 2.1 (suitability paragraph and the sequential Leader example), Section 4 summary ("limitation of a monolithic Agent"), and the lesson quiz explanation contrasting hierarchical planning with co-creation, single-agent, and redundant-draft alternatives.
</details>

## Question 9

A company needs to (1) generate the core creative concept for a brand-new course — open-ended ideation with no single correct answer — and then (2) execute a well-defined production plan with clear deliverables. Following Section 3's design guidance, what approach does the lesson recommend?

A. A hybrid: first determine the core creative idea through a co-creation "brainstorm," then switch to the "project supervisor" hierarchical pattern to divide the work and execute — retaining controllability of the overall structure while introducing creativity at key points.

B. Hierarchical planning for both phases, because clear responsibility and progress tracking matter more than ideation quality.

C. Co-creation collaboration for both phases, because the team that brainstorms the concept together executes it best.

D. Either pattern for both phases, chosen by team preference, because the lesson states the two patterns perform equivalently.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — A hybrid: first determine the core creative idea through a co-creation "brainstorm," then switch to the "project supervisor" hierarchical pattern to divide the work and execute — retaining controllability of the overall structure while introducing creativity at key points.**

Section 3 describes exactly this: "in reality, a complete project may even have both: first determine the core creative idea through a 'brainstorm,' then switch to the 'project supervisor' pattern to divide the work and execute. This hybrid pattern retains the controllability of the overall structure while introduces creativity at key points." B sacrifices the creativity the source assigns to co-creation for open-ended ideation; C applies a divergence-prone pattern to a clearly decomposable execution phase; D distorts "there is no so-called 'best pattern'" — the lesson means the choice should follow the real-world task structure (business process, expert roles, collaboration mode), not that the patterns are interchangeable or equivalent.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — Section 3 "Selection Advice: Design Comes from Reality" (the hybrid brainstorm-then-supervisor example and the three observation aspects: business process, expert roles, collaboration mode).
</details>

## Question 10

A stakeholder objects: "A multi-agent system consumes 3–5x the tokens of a single agent, plus extra latency. Why should we accept that cost?" According to the lesson's cost-and-value guidance, what is the best-supported response?

A. Multi-agent systems actually lower the effective per-call cost, because each expert receives a shorter prompt than a monolithic agent would.

B. The token multiplier is offset automatically by platform caching, so the 3–5x figure never appears on the bill.

C. Although a multi-agent system increases call cost and latency, it improves the "usability" of the final output, avoiding the repeated attempts and hidden costs caused by low-quality output — an effective investment in high-quality results.

D. The 3–5x multiplier applies only to co-creation collaboration; hierarchical planning costs the same as a single agent because members run sequentially.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Although a multi-agent system increases call cost and latency, it improves the "usability" of the final output, avoiding the repeated attempts and hidden costs caused by low-quality output — an effective investment in high-quality results.**

The lesson's summary states this trade-off directly: "although a multi-agent system increases call cost and latency, by improving the 'usability' of the final output it avoids the repeated attempts and hidden costs caused by low-quality output — an effective investment in high-quality results." The 3–5x token-consumption figure comes from the stated course objectives (cost awareness of multi-agent systems). A contradicts the acknowledged cost increase; B invents a platform mechanism the source never mentions; D fabricates a per-pattern cost distinction — the source presents the multiplier as a general property of multi-agent systems, not of one pattern.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — "Course Objectives" (cost awareness of multi-agent systems, 3–5x token consumption) and Section 4 "Summary" (the "trade-off between cost and value" bullet).
</details>
