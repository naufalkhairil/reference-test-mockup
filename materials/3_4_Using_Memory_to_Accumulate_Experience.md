# 3.4 Using Memory to Let the Agent Accumulate Experience

## 🚄 Preface

The Agent can now get things done, but it has no cross-session memory — close the window or clear the context and it resets to zero, so accumulated preferences and pitfalls it's already hit have to be re-explained next time. In this lesson, you'll master the Agent's memory-management strategies, from simple forgetting to active memory, making the Agent understand you better the more you use it.

## 🍁 Course Objectives

**You will learn:**
- Establishing short-term memory: conversation-context management and coping with token limits
- Three memory-management strategies: context truncation, rolling summary, vector-based retrieval
- From passive context to active memory management: the Agent autonomously deciding when to record and when to read
- Building a hybrid system of short-term and long-term memory

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

In this lesson, you'll learn how to give your Agent memory ability, solving the LLM's inherent "forgetfulness" problem. You'll start from the most naive method, gradually discover its limitations, and finally master the industry's mainstream strategies for building short-term and long-term memory.

First, let's configure the environment needed for this lesson.

```python
import os

# Import the modules we'll use later
from agentscope.agent import ReActAgent
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.formatter import DashScopeChatFormatter
from agentscope.embedding import DashScopeTextEmbedding
from agentscope.memory import Mem0LongTermMemory
from agentscope.model import DashScopeChatModel
from agentscope.token import HuggingFaceTokenCounter

# Define a helper function to create an Agent, for convenient reuse in later lessons
def create_agent(name: str, sys_prompt: str, **kwargs) -> ReActAgent:
    """A helper function to create an Agent"""
    # Allow the caller to override the default model/formatter/memory, to avoid repeated binding
    formatter = kwargs.pop("formatter", DashScopeChatFormatter())
    model = kwargs.pop(
        "model",
        DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            stream=True,
        ),
    )
    memory = kwargs.pop("memory", InMemoryMemory())

    return ReActAgent(
        name=name,
        sys_prompt=sys_prompt,
        model=model,
        formatter=formatter,
        memory=memory, # by default, use the simplest in-memory buffer
        **kwargs,
    )

print("Environment configuration complete!")
```

## 1 Establishing Short-Term Memory

In the previous lessons, you've been building a team of Agents that can help you write courses. The content-writing Agent has just finished an excellent draft. You're satisfied and say to it: "Great, now based on the teaching style we discussed last time, make part two more vivid."

However, the Agent's response disappoints you: "OK, what kind of teaching style did we discuss last time?" It has forgotten the details of past tasks. This is because your Agent is stateless. Every time you start a new conversation, it forgets everything from past conversations.

> **Further reading: the LLM's core characteristic — Stateless**
>
> You can imagine the LLM as an expert whose memory lasts only a few seconds. In each independent API call, it can understand all the information you give it and produce a brilliant answer. But once this call ends, it completely forgets everything. It won't remember who you are, what you talked about before, or any of your preferences and requirements. Each `reply` of the Agent is essentially an independent API call, so it naturally inherits this statelessness.

So how do we solve this? The most direct idea is to "review" all the previous chat records every time you talk to it.

In programming implementation, this means you need to create a list to hold all the conversation history. Every time you ask the Agent a question, you send this list containing the complete history along with it. `AgentScope`'s `InMemoryMemory` is exactly the implementation of this naive approach.

Let's verify it with code.

```python
# Create a course-writing Agent
writing_agent = create_agent(
    name="Writer",
    sys_prompt="You are a course-content writer. Your task is to write a Pandas data analysis course."
)

async def run_stateless_test():
    # First conversation: set the teaching style
    msg1 = Msg("user", "Our teaching style should be rigorous and restrained; please remember this.", "user")
    print(f"[{msg1.name}]: {msg1.content}")

    # The Agent stores this conversation in its InMemoryMemory
    reply1 = await writing_agent(msg1)
    print(f"[{reply1.name}]: {reply1.content}")

    print("\n" + "="*20 + "\n")

    # Second conversation: make a new request based on the previous setting
    # When called, writing_agent automatically sends the history in InMemoryMemory together with the new message to the model
    msg2 = Msg("user", "Great, now make part two more professional.", "user")
    print(f"[{msg2.name}]: {msg2.content}")

    reply2 = await writing_agent(msg2)
    print(f"[{reply2.name}]: {reply2.content}")

    print("\n" + "="*20 + "\n")
    print("The Agent's short-term memory content:")
    # Print the Agent's memory; you can see it contains both rounds of conversation
    for m in await writing_agent.memory.get_memory():
        print(f"- [{m.role}] {m.name}: {m.content}")

await run_stateless_test()
```

