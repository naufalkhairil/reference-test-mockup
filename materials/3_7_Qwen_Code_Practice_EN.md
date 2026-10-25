# 3.7 Hands-On with [Qwen Code](https://qwen.ai/qwencode): Mastering the Coding Agent's Daily Workflow

## 🚄 Introduction

In the previous lessons, you learned how an Agent calls tools, breaks down tasks, lets multiple Agents collaborate, and manages memory, and you also learned how to turn experience into a reusable Skill. Looking back, 3.1 through 3.5 covered a core set of capabilities for building an Agent.

But that doesn't mean you need to build an Agent from scratch every time. Just as learning how an engine works doesn't mean you have to build your own car, when it's time to actually get things done, you should learn to drive a good car instead. Qwen Code is exactly that kind of Coding Agent workstation: it packages tool calling, planning, memory, external tool connections, and Skills into one mature tool, letting you complete real development tasks directly in natural language.

The goal of this lesson is to use Qwen Code as a day-to-day development tool. You'll first have it understand a project, then generate a plan, modify code step by step, verify the result, and commit it — and you'll also see how the concepts you learned earlier map onto concrete operations, eventually forming a repeatable Coding Agent workflow.

## 🍁 Learning Objectives

By the end of this lesson, you will be able to:

* Use Qwen Code to complete a real engineering task
* Drive development with a workflow of understand first, then plan, then code, then commit
* Manage the context window, and compress or clear the session when appropriate
* Create and maintain Agent-facing project configuration files
* Extend Qwen Code with custom commands, external tool connections, and Skills
* Recognize the boundaries and common anti-patterns of a Coding Agent

---

## Installing Qwen Code

Qwen Code is an open-source terminal AI agent from the Qwen team that can understand a codebase, call tools, and autonomously complete programming tasks. This entire lesson is done inside Qwen Code, so please install it first:

> One-click install of Qwen Code (about 1 minute).
> After installation, please launch it by typing `qwen` in a terminal — do not run it inside the Notebook.

<style>
    table {
      width: 80%;
      margin: 20px; /* Center the table */
      border-collapse: collapse; /* Collapse borders for a cleaner look */
      font-family: sans-serif; 
    }

    th, td {
      padding: 10px;
      text-align: left;
      border: 1px solid #ddd; /* Light gray border */
    }

    th {
      background-color: #f2f2f2; /* Light gray background for header */
      font-weight: bold;
    }

    tr:nth-child(even) { /* Zebra striping */
      background-color: #f9f9f9;
    }

    tr:hover { /* Highlight row on hover */
      background-color: #e0f2ff; /* Light blue */
    }
</style>
<table width="90%">
<tbody>
<tr>
<td>

```bash
bash -c "$(curl -fsSL https://qwen-code-assets.oss-cn-hangzhou.aliyuncs.com/installation/install-qwen.sh)" -s --source qwenchat < /dev/null
```

</td>
</tr>
</tbody>
</table>

After installation finishes, open a **new terminal window** (in DSW, click the Terminal menu at the top, then click the  icon in the upper right), type `qwen` to start it, and complete login in three steps:

1. Choose a model provider — the default **Qwen** is fine
2. Choose **OAuth Login**; Qwen Code will generate an authorization link
3. Open the link in a browser, log in to your Qwen account, and click **Authorize**

*(Screenshot: `qwen` CLI login — choose a model provider, the terminal generates an authorization link, open it in a browser, log in and click Authorize to complete login (1,000 free requests per day with OAuth).)*

