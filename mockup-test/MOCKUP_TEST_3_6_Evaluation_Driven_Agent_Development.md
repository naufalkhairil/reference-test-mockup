# Professional Exam: 3.6 Evaluation-Driven Agent Development

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

Your course-writing Agent's end-to-end evaluation shows the course-quality score stable at 4.2/5, but user feedback says "the code examples often won't run." How should you locate and solve this problem?

A. Raise the strictness of the end-to-end evaluation, bumping the pass threshold from 4.0 to 4.5 to filter out low-quality output

B. Add white-box evaluation, separately checking whether the code-generation stage's output is executable, precisely locating the fault node

C. Swap the underlying LLM for a version with stronger coding ability, improving code-generation correctness at the model level

D. Append an emphatic instruction "the generated code must be guaranteed to run" to the system prompt to constrain the output

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Add white-box evaluation, separately checking whether the code-generation stage's output is executable, precisely locating the fault node**

A only tightens the overall scoring threshold and can't precisely locate the specific problem of "code not executable." C is an optional optimization direction, but swapping the model without first locating the problem is blind investment, and the code problem may stem from context rather than model capability. D is the typical "solving an engineering problem with a prompt," with uncertain effect and no way to validate. B is correct: the core value of white-box evaluation is "opening the black box," setting a separate check metric for a specific node in the Agent's execution chain (such as the code-generation stage); only after precisely locating the problem can you optimize in a targeted way.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — embedded lesson quiz and its explanation.

</details>