This approach works immediately; the Agent instantly has short-term conversational memory.

## 2 Information Refinement

But when you put this Agent into a real scenario and use it continuously for a dozen or dozens of rounds, two serious problems emerge:

1.  **Context-window limit**. Every LLM has a maximum text length it can process, which we call the "context window." As the number of conversation rounds increases, the conversation history grows like a snowball, eventually exceeding the model's window limit, and the program errors out directly.
2.  **Sharply rising cost**. LLM API calls are billed by usage; every token in the text you send (input) and it generates (output) costs money. After many rounds of conversation, each API call has to re-send the entire history, incurring repeated token cost.
3.  **Performance degradation: Attention Dilution and "Lost in the Middle"**. Even if your wallet and the model's context window can bear an extremely long conversation history, the model's performance degrades.
    *   **Attention dilution**: as the context length grows, the probability that the model forgets context details gradually increases.
    *   **Lost in the middle**: within a context of the same length, the LLM can often clearly remember information at the beginning (primacy effect) and the end (recency effect), but easily ignores key details located in the middle sections.

This naive "memory" approach is only a short-term strategy of robbing Peter to pay Paul. It quickly leads to program errors or cost overruns.

This raises a core question: **how do you effectively manage the length and cost of the context without sacrificing key information?**

The essence of this question is how to efficiently **compress** and **filter** information. Just as when you prepare for an open-book exam, you won't copy the entire textbook onto your cheat sheet, but will distill the most important formulas, definitions, and key arguments.

## 3 Memory-Management Strategies

Let's borrow the way humans prepare for exams and explore strategies for managing the Agent's memory.

### 3.1 Strategy one: simple "forgetting" — Context Truncation

The simplest, most brute-force method is to remember only the most recent events; this is called **fixed-window truncation**.

-   **Idea**: you set a fixed window size, e.g. keep only the most recent N rounds of conversation, or more precisely, keep only the most recent N tokens. When the conversation history exceeds this size, discard the oldest round, ensuring the total context length stays roughly unchanged.
-   **Relative advantage**: extremely simple to implement, low compute overhead, effectively guaranteeing the context length always stays within a controllable range, avoiding errors and unbounded cost growth.
-   **Applicable scenarios**: suited to scenarios where information value decays quickly over time, such as a chit-chat bot or simple customer-service Q&A.
-   **Boundary condition**: this is a "one-size-fits-all" amnesia scheme. If key information from early in the conversation (e.g. the core goal the user set in the first round) gets truncated, the Agent will "lose its memory" again, causing the conversation logic to break.
-   **Performance risk**: even without exceeding the maximum window limit, only truncating when the window is nearly full means the Agent works with a near-limit long context for a long time. Because of **attention dilution**, this degrades the model's ability to handle complex tasks.

*Figure (translated): fixed-window truncation.*

```text
[Conversation history: rules A B C D] -> [Fixed window: keep only the most recent N entries]
                                              │
                                    ┌─────────┴─────────┐
                                    v                   v
                          [Retain: rules C D]   [Discard: rules A B]
```

In `AgentScope`, this function is implemented by the `Formatter` component. You can pass the `max_tokens` argument when initializing the `Formatter` to limit the context length.

