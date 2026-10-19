# Professional Exam: 3.2 Teaching the Agent to Plan & Execute

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

You developed a "course preliminary research" Agent that uses a fixed workflow to call three tools in parallel: industry analysis, user persona, and competitor analysis. After launch, the competitor site was redesigned, causing the crawler tool to fail frequently and the whole process to get stuck. How should you improve it?

A. Add a retry mechanism to the competitor-analysis tool; on failure, automatically retry three times then error out and exit

B. Preset branch handling logic and fallback plans for every tool-failure scenario in the workflow

C. Change the fixed workflow to the Plan & Execute mode, letting the Agent autonomously plan around the goal and dynamically handle exceptions

D. Switch to a more stable competitor-data API provider to eliminate the possibility of tool failure at the data-source level

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Change the fixed workflow to the Plan & Execute mode, letting the Agent autonomously plan around the goal and dynamically handle exceptions**

A only delays the failure; after the site redesign, retrying won't succeed either. B is directionally right but weak in means — presetting a branch for every exception makes workflow complexity explode, and you can't enumerate all accidents. D is idealized; in reality you can't guarantee any external service is always available. C is correct: the Plan & Execute mode turns the Agent from an "executor" into a "planner," so when a tool fails it can autonomously adjust the plan (e.g. switch to another information source or skip that step), gaining adaptability at the architectural level.

**Source:** `3_2_Teaching_Agent_to_Plan_and_Execute.ipynb` — embedded lesson quiz and its explanation.

</details>