Once authorized, the terminal will automatically complete the login. With OAuth you get 1,000 free requests per day. For more configuration options, see the [official Qwen Code documentation](https://qwen.ai/qwencode).

## 1 From Concepts to a Tool: How Qwen Code Integrates Everything You've Learned

Once you're logged in, go to the course project directory and start Qwen Code:

```bash
cd /path/to/大模型ACP认证教程/
qwen
```

After it starts, type a single sentence:

```
Take a look at the overall structure of the course_core/chatbot/ directory and tell me what each file is responsible for
```

Watch how Qwen Code responds. You'll see it first read files and analyze the code, then give you a structured answer. This process looks simple, but behind it are several concepts you learned in earlier lessons:

| The Qwen Code behavior you observe | The corresponding Agent concept (chapter) | What it really is |
|---|---|---|
| Automatically calling tools like file reading and code search | **Function Calling** (3.1) | The model outputs a structured tool-call instruction instead of answering directly |
| Read result → think → read again → think again, looping over multiple rounds | **ReAct loop** (3.1) | Alternating between reasoning and acting until the task is done |
| In Plan Mode, listing steps first and then executing them one by one | **Plan & Execute** (3.2) | Generate a full plan first, then execute step by step |
| Automatically splitting a complex task into subtasks that run in parallel | **SubAgent** (3.3) | The main Agent dispatches temporary sub-agents to handle independent subtasks |
| Remembering your earlier preferences and instructions in a long conversation | **Session memory** (3.4) | Short-term memory stored in the context window |
| Project configuration in the QWEN.md file staying in effect persistently | **Persistent memory** (3.4) | Writing key information to a file so it survives across sessions |
| Loading a Skill on demand to execute a specific workflow | **Skill** (3.5) | A predefined instruction set that the Agent decides whether to load based on the task |

The point of this table isn't to memorize the mapping — it's to make sure you internalize one thing: **Qwen Code isn't an independent new topic; it's an engineering implementation of everything you've already learned.** Once you understand this, whenever you learn a new feature later on, you can ask yourself "which Agent concept does this correspond to?" instead of treating it as a manual you need to memorize by rote.

---

## 2 Core Workflow: Explore → Plan → Code → Commit

### 2.1 Why You Need a Workflow

Now here's a real development task:

> Add a "export conversation history as JSON" feature to the Q&A bot — after a conversation ends, the user can export all the questions and answers from that session into a structured JSON file, including timestamps, user questions, bot responses, and cited sources.

If you hand this requirement directly to Qwen Code like this:

```
Help me implement exporting conversation history as JSON
```

it will very likely start writing code right away — adding an export function to `agent.py`, or creating a new `export.py` file. The code might run, but you'll run into these problems:

- It may not know where your conversation history is stored, and guess the wrong data structure
- It may be incompatible with the source-citation format already used in `rag.py`
- The code it generates has no tests, so you can't be sure it's correct
- It changes multiple files at once, making it hard for you to review whether each change is reasonable

This isn't a limitation of Qwen Code's ability — it's that **you haven't given it enough context and structured guidance.** This is the same lesson from 3.2: executing without planning is far less efficient than planning first and then executing.

Next, you'll complete this same task using the four stages of **Explore → Plan → Code → Commit** (EPCC). Afterward, compare the two approaches yourself.

### 2.2 Explore: Understand Before You Act

The Explore stage has one single goal: **let the Agent (and yourself) fully understand the current state of the code before deciding how to change it.**

Enter the following prompt in Qwen Code:

```
I want to add a "export conversation history as JSON" feature to the Q&A bot. Before we start, please help me figure out the following:
1. How is conversation history currently stored? In which file, and what data structure?
2. What does the source field in rag.py look like?
3. Is there any existing export-related functionality we can reuse?
Please only analyze — don't write any code yet.
```

Notice the last sentence — "please only analyze, don't write any code yet." This is the key constraint of the Explore stage. Without it, Qwen Code's ReAct loop will naturally move into the "Action" stage and start writing code once the analysis is done, which isn't what you want right now.

Watch how Qwen Code responds. It will use file-reading tools to open files like `agent.py` and `rag.py`, search for keywords (like `history`, `message`, `source`), and then give you a structured analysis report.

After reading its analysis, you may notice details you hadn't picked up on before — for example, conversation history might be stored in an AgentScope message list rather than a plain Python list, and the source-citation format might include file paths and related passages that need special handling.

**That's the value of Explore: it lets you build an accurate understanding of the current state before you start acting.** Many developers skip this step and start writing code straight from memory, only to discover halfway through that some assumption was wrong and have to start over. Using the Agent to do the exploring is cheap — a few dozen seconds of analysis buys you a clear picture of the project's state.

### 2.3 Plan: Generate a Plan Using Plan Mode

Now that you have a clear picture of the current code, the next step is to produce a concrete implementation plan. This is where Qwen Code's **Plan Mode** comes in.

Qwen Code has four **approval modes**, which you cycle through with `Shift+Tab`:

| Mode | Behavior | Suitable for |
|------|------|---------|
| **plan** | Only analyzes and plans; doesn't modify files or run commands | Reviewing a plan, understanding code |
| **default** | Asks for confirmation before modifying files or running commands | Everyday development (recommended default) |
| **auto-edit** | Automatically approves file edits; commands still need confirmation | Bulk code-modification scenarios |
| **yolo** | Automatically approves everything | Scenarios where you fully trust the Agent |

You can also switch directly with a slash command:

```
/approval-mode plan
```

After switching to Plan Mode, enter the following prompt:

```
Based on the analysis just now, please come up with an implementation plan for the "export conversation history as JSON" feature. Requirements:
1. The exported JSON should include the fields: timestamp, user_query, bot_response, sources
2. Provide a function export_history(chat_history, output_path)
3. Add an export entry point into the existing conversation flow
4. Include basic unit tests
Please list concrete steps, and for each step state which file to change and what to change.
```

In Plan Mode, Qwen Code **only plans, it doesn't execute** — this is a direct expression of the "Plan" stage of the Plan & Execute pattern you learned in 3.2. It will produce a step-by-step plan, listing which files need to be created or modified and what each step involves.

**In Plan Mode, your core job is to review the plan, not passively accept it.** Pay attention to these questions:

- **Is the granularity of each step right?** Does each step do only one thing? If a step is too vague, ask for it to be split up.
- **Are the dependencies correct?** For example, creating `export.py` must happen before modifying `agent.py`.
- **Is anything missing?** For example, does it need to handle conversation history that includes RAG source citations?

If you have feedback on the plan, give it directly while still in Plan Mode:

```
The plan needs adjustment:
- In step 1, the sources field should be extracted from rag.py's retrieval results, not parsed from the message content
- Add a step: validate the format of chat_history before exporting
```

Qwen Code will update the plan based on your feedback. You can iterate on this as many times as you like until you're satisfied with the plan. This is exactly consistent with what 3.2 taught: "a plan isn't generated once and for all — it needs human review and adjustment."

Once you've confirmed the plan, switch back to default mode to start executing:

```
/approval-mode default
```

### 2.4 Code: Execute and Review

Back in default mode, tell Qwen Code to start implementing the plan:

```
Please start implementing according to the plan we just confirmed. Start with step 1, and pause after each step so I can confirm before you continue.
```

> 💡 **Prediction exercise**: If you don't add the constraint "pause after each step so I can confirm," how would the Agent behave in default mode? Would it plow through all the steps in one go?
>
> Think about it before reading on: in default mode, the Agent already pauses for your confirmation before modifying a file or running a command — so even without this constraint, it won't go completely "off the rails." But the problem is that it may bundle changes from multiple steps together and present them for confirmation all at once, making it hard for you to tell which change belongs to which step. Adding the "pause after each step" constraint effectively inserts a checkpoint between steps, letting you review progress at a coarser, more manageable granularity.

For simple tasks it's fine not to add this constraint, but for tasks involving changes to multiple files, confirming step by step lets you catch and correct problems before they spread.

Once Qwen Code finishes the first step, it will show you the generated code and the file changes. At this point you need to do two things:

**First, review the code content.** Not by reading it line by line, but by focusing on a few key points: does the function signature match what was agreed in the plan? Is the data-processing logic correct? Are there any hardcoded values that should be parameters instead?

**Second, confirm the file changes.** You can ask Qwen Code to show you the current diff:

```
Show me the diff for all the files changed so far
```

If something looks wrong, just say so directly:

```
In the export_history function, timestamp should use ISO 8601 format, not a Unix timestamp. Please fix that.
```

If you need to interrupt the current operation — say, Qwen Code is in the middle of a change you don't want — pressing `Esc` will stop it immediately. **You can interrupt the Agent at any time, adjust direction, and then continue.**

Once you've confirmed the first step is correct, tell it to continue:

```
Step 1 confirmed, please continue with step 2.
```

Repeat this process until all steps are done.

### 2.5 Commit: Verify and Commit

All the code is written, but before committing, you need to verify it actually works. Have Qwen Code run the tests for you:

```
Run the tests in tests/test_export.py; if any fail, analyze why and fix them.
```

This instruction takes advantage of the ReAct loop — Qwen Code will run the tests, observe the results, analyze the cause of any failures, modify the code, and run the tests again, until everything passes.

Once the tests pass, have the Agent review its own changes. This is a low-cost quality check:

```
Please review all the code changes you just made and point out any potential issues.
```

Once you've confirmed everything is fine, generate the commit:

```
All tests pass and the review looks fine. Please generate a git commit message and commit.
```

Looking back at the whole process: **Explore let you understand the current state, Plan let you confirm the direction, Code let you implement and review step by step, and Commit let you verify the result and produce a traceable record.** These four stages aren't an arbitrary process — they're a workflow validated by a great deal of practical experience as the most effective way to collaborate with a Coding Agent. You'll use it repeatedly in your future development work.

---

## 3 Approval Modes and Context Management

In the previous section you already used Plan Mode in practice. This section goes deeper into Qwen Code's approval modes and context-management mechanisms — together, they determine how much autonomy the Agent has and how well it can sustain long-running work.

### 3.1 Choosing Among the Four Approval Modes

In section 2.3 you encountered Plan Mode, one of Qwen Code's four approval modes. Pressing `Shift+Tab` cycles through all four. What differs between them is **how much autonomy the Agent has**:

| Mode | What the Agent can do on its own | What you need to do | Suitable for |
|------|-------------------|-------------|---------|
| plan | Read-only — analyze code, search for information | Review the Agent's analysis and plan | Understanding code, designing a plan |
| default | Read + propose — generates code but waits for your confirmation | Confirm each file edit and command execution individually | Everyday development (recommended) |
| auto-edit | Read + write — automatically modifies files | Only confirm command execution | Bulk edits (e.g. adding docstrings everywhere) |
| yolo | Fully autonomous — everything executes automatically | Review results after the fact | Simple tasks where you fully trust the Agent |

The guiding principle for all four modes is **least privilege**: give the Agent just enough autonomy to complete the current task, no more and no less. When you're just starting out, it's best to stay in default mode. Once you've built up enough trust — knowing which kinds of tasks the Agent is reliable on — you can consider relaxing permissions in specific scenarios.

> 💡 **Tip**: In 3.2 you learned that "more autonomy doesn't necessarily mean better." The same principle applies to choosing an approval mode. yolo mode looks the most efficient (you never have to confirm anything), but if the Agent makes a mistake, you may end up spending far more time tracking it down and rolling it back.

### 3.2 The Context Window: The Agent's Workbench

When you studied memory mechanisms in 3.4, you already learned that an Agent's **short-term memory** lives in the context window. Now let's look at what that concept looks like concretely in Qwen Code.

Qwen Code's context window is **256K tokens** (roughly 200,000 characters of Chinese text). At first glance that seems like plenty — but in practice it gets used up faster than you'd expect. That's because the context window doesn't just hold the prompts you type and the Agent's replies; it also holds:

- The full content of every file read
- The results of every code search
- The Agent's reasoning process
- The requests and return values of every tool call

You can picture the context window as a **fixed-size workbench**. Every time you have Qwen Code read a file, it's like laying a document out on the bench; every analysis is like unrolling a sheet of scratch paper. The bench has limited space — once it's full, the documents laid down earliest get "pushed off the edge" (i.e., discarded).

Type `/context` in Qwen Code and you'll see the current session's context usage details, including how many tokens have been used and the breakdown by category. If you followed along with the whole "export conversation history" task in section 2, context usage at this point might already be at 30%–50%.

**This means: in an overly long session, Qwen Code may "forget" earlier parts of the conversation and analysis results.** This isn't a bug — it's an inherent limitation of the context window. Once you understand this, it makes sense why you need to actively manage context.

### 3.3 /compress and /clear: Managing Context

Qwen Code provides two commands for managing context space:

**`/compress`** (alias `/summarize`) — compresses the context. When run, Qwen Code generates a **rolling summary** of the current session, keeping only the key information and freeing up a large amount of space. You learned about the "summary compression" strategy for memory back in 3.4 — `/compress` is its practical application.

> 💡 **Prediction exercise**: If, after `/compress`, you ask the Agent to recall a specific function parameter name discussed before the compression (e.g., "what was the second parameter of `export_history` we just analyzed called?"), will it answer accurately?
>
> Think about it before checking: most likely not. What `/compress` keeps is a summary of key decisions and conclusions; fine details like specific parameter or variable names are usually lost in the compression. That's why, before compressing, you should write any key details you'll need to reference later into QWEN.md or somewhere else.

Try it yourself: run `/context` first to record the current token usage, then run `/compress`, then run `/context` again to compare before and after. You'll see a significant drop. But be aware: **compression involves information loss.** Fine-grained details (like a specific function's parameter names, or a specific conclusion from a discussion) may be lost after compression. If you'll need to reference those details later, you need to record them manually before compressing — for example, by writing them into QWEN.md, which is covered in the next section.

