# reference-test-mockup

A Kiro skill for creating professional-level Markdown exams grounded in user-provided reference material. Each question has a hidden answer and source-based rationale in a collapsible section.

## What it does

Given a reference document (a file, notebook, spec, etc.), the skill:

1. Reads and extracts the key claims, rules, examples, caveats, and distinctions from the reference, tracking a precise locator (heading, page, section, or example name) for each fact.
2. Builds multiple-choice questions that test understanding and application — not just copied wording — using short scenarios where the source supports it.
3. Produces one unambiguous best answer per question, with four plausible, similarly specific options by default.
4. Emphasizes applied judgment and realistic scenarios, varies correct answer positions, and avoids answer cues.
5. Saves the result as a ready-to-use `.md` file with the answer key and rationale hidden under `<details>`/`<summary>` blocks.

## Usage

### Use the skill

In a Kiro session where this skill is available, ask for an exam and identify the reference file by path. For example:

> Use the reference-test-mockup skill to create a 10-question professional exam from `docs/service-guide.md`. Save the Markdown file in `exams/`.

You can also specify the audience, difficulty, topics to cover, question count, or desired output path. For example:

> Create a 15-question exam for senior support engineers based on `materials/operations.ipynb`. Focus on incident diagnosis and recovery decisions. Save it as `assessments/operations-exam.md`.

The skill reads the source before drafting, uses only source-supported facts, and creates the exam as a Markdown file. Answers and rationales remain hidden under expandable sections. If no question count is specified, it creates 10; unless you request another level, it targets professional-level applied judgment. If the requested filename already exists, it saves a numbered copy rather than overwriting it.

- **Reference file**: Required. Provide a readable file path or identify an accessible file. The skill does not invent source material.
- **Audience, difficulty, and topics**: Optional. State any requirements in your request; unsupported topics are not added.
- **Output path**: Optional. Specify a path to choose where the Markdown exam is saved.

- **Reference file**: Required. The skill will not invent source material — if the file isn't available, it asks for it.
- **Number of questions**: Optional. Defaults to 10 if not specified.
- **Audience / difficulty / topics / style**: Optional. Professional level is the default; the skill infers audience and coverage from the reference if not specified.
- **Question approach**: Scenario-based application and decision-making are preferred. Direct recall is used when precise knowledge itself is important.

## Output

- A standalone `.md` file, not printed inline in the chat.
- Filename: derived from the reference file's basename, prefixed with `MOCKUP_TEST_` (e.g. `notes.ipynb` → `MOCKUP_TEST_notes.md`). A custom output path can be specified instead.
- Saved in the current workspace. If the target filename already exists, a non-overwriting numbered variant is used (e.g. `MOCKUP_TEST_notes_2.md`).
- Each question is numbered, with options labeled A–D (or A–E), followed by a collapsible block containing:
  - The correct answer
  - A detailed rationale, including why tempting distractors are wrong
  - A traceable source locator back to the reference

### Example question format

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

Explanation of why B is correct...

**Source:** `Reference file` — "Section or heading" (page/paragraph/example locator).
</details>
```

## Project structure

```
skills/
  reference-test-mockup/
    SKILL.md   # Skill definition consumed by Kiro
```

## Notes

- Citations are only as precise as the source allows. The skill does not fabricate page numbers, quotations, or other locators.
- The exam is a source-grounded draft; the skill does not claim formal validation or certification equivalence.
- Before returning the exam, the skill checks the requested question count, source support, single-best-answer quality, plausible distractors, and answer-block formatting.

## Streamlit mockup viewer

This repository also includes a Streamlit site for browsing and taking the Markdown quizzes in `mockup-test/`.

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app discovers quiz files from `mockup-test/` at startup. Add a Markdown mockup there to include it in the chapter selector.
