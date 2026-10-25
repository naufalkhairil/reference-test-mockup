# 3.2 Teaching the Agent to Plan & Execute

## 🚄 Preface

The Agent has learned to use tools, but when facing complex tasks it easily makes two kinds of mistakes: one is not verifying its own output (hallucination), and the other is trying to do everything in one go, which leads to it getting increasingly disorganized. In this lesson, you'll learn how to make the Agent reflect first, then plan, then execute — evolving from "brute-force doing" to "doing things methodically."

## 🍁 Course Objectives

**You will learn:**
- Understand the two modes of Agent self-reflection: self-feedback and external verification
- Master the five orchestration patterns of workflows: pipeline, branching, parallel, MoA, human-in-the-loop
- Plan & Execute: the Agent plans first, then executes — code as plan
- Judge when to use a fixed process and when to use autonomous planning

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

## 1 Teaching the Agent to Reflect
### 1.1 The course gets accidentally modified
A colleague wrote an interactive course in notebook format, containing some executable Python code. To make the course's language more vivid, you asked the bot to help polish the whole document's language style.

After polishing, the course's language became smoother and its structure clearer. But when the colleague tried to run the code examples in the course, they found a critical problem:

```python
# The course's original code
def get_user_data(usr_id: str):
  # ... some logic ...
  return f"Data for {usr_id}"

# Runs fine
print(get_user_data(usr_id="u-123"))
```

While "optimizing" the language style, the bot quietly "fixed" the code:

```python
# The code after the Agent polished it
def get_user_data(user_id: str):
  # ... some logic ...
  return f"Data for {user_id}"

# Runtime error!
# print(get_user_data(usr_id="u-123"))
# TypeError: get_user_data() got an unexpected keyword argument usr_id
```

The bot thought `user_id` was more standard than `usr_id`, so it helpfully "optimized" the function definition — but this caused the code that calls the function to error out, because the argument name at the call site wasn't changed along with it.

### 1.2 The LLM's hallucination

How should you solve this problem? The most direct idea is to tell the bot to "be careful." Try adding a warning to its instruction (System Prompt):

```
You are a top-tier course author, responsible for polishing courses in Jupyter Notebook format.
Please optimize the text to make it more engaging.
**Important: absolutely do not modify any content inside code blocks, including variable names, parameter names, and function calls.**
```
But this doesn't work well, because you can't cover every possible scenario by listing prohibitions. Even if you explicitly forbid certain modifications, the LLM still has some probability of "helpfully" changing originally-correct content into something wrong.

The reason is that, because the LLM hallucinates, each of its generations may introduce new errors, and it lacks an inherent mechanism for verification and correction. This kind of "optimization" isn't limited to variable names; it can also happen with
- command-line arguments (changing `-p 8080` to `--port 8080`)
- API version numbers (updating `v1/users` to `v2/users`)
- example values (replacing the demo IP address `192.168.1.10` with `127.0.0.1`)

and anywhere else it deems "not standard enough." In the end, a course that has been "optimized" but is now riddled with errors will trap learners in an endless debugging loop.

So you'll naturally think of another approach: have the LLM check its own output before producing it, just as, during an exam, a human checks their answers before handing in the paper. This is exactly one of the methods the industry currently uses to solve this kind of problem — we call it **Reflection**.

### 1.3 The two modes of reflection
#### 1.3.1 Mode one: Self Review

To implement reflection, the most direct idea is to have the model examine its own output. There are two implementations here: one is simple but limited in effect, and the other is more complex but noticeably more effective.

##### 1.3.1.1 Method one: single-step instruction-based reflection

This is the easiest method to think of: you try, in a single model call, to instruct the model via the prompt to reflect while generating the answer.

```
## Role
You are a top-tier course author.

## Task
1. Polish the course's language, and output the full polished text.

2. Reflect on the polished content:
    - Whether it conforms to writing standards.
    - Besides the language, whether any other content was accidentally modified.
Output the reflection result and revision suggestions.

3. Revise the course against the suggestions, and output the full revised text.

## Course draft
{original_notebook_content}
```

*Figure (translated): single model call with generation, reflection, and correction all-in-one.*

```text
[Course draft] -> [Single LLM call: generate + reflect + correct (all-in-one)] -> [Output result]
```

This method has its advantages: the model can spot and fix problems in a timely manner during generation, while keeping the context coherent and reducing the overhead of multiple round-trips.

But it also has an obvious flaw: when reflection and generation are bound together, the model easily performs self-verification with the same cognitive bias, falling into a "self-justifying" trap. For example, if it changed `usr_id` to `user_id` in the first step, then in the second step's reflection it will very likely consider this a "standardization improvement" rather than an error.

##### 1.3.1.2 Method two: two-step "generate-feedback"

You can also separate the reflection process, splitting the task into two model calls — one responsible for generating, the other for reviewing.

```
# First call (Writing Agent)
You are a top-tier course author, responsible for polishing courses in Jupyter Notebook format. Please optimize the text to make it more engaging.

[Course draft]:
{original_notebook_content}

# Second call (Technical Review Agent)
You are a strict technical reviewer. Your task is to review the polished course content and ensure:
1. The polished course conforms to writing standards.
2. Technical content such as code, config, and data was not accidentally modified.

Please compare [Original content] and [Polished content]:
- If only the wording was changed and the technical content such as code is completely identical (or has only non-functional changes like comments and formatting), answer "Pass."
- If you find any technical content was modified (e.g. code logic, variable names, parameters, config items), answer "Fail," and point out exactly which content was accidentally modified.

[Original content]:
{original_notebook_content}

[Polished content]:
{draft_content}

```

*Figure (translated): writer + reviewer.*

```text
[Course draft] -> [Writing Agent: generate content] -> [Review Agent: independent perspective check]
                      ^                                        |
                      |                (feedback: issues)      | (passed)
                      └────────────────────────────────────────┴──────► [Output result]
```

Because the review Agent's perspective differs from the writing Agent's, this method effectively avoids most role bias. You can even set up multiple specialized review Agents — fact review, logic review, style review, security review — which not only improves the comprehensiveness of the review but also facilitates later A/B testing and metric statistics.

But this method also has an obvious cost: each additional review Agent adds one more model call, consuming more tokens.