**`/clear`** — clears the context. This is equivalent to fully resetting the session: all conversation history, analysis results, and established context are lost.

The two commands are used at different times:

| Scenario | Recommended action | Reason |
|------|---------|------|
| Context usage is over 70%, but the current task isn't finished | `/compress` | Keeps the core context, frees up space to keep working |
| The current task is done and you're about to start an unrelated new task | `/clear` | The old context has no value for the new task; clearing avoids interference |
| The Agent's answers start showing clear errors or contradictions | `/clear` | The context may be polluted by too much information; starting fresh is more efficient |

The key principle is: **`/compress` is a way to save space while a task is still in progress; `/clear` is a way to draw a clean line between tasks.**

### 3.4 A Practical Strategy: When to Start a New Session

Once you understand context management, a natural question arises: instead of compressing repeatedly within one session, why not just start a new session?

The answer is: **often, starting a new session really is the better choice.** Here are three signals that tell you it's time to do so:

1. **The task boundary is clear.** You've finished building the "export conversation history" feature, and you're about to work on a completely different task. There's no contextual dependency between the two tasks, so starting a new session lets the Agent focus all of its attention on the new task.

2. **Context usage is over 80%.** Even if `/compress` can still free up some space, in a heavily loaded context the Agent's attention becomes uneven — it may over-focus on recent content while neglecting important earlier information.

3. **The Agent starts "looping" or giving inconsistent answers.** If you notice Qwen Code repeatedly trying the same approach, or contradicting itself about how to modify a piece of code, this usually means the context has become muddled.

A rhythm that's been validated in practice is: **use 5–10 short sessions per day instead of one long session.** Each session focuses on one concrete task (one feature, one bug, one refactor); once it's done, commit the code, then start a new session for the next task.

If a new session needs the results of a previous one, you don't need to re-explain everything by hand. Qwen Code can directly read the code you've already committed to Git, and read the configuration in QWEN.md — this persisted information naturally becomes part of the new session's context. **Key decisions and agreements that truly need to carry across sessions should be written into QWEN.md rather than relied on from memory.**

---

## 4 Project Configuration: Building Persistent Memory with QWEN.md

In the exercises so far, you've experienced the EPCC workflow and learned to manage a single session's context with `/compress` and `/clear`. But you may have noticed one problem: **every time you start a new session, the Agent knows nothing about your project.**

You end up having to repeat things like "this project builds RAG with LlamaIndex 0.12+," "API calls go through DashScope's OpenAI-compatible interface," and "the code follows PEP 8." If you remember the memory taxonomy from section 3.4, you'll recognize this as a classic case of **procedural memory** — not temporary information from a single conversation, but project-level knowledge that holds true across every session.

The problem is clear: the Agent's session context disappears once you `/clear` it or close the terminal. You need a **persistent project-memory** mechanism so the Agent automatically loads this background knowledge every time it starts.

### 4.1 What Is QWEN.md

**QWEN.md** is a Markdown file placed at the root of the project, which the Agent automatically reads and adds to the system context every time it starts. It's Qwen Code's concrete implementation of **persistent memory**.

You can create this file by hand, or have the Agent generate an initial version for you. Run this in Qwen Code:

```
/init
```

The Agent will scan the project's directory structure, read key files (like `requirements.txt` and the code of major modules), and then produce a draft QWEN.md.

**But don't just use the generated result as-is.** What `/init` produces is the Agent's "first impression" — it may miss important constraints, or misread certain design intentions. You need to review and edit it, just as you would review code the Agent generated.

### 4.2 What to Write, and What Not to Write

A common mistake is turning QWEN.md into a copy of the project documentation. QWEN.md isn't a document for humans to read — it's a **working instruction set** for the Agent, containing only the things that "if the Agent doesn't know them, it will keep making the same mistake."

Here's a practical QWEN.md for the Q&A bot project as an example:

```markdown
# Q&A Bot Project

## Project Overview
An internal company Q&A bot, built on a RAG architecture, that retrieves from the company knowledge base to answer employee questions.

## Tech Stack
- Framework: LlamaIndex 0.12+ (do not use LangChain)
- LLM: Qwen (qwen-plus), called through DashScope's OpenAI-compatible interface
- Embedding: DashScope text-embedding-v2
- API key loading: always use config/load_key.py — never hardcode the API key

## Code Structure
- chatbot/llm.py: basic LLM calls (invoke, invoke_with_stream_log)
- chatbot/rag.py: core RAG logic (indexing, create_query_engine, ask)
- chatbot/agent.py: Agent creation (a ReActAgent built on AgentScope)
- chatbot/evaluate.py: RAGAS evaluation
- config/load_key.py: API key loading, reads Key.json

## Coding Conventions
- Follow PEP 8
- Every function must have a docstring describing parameters and return value
- When adding a new module, update the code-structure notes in this file

## Common Pitfalls
- DashScope's base_url is https://dashscope.aliyuncs.com/compatible-mode/v1 — don't use the default OpenAI address
- LlamaIndex 0.12's import path has changed to llama_index.core — don't use the old path
  - ✗ from llama_index import VectorStoreIndex
  - ✓ from llama_index.core import VectorStoreIndex
- The query_engine returned by create_query_engine() supports streaming output; handle streaming_response carefully when wiring it up to the frontend
```

