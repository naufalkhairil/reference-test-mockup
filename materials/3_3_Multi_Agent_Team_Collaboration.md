# 3.3 Team Collaboration with Multiple Agents

## 🚄 Preface

Task planning taught the Agent to execute step by step, but complex projects still need multiple Agents each doing their own job — just like a team of human experts, where specialists in different roles each handle the parts they're good at, collaborating to accomplish a task one person can't do well. In this lesson, you'll learn two mainstream multi-agent collaboration patterns: "hierarchical planning," like a project manager leading a team, and "co-creation collaboration," like a brainstorm around a whiteboard — and you'll master the design method of distilling an Agent collaboration architecture from real-world team collaboration.

## 🍁 Course Objectives

**You will learn:**
- Two multi-agent collaboration patterns: hierarchical planning (Leader-Worker, implemented with handoff) and co-creation collaboration (Blackboard, implemented with MsgHub)
- The design method of distilling an Agent collaboration architecture from real-world human team collaboration
- Cost awareness of multi-agent systems (3-5x token consumption) and pattern-selection advice

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

## 1 Collaborating Like a Human Team
One day, your colleague proposes: could the bot participate in developing course drafts? For example, writing an interactive-course draft on Pandas data analysis. Of course, ideally the bot could handle courses across many domains, which may have different work stages. You'll find this is a more general task.

You learned earlier:
- For a multi-stage task like writing, you can't have a single Agent complete all tasks — the Agent easily drops things and produces poor results. You should break it into multiple steps, each specialized step handled by a different expert Agent.
- For a creative, diverse task like writing, the steps differ for different types of course writing; you can't enumerate all the writing steps and solidify them into fixed workflows. You can try letting the Agent plan the writing process itself.

So the problem now becomes: how do you effectively organize multiple Agents so they can each plan and execute in parallel, and also integrate the final work products together?

To achieve this, you can borrow the way a team of human experts works. Human experts each have their own areas of expertise; they collaborate to complete complex tasks, and can process tasks in parallel. So you can alsocombine multiple Agents into an Agent Team, where each Agent is an expert in a relevant field, everyone divides the work and collaborates, and they process in parallel.

## 2 Two Collaboration Patterns

In concrete implementation, human expert teams have two common patterns: one is decomposition-and-execution led by a project manager, and the other is a brainstorm around a whiteboard. In multi-agent systems, these correspond respectively to the hierarchical-planning pattern and the co-creation-collaboration pattern.

### 2.1 **Pattern one: Hierarchical Planning (Hierarchical/Team Leader Pattern)**

This is the most direct simulation of how a "project team" works, and its core feature is a centralized star structure. It introduces two roles:

1.  **Team Leader (Leader Agent)**: in this example it can be a "course project supervisor" Agent. It's responsible for receiving and understanding the top-level task (such as "write a Pandas data analysis course"), decomposing it into multiple concrete subtasks ("design the teaching outline," "provide core cases and code," "write the course text," etc.), and assigning these subtasks to suitable team members. It also tracks overall progress and, after all members finish, aggregates the results to form the final course text.
2.  **Team Members (Member Agents)**: each has expertise in a specific domain (instructional designer, data scientist, content writer), focuses on executing the subtask assigned to it, and reports back to the Leader when done.

*Figure (translated): hierarchical planning — a Leader agent assigns subtasks, workers report back.*

```text
[Top-level task: write course] -> [Project manager: Leader Agent]
                                      | (assign)              | (assign)                | (assign)
                                      v                       v                         v
                          [Instructional designer]   [Data scientist]      [Content writer]
                                   (Teacher Li)           (Engineer Wang)        (Xiao Zhang)
                                      │ (report)              │ (report)               │ (report)
                                      └───────────────────────┴────────────────────────┘
                                                              v
                                                  [Final summary: complete course]
```

In AgentScope, you can implement the hierarchical-planning pattern using the handoff mechanism. In this pattern, the Leader Agent treats domain experts as tools, and assigning tasks and hearing reports are implemented in the form of tool calls. AgentScope also supports asynchronous tool calls and dynamic tool extension, meaning you can execute multiple expert Agents concurrently, and even let the Leader Agent create expert Agents in real time as needed.