```python
# Create a Formatter with truncation (a token counter must be provided, or truncation won't trigger)
token_counter = HuggingFaceTokenCounter(
    "Qwen/Qwen3-8B",
    use_mirror=True,
    use_fast=True,
    trust_remote_code=True,
)
truncated_formatter = DashScopeChatFormatter(
    token_counter=token_counter,
    max_tokens=40,
)

# Create an Agent that uses this Formatter
truncation_agent = create_agent(
    name="Trunk",
    sys_prompt="You are a forgetful bot; you can only remember the most recent things.",
    # Replace the default formatter with the truncating one we just created
    formatter=truncated_formatter
)

async def run_truncation_test():
    # Have multiple rounds of conversation, deliberately making the context long
    await truncation_agent(Msg("user", "Rule A: all answers must be declarative sentences.", "user"))
    await truncation_agent(Msg("user", "Rule B: do not use 'you' or 'I'.", "user"))
    await truncation_agent(Msg("user", "Rule C: answers should be as short as possible.", "user"))
    await truncation_agent(Msg("user", "Rule D: numbers must be written in uppercase Chinese characters.", "user"))

    print("After multiple rounds of conversation, the Agent's memory (theoretically very long):")
    for m in await truncation_agent.memory.get_memory():
        print(f"- [{m.role}] {m.name}: {m.content}")

    print("\n" + "="*20 + "\n")

    # Ask a question to test whether the Agent still remembers the earliest Rule A
    reply = await truncation_agent(Msg("user", "Please summarize all the rules.", "user"))

    print(f"[{reply.name}]: {reply.content}")
    print("\nThe Agent has very likely forgotten the earliest 'Rule A', because to satisfy the max_tokens=40 limit, it discarded the earliest conversation from the start of its memory.")

await run_truncation_test()
```

### 3.2 Strategy two: distilling the key points — Rolling Summary

Simple truncation directly discards information, which is clearly not ideal. A smarter approach is to **distill** the key points before forgetting the details. This is the **rolling summary** strategy.

-   **Idea**: as the conversation proceeds, when the history is about to "fill up" the window, you call the LLM once to distill the earliest portion of the conversation (e.g. the first 50%) into a short summary. Then, in subsequent requests, you replace the verbose original conversation record with this condensed "memory summary."
-   **Relative advantage**: while compressing the length, it maximally preserves the core information of the historical conversation, better maintaining the long-term coherence of the conversation.
-   **Improved performance**: compressing or even removing context irrelevant to the current task as early as possible helps alleviate attention dilution, thereby improving the Agent's performance on complex tasks.
-   **Applicable scenarios**: suited to tasks that need to maintain goal consistency over the long term, such as project planning, long-form content creation, etc.
-   **Boundary condition**: it introduces additional API-call cost (for generating the summary), and the summary quality directly affects subsequent conversation.

*Figure (translated): summary memory.*

```text
[Full history: conversations 1-10] -> {Check length}
                                       | (does not exceed threshold)    | (exceeds threshold)
                                       v                                v
                                [Keep as is]                [LLM generates summary]
                                                                         |
                                                                         v
                                                          [Compressed: summary + recent conversation]
```

`AgentScope` doesn't currently have this built in, but you can easily implement this logic by customizing a `Memory` class. Below is a **conceptual implementation approach**:

```python
# This is a pseudocode example to demonstrate the core logic of rolling summary
# It can't run directly; you need to inherit agentscope.memory.MemoryBase and implement the full logic

class SummaryMemory: # (MemoryBase)
    def __init__(self, buffer_size=10, summary_ratio=0.5):
        self.history = []
        self.buffer_size = buffer_size
        self.summary_ratio = summary_ratio

    def add(self, message):
        self.history.append(message)
        self.try_summarize()

    def try_summarize(self):
        if len(self.history) > self.buffer_size:
            # 1. Determine the part to summarize
            num_to_summarize = int(len(self.history) * self.summary_ratio)
            messages_to_summarize = self.history[:num_to_summarize]

            # 2. Call the LLM to generate a summary (pseudocode)
            # summary_text = llm.call("Please summarize the following conversation into one paragraph:", messages_to_summarize)
            summary_text = "The user set the teaching style to witty and humorous, and required the content to be vivid."

            summary_message = Msg("system", f"[History summary] {summary_text}", "system")

            # 3. Replace the original conversation with the summary
            self.history = [summary_message] + self.history[num_to_summarize:]
            print(f"--- Memory compressed; current length {len(self.history)} ---")

    def get_memory(self):
        return self.history

# Usage example
# summary_mem = SummaryMemory()
# summary_mem.add(Msg("user", "Our teaching style should be witty and humorous.", "user"))
# ... after multiple rounds of conversation ...
# summary_mem.add(Msg("user", "Add one more case about cost.", "user")) # this may trigger summarization
```

### 3.3 Strategy three: building a knowledge base — Vector-based Retrieval

The previous strategies still process all conversation history in a **linear**, **undifferentiated** way. But this doesn't match our human memory pattern. Your memory isn't a tape played in chronological order, but a huge, interconnected knowledge network.