Every line in this QWEN.md corresponds to a specific mistake the Agent might otherwise make. Use the table below to decide what to include and what to leave out:

| Include | Don't include |
|------|--------|
| Tech stack and version constraints (LlamaIndex 0.12+) | Complete API documentation or tutorials |
| The responsibilities and calling conventions of key modules | The source-code implementation details of every function |
| Coding conventions (PEP 8, docstring requirements) | General Python programming common sense |
| Specific mistakes the Agent has repeatedly made, and how to fix them | One-off debugging notes |
| Environment configuration like API addresses and auth methods | The API key itself (a security risk) |

The common thread on the left is: **the Agent will get it wrong if it doesn't know this, and it holds true across every session.** The items on the right are either too granular (the Agent can just read the code itself), a security risk (the contents of Key.json), or general knowledge the Agent already has (it already knows what PEP 8 is).

It's recommended to keep the total length of QWEN.md under 200 lines. Beyond that, it starts eating up too much context space on its own, crowding out room for the actual work.

### 4.3 Three Levels of Configuration

Qwen Code supports a **three-level configuration hierarchy**:

| Level | File location | Scope | Typical content |
|------|---------|---------|---------|
| Global | `~/.qwen/QWEN.md` | All projects | Personal coding preferences, general conventions |
| Project | `QWEN.md` at the project root | The current project | Tech stack, module structure, project constraints |
| Directory | `QWEN.md` in a subdirectory | A specific directory | That module's special rules |

When the Agent starts, the three levels are loaded and merged in the order "global → project → directory." More specific configuration takes priority — if the global config says "use 4-space indentation" but the project config says "use 2-space indentation," the Agent will follow 2-space indentation in that project.

In the Q&A bot project, one practical use is placing a directory-level QWEN.md under the `chatbot/` directory that specifically describes the calling relationships between modules in that directory and how they're tested. That way, when the Agent works inside `chatbot/`, it knows both the project's global constraints and this directory's special rules.

### 4.4 Letting QWEN.md Evolve on Its Own

QWEN.md isn't something you write once and never touch again. Recall the core idea from section 3.4: **write memory in response to failure** — the most valuable content in a memory system comes from mistakes the Agent has actually made.

Here's a scenario you might run into: you ask the Agent to modify `rag.py`, and it generates code using `from llama_index import VectorStoreIndex` — the old-style import path from an older LlamaIndex version, which raises `ModuleNotFoundError` on 0.12+. You correct it, and the Agent fixes it. But in the next session, the same mistake may resurface, because the earlier correction only existed in a session that has since been `/clear`ed.

The right approach is: **when you notice the Agent repeatedly making the same kind of mistake, write the fix into QWEN.md.** You can even have the Agent do this itself:

```
Please add a note about LlamaIndex 0.12's import path to the "Common Pitfalls" section of QWEN.md.
```

The Agent will edit QWEN.md, and load the updated version the next time it starts. This forms a **memory evolution loop**: the Agent makes a mistake → you correct it → it's written into QWEN.md → the Agent stops making that kind of mistake.

> 💡 **Prediction exercise**: Suppose you never wrote "the API key is loaded via `config/load_key.py`" into QWEN.md. When the Agent needs to call the LLM in a new session, what kind of code is it most likely to generate?
>
> Think about it before reading on: the Agent will most likely just write `os.getenv("OPENAI_API_KEY")` or hardcode a placeholder string — because that's the pattern it saw most often in its training data. It has no way of knowing your project has a dedicated key-loading module unless you tell it.

---

## 5 Extending Capabilities: Custom Commands, MCP, and Skills

So far you've only used Qwen Code's built-in capabilities: reading files, writing code, running commands. But in real development, teams often have their own specific processes — what to check during code review, what checks to run before committing, which docs to consult for a particular kind of problem. These needs go beyond what the built-in commands cover.

Qwen Code offers three extension mechanisms to address different needs. Let's work through each one hands-on, then build a clear decision framework in section 5.4.

### 5.1 Custom Commands: One-Click Trigger for a Fixed Process

Let's start with the simplest scenario: you want the Agent to run a code review before committing, checking PEP 8 compliance, docstring completeness, and common error patterns. Typing out a long prompt by hand every time is tedious — you need to package this fixed process into a reusable command.

Create `.qwen/commands/review.md` at the project root:

```markdown
---
description: Review code changes, checking conventions and common issues
---

Please review the code changes in the following files: $ARGUMENTS

Checklist:
1. Does it comply with PEP 8?
2. Does every function have a docstring (describing parameters and return value)?
3. Is there any hardcoded API key or secret?
4. Does the DashScope API call use the correct base_url?
5. Does the LlamaIndex import path use llama_index.core?

Output format:
- List issues grouped by file
- Label each issue's severity (Error / Warning / Info)
- End with an overall assessment and suggestions for fixes
```

To use it, type in Qwen Code:

```
/review chatbot/rag.py
```

The instruction the Agent receives is the full content of the template, with `$ARGUMENTS` replaced by `chatbot/rag.py`. It will read the file, go through the checklist item by item, and output a structured review report.

A custom command is essentially a **prompt template** — it takes a complex prompt you use over and over and locks it in place, triggered with one keystroke via `/command-name`. Its defining traits are: **manually triggered, fixed process**.

> 💡 **Tip**: Custom commands also support nested directories. If you create `style.md` and `security.md` under `.qwen/commands/check/`, you can trigger them separately with `/check style` and `/check security`.

### 5.2 Hands-On with MCP: Connecting Bailian's Web Search

Custom commands solve the "fixed process" problem, but some capabilities can't be achieved with a prompt alone. For example, you might want the Agent to consult the latest LlamaIndex documentation in real time while writing code. That requires letting the Agent call an external service — that's **MCP** (Model Context Protocol), which you learned about in section 3.1.

In 3.1 you learned the design idea behind MCP: it decouples the tool provider from the Agent, and the Agent discovers and calls tools through a standard protocol. Now let's actually set it up.

Run this in a terminal:

```bash
qwen mcp add web-search --npx -y @anthropic/mcp-server-web-search
```

This command tells Qwen Code: there's an MCP service called `web-search` available. When the Agent starts, it will discover the tools that service provides through the MCP protocol.

Once it's added, you can just tell the Agent:

```
Please search for the latest usage of VectorStoreIndex in LlamaIndex 0.12,
then check whether the implementation in chatbot/rag.py needs to be updated.
```

Watch the Agent's behavior — it will go through the ReAct loop you learned in 3.1: think (need to check the latest API) → act (call the web search) → observe (search returns documentation) → think (compare with the existing code) → conclude (give a verdict on whether a change is needed).

Throughout this process, the MCP tool call is transparent to you — the Agent decides on its own when it needs to search the web; you don't need to trigger it manually. This is the most fundamental difference between MCP and custom commands: MCP provides **tools the Agent can call autonomously**, while a custom command is a **fixed process you trigger manually**.

Custom commands and MCP solve the "fixed process" and "connecting to external services" problems, respectively. But there's a deeper extension need they don't cover: how do you let the Agent **load domain-specific expert knowledge on demand** — automatically following team conventions during a code review, or automatically checking instructional-design standards during a course review? That's what **Skill** is for, covered in depth in the next section.

---

## 6 Locking In Expert Experience with Skills

