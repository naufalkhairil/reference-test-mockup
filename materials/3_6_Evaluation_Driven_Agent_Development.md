# 3.6 Evaluation-Driven Agent Development

## 🚄 Preface

Earlier you learned to evaluate the answer quality of RAG, but when an Agent goes wrong, the problem often isn't in the final answer — it took the wrong tool path, overran its token budget, or a middle step had a bad format that broke everything downstream. Looking at the result alone won't reveal these. In this lesson, we extend the evaluation-driven methodology from RAG to Agents, establishing a complete evaluation system that covers both process and result.

## 🍁 Course Objectives

**You will learn:**
- Understand why Agent evaluation can't just look at "whether the final answer is correct" — the process matters equally
- End-to-end evaluation: the Task + Metric framework
- White-box evaluation: inspecting the tool-call sequence
- The evaluate-diagnose-optimize closed loop

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

## 1 Why "Feels About Right" Isn't Reliable
You've just deployed the first version of your "course-writing Agent." Testing locally with a few examples, it seemed to perform "pretty well." But after launch, user feedback was disappointing. Some complained the explanations of technical concepts were inaccurate, some felt the response text was too verbose, and others hit format errors that made the code examples fail to run.

You immediately try to fix it — say, adjusting the prompt so the Agent's explanations are "a bit more accurate." After the change, you again input the topic "introduce Python for loops," quickly skim the generated content, and feel "this time it's pretty good, the language flows nicely." But when you deploy it live, new problems appear. You're stuck in a dilemma: where exactly is the problem? Did the change just now optimize or damage overall performance?

> For example, you find the Agent's example for explaining "overfitting" in machine learning is too academic and not accessible enough. So you give the Agent an instruction:
>
> `...when explaining complex concepts, please use everyday-life analogies...`
>
> After running it, it indeed uses "memorizing answers for an exam rather than truly understanding the knowledge" to describe overfitting — a good effect. But you soon find that when generating the "Pandas data filtering" course, it also awkwardly adds an inappropriate analogy, which instead makes a simple operation complex and hard to understand.

## 2 What Can't Be Measured Can't Be Improved

The fundamental problem you're facing is the lack of an objective, quantifiable yardstick. The most direct idea is exactly what you're doing now: manually testing a few cases and judging by subjective feeling. But this "feels good" approach soon exposes its inherent flaws:

*   **Hard to quantify**: "feels better" can't be the basis for an engineering decision. You can't know whether this improvement is 10% or 20% better than the last.
*   **Lacks a standard**: today you think "the example is too complex," and tomorrow in a different mood you might think "the content has depth." Different testers and different points in time can shift the evaluation standard.
*   **Can't reproduce**: you can't systematically regression-test to ensure a new change hasn't broken the original good behavior. After you fix the "inappropriate analogy" problem, you can't guarantee a previous strength of "clear explanation" wasn't accidentally damaged.

Why does this happen? It comes down to how the Agent works. The LLM's generation process is probabilistic, and it itself lacks a "self-check" mechanism. A small tweak to your prompt may trigger an unpredictable "butterfly effect" in a complex system.

Since debugging by feel doesn't work, you'll naturally think of another approach: establish a systematic evaluation framework and drive development with data rather than feeling. It's like preparing for an exam — you can't rely only on "feeling like you've learned it"; you need to take mock exams to objectively check how well you've grasped the material.

This is **Evaluation-Driven Development**. It elevates evaluation from the tail end of the development process to the core position that decides direction.

This idea is based on three interlocking principles:

*   Evaluation — that is, your taste for "good vs. bad" — determines the ceiling of the product's capability.
*   Only what can be measured can be effectively improved.
*   The faster and more accurate the measurement feedback, the higher the efficiency and effect of improvement.

## 3 Two Evaluation Methods: From Macro to Micro

To build an effective evaluation system, you need to examine your Agent from two dimensions: **End-to-End Evaluation** and **White-box Evaluation**.

### 3.1 Evaluation method one: end-to-end evaluation

End-to-end evaluation focuses on the system's final output. It answers the most important question: "Is the course this Agent generates actually useful to the user?"

#### 3.1.1 Establishing evaluation standards iteratively

For a complex Agent system, you can't preset all the perfect evaluation metrics before the project starts. The right approach is to embrace iteration — evaluation is important, but starting quickly is even more important:

1.  **Build quickly**: first build a minimum viable version (MVP).
2.  **Observe problems**: run it in real scenarios and observe where it makes mistakes.
3.  **Summarize the key points**: from these errors, distill the key points that most need prioritized evaluation at the current stage, and turn them into evaluation metrics.

> For example, in the first version of content your course-writing Agent generates, you find the code examples often lack necessary `import` statements, so they can't run directly. This is an obvious, high-priority error. So you establish the first evaluation metric: "**code runnability**" — all code blocks must be self-contained and syntactically correct. Then you find that to make the language more vivid, the Agent overuses analogies, instead blurring the core concepts. So you add a second evaluation metric: "**explanation clarity**," explicitly requiring the avoidance of inappropriate analogies.

This loop repeats continuously, and your evaluation system becomes more complete and precise as the Agent evolves. The figure below shows this complete closed-loop process:

*Figure (translated): the evaluation-driven closed loop.*

```text
[MVP] -> [Real execution] -> [Observe errors] -> [Extract metrics]
                                                     │
                                ┌────────────────────┴────────────────────┐
                                v                                         v
               [Objective metrics: executability /        [Subjective metrics: accuracy /
                format / character count]                   teaching quality / style]
                                │                                         │
                                v                                         v
                           [LLM evaluation]                       [Human evaluation]
                                └────────────────────┬────────────────────┘
                                                     v
                                             [Aggregate score] -> [Improve agent] ──► (back to MVP)
```

As shown, starting from the MVP, through real runs, observing errors, and distilling metrics, then combining the two kinds of evaluation methods (objective and subjective), you finally form continuous improvement of the Agent. Next, we dive into how to design these two kinds of metrics.

#### 3.1.2 Designing evaluation metrics: objective and subjective

A comprehensive evaluation system needs to include both objective and subjective metrics.

| Type | Description | "Course-writing Agent" case |
| :--- | :--- | :--- |
| **Objective metrics** | Can be judged directly by code rules, with a deterministic result. | • **Code executability**: can the generated code snippet run successfully in the Python interpreter?<br>• **Format check**: does it include all required sections such as "pain-point case," "solution," "summary"?<br>• **Word-count limit**: is each section's length between 300-500 characters? |
| **Subjective metrics** | Involve semantics, logic, and quality, usually requiring stronger intelligence to judge. | • **Content accuracy**: are there factual errors in the explanation of technical concepts?<br>• **Teaching effectiveness**: can the introduced case spark learning interest? Is the explanation progressive from easy to hard?<br>• **Language style**: does it conform to the "rigorous, precise, calm" course setting? |

But the core question here is: who defines these metrics? Especially the subjective metrics, like "teaching effectiveness" and "language style" — what exactly do they mean?

**The key is that the evaluation metrics must be led by the most senior business experts on your team.** For your "course-writing Agent," these are the top instructional designers and senior lecturers. But there's a common pitfall to avoid here:

Many teams' approach is that technical staff first build the initial version of the Agent, and after finding the effect unsatisfactory, go to the business experts to "extract knowledge" — asking them "what do you think a good course looks like?" Then the technical team goes back and tries to translate these vague descriptions into evaluation rules. This mode is often inefficient, because:

*   **Experts lack motivation to participate**: they're positioned as "knowledge providers" rather than co-builders of the project. Not seeing a direct connection to their own business goals, their enthusiasm to participate is low.
*   **Knowledge-translation loss**: it's hard for technical staff to fully understand experts' tacit knowledge, and key elements are easily misinterpreted or omitted in translation.
*   **Long feedback cycle**: by the time the technical team implements it and comes back to validate, they've often taken a detour and need a lot of rework.

**The right approach is to make business experts the owners (designers) of the evaluation system from day one of the project, with the technical team playing the facilitator role. Specifically:**

1.  **Mobilize participation with business goals**: don't say "we need your help defining evaluation metrics," but rather "this Agent is to help us achieve [a specific business goal, such as 'shortening the course-production cycle from 2 weeks to 3 days while maintaining over 90% user satisfaction'], and as the gatekeeper of course quality, you need to define what the 'acceptable quality floor' is." When experts see this directly relates to the business outcomes they care about, their willingness to participate rises greatly.