> **Further reading: cost and optimization**
>
> **Is this cost worth it?**
>
> The "generate-feedback" loop seems to increase the number of calls, but we can't simply compare the cost of "one high-quality output" with "one low-quality output." A fairer comparison is: to obtain a "usable" answer, what is the total cost of each path?
>
> If a single call can't effectively solve the problem, then no matter how low its cost, it's a waste. Conversely, through a two-step "generate-feedback" call, letting a mid-tier model reach 95% of a top-tier model's effect achieves nearly the same business value at a lower cost.
>
> **How to further reduce cost?**
>
> In the "generate-feedback" loop, the original course document is passed repeatedly across multiple model calls — the writing Agent needs it, the review Agent needs it, and the correction stage may need it again. If the document is long (e.g. a full course with dozens of code examples), this repetition brings significant token consumption.
>
> Alibaba Cloud Model Studio provides a [Context Cache](https://help.aliyun.com/zh/model-studio/context-cache) mechanism to solve this: on the first call it caches the shared content (such as the original document), and subsequent calls that detect the same prefix reuse it directly; the cache-hit portion is billed at 20% of the standard unit price.
>
> You can organize the prompt structure like this:
> ```
> [Cached part - identical across all calls]
> ## Original course document
> {very long original notebook content}
>
> [Variable part - different each call]
> ## Task
> {writing instruction / review instruction / correction instruction}
>
> ## Content to process
> {polished draft / review feedback, etc.}
> ```
>
> This way, the original document's tokens are billed at the standard unit price on the first call, and enjoy the cache discount in the subsequent review and correction steps, significantly reducing the total cost of multiple calls.

Note that you should let the review Agent be responsible only for "finding problems," not "rewriting directly." If you let it modify the content directly, it may damage the original's intended expression or introduce new errors.

So it's best to feed the review result (`review_result`) back to the writing Agent and let it continue revising the answer based on the feedback. This forms a "generate-feedback" loop, and the bot's answer fidelity improves significantly.

##### 1.3.1.3 The flaw of self-feedback

Self-feedback is better suited to static, text-level comparison (such as checking whether code was accidentally modified), but when you need to verify whether code actually runs, this mode performs poorly.

This is because the LLM is good at judging whether code "looks reasonable," but it can't perform precise semantic verification like a compiler. More critically, the model can't truly execute code — it can't see run logs, can't catch exceptions, and can't perceive dependency version conflicts or environment configuration issues.

To solve this, we need to introduce an external feedback mechanism.

#### 1.3.2 Mode two: External Feedback
##### 1.3.2.1 Using tools to verify results
The core idea of external feedback is: put the LLM's generated result into a real environment to execute, then feed the execution result (success/failure, error message, test report, etc.) back to the model, so it iterates and corrects based on these grounded facts.

If self-feedback is "I think whether I did it right," then external feedback is "the facts prove whether I did it right."

Back to our Jupyter Notebook course-polishing scenario. Suppose the course contains some code examples, and we want to ensure the code still runs correctly while polishing the wording.

This requires combining the **Tool Use** you learned in the previous chapter with the reflection mechanism. Here, the most direct source of external feedback is a code-execution tool. AgentScope has a built-in, powerful `execute_python_code` tool, which provides the Agent with a safe code-interpreter environment so it can actually execute Python code and obtain results or error messages.

The specific workflow is as follows:
1.  **Generate**: the writing Agent polishes the document and outputs notebook content containing code.
2.  **Interact with the external tool**: the system automatically extracts the code blocks and calls the `execute_python_code` tool to try to execute them.
3.  **Obtain external feedback**: the tool returns the execution result; suppose it hits an error: `TypeError: get_user_data() got an unexpected keyword argument 'usr_id'`.
4.  **Correct**: the Agent receives this error feedback and now clearly knows what went wrong with the code. Based on this feedback, it generates the corrected code.

*Figure (translated): self-correction loop driven by code-execution feedback.*

```text
[User input / document] -> [Writing Agent generates notebook (with erroneous code)]
                                     |
                                     v
                            [Code interpreter executes code]
                                     |
                                     v
[Agent corrects: reverts the wrong change to user_id] <- (external feedback: TypeError, usr_id)
                                     |
                                     v
                          [Final correct notebook]
```

Below is a simple example implemented with AgentScope. AgentScope's built-in `execute_python_code` tool doesn't require manually creating a tool function; you just register it via `toolkit.register_tool_function(execute_python_code)`.

```python
"""
Implementing the reflection mechanism with external feedback using AgentScope (simplified)
Scenario: polishing a Jupyter Notebook course, verifying code correctness via a code interpreter
"""

import asyncio
import os
from textwrap import dedent

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit, execute_python_code

# ============================================================
# Create the writing Agent (equipped with the code-interpreter tool)
# ============================================================

def create_writer_agent() -> ReActAgent:
    """Create the writing Agent responsible for polishing course content"""

    # Create a toolkit and register the built-in code-execution tool
    toolkit = Toolkit()
    toolkit.register_tool_function(execute_python_code)

    writer = ReActAgent(
        name="Writer",
        sys_prompt=dedent("""You are a technical course author, responsible for polishing Jupyter Notebook courses.

            Task requirements:
            1. Optimize the text so it reads more smoothly and vividly
            2. **Absolutely do not modify variable names, function names, or parameter names in the code**
            3. After polishing, use the execute_python_code tool to verify all code blocks
            4. If code execution fails, check whether you accidentally modified the code and fix it

            Remember: only change the wording, not the code logic!
        """),
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            stream=False,
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
        max_iters=10,  # up to 10 iterations (example config; adjust based on task complexity and cost budget in practice)
    )

    return writer

# ============================================================
# Main flow
# ============================================================

async def main():
    """Main function - demonstrate the reflection mechanism with external feedback"""

    # Original course content (containing the "non-standard" variable name usr_id)
    original_notebook = """
# Python Function Example Course

In this section, learn how to define and call functions.

## Defining a function

def get_user_data(usr_id: str):
    return f"Data for {usr_id}"

## Calling a function

print(get_user_data(usr_id="u-123"))

## Summary

You've learned to define and call Python functions.
"""

    print("="*60)
    print("Original course content:")
    print("="*60)
    print(original_notebook)

    # Create the Agent
    writer = create_writer_agent()

    # Send the polishing request
    user_msg = Msg(
        name="user",
        content=dedent(f"""Please polish the following course content, with these requirements:

            {original_notebook}

            1. Make the wording more vivid and easy to understand
            2. **Do not modify variable names or function names in the code**
            3. After polishing, use execute_python_code to verify the code runs
            4. If it errors, it means you may have changed the code incorrectly; please fix it
        """),
        role="user"
    )

    print("\n" + "="*60)
    print("The Agent starts working...")
    print("="*60)

    # The Agent automatically does: polish -> verify -> correct -> verify again
    result = await writer(user_msg)

    print("\n" + "="*60)
    print("Final output:")
    print("="*60)
    print(result.get_text_content())

try:
    await main()
except NameError:
    asyncio.run(main())
```

This way, the Agent can use an external tool to verify its output, achieving efficient, precise self-correction.

##### 1.3.2.2 Other verification methods

Besides code execution, this mode can also be applied to other scenarios requiring objective facts:

*   **Scenario: optimizing Matplotlib charts in a research paper**
    *   **Problem**: you ask the Agent to generate data-visualization code for a research paper. The Agent generates a "reasonable"-looking piece of Matplotlib code with correct data-processing logic and plotting-function calls. But code that runs doesn't mean the chart looks good — the actually-rendered figure may have issues like overlapping axis labels, a legend blocking data points, fonts too small to read, or colors unsuitable for printing.
    *   **External-feedback solution**: the system calls the **code interpreter** tool to execute the Matplotlib code and returns the generated image file. **The Agent receives the actually-rendered chart via visual input** and can intuitively spot visual problems (e.g. "the x-axis labels overlap," "the legend blocks a key data point"), then adjust the code parameters accordingly (such as `plt.xticks(rotation=45)` to rotate labels, `bbox_to_anchor` to adjust the legend position, increasing `fontsize`, etc.). This "generate-render-adjust" loop ensures the final chart meets the quality requirements for academic publishing.

*   **Scenario: checking the answer to a complex calculation problem**
    *   **Problem**: in a quantum-mechanics course, you need to write an exercise: "Calculate the ground-state energy, in joules, of an electron (mass ≈ 9.11e-31 kg) confined in a one-dimensional infinite potential well of length 1 nanometer (1e-9 m). (Planck's constant h ≈ 6.626e-34 J·s)" The Agent may err in the solution steps due to the complex exponent arithmetic.
    *   **External-feedback solution**: the system identifies the expression to compute `(1**2 * (6.626e-34)**2) / (8 * 9.11e-31 * (1e-9)**2)` and hands it to the **code interpreter** or **calculator** tool to execute. The tool returns the precise numeric result. This objective computation result serves as feedback, letting the Agent correct the final answer.

*   **Scenario: structured-output validation**
    *   **Problem**: you ask the Agent to generate a config file conforming to a specific JSON Schema, but it may omit required fields or use the wrong data types.
    *   **External-feedback solution**: the system uses a library like Pydantic to validate the generated JSON. When the output doesn't conform to the Schema, the validator returns a detailed error report (e.g. "field 'timeout' should be an integer, not a string"). This objective, precise feedback lets the Agent correct the output until it fully conforms to the predefined structure. This "generate-validate-feedback" loop is one of the most common and fundamental applications of the reflection mechanism in practice.

Finally, how do you choose between these two feedback modes? It depends on your specific needs, budget, and acceptable error rate. For example, if you're just polishing a blog article with no code, then you may not need reflection at all. But if you're revising an interactive course containing dozens of code examples, then introducing an "external feedback" loop based on a code interpreter is a necessary investment to ensure document quality and avoid publishing accidents.

### 1.4 Summary

Let's recap what you learned in this section:
- **The limitation of direct instructions**: directly asking the LLM in the prompt to "be more careful" or "don't change the code" usually doesn't work well, because the model aims to generate "more reasonable" text and sometimes "does bad with good intentions."
- **The core idea of "reflection"**: mimicking human "metacognition," giving the model a chance to examine and evaluate the complete content it has already generated, thereby finding and correcting errors. This is more reliable than simple instructions.
- **Self-feedback vs. external feedback**: "self-feedback" is having another Agent check the draft, suitable for subjective evaluation; "external feedback" is using tools (such as a code interpreter) to verify results, suitable for scenarios requiring objective facts.
- **Engineering implementation: the "generate-feedback" loop**: an effective way to implement "reflection" is to use multiple calls — the first generates a draft, and subsequent calls are responsible for evaluating the draft, providing feedback, and revising based on the feedback.

## 2 Building Workflows

### 2.1 A single Agent handling a complex process

Monday morning, you receive this message:

> "The 'Intro to Python Data Analysis' course submitted last Friday needs to go live ASAP. Can you run it through the standard review process with that AI assistant of yours? Namely: 1) all code examples must run 2) technical concepts must have no serious errors 3) the difficulty gradient should suit absolute beginners 4) the language style should conform to our standards. Need results before 3 PM."

You think, this task is pretty simple. Your bot can already verify code, so handling this "combined task" shouldn't be hard. So you stuff all the requirements into one prompt:

```plaintext
prompt = """Please complete the following course review task:
1. Verify all Python code runs correctly
2. Check the accuracy of technical concepts (especially the explanations of pandas and numpy usage)
3. Evaluate whether the difficulty curve suits programming beginners
4. Adjust wording per our style guide (avoid colloquialisms like "very easy" and "super")
Please give a complete review report."""
response = agent.run(prompt + course_content)
```

A few minutes later, you open the returned result:

- The Agent did verify the code, but while "optimizing the language" it also changed `super()` in the code to `parent()`, because it thought "super is too colloquial."
- It found an error in Chapter 3's explanation of DataFrame, but after correcting it introduced an even more serious error: saying "DataFrame is a Python built-in data structure."
- As for the difficulty evaluation? By the time it processed the 50th question, it seemed to have forgotten about it.

You try to have it redo it; this time it remembers to evaluate difficulty but misses half the code verification. The third time, it does all the tasks but "corrects" an originally-correct concept into a wrong one.

The problem is obvious: having a single Agent simultaneously take on multiple complex tasks is like having one intern answer four phones at once — one of them always goes wrong.

### 2.2 Failure analysis
#### 2.2.1 The forgetting effect of the attention mechanism

When generating a reply, the LLM's "attention" to information at different positions is uneven. By the time the Agent processes the fourth task (polishing language), the details of the first task (code verification) have already been diluted by a lot of intermediate information.

Concretely: the model "forgets" the constraints it verified earlier when revising later. For example, you already verified `super()` is correct Python syntax, but in the language-polishing stage, the model may replace it because the word "super" looks colloquial, causing the code to error.

This isn't simply "poor memory"; it's an inherent limitation of the self-attention mechanism in the Transformer architecture — the attention weights between tokens get diluted as the sequence length increases.

#### 2.2.2 The cascading amplification of errors

When executing multiple tasks sequentially, an early error becomes the "factual basis" for subsequent processing. Suppose the Agent, during the fact-checking stage, wrongly "corrects" the definition of DataFrame (e.g. saying it's built-in); this error enters the subsequent context.

Worse, the model continues reasoning based on this wrong "fact":
- Since DataFrame is "built-in," there's no need to import pandas
- So the import statement gets deleted from the teaching example
- All the code examples become invalid

This error propagation isn't linear but exponential — one small error triggers a chain of wrong decisions.

#### 2.2.3 Flattened understanding vs. structured requirements

Your complex requirement is actually a task graph with an inherent structure:
- Some tasks can run in parallel (code checking and style checking don't interfere with each other)
- Some tasks have dependencies (you must understand the concepts before you can evaluate the difficulty)
- Some tasks need a global view (evaluating the overall difficulty curve)

But to the model, your prompt is just a flat token sequence. It can't automatically recognize this structural relationship; instead it tries to solve a fundamentally graph-structured problem with a linear generation process.

It's like having someone play four games with different rules at once, without telling them which can be played in turns and which must be played simultaneously.

Ultimately, relying on a single Agent to perform a complex review is like building a house without a construction blueprint — every brick you lay may affect the structural stability of the entire building.

### 2.3 Several patterns of workflows

Since having one Agent do everything doesn't work, you'll naturally think of another approach: just as when managing a project you break it into several subtasks assigned to different people or done at different times. This "Divide and Conquer" idea is exactly the core of solving this kind of problem.

We call this pattern — breaking a complex task into multiple nodes and defining the execution relationships between them — a **Workflow**.

The key to building a workflow is understanding the business and making the most appropriate task decomposition. Below, we'll start from the simplest pattern and step by step build a powerful workflow capable of handling complex course review.

#### 2.3.1 Pattern one: Pipeline

This is the most basic, most intuitive workflow. It decomposes a task into multiple fixed steps executed in order. The output of the previous step strictly serves as the input to the next, and the whole process is like a factory assembly line — one-directional and immutable. The RAG Q&A bot you built earlier in this course is a perfect embodiment of this pattern.

*Figure (translated): the pipeline pattern — one-directional and immutable.*

```text
[Course draft] -> [Code extractor] -> [Code validator] -> [Report generator] -> [Final report]
```

```python
"""
Pattern one: Pipeline - Scenario: a quick course-check process
Goal: the user submits a course draft, and the system completes, in order,
1) extract the code from the course -> 2) verify the code's executability -> 3) generate a code-check report
"""
import asyncio
from agentscope.message import Msg
from agentscope.pipeline import sequential_pipeline
from chatbot.agent import create_agent, disable_console_output

async def run_pipeline() -> None:
    # Node A: code-extraction Agent
    # multi_agent=True is a config in AgentScope that ensures the communication format between Agents is compatible;
    # it's the recommended setting for building workflows and multi-agent systems.
    code_extractor = create_agent(
        name="Code Extractor",
        sys_prompt=(
            "You are a code-extraction expert. From the course text provided by the user, precisely extract all Python code blocks. "
            "Output only the code, without any other explanation."
        ),
        model_name="qwen-flash",
        multi_agent=True,
    )

    # Node B: code-verification Agent (can call external tools)
    code_validator = create_agent(
        name="Code Validator",
        sys_prompt=(
            "You are a code-execution and verification expert. You will receive code text. Please use a code interpreter to execute it. "
            "Report whether the code runs successfully, and if not, point out the error."
        ),
        # Here you can configure code_validator to use the code-interpreter tool you learned in section 2
        model_name="qwen-plus",
        multi_agent=True,
    )

    # Node C: report-generation Agent
    report_generator = create_agent(
        name="Report Generator",
        sys_prompt=(
            "You are a review-report writing assistant. Based on the previous step's code-verification result, generate a concise, clear check report for the course designer."
        ),
        model_name="qwen-max",
        multi_agent=True,
    )

    agents = [code_extractor, code_validator, report_generator]
    disable_console_output(agents)

    course_draft = (
        "This is our new course. The first part is `print('Hello, World!')`. "
        "The second part is a buggy piece of code `x = 1 / 0`."
    )
    result = await sequential_pipeline(
        agents=agents,
        msg=Msg("user", course_draft, "user"),
    )

    print("=" * 50)
    print("Pipeline output:")
    print(result.content)
    print("=" * 50)

async def main() -> None:
    await run_pipeline()

await main()
```

Its core advantage is that it's **simple, predictable, and easy to debug**. Because the process is fixed, when a problem occurs you can easily pinpoint which stage (extraction, verification, or report) went wrong. This determinism is crucial in many enterprise-level applications.

It's suited to tasks with very fixed business processes and single-purpose logic. For example:

*   **Preliminary code check**: extract the code first, then run verification.
*   **Document translation**: extract the text first, then translate, then format the output.
*   **New-employee onboarding material distribution**: generate the welcome email first, attach the company documents, then send.

The pipeline's rigidity is its biggest advantage and its most fatal flaw. It can't handle any change outside the process. Faced with a request like "help me evaluate how interesting this course is," this pipeline designed for "code checking" would be completely at a loss, because it has no ability to handle that intent. It assumes all inputs should follow the same processing logic.

#### 2.3.2 Pattern two: Branching

To overcome the pipeline's rigidity, you need to introduce decision-making ability. The core of the branching pattern is to set up a "router" or "dispatch center" at the start or key nodes of the workflow. This decision node analyzes the input (e.g. the user's review request) and, like a traffic officer, directs the task to different preset processing paths (i.e. different pipelines or experts).

*Figure (translated): the router pattern.*

```text
                             ┌──► [Code quick-check expert] ──────┐
[Review request] -> {Task distributor / router}                  ├──► [Chief reviewer] -> [Output result]
                             └──► [Language polishing expert] ────┘
```

```python
"""
Pattern two: Branching - Scenario: course-review task dispatch
The routing Agent reads the review request and chooses one of the following branches:
1) code_check: only quickly check the code
2) style_guide: polish the language per the style guide
3) full_review: perform a comprehensive multi-dimensional review
"""
import asyncio
from typing import Literal
from pydantic import BaseModel, Field
from agentscope.message import Msg
from chatbot.agent import create_agent, disable_console_output

class RouteChoice(BaseModel):
    choice: Literal["code_check", "style_guide", "full_review", None] = Field(
        description="Choose a branch based on user intent: code_check/style_guide/full_review/None"
    )
    extra: str | None = Field(default=None, description="A brief description of the task")

async def branch_code_check(user_msg: Msg) -> Msg:
    agent = create_agent(
        name="Code Quick-Check Expert",
        sys_prompt="You are a code quick-check expert. Based on the user's need, quickly verify whether the code snippets in the course run.",
        model_name="qwen-plus",
        multi_agent=True,
    )
    disable_console_output([agent])
    return await agent(user_msg)

async def branch_style_guide(user_msg: Msg) -> Msg:
    agent = create_agent(
        name="Language Polishing Expert",
        sys_prompt="You are a language-polishing expert. Based on the company style guide, rewrite and polish the course text provided by the user.",
        model_name="qwen-max",
        multi_agent=True,
    )
    disable_console_output([agent])
    return await agent(user_msg)

async def branch_full_review(user_msg: Msg) -> Msg:
    agent = create_agent(
        name="Chief Reviewer",
        sys_prompt="You are the chief reviewer. Inform the user that you will launch a comprehensive review process covering code, facts, and pedagogy.",
        model_name="qwen-flash", # use a lightweight model to simulate the notification action of launching the process
        multi_agent=True,
    )
    disable_console_output([agent])
    return await agent(user_msg)

async def run_branching() -> None:
    router = create_agent(
        name="Review Task Dispatcher",
        sys_prompt=(
            "You are the dispatcher for course-review tasks. Choose a branch based on the user input:\n"
            "- If they just want to check code, output code_check\n"
            "- If they want to polish the writing, output style_guide\n"
            "- If they need a complete, comprehensive review, output full_review\n"
            "Express your choice only through structured output, without a body answer."
        ),
        model_name="qwen-plus",
        multi_agent=False,
    )

    user_text = "This course is almost done — help me check it comprehensively, especially the code and the difficulty."

    res = await router(
        Msg("user", user_text, "user"),
        structured_model=RouteChoice,
    )
    choice = res.metadata.get("choice")

    if choice == "code_check":
        out = await branch_code_check(Msg("user", user_text, "user"))
    elif choice == "style_guide":
        out = await branch_style_guide(Msg("user", user_text, "user"))
    elif choice == "full_review":
        out = await branch_full_review(Msg("user", user_text, "user"))
    else:
        # Default to full review to keep the example runnable
        out = await branch_full_review(Msg("user", user_text, "user"))

    print("=" * 50)
    print(f"Branch choice: {choice}")
    print(out.content)
    print("=" * 50)

async def main() -> None:
    await run_branching()

await main()
```

Compared with a single pipeline, branching makes the system **more flexible and smarter**. It lets one application handle many different types of tasks, greatly expanding its applicability and improving the user experience.

Common application scenarios include:

*   **Intelligent customer service**: route to different processing flows based on the user's question type (course-content inquiry, platform technical support, purchase advice).
*   **Multi-tool Agent**: the Agent decides, based on the task need, whether to call the code interpreter, a search engine, or an internal knowledge base.
*   **Content-processing system**: call different review processes based on content type (video, text, interactive Notebook).

Branching is essentially "choose one of many," and it's still **serial**. It can handle "code checking" or "language polishing," but it can't handle a composite request of "checking code while polishing language." For our original complex request with four review dimensions, it can only go down one branch at a time, requiring the user to have multiple separate conversations with the bot — extremely inefficient.

#### 2.3.3 Pattern three: Parallel Execution

When a request can be decomposed into multiple independent subtasks, making them queue up and wait is a huge waste. The core idea of the parallel-execution pattern is "doing things simultaneously." It first breaks a complex task into multiple subtasks, then distributes these subtasks to different execution units (Agents or tools) to process at the same time, and finally aggregates all the results into the final output.

*Figure (translated): parallel review with a chief editor merge.*

```text
                 ┌─► [Code checker] ───────────┐
                 ├─► [Fact checker] ───────────┤
[Course content] ┼─► [Pedagogy evaluator] ─────┼─► [Chief editor: summary] ──► [Comprehensive report]
                 └─► [Style editor] ───────────┘
```

```python
"""
Pattern three: Parallel Execution - Scenario: full course review
Execute independent review subtasks in parallel: code check, fact check, pedagogy evaluation, language-style check.
The example uses fanout_pipeline to collect reports in parallel, then a synthesis Agent to aggregate.
"""
import asyncio
from typing import List
from agentscope.message import Msg
from agentscope.pipeline import fanout_pipeline
from chatbot.agent import create_agent, disable_console_output

async def run_parallel() -> None:
    # Four "expert" Agents for the independent subtasks
    code_checker = create_agent(
        name="Code Checker",
        sys_prompt="Verify whether the code in the course is correct and error-free, and give fix suggestions.",
        model_name="qwen-plus",
        multi_agent=True,
    )
    fact_checker = create_agent(
        name="Fact Checker",
        sys_prompt="Check whether the technical concepts and function explanations in the course are accurate and whether citations are proper.",
        model_name="qwen-plus",
        multi_agent=True,
    )
    pedagogy_evaluator = create_agent(
        name="Pedagogy Evaluator",
        sys_prompt="Evaluate the course's difficulty curve, the interest level of the examples, and the effectiveness of the exercises.",
        model_name="qwen-flash",
        multi_agent=True,
    )
    style_editor = create_agent(
        name="Style Editor",
        sys_prompt="Based on the company style guide, check and report on language style and terminology-consistency issues.",
        model_name="qwen-flash",
        multi_agent=True,
    )

    experts = [code_checker, fact_checker, pedagogy_evaluator, style_editor]
    disable_console_output(experts)

    course_content = "This is our newly-developed Intro to Python Data Analysis course..."
    msgs = await fanout_pipeline(
        agents=experts,
        msg=Msg("user", course_content, "user"),
        enable_gather=True,
    )

    # Aggregation Agent
    summarizer = create_agent(
        name="Editor-in-Chief",
        sys_prompt="Aggregate the review comments from multiple experts into a clearly-structured, well-organized overall review report.",
        model_name="qwen-max",
        multi_agent=True,
    )
    disable_console_output([summarizer])

    merged_text: List[str] = [m.content[0]["text"] for m in msgs]
    prompt = "\n\n".join(merged_text)
    summary = await summarizer(Msg("user", prompt, "user"))

    print("=" * 50)
    print("Parallel-execution output:")
    print(summary.content)
    print("=" * 50)

async def main() -> None:
    await run_parallel()

await main()
```

The most significant advantage is the **substantial improvement in efficiency**. The total time of the workflow is no longer the sum of all subtasks' times, but is determined by the longest-running subtask. This lets the Agent quickly respond to complex requests involving multiple steps.

Common application scenarios include:

*   **Handling complex review requests**: as in our course-review scenario, processing multiple dimensions like code, facts, pedagogy, and style at the same time.
*   **Generating comprehensive reports**: simultaneously pull information from different data sources (user feedback, market trends, competitor analysis), analyze each separately, and finally aggregate into a new-course proposal report.
*   **Batch data processing**: perform the same formatting or checking operation on multiple course units at the same time.

The premise of this pattern is that the subtasks are **mutually independent**. If there are dependencies between tasks (e.g. you must confirm the course's core knowledge points before you can evaluate whether its examples are apt), you can't simply parallelize. Moreover, it assumes each execution unit can give a "correct" answer, so it's not suitable for creative or decision-making tasks that require multi-party comparison and trade-offs to arrive at the best solution.

#### 2.3.4 Pattern four: Mixture-of-Agents (MoA)

Unlike parallel execution, which aims to improve efficiency, the core goal of the Mixture-of-Agents pattern is to **pursue ultimate quality, robustness, and creativity**. MoA's core idea is based on a key finding: **different LLMs have their own unique strengths and specialties, and when a model can reference the outputs of other models, it often generates a higher-quality response — a phenomenon called model "Collaborativeness."** MoA's approach is to have multiple **different LLMs** process **the same task** simultaneously, then have an aggregation model synthesize, analyze, and fuse all the outputs, producing a final result that far surpasses the level of any single model.

*Figure (translated): LLM debate — analysts generate, an aggregator picks the best solution.*

```text
                 ┌─► [Analyst 1: Qwen3-Max] ─────────┐
[Same task] ─────┼─► [Analyst 2: DeepSeek-V3.2] ─────┼─► [Aggregator: Qwen3-Max] ──► [Best solution]
                 └─► [Analyst 3: Kimi-K2-Thinking] ──┘
```

```python
"""
Pattern four: Mixture-of-Agents (MoA) - Scenario: distilling a course's core selling points
Use three different LLMs to process the same task in parallel, and fuse their outputs via an aggregation model,
leveraging inter-model Collaborativeness to produce a higher-quality result.
"""
import asyncio
from agentscope.message import Msg
from agentscope.pipeline import fanout_pipeline
from chatbot.agent import create_agent, disable_console_output

async def run_moa() -> None:
    # Use three different models as Proposers
    # Each model has its own strengths but processes the same task
    proposer1 = create_agent(
        name="Qwen3-Max",
        sys_prompt="You are a professional course analyst. Please distill the core selling points and promotional copy for the given course.",
        model_name="qwen3-max",
        multi_agent=True,
    )
    proposer2 = create_agent(
        name="DeepSeek-V3.2",
        sys_prompt="You are a professional course analyst. Please distill the core selling points and promotional copy for the given course.",
        model_name="deepseek-v3.2-exp",
        multi_agent=True,
    )
    proposer3 = create_agent(
        name="Kimi-K2",
        sys_prompt="You are a professional course analyst. Please distill the core selling points and promotional copy for the given course.",
        model_name="kimi-k2-thinking",
        multi_agent=True,
    )

    proposers = [proposer1, proposer2, proposer3]
    disable_console_output(proposers)

    task = (
        "This is a new 'AI LLM Applications for Web Developers' course. Please distill its core selling points and promotional copy."
    )
    msgs = await fanout_pipeline(
        agents=proposers,
        msg=Msg("user", task, "user"),
        enable_gather=True,
    )

    # The Aggregator receives all models' outputs and synthesizes the best result
    aggregator = create_agent(
        name="Aggregator",
        sys_prompt=(
            "Your task is to synthesize multiple LLMs' answers to the same question. "
            "These answers come from different models, each with strengths and weaknesses. Please critically evaluate them, "
            "identify their merits and shortcomings, then fuse this information to generate a high-quality, accurate, comprehensive final answer. "
            "Ensure your answer is clearly structured, logically coherent, and meets the highest standards of accuracy and reliability."
        ),
        model_name="qwen3-max",
        multi_agent=True,
    )
    disable_console_output([aggregator])

    # Merge all proposers' outputs and pass them to the aggregator
    merged = "\n\n".join([
        f"Model {i+1}'s answer:\n{m.content}"
        for i, m in enumerate(msgs)
    ])
    final = await aggregator(Msg("user", merged, "user"))

    print("=" * 50)
    print("MoA aggregated output:")
    print(final.content)
    print("=" * 50)

async def main() -> None:
    await run_moa()

await main()
```

**How Mixture-of-Agents (MoA) works**:

MoA divides the participating models into two roles:

1. **Proposers**: multiple different models process the same task in parallel, each generating a response. These models may excel in certain aspects (such as logical reasoning, creative expression, factual accuracy, etc.).
2. **Aggregator**: receives all proposers' outputs and, through critical evaluation, comparison, and fusion, generates a higher-quality final response.

Crucially, the aggregator doesn't simply pick the best answer; it extracts the merits from multiple responses and synthesizes a result that surpasses any single model.

**Advantages of MoA**:

*   **Leveraging model diversity**: different models have different training data, architectures, and optimization goals, causing them to perform differently on different tasks. MoA can leverage the strengths of multiple models at once.
*   **Enhanced robustness**: even if one model performs poorly on a particular input, the high-quality outputs of the other models guarantee a floor on the quality of the final result.
*   **Emergent quality**: research shows that even if the proposer models' individual output quality is low, the aggregated result may still surpass any single model — a direct manifestation of "model Collaborativeness."

MoA is suited to **open-ended or creative tasks** that have no unique standard answer, demand extremely high result quality, and carry huge value.

*   **Core copywriting**: such as course slogans, promotional copy, brand stories.
*   **Complex decision analysis**: synthesizing analysis reports from different models to form a more comprehensive new-course-direction decision recommendation.
*   **Code generation and optimization**: have different models each generate a piece of example code, then have a review Agent select the best or perform a fused refactor, to achieve the best teaching effect.

However, MoA's main constraint is **cost**. Calling N expert Agents brings N times the compute cost and corresponding latency. This is a strategy of trading resources for quality, so it must be used at key stages where "the best steel goes on the blade's edge"; it's not suitable for routine, cost-sensitive daily tasks.

**Advanced: Multi-Layer MoA**

The MoA shown above is a "2-layer structure": the first layer has multiple experts processing the task in parallel, and the second layer has one aggregator synthesizing all the experts' outputs. However, MoA can also be **extended to 3 or more layers**, continuously refining and optimizing the result through multiple rounds of iteration, thereby achieving even better output quality than single-layer MoA.

**The core idea of multi-layer MoA** is: take the previous layer's aggregated output as the input to the next layer, hand it again to multiple experts to examine, critique, and improve, then have a new aggregator perform a higher-level synthesis. This "iterative refinement" process is similar to multiple rounds of review and polishing in a human team — each round can find problems missed in the previous round and spark new ideas, ultimately reaching a level of quality hard to achieve in a single round.

**Advantages of multi-layer MoA**:

*   **Further quality improvement**: the second- and third-layer experts can perform deeper analysis and optimization on top of the first layer's result, just as an editorial team does multiple rounds of polishing on a draft.
*   **Enhanced error-correction**: even if some first-layer experts make mistakes, later-layer experts have a chance to find and correct these errors, making the final result more reliable.
*   **Emergent creativity**: multi-layer interaction may produce a "1+1>2" effect; the collision of ideas among experts at different layers may spark innovative solutions that no single layer could produce.

**Implementation points**:

*Figure (translated): three-layer debate — analysts, reviewers, then aggregator.*

```text
Layer 1: [Analyst 1: Qwen3-Max] ──────► Layer 2: [Reviewer 1: Qwen3-Max] ─────────┐
         [Analyst 2: DeepSeek-V3.2] ──►          [Reviewer 2: DeepSeek-V3.2] ─────┼─► Layer 3: [Aggregator: Qwen3-Max] ──► [Best solution]
         [Analyst 3: Kimi-K2-Thinking] ►         [Reviewer 3: Kimi-K2-Thinking] ──┘
```

```python
async def run_multi_layer_moa() -> None:
    """
    Multi-layer MoA example: a 3-layer architecture to distill a course marketing plan
    Layer 1: 3 different models as proposers generate plans in parallel
    Layer 2: 3 different models optimize and improve the first layer's aggregated output
    Layer 3: the final aggregator synthesizes all information and outputs the best plan
    """
    # Generic aggregation prompt
    aggregate_prompt = (
        "Your task is to synthesize multiple LLMs' answers to the same question. "
        "Please critically evaluate these answers, identify their merits and shortcomings, "
        "then fuse this information to generate a high-quality, accurate, comprehensive final answer."
    )

    # Layer 1: initial proposer layer (3 different models)
    layer1_proposers = [
        create_agent(
            name="Proposer-L1-1",
            sys_prompt="You are a professional course analyst. Please distill the core selling points and promotional copy for the given course.",
            model_name="qwen3-max",
            multi_agent=True
        ),
        create_agent(
            name="Proposer-L1-2",
            sys_prompt="You are a professional course analyst. Please distill the core selling points and promotional copy for the given course.",
            model_name="deepseek-v3.2-exp",
            multi_agent=True
        ),
        create_agent(
            name="Proposer-L1-3",
            sys_prompt="You are a professional course analyst. Please distill the core selling points and promotional copy for the given course.",
            model_name="kimi-k2-thinking",
            multi_agent=True
        ),
    ]

    task = "This is a new 'AI LLM Applications for Web Developers' course. Please distill its core selling points and promotional copy."
    layer1_outputs = await fanout_pipeline(
        agents=layer1_proposers,
        msg=Msg("user", task, "user"),
        enable_gather=True,
    )

    # Layer 1 aggregator
    layer1_aggregator = create_agent(
        name="Aggregator-L1",
        sys_prompt=aggregate_prompt,
        model_name="qwen3-max",
        multi_agent=True,
    )
    layer1_merged = "\n\n".join([f"Model {i+1}:\n{m.content}" for i, m in enumerate(layer1_outputs)])
    layer1_result = await layer1_aggregator(Msg("user", layer1_merged, "user"))

    # Layer 2: second-round proposer layer (3 different models, optimizing based on the first layer's aggregated result)
    layer2_proposers = [
        create_agent(
            name="Proposer-L2-1",
            sys_prompt="You are a professional course analyst. Please examine the given marketing plan and propose improvement suggestions or an optimized version.",
            model_name="qwen3-max",
            multi_agent=True
        ),
        create_agent(
            name="Proposer-L2-2",
            sys_prompt="You are a professional course analyst. Please examine the given marketing plan and propose improvement suggestions or an optimized version.",
            model_name="deepseek-v3.2-exp",
            multi_agent=True
        ),
        create_agent(
            name="Proposer-L2-3",
            sys_prompt="You are a professional course analyst. Please examine the given marketing plan and propose improvement suggestions or an optimized version.",
            model_name="kimi-k2-thinking",
            multi_agent=True
        ),
    ]

    layer2_prompt = f"Below is the marketing plan generated by the first round of analysis:\n\n{layer1_result.content}\n\nPlease propose improvement suggestions or an optimized version on this basis."
    layer2_outputs = await fanout_pipeline(
        agents=layer2_proposers,
        msg=Msg("user", layer2_prompt, "user"),
        enable_gather=True,
    )

    # Layer 2: final aggregation layer
    final_aggregator = create_agent(
        name="Final-Aggregator",
        sys_prompt=aggregate_prompt,
        model_name="qwen3-max",
        multi_agent=True,
    )

    layer2_merged = "\n\n".join([f"Model {i+1}:\n{m.content}" for i, m in enumerate(layer2_outputs)])
    final_output = await final_aggregator(Msg("user", layer2_merged, "user"))

    print("Multi-layer MoA final output:")
    print(final_output.content)

await run_multi_layer_moa()
```

**When to use multi-layer MoA**:

*   **High-value tasks**: such as a company's annual strategy report, important product-launch copy, core course-system design, etc. — the success or failure of these tasks may directly affect business outcomes, making it worth investing more resources.
*   **Highly creative tasks**: such as brand-story creation, teaching-method innovation design, etc. — scenarios that need multiple rounds of idea collision to spark the best creativity.
*   **Low-fault-tolerance tasks**: such as legal documents, technical white papers, etc. — where any error can cause serious consequences, requiring multi-layer review to ensure accuracy.

**Cost trade-off**:

Multi-layer MoA's cost grows linearly with the number of layers. Take the 3-layer architecture above: each layer has 3 proposer models + 1 aggregator, meaning at least (3+1) + (3+1) = 8 model calls, more than double the single-layer 3+1=4. So you should only consider multi-layer MoA when the task's value clearly exceeds the cost.

You can balance cost and quality with the following strategies:
*   **Reduce the number of proposers**: use 3-4 different models in the first layer for diversity, and reduce to 2-3 models in later layers for refinement.
*   **Reduce the number of layers**: for most tasks, 2-layer MoA (proposer layer + aggregation layer) already brings a significant quality improvement; 3 or more layers are usually only worth using for extremely high-value tasks.
*   **Mixed model configuration**: mix models of different performance and cost among the proposers, while the aggregator uses the highest-quality model to ensure the quality of the final output.

> **Further reading: workflow cost optimization and resource management**
>
> You've realized that advanced patterns like Mixture-of-Agents (MoA) bring significant cost increases. This raises a key question you must face before putting any workflow into production: how do you manage resources and optimize cost? Fortunately, you can significantly reduce a workflow's running cost, without sacrificing too much quality, through a series of refined engineering strategies.
>
> *   **Differentiated model allocation**: different nodes in a workflow vary greatly in task complexity and importance. You can allocate lightweight, cheap models to simple tasks (such as intent recognition, format conversion), and reserve expensive advanced models only for the most critical core tasks (such as final decisions, copy generation). Research shows that with reasonable optimization strategies, depending on the specific implementation, enterprises can save 40-70% of token cost.
> *   **Systematic caching**: examine your workflow carefully and you'll find that many nodes' computations are repeatable. For example, retrieving the same company style guide, parsing review requests for the same course, etc. By adding a caching mechanism to these nodes, you can store intermediate results. When the same input is encountered next time, the system can directly return the cached result, completely bypassing the model call, thereby greatly reducing cost and latency.
> *   **Intelligent batching**: not all tasks need an immediate response. For non-real-time tasks such as course-quality report generation and user-feedback analysis, you can design the workflow to intelligently aggregate a batch of similar requests, then "batch-process" them with a single model call, rather than calling once per request. This finds a better balance between cost and response time.

#### 2.3.5 Pattern five: Human-in-the-Loop (HITL)

So far, all the workflows you've designed are fully automated. However, in the real world, handing all decision-making power entirely to AI carries risks, especially when dealing with ambiguous teaching concepts or high-value course content. The human-in-the-loop pattern no longer pursues full automation; instead, it **intentionally designs one or more "pause nodes" in the workflow, returning control to a human**, who makes decisions, approvals, or quality checks before handing the task back to the workflow to continue. This is a key pattern for building trustworthy, safe AI systems.

*Figure (translated): human-in-the-loop.*

```text
[Course content] -> [AI analyst: provides suggestions] -> [AI rewriter: executes modifications] -> {Human expert review}
       ^                                                                                               |
       └──────────────────────────── (when uncertain, send back) ◄──────────────────────────────────────┘
                                                                                                       │ (approved)
                                                                                                       v
                                                                                                [Final version]
```

```python
"""
Pattern five: Human-in-the-Loop (HITL) - Scenario: reviewing a course's difficult point (Human as a Tool)
The AI first gives a revision suggestion for a potential difficult point in the course; then a rewriting Agent equipped with a "consult a human" tool autonomously decides when to call the tool to ask the human, and finally completes the revision.
"""
import asyncio
import os
from agentscope.agent import ReActAgent, UserAgent
from agentscope.message import Msg, TextBlock
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.tool import Toolkit, ToolResponse
from chatbot.agent import create_agent, disable_console_output

# Wrap human intervention as a tool: ask_human_decision
async def ask_human_decision(question: str) -> ToolResponse:
    """Consult a human expert for a decision or opinion.

    Args:
        question (str): the specific question you want the human to confirm or supplement.
    """
    human_expert = UserAgent(name="Teaching Expert")
    reply = await human_expert(
        Msg(
            "assistant",
            question,
            "assistant",
        )
    )
    return ToolResponse(
        content=[
            TextBlock(type="text", text=reply.get_text_content()),
        ]
    )

async def run_hitl() -> None:
    # AI: give a revision suggestion
    suggester = create_agent(
        name="Difficult-Point Analyst",
        sys_prompt=(
            "You are a senior instructional designer. Please find one concept in the course that may be hardest for beginners to understand, "
            "and provide a more accessible explanation as a revision suggestion."
        ),
        model_name="qwen-plus",
        multi_agent=True,
    )
    disable_console_output([suggester])

    course_content = "In Python, a decorator is essentially a function that takes a function as an argument and returns a new function..."
    suggestion = await suggester(Msg("user", course_content, "user"))

    print("AI suggestion:\n")
    print(suggestion.content)

    # Give "human intervention" as a tool to the rewriting Agent, which autonomously decides whether to call it
    toolkit = Toolkit()
    toolkit.register_tool_function(ask_human_decision)

    rewriter = ReActAgent(
        name="Content Rewriter",
        sys_prompt=(
            "You are a course-content rewriter. Complete the final revision based on the provided AI suggestion.\n"
            "- If you're confident, complete the revision directly and give a confirmation message;\n"
            "- If there's uncertainty, ambiguity, or high risk, call the tool ask_human_decision to consult a human expert first, "
            "then complete the revision accordingly;\n"
            "- In the final result, briefly explain whether you consulted a human and why."
        ),
        model=DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.environ.get("DASHSCOPE_API_KEY", "your-api-key"),
            stream=False,
        ),
        formatter=DashScopeMultiAgentFormatter(),
        toolkit=toolkit,
    )
    disable_console_output([rewriter])

    # Provide both the course content and the AI suggestion to the rewriting Agent
    task = (
        "Below is a course excerpt and the AI's revision suggestion. Complete the final revision per the system prompt:\n\n"
        f"[Course content]\n{course_content}\n\n"
        f"[AI suggestion]\n{suggestion.get_text_content()}\n"
    )
    final_action = await rewriter(Msg("user", task, "user"))

    print("=" * 50)
    print("HITL final output:")
    print(final_action.content)
    print("=" * 50)

async def main() -> None:
    await run_hitl()

await main()
```

The advantages of a human-in-the-loop workflow are:

*   **Improved accuracy**: by introducing human common sense and domain knowledge to handle teaching ambiguities the AI struggles to judge (such as whether a metaphor is apt), ensuring the correctness of the final content.
*   **Enhanced safety**: for high-risk operations such as directly publishing a course or modifying a core code base, human final approval is the last line of defense against AI misoperations causing serious consequences.
*   **Building trust**: involving the course designer in the AI's review and revision process gives them a stronger sense of control over and trust in the system's behavior.

Common application scenarios include:

*   **Handling ambiguous requirements**: when requirements are unclear (e.g. "make the course more interesting"), the AI provides multiple instructional-design options and the human chooses.
*   **High-value operation approval**: before executing any operation involving course-content publishing, deleting old versions, etc., the course owner must approve.
*   **Key output quality review**: after "Mixture-of-Agents" generates an important course-outline draft, the final step of the workflow should be to send it to the instructional director for final review, rather than putting it directly into development.

Introducing a human **significantly reduces the workflow's degree of automation and execution speed**. So it's not suitable for fully-automated scenarios pursuing high throughput and millisecond-level response. HITL nodes need to be designed carefully, intervening only at absolutely necessary points and avoiding excessive manual intervention that slows down the whole process.

> **Further reading: production-grade frameworks**
>
> You don't need to implement these complex patterns from scratch. The industry already has mature frameworks to help you build and manage Agent workflows, with built-in exception-handling and state-management tools.
> *   **Code frameworks**: libraries like **AgentScope** and **LangGraph** let you flexibly define nodes and edges in Python code to build arbitrarily complex graph-structured workflows, offering the highest degree of customization.
> *   **Visual orchestration platforms**: low-code/no-code platforms like **Alibaba Cloud Model Studio** and **Dify** let you build workflows by dragging components and connecting lines, like drawing a flowchart. This greatly lowers the development barrier and suits rapid prototyping and scenarios with relatively fixed business processes.

#### 2.3.6 Choosing the right pattern
You've now learned five workflow patterns with different capabilities. A natural question is: when facing a specific business problem, how should I choose, or even combine, these patterns?

Remember one core principle: **there is no "best" pattern, only the "most suitable" one**. Your choice should be determined by the intrinsic properties of the task, such as its complexity, the dependencies between subtasks, the requirements for cost and efficiency, and the tolerance for result quality and risk.

### 2.4 Summary

Let's recap what you learned in this section:

*   **The limitation of a single Agent**: facing a complex task with multiple steps, a single Agent struggles to maintain a stable execution plan and easily fails due to "attention diffusion" or "error accumulation."
*   **The core idea of workflows**: borrowing the "divide and conquer" concept, break a complex task into multiple independent, manageable nodes and define the execution relationships between them, thereby ensuring process reliability.
*   **The five core orchestration patterns**: you learned the five patterns — pipeline, branching, parallel execution, mixture-of-agents, and human-in-the-loop — used respectively for fixed processes, choose-one-of-many decisions, parallel efficiency, pursuing quality, and introducing manual review.
## 3 From Fixed Process to Autonomous Planning

### 3.1 The limitation of fixed workflows

In the previous chapter, you learned how to build fixed workflows for repetitive work. Suppose you developed a "course preliminary research" bot for the company, with a fixed process: when it receives a research request, it analyzes the user persona, competitor courses, and industry needs in parallel.

Now a course designer sends the bot an instruction: "Please help me complete the preliminary research for a new Python intro course."

The bot faithfully launches the workflow you preset:
1.  **Industry-needs analysis** subtask: calls the tool, success.
2.  **User-persona definition** subtask: calls the tool, success.
3.  **Competitor-course analysis** subtask: calls the `analyze_competitor_course` tool, but receives an error: "**Error: because the competitor site's layout was updated, the course outline can't be parsed.**"

At this point, your bot can't continue. Because the process it was designed with has no step to handle the unexpected situation "the competitor-analysis tool failed."

*Figure (translated): without exception handling, the workflow gets stuck.*

```text
                              ┌─► [Industry needs: success] ──────────────┐
[Python course research] ───►{Parallel execution}├─► [User profile: success] ────────────────┼─► [Summary results]
                              └─► [Competitive analysis: website redesign cannot be parsed] ──┘
                                                              |
                                                              v
                                                  [Process interrupted: stuck]
```

### 3.2 The naive solution: add a new branch

You'll think, just add an exception-handling branch to the workflow. You can add a branch to the original fixed process: if `analyze_competitor_course` fails, execute a new step, such as reminding the course designer to handle it manually.

*Figure (translated): exception handling via human intervention.*

```text
                              ┌─► [Industry needs: success] ──────────────────────────┐
[Python course research] ───►{Parallel execution}├─► [User profile: success] ────────────────────────────┼─► [Summary of results] ──► [Process completed]
                              └─► [Competitive analysis: website redesign cannot be parsed] ─► [Human intervention] ──┘
```

This "patching" solution seems effective, but what if next time the industry-needs-analysis API fails due to temporary maintenance? Do you add another branch? What if, when defining the user persona, the required data-source format changes? Add yet another branch?

You'll find you can never anticipate all possible accidents. Trying to preset a handling process for every exception makes your workflow incredibly complex and bloated, hard to maintain. More importantly, once a new problem you didn't anticipate arises, the whole system still "gets stuck."

The root cause is that this Agent is just a faithful executor of a process, not a problem solver. It doesn't "understand" that the user's ultimate goal is to "complete the course preliminary research"; it only knows to strictly follow the flowchart you drew, step by step. When one path is blocked, it doesn't know how, like a human, to proactively find another path to achieve the ultimate goal.

> **Further reading: Goal vs. Task**
>
> Understanding the difference between "goal" and "task" is key to understanding an Agent's autonomous-planning ability.
>
> *   **Goal**: the final state the user wants to achieve. It's high-level and sometimes even vague. For example: "help me complete the research for the Python intro course."
> *   **Task**: the specific, well-defined action that needs to be executed to achieve the goal. For example: "call the `analyze_competitor_course` tool with the argument {url: 'some-site.com'}."
>
> An Agent with only a fixed workflow handles "tasks." When a task fails, it's powerless. A smarter Agent should be able to focus on the user's "goal." When a specific task fails, it should realize this is just one path to the goal being blocked, then proactively plan new tasks to keep approaching the goal.

### 3.3 Teaching the Agent to plan tasks autonomously

This process inspires us: can we also grant the Agent this "planning" power, letting it autonomously design and adjust its own workflow when facing unknown challenges?

This is exactly the industry's core theory for solving this kind of problem: **Planning**.

After introducing planning ability, the Agent's working mode fundamentally changes. The developer's role shifts from "process designer" to "goal setter" and "capability (tool) provider," while the Agent is upgraded from "task executor" to "**solution planner**."

Its workflow becomes:
1.  **Receive the goal**: the Agent receives a high-level user goal (e.g. "complete the preliminary research for the Python course").
2.  **Dynamic planning**: the Agent's "brain" (the LLM) first thinks, decomposes the goal, and dynamically generates an **action Plan** containing multiple steps.
3.  **Execute the plan**: an execution program receives this plan, then calls tools in order to complete each step, just like executing an ordinary workflow.

*Figure (translated): plan-and-execute.*

```text
[User goal: research Python course] -> [Agent: planning] -> [Dynamically generated plan] -> [Executor]
                                                                                              |
      ┌───────────────────────────────────────────────────────────────────────────────────────┤
      v                                                                                       v
[Tool 1: industry needs]   [Tool 2: user profile]   [Tool 3: competitive analysis] ...   ──► [Completed]
```

In this new mode, the "plan" itself becomes data that can be generated and executed. The LLM is no longer a fixed link in the process, but the **creator** of the process.

To help you more intuitively understand the Agent's autonomous-planning ability, we provide a complete example based on the AgentScope framework. This example simulates the scenario at the start of the article: when the competitor-analysis tool fails, how the Agent autonomously plans and finds a solution.

```python
"""AgentScope - Agent autonomous planning and execution example (simplified)"""
import asyncio
import os
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.message import Msg, TextBlock
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit, ToolResponse
from agentscope.plan import PlanNotebook

# Simulated business tools
async def analyze_competitor_course(url: str) -> ToolResponse:
    """Analyze the outline of a competitor's course page"""
    # Simulate a parse failure due to the site being redesigned
    return ToolResponse(content=[
        TextBlock(type="text", text=f"\u274c Error: because the {url} site's layout was updated, the course outline can't be parsed.")
    ])

async def search_industry_demand(topic: str) -> ToolResponse:
    """Query the industry's skill demand"""
    return ToolResponse(content=[
        TextBlock(type="text", text=f"\u2705 Report: the industry-demand analysis for \u201c{topic}\u201d is complete.")
    ])

async def google_search(query: str) -> ToolResponse:
    """Google web search"""
    if "syllabus" in query:
        return ToolResponse(content=[
            TextBlock(type="text", text="Search result: found the syllabus PDF of the 'Python intro course' at a.com/syllabus.pdf")
        ])
    return ToolResponse(content=[TextBlock(type="text", text="No relevant information found")])

async def extract_text_from_pdf(url: str) -> ToolResponse:
    """Extract text from a PDF link"""
    return ToolResponse(content=[
        TextBlock(type="text", text=f"\u2705 Extracted the outline text from {url}: 1. Variables and data types... 2. ...")
    ])

# Hook function used to monitor plan changes
plan_snapshots = []

def capture_plan_snapshot(notebook, plan):
    """Capture a plan snapshot"""
    if plan:
        plan_snapshots.append({
            "name": plan.name,
            "description": plan.description,
            "state": plan.state,
            "subtasks": [
                {
                    "name": st.name,
                    "state": st.state,
                    "outcome": st.outcome
                }
                for st in plan.subtasks
            ]
        })

async def main():

    print("=" * 60)
    print("\U0001f916 Agent autonomous-planning demo")
    print("=" * 60)

    # Create a PlanNotebook and register the hook
    plan_notebook = PlanNotebook()
    plan_notebook.register_plan_change_hook("capture", capture_plan_snapshot)

    # Create the toolkit
    toolkit = Toolkit()
    toolkit.register_tool_function(analyze_competitor_course)
    toolkit.register_tool_function(search_industry_demand)
    toolkit.register_tool_function(google_search)
    toolkit.register_tool_function(extract_text_from_pdf)

    # Create the Agent
    agent = ReActAgent(
        name="CourseResearcherAgent",
        sys_prompt=(
            "You are a course-research assistant. When facing a complex task:\n"
            "1. Use create_plan to create a plan\n"
            "2. Execute step by step, using finish_subtask to mark completion\n"
            "3. Adapt flexibly when you hit a problem, e.g. use google_search to find an alternative\n"
            "4. When done, use finish_plan to end"
        ),
        model=DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        plan_notebook=plan_notebook,
    )

    # User request
    print("\n\U0001f4ac User: Please help me complete the preliminary research for a new Python intro course.\n")
    print("-" * 60)

    await agent(Msg("user", "Please help me complete the preliminary research for a new Python intro course; the competitor is the course on some-site.com.", "user"))

    # Show the result (get the last complete plan from the snapshots)
    print("\n" + "=" * 60)
    print("\U0001f4ca Execution result")
    print("=" * 60)

    if plan_snapshots:
        final_plan = plan_snapshots[-1]
        finished = sum(1 for st in final_plan["subtasks"] if st["state"] == "finished")

        print(f"\n\u2705 Plan: {final_plan['name']}")
        print(f"\U0001f4ca Progress: {finished}/{len(final_plan['subtasks'])}")
        print(f"\U0001f3af State: {final_plan['state']}\n")

        print("Subtask details:")
        for i, subtask in enumerate(final_plan["subtasks"], 1):
            icon = "\u2705" if subtask["state"] == "finished" else "\u23f3"
            print(f"  {icon} {i}. {subtask['name']}")

await main()
```

Through this example, you can see:
1. **Autonomously creating a plan**: the Agent uses the `create_plan` tool to automatically plan the research task.
2. **Flexible execution**: when the competitor-analysis tool fails, the Agent automatically adjusts its strategy and switches to `google_search`.
3. **Progress tracking**: uses `finish_subtask` to mark completed tasks.
4. **A complete closed loop**: the whole process from plan creation to task completion.

This is exactly the core capability that PlanNotebook brings to the Agent: elevating it from a "process executor" to a "problem solver."

> **Further reading: production-grade frameworks**
>
> Open-source frameworks like AgentScope and LangChain both provide mechanisms to implement this "plan-execute" loop. They let you define a set of tools, then have the LLM act as a Planner to decide which tool to call at each step, using the tool's returned result as input for subsequent thinking, thereby achieving complex task decomposition and execution. On Alibaba Cloud's Machine Learning Platform PAI, you can conveniently deploy and manage the LLM services these frameworks need, providing a powerful "brain" for the Agent.

### 3.4 Executing the plan the Agent generates

So, how do you have the LLM generate a "plan" a machine can understand and execute?

The simplest way is to have it generate a natural-language list of steps. But then the downstream execution program can hardly parse it precisely. As you learned earlier when having the Agent call tools, you can use structured **JSON format** to output the tool-call arguments. Here, you can also treat the "execution plan" as calling tools. Each step is a clearly-defined object containing the tool name to call and the corresponding arguments.

```json
{
  "plan": [
    {
      "step": 1,
      "thought": "I first need to analyze the industry demand, which is key to course positioning.",
      "tool_name": "search_industry_demand",
      "tool_params": {"topic": "Python basics"}
    },
    {
      "step": 2,
      "thought": "Next, I'll try to analyze the competitor course's outline.",
      "tool_name": "analyze_competitor_course",
      "tool_params": {"url": "some-site.com/python-course"}
    }
  ]
}
```

This is an effective method, but its expressiveness is limited. If the plan needs to include conditional logic like "if competitor analysis fails, switch to Google search," a simple JSON list can't handle it.

To express more complex logic, you can have the LLM **directly generate code (Code as Action)** to express its plan, then execute the code by calling the "code interpreter" tool.

```plaintext
# Plan generated by LLM
def execute_research_plan():
    # Step 1: Analyze industry demand
    demand_result = search_industry_demand(topic="Python basics")
    print(demand_result)

    # Step 2: Analyze competitor course
    competitor_result = analyze_competitor_course(url="some-site.com/python-course")

    # Step 3: Handle analysis failure
    if not competitor_result.success and "can't be parsed" in competitor_result.message:
        print("The competitor-analysis tool failed; looking for an alternative...")
        search_results = google_search(query="some-site.com python course syllabus")
        # Assume search_results gives a PDF link
        pdf_url = extract_pdf_link(search_results)
        if pdf_url:
            syllabus_text = extract_text_from_pdf(url=pdf_url)
            print(syllabus_text)
    else:
        print(competitor_result)

execute_research_plan()
```

By generating code, the LLM can leverage a programming language's rich built-in capabilities (such as variables, conditionals, loops) and powerful third-party libraries (such as Pandas) to formulate and execute extremely complex plans. This lets the Agent handle not only simple linear processes but also complex scenarios involving logical judgment and data processing.

### 3.5 Advanced: Let the Agent create new tools

You've mastered the powerful method of having the LLM formulate plans by generating code. This grants the Agent the ability to use complex logic like variables, conditionals, and loops.

But there's still a potential bottleneck: the Agent is still limited to the **tool set** you provided in advance. If, while executing a plan, it finds it needs a new tool you didn't provide — say, a function to count the frequency of different tech keywords on job sites — what should it do?

The most direct approach is to have the Agent stop and ask you (the developer) to write this new tool for it. But that interrupts the task's autonomous flow. Let's think one step further: since the Agent can already generate code for **planning**, can it also generate code for **creating new capabilities**?

This leads to a more advanced planning capability: **Dynamic Tool Creation**.

To achieve this, besides providing concrete business tools (such as `analyze_competitor_course`), you also provide the Agent with a core "meta-tool": a **Code Interpreter**.

When the Agent recognizes that existing tools can't meet the need, its plan includes a series of special steps:
1.  **Decision**: the LLM analyzes the task and identifies that it needs a new tool that doesn't currently exist.
2.  **Generate code**: in its plan, it writes a piece of code to define, test, and encapsulate a new tool function.
3.  **Call the new tool**: after the new tool is successfully created in the code-execution environment, the Agent can directly call it in subsequent plan steps, as if the tool had existed from the start.
4.  **Extend the tool library**: this newly-generated tool can be added to the temporary tool library for this task, for reuse in subsequent steps.

*Figure (translated): autonomous tool creation.*

```text
[Receive task] -> [Agent analyzes requirements] -> {Are existing tools sufficient?}
                                                    | (yes)                       | (no)
                                                    v                             v
                                    [Use existing tools: complete task]   [Create new tool: identify gaps -> generate code]
                                                    |                             |
                                                    └──────────► [Execute: register -> invoke tool]
                                                                      |
                                                                      v
                                                 [Task completed; tool library expanded (reusable)]
```

Below is a simple example built with AgentScope. During planning, the Agent can, based on the existing `add` tool, autonomously create and register a `factorial` tool and call it in subsequent tasks.

```python
"""AgentScope Agent autonomously creating tools - streamlined version"""
import asyncio
import os
import sys
from io import StringIO

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg, TextBlock
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit, ToolResponse

# Global toolkit
toolkit = None

async def code_exec(code: str) -> ToolResponse:
    """Code interpreter - used to create and register new tools"""
    global toolkit

    namespace = {
        'ToolResponse': ToolResponse,
        'TextBlock': TextBlock,
        'asyncio': asyncio,
        'agent_toolkit': toolkit,
        'math': __import__('math'),
    }

    stdout, sys.stdout = sys.stdout, StringIO()

    try:
        exec(code, namespace)
        output = sys.stdout.getvalue()
        sys.stdout = stdout
        return ToolResponse(content=[TextBlock(
            type="text",
            text=output or "\u2705 Executed successfully"
        )])
    except Exception as e:
        sys.stdout = stdout
        return ToolResponse(content=[TextBlock(
            type="text",
            text=f"\u274c Error: {e}"
        )])

async def add(a: float, b: float) -> ToolResponse:
    """Addition tool"""
    return ToolResponse(content=[TextBlock(
        type="text",
        text=f"{a} + {b} = {a + b}"
    )])

async def main():
    if "DASHSCOPE_API_KEY" not in os.environ:
        print("\u274c Please set DASHSCOPE_API_KEY")
        return

    global toolkit
    toolkit = Toolkit()
    toolkit.register_tool_function(add)
    toolkit.register_tool_function(code_exec)

    agent = ReActAgent(
        name="ToolMaker",
        sys_prompt=(
            "You can create new tools via code_exec.\n"
            "Template:\n"
            "async def tool_name(param: type) -> ToolResponse:\n"
            "    # description\n"
            "    result = ...\n"
            "    return ToolResponse(content=[TextBlock(type='text', text=f'{result}')])\n"
            "agent_toolkit.register_tool_function(tool_name)\n"
            "print('\u2705 registered tool_name')"
        ),
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
    )

    print("=" * 60)
    print("\U0001f680 Agent autonomous tool-creation demo")
    print("=" * 60)

    # Use an existing tool
    print("\n\u25b6\ufe0f Scenario 1: use an existing tool")
    await agent(Msg("user", "Compute 30 + 45", "user"))

    # Create a new tool
    print("\n\u25b6\ufe0f Scenario 2: create a factorial tool")
    await agent(Msg("user", "Create a factorial tool to compute factorials", "user"))

    # Use the new tool
    print("\n\u25b6\ufe0f Scenario 3: use the new tool")
    await agent(Msg("user", "Use factorial to compute the factorial of 5", "user"))

    # Show the toolkit
    print("\n\U0001f4e6 Final toolkit:")
    for i, s in enumerate(toolkit.get_json_schemas(), 1):
        print(f"{i}. {s['function']['name']}")

if __name__ == "__main__":
    await main()
```

By providing a code interpreter, you elevate the Agent from a mere tool **user** to a tool **creator**. Its capability boundary is no longer bound by the tool set you predefined, giving it true creativity and adaptability in problem-solving.

### 3.6 When to choose autonomous planning?

You've now learned the two modes "fixed workflow" and "autonomous planning." You might ask: should I use the smarter autonomous planning in all scenarios and abandon fixed workflows entirely?

That's the wrong way to think. A more autonomous mode isn't a silver bullet, and a less autonomous mode also has broad application scenarios. In production practice, a very effective best practice is to adopt an **"explore-then-solidify" hybrid mode**.

This mode divides task handling into two phases:

1.  **Exploration phase**: for newly-appearing tasks with unclear processes (e.g. you need to research a brand-new niche tech field you've never touched), you can't predefine a perfect process. Here you should dispatch the autonomous-planning Agent. Its task is to explore different paths to solve the problem, calling the tools it deems appropriate — even if it makes mistakes or hits dead ends along the way, the ultimate goal is to find a solution that reliably solves the problem.

2.  **Solidification phase**: after the autonomous-planning Agent has explored many times and verified and summarized a stable, efficient solution path (e.g. it finds that "first use tool A to crawl information from a specific site, then use tool B for data cleaning, and finally use tool C to generate a summary report" has the highest success rate), you can **abstract and solidify** this verified path, encapsulating it into a reliable "fixed workflow" for subsequent large-scale, repetitive production calls.

This way, you build a continuously-optimizing positive loop.

> **Preview**: in Chapter 7 "Agent Skills," you'll experience the capability boundary of an autonomous Agent firsthand through a real course-review task, and learn how to encapsulate expert knowledge as a Skill to break through these limits.

### 3.7 Case study: letting the Agent operate web pages

To help you more concretely understand how this "perceive-plan-act" loop applies in real products, let's look at a case of a highly-autonomous web-operation Agent, such as the open-source project Browser Use.

Traditional web automation (RPA) tools require writing fixed operation scripts for each website and each task. Once the website interface changes slightly, the script fails, with extremely high maintenance cost.

An Agent with planning ability can fundamentally solve this problem. It doesn't rely on fixed scripts; instead, like a human, it **understands** the user's goal, **perceives** the current web-page state, and dynamically **plans** the next action.

**Execution-flow breakdown:**
When the user gives the instruction "Search Amazon for books about AI":
1.  **Understanding and initial planning**: the LLM decomposes the vague goal into a series of high-level steps: "1. Open the Amazon website; 2. Find the search box; 3. Enter 'AI books'; 4. Click search; 5. Analyze the results."
2.  **Action and perception**: the Agent executes the first step (open the website). Then it "perceives" the new page — not just reading the HTML code, but possibly also analyzing the visual layout of the screenshot to understand what elements are on the page.
3.  **Decision and re-planning**: based on the perceived information, it decides the next action: find the input area that most looks like a "search box." If there are multiple input boxes on the page, it reasons and judges based on position, labels, and other information.
4.  **Loop execution**: it continues this "perceive-plan-act" loop until all steps are complete, and returns the list of books it found.
5.  **Exception handling**: if it encounters something unexpected at any step, such as a CAPTCHA popping up after clicking search, it doesn't get stuck. It perceives this new situation and inserts "handle the CAPTCHA" as a new obstacle into the current plan, trying to solve it or asking the user for help.

*Figure (translated): a planning agent driving a browser.*

```text
[Goal: search AI books on Amazon] -> [LLM initial planning] -> [Generate action: open amazon.com] -> [Browser executes operation]
                                                                                                            |
                                                                                                            v
                                                                                                [Perceive page state (HTML + screenshot)]
                                                                                                            |
                                                                                                            v
                                                                                       {LLM decision: analyze page, plan next step}
                                                                                       | (task completed)          | (unexpected issue)
                                                                                       v                           v
                                                                            [Output result: book list]     [Re-plan] ──► (back to generating actions)
```

This case fully demonstrates the core advantage of a planning-type Agent: it's no longer a script executor, but achieves truly **adaptive** operation of dynamic, unknown web environments through a continuous "perceive-plan-act" loop.

### 3.8 Summary
Let's recap what you learned in this section:

*   **The limitation of fixed workflows**: when facing unexpected obstacles like "tool failure," a preset fixed process "gets stuck," because it lacks adaptability. Simply adding a branch for every accident makes the process complex and hard to maintain.

*   **"Planning" is the core solution**: mimicking how humans solve problems, we upgrade the Agent from "task executor" to "solution planner." It no longer passively executes fixed steps, but autonomously and dynamically generates and adjusts action plans around the user's ultimate "goal."

*   **Turning plans into action**: you can guide the LLM to generate a structured plan (such as JSON or code) for a machine to execute precisely. A more advanced approach is to provide the Agent with a code interpreter, so it can dynamically create and use new tools during planning, breaking through the limits of preset capabilities.

*   **Trade-off between stability and flexibility**: "autonomous planning" suits innovative tasks that explore the unknown and have variable processes, while "fixed workflows" guarantee the stability and efficiency of core business. In production, you need to combine strategies like human-in-the-loop and explore-then-solidify, and make a wise choice between these two modes based on your specific business needs.

## 🔥 Quiz

### 🔍 Single choice 3.2.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>You developed a "course preliminary research" Agent that uses a fixed workflow to call three tools in parallel: industry analysis, user persona, and competitor analysis. After launch, the competitor site was redesigned, causing the crawler tool to fail frequently and the whole process to get stuck. How should you improve it?❓</b>

- A. Add a retry mechanism to the competitor-analysis tool; on failure, automatically retry three times then error out and exit
- B. Preset branch handling logic and fallback plans for every tool-failure scenario in the workflow
- C. Change the fixed workflow to the Plan & Execute mode, letting the Agent autonomously plan around the goal and dynamically handle exceptions
- D. Switch to a more stable competitor-data API provider to eliminate the possibility of tool failure at the data-source level

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: C**
📝 **Explanation**:
A only delays the failure; after the site redesign, retrying won't succeed either. B is directionally right but weak in means — presetting a branch for every exception makes workflow complexity explode, and you can't enumerate all accidents. D is idealized; in reality you can't guarantee any external service is always available. C is correct: the Plan & Execute mode turns the Agent from an "executor" into a "planner," so when a tool fails it can autonomously adjust the plan (e.g. switch to another information source or skip that step), gaining adaptability at the architectural level.
</div>
</details>

## ✉️ Feedback
You're welcome to participate in the [Alibaba Cloud LLM ACP course survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie) to share your learning experience and course feedback.
Your criticism and encouragement are our motivation to keep improving!