```python
import os
from typing import Any

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.tool import ToolResponse, Toolkit

# ---- 1. Define the unified expert-Agent roles and prompts ----

DESIGNER_LI_PROMPT = """
You are Teacher Li, an experienced instructional designer. Your task is to design a clear, logical teaching outline for the "Intro to Pandas Data Analysis" course. Focus on: 1. Defining clear learning objectives for each module. 2. Ensuring the knowledge points go from easy to hard, progressing step by step. 3. Proposing interactive exercises and projects to consolidate the learning outcome.
"""

SCIENTIST_WANG_PROMPT = """
You are Engineer Wang, a senior data scientist and a hands-on Pandas expert. Your task is to provide accurate, practical technical content for the course. Focus on: 1. Providing the most core, most commonly-used Pandas knowledge points. 2. Designing cases and datasets drawn from real work scenarios. 3. Writing concise, standard, easy-to-understand code examples.
"""

WRITER_ZHANG_PROMPT = """
You are Xiao Zhang, a creative course-content writer. Your task is to turn technical content into course text that is easy to understand yet rigorous, with a calm and restrained tone. Focus on: 1. Explaining complex concepts with plain language and analogies. 2. Designing highly realistic case scenarios and module titles. 3. Ensuring the course's overall tone is encouraging and inspiring.
"""

LEADER_PROMPT = """
You are a course project supervisor, responsible for coordinating the team to complete the draft development of the "Intro to Pandas Course."
You have three team members you can call as tools, and each one's work depends on the previous one's output.

Your workflow must strictly follow this order:
1.  **First, call invoke_designer_li** to have him create a preliminary outline and learning objectives for the course.
2.  **Second, call invoke_scientist_wang**. Pass Teacher Li's generated outline as the `context` argument, and ask him to fill in technical points and code examples based on this outline.
3.  **Next, call invoke_writer_zhang**. Merge all of Teacher Li's and Engineer Wang's output and pass it as the `context` argument, asking her to write the complete, learner-friendly course text on this basis.
4.  **Finally**, after receiving all experts' final results, integrate them into a final course document with unified formatting and complete content, then give it as your final reply.
"""

# ---- 2. Unified model and Agent configuration ----

def get_model_instance() -> DashScopeChatModel:
    """Get a uniformly-configured model instance."""
    return DashScopeChatModel(
        model_name="qwen-plus",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
    )

def create_member_agent(name: str, sys_prompt: str) -> ReActAgent:
    """Create a team-member Agent from the given name and system prompt."""
    return ReActAgent(
        name=name,
        sys_prompt=sys_prompt,
        model=get_model_instance(),
        formatter=DashScopeMultiAgentFormatter(),
    )

# ---- 3. Define the "team member" Agents as tools (Handoffs pattern) ----

async def invoke_designer_li(task_description: str, context: str = "") -> ToolResponse:
    """
    Call instructional designer Teacher Li when you need to design a course outline, learning objectives, or teaching activities.

    Args:
        task_description (str): clearly describe the design task you need Teacher Li to complete.
        context (str): optional. Pass relevant background information or prior work products.
    """
    print("\n--- Task dispatch: calling instructional designer Teacher Li ---")
    agent = create_member_agent("DesignerLi", DESIGNER_LI_PROMPT)

    content_for_agent = task_description
    if context:
        content_for_agent = f"Background information:\n{context}\n\nYour task: {task_description}"

    result_msg = await agent(Msg(name="user", role="user", content=content_for_agent))
    return ToolResponse(content=result_msg.get_text_content())

async def invoke_scientist_wang(task_description: str, context: str = "") -> ToolResponse:
    """
    Call data scientist Engineer Wang when you need professional technical knowledge, code examples, or real cases.

    Args:
        task_description (str): clearly describe the technical task you need Engineer Wang to complete.
        context (str): optional. Pass prior work products such as the course outline, so he can build on them.
    """
    print("\n--- Task dispatch: calling data scientist Engineer Wang ---")
    agent = create_member_agent("ScientistWang", SCIENTIST_WANG_PROMPT)

    content_for_agent = task_description
    if context:
        content_for_agent = f"Please complete your task based on the following course outline and background information:\n{context}\n\nYour specific task is: {task_description}"

    result_msg = await agent(Msg(name="user", role="user", content=content_for_agent))
    return ToolResponse(content=result_msg.get_text_content())

async def invoke_writer_zhang(task_description: str, context: str = "") -> ToolResponse:
    """
    Call content writer Xiao Zhang when you need to turn technical content into easy-to-understand text.

    Args:
        task_description (str): clearly describe the writing task you need Xiao Zhang to complete.
        context (str): optional. Pass prior work products such as the outline and technical points as the writing basis.
    """
    print("\n--- Task dispatch: calling content writer Xiao Zhang ---")
    agent = create_member_agent("WriterZhang", WRITER_ZHANG_PROMPT)

    content_for_agent = task_description
    if context:
        content_for_agent = f"Please complete your writing task based on the following course draft (containing the outline and technical points):\n{context}\n\nYour specific task is: {task_description}"

    result_msg = await agent(Msg(name="user", role="user", content=content_for_agent))
    return ToolResponse(content=result_msg.get_text_content())

# ---- 4. Organize the "hierarchical planning" workflow ----

async def main() -> None:
    """Main execution function, responsible for orchestrating the whole workflow."""

    # 4.1 Create the supervisor's toolkit and register the team members
    leader_toolkit = Toolkit()
    leader_toolkit.register_tool_function(invoke_designer_li)
    leader_toolkit.register_tool_function(invoke_scientist_wang)
    leader_toolkit.register_tool_function(invoke_writer_zhang)

    # 4.2 Create the supervisor Agent
    leader_agent = ReActAgent(
        name="ProjectLeader",
        sys_prompt=LEADER_PROMPT,
        model=get_model_instance(),
        toolkit=leader_toolkit,
        formatter=DashScopeMultiAgentFormatter(),
    )

    # 4.3 Define the top-level task
    top_level_task = (
        "Please create a short course draft on Pandas data analysis for beginners."
    )

    print(f"Top-level task received by the project supervisor:\n{top_level_task}\n" + "="*50)

    # 4.4 Hand the task to the supervisor Agent to execute
    final_response_msg = await leader_agent(Msg(name="user", role="user", content=top_level_task))

    # 4.5 Show the final result
    print("\n" + "="*50)
    print("  The project supervisor's final aggregated report:")
    print("="*50 + "\n")
    print(final_response_msg.get_text_content())

# ---- 5. Run the main program ----
await main()
```