2.  **Provide structured tools to lower the participation barrier**: the technical team's value is in providing scaffolding, not doing it for them. For example:
    *   **Evaluation-metric workshop**: organize experts in structured conversation, guiding with questions like "if you could only look at three metrics to judge whether a course is good or bad, which three would you pick?";
    *   **Scoring-rubric template**: provide a fill-in template of "1-5 points, what specific characteristics correspond to each score," letting experts fill it in rather than describe from scratch;
    *   **Case-annotation tool**: let experts annotate "what's good, what's bad" directly on real Agent outputs, then reverse-engineer the rules.
> For example, when an expert annotates a lesson plan as 'feels too bland,' the technical facilitator needs to probe: does 'bland' mean it lacks a pain-point case that resonates? This can distill the 'opening-case relevance' metric.
>
> When an expert says 'students won't understand,' keep digging: is the concept jumping too fast, e.g. jumping straight to 'lists' without explaining 'variables'? This can be turned into the 'theory-progression logic' metric.
>
> Through this kind of dialogue, you can encode the expert's 'taste' into evaluation items a machine can check.

3.  **Establish a continuous collaboration mechanism**: evaluation standards aren't a one-off document, but a living document that evolves with the Agent's capabilities and business needs. In a weekly review meeting, experts look at data, the technical team tunes the system, and both sides jointly decide the next optimization direction.

In this way, experts are no longer objects from whom "knowledge is extracted," but the true owners of the evaluation system. Their "teaching intuition" (i.e. "Tacit Knowledge"), with the aid of structured tools, gets systematically transformed into executable, iterable evaluation rules.

#### 3.1.3 Improving the stability of subjective evaluation

After defining the metrics, the next step is how to execute the evaluation. You have two choices: human evaluation and automated evaluation with an LLM (LLM-as-a-Judge).

*   **Human evaluation**: human experts score against the evaluation standard. This is the most reliable "gold standard," and especially early in the project it can calibrate your definition of "good" and "bad" for you. But its downside is high cost and slow speed, hard to do at large scale and high frequency.

*   **LLM automated evaluation**: train or guide another LLM to play the role of "evaluation expert," automatically scoring the "course-writing Agent's" output based on the metrics and scoring rules you define.

To make LLM evaluation more stable, you need to decompose a vague evaluation goal (like "good content quality") into a series of specific, checkable rules. Then have the LLM judge item by item, and finally aggregate into a score by rule.

> For example, evaluating the "content quality" of what the "course-writing Agent" generates can be decomposed into:
> 1.  **Pain-point introduction**: does it open with an everyday, concrete pain point? (Yes/No)
> 2.  **Theoretical elevation**: does it clearly point out the limitation of the initial solution and lead to the core theory? (Yes/No)
> 3.  **Code-example relevance**: is the provided code example closely related to the theory being explained, and simplified enough? (Yes/No)

**But you must be wary that LLM evaluation itself may be biased.**

> **Further reading: the LLM evaluator's "mindset"**
>
> Using an LLM as an evaluator is like hiring a learned but personally-biased expert. Its own training data determines its "taste."
> - **Style bias**: it may favor a certain code style (e.g. championing method chaining), thereby giving low scores to other equally-correct code of a different style.
> - **Length bias**: it may tend to consider longer, more detailed explanations as "more complete," thereby unfairly penalizing "concise but on-point" answers.
> - **"Yes-man" bias**: some models tend to give positive evaluations to avoid conflict, making it hard to discover real problems.
> - **Position bias**: some research shows that when handling a list or comparing multiple options, a model may tend to pick the option at the beginning or end. When designing the evaluation prompt, you can consider randomly shuffling the order of the content being evaluated to mitigate this bias.
>
> Therefore, the best practice is: **use human-expert evaluation early on to establish a high-quality "gold test set." Then use this test set to "calibrate" your LLM evaluator**, checking the consistency of its scoring with human experts. In subsequent development, periodically use manual spot-checks to ensure the automated evaluation system hasn't "drifted."

### 3.2 Evaluation method two: white-box evaluation

When your Agent's flow becomes complex, the drawbacks of end-to-end evaluation show. For example, your "course-writing Agent" may contain a "concept-explanation" component and a "code-generation" component. If the final course scores low, it's hard for you to judge whether the concept explanation was poor or the code example was terrible.

**White-box Evaluation** is designed to solve this problem. It advocates going deep into the system's internals and **designing a separate evaluation system for key components**.

