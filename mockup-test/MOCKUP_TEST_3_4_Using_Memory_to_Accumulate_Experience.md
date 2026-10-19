# Professional Exam: 3.4 Using Memory to Let the Agent Accumulate Experience

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

After your course-writing Agent works for 30 rounds straight, it forgets the "style must be rigorous and academic" requirement the user set in round 1, and starts outputting casual, colloquial content. You're currently using a simple truncation strategy (keep the most recent N rounds). What's the most reasonable improvement?

A. Expand the truncation window from N rounds to 2N rounds to ensure the early style requirement isn't discarded

B. Hardcode the style requirement into the system prompt so it's unaffected by the memory-management strategy

C. Introduce vector-based long-term memory, persistently storing key preferences and retrieving them on demand before each reply

D. Switch to a rolling-summary strategy, periodically compressing old conversation into a summary to preserve core information

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Introduce vector-based long-term memory, persistently storing key preferences and retrieving them on demand before each reply**

A only delays when the problem occurs; no matter how big the window, it eventually fills up, and a long context causes attention dilution. B is feasible in this scenario, but only applies to known, fixed preferences; it can't handle new preferences the user dynamically generates during conversation, so it isn't general. D is better than truncation and can preserve some key information, but the summary quality depends on the compression model, and long-term accumulation may still lose details. C is the most reasonable: vector-based long-term memory persists key preferences into a vector database and, each time, retrieves the most relevant memory by the current task's semantics, fundamentally shaking off the length limit of the context window.

**Source:** `3_4_Using_Memory_to_Accumulate_Experience.ipynb` — embedded lesson quiz and its explanation.

</details>