When a course-development project kicks off, the project supervisor breaks the requirements document into a clear task list, then distributes it to the **instructional designer, data scientist, and content writer**. The advantages of this pattern are obvious: **clear structure, clear division of responsibility**. Everyone knows their own task and delivery deadline, and the project supervisor can easily track overall progress, ensuring the project doesn't stray off track. More importantly, from a context-engineering perspective, **each sub-agent has an independent context window**; it only needs to focus on the part of the task it's responsible for, without being disturbed by irrelevant information from other stages. This means each sub-agent's input is more focused and its output more precise — the instructional designer focuses only on outline design, the data scientist focuses only on code examples, each producing local content in its own "focus space," so quality is naturally higher. Therefore, this pattern is very suitable for scenarios with **a clear goal that can be cleanly decomposed into multiple parallel subtasks**.

But this pattern's limitations also stem from its structure. The **instructional designer and data scientist** usually don't communicate directly, but pass information through the project supervisor. If, while writing code, the **data scientist** finds that a certain theoretical point could be explained more clearly with a simpler example, he needs to report to the supervisor first, and the supervisor then relays it to the designer. This process **may involve information delay or distortion**. In the end, although each module of the course is completed with high quality, combined together they may feel a bit stiff, lacking a seamless, integrated flow. Because the experts lack direct, real-time collision of ideas.