The core advantages of white-box evaluation are:
*   **Clear signal**: provides an interference-free improvement signal, letting you focus on the real bottleneck.
*   **Fast iteration**: you only need to test a single component, without running the entire complex flow, greatly shortening the validation cycle.
*   **Precise optimization**: whether adjusting hyperparameters or swapping an external service, the effect can be precisely measured, making decisions evidence-based.

> This way, you can:
> - **Evaluate the "concept-explanation" component separately**: build a test set containing a series of technical terms (like "list comprehension," "decorator"), then only evaluate whether the text explanations this component generates are clear and accurate.
> - **Evaluate the "code-generation" component separately**: build a test set containing a series of task descriptions (like "generate a function to merge two dictionaries"), then only evaluate whether the generated code runs correctly and follows best practices.
>
> The advantage of this method is that it provides an interference-free improvement signal, letting you focus on the real bottleneck for fast, precise optimization.

In practice, you don't have to pursue a fully-automated, all-dimension-covering complex evaluation system from the start. For example, when handling code correctness, you can start with the simplest method: manually copy the code and run it a few times. Then gradually upgrade to writing a script that automatically executes the code and catches errors. Finally, you can build a complete evaluation pipeline with multiple metrics (style, efficiency, correctness). The final choice depends on your specific needs, budget, and acceptable error rate.

## 4 Evaluation Frameworks

You can build your own evaluation workflow that fits your business needs, based on code-written rules combined with an LLM. Of course, you can also use mature community evaluation frameworks to accelerate this. Besides AgentScope, RAGAS — the evaluation framework mentioned in the RAG-effectiveness-evaluation chapter — also provides end-to-end and component-level evaluation capabilities for Agents. In addition, you can choose DeepEval as an LLM evaluation framework.

### 4.1 Practice: AgentScope evaluation-framework demo

To run through an end-to-end example of "evaluation-driven development" with minimal code, you need to understand the following modules:

- **agentscope.evaluate**: `Task` (task definition), `MetricBase/MetricResult/MetricType` (custom metrics), `SolutionOutput` (a unified representation of the solution).
- **pydantic**: used to define models for structured output, improving evaluation stability (making the model output parsable numeric values).
- **agentscope.init (optional)**: used to enable Tracing, sending the run trajectory to Studio or an OTLP-compatible backend.

> Note: the teaching-oriented "minimal runnable" version doesn't depend on more complete evaluators like `GeneralEvaluator/RayEvaluator`; we directly compose a compact loop with `Task + Metric`. If you want to run large-scale benchmarks or distributed evaluation, just bring in the evaluator and storage modules.

The example below demonstrates "writing a lesson draft for a pandas data-analysis course" and gives the draft a programmable objective score. Key points:
- Structured output (`title/learning_objectives/code_example/quiz`) to improve evaluation stability.
- Fine-grained subjective scoring (LLM-as-Judge): score five dimensions on a 1-5 scale — language clarity/ambiguity, whether there are factual errors, consistency of expression, redundancy of expression (less redundancy = higher score), readability; use structured output for stable scoring.
Tracing (optional): set `AGENTSCOPE_STUDIO_URL` (to connect AgentScope Studio) or `OTEL_TRACING_URL` (to connect any OTLP-compatible backend) to automatically enable tracing; when unset, the example runs as usual.

*Figure (translated): example evaluation pipeline.*

```text
[Course benchmark: pandas task] -> [Generation agent] -> [Chapter draft: title / objectives / code / quiz]
                                                                 |
                                                                 v
                                                          [Review agent] -> [Five-dimensional scoring] -> [Results summary]
```