### 6.1 From Ad-Hoc Instructions to Skills: Why You Need an Evolution Path

MCP gives the Agent "more things it can do," but sometimes what the Agent needs isn't a new tool — it's **domain-specific expert knowledge**. For example, when reviewing code for the Q&A bot, you want the Agent to automatically check a few things: whether it used `config/load_key.py` to load the API key, whether LlamaIndex import paths are correct, and whether every function has a docstring.

You could type these rules into the chat box every time. But by the third time, it gets tedious — the rules keep growing, copy-pasting is error-prone, and different tasks need different rule sets.

You learned the theory behind Skill in 3.5 — packaging expert knowledge into a triggerable, self-contained unit. Now let's see how it's actually implemented in Qwen Code.

This evolution happens in four steps, each one solving a specific pain point from the previous step:

| Stage | Form | Pain point solved | New problem |
|------|------|-----------|---------|
| Ad-hoc instruction | Type rules directly into the conversation | None | Rules keep growing longer, pasted over and over |
| Standalone file | Save the rules as a `.md` file, referenced with `@rules.md` in conversation | No more repeated pasting | Must reference it manually each time; easy to forget |
| Custom command | Placed in `.qwen/commands/` | `/review` triggers it with one keystroke | Must be triggered manually; the Agent won't use it on its own |
| **Skill** | Placed in `.qwen/skills/` | The Agent decides on its own whether to load it, based on the task | — |

That last step is where Skill's real value lies: **you don't have to tell the Agent "use the review convention now" — it figures out what knowledge it needs based on your task description, and loads it on demand.** This is the practical implementation of "Progressive Disclosure," which you learned about in section 3.5.

### 6.2 Designing a Skill's Structure and Trigger Conditions

A Skill is a directory — the directory name is the Skill's name — that must contain a `SKILL.md` file. This file has two parts:

**YAML frontmatter** (metadata):

```yaml
---
name: course-review
description: Review ACP course content against the writing conventions. Use when the user asks to review course material or check the quality of instructional content.
---
```

**Body** (the instruction text):

```markdown
# Course Content Review Guidelines

## Language Style
- Must use second person ("you")
- Do not use internet slang or overly cute phrasing
...
```

**The underlying logic of the trigger mechanism:** when Qwen Code starts, it only reads the `name` and `description` fields of every Skill (not the body) and injects these summaries into the Agent's system prompt. When you give it a task — say, "help me review the content of lesson 3.5" — the Agent notices that "review course content" in the `description` matches the current task, and then reads the full body into context.

This design has three implications you need to understand for practical use:

1. **The quality of `description` determines trigger accuracy.** Write it too vaguely (like "general review") and the Agent may load it even when it's not needed; write it too narrowly (like "review lesson 3.5") and the Agent may fail to trigger it when reviewing lesson 3.6. A good description should describe the **type of task**, not a **specific instance**.

2. **The body doesn't stay resident in context.** Unlike QWEN.md, a Skill's body is only loaded when triggered. That means you can create many Skills without worrying about crowding out context — only the Skill the current task actually needs gets loaded.

3. **Complex Skills should use progressive disclosure.** If your review guidelines have 10 categories and 200 rules, don't put them all in SKILL.md. The main file should only contain the framework and a table of contents, with detailed rules in sub-files in the same directory. The Agent reads the sub-files when it reaches the corresponding step — this way, only the part actually needed gets loaded each time, avoiding wasted context.

### 6.3 Distilling a Skill from Failure Cases

