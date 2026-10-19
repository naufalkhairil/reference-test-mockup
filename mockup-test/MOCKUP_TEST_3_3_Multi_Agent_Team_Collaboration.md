# Professional Exam: 3.3 Team Collaboration with Multiple Agents

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

Your team is going to use a multi-agent system to develop a new course. The requirements are clear: first the instructional designer produces the outline, then the technical expert fills in code examples, and finally the editor writes the text. Which collaboration pattern should you choose?

A. Co-creation collaboration, letting three Agents discuss freely around a shared whiteboard and produce the final plan through multiple rounds of iteration

B. Hierarchical planning, setting up a Leader Agent to assign subtasks to each expert Agent in order and aggregate the results

C. Have one all-powerful Agent play the three roles in turn, completing all the stages in the same context window

D. Have the three Agents each independently complete a full course draft, then have a human pick the best-quality one as the finished product

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Hierarchical planning, setting up a Leader Agent to assign subtasks to each expert Agent in order and aggregate the results**

This task has clear upstream-downstream dependencies (outline → code → text), a clear goal, and is decomposable — well suited to the hierarchical-planning pattern. A's co-creation pattern suits open-ended creative problems (such as "what kind of case to design"); used for a task with a clear process, it easily diverges and fails to converge. C violates the core value of multi-agent — each Agent has an independent context and focuses on its own task; a monolithic Agent handling multiple roles easily suffers attention diffusion. D is a parallel-redundancy strategy rather than collaboration; it wastes 3x compute resources and can't leverage the advantage of specialized division of labor.

**Source:** `3_3_Multi_Agent_Team_Collaboration.ipynb` — embedded lesson quiz and its explanation.

</details>
