# 3.5 Using Skills to Solidify Capabilities into Reusable Processes

## 🚄 Preface

Memory made the Agent remember your preferences, but the specific working methods still have to be re-explained in conversation each time. Skills solve exactly this: solidifying "in what situation, what the correct approach is" into a triggerable, dedicated process. In this lesson, you'll learn to design a Skill from scratch and explore the team-based application of Skills.

## 🍁 Course Objectives

**You will learn:**
- Understand the evolution logic from "temporary Prompt" to "reusable Skill"
- The structure of a Skill: trigger conditions, workflow, knowledge base
- How to write a high-quality Skill (the five-step writing method)
- Skills-as-Code: bringing Skills into version control and CI/CD
- The Skill ecosystem: community sharing and reuse

```python
# Load the Model Studio API Key for calling the Qwen LLM
import os, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath('')), 'course_core'))
sys.path.insert(0, os.getcwd())

from openai import OpenAI
from config.load_key import load_key
load_key()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
print(f"API Key loaded: {os.environ['DASHSCOPE_API_KEY'][:5]}*****")
```

Let's recap the path you've walked: you first equipped the Agent with monolithic capabilities like tool calling, reflection, and memory, using these to let it handle multi-step tasks and then cope with more complex scenarios. At this point, the Agent is already quite complete at the **capability** level.

You've probably tried having AI review code, revise articles, or check documents for you — it does give feedback, but it always feels like scratching an itch through a boot: the issues it raises are either too generic ("suggest adding comments") or miss the point (missing the real bug while fussing over naming style). The problem isn't that the Agent's capability is insufficient, but that it doesn't know **what your standard is**.

This chapter uses "reviewing technical tutorials" as a running example — at an educational content company, reviewing tutorials written by colleagues is part of daily work, and you have ready-made material at hand (the Jupyter Notebooks under the `docs/` directory). But the problem to solve here is general: **how do you hand the professional standard in your head to the Agent?**

Suppose you receive a task: review a technical tutorial written by a colleague. This tutorial is "Python Data Analysis in Practice" under the `docs` directory — a complete Jupyter Notebook with nearly 300 cells, covering everything from environment setup, data cleaning, feature engineering, to visualization and comprehensive business analysis. The easiest method you'd think of is: use your existing Agent and just give it one sentence.

## 1 Reviewing a Tutorial with a Prompt

You already have a fully-functional ReActAgent. Equip it with a `read_file` tool so it can read files, then, just as you'd normally use an AI assistant, give it one sentence directly:

```python
import asyncio
import os
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg, TextBlock
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit, ToolResponse

async def read_file(file_path: str) -> ToolResponse:
    """Read the content of the file at the given path.

    Args:
        file_path: the path of the file to read

    Returns:
        the file content as a string
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return ToolResponse(content=[TextBlock(type="text", text=content)])

async def main():
    toolkit = Toolkit()
    toolkit.register_tool_function(read_file)

    agent = ReActAgent(
        name="Course Reviewer",
        sys_prompt="You are an AI assistant that can help users complete various tasks.",
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
        max_iters=8,
    )

    # Turn off console output of the intermediate process (tool calls, JSON, etc.), keeping only the final result
    agent.set_console_output_enabled(False)

    response = await agent(Msg("user",
        "Help me review docs/Python数据分析实战.ipynb — see how the quality is and whether it can be published.",
        "user"))

    # Extract the plain-text content from the returned Msg object
    print(response.get_text_content())

await main()
```

Run the code above and observe the review report the Agent returns. You'll find it does give feedback — but most of it is "one-size-fits-all" generic advice, such as "add code comments," "add exception handling," "optimize chart display," "add learning resources," etc. **Replace "Python Data Analysis in Practice" with any technical tutorial and this advice still holds.** It's correct nonsense.

And if you spot-check this Notebook yourself, you'll find it mentions not a single one of the real problems that **hold true only for this tutorial**:

- **Code won't run**: the end of the course uses `pd.ExcelWriter(..., engine='openpyxl')` to export analysis results to Excel, but the environment-setup section only installed `pandas numpy matplotlib seaborn` — executing to this point will directly raise `ModuleNotFoundError`.
- **Saying one thing, doing another**: the cleaning plan explicitly states filling `city` and `gender` with the **mode**, but the actual code fills them with the string `"unknown"` — two completely different strategies, with no explanation in between.
- **Explanation-style issues**: the course opens with a whole paragraph of novel-style description ("You've just joined a mid-sized e-commerce company, your seat isn't even warm yet..."), with wisecracks appearing in several places ("the data comes with all kinds of 'surprises'," "Congratulations!").

Why can't the Agent find these real problems?

Because the Agent uses a **generic review standard** — it knows a course should be complete, clearly structured, and runnable, but this is only a generalized understanding. Your team, however, has a more **professional, more fine-grained** set of review requirements that only you and your team members know:

1. **Code executability**: whether each code block executes smoothly in a clean environment, whether there are missing dependencies or path problems
2. **Content accuracy**: whether the technical concepts and API usage are consistent with the latest docs, whether the text descriptions and code implementations are consistent
3. **Learning curve**: whether the arrangement of knowledge points follows a progressive design, whether there are jumps that are too large
4. **Explanation style**: whether it's friendly to beginners, whether there are wisecracks or superfluous scenario descriptions

These standards live in the experience of you and your team members — a generic model has no way to know them.

> 💡 **Tip**: in review tasks, the LLM easily gives "one-size-fits-all" generic advice. To get targeted feedback, the key isn't wording tricks, but providing a clear review standard — telling it exactly what you care about.

The natural improvement idea is: **write these review standards explicitly into the Prompt**, telling the Agent what your team actually cares about. Besides the review standards, you may also need to tell it how to handle the Notebook format (`.ipynb` is a JSON structure, where code blocks, Markdown blocks, and output blocks each have different fields). The final Prompt might become like this:

```text
Please review docs/Python数据分析实战.ipynb, checking item by item against the following standards:

## Review standards
1. Code executability: execute all code blocks one by one in a clean environment, checking for missing
   dependencies, undefined variables, path problems. Note that .ipynb files are JSON format, and the code
   is in the cells[*].source field.
2. Content accuracy: verify whether API usage is consistent with the latest docs, and whether the text
   description and code implementation are consistent (e.g. if the text says "fill with the mode," does
   the code really use the mode).
3. Learning curve: from the first section to the last, whether knowledge points progress gradually, whether
   there are jumps that are too large.
4. Explanation style: no wisecracks (like "Congratulations, you've unlocked a new skill!"), no superfluous
   scenario descriptions (like "You walk into the office with a coffee in hand..."), and terms need
   explanation on first appearance.

## Output format
For each item give: pass/fail + specific location + revision suggestion
```

This Prompt is much better than the earlier "help me review it" — it clarifies what to check, how to check, and what output format. 

But if you actually put it to use, you'll soon run into some practical problems. Imagine: today you finish reviewing "Python Data Analysis in Practice," next week you review "Intro to Machine Learning," and next month there's "Deep Learning in Practice." Each time, you need to:

- **Find this Prompt**: it lives in your chat history, maybe in some document, or maybe only in your head
- **Copy-paste it into the new conversation**: every new session, you have to paste this big chunk of text all over again
- **Align wording with colleagues**: you wrote one version of the Prompt, your colleague wrote another, and the two of you have different requirements for "explanation style" — the review results aren't comparable
- **Remember what you changed last time**: last time you found the rule "terms need explanation on first appearance" important and added it — but to which version?

The root of these problems is: **the Prompt is session-level**. It only takes effect in the current conversation; when the conversation ends, the knowledge scatters. It's not an independent resource that can be stored, version-managed, and shared by a team. It's like writing your operating procedures on a sticky note — fine to use once yourself, but the note gets lost, others can't see it, and changes go unnoticed.

What you need is something else: a set of **reusable, file-based professional-knowledge modules** — written once, stored in the file system, loaded into the Agent's context on demand, without manually pasting every time.

## 2 Precipitating Review Experience

Since a Prompt scattered in chat history isn't handy, let's fix it in place. Next, in four steps, we'll gradually build a set of reusable review knowledge base.

### 2.1 From chat history to an independent file

First, solve the "can't find it" problem.

Digging through chat history for that Prompt every time you review is both troublesome and error-prone. The most direct improvement is: **save it as a Markdown file** in the project directory.

Use a script to create `course-review.md`:

```python
review_guide = """\
# Tutorial Review Guide

## Review Standards

### 1. Code executability
- Whether all code blocks can execute smoothly in a clean environment
- Whether there are missing dependencies (e.g. openpyxl is used but not installed)
- Whether there are undefined variables or path problems

### 2. Content accuracy
- Whether technical concepts and API usage are consistent with the latest docs
- Whether text descriptions and code implementations are consistent (says "use the mode," does the code really use the mode)
- Whether important terms have an explanation on first appearance

### 3. Learning curve
- Whether the arrangement of knowledge points follows a progressive design, whether there are jumps that are too large
- Whether core concepts have a hands-on part — the reader tries first, then learns the principle, rather than hearing the explanation first and then seeing the example
- Whether the opening includes a preface and course objectives

### 4. Explanation style

**No wisecracks**: no smart-alecky wisecracks, internet slang, or joke-style expressions. The course tone should be plain, professional, and direct.

| Unacceptable | Acceptable |
|-------|------|
| "Congratulations, you've unlocked a new skill! 🎉" | "At this point, you've mastered the basic usage of X." |
| "Doesn't it feel like cheating?" | "Compared with manual processing, this approach is clearly more efficient." |
| "This is like giving the model a third eye" | "This lets the model access external data sources" |

**No superfluous scenario descriptions**: scene introductions should be to the point — a sentence or two to explain the background and problem is enough; don't write novel-style buildup.

| Unacceptable | Acceptable |
|-------|------|
| "At nine on Monday morning, you walk into the office with a coffee in hand, sunlight spilling through the blinds onto your desk..." | "Your manager gave you a set of sales data and asked you to finish the analysis report this week." |

**Criterion**: if deleting a description doesn't affect the reader's understanding of the technical content at all, then that description is superfluous.

## Output Format

For each check give:
- Status: pass / fail / needs manual review
- Location: section name + cell number
- Note: specific problem description and revision suggestion
"""

with open("course-review.md", "w", encoding="utf-8") as f:
    f.write(review_guide)

print("Created course-review.md")
```