```python
# Educational course writing (pandas) end-to-end evaluation: two lesson drafts + five-dimension LLM scoring
import asyncio
import copy
import json
import os
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

import agentscope
from agentscope.message import Msg
from agentscope.agent import ReActAgent
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeChatFormatter
from agentscope.evaluate import (
    Task,
    MetricBase,
    MetricResult,
    MetricType,
    SolutionOutput,
)

assert os.getenv("DASHSCOPE_API_KEY"), "Please set DASHSCOPE_API_KEY in the environment first"

# (Optional) Enable tracing: prefer connecting to Studio; otherwise connect to any OTLP-compatible backend
studio_url = os.getenv("AGENTSCOPE_STUDIO_URL")
otel_url = os.getenv("OTEL_TRACING_URL")
if studio_url:
    agentscope.init(studio_url=studio_url)
elif otel_url:
    agentscope.init(tracing_url=otel_url)

# 1) Define a minimal benchmark (two lesson-writing tasks)
COURSE_BENCHMARK = [
    {
        "id": "pandas_intro",
        "prompt": (
            "Please write, in concise English, an intro lesson draft for pandas DataFrame. The output must include structured fields:\n"
            "- title: the course title;\n"
            "- learning_objectives (3-5 items, each no more than 25 words);\n"
            "- lesson_content: at least 180 words of lesson body, including an opening lead-in, core-concept explanation, step-by-step example walkthrough, and a class summary;\n"
            "- code_example: minimal runnable pandas code with comments (showing import pandas as pd and read_csv or DataFrame creation plus a head() usage example);\n"
            "- quiz: one single-choice question with options, at least 4 options, marking the correct answer.\n"
            "lesson_content should emphasize common beginner pitfalls and echo the code example."
        ),
        "tags": {"topic": "intro", "min_objectives": 3},
    },
    {
        "id": "pandas_groupby",
        "prompt": (
            "Please write, in concise English, a lesson draft for pandas groupby and aggregation. The output must include structured fields:\n"
            "- title: the course title;\n"
            "- learning_objectives (3-5 items, each no more than 25 words);\n"
            "- lesson_content: at least 200 words of lesson body, first explaining the groupby idea, then breaking down the aggregation steps with a real business background, including the difference between agg and describe, and adding common-mistake hints;\n"
            "- code_example: minimal runnable pandas code with comments, showing at least one groupby and one agg or describe;\n"
            "- quiz: one single-choice question with options, at least 4 options, marking the correct answer.\n"
            "lesson_content should provide a step-by-step walkthrough and extended thinking."
        ),
        "tags": {"topic": "groupby", "min_objectives": 3},
    },
]

# 2) Define the structured-output model
class CourseDraft(BaseModel):
    title: str = Field(description="lesson title")
    learning_objectives: List[str] = Field(description="learning objectives (3-5 items)")
    lesson_content: str = Field(description="lesson body, a detailed draft of at least 180 words")
    code_example: str = Field(description="minimal runnable pandas code example")
    quiz: str = Field(description="one multiple-choice question (short)")

# 3) Define the five-dimension LLM scoring structure and metric
class EvalScore(BaseModel):
    clarity: int = Field(description="language clarity/ambiguity, 1-5 (high = clearer)")
    factual_correctness: int = Field(description="factual correctness, 1-5 (high = more correct)")
    consistency: int = Field(description="consistency of expression, 1-5 (high = more consistent)")
    redundancy: int = Field(description="expression redundancy, 1-5 (high = more concise)")
    readability: int = Field(description="readability, 1-5 (high = more readable)")
    overall: Optional[float] = Field(default=None, description="optional, total score 0-1")
    feedback: str = Field(description="a one-sentence improvement suggestion")

class LLMEvalMetric(MetricBase):
    def __init__(self, eval_agent: ReActAgent, axis_weights: Optional[Dict[str, float]] = None):
        super().__init__(
            name="llm_eval_course_draft",
            metric_type=MetricType.NUMERICAL,
            description="LLM-as-Judge for five axes",
            categories=[],
        )
        self.eval_agent = eval_agent
        self.axis_weights = axis_weights or {
            "clarity": 1.0,
            "factual_correctness": 1.0,
            "consistency": 1.0,
            "redundancy": 1.0,
            "readability": 1.0,
        }
        # Take a snapshot of the evaluator's pristine state so every call starts clean.
        self._initial_state = copy.deepcopy(self.eval_agent.state_dict())

    async def __call__(self, solution: SolutionOutput) -> MetricResult:
        # Reset evaluator state before scoring to avoid cross-task contamination.
        try:
            self.eval_agent.load_state_dict(copy.deepcopy(self._initial_state))
        except Exception as exc:  # pragma: no cover - defensive
            return MetricResult(
                name=self.name,
                result=0.0,
                message=f"failed to reset evaluator state: {exc}",
            )

        draft = solution.output or {}
        # Provide clear scoring criteria and require strictly structured output
        prompt = (
            "As an educational-content reviewer, please score the following lesson draft on five dimensions from 1-5, and give a one-sentence improvement suggestion.\n"
            "Scoring dimensions:\n"
            "1) clarity: language clarity/ambiguity (clearer = higher score);\n"
            "2) factual_correctness: whether there are factual errors (more correct = higher score);\n"
            "3) consistency: consistency of expression (more consistent = higher score);\n"
            "4) redundancy: expression redundancy (less redundancy = higher score);\n"
            "5) readability: readability (more readable = higher score).\n"
            "Scoring reference: 5 is reserved only for outstanding drafts needing almost no revision; 4 means excellent but still needs minor adjustment; 3 means basically acceptable but with obvious problems; 2 or below means major revision is needed. If lesson_content is under 180 words, lacks a step-by-step walkthrough, or doesn't cover common pitfalls, cap the clarity and readability scores at 3 and explain in the feedback.\n"
            "Check points: whether the number of learning objectives meets the requirement, whether lesson_content includes introduction -> concept -> example -> summary and echoes the code, whether the code example is runnable and commented, and whether the quiz clearly marks the correct answer.\n"
            "Output only the structured fields: clarity, factual_correctness, consistency, redundancy, readability, overall (optional), feedback.\n\n"
            f"Title: {draft.get('title','')}\n"
            f"Learning objectives: {draft.get('learning_objectives', [])}\n"
            f"Body:\n{draft.get('lesson_content','')}\n\n"
            f"Code example:\n{draft.get('code_example','')}\n"
            f"Quiz: {draft.get('quiz','')}\n"
        )

        try:
            res = await self.eval_agent(
                Msg("user", prompt, role="user"),
                structured_model=EvalScore,
            )
        except Exception as exc:
            return MetricResult(
                name=self.name,
                result=0.0,
                message=f"evaluator call failed: {exc}",
            )

        s = res.metadata or {}
        if not isinstance(s, dict):
            return MetricResult(
                name=self.name,
                result=0.0,
                message=f"invalid evaluator metadata type: {type(s).__name__}",
            )

        axes = ["clarity", "factual_correctness", "consistency", "redundancy", "readability"]

        def norm(v: int) -> float:
            return max(0.0, min(1.0, (float(v) - 1.0) / 4.0))

        def _coerce(axis: str) -> int:
            if axis not in s:
                return 1
            return int(s[axis])

        try:
            # Coerce scores to integers, defaulting to baseline when missing.
            values = {axis: _coerce(axis) for axis in axes}
        except Exception as exc:
            return MetricResult(
                name=self.name,
                result=0.0,
                message=f"invalid evaluator payload: {exc}",
            )

        weighted = sum(self.axis_weights[axis] * norm(values.get(axis, 1)) for axis in axes)
        denom = sum(self.axis_weights.values()) or 1.0
        score = weighted / denom

        msg = (
            f"clarity={values.get('clarity')} | factual={values.get('factual_correctness')} | "
            f"consistency={values.get('consistency')} | redundancy={values.get('redundancy')} | "
            f"readability={values.get('readability')} | feedback={s.get('feedback','')}"
        )
        return MetricResult(name=self.name, result=score, message=msg)

# 4) Assemble into a Task list
def build_tasks() -> list[Task]:
    tasks: list[Task] = []
    for item in COURSE_BENCHMARK:
        tasks.append(
            Task(
                id=item["id"],
                input=item["prompt"],
                ground_truth=1.0,  # expect all to pass the objective checks
                tags=item["tags"],
                metrics=[],  # LLM scoring metric injected later
                metadata={},
            )
        )
    return tasks

# 5) Create a minimal agent (real DashScope API call)
agent = ReActAgent(
    name="Friday",
    sys_prompt=(
        "You are an educational course author focused on pandas data analysis. Please write lesson drafts in concise English, "
        "strictly outputting the structured fields: title, learning_objectives(list[str]), lesson_content(str), code_example(str), quiz(str). "
        "lesson_content must be at least 180 words, including introduction, concept explanation, step-by-step example, common-mistake reminders, and a summary."
    ),
    model=DashScopeChatModel(
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        model_name="qwen-plus",
        stream=False,
    ),
    formatter=DashScopeChatFormatter(),
    enable_meta_tool=False,
)

# 5.1) Reviewer agent (can reuse the same model as generation)
evaluator = ReActAgent(
    name="Evaluator",
    sys_prompt=(
        "You are a strict educational-content reviewer. Output structured scores (1-5) and a one-sentence suggestion per the scoring criteria, "
        "and output nothing other than the structured content."
    ),
    model=DashScopeChatModel(
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        model_name="qwen-plus",
        stream=False,
    ),
    formatter=DashScopeChatFormatter(),
    enable_meta_tool=False,
)

# 6) Minimal evaluation loop
async def run_minimal_eval() -> None:
    tasks = build_tasks()
    # Inject the five-dimension LLM scoring metric
    metric = LLMEvalMetric(eval_agent=evaluator)
    for t in tasks:
        t.metrics = [metric]
    scores = []
    for task in tasks:
        res = await agent(
            Msg("user", task.input, role="user"),
            structured_model=CourseDraft,
        )
        draft = {
            "title": res.metadata.get("title"),
            "learning_objectives": res.metadata.get("learning_objectives"),
            "lesson_content": res.metadata.get("lesson_content"),
            "code_example": res.metadata.get("code_example"),
            "quiz": res.metadata.get("quiz"),
        }
        print(
            f"\n[{task.id}] Draft Content:\n"
            f"{json.dumps(draft, ensure_ascii=False, indent=2)}"
        )

        solution = SolutionOutput(success=True, output=draft, trajectory=[])
        metric_res = await task.metrics[0](solution)
        scores.append(metric_res.result)
        print(f"[{task.id}] score={metric_res.result:.2f} ({metric_res.message})")

    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"\nAverage score: {avg:.2f}")

await run_minimal_eval()
```

