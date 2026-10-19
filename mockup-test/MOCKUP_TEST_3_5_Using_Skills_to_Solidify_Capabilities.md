# Professional Exam: 3.5 Using Skills to Solidify Capabilities into Reusable Processes

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

Your course-review Agent always misses the team convention "code examples must have comments." You've reminded it repeatedly across multiple conversations, but every new session it forgets again. What's the most effective solution?

A. Write "code must have comments" into the Agent's long-term memory, so it auto-retrieves this experience before each review

B. Write a Skill file containing the complete review checklist, and have the Agent load this Skill when executing the review task

C. Manually paste this requirement into the first message as a prompt each time you start a new conversation

D. Raise the model's temperature parameter so the Agent considers more possibilities during review and thereby covers this convention

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Write a Skill file containing the complete review checklist, and have the Agent load this Skill when executing the review task**

A is directionally right but not at the right level — Memory suits recording preferences and experience fragments (like "last time the API errored because the version was wrong"), but a scattered memory lacks execution context; the Agent knows "to check comments" but not necessarily the complete check process. C is manual repetitive labor and can't scale. D is unrelated to the problem — temperature affects output diversity, not check coverage. B is correct: a Skill encapsulates the complete review SOP (including all check items, check order, and criteria) as a reusable module; after loading it, the Agent gets systematic work instructions rather than scattered memory hints.

**Source:** `3_5_Using_Skills_to_Solidify_Capabilities.ipynb` — embedded lesson quiz and its explanation.

</details>