Now have the Agent review "Python Data Analysis in Practice" against this standard:

```python
async def main():
    toolkit = Toolkit()
    toolkit.register_tool_function(read_file)

    agent = ReActAgent(
        name="Course Reviewer",
        sys_prompt="You are an AI assistant that can help users complete various tasks.",
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
        max_iters=10,
    )

    agent.set_console_output_enabled(False)

    response = await agent(Msg("user",
        "Following the standards in course-review.md, review docs/Python数据分析实战.ipynb",
        "user"))

    print(response.get_text_content())

await main()
```

The problem is half solved: the file has a fixed location and won't get lost again; team members can also share the same file. But when you actually start adding details to it, new trouble arrives.

### 2.2 From a single file to a knowledge-base directory

But `course-review.md` will soon become very long. You'll find you need to add more details:

- Which pandas APIs are deprecated? (`append` is deprecated; you should use `concat`)
- What kind of scenario description counts as "superfluous"? Needs positive and negative examples
- To what degree should code comments be written?

If you stuff all of this into one file, it will balloon to dozens of pages, becoming hard to maintain instead.

A better approach is: **keep the main file lean, and split detailed content into sub-files**.

```
course-review/
├── README.md            # review-process overview (entry)
├── code-quality.md      # detailed checklist for code executability
├── content-accuracy.md  # detailed checklist for factual accuracy
├── style-guide.md       # positive and negative examples of explanation style
└── outdated-api.md      # pandas/numpy deprecated-API reference table
```

Below, use a script to split the original single file into this directory structure. The core idea is: `README.md` keeps only the review process and a directional index, while the specific checklists, style requirements, and API reference table each become their own file.

```python
import os

# Create the directory
os.makedirs("course-review", exist_ok=True)

# ---- 1. README.md: the lean entry file ----
# Only lists the review process and four directions, using links to point to sub-files
readme = """\
# Tutorial Review Guide

## Review Process

1. Extract the Notebook's table of contents to understand the overall chapter arrangement
2. Check section by section, comparing each against the following four directions
3. Aggregate the review results and output a structured report

## Review Directions

| Direction | Detailed rules |
|------|---------|
| Code executability | See [code-quality.md](code-quality.md) |
| Content accuracy | See [content-accuracy.md](content-accuracy.md) |
| Explanation style | See [style-guide.md](style-guide.md) |
| Deprecated API | See [outdated-api.md](outdated-api.md) |

## Output Format

For each check give:
- Status: pass / fail / needs manual review
- Location: section name + cell number
- Note: specific problem description and revision suggestion
"""

# ---- 2. code-quality.md: detailed checklist for code executability ----
code_quality = """\
# Code Executability Check

## Checklist

- [ ] Whether all code blocks can execute top to bottom in order in a clean environment
- [ ] Whether dependencies are complete (e.g. openpyxl is used but there's no `pip install` cell)
- [ ] Whether there are undefined variables or missing file paths
- [ ] Whether data files are provided with the course, or there's clear download guidance
- [ ] Whether long-running operations (model training, large-file downloads) have an expected-time hint

## Common Problems

| Problem | Example | Fix suggestion |
|------|------|---------|
| Implicit dependency | `import openpyxl` in code but not installed | Add `pip install openpyxl` in the environment-setup section |
| Hardcoded path | `pd.read_csv('/home/user/data.csv')` | Change to a relative path or provide a download script |
| Cell-order dependency | Cell 10 uses a variable only defined in Cell 15 | Adjust cell order to ensure top-to-bottom executability |
"""

# ---- 3. content-accuracy.md: detailed checklist for factual accuracy ----
content_accuracy = """\
# Content Accuracy Check

## Checklist

- [ ] Whether technical concepts and API usage are consistent with the latest official docs
- [ ] Whether text descriptions and code implementations are consistent (says "use the mode," does the code really use the mode)
- [ ] Whether important terms have a concise explanation on first appearance
- [ ] Whether the data in numbers, formulas, and charts matches the code output
- [ ] Whether external links are valid, and whether cited papers/docs note a version or date

## Common Problems

| Problem | Example | Fix suggestion |
|------|------|---------|
| Text-code mismatch | Text says "fill with the median," code uses `mean()` | Unify to the same method |
| Term without explanation | Uses "embedding" directly with no explanation | Add a parenthetical explanation on first appearance |
| Outdated API version | Uses `df.append()` | Replace per outdated-api.md |
"""

# ---- 4. style-guide.md: positive and negative examples of explanation style ----
style_guide = """\
# Explanation Style Guide

## Rule 1: No wisecracks

No smart-alecky wisecracks, internet slang, or joke-style expressions. The course tone should be plain, professional, and direct.

| Unacceptable | Acceptable |
|-------|------|
| "Congratulations, you've unlocked a new skill! 🎉" | "At this point, you've mastered the basic usage of X." |
| "Doesn't it feel like cheating?" | "Compared with manual processing, this approach is clearly more efficient." |
| "This is like giving the model a third eye" | "This lets the model access external data sources" |

## Rule 2: No superfluous scenario descriptions

Scene introductions should be to the point — a sentence or two to explain the background and problem is enough; don't write novel-style buildup.

| Unacceptable | Acceptable |
|-------|------|
| "At nine on Monday morning, you walk into the office with a coffee in hand, sunlight spilling through the blinds onto your desk..." | "Your manager gave you a set of sales data and asked you to finish the analysis report this week." |

**Criterion**: if deleting a description doesn't affect the reader's understanding of the technical content at all, then that description is superfluous.

## Rule 3: Learning curve

- Knowledge points follow a progressive arrangement; jumps can't be too large
- For core concepts, do first then explain the principle (try first, then explain)
- The opening includes a preface and course objectives
"""

# ---- 5. outdated-api.md: deprecated-API reference table ----
outdated_api = """\
# Deprecated-API Reference Table

When reviewing code, if you find any of the following deprecated APIs, mark it as "fail" and give a replacement suggestion.

## pandas

| Deprecated | Replace with | Deprecated in | Note |
|--------|--------|---------|------|
| `DataFrame.append()` | `pd.concat([df1, df2])` | 1.4.0 | append was removed in 2.0 |
| `DataFrame.swaplevel()` with no args | Explicitly pass `i, j` args | 1.5.0 | Future versions no longer support implicit args |

## numpy

| Deprecated | Replace with | Deprecated in | Note |
|--------|--------|---------|------|
| `np.bool` | `np.bool_` or `bool` | 1.20.0 | Built-in type alias removed |
| `np.int` | `np.int_` or `int` | 1.20.0 | Same as above |
| `np.float` | `np.float64` or `float` | 1.20.0 | Same as above |
| `np.object` | `np.object_` or `object` | 1.20.0 | Same as above |

> This table needs continuous maintenance — each time the library releases a new version, check the Deprecation section of the Release Notes and update.
"""

# ---- Write files ----
files = {
    "course-review/README.md": readme,
    "course-review/code-quality.md": code_quality,
    "course-review/content-accuracy.md": content_accuracy,
    "course-review/style-guide.md": style_guide,
    "course-review/outdated-api.md": outdated_api,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\u2705 Created {path}")

print(f"\nSplit complete; generated {len(files)} files in total.")
print("The original course-review.md can be archived or deleted.")
```

`README.md` only lists the review process and the four big directions; when you need to see details, you go read the corresponding sub-file. This keeps the entry concise while carrying rich enough expert knowledge.

The knowledge base's structure is now clear, but the review target itself also poses a challenge — that Notebook with nearly 300 cells: can the Agent read it all in one go?

### 2.3 Coping with long documents: segmented checking

There's another practical problem: the Notebook file may be very long. "Python Data Analysis in Practice" has nearly 300 cells, and stuffing it into the context all at once would get truncated.

An experienced reviewer won't read straight through from start to finish in one go — she'll first flip through the table of contents to understand the structure, then check section by section. You can use a script to help the Agent do the same.

**Method one: extract the table of contents**

Create a script to extract all Markdown headings from the Notebook:

```python
import os

os.makedirs("scripts", exist_ok=True)

extract_toc_code = '''\
import json
import sys

def extract_toc(notebook_path):
    """Extract all Markdown headings from a Jupyter Notebook, generating a TOC with cell numbers."""
    # An .ipynb is essentially a JSON file; the cells array contains all cells
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    toc = []
    for i, cell in enumerate(nb['cells']):
        # Only care about Markdown cells; skip code and output
        if cell['cell_type'] == 'markdown':
            # cell['source'] is a list of lines; join then scan line by line for headings
            source = ''.join(cell['source'])
            for line in source.split('\\n'):
                if line.startswith('#'):
                    # Record the cell number for later locating
                    toc.append(f"[Cell {i}] {line}")
    return '\\n'.join(toc)

if __name__ == '__main__':
    print(extract_toc(sys.argv[1]))
'''

with open("scripts/extract_toc.py", "w", encoding="utf-8") as f:
    f.write(extract_toc_code)

print("Created scripts/extract_toc.py")
```