> Recap: the code above shows the minimal closed loop of "evaluation-driven development" — using `Task + Metric` to encode the objective elements of a "good lesson" into executable checks, then running end-to-end with a real API and quantifying the score. You can try: fine-tuning the `sys_prompt`, swapping the `model_name` or temperature, or improving the metrics (e.g. checking whether the code runs, whether it includes output-screenshot links, etc.), then repeat the evaluation and observe whether the score rises. If you set `AGENTSCOPE_STUDIO_URL` or `OTEL_TRACING_URL`, you can also view the timing and trajectory details of the model/tool/formatter in the tracing backend.

4.1 showed how to build a general evaluation closed loop with AgentScope's `Task + Metric`. Next, apply the same method to a concrete scenario: evaluating the Agent Skill built in Lesson 3.5.

### 4.2 Practice: evaluating your Agent Skill

The evaluation framework from 4.1 directly applies to Skills, but a Skill has two unique validation dimensions: **whether it triggers correctly** (triggers when it should, doesn't when it shouldn't) and **whether the process conforms to the SOP** (whether it executes per the steps defined by the Skill). Below, using `CourseTestingSkill` as an example, we show how to apply the framework above to concrete Skill evaluation.

#### Building a prompt set: positive triggers and negative controls

For a single Skill, **10-20 prompts are enough to discover regressions and validate improvements**. The key is to cover different trigger scenarios:

```csv
id,should_trigger,prompt
test-01,true,"Use CourseTestingSkill to run acceptance testing on the Python intro course"
test-02,true,"Help me check whether this course can be published; I need to verify the code examples and form functionality"
test-03,true,"Run a complete pre-publish test on the course_test_mock.html page"
test-04,false,"Help me fix the CSS style problem in the course page"
```

These four test cases test different scenarios:

- **Explicit invocation (test-01)**: names the Skill directly, validating that `name` and `description` aren't broken.
- **Implicit invocation (test-02)**: describes the scenario without mentioning the Skill name, testing whether the trigger conditions are strong enough.
- **Contextual invocation (test-03)**: adds a specific filename, testing whether it triggers correctly in a noisy prompt.
- **Negative control (test-04)**: should not trigger `CourseTestingSkill`, used to catch false triggering.

As you discover new failure cases, add them to this list — this small CSV becomes a living document of the scenarios the Skill must keep handling correctly.

#### Two-layer check: objective + subjective

A Skill's SOP compliance needs to check both "what was done" and "how well it was done," corresponding respectively to objective and subjective checkers:

**Objective check -> deterministic checker**: analyze the event sequence in the execution trace to verify that key steps occurred.

```python
def check_screenshot_taken(events):
    """Check whether a screenshot command was executed"""
    return any(
        e.get("type") == "tool_call" and
        "screenshot" in e.get("tool_name", "").lower()
        for e in events
    )

def check_report_generated(artifacts):
    """Check whether a test-report file was generated"""
    return any(
        "test_report" in f.lower() or "测试报告" in f
        for f in artifacts
    )
```