This "retrieve on demand" pattern is exactly the core of building an advanced memory system. This strategy completely changes the rules of the game: you no longer try to stuff all history into the context, but turn each round of conversation into an independently-retrievable "memory fragment" and store it in a dedicated "long-term memory library."

-   **Idea**:
    1.  **Ingestion**: after each round of conversation, you convert the conversation content into a mathematical vector (Embedding), then store it along with the original text in a **Vector Database**.
    2.  **Retrieval**: when the user asks a new question, you first convert this question into a vector too, then do a similarity search in the database to find the few historical conversation records **most relevant** to the current question.
    3.  **Composition**: finally, you combine the retrieved "relevant memories" and the user's "latest question" into a concise, efficient context, then send it to the LLM.

-   **Relative advantage**: fundamentally shakes off the length constraint of the context window; based on the current intent, it can precisely "recall" the most relevant content from a massive amount of information, greatly saving cost.
-   **Applicable scenarios**: this is the cornerstone of building a truly intelligent Agent capable of long-term interaction. Suited to all complex scenarios such as personalized assistants, enterprise knowledge bases, and intelligent learning companions.
-   **Boundary condition**: the highest system complexity. It introduces new tech stacks such as an Embedding model and a vector database.

*Figure (translated): long-term memory with a vector database.*

```text
Storage phase:    [Conversation content] -> [Convert to vector (embedding)] -> (Vector database)
                                                                                  |
                                                                                  v
Retrieval phase:  [New question] -> [Convert to vector] -> [Similarity search]
                                                              |
                                                              v
                                                   [Top-K relevant conversations]
                                                              |
                                                              v
                                      [Combine relevant memories + new question] -> [Send to model]
```

`AgentScope` elegantly implements this function through the `Mem0LongTermMemory` module. It supports two working modes:

1.  **`static_control`**: automatically and passively save and retrieve memory before and after each Agent reply.
2.  **`agent_control`**: give the Agent tools to actively manage memory (`record_to_memory`, `retrieve_from_memory`), letting the Agent decide for itself when to record and when to recall.

Let's first look at the simpler `static_control` mode.

```python
# 1. Initialize the long-term memory module
# It needs a language model (for internal processing) and an embedding model
from mem0.vector_stores.configs import VectorStoreConfig

# Specify the same dimension (2048) as DashScope Embedding for the local Qdrant vector store
vector_store = VectorStoreConfig(
    config={
        "on_disk": False,
        "embedding_model_dims": 2048,
    }
)

long_term_memory = Mem0LongTermMemory(
    agent_name="Writer",
    user_name="user",
    model=DashScopeChatModel(
        model_name="qwen-plus",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        stream=False,
    ),
    embedding_model=DashScopeTextEmbedding(
        model_name="text-embedding-v4",
        api_key=os.environ.get("DASHSCOPE_API_KEY"),
        dimensions=2048
    ),
    vector_store_config=vector_store,
)

# 2. Create an Agent equipped with long-term memory
ltm_agent_static = create_agent(
    name="LTM_Writer_Static",
    sys_prompt="You are a course writer with long-term memory.",
    long_term_memory=long_term_memory,
    long_term_memory_mode="static_control", # key parameter: set to static-control mode
)

async def run_ltm_static_test():
    # Conversation 1: store a key piece of information
    msg1 = Msg("user", "Remember, we are writing a Pandas data analysis course, and the first draft is now done.", "user")
    print(f"[{msg1.name}]: {msg1.content}")
    reply1 = await ltm_agent_static(msg1)
    print(f"[{reply1.name}]: {reply1.content}")
    # After this step, the conversation content is automatically stored in long-term memory

    print("\n" + "="*20 + " Simulating a new session " + "="*20 + "\n")

    # Clear the Agent's short-term memory to simulate a brand-new session
    await ltm_agent_static.memory.clear()
    print("The Agent's short-term memory has been cleared.")

    # Conversation 2: ask a related question
    # Before replying, the Agent uses the question to retrieve from long-term memory
    msg2 = Msg("user", "Where did we get to in our work last time?", "user")
    print(f"[{msg2.name}]: {msg2.content}")
    reply2 = await ltm_agent_static(msg2)
    print(f"[{reply2.name}]: {reply2.content}")
    print("\nNote: even though the short-term memory was cleared, the Agent can still answer correctly, because it retrieved the relevant information from long-term memory.")

await run_ltm_static_test()
```