```python
import os
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.pipeline import MsgHub
from textwrap import dedent

# ---- 1. Define the unified expert-Agent roles and prompts ----

DESIGNER_LI_PROMPT = """
You are Teacher Li, an experienced instructional designer. Your task is to design a clear, logical teaching outline for the "Intro to Pandas Data Analysis" course. In the discussion, you focus on: 1. Defining clear learning objectives for each module. 2. Ensuring the knowledge points go from easy to hard, progressing step by step. 3. Proposing interactive exercises and projects to consolidate the learning outcome.
"""

SCIENTIST_WANG_PROMPT = """
You are Engineer Wang, a senior data scientist and a hands-on Pandas expert. Your task is to provide accurate, practical technical content for the course. In the discussion, you focus on: 1. Providing the most core, most commonly-used Pandas knowledge points. 2. Designing cases and datasets drawn from real work scenarios. 3. Writing concise, standard, easy-to-understand code examples.
"""

WRITER_ZHANG_PROMPT = """
You are Xiao Zhang, a creative course-content writer. Your task is to turn technical content into course text that is easy to understand yet rigorous, with a calm and restrained tone. In the discussion, you focus on: 1. Explaining complex concepts with plain language and analogies. 2. Designing highly realistic case scenarios and module titles. 3. Ensuring the course's overall tone is encouraging and inspiring.
"""

# ---- 2. Helper function to create an expert Agent ----
def create_expert_agent(name: str, sys_prompt: str) -> ReActAgent:
    """Create an expert Agent from the given name and system prompt."""
    return ReActAgent(
        name=name,
        sys_prompt=sys_prompt,
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
        ),
        formatter=DashScopeMultiAgentFormatter(),
    )

# ---- 3. Main function organizing the collaboration flow ----
async def main() -> None:
    """Run the co-creation collaboration pattern for Pandas course development, and generate the final result."""
    print("=== Starting the course-development meeting: brainstorming the 'Intro to Pandas' course outline and cases ===")

    # Create the course-development team
    designer_li = create_expert_agent("Teacher Li (Instructional Designer)", DESIGNER_LI_PROMPT)
    scientist_wang = create_expert_agent("Engineer Wang (Data Scientist)", SCIENTIST_WANG_PROMPT)
    writer_zhang = create_expert_agent("Xiao Zhang (Content Writer)", WRITER_ZHANG_PROMPT)

    # Define the meeting opening remarks
    announcement = Msg(
        "system",
        (
            "Hello team, our goal today is to collaborate on a complete, engaging **course outline and core cases** for the 'Intro to Pandas Data Analysis' course. "
            "Please brainstorm together, starting with instructional designer Teacher Li — offer your first round of suggestions."
        ),
        "system",
    )

    # Start multi-round discussion
    async with MsgHub(
        participants=[designer_li, scientist_wang, writer_zhang],
        announcement=announcement,
    ) as hub:
        for i in range(2):
            print(f"\n--- Collaboration round {i + 1} ---")
            # Call each in speaking order
            await designer_li()
            await scientist_wang()
            await writer_zhang()

    print("\n=== Meeting ended ===")

    # ==================== Aggregation stage ====================
    print("\n=== Starting to generate the final team result (course outline draft) ===")

    # 4.1 Define a "meeting secretary" Agent to organize the meeting minutes
    secretary_prompt = dedent("""
        You are a professional meeting secretary, very skilled at organizing meeting minutes.
        Your task is to read the team discussion record below, then, based on the discussion, generate the **course outline draft**
        for the "Intro to Pandas Course" in clear Markdown format.

        The outline should include the following parts:
        - **Module title**: an engaging title.
        - **Learning objectives**: clearly list what students can do after finishing this module.
        - **Core concepts**: the key technical points covered.
        - **Core case**: the hands-on case and dataset running through this module.
        - **Code examples**: the key code demonstrations to include.
        - **Homework exercise**: a specific hands-on exercise task.
    """)
    secretary_agent = create_expert_agent("Meeting Secretary", secretary_prompt)

    # 4.2 Prepare the complete discussion record
    full_transcript_msgs = await designer_li.memory.get_memory()

    transcript_text = "Below is the team's discussion record:\n\n"
    for msg in full_transcript_msgs:
        if msg.role != "system":
            transcript_text += f"[{msg.name}]: {msg.content}\n"

    # 4.3 Assign the aggregation task
    final_task_prompt = dedent(
        f"{transcript_text}\n"
        "Please organize a course outline draft based on the above discussion record."
    )

    # Call the secretary Agent to complete the task
    final_output_msg = await secretary_agent(Msg("user", final_task_prompt, "user"))

    # 4.4 Show the final result
    print("\n" + "="*25)
    print("  Final team result: course outline draft")
    print("="*25 + "\n")
    print(final_output_msg.content)

await main()
```

In this kind of open discussion, one person's idea immediately sparks another's inspiration, producing a "1+1>2" effect. This **decentralized collaboration can maximally stimulate collective intelligence**, and is especially suited to solving **open-ended, creative problems that have no single correct answer and need brainstorming**.

Of course, this pattern's risks are also obvious. A brainstorm without good facilitation may well **fail to converge for a long time because the discussion diverges**, or fall into a deadlock. Since there's no centralized decision-maker, the team may over-optimize some details while losing sight of the overall goal. At the same time, all members need to constantly sync and process the massive amount of information from others, which places higher demands on controlling communication cost.

