# Professional Exam: Harness Engineering and Loop Engineering for Production-Ready Business Capabilities

Source: `3_8_Harness_Loop_Production_Capabilities_EN.ipynb` (Alibaba Cloud ACP LLM course, Lesson 3.8). This is a source-grounded draft practice exam, not an official or validated certification assessment.

> **Source-limitation note:** The reference notebook is a short section introduction (~3.4 KB): an introduction, learning objectives, a lesson preview containing the core improvement loop, and a pointer to the full course, whose lab manual, copy-ready prompts, and flowchart standard files are only available in the paid course. The detailed practice material is therefore not examinable. This exam contains 4 items covering everything the available intro text can rigorously support; a 10-question set could not be written without padding or fabricating content.

Choose the single best answer for each question.

## Question 1

According to the lesson's introduction, what is the central problem this lesson addresses?

A. How to produce publication-quality technical-documentation flowcharts from a single well-crafted Qwen Code prompt.

B. How to reduce the token cost of Agent workflows that run continuously in production.

C. How an Agent task goes from "works this one time" to "still works reliably when the topic or requirements change" — turning a category of Agent workflow into a business capability that is checkable, reusable, and production-ready.

D. How to evaluate and select among multiple LLMs for diagram-generation tasks in a documentation pipeline.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — How an Agent task goes from "works this one time" to "still works reliably when the topic or requirements change" — turning a category of Agent workflow into a business capability that is checkable, reusable, and production-ready.**

The introduction poses precisely this question ("The next problem to solve is: how does an Agent task go from 'works this one time' to 'still works reliably when the topic or requirements change'?") and states the lesson's point: "it isn't to draw one diagram — it's to learn how to turn a category of Agent workflow into a business capability that's checkable, reusable, and production-ready." Option A is the most tempting alternative because the flowchart pipeline is the lesson's exercise vehicle, but the source explicitly says drawing one diagram is not the point; B and D raise concerns the available notebook text never discusses.

**Source:** `3_8_Harness_Loop_Production_Capabilities_EN.ipynb` — "🚄 Introduction" (the "works this one time" question and the closing "checkable, reusable, and production-ready" statement).
</details>

## Question 2

Which sequence matches the core improvement loop stated in the lesson preview?

A. Skill → Standard → Test samples → Issue log → Screenshot verification → Write rules back → Verify on a new topic

B. Test samples → Skill → Standard → Screenshot verification → Issue log → Verify on a new topic → Write rules back

C. Standard → Test samples → Skill → Issue log → Screenshot verification → Verify on a new topic → Write rules back

D. Standard → Skill → Test samples → Screenshot verification → Issue log → Write rules back → Verify on a new topic

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Standard → Skill → Test samples → Screenshot verification → Issue log → Write rules back → Verify on a new topic**

The lesson preview gives the loop verbatim in a code block: `Standard -> Skill -> Test samples -> Screenshot verification -> Issue log -> Write rules back -> Verify on a new topic`, and the surrounding text reinforces the ordering — "define the standard first, then generate samples, use browser screenshots and verification reports to find problems, and write reusable lessons back into the Skill or the validator." A and B violate the "standard first" principle; C generates samples before the Skill exists and puts the write-back after new-topic verification, so lessons would never inform the verification they are meant to improve.

**Source:** `3_8_Harness_Loop_Production_Capabilities_EN.ipynb` — "🔎 Lesson Preview" (the fenced `Standard -> Skill -> ...` loop and the preceding sentence on defining the standard first).
</details>

## Question 3

In the workflow the lesson describes, what evidence is used to find problems in the generated flowcharts, and where should the reusable lessons learned be written back?

A. A human designer's aesthetic review; lessons go into an external style guide maintained outside the system.

B. Browser screenshots and verification reports; reusable lessons are written back into the Skill or the validator so future runs improve based on evidence.

C. The model's self-assessed confidence scores; lessons go into the run logs for a human to audit later.

D. Run duration and cost metrics per sample; lessons go into the stop conditions to bound future runs.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Browser screenshots and verification reports; reusable lessons are written back into the Skill or the validator so future runs improve based on evidence.**

The lesson preview states the workflow "use[s] browser screenshots and verification reports to find problems, and write[s] reusable lessons back into the Skill or the validator," and the introduction lists browser screenshots and verification reports among the components filled into the generated Skill "so it can keep improving based on evidence." C is the most tempting alternative because run logs are indeed part of the filled-in components, but the source assigns the problem-finding role to screenshots and verification reports, and the write-back target is the Skill or validator — logs are records, not where reusable rules land. A moves judgment outside the evidence loop the lesson builds; D invents metrics the notebook never mentions.

**Source:** `3_8_Harness_Loop_Production_Capabilities_EN.ipynb` — "🔎 Lesson Preview" (screenshots/verification reports and write-back sentence) and "🚄 Introduction" (component list: standards, browser screenshots, verification reports, Reviewer role, run logs, stop conditions).
</details>

## Question 4

So that the workflow "can keep improving based on evidence," which set of components does the introduction say you will fill into the Skill that Qwen Code first generates?

A. Standards, browser screenshots, verification reports, a Reviewer role, run logs, and stop conditions.

B. Standards, a fine-tuning dataset, GPU quotas, and a deployment manifest.

C. A vector database, an embedding model, retrieval tools, and memory-governance rules.

D. A Leader agent, Worker agents, a shared message hub, and a meeting secretary.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Standards, browser screenshots, verification reports, a Reviewer role, run logs, and stop conditions.**

The introduction states: "You'll have Qwen Code first generate an illustration Skill, then fill in standards, browser screenshots, verification reports, a Reviewer role, run logs, and stop conditions, so it can keep improving based on evidence." Option A matches this list item for item. C and D are the most tempting alternatives for candidates conflating lessons: they name capabilities taught elsewhere in this course (vector-based long-term memory in Lesson 3.4; multi-agent Leader/Member collaboration with a message hub and secretary in Lesson 3.3), but neither list appears in this lesson's Skill components; B invents infrastructure concerns the notebook never mentions.

**Source:** `3_8_Harness_Loop_Production_Capabilities_EN.ipynb` — "🚄 Introduction" (the second paragraph's component list for the generated illustration Skill).
</details>