The most common mistake in writing a Skill is "designing it out of thin air" — sitting down and thinking "what rules should the Agent follow," then listing them one by one. Skills written this way tend to be either too generic ("write good code") or missing key scenarios (because you didn't anticipate where the Agent would actually go wrong).

Section 3.5 taught a more reliable method: **distill from failure.** In Qwen Code, this process can be done in five steps:

**Step 1: Have the Agent complete a real task with no Skill at all.** For example, have it review the code quality of `chatbot/rag.py`. Record its output: what it checked, what it missed, and which suggestions were inaccurate.

**Step 2: Extract patterns from the failures.** Suppose you find three problems: (1) it didn't check the LlamaIndex import path; (2) it suggested a deprecated API usage; (3) it ignored the calling convention for `load_key()`. These three problems are exactly what your Skill needs to cover.

**Step 3: Write a first draft of the Skill.** Write rules targeting the problems you found in step 2. Don't aim for perfection — start by covering just the 3–5 most critical rules.

**Step 4: Verify with a new session.** Start a completely fresh Qwen Code session (`/clear` or a new terminal), have the Agent load your Skill, and run the same task again. Compare the output with and without the Skill. Were the three problems from step 1 solved? Did it introduce any new problems?

**Step 5: Iterate.** Revise the Skill based on the results of step 4, then repeat step 4 to verify, until the Agent reliably passes every check you care about.

The key insight here is: **establish a baseline first (the Agent's unaided failure case), then write the Skill.** Don't skip step 1. Without a baseline, you can't tell whether the Skill actually improved the Agent's behavior — you're just going on a "feeling" that it got better.

### 6.4 Using Evaluation to Drive Skill Optimization

Distilling rules from failure cases can help you write a Skill that works. But there's still a gap between "works" and "works well" — a Skill might perform fine on the scenarios you tested, but fail on new ones.

Section 3.5 introduced **evaluation-driven Skill self-optimization**. In Qwen Code, this can be implemented as follows:

**Build an evaluation set.** Prepare 10–20 test cases for your Skill, covering three categories:

- **Positive triggers** (8–12 cases): scenarios where the Agent should load the Skill and execute it correctly
- **Edge cases** (3–5 cases): tricky borderline situations
- **Negative controls** (2–3 cases): scenarios where the Agent should *not* trigger the Skill (e.g., "help me write a new function" shouldn't need the course-review Skill)

**Run it automatically.** Batch-run the evaluation using Qwen Code's headless mode:

```bash
qwen -p "Please review the quality of the following code snippet: [test case 1]" --output-format stream-json
```

The output for each test case can be automatically collected and compared against the expected result.

**Analyze failure cases.** Find the cases the Skill didn't handle correctly, and figure out the root cause: did the `description` fail to trigger it? Is there a gap in the rules themselves? Or are the rules written too vaguely, causing the Agent to misinterpret them?

**Iterate.** Revise SKILL.md based on your analysis, then rerun the evaluation set to confirm the fix solved the problem without breaking existing cases — this is the same principle as the "full regression to prevent the whack-a-mole effect" you learned in section 3.5.

> 💡 **Tip**: The **skill-creator meta-Skill** mentioned in section 3.5 can speed up this process — hand it your failure cases and execution traces, and let it analyze the root cause and propose changes to SKILL.md. But skill-creator only speeds up iteration; it doesn't replace your own understanding of Skill structure and trigger design. Using skill-creator without understanding the underlying principles means even the changes it produces might not actually help.

### 6.5 Managing and Sharing Qwen Code Skills

The Skill you created for the Q&A bot project, and the QWEN.md and custom commands you use every day, are essentially different layers of the same underlying idea:

| Mechanism | What it really is | Scope |
|------|------|---------|
| QWEN.md | Project knowledge that's always in effect | Automatically loaded every session |
| Custom command | A manually triggered fixed process | Loaded when you type `/command-name` |
| **Skill** | An expert-knowledge package the Agent decides to load on its own | Loaded on demand when it matches the task |

Qwen Code stores Skills in two locations: project-level (`.qwen/skills/`) and user-level (`~/.qwen/skills/`). You can use the `/skills` command to see all currently available Skills.

A Skill's value grows with how widely it's reused. The Skill you wrote for course review can be used by everyone on your team — as long as the `.qwen/skills/` directory is checked into Git version control. When your Skill is used by 10 people, the effort you invested packaging it once pays off tenfold. This is the practical realization of "package once, reuse many times" from section 3.5, now applied inside Qwen Code.

---

## 7 Harness Engineering: From Using Tools to Steering a System

Up to this point, you've had Qwen Code understand a project first, generate a plan, modify code step by step, verify it, and commit — and you've also used approval modes, context management, QWEN.md, custom commands, MCP, and Skills. Looked at individually, they seem like a set of separate tools; step back, and they together form the external environment that lets a model actually work inside a code repository.

This external environment has a name: **Harness Engineering**. A large language model is like an engine — it can understand code, produce plans, and execute actions; but for this engine to reliably complete engineering tasks, it also needs context, tools, permissions, memory, checks, and boundaries.

Qwen Code is a concrete example of this. It has already organized capabilities like reading files, editing code, running commands, and human approval into a default Harness. Section 3.7 looks at how this default Harness supports everyday development; in 3.8, we'll go further and put Harness Engineering and Loop Engineering into concrete business workflows.

### 7.1 Letting the Model Truly Operate Inside the Code Repository

The role of a Harness isn't to limit the model — it's to make the model's ability controllably productive. Just as a race car's control systems don't slow the engine down, they let the driver direct every bit of its horsepower.

The default Harness that Qwen Code provides organizes these capabilities together:

| Component | How it shows up in Qwen Code | The problem it solves |
| --- | --- | --- |
| File and command tools | Reading files, searching code, running commands | Lets the Agent operate inside a real repository |
| Context management | `/context`, `/compress`, `/clear` | Lets the Agent manage its attention |
| Approval modes | plan, default, and other modes | Controls how much the Agent can do |
| Project memory | QWEN.md | Keeps project rules persistent across sessions |
| Extension capabilities | Custom commands, MCP, Skill | Brings in fixed processes and external tools |

This section is first about learning to use the default working environment Qwen Code provides — knowing what it can do, where its boundaries are, and when human judgment is required.

### 7.2 Repository Knowledge Is the Agent's Source of Truth

An Agent can only use what it can actually see. Architectural decisions discussed in team chat, product direction from meeting notes, coding preferences that exist only in someone's head — if none of it is written into the repository, none of it exists as far as the Agent is concerned.

You might think: then just write every rule into QWEN.md. That approach fails fast, for several reasons.

1. **Context gets crowded out.** If the instruction file is too big, there's no room left for the task and the code itself.
2. **Too many rules lose focus.** If everything is "important," the Agent doesn't know what to look at first.
3. **A large file quickly goes stale.** If no one cleans up old rules, the Agent can't tell which ones are still valid.
4. **It's hard to audit.** A giant file is hard to check for coverage, staleness, or cross-references.

So QWEN.md shouldn't be written as an encyclopedia — it should be written as a table of contents: what the project is, where the rules live, which files must not be touched, and which document to consult for a specific problem. Detailed rules belong in a Skill, in docs, or in a dedicated conventions file, which the Agent reads on demand when it reaches the relevant task.

This is the same idea as a Skill's progressive disclosure: the main file only contains the core flow used every time, while detailed rules go into references or scripts, avoiding filling up the context all at once.

### 7.3 Enforcing Engineering Constraints Mechanically

"Telling the Agent to follow a convention" and "making the Agent unable to get away with not following it" are two different things. The former relies on a prompt — the Agent may remember it, or may forget it; the latter relies on a mechanism — a violation gets caught by a tool, or at least produces a clear error message.

In a real project, any rule that can be turned into a command, a script, a Hook, CI, or a review checklist shouldn't just stay a verbal reminder. The error message a checking tool produces is itself a clue for the next round of fixes.

The table below maps Harness Engineering principles to the mechanisms you've already learned in Qwen Code:

| Harness Engineering principle | How it shows up in Qwen Code |
| --- | --- |
| Repository knowledge is the source of truth | QWEN.md, Skill, and docs are managed alongside the code |
| Navigate like a table of contents, not an encyclopedia | QWEN.md stays lean; details go into Skill and docs |
| Enforce constraints mechanically | Custom commands, Hooks, CI, review checklists |
| The process is observable | `/context` to inspect context; export session logs when needed |
| Experience keeps accumulating | Recurring mistakes get written back into QWEN.md or a Skill |
| Continuous human-taste feedback | Plan Mode reviews the plan; default mode confirms high-risk actions |

This way, the Agent isn't following rules "on its own conscience" — it's working inside an environment that has checks and boundaries built in.

### 7.4 From "Using Tools" to "Steering a System"

Putting everything you've learned together, you can see a layered structure:

| Layer | What you learned | Its role in the Harness |
| --- | --- | --- |
| Tool layer | Reading files, editing code, running commands, approval modes | Lets the Agent get things done, while knowing what needs human confirmation |
| Context layer | `/context`, `/compress`, `/clear` | Manages the Agent's attention |
| Memory layer | QWEN.md's three-level configuration | Preserves project knowledge across sessions |
| Extension layer | Custom commands, MCP, Skill | Brings in fixed processes, external tools, and expert experience |
| Verification layer | Tests, code review, evaluation sets | Judges whether the result is reliable |
| Evolution layer | Updating QWEN.md and iterating on Skills in response to problems | Lets the environment keep improving as it's used |

Stack these layers together and you get the Harness built around the large-model engine. You don't need to build out every layer all at once — start with QWEN.md, write a custom command whenever you hit a fixed process, connect an MCP whenever you need external material, turn recurring expert experience into a Skill, and add tests and reviews at the key checkpoints.

What matters isn't that every layer is perfect — it's forming a continuous loop: **find a problem → lock in a solution → verify the effect.** Every mistake the Agent makes is a chance to improve the external environment.

> 💡 **Prediction exercise**: Suppose 5 people on a team are all using Qwen Code to develop the Q&A bot project. One person writes a useful code-review Skill — how can the others start using it?
>
> Think about it before reading on: check `.qwen/skills/` and `.qwen/commands/` into Git version control. Once one person creates a Skill, everyone else can use it after a `git pull`. This is the practical realization, in engineering terms, of "from individual capability to team asset" from section 3.5, and a direct expression of "repository knowledge is the source of truth."

That's it for 3.7. You can now use Qwen Code's default working environment: it can read code, edit files, call tools, manage context, and load project memory and Skills.

The next lesson goes further: on top of Qwen Code, you'll fill in the standards, samples, checks, records, and stop conditions for a concrete business task. In other words, rather than just using off-the-shelf tools, you'll put Harness Engineering and Loop Engineering into a business workflow, so the Agent generates, checks, revises, and accumulates experience according to your own standards.

---

## 8 Putting It All Together: Building a Gradio Web UI with Qwen Code

The previous sections covered the workflow, context management, project configuration, and extension mechanisms. Now let's put these methods into one complete task: **adding a Gradio web interface to the Q&A bot**.

### 8.1 Requirements and Task Breakdown

The requirement is clear: wrap `chatbot/rag.py`, which currently can only be called from a Notebook, into a web app — a user types a question in the browser and sees the answer along with the original source documents that were retrieved.

- The user types a question and clicks an "Ask" button
- The page displays the Q&A bot's answer
- Below the answer, the page shows the retrieved source documents (file name and relevant passage)
- Use the existing functions in `chatbot/rag.py`
- Put the code in `app.py` at the project root

In Qwen Code, switch to Plan Mode (`/approval-mode plan`) and enter the requirement to have the Agent produce a plan.

### 8.2 Explore + Plan: Analyzing the Existing Code and Designing a Plan

In Plan Mode, the Agent will first read the code in `chatbot/rag.py`, understand the interfaces of functions like `load_index()`, `create_query_engine()`, and `ask()`, and then produce a step-by-step plan.

> 💡 **Prediction exercise**: The `ask()` function currently calls `streaming_response.print_response_stream()`, printing directly to the terminal. If the Agent calls `ask(question, query_engine)` directly inside `app.py`, what will show up in the Gradio interface?
>
> The answer is: nothing will show up in the interface. `print_response_stream()` writes its output to standard output (the terminal), not back to the caller. The Agent needs to bypass `ask()` and use `query_engine.query()` directly to get a return value. If, while reviewing the Agent's plan, you notice it intends to call `ask()` to get an answer string, you should point this out immediately.

The core question when reviewing the plan is: did the Agent correctly understand how the existing functions actually behave? Once you've confirmed the plan is sound, switch back to default mode to start executing.

### 8.3 Code: Step-by-Step Implementation

During implementation, apply all the key practices you've learned so far:

**Check the diff.** Pay particular attention to whether the Agent modified any existing functions in `chatbot/rag.py` — if the task only requires creating a new `app.py`, the Agent shouldn't be touching the public interface of an existing module. If it tries to change the signature of `ask()`, you need to judge: would this change affect other code that depends on `ask()` (like calls from a Notebook)?

**Monitor the context.** Periodically run `/context` to check usage. As the Agent repeatedly reads files, generates code, and fixes errors, the context can balloon quickly. Once usage exceeds 60%, run `/compress` after a subtask finishes to compress the conversation history.

**Update QWEN.md.** If the Agent makes a repeated mistake (like using a deprecated Gradio API), fix it and write the correction into QWEN.md.

**Make use of MCP.** If the Agent is unsure about a parameter for some Gradio component, it can look up the latest documentation through the web-search MCP you configured in section 5.2.

The core logic of the `app.py` the Agent generates looks roughly like this:

```python
import gradio as gr
from config.load_key import load_key
from chatbot.rag import load_index, create_query_engine

load_key()

# Load the index and query engine on startup
index = load_index()
query_engine = create_query_engine(index)

def answer_question(question):
    """Handle a user question and return the answer and its source information."""
    response = query_engine.query(question)

    # Extract the answer text
    answer = response.response

    # Extract the source information
    sources = []
    for node in response.source_nodes:
        source_info = {
            "file": node.metadata.get("file_name", "unknown"),
            "content": node.get_content()[:200]
        }
        sources.append(source_info)

    source_text = "\n\n".join(
        [f"📄 {s['file']}\n{s['content']}" for s in sources]
    )
    return answer, source_text
```

Notice two key design decisions: first, the code uses `config/load_key.py` to load the API key (because of the explicit constraint in QWEN.md); second, the Agent didn't call the `ask()` function — it used `query_engine.query()` directly, because it needed the full `Response` object in order to extract `source_nodes`.

### 8.4 Verification and Delivery

Once the code is implemented, start the app in a terminal to test it:

```bash
python app.py
```

Test the following scenarios:

1. **A normal question**: enter a question that the knowledge base can answer (e.g., "What are the writing-convention requirements at the company?"), and confirm the answer is correct and the sources are fully displayed
2. **A question outside the knowledge base**: enter a question the knowledge base has no answer for, and confirm the bot doesn't make one up
3. **Empty input**: click "Ask" without typing anything, and confirm nothing crashes
4. **Long text**: enter a fairly long question, and confirm the layout doesn't break

Once testing passes, use the custom command you created to run a code review:

```
/review app.py
```

Once you've confirmed there are no serious issues, have the Agent generate the commit:

```
Please generate a git commit for this change and commit it.
```

Before confirming the commit, check the list of staged files — make sure `Key.json` isn't included.

At this point, you've used Qwen Code to complete an entire development flow, from requirements analysis to code delivery.

---

## 9 Recap: The Boundaries and Anti-Patterns of a Coding Agent

### 9.1 What the Agent Is Good At, and Where It Tends to Go Wrong

**What the Agent is good at:**

- **Scaffolding code**: generating a module's basic structure from a requirement description, like the Gradio interface skeleton for `app.py`
- **Reading and explaining code**: quickly analyzing the calling relationships between functions in `chatbot/rag.py`
- **Repetitive changes**: for example, adding docstrings to every function, or bulk-updating import paths
- **Generating test cases**: automatically producing test code from function signatures and docstrings
- **Searching and synthesizing information**: connecting to web search via MCP, consulting framework docs, and summarizing key points

**Where the Agent tends to go wrong:**

- **Outdated API usage**: the Agent's training data has a cutoff date, so it may generate calls to functions that have since been deprecated
- **Project-specific constraints**: unless it's written in QWEN.md, the Agent doesn't know about your project's special rules
- **Cross-file side effects**: when changing a function's return type, the Agent may forget to check other call sites
- **Edge-case handling**: generated code usually covers the normal path but tends to miss things like empty input or unexpected responses
- **Security-sensitive operations**: the Agent may hardcode an API key in the code, or create a file containing sensitive information outside `.gitignore`

These two lists aren't meant to judge whether the Agent is "good" — they're meant to help you set clear expectations: **let it run freely in areas it's good at, and focus your review on the areas where it tends to go wrong.**

### 9.2 Five Anti-Patterns

Here are the five most common inefficient habits when working with a Coding Agent:

| Anti-pattern | What it looks like | The right approach |
|--------|------|---------|
| **Saying too much at once** | Cramming several unrelated requirements into a single instruction | One task at a time, working through the four EPCC stages step by step |
| **Not checking the diff** | Continuing right after the Agent edits a file, without checking what actually changed | Review the diff after every file change, watching for edits to files that shouldn't have been touched |
| **Ignoring context bloat** | Long sessions that never use `/compress` or `/clear` | Monitor with `/context` regularly, `/compress` after a subtask is done, `/clear` before a new task |
| **Treating the Agent as a search engine** | Repeatedly asking conceptual questions instead of giving it development tasks | Use docs or a search engine for conceptual questions — the Agent's value lies in reading/writing code and executing actions |
| **Committing without verifying** | Committing right after the Agent generates code, without running tests or checking manually | Run it, test it, review it first — commit only once you've confirmed it's correct |

The common root cause of all five anti-patterns is **over-trusting or over-relying on the Agent.** The Agent is an efficient collaborator, but it doesn't make judgment calls for you — deciding "should this code really be changed this way" and "is this result actually correct" is still your responsibility.

---

## ✅ Lesson Summary

This lesson walked through the Coding Agent's day-to-day workflow from a user's perspective, start to finish.

- Understand the project first, then make a plan, then code step by step, then verify and commit — so development tasks move forward in an orderly way.
- Approval modes let you control how much autonomy the Agent has: review the plan carefully for complex tasks, and let it run more freely for everyday changes.
- Context management keeps long sessions from spiraling out of control — check `/context` when needed, and tidy up the session with `/compress` or `/clear`.
- QWEN.md turns project knowledge into memory that persists across sessions, so the Agent still knows the project's rules the next time it starts.
- Skills lock in expert experience as reusable workflows, and can keep being refined based on failure cases and evaluation results.
- Harness Engineering brings all these mechanisms together into a single external environment, so the model isn't just generating code — it's working within boundaries, checks, and human feedback.
- The five anti-patterns are a reminder: the Agent is an efficient collaborator, but judging whether a result is correct and whether a change should be merged remains a human responsibility.

All of this answers the question of "how do you use a Coding Agent well." The next lesson goes further: on top of Qwen Code, you'll fill in the standards, samples, checks, records, and stop conditions for a concrete business task, so the Agent doesn't just complete one task — it keeps improving at a whole category of tasks according to your standards.

## 🔥 Quiz

### 🔍 Multiple Choice 3.7.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Regarding the "understand first, then plan, then code, then commit" workflow, which of the following is the most sensible practice❓</b>

- A. Always strictly follow all four E → P → C → C stages every time, without skipping any of them
- B. For a simple single-file change, you can skip Explore and Plan and go straight to the Code stage
- C. Once the Agent generates a plan in the Plan stage, execute it directly without human review
- D. In the Commit stage, just let the Agent commit directly, without checking the list of staged files

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
This workflow is a flexible framework, not a rigid process. For simple tasks, just tell the Agent what to do directly; but for complex tasks involving multiple files and multiple steps, understanding and planning first significantly reduces rework. Option C is wrong: the plan must be reviewed by a human. Option D is wrong: you must check the list of staged files before committing.
</div>
</details>

### 🔍 Multiple Choice 3.7.2
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Every new session, the Agent writes DashScope's API address as the OpenAI default address, and you've already corrected it three times. What's the most sensible way to fix this❓</b>

- A. Manually remind the Agent at the start of every session
- B. Write the correct API address and an example of the mistake into the "Common Pitfalls" section of QWEN.md
- C. Create a custom command `/fix-url` and trigger it manually whenever you spot the error
- D. Create a Skill that has the Agent automatically check the API address while writing code

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
This is a project constraint that holds true across every session, and it's a specific mistake the Agent keeps repeating — this fits QWEN.md's principle of "writing memory in response to failure" exactly. Once written in, the Agent loads it every time it starts. Option C is a remedy after the fact, not prevention. Option D is overkill for this.
</div>
</details>

### 🔍 Multiple Choice 3.7.3
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>While developing a Gradio UI, /context shows context usage at 75%. What's the most sensible action to take now❓</b>

- A. Immediately run `/clear` to wipe out all context
- B. Run `/compress` to compress the conversation history, then continue with the current task
- C. Ignore the usage level and keep developing until the Agent starts noticeably forgetting things
- D. Close the terminal and restart Qwen Code

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
When context usage is high but the task isn't finished yet, `/compress` keeps the key information and compresses redundant history, freeing up space to keep working. Option A is too drastic — you lose all session context and have to re-explain the current task to the Agent. Option C is risky — once the context overflows, the Agent may lose its memory of important constraints.
</div>
</details>

### 🔍 Multiple Choice 3.7.4
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Which extension mechanism should each of the following four needs use?<br>① Checking for hardcoded API keys before every commit<br>② Looking up the latest LlamaIndex documentation while writing code<br>③ The project must follow the PEP 8 convention<br>④ Automatically checking instructional-writing conventions when reviewing course content❓</b>

- A. ① Skill ② MCP ③ QWEN.md ④ Custom command
- B. ① Custom command ② MCP ③ QWEN.md ④ Skill
- C. ① Custom command ② Skill ③ QWEN.md ④ MCP
- D. ① QWEN.md ② MCP ③ Skill ④ Custom command

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
Using the decision tree from section 5.4 — ① is a fixed check process, manually triggered → custom command. ② requires calling an external service, with the Agent deciding on its own when to consult it → MCP. ③ is a project constraint that holds true across every session → QWEN.md. ④ is domain-expert knowledge that should load automatically when the Agent recognizes a relevant task → Skill.
</div>
</details>

### 🔍 Multiple Choice 3.7.5
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Which of the following counts as the "committing without verifying" anti-pattern❓</b>

- A. After the Agent modifies rag.py, you run the existing test cases, confirm they pass, and commit
- B. After the Agent generates app.py, you start the Gradio app, manually test three scenarios, and then commit
- C. After the Agent modifies evaluate.py, you check the diff, decide the change looks reasonable, and commit directly
- D. After the Agent creates a new .gitignore file, you check its contents to confirm Key.json is included, and commit

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: C**
📝 **Explanation**:
Option C only checks that the diff "looks reasonable," without actually running the code to verify the change is correct. evaluate.py involves RAGAS evaluation logic, and reviewing the diff alone can't catch problems that only surface at runtime (like a parameter type mismatch). The core problem with "committing without verifying" isn't "not looking at the diff" — it's "assuming the code is correct without running or testing it."
</div>
</details>

### 🔍 Multiple Choice 3.7.6
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Regarding QWEN.md's three-level configuration hierarchy, which statement is correct❓</b>

- A. A directory-level QWEN.md's content completely overrides a project-level QWEN.md's content
- B. A global QWEN.md is a good place to put a specific project's tech stack and module structure information
- C. The three levels load in the order "global → project → directory," and the more specific level has higher priority
- D. If the project-level and directory-level QWEN.md files conflict, the Agent will prompt the user to choose

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: C**
📝 **Explanation**:
The three-level configuration is designed to go "from general to specific," with more specific configuration taking priority. A is wrong: the directory level adds to and overrides the project level — it doesn't replace it entirely. B is wrong: global configuration is for content that's general across projects (like personal coding preferences). D is wrong: configuration conflicts are resolved automatically by priority — the user doesn't need to choose manually.
</div>
</details>

### 🔍 Multiple Choice 3.7.7
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Regarding the five-step method for writing a Skill, which step is most critical❓</b>

- A. Step 3: writing the first draft of the Skill — the more complete the rules, the better
- B. Step 1: have the Agent run unaided once, and record the failure cases as a baseline
- C. Step 5: iterate repeatedly until the Skill perfectly covers every scenario
- D. Step 4: verify with a new session — make sure the Agent has loaded the Skill

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
Step 1 (establishing a baseline) is the foundation of the whole method. Without a baseline, you can't tell whether the Skill actually improved the Agent's behavior — you're just going on a "feeling" that it got better. Skipping step 1 and writing the Skill directly often produces rules that "look reasonable but don't actually solve the problem." The problem with option A is chasing completeness instead of targeting — a Skill should first cover the most critical failure scenarios, not attempt to be an encyclopedia.
</div>
</details>

### 🔍 Multiple Choice 3.7.8
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>From a Harness Engineering perspective, what role should QWEN.md play❓</b>

- A. The project's complete technical documentation — the more detailed, the better
- B. A directory and navigation aid for project knowledge — stay lean, and point to more detailed sources of information
- C. The Agent's sole source of knowledge — every rule must be written in QWEN.md
- D. A configuration file written once, with no need for further updates

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
QWEN.md is better suited to serving as a table of contents for project knowledge, not an encyclopedia. It should stay lean, providing only project background and pointers to "where to find more detailed information." Detailed design docs, coding conventions, and architectural decisions belong in separate files, which the Agent reads on demand. Option A crowds out context. Option C ignores the role that Skills and standalone docs play. Option D violates the principle of "updating continuously in response to problems."
</div>
</details>

---

## ✉️ Feedback

Thank you for taking Alibaba Cloud's LLM ACP certification course. If you have thoughts on what worked well or what could be improved, we'd love for you to [share your feedback through this survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie).

Your critiques and encouragement are what drive us forward.