## 3 Selection Advice: Design Comes from Reality

After learning the two patterns — hierarchical planning and co-creation collaboration — a natural question is: which should I choose? Or are there other patterns?

The answer is: **there is no so-called "best pattern."** The design of an excellent multi-agent system often comes from imitating and distilling the real world.

Rather than memorizing abstract pattern names, it's better to go into your business and observe how teams of human experts complete similar tasks in the real world. When observing, you can focus on the following three aspects:

*   **Business process**: what stages does the task itself contain? Are these stages upstream-downstream dependent or can they run in parallel? How are they connected?
*   **Expert roles**: what experts with different abilities does this process need? What are their core responsibilities?
*   **Collaboration mode**: how do the experts communicate? Do they pass information through a centralized project manager, or discuss freely around a whiteboard in a meeting room? How does information flow between them?

Based on these observations, you can follow a clear design path:

1.  **① Observe reality**: deeply understand how the human team works.
2.  **② Reconstruct the process**: map the real-world roles and collaboration process to your Agent roles and collaboration mechanism.
3.  **③ Iteratively improve**: on top of the reconstruction, use AI's strengths to optimize and enhance.

For example, in our course-development case, the "project supervisor" pattern is a simulation of a project with a clear Deliverable; while the "brainstorm" pattern is a simulation of an early creative-ideation meeting. In reality, a complete project may even have both: first determine the core creative idea through a "brainstorm," then switch to the "project supervisor" pattern to divide the work and execute. This hybrid pattern retains the controllability of the overall structure while introducing creativity at key points.

Ultimately, remember this core idea:

**Rather than memorizing what patterns Multi-Agent has, go into the business and see how human experts collaborate in the real world.**

## 4 Summary

Let's recap what you learned in this section:

*   **The limitation of a monolithic Agent**: a single Agent pursuing "omnipotence" often performs poorly on complex tasks spanning multiple professional domains (such as course development), due to knowledge boundaries and cognitive load.
*   **The core idea of multi-agent**: from the failure of the rigid "pipeline" pattern, inspired by efficient real-world teams, you recognized that "specialized division of labor, parallel processing, communication and integration" is the key to solving complex problems.
*   **Multi-agent collaboration patterns**: you mastered two mainstream collaboration patterns. The **hierarchical-planning pattern**, by simulating a "project supervisor - expert" structure, efficiently handles tasks that can be cleanly decomposed; the **co-creation-collaboration pattern**, by simulating a "brainstorm," stimulates collective intelligence on open-ended problems.
*   **The trade-off between cost and value**: although a multi-agent system increases call cost and latency, by improving the "usability" of the final output it avoids the repeated attempts and hidden costs caused by low-quality output — an effective investment in high-quality results.

## 🔥 Quiz

### 🔍 Single choice 3.3.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Your team is going to use a multi-agent system to develop a new course. The requirements are clear: first the instructional designer produces the outline, then the technical expert fills in code examples, and finally the editor writes the text. Which collaboration pattern should you choose?❓</b>

- A. Co-creation collaboration, letting three Agents discuss freely around a shared whiteboard and produce the final plan through multiple rounds of iteration
- B. Hierarchical planning, setting up a Leader Agent to assign subtasks to each expert Agent in order and aggregate the results
- C. Have one all-powerful Agent play the three roles in turn, completing all the stages in the same context window
- D. Have the three Agents each independently complete a full course draft, then have a human pick the best-quality one as the finished product

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: B**
📝 **Explanation**:
This task has clear upstream-downstream dependencies (outline → code → text), a clear goal, and is decomposable — well suited to the hierarchical-planning pattern. A's co-creation pattern suits open-ended creative problems (such as "what kind of case to design"); used for a task with a clear process, it easily diverges and fails to converge. C violates the core value of multi-agent — each Agent has an independent context and focuses on its own task; a monolithic Agent handling multiple roles easily suffers attention diffusion. D is a parallel-redundancy strategy rather than collaboration; it wastes 3x compute resources and can't leverage the advantage of specialized division of labor.
</div>
</details>

## ✉️ Feedback
You're welcome to participate in the [Alibaba Cloud LLM ACP course survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie) to share your learning experience and course feedback.
Your criticism and encouragement are our motivation to keep improving!