Run the script to extract the table of contents of "Python Data Analysis in Practice":

```python
import subprocess

result = subprocess.run(
    ["python", "scripts/extract_toc.py", "docs/Python数据分析实战.ipynb"],
    capture_output=True, text=True
)
print(result.stdout)
```

The Agent can then first see the complete chapter structure, and then decide where to start reading closely.

**Method two: convert to Markdown for easier editing**

If you need to frequently modify the Notebook, you can use `jupytext` to sync between `.ipynb` and `.md`:

```python
%%bash
# Install
pip install jupytext

# Notebook -> Markdown
jupytext --to md docs/Python数据分析实战.ipynb

# After editing the Markdown, sync back to Notebook
jupytext --to ipynb docs/Python数据分析实战.md
```

The Markdown format is easier to search and edit with text tools.

> **Further reading: why not just stuff the whole file into the context?**
>
> The context windows of current mainstream models are getting longer (128K–1M tokens), so in theory the whole Notebook fits. But research shows the model's **ability to process information in the middle of the context drops noticeably** — this is called the **Lost in the Middle** effect. Even if the file fits, problems in the middle part are easily ignored. Segmented checking not only bypasses the window limit but also lets the Agent keep high-quality attention on each segment.

Put these scripts into the `course-review/` directory created in 2.2 as well:

```python
import os
import shutil

# Create the scripts sub-directory
os.makedirs("course-review/scripts", exist_ok=True)

# Move the TOC-extraction script in
if os.path.exists("scripts/extract_toc.py"):
    shutil.move("scripts/extract_toc.py", "course-review/scripts/extract_toc.py")

# Create the format-conversion script
convert_script = """\
#!/bin/bash
jupytext --to md "$1"
"""

with open("course-review/scripts/convert_format.sh", "w") as f:
    f.write(convert_script)

os.chmod("course-review/scripts/convert_format.sh", 0o755)

print("Integrated the helper scripts into the course-review/scripts/ directory")
```

Together with the files already created in 2.2, the complete directory structure is as follows:

```text
course-review/
├── README.md
├── code-quality.md
├── content-accuracy.md
├── style-guide.md
├── outdated-api.md
└── scripts/
    ├── extract_toc.py      # extract the Notebook TOC
    └── convert_format.sh   # jupytext format conversion
```

The knowledge base is getting more complete. But if you stuff the entire directory into the Agent every conversation, you're back to another problem.

### 2.4 Load on demand: don't stuff everything at once

Now you have a complete review knowledge base. But a new problem arises: if you stuff the entire directory into the Agent every conversation, the context gets crowded.

Recall the `README.md` created in 2.2 — its "review directions" table already uses Markdown links to point to sub-files:

| Direction | Detailed rules |
|------|---------|
| Code executability | See `code-quality.md` |
| Content accuracy | See `content-accuracy.md` |
| Explanation style | See `style-guide.md` |
| Deprecated API | See `outdated-api.md` |

This structure naturally supports loading on demand — after the Agent gets `README.md`, it only needs to read the corresponding sub-file based on the direction it's currently checking:

- When reviewing code quality → load `code-quality.md` and `outdated-api.md`
- When reviewing explanation style → load `style-guide.md`
- When handling a long Notebook → first run `extract_toc.py`, then check section by section

The Agent doesn't need to load all content up front; instead, based on the current checking stage, it reads the corresponding file on demand.

### 2.5 Comparison: before vs. after the transformation

The figure below shows the four-step evolution from "one-off Prompt" to "reusable knowledge base":

*(Figure: structured status feedback — tools output structured results such as JSON (e.g. {"status": "failed"}) so the agent can decide the next step precisely.)*

Let's review the changes these four steps brought:

| Before (one-off Prompt) | After (knowledge-base directory) |
|----------------------|------------------|
| Scattered in chat history | Stored in a fixed location, version-manageable |
| All content mixed together | Main file lean, detailed content split out |
| Notebook too long gets truncated | Extract TOC first, check section by section |
| Have to stuff all content every time | Load on demand, avoiding context crowding |
| Written by one person, inconsistent standards | Team shares the same file, collaboratively iterable |

Now you have a complete `course-review/` directory at hand — it's not a Prompt, but a set of **reusable, maintainable, team-collaborative expert knowledge base**.

Let's review the core takeaways of Chapters 1 and 2:

- **The limitation of a generic Prompt**: when the Agent reviews a tutorial with a generic standard, it misses the team's specific professional requirements — fine-grained standards like code-dependency completeness, text-code consistency, and explanation-style compliance, which a generic model has no way to know
- **The Prompt is session-level**: it only takes effect in the current conversation and can't be stored, version-managed, and team-shared
- **File-ization solves reuse**: save the review standard as an independent file, and team members share the same standard
- **Directory-ization solves maintenance**: keep the main file lean and split detailed content into sub-files, each doing its own job
- **Load on demand solves efficiency**: load the corresponding content based on the current checking stage, avoiding context crowding

But this approach is still "human-driven" — you need to manually tell the Agent which file to read and what process to follow. Is there a way to let the Agent know what to do on its own?

## 3 Agent Skills: Injecting Expert Knowledge into the Agent

### 3.1 The concept of a Skill

Recall what you did at the very start. Every time you had the Agent review a course, you had to re-describe the review standards, workflow, quality requirements, anti-pattern list... This information is essentially stable, yet you piece it together repeatedly in every conversation. Miss one checklist item and the review quality drops; hand it to a different person and you have to explain everything from scratch again.

This is exactly why you split that long one-off Prompt into the `course-review/` directory — you wanted to fix this stable knowledge in place and stop repeating it every time.

The thing you built is a **Skill**.

**A Skill is a modular functional unit that extends an Agent's capability.** Each Skill packages instructions, metadata, and optional resources (scripts, templates, etc.) together, and the Agent invokes it automatically when it encounters a matching task.

Look at the `CourseReviewSkill` you built:

```
course-review/
├── SKILL.md                # main instructions (entry)
├── code-quality.md         # detailed checklist for code executability
├── content-accuracy.md     # detailed checklist for factual accuracy
├── style-guide.md          # positive and negative examples of explanation style
├── outdated-api.md         # deprecated-API reference table
└── scripts/
    ├── extract_toc.py      # extract the Notebook TOC
    └── convert_format.sh   # jupytext format conversion
```

Here `SKILL.md` is the upgraded version of that `README.md` in 2.2 — the entry file is renamed from `README.md` to `SKILL.md` (a Skill-spec convention), while adding two parts not yet expanded in 2.2: more detailed workflow steps, and anti-patterns to avoid during review. Below is an excerpt:

```text
# CourseReviewSkill

## Review process
1. Extract the Notebook TOC to understand the overall chapter arrangement
2. Check section by section, comparing against the following directions:
   - Code executability (see [code-quality.md](code-quality.md))
   - Content accuracy (see [content-accuracy.md](content-accuracy.md))
   - Explanation style (see [style-guide.md](style-guide.md))
   - Deprecated API (see [outdated-api.md](outdated-api.md))
3. Aggregate the review results and generate a report per the output format

## Anti-pattern list
- ❌ Don't modify variable names or API version numbers in the code
- ❌ Don't skip any check item
- ❌ Don't introduce new technical concepts during the review

## Output format
For each check give: pass/fail/needs manual review + location + revision suggestion
```

Compared with the `README.md` in 2.2, there are two changes: one is that the review process is refined from a brief 3 steps into more actionable steps (each direction carries a link), and the other is the newly-added anti-pattern list — all precipitated from experience in later use.

Note the links in step 2 — this is **progressive disclosure**: the main file only gives the process framework, and the detailed checklists go in sub-files. Only when the Agent reaches the corresponding step does it read the document behind the link, neither wasting the context window nor missing details.

This design brings three benefits:

**No more re-explaining.** Review standards, workflow, anti-pattern list — once this stable knowledge is written into the Skill, it's fixed. No matter who uses it or how many times, the Agent executes by the same set of standards. Your preferences too: you like to first use `jupytext` to convert the Notebook to Markdown before reviewing, you like to output check results in a table — write it into the Skill, and you don't have to re-explain every time.

**No pollution of unrelated tasks.** The Agent automatically judges whether it needs this Skill based on the task. When you have it review a course, it loads `CourseReviewSkill`; when you have it write code, it won't stuff review rules into the context. Of course, you can also specify explicitly — e.g. tell the Agent "check this document against the course-review standard."

**No blowing up the context.** Even with the Skill activated, the Agent won't read all sub-files in one go. It first reads `SKILL.md` to get the process framework, and only when it reaches the "check technical-concept accuracy" step does it read `content-accuracy.md`. The context window always holds only the content the current step needs.