### 3.4 Advanced: from passive context to active memory management

By now, you've mastered powerful strategies for building a memory system for the Agent. But a truly intelligent Agent shouldn't just passively receive the context you've prepared; it should be able to **actively manage its own memory**.

By setting `long_term_memory_mode` to `agent_control`, the `ReActAgent` automatically gains the two tools `record_to_memory` and `retrieve_from_memory`. You need to guide it in the system prompt to use these tools.

```python
# Reuse the long_term_memory instance created earlier
# Re-create an Agent, this time using agent_control mode
from textwrap import dedent
ltm_agent_active = create_agent(
    name="LTM_Writer_Active",
    sys_prompt=dedent(
        "You are a course writer with active memory-management ability.\n"
        "You can use the following tools to manage your long-term memory:\n"
        "- `record_to_memory(data: str)`: record an important piece of information into long-term memory.\n"
        "- `retrieve_from_memory(query: str) -> str`: retrieve relevant information from long-term memory based on a query.\n"
        "Before answering a question, first think about whether you need to retrieve memory. After the conversation ends, think about whether there's key information to record."
    ),
    long_term_memory=long_term_memory,
    long_term_memory_mode="agent_control", # key parameter: set to Agent-control mode
)

async def run_ltm_active_test():
    # Conversation 1: the Agent autonomously decides to record information
    msg1 = Msg("user", "The course's writing style must be very rigorous and academic; this is a core requirement.", "user")
    print(f"[{msg1.name}]: {msg1.content}")
    reply1 = await ltm_agent_active(msg1)
    # In its thinking process here, the Agent judges that "core requirement" is important information and calls the record_to_memory tool
    print(f"[{reply1.name}]: {reply1.content}")

    print("\n" + "="*20 + " Simulating a new session " + "="*20 + "\n")
    await ltm_agent_active.memory.clear()

    # Conversation 2: the Agent autonomously decides to retrieve information
    msg2 = Msg("user", "I forgot — what was our course's writing style again?", "user")
    print(f"[{msg2.name}]: {msg2.content}")
    reply2 = await ltm_agent_active(msg2)
    # In its thinking process here, the Agent first calls retrieve_from_memory(query="writing style"), then generates the answer based on the retrieval result
    print(f"[{reply2.name}]: {reply2.content}")

await run_ltm_active_test()
```

In this way, memory is no longer data you "feed" the Agent from the outside, but inner knowledge it actively acquires, stores, and maintains itself. This lets the Agent evolve from a simple "tool" toward a true "partner."

> **Further reading: cost-benefit analysis**
>
> You might think that vector-based retrieval and active memory management introduce Embedding-model calls, vector-database queries, and extra LLM inference (to decide whether to call a tool), which increases cost and latency.
>
> However, we can't simply compare the cost of "one high-quality output" with the cost of "one low-quality output." Because if a single call can't effectively solve the problem (e.g. forgetting a key requirement), then no matter how low its cost, it's a waste.
>
> A fairer comparison is: to obtain a "usable" answer, what is the total cost of each path?
> - **Path A (no long-term memory)**: one call, gets a wrong answer (problem unsolved). You have to manually remind it and call again to solve the problem.
> - **Path B (with long-term memory)**: one call (including retrieval), directly gets the correct answer (problem solved).
>
> From this angle, the extra investment in the memory system is a necessary investment to ensure output quality and avoid repeated, ineffective attempts.

### 3.5 Building a short-term and long-term memory system

Through the combination of the above strategies, you've built a complete memory system for the Agent, which can be clearly divided into two parts:

*   **Short-term Memory**: based on a conversation buffer, managed through truncation or summary strategies. Its core responsibility is to **maintain the coherence of the current session**. For example, remembering the specific requirement you just made about "Chapter 2's content needs one more case added."
*   **Long-term Memory**: based on a vector database and tool-based calls. Its core responsibility is to **persistently store key information and support intelligent cross-session retrieval**. For example, remembering that the entire course project's core goal is "designed for beginners, with a witty and humorous style."

An Agent with memory is no longer a cold, one-off Q&A machine. It can learn from experience, remember your preferences, understand long-term context, and finally evolve from a simple "tool" into a true "partner."

