# reference-test-mockup

A Kiro skill that generates Markdown multiple-choice test mockups grounded in a user-provided reference file. Answers and explanations are hidden in collapsible sections, so the generated file doubles as a self-check quiz.

## What it does

Given a reference document (a file, notebook, spec, etc.), the skill:

1. Reads and extracts the key claims, rules, examples, caveats, and distinctions from the reference, tracking a precise locator (heading, page, section, or example name) for each fact.
2. Builds multiple-choice questions that test understanding and application — not just copied wording — using short scenarios where the source supports it.
3. Produces one unambiguous best answer per question, with 4–5 plausible, similarly-specific distractors.
4. Varies the correct answer position and avoids tells (absolutes, option length, repeated patterns).
5. Saves the result as a ready-to-use `.md` file with the answer key and rationale hidden under `<details>`/`<summary>` blocks.

## Usage

Invoke the skill by providing or identifying a reference file and asking for practice questions, a quiz, or an exam-style mockup based on it.

- **Reference file**: Required. The skill will not invent source material — if the file isn't available, it asks for it.
- **Number of questions**: Optional. Defaults to 10 if not specified.
- **Audience / difficulty / topics / style**: Optional. Inferred from the reference if not specified.
- **Question categories**: Usage, parameters, use cases, concepts, and best practices — only the categories the reference actually supports are used.

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

- Citations are only as good as the reference — the skill does not fabricate page numbers or quotations.
- Before returning the mockup, it self-checks question count, answer key correctness, source support, and that every answer stays inside its collapsible block.

## Streamlit mockup viewer

This repository also includes a Streamlit site for browsing and taking the Markdown quizzes in `mockup-test/`.

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The app discovers quiz files from `mockup-test/` at startup. Add a Markdown mockup there to include it in the chapter selector.