The value of these checkers is that they're **deterministic and debuggable** — if a check fails, you can open the execution record and see exactly the execution sequence of each tool call.

**Subjective check -> Rubric scoring**: for qualitative requirements (report structure, coverage, description accuracy), use model-assisted scoring and require a structured response:

```json
{
  "type": "object",
  "properties": {
    "overall_pass": { "type": "boolean" },
    "score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "pass": { "type": "boolean" },
          "notes": { "type": "string" }
        },
        "required": ["id", "pass", "notes"]
      }
    }
  },
  "required": ["overall_pass", "score", "checks"]
}
```

The JSON Schema above defines the structure of the scoring result. Send it together with the following Rubric prompt to the scoring model, having it return a structured result per the Schema:

```
Evaluate the test report generated by CourseTestingSkill, checking the following requirements:
- Whether it includes all required items (title, form, boundary conditions)
- Whether each check item has a clear pass/fail status
- Whether screenshot evidence is attached
- Whether the descriptions are accurate and unambiguous

Return a JSON result conforming to the specified Schema, with check-item ids being:
completeness, status_clarity, evidence, accuracy
```

#### Iterative improvement

The iterative method is consistent with the "establishing evaluation standards iteratively" described in 3.1.1: **every manual fix is a signal — turn it into a test case to ensure the Skill keeps doing it right.** The prompt set and check rules are living documents that keep expanding as the Skill matures.

#### Section recap

- **Reuse the evaluation framework**: the methodology of Skill evaluation focuses on the two validation dimensions unique to Skills: trigger correctness and SOP compliance.
- **Two-layer check**: use deterministic checkers to verify key behaviors, and Rubric scoring to handle qualitative requirements.
- **Living document**: the prompt set and check rules keep expanding as the Skill matures, and every failure case is a starting point for improvement.

## 5 Summary

Let's recap what you learned in this section:

-   **Beyond subjective feeling**: Agent optimization should break free from the "feels good" mode and turn to evaluation-driven development based on objective data — the prerequisite for rigorous, controllable optimization.
-   **Experts define the standards**: evaluation metrics, especially subjective ones, should be led by senior business experts, transforming their hard-to-articulate "tacit knowledge" into clear, measurable rules.
-   **Beware model bias**: when using an LLM for automated evaluation, you must be wary of its inherent biases like style and length, and calibrate periodically with a human-expert "gold test set."
-   **Combine end-to-end and white-box**: use end-to-end evaluation to grasp the Agent's overall user value, while using white-box evaluation to go deep into key components to precisely locate and solve performance bottlenecks.
-   **Iterative refinement**: a powerful evaluation system evolves gradually rather than being achieved in one step. Start with the most critical, most easily-implemented parts and iterate continuously.

## 🔥 Quiz

### 🔍 Single choice 3.6.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Your course-writing Agent's end-to-end evaluation shows the course-quality score stable at 4.2/5, but user feedback says "the code examples often won't run." How should you locate and solve this problem?❓</b>

- A. Raise the strictness of the end-to-end evaluation, bumping the pass threshold from 4.0 to 4.5 to filter out low-quality output
- B. Add white-box evaluation, separately checking whether the code-generation stage's output is executable, precisely locating the fault node
- C. Swap the underlying LLM for a version with stronger coding ability, improving code-generation correctness at the model level
- D. Append an emphatic instruction "the generated code must be guaranteed to run" to the system prompt to constrain the output

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: B**
📝 **Explanation**:
A only tightens the overall scoring threshold and can't precisely locate the specific problem of "code not executable." C is an optional optimization direction, but swapping the model without first locating the problem is blind investment, and the code problem may stem from context rather than model capability. D is the typical "solving an engineering problem with a prompt," with uncertain effect and no way to validate. B is correct: the core value of white-box evaluation is "opening the black box," setting a separate check metric for a specific node in the Agent's execution chain (such as the code-generation stage); only after precisely locating the problem can you optimize in a targeted way.
</div>
</details>

## ✉️ Feedback
You're welcome to participate in the [Alibaba Cloud LLM ACP course survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie) to share your learning experience and course feedback.
Your criticism and encouragement are our motivation to keep improving!