> **Practical implementation and usage suggestions**
>
> **I. Quickly introducing memory ability**
>
> You can use mature open-source frameworks or platforms to quickly add memory ability to your Agent.
> *   **AgentScope**: as shown in this lesson, `AgentScope` provides `InMemoryMemory` as basic short-term memory, and `Mem0LongTermMemory` integrated with `Mem0` as an out-of-the-box long-term memory solution.
> *   **Mem0**: an open-source intelligent memory layer designed specifically for AI applications; it encapsulates complex logic like vector-based retrieval and memory-conflict handling, providing powerful underlying support.
> *   **LangChain Memory**: the powerful Agent development framework LangChain provides rich built-in Memory modules, including `ConversationBufferMemory` (buffer), `ConversationSummaryMemory` (summary), and `VectorStoreRetrieverMemory` (vector retrieval), allowing you to flexibly combine them as needed.
> *   **Alibaba Cloud Model Studio platform**: for teams that want quick validation or have a non-technical background, the Model Studio platform provides a visual Agent-building flow; you just need simple configuration to enable long-term memory for the Agent.
>
> **II. Memory-usage suggestions**
>
> *   **Remember selectively**: more memory isn't always better. Accumulating lots of low-value or noisy information interferes with subsequent retrieval. You should establish an admission mechanism for memory writes, e.g. writing only when the user explicitly asks ("please remember...") or when the information's importance exceeds a certain threshold. The `agent_control` mode is a good way to achieve this.
> *   **Continuous governance**: memory is a kind of dynamic data asset that needs a continuous governance mechanism, including regularly cleaning up outdated information, merging duplicate entries, verifying factual accuracy, and providing users an interface to actively manage their own memory (view, modify, delete).
> *   **Scenario-based application**: different business scenarios have different memory needs. For example, in a course-document workflow that requires style consistency, personalized preferences shouldn't be recorded; but for a product's factual information (such as API parameters, feature limits), you can record it and regularly review its validity to ensure the accuracy of the Agent's generated content.
---

## 4 Summary

Let's recap what you learned in this section:

*   **The root of the problem: statelessness**: the LLM itself has no memory; each call is independent. Naively passing the complete history leads to overly-long context and out-of-control cost.
*   **Short-term memory vs. long-term memory**: you can manage **short-term memory** through "truncation" and "summary" strategies to maintain the coherence of the current session; and build **long-term memory** through "vector-based retrieval" to achieve cross-session knowledge storage and access.
*   **Active memory management**: by providing the Agent with memory tools like `save`, `recall`, and `update`, you can turn it from passively receiving context into an agent that actively manages and uses its own memory, achieving true learning and growth.
*   **Memory best practices**: a powerful memory system needs to be effectively governed. You should write selectively, continuously clean up and update memory, and decide what to remember and what not to based on the specific business scenario.

## 🔥 Quiz

### 🔍 Single choice 3.4.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>After your course-writing Agent works for 30 rounds straight, it forgets the "style must be rigorous and academic" requirement the user set in round 1, and starts outputting casual, colloquial content. You're currently using a simple truncation strategy (keep the most recent N rounds). What's the most reasonable improvement?❓</b>

- A. Expand the truncation window from N rounds to 2N rounds to ensure the early style requirement isn't discarded
- B. Hardcode the style requirement into the system prompt so it's unaffected by the memory-management strategy
- C. Introduce vector-based long-term memory, persistently storing key preferences and retrieving them on demand before each reply
- D. Switch to a rolling-summary strategy, periodically compressing old conversation into a summary to preserve core information

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: C**
📝 **Explanation**:
A only delays when the problem occurs; no matter how big the window, it eventually fills up, and a long context causes attention dilution. B is feasible in this scenario, but only applies to known, fixed preferences; it can't handle new preferences the user dynamically generates during conversation, so it isn't general. D is better than truncation and can preserve some key information, but the summary quality depends on the compression model, and long-term accumulation may still lose details. C is the most reasonable: vector-based long-term memory persists key preferences into a vector database and, each time, retrieves the most relevant memory by the current task's semantics, fundamentally shaking off the length limit of the context window.
</div>
</details>

## ✉️ Feedback
You're welcome to participate in the [Alibaba Cloud LLM ACP course survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie) to share your learning experience and course feedback.
Your criticism and encouragement are our motivation to keep improving!
