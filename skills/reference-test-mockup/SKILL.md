---
name: reference-test-mockup
description: Create rigorous, professional-level Markdown exams grounded in user-provided reference material, with hidden answer keys, evidence-based rationales, and traceable citations.
---

# Professional reference-based exam

Use this skill when a user provides or identifies a reference file and wants an exam, assessment, practice test, or question set based on it. Unless the user asks for a simpler quiz or specifies another level, write for a professional audience and assess applied judgment, not memorization alone.

## Inputs and source boundaries

- Identify and read the reference material before drafting. If it is unavailable, ask the user to attach it or provide an accessible path. Never invent facts, policies, tools, or expected practices.
- Honor the requested question count, audience, difficulty, topics, format, and output path. If no question count is given, create **10** questions without pausing to ask.
- Infer the professional audience and exam level from the reference. If the user asks for certification, hiring, compliance, or another consequential use, match the requested context while keeping every answer supportable by the supplied source.
- Assess only what the reference can support. Distinguish direct source facts from conclusions that require reasonable application of those facts. Do not use outside knowledge to make an answer key more demanding.
- If the source is too thin for the requested count or coverage, create the strongest supportable exam and briefly disclose the limitation in the final response; do not pad it with repetitive or speculative items.

## Build an exam blueprint

1. Extract the source's core concepts, procedures, decision rules, parameters, examples, limitations, risks, and exceptions. Record a precise locator for each usable point: heading, page, section, table, or named code/example.
2. Group those points into the major competencies the source supports. Allocate questions across them in proportion to their importance and coverage. Avoid over-testing one section just because it is easy to turn into questions.
3. For a 10-question set, aim for a progression such as: 2 foundational interpretation items, 5 applied scenario or decision items, and 3 analysis/troubleshooting items. Adjust when the source or requested audience calls for a different balance. Do not label items with cognitive taxonomies unless requested.
4. Prefer realistic professional scenarios with enough context to determine the best action, diagnosis, or conclusion. Test selection and application of principles, trade-offs, and failure analysis. Use direct recall only when precise knowledge itself is a material competency.

## Write and calibrate items

- Give each question one clear task and one unambiguously best answer under the stated assumptions. State necessary constraints in the stem; do not expect examinees to guess unstated environment, policy, or priorities.
- Use four options (A–D) by default, or five (A–E) when the extra distractor is genuinely plausible. Keep all options in the same category and similar in length, detail, and grammatical form.
- Make distractors credible and diagnostic: base them on likely misreadings, omitted prerequisites, incorrect sequencing, overgeneralization, or misuse of a source-supported concept. Do not use nonsense, unrelated options, or choices that are obviously inferior from wording alone.
- Make options mutually exclusive. Check that a knowledgeable candidate could not defend a second answer using the source or reasonable assumptions. If two choices are defensible, revise the stem or options rather than relying on the explanation to force a distinction.
- Avoid trick wording, double negatives, vague qualifiers, hidden assumptions, and unnecessary reading load. Avoid “all/none of the above.” Use a negative stem only when identifying what not to do is a core competency; emphasize the negative term.
- Vary answer positions across the exam without creating a predictable pattern. Do not let one letter dominate. Do not alter factual correctness merely to achieve a pattern.
- Avoid cues such as a uniquely detailed correct option, repeated wording between stem and key, grammatical mismatches, absolute terms used only in distractors, and neighboring questions that reveal each other's answers.
- Keep items independent unless the user requests a case-based exam. If items share a case, provide all case facts up front and ensure one answer does not disclose another.
- Do not claim the exam is validated, standardized, psychometrically reliable, or equivalent to a real certification exam. It is a source-grounded draft unless formal validation evidence is provided.

## Exam presentation

Create a clean, candidate-facing document with:

- A descriptive title derived from the source and a concise instruction line.
- A note to select the single best answer for each item, unless the format differs.
- Numbered questions with consistently labeled options.
- No answers, hints, or rationales visible in the question text.
- A native `<details>` block under each question containing the answer key and review material.

In each answer block:

- Give the correct option letter and its text.
- Explain why it is best by connecting the relevant source principle to the specific facts in the stem.
- Briefly explain why the most tempting alternative fails when doing so teaches a meaningful distinction. Do not mechanically explain every obviously wrong option.
- Give a precise, traceable source locator. Prefer a heading, page, table, section, or named code/example. If pagination is unstable or absent, cite the heading and identify the relevant passage. Never fabricate page numbers, quotations, or source details.
- Clearly identify any reasonable inference as an application of the cited material, not as a direct source statement.

Use this pattern unless the user requests another output format:

```markdown
# Professional Exam: [Topic]

Choose the single best answer for each question.

## Question 1

[A realistic task, scenario, or decision question.]

A. [Plausible option]

B. [Plausible option]

C. [Plausible option]

D. [Plausible option]

<details>
<summary>Show answer and rationale</summary>

**Answer: B — [option text]**

[Explain why this answer follows from the source and the scenario. Address the most plausible competing option when useful.]

**Source:** `Reference file` — “[Section or heading]” (specific passage, table, page, or example). [Explain the connection between this source point and the answer.]
</details>
```

## Output and file handling

- Create a ready-to-use `.md` file; do not print the full exam in chat or the console. Honor a user-specified output path.
- If no path is given, derive the filename from the reference basename (without its extension), prefix it with `MOCKUP_TEST_`, and use `.md`. For example, `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` becomes `MOCKUP_TEST_2_2_Expand_Knowledge_Scope_of_FAQ_Bot.md`.
- Save it in the current workspace. If the target exists, preserve it and choose a numbered variant such as `_2`.
- After saving, respond with a link to the file and a brief summary. Mention material source-coverage limitations when applicable.

## Final quality review

Before returning the file, verify:

1. The requested number and coverage are satisfied, or any source limitation is disclosed.
2. Every keyed answer is supported by the cited source, and the rationale accurately applies it to the stem.
3. Each item has exactly one best answer, sufficient context, and plausible, mutually exclusive distractors.
4. The exam tests professional judgment and application at the intended level without adding unsupported requirements.
5. Topics are balanced, questions are not duplicates or answer-revealing, and correct answer positions are reasonably distributed.
6. Every answer and rationale is inside its matching `<details>` block; references are traceable and contain no fabricated locators.