> **💡 The difference between Skill and RAG**
>
> You might ask: how is this different from RAG? Aren't they both supplementing information for the Agent?
>
> First, the problems they solve differ. RAG solves "the model doesn't know a certain fact" — such as the content of a document or the parameters of a product; Skill solves "the model doesn't know how to do something" — such as what process to follow when reviewing a course, or how to handle a deprecated API.
>
> Second, from the context perspective, the way information enters the context also differs:
>
> **RAG is "retrieve-inject."** After the user asks, the system slices the long document into chunks, finds the few most relevant fragments through semantic retrieval, and stuffs them directly into the context. The model gets a pile of factual material and uses it to answer the question. The whole process is one-off — inject after retrieving, generate after injecting.
>
> **Skill is "select-expand."** When the Agent starts, the descriptions of all available Skills (similar to tool descriptions) are fully presented to it. The Agent judges, based on the current task, whether it needs and which Skill it needs. Only after choosing to activate a Skill does it read its detailed content — and progressively, reading the corresponding sub-file only when it reaches that step.

*Figure (translated): the structure of a Skill.*

```text
[SKILL.md]
   ├─ Frontmatter (name / description): decides "whether to use it"
   ├─ Markdown body (workflow / rules / templates): decides "how to do it"
   └─ External resource files: loaded on demand (scripts, checklists, references)
```

### 3.2 The structure of a Skill

You've already seen a simple Skill — `CourseReviewSkill`, with `SKILL.md`, a few checklists, and helper scripts. Now let's look at what a formal Skill should look like.

Recall how a Skill works: when the Agent starts it sees all Skills' descriptions, judges which the current task needs, and only reads the detailed content after selecting. This means a Skill must solve two problems at once: **let the Agent quickly judge "whether to use it"**, and **tell the Agent "specifically how to do it."**

`SKILL.md` is designed for exactly this. It consists of two parts — the YAML frontmatter solves the first problem, and the Markdown body solves the second:

```text
---
name: course-review
description: |
  Review the technical accuracy, code correctness, and teaching quality of course content. Use this skill when the user asks to review, audit, or evaluate an existing course or training material.
---

# Course Review Skill

## Quick start
1. Run code validation: `python scripts/validate_code.py`
2. Check terminology against [CHECKLIST.md](CHECKLIST.md)
...
```

The part wrapped by `---` is the YAML frontmatter. Before the Agent has even decided whether to use this Skill, it can already see the information here — just like browsing books in a bookstore, you first read the back-cover blurb before deciding whether to read.

**`name`**: the Skill's unique identifier. The user can explicitly invoke it via `/course-review`, so picking a self-evident name matters more than anything.

**`description`**: this is the key to whether a Skill can be correctly triggered. When facing a user instruction, the Agent needs to pick the right one out of possibly hundreds of Skills — and what it relies on is each Skill's description.

A good description needs to answer two questions:
1. **What this Skill does** (function description)
2. **When it should be triggered** (trigger conditions)

```text
# ❌ Vague description
description: Handle course-related tasks.

# ✅ Clear description
description: |
  Review the technical accuracy, code correctness, and teaching quality of course content. Use this skill when the user asks to review, audit, or evaluate an existing course or training material.
```

The problem with the first version is: what does "handle course-related tasks" mean? Writing a course, reviewing a course, and translating a course all count, and the Agent simply can't judge whether to trigger it. The second version first states the function (review the technical accuracy, code correctness, and teaching quality of course content), then clarifies the trigger conditions (use when the user asks to review, audit, or evaluate a course), so the Agent can precisely match the user's intent.

The figure below shows the complete structure of SKILL.md — the YAML frontmatter solves "whether to use it," the Markdown body solves "how to do it," and external resource files load on demand:

