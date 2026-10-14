---
name: reference-test-mockup
description: Generate Markdown multiple-choice test mockups grounded in a user-provided reference file, with answers and cited explanations hidden in collapsible sections.
---

# Reference-based test mockup

Use this skill when a user provides or identifies a reference file and wants practice questions, a quiz, or an exam-style mockup based on it.

## Inputs

- Identify the reference file and read it before drafting questions. If it is unavailable, ask the user to attach it or provide an accessible path; do not invent source material.
- Let the user specify the number of questions. If they do not, generate **10** by default; do not pause to ask.
- Honor any requested audience, difficulty, topics, or question style. If these are unspecified, infer a reasonable level from the reference and make the set balanced.
- The skill should support questions about **usage, parameters, use cases, concepts, and best practices**. Cover the categories that the reference actually supports; do not force unsupported categories.

## Create the questions

1. Extract the reference's key claims, rules, examples, caveats, and distinctions. Track a precise locator for each fact (heading, page, section, or code/example name).
2. Build questions that test understanding and application, not just copied wording. Use short scenarios when the source provides enough detail.
3. Give each question one unambiguous best answer. Provide four or five plausible options, unless the user requests another format. Keep options similar in specificity and length; distractors should reflect realistic misunderstandings, not absurd or giveaway choices.
4. Vary the correct answer position. Check that no other option could also be correct under the stated assumptions, and that questions do not rely on facts absent from the reference.
5. Avoid duplicate questions and avoid making the answer obvious through wording, option length, absolutes, or repeated patterns.

## Output format

Create a ready-to-use `.md` file containing the mockup; do not print the full mockup in the chat or console. Honor a user-specified output path. If none is specified, derive the filename from the reference file's basename (without its extension), prefix it with `MOCKUP_TEST_`, and use the `.md` extension. For example, `2_2_Expand_Knowledge_Scope_of_FAQ_Bot.ipynb` becomes `MOCKUP_TEST_2_2_Expand_Knowledge_Scope_of_FAQ_Bot.md`. Save it in the current workspace. If the target filename already exists, choose a non-overwriting variant by adding a number, such as `MOCKUP_TEST_2_2_Expand_Knowledge_Scope_of_FAQ_Bot_2.md`. After saving, respond with a link to the file and a brief summary only.

Number each question and label options consistently (A–D or A–E). Place the key and explanation in a native collapsible block using `<details>` and `<summary>` so it is hidden until opened. For each item, include the correct option, a detailed rationale, a brief explanation of why the tempting alternatives are wrong when useful, and the reference locator.

Use this pattern:

```markdown
## Question 1

Question text

A. First option
B. Second option
C. Third option
D. Fourth option

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

Explanation of why B is correct, including the relevant reasoning. Note why plausible distractors do not apply, where useful.

**Source:** `Reference file` — “Section or heading” (page/paragraph/example locator). Explain how that passage supports the answer.
</details>
```

Repeat the block for the requested number of questions. Make source references traceable to the supplied material: prefer page and section/heading, or a named code/example. Do not fabricate page numbers or quotations. If the reference has no stable pagination, cite its heading and describe the relevant passage; use a short quote only when exact wording helps identify it.

## Final review

Before returning the mockup, verify the question count, answer key, source support, single-best-answer quality, plausible distractors, and that every answer remains inside its collapsible block. State briefly if the reference did not cover a requested topic or if any citation locator is approximate.