*(Figure: the agent first reads a Skill's description, then reads its detailed content, and only loads each sub-file when execution reaches that step.)*

**Why do we need external resource files?**

The Markdown body defines the Skill's core instructions — workflow, key rules, review standards. But some content, placed in the main file, would make it bloated: 10 writing-style guides, a 200-line checklist, a deprecated-API reference table... These are all detailed reference materials the Agent doesn't need to read fully up front.

The solution is to split them into independent files, with SKILL.md keeping only the links. Take the `course-writer` Skill as an example:

```
course-writer/
├── SKILL.md                          # core instructions: writing process, quality standards
└── guides/                           # external resources: 10 detailed writing-style guides
    ├── 01-chapter-structure.md       #   chapter-opening structure
    ├── 02-scenario-driven.md         #   scenario-driven narrative
    ├── 05-code-examples.md           #   code-example conventions
    └── ...
```

SKILL.md uses a table to list the purpose of each guide, and when the Agent writes a course it reads the corresponding `05-code-examples.md` based on the current stage (e.g. currently writing code examples), rather than loading all 10 at once. The benefit is: SKILL.md stays concise and readable, the context window won't be filled up by reference materials, and the Agent can find details anytime it needs them.

**Why do we need local scripts?**

Some judgments shouldn't be left to the model to "guess." For example, "can this code run normally" — the model might miss an import statement, or guess that some version of an API is still usable. But a script can directly execute the code and give a deterministic result.

```
course-testing/
├── SKILL.md                          # core instructions: review process, check standards
├── CHECKLIST.md                      # external resource: review checklist
└── scripts/
    └── validate_code.py              # local script: automatically execute code blocks and report results
```

When the Agent reaches the code-testing stage, it directly runs `python scripts/validate_code.py` and gets a precise result like "code block 3 errors: ModuleNotFoundError: No module named 'sklearn'," rather than reading the code line by line itself and guessing whether it runs. **Let the model do what it's good at (understanding, reasoning, generating), and let scripts do what they're good at (executing, validating, computing).**

### 3.3 How to write a high-quality Skill

Knowing a Skill's structure is one thing; writing a truly usable Skill is another. A Skill with a complete structure but vague instructions, versus a carefully-polished Skill, differ hugely in effect — the former may make the Agent repeat the same mistakes, while the latter lets the Agent stably deliver high-quality results.

Writing a good Skill essentially means going through five steps: judge whether it's worth doing → extract what to write → write good instructions → configure good tools → validate and iterate. Each step solves a different problem, and skipping any step plants a landmine down the line.

*Figure (translated): the Skill development flow — each step solves a different problem.*

```text
[1. Judge whether it is worth doing] -> [2. Design the workflow] -> [3. Write AI-friendly scripts] -> [4. Validate and iterate]
```

#### Step 1: judge whether it's worth doing

Encapsulating a Skill has costs — designing the structure, writing the instructions, testing and iterating. If the task itself is very simple or only runs once, these costs are wasted. Before you start, ask yourself three questions:

**Does this task have "expert intuition"?**

> "Look for those stages where 'an expert can do it right by intuition, but a novice often misses the edge cases.'"

Course review is a typical example. A senior instructional designer can tell at a glance that "this code example is too complex for a beginner," but a novice often doesn't realize it. This kind of "tacit knowledge" is exactly what a Skill should most capture.

**Is this task complex enough?**

> "Operations that can be completed via GUI within 3 steps are strictly forbidden from being encapsulated as a Skill."

If a task is simple enough (e.g. "translate this text into English"), describing it directly in natural language is enough; there's no need to go to great lengths to create a Skill. Using AI for the sake of using AI is one of the most common pitfalls in engineering practice.

**Will this task be executed repeatedly?**

The value of a Skill lies in reuse. If a task will only be executed once, the input-output ratio of encapsulating it is very low. But if your team has to review 20 courses every week, then spending a day polishing a `CourseReviewSkill` is very worthwhile.

Only when all three questions are answered "yes" is it worth encapsulating. This judgment helps you avoid the most common waste — not that the Skill is written poorly, but that it shouldn't be written at all.

#### Step 2: extract what to write

After deciding to write, many people directly list the operational steps — "step one do X, step two do Y." But such a Skill is no different from an ordinary Prompt.

The truly valuable content is the **tacit knowledge that experts know but find hard to articulate**. The core work you need to do is to make it explicit:

- Extract the expert's **decision tree** rather than mere steps — "under what conditions choose option A, under what conditions choose option B"
- Inject **anti-pattern checks** — "which pits absolutely must not be stepped into"

A Skill that only tells the Agent "what to do" is incomplete. An excellent Skill also tells the Agent "what not to do" and "why."

After extracting the knowledge, how do you present it to the model? There are two efficient ways:

**Template mode: standardize the output format**

If your task needs standardized output (review reports, changelogs, test summaries, etc.), provide an output template directly in the Skill. A template is more precise than a text description; the model doesn't need to "guess" what format you want.

```text
## Output format

Generate the review report per the following template:

## Review report: {course name}

### Overview
- Overall quality: {1-5}/5
- Code correctness: {pass count}/{total} code blocks pass
- Key issues: {count} found

### Key issues
{list one by one:}
- **[Line {n}]**: {problem description}
  - Severity: {severe|normal|minor}
  - Fix suggestion: {suggestion}

### Improvement suggestions
1. {suggestion content}
```

The Agent will strictly generate output per this template, ensuring each review report has a consistent structure and complete information.

**Examples mode: use examples instead of descriptions**

Sometimes it's hard to precisely describe the style and level of detail you expect in words. In this case, a good input/output example is more effective than a page of text description.

```text
## Style example

### Input example
> Course topic: Python list comprehensions

### Output example
> **Pain-point introduction**: have you ever written code like this — a 5-line for loop just to
> filter the even numbers out of a list? Python offers a more elegant way.
>
> **Core concept**: the syntax of a list comprehension is `[expression for item in iterable if condition]`...
>
> **Comparison**:
> ```python
> # Traditional (4 lines)
> result = []
> for x in range(10):
>     if x % 2 == 0:
>         result.append(x)
>
> # List comprehension (1 line)
> result = [x for x in range(10) if x % 2 == 0]
> ```
```

This example implies a lot of information: you expect the "pain-point introduction → core concept → comparison" narrative structure, the code should have comments, and comparison should be used to highlight the advantage. If described in pure text, this might take several paragraphs and still not be clear.

The two modes can be combined: Template controls structure, Examples control style.

#### Step 3: write good instructions

With content in hand, next is how to write it. The context window is a limited shared resource — your Skill has to share this space with the System Prompt, conversation history, and other Skills' metadata. Write too much and the model can't grasp the key points; write too rigidly and flexible tasks get constrained; write too long and a single file can't hold it. These three problems correspond to three principles.

**Concise: every sentence must be worth its token cost**

Before writing each paragraph, ask yourself: does the model really need this explanation? Can I assume the model already knows this?

Look at a concrete example — how to instruct the Agent to extract PDF text:

**❌ Redundant version (~150 tokens)**:

```text
## Extract PDF text

PDF (Portable Document Format) is a common file format containing text, images, and other content.
To extract text from a PDF, you need to use a library. There are many PDF-processing libraries to choose from,
but we recommend pdfplumber because it's easy to use and handles most scenarios.
First, you need to install it via pip. Then you can use the following code...
```

**✅ Concise version (~50 tokens)**:

```text
## Extract PDF text

Use pdfplumber to extract text:

```
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

The concise version assumes the model already knows what a PDF is and how libraries work. It only provides the information the model **truly needs**: which tool to use and how to call it. The 100 tokens saved are left for places that really need explanation.

**Freedom matching: the degree of constraint should match the task's risk**

Different tasks need different degrees of instruction precision. A database-migration script must strictly follow each step, while a code review can let the Agent play freely. If you use the same degree of constraint everywhere, either the places that should be strict are too loose (accidents happen), or the places that should be flexible are too rigid (limiting the model's ability).

| Freedom | Applicable scenario | Example |
|--------|----------|------|
| **High** (text instructions) | Multiple methods all work, relying on contextual judgment | Code review, content analysis |
| **Medium** (pseudocode/parameterized) | There's a preferred pattern, allowing moderate variation | Report generation, config tasks |
| **Low** (precise script) | The operation is fragile and must be strictly followed | Database migration, deployment scripts |

Think of the model as a robot exploring a path. **Narrow bridge + cliff** (database migration): there's only one safe path, so you need to provide precise guardrails (low freedom). **Open field** (code review): multiple paths all reach the destination, so you only need to give a rough direction (high freedom).

**Low-freedom example**:

```text
## Database migration

Strictly execute the following script:

```
python scripts/migrate.py --verify --backup
```

Do not modify the command or add extra arguments.
```

**High-freedom example**:

```text
## Code-review process

1. Analyze the code structure and organization
2. Check for potential bugs and edge cases
3. Propose improvements for readability and maintainability
4. Verify compliance with project conventions
```

**Progressive disclosure: keep the main file lean, load details on demand**

When a Skill contains a lot of reference material, don't stuff all of it into SKILL.md — you've already seen this principle. Here's an important practical detail to add: **keep a flat structure, avoid deep nesting**.

```
# ❌ Deep nesting: SKILL.md → config.md → rules/
course-review/
├── SKILL.md              → "see config.md"
├── config.md             → "rule definitions in the rules/ directory"
└── rules/
    ├── code_quality.md   # the model may never reach here
    └── style_guide.md

# ✅ Flat structure: SKILL.md directly links all resources
course-review/
├── SKILL.md              → directly links each file below
├── CHECKLIST.md
├── STYLE_GUIDE.md
└── scripts/
    └── validate_code.py
```

Why? When the reference levels are too deep, the model may only preview an intermediate file with `head -100` rather than reading it fully, causing key information to be lost in the passing chain. A flat structure ensures the model needs only "one step" to access any needed resource.

#### Step 4: configure good tools

We've already covered why scripts are needed — so the model doesn't have to "guess." But the **output quality** of a script directly determines whether the Agent can use it well. A script that outputs `"Error: exit code 1"` and one that outputs structured diagnostic information are worlds apart for the Agent.

Let's first look at workflow design, then at how to write the tools themselves.

**Design a traceable workflow**

Complex tasks need a clear workflow. Providing the Agent with a traceable checklist significantly improves execution reliability.

```text
## Course-review workflow

Copy this checklist and track your progress:

```
Review progress:
- [ ] Step 1: extract all code blocks
- [ ] Step 2: validate each code block
- [ ] Step 3: check technical accuracy
- [ ] Step 4: evaluate the difficulty gradient
- [ ] Step 5: verify style compliance
- [ ] Step 6: generate the review report
```

**Step 1: extract all code blocks**
Scan the course document and extract each code block...

**Step 2: validate each code block**
Run each code block. If validation fails:
- Record the error message
- Mark as "needs fixing"
- Continue to the next code block
```

**Feedback-loop pattern**

For tasks that need validation, establish a "run → check → fix → repeat" feedback loop:

```text
## Validation loop

1. Run the validator: `python scripts/validate.py`
2. If errors are found:
   - Read the error message
   - Fix the problem
   - Run the validator again
3. Only continue after validation passes
```

This pattern gives the Agent a chance to self-correct, rather than being done in one shot.

**High-risk operations: validate the plan before executing**

The feedback loop is "check after doing," but for high-risk operations (batch file modifications, database migrations, etc.), you may want the Agent to **validate the plan before executing**.

```text
## Batch-update workflow

Before making any changes:

1. Generate a change plan in JSON format:
   ```
   python scripts/plan_changes.py --output changes.json
   ```
2. Validate the plan:
   ```
   python scripts/validate_plan.py changes.json
   ```
   - Verify no files will be deleted
   - Verify all target paths exist
   - Verify the changes are reversible
3. Only after validation passes, execute:
   ```
   python scripts/apply_changes.py changes.json
   ```
```

The core difference from the feedback loop: **errors are intercepted before execution**, rather than discovered after.

*(Figure: AI-friendly scripts — unlike the feedback loop, errors are intercepted before execution rather than discovered after.)*

**Write AI-friendly scripts**

The workflow is designed; how should the script itself be written? The core idea: **don't kick the problem back to the model**. When a tool returns a vague error message, the model can only guess the cause; when a tool returns a structured diagnostic result, the model can precisely decide the next step. Four key principles:

*Figure (translated): four-step evolution from a one-off prompt to a reusable knowledge base.*

```text
[One-off Prompt] -> [Fixed template] -> [Script/checklist] -> [Knowledge-base directory (reusable Skill)]
```

**Structured status feedback** — output JSON rather than free text. The Agent receiving `"status": "failed"` can immediately enter the fix flow; receiving "check complete, some problems found" still needs to first understand what that sentence means.

**Error messages contain fix clues** — the Agent doesn't need a stack trace; it needs "what's wrong + how to fix it."

| Practice | Example |
|------|------|
| **Bad** | `FileNotFoundError: No such file or directory: 'config.yaml'` |
| **Good** | `{"error": "CONFIG_NOT_FOUND", "file": "config.yaml", "suggestion": "Please create config.yaml in the project root; refer to config.example.yaml", "fallback_used": true}` |

The bad version only tells the Agent "an error occurred"; the good version tells the Agent "what error occurred, how to fix it, and whether there's currently a fallback."

**Degrade gracefully rather than crash** — a tool should, where possible, provide default values and continue rather than crashing directly. After receiving a crash the Agent can only guess the cause; after receiving a degradation notice it can decide precisely.

```python
# Bad: crash directly
def load_config(path):
    with open(path) as f:  # FileNotFoundError -> the Agent only sees a stack trace
        return json.load(f)

# Good: degrade gracefully, return structured status
def load_config(path):
    result = {"status": "ok", "warnings": []}
    if not os.path.exists(path):
        result["status"] = "degraded"
        result["warnings"].append(f"Config '{path}' not found, using defaults")
        return {**result, "config": DEFAULT_CONFIG}
    # ... normal loading logic
```

**Idempotent and safe** — the Agent may call the same tool multiple times (especially in a feedback loop). A tool should support repeated execution without side effects.

| Scenario | Non-idempotent (dangerous) | Idempotent (safe) |
|------|---------------|-------------|
| File writing | Each call appends content, causing duplication | Clear first then write, or check before writing |
| Database operation | Each call INSERTs a new record | Use UPSERT or check whether it already exists first |
| API call | Each call creates a new resource | Use an idempotency key to ensure a repeated request takes effect only once |

Combining these four principles, look at a complete comparison — take `validate_code.py` as an example:

```python
# ❌ Ordinary version: human-facing output
def validate(file_path):
    errors = run_checks(file_path)
    if errors:
        print(f"Found {len(errors)} issues:")
        for e in errors:
            print(f"  - Line {e['line']}: {e['message']}")
        sys.exit(1)
    print("\u2705 All passed!")
```

```python
# ✅ AI-friendly version: structured output + fix clues + graceful degradation
def validate(file_path):
    result = {
        "status": "passed",
        "file": file_path,
        "errors": [],
        "warnings": [],
        "summary": ""
    }
    if not os.path.exists(file_path):
        result["status"] = "error"
        result["summary"] = f"File '{file_path}' not found"
        result["suggestion"] = "Please check the file path and retry"
        print(json.dumps(result, ensure_ascii=False))
        return

    errors = run_checks(file_path)
    if errors:
        result["status"] = "failed"
        result["errors"] = [
            {
                "line": e["line"],
                "rule": e["rule"],
                "message": e["message"],
                "fix_hint": e.get("fix_hint", "")
            }
            for e in errors
        ]
        result["summary"] = f"{len(errors)} issues found, {sum(1 for e in errors if e.get('fix_hint'))} auto-fixable"
    else:
        result["summary"] = "All checks passed"

    print(json.dumps(result, ensure_ascii=False))
```

When the Skill's feedback loop calls the AI-friendly version of the tool, the Agent can directly parse the JSON, fix issues one by one per `fix_hint`, then run validation again — the whole process needs no human intervention.

#### Step 5: validate and iterate

The Skill is written; how do you know if it's good? Reading it through yourself isn't enough — you think it's clearly written, but the model may understand something completely different. The most effective way is to **develop in collaboration with AI**.

**The "dual-Agent" pattern**

- **Agent A (Designer)**: helps you design and refine the Skill's instructions
- **Agent B (User)**: tests the Skill in real tasks

**The development flow has three stages**:

*Figure (translated): Skill development flow with two agents and three stages.*

```text
[Agent A (Developer): writes the Skill's instructions] ──► [Agent B (User): tests the Skill in real tasks]

Stage 1: establish an evaluation baseline (Agent A completes a real task without any Skill)
Stage 2: Agent A develops the Skill, Agent B tests and measures the improvement
Stage 3: iterate until the Skill passes the quality bar
```

**Stage 1: establish an evaluation baseline.** First use Agent A to complete a real task (without any Skill). Record where it made mistakes and where you had to repeatedly correct it, and pick the 3 most typical failure scenarios as evaluation cases. **Have the evaluation first, then write the Skill** — otherwise all subsequent optimization relies on "feeling."

**Stage 2: extract the Skill.** After the task is done, have Agent A help you summarize: "which information did you provide repeatedly?" Organize this information into a first draft of the Skill.

**Stage 3: test and iterate.** Have Agent B (a brand-new session) load this Skill and execute the evaluation cases from Stage 1. Compare the outputs: what improved? What's still unsolved? Bring the observations back to Agent A to improve the Skill, and repeat the test until Agent B can stably pass all evaluation cases.

This "evaluate-improve-validate" loop is the most effective way to polish a Skill. The evaluation cases run through the entire development process, providing an objective measure for each round of iteration. This idea is expanded more systematically in [Lesson 3.6 "Evaluation-Driven Agent Development"](./3_6_用评测驱动Agent开发.ipynb).

## 4 Letting Your Agent Use and Generate Skills

So far, you've manually completed the whole process of a Skill from design to iteration: using the review experience precipitated in Chapter 2, you distilled a checklist and in Chapter 3 encapsulated it into the `course-review/` directory structure, then repeatedly polished the instructions through the "dual-Agent" pattern. But this Skill is still just a set of Markdown files lying in the file system — how does the Agent discover it, load it, and invoke it in a real task?

### 4.1 Loading a Skill in AgentScope

The good news is you don't need to write the loading logic yourself. The AgentScope framework already has built-in support for the Skill directory structure — besides registering ordinary tool functions, its `Toolkit` class also provides a `register_agent_skill` method, which can directly read a Skill directory (containing SKILL.md and related resource files), automatically parse the metadata, and generate a prompt the Agent can use.

Before registering, one preparatory step is needed: `register_agent_skill` requires the entry file to be named `SKILL.md` (not the `README.md` created in 2.2), and the top of the file must contain YAML frontmatter — the framework extracts `name` and `description` from it to generate the Skill prompt visible to the Agent.

The script below upgrades the `README.md` from 2.2 into a spec-compliant `SKILL.md`: it adds YAML frontmatter before the original content, then renames the file.

```python
import os

# Read the README.md created in 2.2
with open("course-review/README.md", "r", encoding="utf-8") as f:
    original_content = f.read()

# Add YAML frontmatter
frontmatter = """\
---
name: course-review
description: |
  Review the technical accuracy, code correctness, and teaching quality of course content.
  Use this skill when the user asks to review, audit, or evaluate an existing course or training material.
---

"""

with open("course-review/SKILL.md", "w", encoding="utf-8") as f:
    f.write(frontmatter + original_content)

# Delete the old entry file
os.remove("course-review/README.md")

print("Upgraded README.md to SKILL.md (with YAML frontmatter)")
```

**Step 1: register the Skill and view the generated Prompt**

```python
from agentscope.tool import Toolkit

# 1. Register the tool function (reuse read_file defined in Chapter 1)
toolkit = Toolkit()
toolkit.register_tool_function(read_file)

# 2. Register the Skill: pass in the directory path containing SKILL.md
toolkit.register_agent_skill("course-review")

# 3. View the Skill prompt the framework generates for the Agent
print(toolkit.get_agent_skill_prompt())
```

The framework automatically read the YAML frontmatter of `SKILL.md`, extracted `name` and `description`, and generated a concise prompt. The prompt tells the Agent "there's a Skill here; read SKILL.md when you need to use it" — rather than stuffing the entire file content into the system prompt.

**Step 2: integrate into ReActAgent and execute the review**

In 2.3, `jupytext` was already used to convert the Notebook into Markdown format. The `.md` file strips the JSON metadata and cell outputs, is far smaller than the `.ipynb`, and the Agent reads it faster and consumes fewer tokens. Here we directly review the converted `.md` file:

```python
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel

reviewer = ReActAgent(
    name="CourseReviewer",
    sys_prompt="You are a course-quality reviewer.",
    model=DashScopeChatModel(
        model_name="qwen-plus",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
    ),
    formatter=DashScopeChatFormatter(),
    toolkit=toolkit,  # the Skill prompt is automatically appended to the system prompt
    memory=InMemoryMemory(),
    max_iters=12,
)

reviewer.set_console_output_enabled(False)

# Review the converted Markdown file — smaller and faster to respond
response = await reviewer(Msg("user", "Review docs/Python数据分析实战.md", "user"))
print(response.get_text_content())
```

This time the Agent won't give a perfunctory conclusion like "overall not bad, suggest publishing." It will first read `SKILL.md` via `read_file` to get the workflow framework, then execute item by item — reading `code-quality.md` when checking code, `content-accuracy.md` when verifying accuracy, `style-guide.md` when proofreading style, and finally generating a structured report per the output-format template.

*(Figure: three design decisions — inject only the Skill's description rather than its full text (context window is a scarce resource), load sub-files on demand, and rely on structured outputs.)*

**Three design decisions**

> **Why inject only the description rather than the full text?** The context window is a shared resource. The framework injects only the `description` (a few dozen tokens) into the system prompt, telling the Agent this Skill's existence and purpose. The complete workflow, anti-pattern list, etc. are loaded by the Agent on demand via `read_file` when it decides to use the Skill.
>
> **Why does the Agent need a file-reading tool?** This is the core of the Skill mechanism: the Agent first judges from the `description` whether it needs this Skill, then reads `SKILL.md` for detailed instructions, and reads sub-files (such as `style-guide.md`) when it needs more detail. This is the framework-level implementation of progressive disclosure.
>
> **Why is the quality of the `description` field key?** When the Agent is equipped with multiple Skills, it judges from the `description` which Skill the current task should use. A vague description (like "handle course-related tasks") causes matching failures; a specific description (stating what it does and when it triggers) ensures correct activation.

> 📚 **Further reading**: for the complete documentation of AgentScope's Skill mechanism, see [Task Agent Skill](https://doc.agentscope.io/tutorial/task_agent_skill.html), which contains more registration methods and advanced usage.

### 4.2 Letting the Agent auto-generate a Skill

Manually writing a Skill is a necessary learning process, but once you're proficient, you can have the Agent assist with the first draft. The `resources/2_6/skill-creator/` directory provides a `skill-creator` Skill, trimmed down from an open-source version. The original targets a complete Coding Agent workflow; we kept the core writing guidance — intent capture, requirement research, SKILL.md writing conventions, progressive disclosure — and removed environment dependencies like the CLI toolchain.

**Load skill-creator and generate a new Skill**

```python
from agentscope.tool import Toolkit, ToolResponse
from agentscope.message import TextBlock

# Define a write-file tool (symmetric with Chapter 1's read_file)
async def write_file(path: str, content: str) -> ToolResponse:
    """Write content to the file at the given path. Auto-create the directory if it doesn't exist."""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return ToolResponse(content=[TextBlock(type="text", text=f"Written to {path}")])

# 1. Register the tools and the Skill
#    read_file lets the Agent read SKILL.md to get the creation guide
#    write_file lets the Agent write the generated Skill to files
toolkit = Toolkit()
toolkit.register_tool_function(read_file)
toolkit.register_tool_function(write_file)
toolkit.register_agent_skill("resources/2_6/skill-creator")

# 2. Create the Skill-generation Agent
creator = ReActAgent(
    name="SkillCreator",
    sys_prompt="You are an Agent Skill designer.",
    model=DashScopeChatModel(
        model_name="qwen-plus",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
    ),
    formatter=DashScopeChatFormatter(),
    toolkit=toolkit,
    memory=InMemoryMemory(),
    max_iters=12,
)

# 3. Describe the requirement in natural language; the Agent auto-generates the Skill
creator.set_console_output_enabled(False)

response = await creator(Msg(
    "user",
    "Help me create a Skill for reviewing REST API documentation. "
    "It should check: 1. whether all endpoints have example requests and responses; "
    "2. whether error codes are explained; 3. whether parameters have type annotations.",
    "user",
))
print(response.get_text_content())
```

The Agent will generate a complete `api-doc-review/` directory, containing a spec-compliant `SKILL.md` and a checklist.

However, this is acceleration, not replacement. You still need to understand the design principles from Chapter 3 to judge whether the Agent's generated content is reasonable. An expert using `skill-creator` can quickly produce a high-quality Skill, while a novice who doesn't understand the design principles will struggle to produce a usable result even with `skill-creator`.

> 💡 **Tip**: the generated Skill draft must be validated with the earlier "dual-Agent" evaluation flow. Auto-generation only solves the "write it out" problem; "whether it's written correctly" still needs evaluation-driven iteration.

### 4.3 The Skill marketplace: reusing the community's expert knowledge

The previous two sections introduced how to register and generate self-built Skills in AgentScope. In the broader Coding Agent ecosystem, the community has already formed mature Skill-sharing platforms.

**Discovering Skills**

Suppose you're developing a TypeScript project and want to see if there's a ready-made code-convention Skill. The `skills find` command supports searching by keyword:

```text
# Search by keyword
npx skills find typescript

# Example output:
# Install with npx skills add <owner/repo@skill>
#
# vercel-labs/agent-skills@typescript-best-practices
# https://github.com/vercel-labs/agent-skills/tree/main/skills/typescript-best-practices
#
# acme/skills@typescript-linter
# https://github.com/acme/skills/tree/main/typescript-linter
```

Running `npx skills find` without arguments enters an interactive fuzzy-search interface, suited to exploratory scenarios where you're not yet sure of the keywords. After finding a Skill of interest, clicking the link lets you view the full content and security-audit rating on the relevant platform.

**Installing and using**

```text
# Install a specific Skill
npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices

# Update all installed Skills
npx skills update
```

After installation, the Skill files are downloaded into the project directory. Coding Agents (such as Cursor, etc.) automatically read and follow the guidance in them. Each Skill is essentially a set of Markdown files, exactly the same structure you learned in Chapter 3. Before installing, be sure to check the security-audit rating on the relevant platform's detail page — although a Skill is just Markdown files, the instructions in it directly affect the Agent's behavior.

**The division of labor between community Skills and self-built Skills**

| Scenario | Recommended approach |
|------|---------|
| General technical best practices (React performance optimization, code conventions) | Community Skill |
| Mature industry-standard processes (security audit, SEO optimization) | Community Skill |
| Enterprise-internal business processes and quality standards | Self-built Skill |
| The team's specific code conventions and architecture agreements | Self-built Skill |
| A domain expert's tacit knowledge (like this chapter's course-review Skill) | Self-built Skill |

The two aren't mutually exclusive: community Skills cover general technical capabilities, self-built Skills encapsulate business-specific expert knowledge, and combining them works best.

**Precautions when using**

- **Avoid too many Skills**: installing too many Skills fills up the system prompt and instead dilutes the attention weight of the core instructions
- **Watch version matching**: after the tools or frameworks a Skill depends on are updated, the commands and paths in the Skill may be outdated
- **Reasonable expectations**: a Skill raises the floor (keeps the Agent from making low-level mistakes), not the ceiling (makes the Agent produce results beyond expert level)

### 4.4 Section recap

This section expanded on "using" Skills at three levels:

1. **Registering and loading** (4.1): AgentScope's `register_agent_skill` method turns a Skill directory into a prompt the Agent can use; the framework injects only the `description` rather than the full text, and the Agent reads the detailed instructions on demand — the framework-level implementation of progressive disclosure.
2. **Auto-generation** (4.2): with the "meta-Skill" `skill-creator`, the Agent can generate a Skill draft from a natural-language requirement, but the generated result still needs validation through the evaluation flow.
3. **Community reuse** (4.3): relevant platforms provide ready-made general Skills, complementing self-built Skills — the community covers general capabilities, self-built ones encapsulate business knowledge.

## 5 When Skills Meet the Team

### 5.1 One person's success, ten people's chaos

In Part 4 you successfully built `CourseReviewSkill`, which helped you shorten course-review time from 2 hours to 20 minutes. Your manager was pleased and asked you to roll out this Skill to the entire instructional-design team — 10 people. You sent the SKILL.md file to the group chat with a brief usage note.

A month later, problems came one after another.

**Version chaos**: you updated the scoring weights based on the latest course standard, but 3 colleagues were still using the old version of the Skill. The same course was reviewed with contradictory conclusions — your report says "reasonable structure," your colleague's says "improper chapter division." The team had to spend half a day troubleshooting before finding it was a Skill-version inconsistency.

**Wrong modification**: an intern felt the rule "avoid using `print()` for debugging" in SKILL.md was too strict and changed it on their own to "allow using `print()` during the development stage." As a result, the Agent began marking all `print()` debug code as "compliant," and it wasn't discovered until three weeks later.

**Knowledge gap**: you took a two-week vacation, and the team hit 3 review edge cases — "do comments in code examples count as teaching content?" "does referencing external API docs require checking link validity?" — and no one could answer, because this judgment logic existed only in your experience and wasn't written into the Skill.

These three problems have one thing in common: `CourseReviewSkill` ran well as one person's work, but it wasn't designed for team collaboration.

### 5.2 Naive patching: why "just send it in the group chat" doesn't work

Facing these problems, you might think of a few intuitive patch solutions.

**Unified storage location**. Put the Skill file on a shared drive so everyone gets it from the same place. But problems follow: who has permission to modify this file? If all 10 people can change it, that's the same as no one being responsible — anyone's casual "quick tweak" may affect the whole team's review results.

**Send a usage-instruction document**. Write a detailed operation guide explaining how to use the Skill and precautions. But the document and the Skill are separate; two weeks later the Skill has iterated and the document still stays at the old version. The more detailed the document, the faster it becomes outdated.

**Have one person responsible for all modifications**. Any change must go through you. This does guarantee quality, but you become the bottleneck — the team's 10 requests queue up waiting for you, and you're not an expert in every review domain, so for some improvements you lack the ability to make the right judgment.

The fundamental reason these patch solutions fail is: a Skill isn't an ordinary config file, but an executable asset encapsulating expert knowledge. It directly determines the Agent's behavior and output quality. Managing this kind of asset needs clear ownership and an engineered lifecycle — which is exactly how software engineering has solved similar problems for decades.

From another angle, the true value of a Skill is as a **capability amplifier**: a senior instructional designer can only review 10 courses a week, but after she encapsulates her review experience into a Skill, the 10 junior members on the team can all invoke it — her professional ability is replicated at scale. But to make this amplifier run stably in a team, you need to solve three problems: ownership, collaboration process, and quality assurance.

*(Figure: domain-team ownership — those who understand the business best define and maintain the Skill.)*

### 5.3 Domain-team ownership: let those who understand the business best manage the Skill

Who is most capable of defining and maintaining the review standards of `CourseReviewSkill`? Not the IT department, not any single person, but the instructional-design team — they best understand "what makes a good course" and are most capable of judging whether the review standard needs updating.

This is the core idea of **domain-team ownership**: the team with the most measurement capability owns and maintains that domain's Skill.

**A new division of labor**

| Role | Responsibility |
|------|------|
| **Expert** | Define standards, encapsulate the Skill, review changes |
| **Member** | Invoke the Skill, report problems, submit improvement suggestions |

The value of this division of labor isn't the simple allocation of "whoever writes it uses it," but scaled replication: the expert's time is limited, but the Skill can be invoked an unlimited number of times. The expert shifts from "personally performing every review" to "maintaining the review standard," and their influence grows from linear to exponential.

In a real organization, Skills of different domains should be owned by the corresponding business teams:

| Domain | Owning team | Example Skills maintained |
|------|-----------|-----------------|
| Course quality | Instructional-design team | `CourseReviewSkill`, `LearningObjectiveSkill` |
| Data analysis | Data team | `DataCleaningSkill`, `ABTestAnalysisSkill` |
| Security compliance | Security team | `CodeSecurityScanSkill`, `ComplianceCheckSkill` |

"Most measurement capability" means this team not only understands the business rules but can also design an evaluation scheme to validate the Skill's output quality. The instructional-design team can judge whether a review report is on point, and the data team can judge whether a cleaning missed outliers — this judgment is the basis for the Skill's continuous improvement.

Writing a high-quality Skill usually requires collaboration between business experts and technical staff:

| Role | Responsibility |
|------|------|
| **Business expert (SOP Owner)** | Define the process standard and boundary conditions |
| **Technical staff (Agent Architect)** | Prompt-structure tuning and tool mounting |

The collaboration flow has three steps:

1. The business expert describes in natural language "how an excellent reviewer would do it"
2. The technical staff converts it into a structured Skill format
3. Both sides test and iterate together, adjusting the instructions based on the Agent's actual output

To make ownership information explicit in the Skill file, you can add management metadata to the YAML frontmatter:

```yaml
---
name: course-review
description: 
  Review the quality and structural integrity of course content.
  Trigger when the user asks to check, review, or evaluate course material.
owner: Instructional-Design Team
maintainers:
  - zhang-wei        # course-quality lead
  - li-na            # senior instructional designer
version: 2.1.0
last-reviewed: 2026-01-15
---
```

These fields let anyone who opens the file know: whom to contact with a problem, what the current version is, and when it was last reviewed.

> **Tip**: if your team uses GitHub to manage the Skill repository, you can configure a `CODEOWNERS` file to automate review permissions. For example, adding `/skills/course-review/ @teaching-design-team` in `.github/CODEOWNERS` means any modification to that Skill will automatically require approval from an instructional-design team member, institutionally preventing unauthorized changes.

### 5.4 Skills-as-Code: managing Skill assets with engineering methods

After ownership is clear, the next question is: how does the team collaboratively iterate on Skills? The answer is to manage Skills as code — version control, code review, CI/CD, these mature software-engineering practices apply equally to Skills.

**The Skills-as-Code lifecycle**

*Figure (translated): the Skills-as-Code lifecycle.*

```text
[1. Local iteration: maintainer edits and validates on a few representative cases]
        -> [2. Code review + CI/CD: automated checks in the pipeline]
        -> [3. Release: publish the new version for the team]
```

1. **Local iteration**: the maintainer modifies the Skill locally and quickly validates the effect with a few representative cases
2. **PR / Review**: submit a Pull Request, and other team members (especially business experts) review the change
3. **CI evaluation**: an automated pipeline runs the evaluation cases to ensure the change introduces no regression
4. **Deployment**: after merging into the main branch, all Agents using this Skill automatically get the latest version
5. **Feedback collection**: track online usage, collect user feedback, and identify areas needing improvement

Below is a GitHub Actions config example, used to automatically check the Skill's metadata completeness and run evaluation cases at the PR stage:

```yaml
# .github/workflows/skill-review.yml
name: Skill Review

on:
  pull_request:
    paths:
      - 'skills/**/SKILL.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check SKILL.md metadata
        run: |
          for skill_file in $(git diff --name-only origin/main | grep 'SKILL.md'); do
            echo "Checking $skill_file..."
            # Validate the required frontmatter fields
            for field in name description owner version last-reviewed; do
              if ! grep -q "^${field}:" "$skill_file"; then
                echo "ERROR: Missing required field '${field}' in $skill_file"
                exit 1
              fi
            done
          done

      - name: Run skill evaluation
        run: |
          # Run the evaluation cases (see Lesson 3.6 "Evaluation-Driven Agent Development")
          python scripts/evaluate_skill.py --changed-only
```

This pipeline does two things: check whether each modified SKILL.md contains the required management fields (`name`, `description`, `owner`, `version`, `last-reviewed`), then run the evaluation script to validate the Skill's actual effect.

**Deprecation and cleanup**

A Skill isn't valid forever once written. It's recommended to review once a quarter and decide the disposition per the following criteria:

- Not invoked in the past 3 months → consider archiving
- The corresponding business process has been canceled → delete immediately
- Overlaps in function with other Skills → merge and streamline

**Core metrics**

| Metric | Definition | Meaning |
|------|------|------|
| **Reuse rate** | The frequency at which the Skill is invoked by different team members | Only a repeatedly-invoked Skill is an effective asset |
| **Delivery-standard consistency** | The output quality of a novice using the Skill vs. the expert baseline | Measures whether the Skill truly transfers the expert's ability |

These two metrics help you judge whether a Skill is worth continuing to maintain. If the reuse rate is low, the Skill isn't solving a high-frequency problem; if delivery-standard consistency is low, the Skill's instructions aren't clear enough and need continued iteration.

> **Further reading**: you may have noticed that the CI pipeline above includes the "run evaluation cases" step. How do you establish a reliable evaluation system for the probabilistic output of an Agent? This is exactly the topic of [Lesson 3.6 "Evaluation-Driven Agent Development"](./3_6_用评测驱动Agent开发.ipynb). A Skill's quality assurance is inseparable from evaluation-driven development — without evaluation, you can't judge whether a Skill change is an improvement or a regression.

### 5.5 Rollout path: from a seed team to full promotion

After understanding ownership and engineered management, the last question is: how do you actually push this forward in the organization? Rolling out to everyone directly almost inevitably fails. The recommended approach is a "seed Skill" strategy:

1. **Pick a 3-5 person pioneer squad**: find seed members interested in AI tools and with some technical foundation
2. **Focus on one high-value pain point**: such as Code Review, course review, data cleaning — pick the one the team hurts most from
3. **Run through the complete closed loop**: go through one round of "identify expert knowledge → encapsulate the Skill → evaluate and validate → team trial"
4. **Use results to persuade the rest of the team**: bring out concrete data (review time shortened by X%, output quality reaching Y% of expert level)

As the number and scope of Skills expand, the governance mechanism also needs to evolve accordingly:

| Dimension | Pilot phase | Promotion phase |
|------|--------|--------|
| **Who writes** | Technical backbone + business expert | Any team member can submit |
| **Who reviews** | Peer Code Review | A dedicated Skill-review group |
| **Who approves** | Team lead | Domain knowledge engineer |

The focus of the pilot phase is to validate the model's feasibility and accumulate best practices; the focus of the promotion phase is to lower the participation barrier and establish standardized processes. The mark of moving from pilot to promotion is: the seed team can prove with data that Skills brought a quantifiable value improvement.

In the early stage of introducing Skills (usually 1-3 months), overall efficiency may drop rather than rise. This is normal — learning the Skill-writing conventions, debugging Agent behavior, and establishing an evaluation system all take time. The key is to give management appropriate expectations, building confidence with pilot-phase data rather than drawing conclusions in the first month.

Finally, about accountability: when the Agent invokes a Skill to produce code or documents, who is responsible? **Merge means responsibility** — the person who clicks the merge button bears final responsibility for the output. This rule is clear and executable, avoiding the buck-passing of "the AI did it, not my problem."

### 5.6 Section recap

1. **The rollout dilemma**: when an individually-built Skill is used in a team, it hits three kinds of problems — version chaos, wrong modification, and knowledge gap
2. **Capability amplifier**: the core value of a Skill is to replicate expert ability at scale, but it needs ownership and an engineered process to guarantee it
3. **Domain-team ownership**: the team with the most measurement capability owns and maintains the corresponding domain's Skill, making rights and responsibilities clear through YAML metadata and CODEOWNERS
4. **Skills-as-Code**: manage Skills as code, going through the complete engineering lifecycle of PR → Review → CI evaluation → deployment
5. **Rollout strategy**: start from a seed team, focus on a high-value pain point, let data speak, and gradually promote to the whole organization

## 6 Summary

Starting from a tutorial-review task, we gradually led to the core method of Agent context management — from discovering the problem, to understanding the cause, to solving it with Skills, and then to scaling it in a team:

*   **The pain points in tutorial review** (Chapter 1): an autonomous Agent can start working, but when reviewing with a generic standard it misses the team's specific professional requirements; and after writing the professional standard into a Prompt, you face the problems of it being scattered in chat history and unable to be reused and shared.
*   **Precipitating review experience** (Chapter 2): through the four steps of file-ization → directory-ization → segmented checking → load on demand, transform a one-off Prompt into a reusable, maintainable knowledge-base directory. Keep the main file lean, split detailed content into sub-files, and load on demand to avoid context crowding.
*   **Agent Skills** (Chapter 3): a Skill is pre-refined, high-signal-to-noise-ratio context, packaging SOPs, dedicated tools, and expert experience into a reusable module. SKILL.md consists of YAML frontmatter (`name` + `description`) and a Markdown body, following the four writing principles of conciseness, freedom matching, progressive disclosure, and feedback loop. Polish the Skill's quality through the "dual-Agent" evaluation pattern (designer + user).
*   **Framework integration and ecosystem** (Chapter 4): AgentScope's `register_agent_skill` implements Skill registration and on-demand loading; the `skill-creator` meta-Skill can auto-generate a draft (but still needs manual review); relevant platforms provide search (`npx skills find`) and installation of community Skills, used complementarily with self-built Skills.
*   **Team collaboration** (Part 5): when an individual Skill is promoted to a team, it hits version chaos, wrong modification, and knowledge gap. The solutions are domain-team ownership (the team that understands the business best manages the Skill) and Skills-as-Code (managing the Skill lifecycle with PR, Review, and CI evaluation). Start from a seed team, focus on a high-value pain point, and drive promotion with data.

## 🔥 Quiz

### 🔍 Single choice 3.5.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Your course-review Agent always misses the team convention "code examples must have comments." You've reminded it repeatedly across multiple conversations, but every new session it forgets again. What's the most effective solution?❓</b>

- A. Write "code must have comments" into the Agent's long-term memory, so it auto-retrieves this experience before each review
- B. Write a Skill file containing the complete review checklist, and have the Agent load this Skill when executing the review task
- C. Manually paste this requirement into the first message as a prompt each time you start a new conversation
- D. Raise the model's temperature parameter so the Agent considers more possibilities during review and thereby covers this convention

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: B**
📝 **Explanation**:
A is directionally right but not at the right level — Memory suits recording preferences and experience fragments (like "last time the API errored because the version was wrong"), but a scattered memory lacks execution context; the Agent knows "to check comments" but not necessarily the complete check process. C is manual repetitive labor and can't scale. D is unrelated to the problem — temperature affects output diversity, not check coverage. B is correct: a Skill encapsulates the complete review SOP (including all check items, check order, and criteria) as a reusable module; after loading it, the Agent gets systematic work instructions rather than scattered memory hints.
</div>
</details>

## ✉️ Feedback
You're welcome to participate in the [Alibaba Cloud LLM ACP course survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie) to share your learning experience and course feedback.
Your criticism and encouragement are our motivation to keep improving!
