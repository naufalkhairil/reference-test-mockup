# 2.6 Building agents for complex tasks

## 🚄 Preface

Having completed the previous chapters, you have successfully built a Q&A bot – one that can accurately answer questions related to writing guidelines.

Now, many colleagues have raised a similar request: since the Q&A bot is well-versed in writing guidelines, could it assist in developing educational courses?

Let's analyze the technical feasibility. You'll find that the bot can only retrieve writing guidelines from its internal knowledge base. It cannot access the latest research papers, nor can it automatically remember the progress of course development.

This is because a standalone Large Language Model (LLM) is like a brain isolated in a room – it can think, but it lacks senses to receive real-time information, hands and feet to perform specific tasks, and the ability to learn continuously.

To overcome these limitations, you need to build a complete system on top of an LLM, allowing it to perceive its environment, think, plan, execute tasks, and learn from experience, much like a domain expert. This system is called an Agent. It consists of the following core modules:

| Core Module        | Function                                                  | Analogy         |
|--------------------|-----------------------------------------------------------|-----------------|
| Thinking & Planning| LLM understands intent, breaks down tasks into executable steps | 🧠 Brain        |
| Perception         | Receives user input, API responses, system status         | 👀 Senses       |
| Execution          | Calls APIs, queries databases, sends messages             | ✋ Hands & Feet  |
| Memory             | Stores history, experiences, lessons, supports decision-making | 📚 Memory       |

These four modules form a **"Think-Act-Observe"** closed loop. Through this cycle, an Agent can autonomously plan, execute tasks, and adjust its behavior based on real-world feedback to accomplish complex tasks.

## 🍁 Goals

Agent building is an experimental science with no standard methodology, so you will need to continuously explore and iterate on Agent architectures in practice. This section will delve into the core modules and evaluation system of Agents, helping you master:
- Task Decomposition Capability: Breaking down complex requirements into executable steps.
- Prototype Building Capability: Rapidly setting up business Agent systems.
- Evaluation and Iteration Capability: Quantitatively diagnosing and continuously optimizing.

## 🛠️ Environment setup and basic tools

At the start of this course, you will continue to learn how to use the OpenAI SDK to call LLMs. Here is an example:

```python
import os
from openai import OpenAI
from config.load_key import load_key
load_key()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_API_BASE"),
)

completion = client.chat.completions.create(
    model="qwen-plus", 
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Who are you?'}
    ]
)
print(completion.choices[0].message.content)
```

## 1 Teaching the agent to use tools
### 1.1 Your first tool function
A colleague is developing an online course on "Basic Principles of LLMs," and he hopes the bot can help him collect the latest teaching materials from the internet.

You will find that the bot can only retrieve information from the company's knowledge base or answer questions using the LLM's world knowledge.

#### 1.1.1 Hardcoded solution: The simplest implementation
To enable the bot to access internet information, the most direct approach is to write a web search tool function for it. This function will search for the user's question each time and send the search results along with the question to the LLM.

Suppose you have already written a function called web_search that can find information via a search engine. Now, when a user makes a request, you want the model to utilize this function. The simplest way to implement this is for the program to "hardcode" the execution of this function upon receiving a request, then send the execution result along with the original request to the LLM, allowing it to generate a summary response.

*Figure (translated): hardcoded tool calling — the flow is fixed in code.*

```text
[User request] -> [Hardcoded execution: web_search] -> [Search results (text data)]
      |                                                    |
      └──────────────────┬─────────────────────────────────┘
                         v
                    [LLM (Qwen-Plus)] -> [Final response]
```

```python
# 1. User's original request
user_request = "Hello, please help me collect some latest materials about Transformer models."

# 2. "Hardcoded" execution of the tool function
# The web_search function here is simulated to focus on the core logic.
def web_search(query: str):
    """Simulates performing a web search and returning results in JSON format."""
    print(f"--- [Tool Executing] Searching: {query} ---")
    # In a real scenario, this would call a real search engine API.
    return '''{
        "results": [
            {"title": "Attention Is All You Need (Transformer original paper)", "url": "https://arxiv.org/abs/1706.03762", "snippet": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks... We propose a new simple network architecture, the Transformer, based solely on attention mechanisms..."},
            {"title": "The Illustrated Transformer – Jay Alammar", "url": "https://jalammar.github.io/illustrated-transformer/", "snippet": "A visual and intuitive explanation of the Transformer model."}
        ]
    }'''

tool_result = web_search(query=user_request)

print(f"User Request: {user_request}")
print(f"Tool Result: {tool_result}\n")

# 3. Concatenate the user request and tool result into a prompt and send it to the LLM.
#    The goal is for the model to generate a human-readable response based on the structured tool output.
completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {'role': 'system', 'content': 'You are a course research assistant. Your task is to generate a friendly and clear response to the user based on the tool execution results.'},
        {'role': 'user', 'content': f'User original request: "{user_request}"\nTool execution result: {tool_result}'}
    ]
)

# 4. Output the model's final response
final_response = completion.choices[0].message.content
print(f"Model's Final Response:\n{final_response}")
```

#### 1.1.2 Limitations analysis: Why a more flexible solution is needed

While this approach is simple and effective, it has limitations: it only applies to scenarios where "there is exactly one tool, and it must be called every time." As colleagues' needs grow, your bot may need to add more tools, such as `search_arxiv_paper` (to search for papers on academic sites like Arxiv) or `fetch_webpage_content` (to retrieve the full content of a specified web page). At this point, you will encounter a more difficult problem: how can the bot call tools on demand?

### 1.2 Intent recognition: Letting the agent decide which tool to use
#### 1.2.1 Fragile keyword matching
A direct idea is to write a "router" that uses `if/elif` structures and keyword matching to determine the user's intent.

```python
# Pseudocode: A fragile, keyword-based tool router
def route_to_tool(user_input):
    if "paper" in user_input or "arxiv" in user_input:
        return "search_arxiv_paper"
    elif "search" in user_input or "find" in user_input or "materials" in user_input:
        return "web_search"
    elif "summarize" in user_input or "content" in user_input or "http" in user_input:
        return "fetch_webpage_content"
    # ... You need to keep adding elif conditions here
    else:
        return "no_tool_needed"
```

The drawbacks of this method are immediately apparent: it's very **fragile and difficult to maintain**. If the user says, "I want to see what that 'Attention Is All You Need' paper is about," this rudimentary router cannot identify the intent to use `search_arxiv_paper` and `fetch_webpage_content` because it does not contain any predefined keywords.

#### 1.2.2 LLM-based intent recognition
A better approach is to list all available tools in the prompt and let the LLM decide which tool to call and with what parameters. This is a simple implementation of intent recognition.

```python
def get_tool_decision_from_llm(user_request):
    from textwrap import dedent

    # Use dedent to remove indentation added for code aesthetics,
    # preventing these formatting tabs/spaces from being passed to the LLM.
    prompt = dedent(f"""
        You are a routing module for an intelligent assistant. Your task is to select the most suitable tool from the list below to solve the problem based on the user's request, and provide the input parameters.

        [Available tools list]
        1. web_search: Used to search for general information on the internet.
        2. search_arxiv_paper: Used to search for academic papers on Arxiv.org.
        3. fetch_webpage_content: Used to retrieve the content of a web page from a specified URL.

        [User request]
        "{user_request}"

        [Decision]
        Please tell the user your decision.
    """)
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.0 # Use low temperature to get more deterministic decisions
    )
    decision = completion.choices[0].message.content
    return decision

# --- Test cases ---
request = "Help me find that classic Transformer paper titled 'Attention Is All You Need'"
decision = get_tool_decision_from_llm(request)
print(f"User request: \"{request}\"")
print(f"Model decision: {decision}\n")
```

### 1.3 Ensuring reliability: Structured output
#### 1.3.1 Why structured output is needed
Now that you've solved the problem of "which tool to call," the next step is to parse and execute the LLM's decision using code. However, you'll find that the LLM's results are interspersed with natural language and lack a fixed format:

*   `I will use the search_arxiv_paper tool to search for the classic Transformer paper titled "Attention Is All You Need".`
*   `Okay, the tool is search_arxiv_paper`
*   `search_arxiv_paper(query="Attention Is All You Need")`

This is because LLMs tend to generate diverse text, but what you need is an easy-to-parse, deterministic data format. To solve this problem, you need to turn it around and require the model to output strictly according to your predefined structured format.

JSON is such an ideal format. A clearly defined JSON output is unambiguous and easy to parse:
```json
{
  "tool_name": "search_arxiv_paper",
  "parameters": {
    "query": "Attention Is All You Need"
  }
}
```
It clearly defines "what to do" (tool_name) and "what to use to do it" (parameters). This key-value pair structure can be easily parsed by any programming language.

#### 1.3.2 Building a "guide-validate-retry" closed loop

The next task is to ensure that the model can consistently and strictly output in the JSON structure you define. To achieve this, you need to establish a clear process.

1.  **Define structure**: First, you need to precisely define your expected output structure. You can use JSON Schema (a language for describing JSON data structures) or define data models in Python code using libraries like Pydantic. This Schema explicitly states which fields the final output must contain and the type of each field, serving as the foundation of the entire process.

2.  **Construct the prompt**: In your prompt, in addition to giving task instructions, you should also include the complete Schema definition and provide one or two output examples that perfectly conform to this Schema. Through this "instruction + example" method, the model can more thoroughly understand your requirements.

3.  **Validate and retry**: After receiving the model's output, the program must strictly validate it using the same Schema. If validation fails, the program should capture the validation error message and send it, along with the model's previous erroneous output, back to the model as a correction clue, requesting it to regenerate.

*Figure (translated): structured output with schema validation and retry.*

```text
[User request] -> [Schema definition + prompt construction] -> [LLM generation] -> {Validate}
                                                                                      |
                              ┌─────────────── (Pass) ───────────────► [Structured result]
                              │
                              ├── (Fail, less than 2 times) ──► [Retry] ──► (back to LLM generation)
                              └── (Timeout) ──► [Failure]
```

```python
import json
from textwrap import dedent
from typing import Union, Literal
from pydantic import BaseModel, Field, ValidationError, TypeAdapter

# 1. Define Pydantic parameter models for course research-related tools
class WebSearchParams(BaseModel):
    query: str = Field(description="Keywords for web search.")

class SearchArxivParams(BaseModel):
    query: str = Field(description="Paper title or keywords for searching on Arxiv.org.")

# 2. Define the tool call model, binding tool name with its corresponding parameter model
class WebSearchCall(BaseModel):
    tool_name: Literal["web_search"]
    parameters: WebSearchParams

class SearchArxivCall(BaseModel):
    tool_name: Literal["search_arxiv_paper"]
    parameters: SearchArxivParams

# Use Union type to indicate that the model's final decision is one of these two calls
ToolCall = Union[WebSearchCall, SearchArxivCall]

# 3. Build the prompt, including clear instructions, tool definitions, and examples
def build_prompt(user_request: str) -> str:
    return dedent(f"""
        Your task is to select the most suitable tool from the list of available tools based on the user's request, and output the call information in a strict JSON format.

        # Available tools:
        - `web_search(query: str)`: Use when needing to search for general information, news, or non-academic content.
        - `search_arxiv_paper(query: str)`: Use when needing to search for academic papers, especially from Arxiv.org.
        - `fetch_webpage_content(url: str)`: Use to retrieve content from a specified URL. # Note: This tool was mentioned in 1.2.1 but not defined in the class here, adding it for completeness if it were present.

        # Output format requirements:
        You must strictly follow the JSON structure below and do not include any additional natural language explanations.

        {{
        "tool_name": "tool_name",
        "parameters": {{
            "parameter_name": "parameter_value"
        }}
        }}

        # Example:
        User request: "What's the latest interesting news in the AI field?"
        Your output:
        {{
        "tool_name": "web_search",
        "parameters": {{
            "query": "latest news in AI field"
        }}
        }}

        # User request:
        "{user_request}"

        # Your output:
    """)

# 4. Call and validate (with retry)
def get_structured_output(user_request: str, max_retries: int = 2):
    messages = [{'role': 'user', 'content': build_prompt(user_request)}]
    adapter = TypeAdapter(ToolCall)

    for attempt in range(max_retries):
        # This is an API call to the LLM service. For the universality of the course, the specific implementation is omitted.
        # You can replace it with your own code, e.g., client.chat.completions.create(...)
        completion = client.chat.completions.create(
            model="qwen-plus", messages=messages, temperature=0
        )
        raw_output = completion.choices[0].message.content

        try:
            # Parse and validate
            # Remove markdown code block fences if present
            clean_output = raw_output.strip().removeprefix('```json').removesuffix('```').strip()
            data = json.loads(clean_output)
            # Use Pydantic model to validate the parsed data
            validated_data = adapter.validate_python(data)
            return validated_data.model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            # If failed, add the error message and the original output to the conversation history,
            # so the model can make corrections
            messages.extend([
                {'role': 'assistant', 'content': raw_output},
                {'role': 'user', 'content': f"Format error: {e}. Please strictly re-output in JSON format."}
            ])

    return None

# Usage
# Assume client variable is already initialized elsewhere
user_request = "Help me find that classic Transformer paper titled 'Attention Is All You Need'"
result = get_structured_output(user_request)

if result:
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

By establishing such a "guide-validate-retry" closed loop, you can improve parsing success rates and make your tool-calling code more robust and reliable.

> **Further reading: Controlled decoding**
>
> Many model providers' "JSON Mode" does not rely solely on "optimized training" but uses a more precise technique: **controlled decoding**.
>
> When the model generates each token, it first calculates the probability distribution of all candidate tokens. At this point, the system, based on the grammar rules compiled from your provided Schema, prunes all options from these candidate tokens that cannot form a legal JSON.
>
> This is like a grammar checker, but instead of checking after the fact, it "hides" all options that would lead to grammar errors from the keyboard every time you choose the next character.
>
> This technique transforms "output format" from a vague task that the model needs to "learn" into a deterministic process driven by grammar rules, fundamentally ensuring the reliability of the output.

### 1.4 Mainstream solution: Function calling
#### 1.4.1 How function calling works
The "intent recognition -> structured output -> validation and retry" flow you just manually implemented is a robust tool-calling process, but its full implementation is quite complex. To simplify development, many LLM service providers (such as Alibaba Cloud, OpenAI, Anthropic, Google, etc.) have built this capability into their APIs, which is known as **function calling** or **tool calling**.

Taking OpenAI SDK's function calling as an example:

*   **Tool definition**: You need to define the available tools in the `tools` parameter of the API, using JSON Schema to describe each tool's `name`, `description`, and `parameters` (the structure of input parameters required by the function).

*   Call decision: The model automatically decides whether to call a tool based on user input and tool definitions. If a tool call is needed, the model returns a `tool_calls` field in its response, containing the name of the function to be called and the JSON parameters conforming to the Schema.

*   Execute & return: You need to:
    1. Parse the function name and parameters from `tool_calls`.
    2. Actually execute the corresponding function in your code.
    3. Wrap the function execution result into a message with `role: "tool"`.
    4. Call the API again, sending the tool execution result back to the model.
    5. The model generates the final user response based on the tool's return.

*Figure (translated): the complete tool-calling sequence.*

```text
1. User -> LLM:   first API call (model + messages + tools)
2. LLM -> User:   tool_calls returned (function_name + arguments)
3. User -> Tool:  actual function call with arguments
4. Tool -> User:  execution result
5. User -> LLM:   second API call with tool results
6. LLM -> User:   final response (based on tool results)
```

```python
import json
# 1. Define the list of tools, including the JSON Schema description for each function
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_arxiv_paper",
            "description": "Search for academic papers on Arxiv.org",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Title or keywords of the paper"},
                },
                "required": ["query"],
            },
        }
    }
]
# 2. Make the first API call to let the model decide
messages = [{"role": "user", "content": "Help me find that classic Transformer paper 'Attention Is All You Need'"}]
response = client.chat.completions.create(
    model="qwen-plus", messages=messages, tools=tools, tool_choice="auto"
)
response_message = response.choices[0].message
# 3. Check if the model decided to call a tool and execute
if response_message.tool_calls:
    tool_call = response_message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    print(f"Model decided to call tool: `{function_name}`")
    print(f"Arguments: {function_args}")

    # Here we simulate the function execution result
    tool_result = json.dumps({"paper_id": "1706.03762", "url": "https://arxiv.org/abs/1706.03762", "title": "Attention Is All You Need"})
    print(f"Tool execution result: {tool_result}")
    # 4. Pass the model's decision and the tool's execution result back to the model to generate the final response
    messages.append(response_message)
    messages.append(
        {"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": tool_result}
    )

    final_response = client.chat.completions.create(model="qwen-plus", messages=messages)
    print("\nModel's final response:")
    print(final_response.choices[0].message.content)
```

#### 1.4.2 ReAct pattern: Think-act-observe

You will find that the results of tool calls are passed to the LLM through another call. The LLM will observe the results of the tool call, then think about whether the task is complete, and then reply with the final answer or continue to act (call another tool). This is very similar to the "multi-turn conversation" you learned earlier.

We call this **think-act-observe** loop pattern **ReAct**, and Agents that work according to this pattern are called **ReAct Agents**.

Manually implementing ReAct Agent logic is complex. To simplify the development process, we will use [AgentScope](https://github.com/agentscope-ai/agentscope), a production-grade Agent framework that has already encapsulated the complete logic of ReAct Agent and tool calling for you.

> AgentScope is a production-grade Agent framework designed for developers. It defines Agent communication, memory, and tool calling in a standardized way, allowing you to focus on business logic rather than underlying implementations. Key advantages of AgentScope include:
> 
> - **Out-of-the-box ReAct Agent**：Built-in complete "think-act-observe" loop logic.
> - **Flexible tool management**: Uniformly manages tool functions through the `Toolkit` class, supporting automatic parsing of tool JSON Schema.
> - **Multi-model support**: Compatible with mainstream LLM APIs such as OpenAI, DashScope, Anthropic.
> - **State management**: Automatically handles conversation history, tool call records, and other states.
> - **Asynchronous support**: All core functions support asynchronous calls to improve performance.

Let's look at how AgentScope implements the tool call we just discussed:

*Figure (translated): how AgentScope runs the same tool call.*

```text
1. Developer -> Agent:  configure model and formatter, register tool functions
2. Developer -> Agent:  ask: find the paper "Attention Is All You Need"
3. Agent -> Tool:       call search_arxiv_paper
4. Tool -> Agent:       return paper links
5. Agent -> Developer:  return result (ToolResponse)
```

```python
import asyncio
from agentscope.agent import ReActAgent
from agentscope.tool import Toolkit, ToolResponse
from agentscope.model import DashScopeChatModel
from agentscope.message import Msg, TextBlock
from agentscope.formatter import DashScopeChatFormatter

# 1. Define a tool that returns results using ToolResponse
def search_arxiv_paper(query: str) -> ToolResponse:
    """Searches for academic papers on Arxiv.org.

    Args:
        query (str): Search keyword
    """
    print(f"--- [Tool executing] Searching Arxiv for: {query} ---")
    # Simulate search results here
    paper_url = "https://arxiv.org/abs/1706.03762"
    return ToolResponse(
        content=[
            TextBlock(
                type="text",
                text=f"Successfully found paper '{query}'. You can access it here: {paper_url}",
            )
        ]
    )

async def run_agentscope_example():
    # 2. Register the tool function to the toolkit
    toolkit = Toolkit()
    toolkit.register_tool_function(search_arxiv_paper)

    # 3. Create a ReActAgent and equip it with the toolkit
    agent = ReActAgent(
        name="Course Research Agent",
        sys_prompt="You are a course research assistant, skilled at collecting and organizing learning materials.",
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
        ),
        toolkit=toolkit,
        formatter=DashScopeChatFormatter()
    )

    # 4. Send a message to the Agent, it will automatically complete all steps
    user_request = "Help me find that classic Transformer paper 'Attention Is All You Need'"
    msg = Msg(name="user", content=user_request, role="user")

    print(f"User request: {user_request}\n")
    await agent(msg)

# Run the example
try:
    # In a Jupyter Notebook environment, you can directly await the coroutine
    await run_agentscope_example()
except NameError:
    # In a regular Python script, you need to use asyncio.run() to run asynchronous functions
    asyncio.run(run_agentscope_example())
```

Compared to the manually implemented OpenAI Function Calling, AgentScope's advantages are:
1. **More concise tool definition**: You only need to write regular Python functions with docstrings; the framework automatically parses and generates the JSON Schema.
2. **No manual parsing required**: `ReActAgent` automatically handles the tedious steps of parsing `tool_calls`, executing functions, and wrapping results internally.
3. **Automatic conversation history management**: The framework automatically records user messages, tool calls, tool results, etc., without requiring manual maintenance.
4. **Supports multi-turn tool calls**: If one tool call is insufficient, the Agent will automatically continue to think and call more tools until the task is completed.

Seeing AgentScope's concise implementation, you might wonder: since there's an existing framework, why bother learning the cumbersome manual implementation?
This is because:

1. **Understand underlying principles**: The framework internally performs the "call model -> parse tool_calls -> execute function -> call model again" process. Understanding the mechanism is essential for debugging issues.
2. **Custom requirements**: Production environments often require special logic such as permission validation, caching, retries, and logging monitoring. Understanding the underlying principles allows for framework extension.
3. **Compatibility assurance**: When some models or platforms do not support standard Function Calling formats, manual implementation can serve as a fallback solution.

### 1.5 Scalable management: Model context protocol (MCP)
#### 1.5.1 Challenges of tool reuse
The Function Calling pattern solves the problem of how a single application calls tools. However, when tools need to be reused across multiple Agent applications, it introduces challenges for scalable maintenance.
Imagine your team has multiple Agents, all needing to call internet search, internal company document search, and other tools. If a parameter in a tool's API changes, you need to modify every Agent that depends on it, leading to high maintenance costs. The root cause of the problem is that **tool definitions are hardcoded into the code of each "consumer" (Agent application)**.

#### 1.5.2 Decoupling concept of MCP
To solve this problem, Anthropic proposed the **Model Context Protocol (MCP)**. Its core idea is to shift the responsibility for defining tools from the "consumer" to the "provider."

* **Without MCP**: Each AI application needs to encapsulate all tool definitions itself. When a tool is updated, all applications need to be modified.
* **With MCP**: The tool service provider (e.g., search service) "broadcasts" its capability definitions. AI applications only need to connect to the service provider via the MCP protocol to automatically obtain the latest tool definitions, without hardcoding.

*Figure (translated): with vs. without MCP — MCP provides one unified tool definition shared by all applications.*

```text
Without MCP (each application wraps all tools itself):
[Agent A] -> [Search service] + [Document service]
[Agent B] -> [Search service] + [Document service]
[Agent C] -> [Search service] + [Document service]

With MCP (unified tool definition):
[Agent A] ─┐
[Agent B] ─┼──► [MCP] ──► [Search service]
[Agent C] ─┘              [Document service]
                          [Data service]
```

#### 1.5.3 Practice: Self-Hosting and Connecting to MCP Services

This practice demonstrates a self-contained workflow for AgentScope's MCP, simplifying development by launching tool servers directly within the notebook.

Execution Steps:
> - Run Cell 1 (Add Server): Execute the first cell below to start the add service. It will run in the background, and you should see a success message.
> - Run Cell 2 (Multiply Server): Next, execute the second cell to start the multiply service in its own background thread.
> - Run Cell 3 (Client): Before running the final client cell, ensure your DashScope API credentials are set as environment variables.

```python
# Cell 1: Start the Adding Service (Elegant 'if/else' version)

import threading
import time
from mcp.server import FastMCP

# The main logic is now a clean if/else block.
# Condition: Is the server thread variable defined AND is the thread still alive?
if 'add_server_thread' in globals() and add_server_thread.is_alive():
    # This block executes if the server is already running.
    print("✅ Add Server is already running in the background.")
else:
    # This block executes on the first run, or if the previous thread has died.
    # This is now our primary, "happy path" logic for starting the server.
    
    print("Starting Add Server in a background thread...")

    def start_add_server():
        """Starts the addition MCP server."""
        print("Add Server: Initializing...")
        mcp_add = FastMCP("Add", port=8001)

        @mcp_add.tool()
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        
        print("Add Server: Preparing to run on port 8001 (transport=sse)...")
        mcp_add.run(transport="sse")

    # Define the global variable 'add_server_thread' here.
    add_server_thread = threading.Thread(target=start_add_server, daemon=True)
    add_server_thread.start()
    
    time.sleep(2) 
    
    if add_server_thread.is_alive():
        print("✅ Add Server seems to have started successfully in the background!")
    else:
        print("❌ Add Server failed to start. Please check the logs.")
```

You might get following outputs:
```text
INFO:     Started server process [6909]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
Starting Add Server in a background thread...
Add Server: Initializing...
Add Server: Preparing to run on port 8001 (transport=sse)...
✅ Add Server seems to have started successfully in the background!
```

```python
# Cell 2: Start the Multiplication Service (Elegant 'if/else' version)

import threading
import time
from mcp.server import FastMCP

# The main logic is a clean if/else block.
# Condition: Is the server thread variable defined AND is the thread still alive?
if 'multiply_server_thread' in globals() and multiply_server_thread.is_alive():
    # This block executes if the server is already running.
    print("✅ Multiply Server is already running in the background.")
else:
    # This block executes on the first run, or if the previous thread has died.
    
    print("Starting Multiply Server in a background thread...")

    def start_mul_server():
        """Starts the multiplication MCP server."""
        print("Multiply Server: Initializing...")
        mcp_mul = FastMCP("Multiply", port=8002)

        @mcp_mul.tool()
        def multiply(a: int, b: int) -> int: # Note: Renamed from 'mul' to 'multiply' to match agent's call
            """Multiply two numbers."""
            return a * b
        
        print("Multiply Server: Preparing to run on port 8002 (transport=sse)...")
        mcp_mul.run(transport="sse")

    # Define the global variable 'multiply_server_thread' here.
    multiply_server_thread = threading.Thread(target=start_mul_server, daemon=True)
    multiply_server_thread.start()
    
    time.sleep(2)
    
    if multiply_server_thread.is_alive():
        print("✅ Multiply Server seems to have started successfully in the background!")
    else:
        print("❌ Multiply Server failed to start. Please check the logs.")
```

You might get following outputs:
```text
Starting Multiply Server in a background thread...
Multiply Server: Initializing...
Multiply Server: Preparing to run on port 8002 (transport=sse)...
INFO:     Started server process [6909]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
✅ Multiply Server seems to have started successfully in the background!
```

```python
# Cell 3: Run this Client Cell

# --- Core Imports ---
import asyncio
import json
import os
from pydantic import BaseModel, Field

# --- AgentScope Imports ---
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeChatFormatter
from agentscope.mcp import HttpStatelessClient, HttpStatefulClient
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.tool import Toolkit

# ==============================================================================
# Client Execution Logic
# ==============================================================================
class NumberResult(BaseModel):
    result: int = Field(description="The result of the calculation")

# --- Initialize Toolkit and Clients ---
toolkit = Toolkit()

# Client 1: Connect to the add service (sse)
add_mcp_client = HttpStatefulClient(
    name="add_mcp",
    transport="sse",
    url="http://127.0.0.1:8001/sse",
)

# Client 2: Also connect to the multiply service using sse
multiply_mcp_client = HttpStatefulClient(
    name="multiply_mcp",
    transport="sse",
    url="http://127.0.0.1:8002/sse",
)
# =====================================================================

# Stateful clients must be connected before use
print("Connecting to stateful 'add_mcp' server...")
await add_mcp_client.connect()
print("Connecting to stateful 'multiply_mcp' server...")
await multiply_mcp_client.connect() # Also connect the second client
print("All connections successful.")

# Register the MCP clients to the toolkit
await toolkit.register_mcp_client(add_mcp_client)
await toolkit.register_mcp_client(multiply_mcp_client)
print("All MCP clients registered with the toolkit.")

# --- Initialize the Agent ---
agent = ReActAgent(
    name="Jarvis",
    sys_prompt=(
        "You are a helpful AI assistant. You must think and act step-by-step. "
        "When you have the final answer, you MUST use the 'generate_response' tool "
        "to provide the final, structured answer."
    ),
    model=DashScopeChatModel(
        model_name="qwen-max",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
    ),
    formatter=DashScopeChatFormatter(),
    toolkit=toolkit,
)

# --- Run the agent with a calculation task ---
print("\nAgent starting calculation task...")
response = await agent(
    Msg(
        "user",
        "Calculate 2345 multiplied by 3456, then add 4567 to the result. What is the final outcome?",
        "user",
    ),
    structured_model=NumberResult,
)

print(
    f"\nStructured Output:\n```json\n{json.dumps(response.metadata, indent=2, ensure_ascii=False)}\n```"
)

# --- Manual Tool Call Demonstration ---
add_tool_function = await add_mcp_client.get_callable_function("add", wrap_tool_result=True)
manual_result = await add_tool_function(a=5, b=10)
print(f"\nManual call to 'add(a=5, b=10)' returned: {manual_result}")

# --- Clean up resources ---
print("\nDisconnecting stateful clients...")
await add_mcp_client.close()
await multiply_mcp_client.close() # Also close the second client
print("All connections closed. Script finished.")
```

You might get following outputs:
```text
Connecting to stateful 'add_mcp' server...

Connecting to stateful 'multiply_mcp' server...

All MCP clients registered with the toolkit.

Agent starting calculation task...
Jarvis: {
    "type": "tool_use",
    "id": "call_179xxxxxxxxdf28",
    "name": "multiply",
    "input": {
        "a": 2345,
        "b": 3456
    }
}
Jarvis: {
    "type": "tool_use",
    "id": "call_f71xxxxxxxx6600",
    "name": "add",
    "input": {
        "a": 4567,
        "b": 0
    }
}

...

Jarvis: The multiplication of 2345 and 3456 gives a result of 8104320. Adding 4567 to this result, we get a final outcome of 8108887. Therefore, the answer is 8108887.

...

Manual call to 'add(a=5, b=10)' returned: ToolResponse(content=[{'type': 'text', 'text': '15'}]

Disconnecting stateful clients...
All connections closed. Script finished.
```

MCP aims to solve the scalability problem of "how tools are discovered and managed" by decoupling tool definition from tool usage.

> **Related thinking: USB protocol**
>
> You can compare MCP to the USB protocol in the real world. Before USB, each peripheral (mouse, keyboard, printer) had its own unique interface, and computers needed to adapt to each one. The USB protocol unified all of this, allowing any compliant device to be plug-and-play.
> *   **Function Calling** is like an **internal bus** on a computer motherboard, defining how the CPU communicates with a specific component.
> *   **MCP** is like an **external USB interface**, defining an open standard that allows countless third-party devices to easily integrate into the ecosystem.

At this point, you have mastered the complete chain from single tool functions, reliable intent recognition, to scalable tool management. Your Agent can now stably and efficiently interact with the outside world.

### 1.6 Summary

Let's review what you've learned in this section:
* **Connecting models to the outside world**: You learned how to write tool functions for Agents to retrieve external information, and how to upgrade from fragile `if/else` rule judgments to leveraging the LLM's own understanding to decide which tool to call.
* **Manually implementing reliable tool calls**: You mastered how to build a "guide-validate-retry" closed loop to make the model stably output structured JSON instructions, and understood that this is the underlying logic for robust tool calls.
* **Function calling and tool discovery**: You learned about "function calling," an industry standard that encapsulates the complex process of tool calling into simple APIs. Furthermore, you also learned how the MCP protocol decouples tool definition from usage, solving the challenges of scalable reuse and maintenance.
* **ReAct loop and development frameworks**: You recognized that tool calling is key to implementing the **ReAct (think-act-observe)** loop pattern and learned how to use development frameworks like AgentScope to free you from tedious manual implementations, allowing you to focus more on business logic.

## 2 Teaching the agent to reflect
### 2.1 Course unexpectedly modified
A colleague wrote an interactive course in Jupyter Notebook format, which included some executable Python code. To make the course language more engaging, you asked the bot to polish the language style of the entire document.

After polishing, the course language became smoother and the structure clearer. However, when he tried to run the code examples in the course, he discovered a critical issue:

```python
# Original code of the course
def get_user_data(usr_id: str):
  # ... some logic ...
  return f"Data for {usr_id}"

# Executes normally
print(get_user_data(usr_id="u-123"))
```

When "optimizing" the language style, the bot quietly "corrected" the code:

```python
# Agent's polished code
def get_user_data(user_id: str):
  # ... some logic ...
  return f"Data for {user_id}"

# Runtime error!
# print(get_user_data(usr_id="u-123"))  # TypeError: get_user_data() got an unexpected keyword argument 'usr_id'
```

The bot thought `user_id` was more standard than `usr_id`, so it "optimized" the function definition, but this caused an error when calling the function, because the parameter name at the call site was not changed along with it.

### 2.2 LLM hallucinations

How should you solve this problem? The most direct idea is to tell the bot to "be careful". You could try adding a warning to its instructions (System Prompt):

```
You are a top course writer, responsible for polishing Jupyter Notebook formatted courses.
Please optimize the text to make it more engaging.
**Important: Absolutely do not modify any content within code blocks, including variable names, parameter names, and function calls.**
```
But this doesn't work well, because you can't list prohibitions to cover all possible scenarios. Even if you explicitly forbid certain modifications, the LLM still has a certain probability of "accidentally" changing correct content into errors.

The reason is that due to LLM hallucinations, each generation it produces may introduce new errors, and it lacks an internal mechanism for verification and correction. This "optimization" is not limited to variable names, but can also occur in:

- Command-line arguments (changing `-p 8080` to `--port 8080`)
- API version numbers (updating `v1/users` to `v2/users`)
- Example values (replacing demo IP address `192.168.1.10` with `127.0.0.1`)

and any other places it deems "not standardized enough." Ultimately, a course that has been "optimized" but is mixed with errors will plunge students into endless debugging loops.

Therefore, you naturally think of another approach: let the LLM check itself before outputting, just as humans check their answers before submitting an exam. This is one method currently used in the industry to solve such problems, which we call **reflection**.

### 2.3 Two modes of reflection
#### 2.3.1 Mode one: Self review

To implement reflection, the most direct approach is to have the model examine its own output. There are two ways to implement this: one is simple but has limited effectiveness, the other is more complex but significantly more effective.

##### 2.3.1.1 Method one: Single-step instruction-based reflection

This is the easiest method to think of. You try to instruct the model within a single model call, through the Prompt, to reflect while generating the answer.

```
## Role
You are a top course writer.

## Task
1. Polish the language expression of the course and output the entire polished document.

2. Reflect on the polished content:
   - Does it comply with writing guidelines?
   - Has other content been accidentally modified besides language expression?
   Output the reflection results and modification suggestions.

3. Modify the course according to the suggestions and output the modified full content.

## Course draft
{original_notebook_content}
```

*Figure (translated): single model call with generation, reflection, and correction all-in-one.*

```text
[Course draft] -> [Single LLM call: generate + reflect + correct (all-in-one)] -> [Output result]
```

This method has its advantages: the model can promptly detect and correct issues during generation, and the context remains coherent, reducing the overhead of multiple rounds of communication.
However, it also has obvious drawbacks: when reflection is tied to generation, the model can easily fall into a "self-verification" trap, carrying the same cognitive bias into its self-assessment. For example, if it changed `usr_id` to `user_id` in the first step, it is very likely to consider this a "standardization improvement" rather than an error during the second step of reflection.

##### 2.3.1.2 Method two: Two-step "generate-feedback"

You can also separate the reflection process, breaking the task into two model calls: one responsible for generation, and the other for review.

```
# First call (Writing Agent)
You are a top course writer, responsible for polishing Jupyter Notebook formatted courses. Please optimize the text to make it more engaging.

[Course Draft]: {original_notebook_content}

# Second call (Technical Review Agent)
You are a strict technical reviewer. Your task is to review the polished course content to ensure:
1. The polished course complies with writing guidelines.
2. Technical content such as code, configurations, and data has not been accidentally modified.

Please compare [Original Content] and [Polished Content]:
- If only the wording has been changed, and technical content such as code is completely identical (or only non-functional changes like comments, formatting), answer "Pass."
- If any technical content is found to be modified (e.g., code logic, variable names, parameters, configuration items), answer "Fail" and specify where the content was accidentally modified.

[Original Content]: {original_notebook_content}

[Polished Content]: {draft_content}

```

*Figure (translated): writer + reviewer — the reviewer checks from an independent perspective.*

```text
[Course draft] -> [Writing Agent: generate content] -> [Review Agent: independent perspective check]
                      ^                                        |
                      |                (feedback: issues)      | (passed)
                      └────────────────────────────────────────┴──────► [Output result]
```

Because the review Agent has a different perspective from the writing Agent, this method can effectively avoid most role biases. You can even set up multiple specialized review Agents—for factual review, logical review, style review, security review. This not only increases the comprehensiveness of the review but also facilitates later A/B testing and metric statistics.

However, this method also has obvious costs: each additional review Agent adds another model call, leading to higher token consumption.

> **Further reading: Cost and optimization**
>
> **Is this cost worth it?**
>
> The "generate-feedback" loop seemingly increases the number of calls, but we cannot simply compare the cost of "one high-quality output" with "one low-quality output." A fairer comparison is: what is the total cost of both paths to obtain a "usable" answer?
>
> If a single call cannot effectively solve the problem, then no matter how low its cost, it is a waste. Conversely, by using a two-step "generate-feedback" approach, allowing a mid-tier model to achieve 95% of the effect of a top-tier model, almost the same business value can be achieved at a lower cost.
>
> **How to further reduce costs?**
>
> In the "generate-feedback" loop, the original course document is repeatedly passed through multiple model calls—the writing Agent needs it, the review Agent needs it, and it may be used again during the correction phase. If the document is very long (e.g., a complete course with dozens of code examples), this repetition can lead to significant token consumption.
>
> Alibaba Cloud Model Studio provides a [context cache](https://www.alibabacloud.com/help/en/model-studio/context-cache) mechanism to solve this problem: shared content (like the original document) is cached during the first call, and subsequent calls detect the same prefix and directly reuse it. The cached part is billed at 20% of the standard unit price.
> 
> You can organize your Prompt structure like this:
> ```
> [Cached part - same for all calls]
> ## Original course document
> {very long original notebook content}
> 
> [Variable part - different for each call]
> ## Task
> {writing instructions / review instructions / correction instructions}
> 
> ## Content to be processed
> {polished draft / review feedback, etc.}
> ```

It is important to note that the review Agent should only be responsible for "identifying issues" rather than "directly rewriting." If it directly modifies the content, it may alter the original expressive intent or introduce new errors.

Therefore, it's best to feed the review result (`review_result`) back to the writing Agent, allowing it to continue modifying the answer based on the feedback. This forms a "generate-feedback" loop, significantly improving the faithfulness of the bot's responses.

##### 2.3.1.3 Drawbacks of self-reflection

Self-reflection is more suitable for static text-level comparisons (e.g., checking if code has been accidentally modified), but its effectiveness is poor when you need to verify if the code can run normally.

This is because LLMs are good at judging whether code "looks reasonable," but cannot perform precise semantic validation like a compiler. More critically, the model cannot actually execute code—it cannot see runtime logs, catch error reports, or perceive library version conflicts or environment configuration issues.

To solve this problem, we need to introduce an external feedback mechanism.

#### 2.3.2 Mode two: External feedback
##### 2.3.2.1 Using tools to validate results
The core idea of external feedback is to execute the LLM's generated results in a real environment, then feed the execution results (success/failure, error messages, test reports, etc.) back to the model, allowing it to iterate and correct based on these concrete facts.

If self-reflection is "I think I did it right," then external feedback is "facts prove whether I did it right."

Returning to our Jupyter Notebook course polishing scenario. Suppose the course contains some code examples, and we want to ensure that the code still runs correctly while polishing the text.

This requires combining **tool use** (learned in the previous chapter) with reflection mechanisms. Here, the most direct source of external feedback is a code execution tool. AgentScope has a powerful `execute_python_code` tool built-in, which provides a secure code interpreter environment for the Agent, allowing it to truly execute Python code and retrieve results or error messages.

The specific workflow is as follows:

1. **Generate**: The writing Agent polishes the document and outputs the notebook content containing the code.
2. **Interact with external tools**: The system automatically extracts code blocks and calls the `execute_python_code` tool to attempt execution.
3. **Obtain external feedback**: The tool returns the execution result, let's say an error: `TypeError: get_user_data() got an unexpected keyword argument 'usr_id'`.
4. **Correct**: The Agent receives this error feedback. It now clearly knows what went wrong with the code. Based on this feedback, it generates corrected code.

*Figure (translated): self-correction loop driven by external code-execution feedback.*

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

Below is a simple example implemented using AgentScope. The `execute_python_code` tool built into AgentScope does not require manually creating tool functions; you just need to register it via `toolkit.register_tool_function(execute_python_code)`.

```python
"""
Using AgentScope to implement an external feedback reflection mechanism (simplified)
Scenario: Polishing Jupyter Notebook courses, verifying code correctness via a code interpreter
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
# Create writing Agent (equipped with code interpreter tool)
# ============================================================
# from agentscope.model import OpenAIChatModel
def create_writer_agent() -> ReActAgent:
    """Creates a writing Agent responsible for polishing course content"""

    # Create a toolkit and register the built-in code execution tool
    toolkit = Toolkit()
    toolkit.register_tool_function(execute_python_code)

    writer = ReActAgent(
        name="Writer",
        sys_prompt=dedent("""You are a technical course writer, responsible for polishing Jupyter Notebook courses.
            Task requirements:
            1. Optimize text expression to make it smoother and more vivid
            2. **Absolutely do not modify variable names, function names, or parameter names in the code**
            3. After polishing, use the execute_python_code tool to verify all code blocks
            4. If code execution fails, check if you accidentally modified the code and correct it

            Remember: only change text, not code logic!
        """),
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
            # os.getenv("DASHSCOPE_API_BASE"),
            stream=False,
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
        max_iters=10,  # Max iterations (example configuration, should be adjusted based on task complexity and cost budget)
    )

    return writer

# ============================================================
# Main process
# ============================================================

async def main():
    """Main function - demonstrates the external feedback reflection mechanism"""

    # Original course content (contains "non-standard" variable name usr_id)
    original_notebook = """ # Python function example course

  This section teaches how to define and call functions.

  ## Defining functions

  def get_user_data(usr_id: str):
      return f"Data for {usr_id}"

  ## Calling functions

  print(get_user_data(usr_id="u-123"))

  ## Summary

  You have learned to define and call Python functions.
  """

    print("="*60)
    print("Original course content:")
    print("="*60)
    print(original_notebook)

    # Create Agent
    writer = create_writer_agent()

    # Send polishing request
    user_msg = Msg(
        name="user",
        content=dedent(f"""Please polish the following course content, requirements:
            {original_notebook}
            1. Make the text more vivid and easy to understand
            2. **Do not modify variable names or function names in the code**
            3. After polishing, use execute_python_code to verify if the code can run
            4. If an error occurs, it means you might have modified the code incorrectly, please correct it
        """),
        role="user"
    )

    print("\n" + "="*60)
    print("Agent starts working...")
    print("="*60)

    # Agent automatically performs: Polish -> Validate -> Correct -> Re-validate
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

Through this method, the Agent can use external tools to verify output results, thereby achieving efficient and precise self-correction.

##### 2.3.2.2 Other validation methods

In addition to code execution, this pattern can be applied to other scenarios requiring objective facts:

*   **Scenario: Optimizing Matplotlib charts in research papers**
    *   **Problem**: You ask the Agent to generate data visualization code for a research paper. The Agent generates a Matplotlib code that "looks reasonable," containing correct data processing logic and plotting function calls. However, code that runs does not mean the chart looks good—the actual rendered chart might have overlapping axis labels, legends obscuring data points, fonts too small to read, color schemes unsuitable for printing, etc.
    *   **External feedback solution**: The system calls a **code interpreter** tool to execute the Matplotlib code and returns the generated image file. The **Agent receives the actual rendered chart through visual input**, allowing it to intuitively identify visual problems (e.g., "x-axis labels overlap," "legend blocks critical data points") and then specifically adjust code parameters (e.g., `plt.xticks(rotation=45)` to rotate labels, `bbox_to_anchor` to adjust legend position, increase `fontsize`). This "generate-render-adjust" loop ensures the final chart meets academic publication quality requirements.

*   **Scenario: Checking answers for complex calculation problems**
    *   **Problem**: In a quantum mechanics lesson, you need to create a practice problem: "What is the ground state energy in joules for an electron (`mass ≈ 9.11e-31 kg`) confined in a one-dimensional infinite potential well of length 1 nanometer (1e-9 m)? (Planck's constant `h ≈ 6.626e-34 J·s`)". The Agent might make errors during the solution steps due to complex exponential calculations.
    *   **External feedback solution**: The system identifies the expression needing calculation `(1**2 * (6.626e-34)**2) / (8 * 9.11e-31 * (1e-9)**2)` and hands it to a **code interpreter** or **calculator** tool for execution. The tool returns the precise numerical result. This objective calculation result is provided as feedback, allowing the Agent to correct its final answer.

*   **Scenario: Structured output validation**
    *   **Problem**: You ask the Agent to generate a configuration file conforming to a specific JSON Schema, but it might omit required fields or use incorrect data types.
    *   **External feedback solution**: The system uses libraries like Pydantic to validate the generated JSON. When the output does not conform to the Schema, the validator returns a detailed error report (e.g., "field 'timeout' should be an integer, not a string"). This objective, precise feedback allows the Agent to correct its output until it fully conforms to the predefined structure. This "generate-validate-feedback" loop is the most common and fundamental application of reflection mechanisms in practice.

Finally, how do you choose between these two feedback modes? This depends on your specific needs, budget, and acceptable error rate. For example, if you are just polishing a blog post without code, reflection might not be needed at all. But if you are modifying an interactive course with dozens of code examples, then introducing an "external feedback" loop based on a code interpreter is a necessary investment to ensure document quality and avoid publishing accidents.

### 2.4 Summary

Let's review what you've learned in this section:
- **Limitations of direct instructions**: Directly asking the LLM in the Prompt to "be more careful" or "do not modify code" usually has poor results, because the model aims to generate "more reasonable" text and sometimes "means well but does harm."
- **Core idea of "reflection"**: Mimicking human "metacognition," giving the model an opportunity to review and evaluate its own complete generated content, thereby finding and correcting errors. This is more reliable than simple instructions.
- **Self-reflection vs. external feedback**: "Self-reflection" is having another Agent check the draft, suitable for subjective evaluation; "external feedback" is using tools (like a code interpreter) to verify results, suitable for scenarios requiring objective facts.
- **Engineering implementation: "Generate-feedback" loop**: An effective way to implement "reflection" is to use multiple calls: the first generates a draft, and subsequent calls are responsible for evaluating the draft, providing feedback, and making modifications based on that feedback.

## 3 Building workflows

### 3.1 Single agent handling complex processes

On Monday morning, you received this message:

> "The 'Introduction to Python Data Analysis' course submitted last Friday needs to be launched as soon as possible. Can you run it through our standard review process with your AI assistant? That means: 1) all code examples must run; 2) technical concepts must be sound; 3) the difficulty gradient should suit beginners; 4) the language style must conform to our guidelines. I need the results by 3 PM."

You thought, this task is quite simple. Your bot can already validate code, so handling this "composite task" shouldn't be difficult. So you crammed all the requirements into one prompt:

```plaintext
prompt = """Please complete the following course review tasks:
1. Verify that all Python code runs correctly.
2. Check the accuracy of technical concepts (especially the usage of pandas and numpy).
3. Evaluate whether the difficulty curve is suitable for programming novices.
4. Adjust the wording according to our style guide (avoid colloquialisms like "very simple" or "super").
Please provide a complete review report."""
response = agent.run(prompt + course_content)
```

A few minutes later, you opened the returned result:

* The Agent indeed validated the code, but when "optimizing the language," it changed `super()` in the code to `parent()`, because it felt "super" was too colloquial.
* It found an error in the explanation of DataFrame in Chapter 3, and after correcting it, introduced a more serious error: stating that "DataFrame is a built-in Python data structure."
* As for difficulty assessment? It seemed to have forgotten about it when it reached the 50th issue.

You tried to make it start over. This time it remembered to assess the difficulty but missed half of the code validation. The third time, it did all the tasks but "corrected" some originally correct concepts into errors.

The problem is obvious: asking a single Agent to manage multiple complex tasks simultaneously is like asking an intern to answer four phones at once—something is bound to go wrong.

### 3.2 Analysis of failure causes
#### 3.2.1 Forgetting effect of attention mechanisms

When LLMs generate responses, their "attention" to information at different positions is uneven. When the Agent processes the fourth task (polishing language), the details of the first task (code validation) have been diluted by a large amount of intermediate information.

Specifically, the model "forgets" the constraints validated earlier when making later modifications. For example, even if you have confirmed that `super()` is correct Python syntax, during the language polishing phase, the model might replace it because the word "super" seems colloquial, leading to code errors.

This is not simply "poor memory," but an inherent limitation of the self-attention mechanism in the Transformer architecture—the attention weights between tokens are diluted as the sequence length increases.

#### 3.2.2 Cascading error amplification

When executing multiple tasks sequentially, early errors become the "factual basis" for subsequent processing. Suppose the Agent incorrectly "corrected" the definition of DataFrame during the fact-checking phase (e.g., claiming it's built-in Python). This error would then enter the subsequent context.
What's worse, the model would continue reasoning based on this erroneous "fact":

- Since DataFrame is "built-in," there's no need to import pandas.
- Import statements would be removed from teaching examples.
- All code examples would become invalid.

This error propagation is not linear, but exponential—a small error can trigger a cascade of incorrect decisions.

#### 3.2.3 Flattened understanding vs. structured requirements

Your complex requirement is actually a task graph with an internal structure:
- Some tasks can be performed in parallel (code checking and style checking don't interfere with each other).
- Some tasks have dependencies (conceptual understanding must precede difficulty assessment).
- Some tasks require a global perspective (evaluating the overall difficulty curve).

But for the model, your prompt is just a flat sequence of tokens. It cannot automatically recognize these structural relationships and instead attempts to solve an inherently graph-structured problem with a linear generation process.

It's like asking someone to play four games with different rules simultaneously, without telling them which can be played in turns and which must be played concurrently.

Ultimately, relying on a single Agent to perform complex reviews is like building a house without blueprints; every brick laid might affect the structural stability of the entire building.

### 3.3 Several workflow patterns

Since having one Agent handle everything doesn't work, you naturally think of another approach: just as you break a project into subtasks and assign them to different people or complete them at different times when managing a project. This "Divide and Conquer" approach is central to solving such problems.

We call this pattern of breaking down complex tasks into multiple nodes and defining their execution relationships a **workflow**.

The key to building workflows is understanding the business and making the most appropriate task breakdown. Below, we will start with the simplest pattern and gradually build powerful workflows capable of handling complex course reviews.

#### 3.3.1 Pattern one: Pipeline

This is the most basic and intuitive workflow. It breaks a task into several fixed, sequentially executed steps. The output of the previous step serves strictly as the input for the next step. The entire process resembles a factory assembly line: unidirectional and immutable. The RAG Q&A bot you built earlier in this course is a perfect example of this pattern.

*Figure (translated): the pipeline pattern — one-directional and immutable.*

```text
[Course draft] -> [Code extractor] -> [Code validator] -> [Report generator] -> [Final report]
```

```python
""" Pattern one: Pipeline - Scenario: Course quick check process
Goal: User submits a course draft, the system sequentially completes 1) Extract code from course -> 2) Validate code executability -> 3) Generate code review report """
import asyncio
from agentscope.message import Msg
from agentscope.pipeline import sequential_pipeline
from chatbot.agent import create_agent, disable_console_output

async def run_pipeline() -> None:
    # Node A: Code Extraction Agent
    # multi_agent=True is a configuration in AgentScope, used to ensure communication format compatibility between Agents,
    # and is a recommended setting for building workflows and multi-agent systems.
    code_extractor = create_agent(
        name="Code Extractor",
        sys_prompt=(
            "You are a code extraction expert. Please accurately extract all Python code blocks from the user-provided course text."
            "Only output the code, without any other explanations."
        ),
        model_name="qwen-flash",
        multi_agent=True,
    )

    # Node B: Code Validation Agent (can call external tools)
    code_validator = create_agent(
        name="Code Validator",
        sys_prompt=(
            "You are a code execution and validation expert. You will receive code text. Please use a code interpreter to execute it."
            "Report whether the code runs successfully, and if not, point out the error."
        ),
        # Here you can configure code_validator to use the code interpreter tool you learned in section two
        model_name="qwen-plus",
        multi_agent=True,
    )

    # Node C: Report Generation Agent
    report_generator = create_agent(
        name="Report Generator",
        sys_prompt=(
            "You are a review report writing assistant. Generate a concise and clear inspection report for the course designer based on the code validation results from the previous step."
        ),
        model_name="qwen-max",
        multi_agent=True,
    )

    agents = [code_extractor, code_validator, report_generator]
    disable_console_output(agents)

    course_draft = (
        "This is our new course. The first part is `print('Hello, World!')`."
        "The second part is a problematic code `x = 1 / 0`."
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

Its core advantage lies in its **simplicity, predictability, and ease of debugging**. Because the process is fixed, when a problem occurs, you can easily pinpoint which stage (extraction, validation, or reporting) caused the issue. This determinism is crucial in many enterprise applications.

It is suitable for tasks with very fixed business processes and single logic. For example:

* **Initial code check**: First extract the code, then run the validation.
* **Document translation**: First extract the text, then translate, and finally format the output.
* **New employee onboarding material distribution**: First generate a welcome email, then attach company documents, and finally send them.

The rigidity of the pipeline is its greatest strength and also its most fatal weakness. It cannot handle any changes outside the defined process. Faced with a request like "help me evaluate the fun factor of this course," this pipeline designed for "code checking" will be completely at a loss, because it lacks the ability to handle such intent. It assumes all inputs should follow the same processing logic.

#### 3.3.2 Pattern two: Branching

To overcome the rigidity of pipelines, you need to introduce decision-making capabilities. The core of the branching pattern is to set up a "router" or "dispatch center" at the beginning or at key nodes of the workflow. This decision node analyzes the input (e.g., user review requirements) and then, like a traffic policeman, directs the task to different, predefined processing paths (i.e., different pipelines or experts).

*Figure (translated): the router pattern — a distributor directs the task to the right expert path.*

```text
                             ┌──► [Code quick-check expert] ──────┐
[Review request] -> {Task distributor / router}                  ├──► [Chief reviewer] -> [Output result]
                             └──► [Language polishing expert] ────┘
```

```python
""" Pattern two: Branching - Scenario: Course review task distribution
Routing Agent reads review request, selects one of the following branches:
1) code_check: Quick code check only
2) style_guide: Polish language according to style guide
3) full_review: Perform a comprehensive multi-dimensional review """
import asyncio
from typing import Literal
from pydantic import BaseModel, Field
from agentscope.message import Msg
from chatbot.agent import create_agent, disable_console_output

class RouteChoice(BaseModel):
    choice: Literal["code_check", "style_guide", "full_review", None] = Field(
        description="Select branch based on user intent: code_check/style_guide/full_review/None"
    )
    extra: str | None = Field(default=None, description="Brief description of the task")

async def branch_code_check(user_msg: Msg) -> Msg:
    agent = create_agent(
        name="Code Quick Check Expert",
        sys_prompt="You are a code quick check expert. Based on user requirements, quickly verify if code snippets in the course can run.",
        model_name="qwen-plus",
        multi_agent=True,
    )
    disable_console_output([agent])
    return await agent(user_msg)

async def branch_style_guide(user_msg: Msg) -> Msg:
    agent = create_agent(
        name="Language Polishing Expert",
        sys_prompt="You are a language polishing expert. Please rewrite and polish the user-provided course text according to the company style guide.",
        model_name="qwen-max",
        multi_agent=True,
    )
    disable_console_output([agent])
    return await agent(user_msg)

async def branch_full_review(user_msg: Msg) -> Msg:
    agent = create_agent(
        name="Chief Reviewer",
        sys_prompt="You are the chief reviewer. Inform the user that you will initiate a comprehensive review process including code, facts, and pedagogy.",
        model_name="qwen-flash", # Use a lightweight model to simulate the notification action for starting the process
        multi_agent=True,
    )
    disable_console_output([agent])
    return await agent(user_msg)

async def run_branching() -> None:
    router = create_agent(
        name="Review Task Dispatcher",
        sys_prompt=(
            "You are a course review task dispatcher. Select a branch based on user input:\n"
            "- If only checking code, output code_check\n"
            "- If polishing text, output style_guide\n"
            "- If a complete, comprehensive review is needed, output full_review\n"
            "Only express your choice through structured output, do not provide a main body response."
        ),
        model_name="qwen-plus",
        multi_agent=False,
    )

    user_text = "This course is almost done, please give it a comprehensive check, especially the code and difficulty."

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
        # Default to full review to ensure the example runs
        out = await branch_full_review(Msg("user", user_text, "user"))

    print("=" * 50)
    print(f"Branch choice: {choice}")
    print(out.content)
    print("=" * 50)

async def main() -> None:
    await run_branching()

await main()
```

Compared to a single pipeline, branching makes the system more flexible and intelligent. It enables an application to handle multiple types of tasks, greatly expanding its applicability and improving the user experience.

Common application scenarios include:

* **Intelligent customer service**: Routes based on user query type (course content inquiry, platform technical support, purchase advice) to different processing flows.
* **Multi-tool Agent**: The Agent decides whether to call a code interpreter, search engine, or internal knowledge base based on task requirements.
* **Content processing system**: Calls different review processes based on content type (video, text, interactive Notebook).

Branching is essentially "one of many choices," and it is still sequential. It can handle "code checking" or "language polishing," but it cannot handle composite requests like "checking code while polishing language." For our initial complex request involving four review dimensions, it can only follow one branch at a time, requiring multiple independent conversations between the user and the bot, which is very inefficient.

#### 3.3.3 Pattern three: Parallel execution

When a request can be broken down into multiple independent subtasks, queuing them up is a huge waste. The core idea of the parallel execution pattern is "doing things simultaneously." It first breaks a complex task into multiple subtasks, then distributes these subtasks to different execution units (Agents or tools) for concurrent processing, and finally gathers all results to form the final output.

*Figure (translated): parallel execution — several experts review concurrently, then a chief editor merges.*

```text
                 ┌─► [Code reviewer] ─────────┐
                 ├─► [Fact checker] ──────────┤
[Course content] ┼─► [Pedagogy evaluator] ────┼─► [Chief editor: summary] ──► [Comprehensive report]
                 └─► [Style editor] ──────────┘
```

```python
""" Pattern three: Parallel Execution - Scenario: Comprehensive course review
Executes independent review subtasks in parallel: code check, fact verification, pedagogy evaluation, language style check.
Example uses fanout_pipeline to collect reports in parallel, then a summarizer Agent consolidates them. """
import asyncio
from typing import List
from agentscope.message import Msg
from agentscope.pipeline import fanout_pipeline
from chatbot.agent import create_agent, disable_console_output

async def run_parallel() -> None:
    # Four independent subtask "expert" Agents
    code_checker = create_agent(
        name="Code Checker",
        sys_prompt="Verify that the code in the course is correct and provide suggestions for fixing it.",
        model_name="qwen-plus",
        multi_agent=True,
    )
    fact_checker = create_agent(
        name="Fact Checker",
        sys_prompt="Verify the accuracy of technical concepts, function explanations, and citation norms in the course.",
        model_name="qwen-plus",
        multi_agent=True,
    )
    pedagogy_evaluator = create_agent(
        name="Pedagogy Evaluator",
        sys_prompt="Evaluate the course's difficulty curve, case appeal, and exercise effectiveness.",
        model_name="qwen-flash",
        multi_agent=True,
    )
    style_editor = create_agent(
        name="Style Editor",
        sys_prompt="Check and report on language style and terminology consistency issues according to company style guidelines.",
        model_name="qwen-flash",
        multi_agent=True,
    )

    experts = [code_checker, fact_checker, pedagogy_evaluator, style_editor]
    disable_console_output(experts)

    course_content = "This is our newly developed introductory Python data analysis course..."
    msgs = await fanout_pipeline(
        agents=experts,
        msg=Msg("user", course_content, "user"),
        enable_gather=True,
    )

    # Summarizer Agent
    summarizer = create_agent(
        name="Chief Editor",
        sys_prompt="Consolidate review comments from multiple experts into a clear, well-structured comprehensive review report.",
        model_name="qwen-max",
        multi_agent=True,
    )
    disable_console_output([summarizer])

    merged_text: List[str] = [m.content for m in msgs]
    prompt = "\n\n".join(merged_text)
    summary = await summarizer(Msg("user", prompt, "user"))

    print("=" * 50)
    print("Parallel execution output:")
    print(summary.content)
    print("=" * 50)

async def main() -> None:
    await run_parallel()

await main()
```

The most significant advantage is a substantial increase in efficiency. The total time taken for the workflow is no longer the sum of all subtask times, but depends on the longest subtask. This allows the Agent to quickly respond to complex requests involving multiple steps.

Common application scenarios include:

* Handling complex review requests: Such as our course review scenario, simultaneously addressing multiple dimensions like code, facts, pedagogy, and style.
* Generating comprehensive reports: Simultaneously pulling information from different data sources (user feedback, market trends, competitor analysis) and analyzing them separately, finally consolidating into a new course project proposal report.
* Batch data processing: Performing the same formatting or checking operations on multiple course units concurrently.

The prerequisite for this pattern is that subtasks are mutually independent. If tasks have dependencies (e.g., the core knowledge points of a course must be confirmed before evaluating the relevance of its cases), simple parallelization is not possible. Moreover, it assumes that each execution unit can provide a "correct" answer, making it unsuitable for creative or decision-making tasks that require comparison and trade-offs between multiple parties to arrive at the best solution.

#### 3.3.4 Pattern four: Mixture-of-Agents (MoA)

Unlike parallel execution, which aims to improve efficiency, the core objective of the Mixture-of-Agents pattern is to **pursue extreme quality, robustness, and creativity**. The core concept of MoA is based on a key discovery: **different LLMs have their own unique strengths and specialties, and when one model can refer to the outputs of other models, it often generates higher quality responses—this phenomenon is called "collaborativeness" of models**. The MoA approach involves having multiple **different LLMs** process the **same task** simultaneously, then an aggregation model synthesizes, analyzes, and merges all outputs to produce a final result that far surpasses the capabilities of any single model.

*Figure (translated): LLM debate — multiple analysts work on the same task, then an aggregator picks the best solution.*

```text
                 ┌─► [Analyst 1: Qwen3-Max] ─────────┐
[Same task] ─────┼─► [Analyst 2: DeepSeek-V3.2] ─────┼─► [Aggregator: Qwen3-Max] ──► [Best solution]
                 └─► [Analyst 3: Kimi-K2-Thinking] ──┘
```

```python
""" Pattern four: Mixture-of-Agents (MoA) - Scenario: Course core selling point extraction
Uses three different LLMs to process the same task in parallel, and an aggregator model fuses their outputs,
leveraging the collaborativeness between models to produce higher quality results. """
import asyncio
from agentscope.message import Msg
from agentscope.pipeline import fanout_pipeline
from chatbot.agent import create_agent, disable_console_output

async def run_moa() -> None:
    # Use three different models as Proposers
    # Each model has its unique strengths but processes the same task
    proposer1 = create_agent(
        name="Qwen3-Max",
        sys_prompt="You are a professional course analyst. Please extract the core selling points and promotional copy for the given course.",
        model_name="qwen3-max",
        multi_agent=True,
    )
    proposer2 = create_agent(
        name="Qwen3-Flash",
        sys_prompt="You are a professional course analyst. Please extract the core selling points and promotional copy for the given course.",
        model_name="qwen-flash",
        multi_agent=True,
    )
    proposer3 = create_agent(
        name="Qwen3-Plus",
        sys_prompt="You are a professional course analyst. Please extract the core selling points and promotional copy for the given course.",
        model_name="qwen-plus",
        multi_agent=True,
    )

    proposers = [proposer1, proposer2, proposer3]
    disable_console_output(proposers)

    task = (
        "This is a new course on 'LLM Applications for Web Developers'. Please extract its core selling points and promotional copy."
    )
    msgs = await fanout_pipeline(
        agents=proposers,
        msg=Msg("user", task, "user"),
        enable_gather=True,
    )

    # The Aggregator receives outputs from all models and synthesizes the best result
    aggregator = create_agent(
        name="Aggregator",
        sys_prompt=(
            "Your task is to synthesize the answers from multiple LLMs to the same question."
            "These answers come from different models, each with its strengths and weaknesses. Please critically evaluate these answers,"
            "identify their pros and cons, and then merge this information to generate a high-quality, accurate, and comprehensive final answer."
            "Ensure your answer is clearly structured, logically coherent, and meets the highest standards of accuracy and reliability."
        ),
        model_name="qwen3-max",
        multi_agent=True,
    )
    disable_console_output([aggregator])

    # Merge all proposers' outputs and pass to the aggregator
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

**How MoA works**:

MoA divides participating models into two types of roles:

1. **Proposers**: Multiple different models process the same task in parallel, each generating responses. These models may excel in certain aspects (e.g., logical reasoning, creative expression, factual accuracy).
2. **Aggregator**: Receives the output from all proposers, and through critical evaluation, comparison, and merging, generates a higher-quality final response.

Crucially, the aggregator does not simply choose the best answer; rather, it extracts the strengths from multiple responses to synthesize a result that surpasses any single model.

**Advantages of MoA**:

* **Leverages model diversity**: Different models have different training data, architectures, and optimization goals, leading to varied performance across tasks. MoA can leverage the strengths of multiple models simultaneously.
* **Enhanced robustness**: Even if a particular model performs poorly on certain inputs, the high-quality outputs from other models ensure a minimum level of quality for the final result.
* **Emergent quality**: Research shows that even if the individual output quality of proposer models is low, the aggregated result can still surpass any single model—this is a direct manifestation of "model collaborativeness."

MOA is suitable for **open-ended or creative tasks** that have no single standard answer, require extremely high-quality results, and are of significant value.

* **Core copy writing**: Such as course slogans, promotional texts, brand stories.
* **Complex decision analysis**: Synthesizing analysis reports from different models to form more comprehensive recommendations for new course directions.
* **Code generation and optimization**: Allowing different models to generate example code, then having a review Agent select the best or perform integrated restructuring to achieve optimal teaching effects.

However, the primary constraint of MOA is **cost**. Calling N expert Agents incurs N times the computational cost and corresponding latency. This is a strategy that exchanges resources for quality, and therefore must be used for critical tasks where "the steel is used on the blade," not for routine, cost-sensitive daily tasks.

**Advanced: Multi-layer MoA**

The MoA demonstrated above is a "2-layer structure": the first layer has multiple experts processing tasks in parallel, and the second layer consists of an aggregator synthesizing the outputs of all experts. However, MoA can also be **extended to 3 or more layers**, continuously refining and optimizing results through multiple iterations to achieve even more outstanding output quality than a single-layer MoA.

**The core idea of multi-layer MoA** is to take the aggregated output of the previous layer as input for the next layer, which is then reviewed, critiqued, and improved by multiple experts, followed by a new aggregator performing a higher level of synthesis. This "iterative refinement" process is similar to multiple rounds of review and polishing in human teams; each round can uncover issues missed in previous rounds and stimulate new ideas, ultimately achieving a quality level that would be difficult to reach in a single round.

**Advantages of multi-layer MoA**:

*   **Further quality improvement**: Experts in the second and third layers can build upon the results of the first layer, performing deeper analysis and optimization, much like an editorial team polishes a draft multiple times.
*   **Enhanced error correction capability**: Even if some experts in the first layer make mistakes, experts in subsequent layers have the opportunity to discover and correct these errors, making the final result more reliable.
*   **Emergence of creativity**：Multi-layered interaction may produce a "1+1>2" effect, where the collision of ideas among experts at different levels can spark innovative solutions that no single layer could generate on its own.

**Key implementation points**:

*Figure (translated): three-layer debate — analysts generate, reviewers critique, the aggregator merges.*

```text
Layer 1 (analysts):                            Layer 2 (reviewers):                        Layer 3:
[Analyst 1: Qwen3-Max] ──────► [Reviewer 1: Qwen3-Max] ─────────┐
[Analyst 2: DeepSeek-V3.2] ──► [Reviewer 2: DeepSeek-V3.2] ─────┼─► [Aggregator: Qwen3-Max] ──► [Best solution]
[Analyst 3: Kimi-K2-Thinking] ► [Reviewer 3: Kimi-K2-Thinking] ─┘
        ▲
   [Same task]
```

```python
async def run_multi_layer_moa() -> None:
    """
    Multi-layer MoA example: 3-layer architecture for refining course marketing plans
    Layer 1: 3 different models act as proposers to generate plans in parallel
    Layer 2: 3 different models optimize and improve the aggregated output from Layer 1
    Layer 3: The final aggregator synthesizes all information to output the best plan
    """
    # General aggregation prompt
    aggregate_prompt = (
        "Your task is to synthesize the answers from multiple LLMs to the same question."
        "Please critically evaluate these answers, identify their pros and cons,"
        "then merge this information to generate a high-quality, accurate, and comprehensive final answer."
    )

    # Layer 1: Initial proposer layer (3 different models)
    layer1_proposers = [
        create_agent(
            name="Proposer-L1-1",
            sys_prompt="You are a professional course analyst. Please extract the core selling points and promotional copy for the given course.",
            model_name="qwen3-max",
            multi_agent=True
        ),
        create_agent(
            name="Proposer-L1-2",
            sys_prompt="You are a professional course analyst. Please extract the core selling points and promotional copy for the given course.",
            model_name="qwen-plus",
            multi_agent=True
        ),
        create_agent(
            name="Proposer-L1-3",
            sys_prompt="You are a professional course analyst. Please extract the core selling points and promotional copy for the given course.",
            model_name="qwen-flash",
            multi_agent=True
        ),
    ]

    task = "This is a new course on 'LLM Applications for Web Developers'. Please extract its core selling points and promotional copy."
    layer1_outputs = await fanout_pipeline(
        agents=layer1_proposers,
        msg=Msg("user", task, "user"),
        enable_gather=True,
    )

    # Layer 1 Aggregator
    layer1_aggregator = create_agent(
        name="Aggregator-L1",
        sys_prompt=aggregate_prompt,
        model_name="qwen3-max",
        multi_agent=True,
    )
    layer1_merged = "\n\n".join([f"Model {i+1}:\n{m.content}" for i, m in enumerate(layer1_outputs)])
    layer1_result = await layer1_aggregator(Msg("user", layer1_merged, "user"))

    # Layer 2: Second round proposer layer (3 different models, optimizing based on aggregated result from Layer 1)
    layer2_proposers = [
        create_agent(
            name="Proposer-L2-1",
            sys_prompt="You are a professional course analyst. Please review the given marketing plan and suggest improvements or optimized versions.",
            model_name="qwen3-max",
            multi_agent=True
        ),
        create_agent(
            name="Proposer-L2-2",
            sys_prompt="You are a professional course analyst. Please review the given marketing plan and suggest improvements or optimized versions.",
            model_name="qwen-plus",
            multi_agent=True
        ),
        create_agent(
            name="Proposer-L2-3",
            sys_prompt="You are a professional course analyst. Please review the given marketing plan and suggest improvements or optimized versions.",
            model_name="qwen-flash",
            multi_agent=True
        ),
    ]

    layer2_prompt = f"Here is the marketing plan generated from the first round of analysis:\n\n{layer1_result.content}\n\nBased on this, please provide suggestions for improvement or optimized versions."
    layer2_outputs = await fanout_pipeline(
        agents=layer2_proposers,
        msg=Msg("user", layer2_prompt, "user"),
        enable_gather=True,
    )

    # Layer 3: Final aggregation layer
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

**When to use multi-layer MoA:**

*   **Extremely high-value tasks**: Such as annual company strategic reports, important product launch texts, core curriculum system design. The success or failure of these tasks can directly impact business results, making them worth investing more resources.
*   **Extremely high creative requirements**: Such as brand story creation, innovative teaching method design, scenarios that require multiple rounds of idea generation to spark the best creativity.
*   **Extremely high fault tolerance requirements**: Such as legal documents, technical white papers, where any error could lead to severe consequences, requiring multi-layer review to ensure accuracy.

**Cost trade-offs**：

The cost of multi-layer MoA increases linearly with the number of layers. Taking the 3-layer architecture above as an example: 3 proposer models + 1 aggregator per layer means at least (3+1) + (3+1) + 1 = 9 model calls, which is more than double the cost of a single layer's 3+1=4 calls. Therefore, multi-layer MoA should only be considered when the value of the task significantly outweighs the cost, and not for routine, cost-sensitive daily tasks.

You can balance cost and quality with the following strategies:
*   **Reduce the number of proposers**: Use 3-4 different models in the first layer for diversity, and then reduce to 2-3 models for refinement in subsequent layers.
*   **Reduce the number of layers**: For most tasks, 2-layer MoA (proposer layer + aggregation layer) can already provide significant quality improvement. 3 or more layers are usually only worth using for extremely high-value tasks.
*   **Hybrid model configuration**: Mix models of different performance and costs among the proposers, and use the highest quality model for the aggregator to ensure the final output quality.

> **Further reading: Cost optimization and resource management for workflows**
>
> You've already realized that advanced patterns like Mixture-of-Agents (MoA) can significantly increase costs. This raises a crucial question that must be addressed before any workflow is put into production: how to manage resources and optimize costs? Fortunately, you can significantly reduce the operational costs of workflows without sacrificing too much quality by implementing a series of sophisticated engineering strategies.
>
> *   **Differentiated model allocation**: Different nodes in a workflow can vary greatly in task complexity and importance. You can assign lightweight, inexpensive models to simple tasks (e.g., intent recognition, format conversion) and reserve expensive, advanced models only for the most critical core tasks (e.g., final decision-making, content generation). Research shows that with reasonable optimization strategies, companies can save 40-70% of token costs depending on the specific implementation.
> *   **Systematic caching**: By carefully observing your workflow, you will find that many node computations are repeatable. For example, retrieving the same company style guide, parsing the same course review request, etc. By adding caching mechanisms to these nodes, you can store intermediate results. When the same input is encountered next time, the system can directly return the cached result, completely bypassing model calls, thereby greatly reducing costs and latency.
> *   **Smart batching**: Not all tasks require an immediate response. For non-real-time tasks like course quality report generation or user feedback analysis, you can design workflows to intelligently aggregate a batch of similar requests, then process them in a "batch" with a single model call, instead of calling the model separately for each request. This finds a better balance between cost and response time.

#### 3.3.5 Pattern five: Human-in-the-loop (HITL)

So far, all the workflows you've designed are fully automated. However, in the real world, fully entrusting all decision-making power to AI carries risks, especially when dealing with ambiguous teaching concepts or high-value course content. The Human-in-the-Loop pattern no longer pursues complete automation; instead, it intentionally designs one or more "pause points" in the workflow, handing control back to humans for decision-making, approval, or quality control, before returning the task to the workflow to continue execution. This is a critical pattern for building trustworthy and secure AI systems.

*Figure (translated): human-in-the-loop — a human expert reviews and decides when the agent is uncertain.*

```text
[Course content] -> [AI analyst: provides suggestions] -> [AI rewriter: executes modifications] -> {Human expert review}
       ^                                                                                               |
       └──────────────────────────── (when uncertain, send back) ◄──────────────────────────────────────┘
                                                                                                       │ (approved)
                                                                                                       v
                                                                                                [Final version]
```

```python
""" Pattern five: Human-in-the-Loop (HITL) - Scenario: Course difficult point review (Human as a Tool)
AI first provides modification suggestions for a potentially difficult point in the course; then a rewriter Agent equipped with a "human consultation" tool autonomously decides when to call this tool to consult a human, and finally completes the modification. """
import asyncio
import os
from agentscope.agent import ReActAgent, UserAgent
from agentscope.message import Msg, TextBlock
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.tool import Toolkit, ToolResponse
from chatbot.agent import create_agent, disable_console_output

# Encapsulate human intervention as a tool: ask_human_decision
async def ask_human_decision(question: str) -> ToolResponse:
    """Asks a human expert for a decision or opinion.

    Args:
        question (str): The specific question to ask the human for confirmation or supplementation.
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
    # AI: provides modification suggestions
    suggester = create_agent(
        name="Difficult Point Analyst",
        sys_prompt=(
            "You are a senior teaching designer. Please identify the concept in the course that might be most difficult for beginners to understand,"
            "and provide a more accessible explanation as a modification suggestion."
        ),
        model_name="qwen-plus",
        multi_agent=True,
    )
    disable_console_output([suggester])

    course_content = "In Python, a decorator is essentially a function that takes a function as an argument and returns a new function..."
    suggestion = await suggester(Msg("user", course_content, "user"))

    print("AI suggestion is as follows:\n")
    print(suggestion.content)

    # Hand the "human intervention" as a tool to the rewriter Agent, which autonomously decides whether to call it
    toolkit = Toolkit()
    toolkit.register_tool_function(ask_human_decision)

    rewriter = ReActAgent(
        name="Content Rewriter",
        sys_prompt=(
            "You are a course content rewriter. Complete the final modification based on the AI suggestion provided.\n"
            "- If you are confident, please complete the modification directly and provide confirmation;\n"
            "- If there is uncertainty, ambiguity, or high risk, please call the ask_human_decision tool to consult a human expert first,"
            "then complete the modification based on their input;\n"
            "- Briefly explain in the final result whether a human was consulted and why."
        ),
        model=DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
            
            stream=False,
        ),
        formatter=DashScopeMultiAgentFormatter(),
        toolkit=toolkit,
    )
    disable_console_output([rewriter])

    # Provide course content and AI suggestion together to the rewriter Agent
    task = (
        "Below is a course excerpt and AI's modification suggestion. Complete the final modification based on the system prompt:\n\n"
        f"[Course Content]\n{course_content}\n\n"
        f"[AI Suggestion]\n{suggestion.get_text_content()}\n"
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

The advantage of human intervention in workflows is:

*   **Improved accuracy**: By introducing human common sense and domain knowledge to handle teaching ambiguities that AI finds difficult to judge (e.g., whether a metaphor is appropriate), ensuring the correctness of the final content.
*   **Enhanced security**: For high-risk operations such as directly publishing courses or modifying core codebases, human final approval is the last line of defense against AI misoperations leading to serious consequences.
*   **Building trust**: Allowing course designers to participate in the AI's review and modification process gives them a stronger sense of control and trust in the system's behavior.

Common application scenarios include:

*   **Handling ambiguous requirements**: When requirements are unclear (such as making a course "more interesting"), AI provides multiple instructional design proposals for humans to choose from.
*   **Approval of high-value operations**: Before executing any actions related to course content publication or deletion of old versions, approval from the course leader is mandatory.
*   **Quality review of critical outputs**: After a "mixed expert" model generates an important initial draft of a course outline, the final step in the workflow should be sending it for review by the instructional director, instead of directly proceeding to development.

Introducing human oversight significantly reduces the degree of automation and execution speed of workflows. Therefore, it is not suitable for fully automated scenarios aiming for high throughput and millisecond response times. The design of Human-in-the-Loop (HITL) nodes needs careful consideration, intervening only where absolutely necessary to avoid excessive manual checks slowing down the entire process.

> **Further reading: Production-grade frameworks**
>
> You don't need to implement these complex patterns from scratch. The industry already has mature frameworks to help you build and manage Agent workflows, which also include built-in error handling and state management tools.
> *   **Code frameworks: AgentScope, LangGraph**, and other libraries allow you to flexibly define nodes and edges with Python code, building arbitrarily complex graph-structured workflows, providing the highest level of customization.
> *   **Visual orchestration platforms: Alibaba Cloud Model Studio, Dify**, and other low-code/no-code platforms allow you to build workflows by dragging components and connecting lines, much like drawing a flowchart. This greatly lowers the development threshold, making it suitable for rapid prototyping and scenarios with relatively fixed business processes.

#### 3.3.6 Choosing the right pattern
You have learned about five different workflow patterns. A natural question is: when faced with a specific business problem, how should I choose, or even combine, these patterns?

Remember a core principle: **there is no “best” pattern, only the “most suitable” pattern**. Your choice should be determined by the inherent properties of the task, such as its complexity, dependencies between subtasks, requirements for cost and efficiency, and tolerance for result quality and risk.

### 3.4 Summary

Let’s review what you’ve learned in this section:

*   **Limitations of a single Agent**: When faced with complex, multi-step tasks, a single Agent struggles to maintain a stable execution plan and is prone to failure due to “attention drift” or “error accumulation.”
*   **Core idea of workflows**: Inspired by the “divide and conquer” philosophy, complex tasks are decomposed into multiple independent, manageable nodes, with explicit execution relationships defined among them to ensure process reliability.
*   **Five core orchestration patterns**: You have learned about pipeline, branching, parallel execution, mixture-of-experts, and human-in-the-loop. These patterns address scenarios involving fixed processes, one-of-many decisions, performance through concurrency, quality-focused outputs, and human oversight, respectively.

## 4 From fixed processes to autonomous planning

### 4.1 Limitations of fixed workflows

In the previous chapter, you learned how to build fixed workflows for repetitive tasks. Suppose you developed a “course preliminary research” bot for your company with a predefined process: upon receiving a request, it concurrently analyzes user personas, competitor courses, and industry demands.

Now, a course designer sends the bot the following instruction:  
“Please help me complete the preliminary research for a new Python introductory course.”

The bot faithfully initiates your preset workflow:
1.  **Industry demand analysis** subtask: tool call succeeds.
2.  **User persona definition** subtask: tool call succeeds.
3.  **Competitor course analysis** subtask: calls the `analyze_competitor_course` tool but receives an error:  
    “**Error: Unable to parse course outline due to competitor website layout update.**”

At this point, your bot cannot proceed further—because the designed workflow contains no logic to handle unexpected failures like “competitor analysis tool breakdown.”

*Figure (translated): without exception handling the workflow gets stuck when an unexpected failure occurs.*

```text
                              ┌─► [Industry needs: success] ──────────────┐
[Python course research] ───►{Parallel execution}├─► [User profile: success] ────────────────┼─► [Summary results]
                              └─► [Competitive analysis: website redesign cannot be parsed] ──┘
                                                              |
                                                              v
                                                  [Process interrupted: stuck]
```

### 4.2 Naive solution: Adding new branches

You might think: just add an exception-handling branch. For example, if `analyze_competitor_course` fails, trigger a new step—such as notifying the course designer for manual intervention.

*Figure (translated): exception handling via human intervention — the failed branch is handed to a human, then the workflow continues.*

```text
                              ┌─► [Industry needs: success] ──────────────────────────┐
[Python course research] ───►{Parallel execution}├─► [User profile: success] ────────────────────────────┼─► [Summary of results] ──► [Process completed]
                              └─► [Competitive analysis: website redesign cannot be parsed] ─► [Human intervention] ──┘
```

This “patch-on-demand” approach may seem effective—but what if next time the industry demand analysis API is temporarily down? Would you add another branch? What if the data source format changes during user persona definition? Another branch again?

You’ll quickly realize that it’s impossible to anticipate every possible failure mode. Predefining a handler for each exception leads to workflows that are overly complex, bloated, and hard to maintain. Worse, any unforeseen issue will still cause the entire system to stall.

The root cause is this: the Agent is merely a faithful executor of a rigid process—not a problem solver. It doesn’t “understand” that the user’s ultimate goal is to “complete the course preliminary research.” It only knows to follow your flowchart step by step. When one path is blocked, it lacks the ability to adaptively find alternatives—unlike a human would—to achieve the end goal.

> **Further reading: Goal vs. Task**
>
> Understanding the distinction between “goal” and “task” is key to grasping autonomous planning in Agents.
>
> *   **Goal**: The desired end state the user wants to achieve. It is high-level and sometimes ambiguous.  
>     Example: “Help me complete the preliminary research for a Python introductory course.”
> *   **Task**: A concrete, well-defined action taken to move toward the goal.  
>     Example: “Call the `analyze_competitor_course` tool with parameters `{url: 'some-site.com'}`.”
>
> An Agent limited to fixed workflows operates on “tasks.” When a task fails, it has no recourse. A more intelligent Agent focuses on the “goal.” Upon task failure, it recognizes that one route is blocked and autonomously devises new tasks to continue progressing toward the objective.

### 4.3 Enabling agents to plan autonomously

This insight leads to a pivotal question: Can we delegate the power of “planning” to the Agent itself—so it can dynamically design and adjust its workflow when facing unknown challenges?

This is precisely the core paradigm used in the industry to address such limitations: **Planning**.

With planning capabilities, the Agent’s operational model undergoes a fundamental shift. The developer’s role evolves from “workflow designer” to “goal specifier” and “capability (tool) provider,” while the Agent upgrades from a “task executor” to a **“solution planner.”**

Its new workflow looks like this:
1.  **Receive goal**: The Agent accepts a high-level user goal (e.g., “Complete preliminary research for a Python course”).
2.  **Dynamic planning**: The Agent’s “brain” (an LLM) reasons over the goal, decomposes it, and dynamically generates an **action plan**—a sequence of executable steps.
3.  **Execute plan**: An execution engine carries out the plan by invoking tools step-by-step, just like running a standard workflow.

*Figure (translated): the plan-and-execute paradigm — the plan becomes a generatable, executable artifact.*

```text
[User goal: research Python course] -> [Agent: planning] -> [Dynamically generated plan] -> [Executor]
                                                                                              |
                ┌─────────────────────────────────────────────────────────────────────────────┤
                v                                                                             v
[Tool 1: industry needs]    [Tool 2: user profile]    [Tool 3: competitive analysis] ...  ──► [Completed]
```

In this paradigm, the “plan” itself becomes a first-class, generatable, and executable artifact. The LLM is no longer a static node within a pipeline—it becomes the **creator** of the workflow.

To help you intuitively grasp this autonomous planning capability, we provide a complete example built with the AgentScope framework. It simulates the opening scenario: when the competitor analysis tool fails, the Agent autonomously replans and finds an alternative path to fulfill the user’s goal.

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

# Simulate business tools
async def analyze_competitor_course(url: str) -> ToolResponse:
    """Analyzes the outline of a competitor's course page"""
    # Simulate parsing failure due to website redesign
    return ToolResponse(content=[
        TextBlock(type="text", text=f"❌ Error: Due to {url} website layout update, unable to parse course outline.")
    ])

async def search_industry_demand(topic: str) -> ToolResponse:
    """Queries industry skill demands"""
    return ToolResponse(content=[
        TextBlock(type="text", text=f"✅ Report: Industry demand analysis for \"{topic}\" completed.")
    ])

async def google_search(query: str) -> ToolResponse:
    """Google web search"""
    if "syllabus" in query:
        return ToolResponse(content=[
            TextBlock(type="text", text="Search results: Found 'Python introductory course' syllabus PDF, address a.com/syllabus.pdf")
        ])
    return ToolResponse(content=[TextBlock(type="text", text="No relevant information found")])

async def extract_text_from_pdf(url: str) -> ToolResponse:
    """Extracts text from a PDF link"""
    return ToolResponse(content=[
        TextBlock(type="text", text=f"✅ Extracted outline text from {url}: 1. Variables and data types... 2. ...")
    ])

# Hook function for monitoring plan changes
plan_snapshots = []

def capture_plan_snapshot(notebook, plan):
    """Captures a snapshot of the plan"""
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
    print("🤖 Agent autonomous planning demo")
    print("=" * 60)

    # Create PlanNotebook and register the hook
    plan_notebook = PlanNotebook()
    plan_notebook.register_plan_change_hook("capture", capture_plan_snapshot)

    # Create toolkit
    toolkit = Toolkit()
    toolkit.register_tool_function(analyze_competitor_course)
    toolkit.register_tool_function(search_industry_demand)
    toolkit.register_tool_function(google_search)
    toolkit.register_tool_function(extract_text_from_pdf)

    # Create Agent
    agent = ReActAgent(
        name="CourseResearcherAgent",
        sys_prompt=(
            "You are a course research assistant. When encountering complex tasks:\n"
            "1. Create a plan using create_plan\n"
            "2. Execute step by step, mark completion with finish_subtask\n"
            "3. Flexibly adjust when encountering problems, for example, use google_search to find alternative solutions\n"
            "4. Finish with finish_plan when done"
        ),
        model=DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        plan_notebook=plan_notebook,
    )

    # User request
    print("\n💬 User: Please help me complete the preliminary research for a new Python introductory course.\n")
    print("-" * 60)

    await agent(Msg("user", "Please help me complete the preliminary research for a new Python introductory course, the competitor is a course from some-site.com.", "user"))

    # Display results (get the last complete plan from snapshots)
    print("\n" + "=" * 60)
    print("📊 Execution result")
    print("=" * 60)

    if plan_snapshots:
        final_plan = plan_snapshots[-1]
        finished = sum(1 for st in final_plan["subtasks"] if st["state"] == "finished")

        print(f"\n✅ Plan: {final_plan['name']}")
        print(f"📊 Progress: {finished}/{len(final_plan['subtasks'])}")
        print(f"🎯 Status: {final_plan['state']}\n")

        print("Subtask details:")
        for i, subtask in enumerate(final_plan["subtasks"], 1):
            icon = "✅" if subtask["state"] == "finished" else "⏳"
            print(f"  {icon} {i}. {subtask['name']}")

await main()
```

Through this example, you can see:
1. **Autonomous plan creation**: The Agent uses the `create_plan` tool to automatically plan research tasks.
2. **Flexible execution**: When the competitor analysis tool fails, the Agent automatically adjusts its strategy and switches to using `google_search`.
3. **Progress tracking**: Tasks are marked as complete using `finish_subtask`.
4. **Complete closed loop**: The entire process from plan creation to task completion.

This is precisely the core capability that PlanNotebook brings to the Agent: elevating it from a "process executor" to a "problem solver."

> **Further reading: Production-grade frameworks**
>
> Open-source frameworks like AgentScope and LangChain provide mechanisms to implement this “plan-execute” loop. They allow you to define a series of tools and then let the LLM act as a Planner to decide which tool to call at each step, using the results returned by the tool as input for subsequent reasoning, thereby achieving complex task decomposition and execution. On Alibaba Cloud Machine Learning Platform PAI, you can easily deploy and manage the LLM services required by these frameworks, providing powerful “brains” for your Agents.

### 4.4 Executing agent-generated plans

So, how can an LLM generate a “plan” that a machine can understand and execute?

The simplest way is to have it generate a natural language list of steps. But with this approach, it’s difficult for a downstream execution program to parse precisely. As you learned when having an Agent call tools, you can use a structured **JSON format** to output tool call parameters. Here, you can also view “executing a plan” as calling tools. Each step is a clearly defined object, containing the tool name to be called and its corresponding parameters.

```json
{
  "plan": [
    {
      "step": 1,
      "thought": "I first need to analyze industry demand, which is key to course positioning.",
      "tool_name": "search_industry_demand",
      "tool_params": {"topic": "Python basics"}
    },
    {
      "step": 2,
      "thought": "Next, I will try to analyze the outline of a competitor's course.",
      "tool_name": "analyze_competitor_course",
      "tool_params": {"url": "some-site.com/python-course"}
    }
  ]
}
```

This is an effective method, but its expressive power is limited. If the plan needs to include conditional logic like “if competitor analysis fails, switch to Google search,” a simple JSON list would be difficult to handle.

To express more complex logic, you can have the LLM directly generate code (Code as Action) to represent its plan, and then execute the code by calling a “code interpreter” tool.

```plaintext
# Plan generated by LLM
def execute_research_plan():
    # Step 1: Analyze industry demand
    demand_result = search_industry_demand(topic="Python basics")
    print(demand_result)

    # Step 2: Analyze competitor course
    competitor_result = analyze_competitor_course(url="some-site.com/python-course")

    # Step 3: Handle analysis failure
    if not competitor_result.success and "unable to parse" in competitor_result.message:
        print("Competitor analysis tool failed, looking for alternative solutions...")
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

By generating code, the LLM can leverage the rich capabilities inherent in programming languages (such as variables, conditional statements, loops) and powerful third-party libraries (such as Pandas) to formulate and execute extremely complex plans. This enables the Agent to handle not only simple linear processes but also complex scenarios involving logical judgments and data processing.

### 4.5 Advanced: Letting the agent create new tools

You have mastered a powerful method for LLMs to generate code for planning. This approach gives the Agent the ability to use complex logic such as variables, conditional statements, and loops.

But there is still a potential bottleneck: the Agent is still limited by the toolset you provide in advance. What if, while executing a plan, it discovers it needs a new tool that you haven't provided, such as a function to calculate the frequency of different technical keywords on recruitment websites? What should it do then?

The most direct way is for the Agent to stop and ask you (the developer) to write this new tool for it. But this interrupts the autonomous process of the task. Let's think further: since the Agent can already generate code for planning, can it also generate code for creating new capabilities?

This leads to a more advanced planning capability: dynamic tool creation.

To achieve this, in addition to providing specific business tools (like analyze_competitor_course), you need to provide the Agent with a core "meta-tool": a code interpreter.

When the Agent identifies that existing tools cannot meet its needs, its plan will include a series of special steps:

1. Decision: The LLM analyzes the task and identifies the need for a new tool that currently doesn't exist.
2. Generate code: In its plan, it will write a piece of code to define, test, and encapsulate a new tool function.
3. Call new tool: After the new tool is successfully created in the code execution environment, the Agent can directly call it in subsequent plan steps, just as if the tool had existed from the beginning.
4. Extend tool library: This newly generated tool can be added to the temporary tool library for the current task, for reuse in subsequent steps.

*Figure (translated): autonomous tool creation — when existing tools are insufficient, the agent generates and registers a new one.*

```text
[Receive task] -> [Agent analyzes requirements] -> {Are existing tools sufficient?}
                                                    | (yes)                       | (no)
                                                    v                             v
                                    [Use existing tools: complete task]   [Create new tool: identify gaps -> generate code]
                                                    |                             |
                                                    └──────────► [Execute: register -> invoke tool]
                                                                      |
                                                                      v
                                                 [Task completed; tool library expanded (new tool is reusable)]
```

Below is a simple example built using AgentScope, where the Agent can autonomously create and register a `factorial` tool during the planning process, based on the existing `add` tool, and then call it in subsequent tasks.

```python
"""AgentScope Agent Autonomous Tool Creation - Simplified Version"""
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
    """Code interpreter - Used to create and register new tools"""
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
            text=output or "✅ Execution successful"
        )])
    except Exception as e:
        sys.stdout = stdout
        return ToolResponse(content=[TextBlock(
            type="text",
            text=f"❌ Error: {e}"
        )])

async def add(a: float, b: float) -> ToolResponse:
    """Addition tool"""
    return ToolResponse(content=[TextBlock(
        type="text", 
        text=f"{a} + {b} = {a + b}"
    )])

async def main():
    if "DASHSCOPE_API_KEY" not in os.environ:
        print("❌ Please set DASHSCOPE_API_KEY")
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
            "    '''Description'''\n"
            "    result = ...\n"
            "    return ToolResponse(content=[TextBlock(type='text', text=f'{result}')])\n"
            "agent_toolkit.register_tool_function(tool_name)\n"
            "print('✅ Tool tool_name registered')"
        ),
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
    )
    
    print("=" * 60)
    print("🚀 Agent autonomous tool creation demo")
    print("=" * 60)
    
    # Use existing tools
    print("\n▶️ Scenario 1: Using existing tools")
    await agent(Msg("user", "Calculate 30 + 45", "user"))
    
    # Create new tool
    print("\n▶️ Scenario 2: Creating a factorial tool")
    await agent(Msg("user", "Create a factorial tool to compute factorials", "user"))
    
    # Use new tool
    print("\n▶️ Scenario 3: Using the new tool")
    await agent(Msg("user", "Calculate the factorial of 5 using factorial", "user"))
    
    # Display toolkit
    print("\n📦 Final toolkit:")
    for i, s in enumerate(toolkit.get_json_schemas(), 1):
        print(f"{i}. {s['function']['name']}")

if __name__ == "__main__":
    await main()
```

By providing a code interpreter, you elevate the Agent from a mere tool **user** to a tool **creator**. Its capability boundaries are no longer restricted by your predefined toolset, thereby giving it true creativity and adaptability in problem-solving.

### 4.6 When to choose autonomous planning?

You have learned about “fixed workflows” and “autonomous planning” modes. You might ask: should I always use the more intelligent autonomous planning in all scenarios and completely abandon fixed workflows?

This thinking is incorrect. Higher autonomy modes are not a silver bullet, and lower autonomy modes also have wide application scenarios. In production practice, a very effective best practice is to adopt a **“explore-crystallize” hybrid mode**.

This mode divides task processing into two stages:

1.  **Exploration phase**: For new, undefined tasks (e.g., you need to research a completely new, niche technology domain you’ve never encountered before), you cannot predefine a perfect process. In this case, you should deploy an autonomous planning Agent. Its task is to explore different paths to solve the problem, calling tools it deems appropriate, even if it makes mistakes or hits dead ends along the way. The ultimate goal is to find a stable solution path.

2.  **Crystallization phase**: When the autonomous planning Agent, after multiple explorations, validates and summarizes a stable, efficient solution path (e.g., it finds that the process of “first using tool A to crawl information from a specific website, then using tool B for data cleaning, and finally using tool C to generate a summary report” has the highest success rate), you can then abstract and crystallize this validated path into a reliable “fixed workflow” for subsequent large-scale, repetitive production calls.

This way, you establish a continuously optimizing positive feedback loop.

### 4.7 Case study: Letting the agent operate web pages

To help you understand more concretely how this “perceive-plan-act” loop is applied in actual products, let’s look at a case study of a highly autonomous web operating Agent, such as the open-source project Browser Use.

Traditional web automation (RPA) tools require fixed operating scripts to be written for each website and each task. Once the website interface changes slightly, the script becomes invalid, leading to extremely high maintenance costs.

An Agent with planning capabilities can fundamentally solve this problem. It does not rely on fixed scripts but **understands** the user’s goal like a human and **perceives** the current web page state to dynamically **plan** the next operation.

**Breakdown of execution process:**  
When a user gives the instruction “Search for books about AI on Amazon”:
1.  **Understanding and initial planning**: The LLM breaks down the vague goal into a series of high-level steps: “1. Open Amazon website; 2. Find search bar; 3. Type ‘AI books’; 4. Click search; 5. Analyze results.”
2.  **Action and perception**: The Agent executes the first step (opening the website). Then it “perceives” the new page—this includes not just looking at the HTML code but also potentially analyzing screenshots for visual layout to understand what elements are on the page.
3.  **Decision and replanning**: Based on the perceived information, it decides the next action: find the input area that looks most like a “search bar.” If there are multiple input fields on the page, it will infer and judge based on location, labels, and other information.
4.  **Loop execution**: It continues this “perceive-plan-act” loop until all steps are completed and returns the list of searched books.
5.  **Exception handling**: If it encounters an unexpected event at any step, such as a captcha popping up after clicking search, it won’t get stuck. It will perceive this new situation and insert “handle captcha” as a new obstacle into the current plan, attempting to resolve it or ask the user for help.

*Figure (translated): a planning agent driving a browser — perceive, decide, and re-plan on unexpected obstacles.*

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

This case fully demonstrates the core advantage of a planning Agent: it is no longer a script executor but achieves true **adaptive** operation in dynamic, unknown web environments through a continuous “perceive-plan-act” loop.

### 4.8 Summary

Let’s review what you’ve learned in this section:

*   **Limitations of fixed workflows**: When faced with unexpected obstacles like “tool failure,” preset fixed processes “get stuck” because they lack adaptability. Simply adding branches for every eventuality makes the process complex and difficult to maintain.

*   **“Planning” is the core solution**: Mimicking how humans solve problems, we elevate the Agent from a “task executor” to a “solution planner.” It no longer passively executes fixed steps but autonomously generates and adjusts action plans around the user’s ultimate “goal.”

*   **Translating plans into action**: You can guide the LLM to generate structured plans (e.g., JSON or code) for precise machine execution. A more advanced method is to provide the Agent with a code interpreter, enabling it to dynamically create and use new tools during planning, breaking through the limitations of preset capabilities.

*   **Balancing stability and flexibility**: “Autonomous planning” is suitable for exploring unknown, variable innovation tasks, while “fixed workflows” ensure the stability and efficiency of core business. In a production environment, you need to combine strategies like human-in-the-loop and explore-crystallize, making informed choices between these two modes based on specific business needs.

## 5 Multi-agent collaboration

### 5.1 Collaborating like a human team

One day, your colleague suggested: Can the bot participate in developing course drafts? For example, writing a draft for an interactive course on Pandas data analysis. Of course, the bots should ideally handle courses from various domains, which might have different work stages. You will find that this is a more general task.

You learned before:
- For multi-stage tasks like writing, you cannot have a single Agent complete all tasks, as this often leads to the Agent forgetting things and poor work quality. It should be broken down into multiple steps, with each specialized step handled by a different expert Agent.
- For creative, diverse tasks like writing, the steps for different types of course writing vary. You cannot enumerate all writing steps and hardcode them into workflows. You can try to let the Agent plan the writing process itself.

So, the problem now becomes how to effectively organize multiple Agents, allowing them to plan and execute in parallel while also integrating their final work results.

To achieve this, you can draw inspiration from how human expert teams work. Human experts have their respective areas of expertise, and they collaborate to complete complex tasks, often processing tasks in parallel. Therefore, you can also form an Agent Team, where each Agent is an expert in a relevant field, and they divide labor and collaborate in parallel.

### 5.2 Two collaboration patterns

In terms of specific implementation, human expert teams typically follow two common patterns: one is decomposition and execution led by a project manager, and the other is brainstorming around a whiteboard. In multi-agent systems, these correspond to the hierarchical planning pattern and the co-creation collaboration pattern, respectively.

#### 5.2.1 **Pattern one: Hierarchical/team leader pattern**

This is the most direct simulation of how a “project team” works, characterized by a centralized star-shaped structure. It introduces two roles:

1.  **Leader Agent**: In this example, it could be a “Course Project Manager” Agent. It is responsible for receiving and understanding top-level tasks (e.g., “Write a Pandas data analysis course”), breaking them down into multiple specific subtasks (“Design teaching outline,” “Provide core cases and code,” “Write course text”), and assigning these subtasks to appropriate team members. It is also responsible for tracking overall progress and, after all members complete their tasks, aggregating the results to form the final course document.
2.  **Member Agents**: Each possesses expertise in a specific domain (teaching designer, data scientist, content writer), focusing on executing assigned subtasks and reporting back to the Leader upon completion.

*Figure (translated): hierarchical planning — a Leader agent assigns subtasks and workers report back.*

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

In AgentScope, you can implement the hierarchical planning pattern using a handoff mechanism. In this pattern, the Leader Agent treats each domain expert as a tool, and task assignment and reporting are achieved through tool calls. AgentScope also supports asynchronous tool calls and dynamic tool extension, meaning you can execute multiple expert Agents concurrently and even allow the Leader Agent to create expert Agents in real-time as needed.

```python
import os
from typing import Any

from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.tool import ToolResponse, Toolkit

# ---- 1. Define unified expert Agent roles and prompts ----

DESIGNER_LI_PROMPT = """ You are Teacher Li, an experienced instructional designer. Your task is to design a clear, logical teaching outline for the "Introduction to Pandas Data Analysis" course. Focus on: 1. Defining clear learning objectives for each module. 2. Ensuring knowledge points progress from shallow to deep, step by step. 3. Proposing interactive exercises and projects to consolidate learning effects. """

SCIENTIST_WANG_PROMPT = """ You are Engineer Wang, a senior data scientist and a practical expert in Pandas. Your task is to provide accurate, practical technical content for the course. Focus on: 1. Providing the most core and commonly used Pandas knowledge points. 2. Designing cases and datasets derived from real work scenarios. 3. Writing concise, standardized, and easy-to-understand code examples. """

WRITER_ZHANG_PROMPT = """ You are Xiao Zhang, a creative course content writer. Your task is to write course material that explains technical content in an accessible way, without losing rigor, and with calm, restrained language. Focus on: 1. Using easy-to-understand language and metaphors to explain complex concepts. 2. Designing highly realistic case scenarios and module titles. 3. Ensuring the overall tone of the course is encouraging and inspiring. """

LEADER_PROMPT = """ You are a course project manager, responsible for coordinating the team to complete the draft of the "Introduction to Pandas" course. You have three team members available as tools to call, and each person's work depends on the output of the previous person.

Your workflow must strictly follow this order:
1.  **First, call invoke_designer_li**, asking him to create an initial outline and learning objectives for the course.
2.  **Second, call invoke_scientist_wang**. Pass the outline generated by Teacher Li to him as `context`, asking him to fill in technical key points and code examples based on this outline.
3.  **Then, call invoke_writer_zhang**. Merge all outputs from Teacher Li and Engineer Wang, and pass them as `context` to her, asking her to write the complete, learner-friendly course material based on this.
4.  **Finally**, after receiving the final results from all experts, integrate them into a uniformly formatted, complete final course document, and then provide it as your final response. """

# ---- 2. Unified model and Agent configuration ----

def get_model_instance() -> DashScopeChatModel:
    """Gets a uniformly configured model instance."""
    return DashScopeChatModel(
        model_name="qwen-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
    )

def create_member_agent(name: str, sys_prompt: str) -> ReActAgent:
    """Creates a team member Agent based on the given name and system prompt."""
    return ReActAgent(
        name=name,
        sys_prompt=sys_prompt,
        model=get_model_instance(),
        formatter=DashScopeMultiAgentFormatter(),
    )

# ---- 3. Define "team member" Agents as tools (Handoffs pattern) ----

async def invoke_designer_li(task_description: str, context: str = "") -> ToolResponse:
    """
    Calls instructional designer Teacher Li when needing to design course outlines, learning objectives, or teaching activities.

    Args:
        task_description (str): Clearly describes the design task you need Teacher Li to complete.
        context (str): Optional. Pass relevant background information or previous work results.
    """
    print("\n--- Task assignment: Calling instructional designer Teacher Li ---")
    agent = create_member_agent("DesignerLi", DESIGNER_LI_PROMPT)

    content_for_agent = task_description
    if context:
        content_for_agent = f"Background information:\n{context}\n\nYour task: {task_description}"

    result_msg = await agent(Msg(name="user", role="user", content=content_for_agent))
    return ToolResponse(content=result_msg.get_text_content())

async def invoke_scientist_wang(task_description: str, context: str = "") -> ToolResponse:
    """
    Calls data scientist Engineer Wang when needing to provide professional technical knowledge, code examples, or real-world cases.

    Args:
        task_description (str): Clearly describes the technical task you need Engineer Wang to complete.
        context (str): Optional. Pass previous work results such as course outlines, so he can build upon them.
    """
    print("\n--- Task assignment: Calling data scientist Engineer Wang ---")
    agent = create_member_agent("ScientistWang", SCIENTIST_WANG_PROMPT)

    content_for_agent = task_description
    if context:
        content_for_agent = f"Please complete your task based on the following course outline and background information:\n{context}\n\nYour specific task is: {task_description}"

    result_msg = await agent(Msg(name="user", role="user", content=content_for_agent))
    return ToolResponse(content=result_msg.get_text_content())

async def invoke_writer_zhang(task_description: str, context: str = "") -> ToolResponse:
    """
    Calls content writer Xiao Zhang when needing to transform technical content into easy-to-understand text.

    Args:
        task_description (str): Clearly describes the writing task you need Xiao Zhang to complete.
        context (str): Optional. Pass previous work results such as outlines and technical points, as a basis for writing.
    """
    print("\n--- Task assignment: Calling content writer Xiao Zhang ---")
    agent = create_member_agent("WriterZhang", WRITER_ZHANG_PROMPT)

    content_for_agent = task_description
    if context:
        content_for_agent = f"Please complete your writing task based on the following course draft (including outline and technical points):\n{context}\n\nYour specific task is: {task_description}"

    result_msg = await agent(Msg(name="user", role="user", content=content_for_agent))
    return ToolResponse(content=result_msg.get_text_content())

# ---- 4. Organize "hierarchical planning" workflow ----

async def main() -> None:
    """Main execution function, responsible for orchestrating the entire workflow."""

    # 4.1 Create supervisor's toolkit and register team members
    leader_toolkit = Toolkit()
    leader_toolkit.register_tool_function(invoke_designer_li)
    leader_toolkit.register_tool_function(invoke_scientist_wang)
    leader_toolkit.register_tool_function(invoke_writer_zhang)

    # 4.2 Create supervisor Agent
    leader_agent = ReActAgent(
        name="ProjectLeader",
        sys_prompt=LEADER_PROMPT,
        model=get_model_instance(),
        toolkit=leader_toolkit,
        formatter=DashScopeMultiAgentFormatter(),
    )

    # 4.3 Define top-level task
    top_level_task = (
        "Please create a short course draft for beginners on Pandas data analysis."
    )

    print(f"Top-level task received by project manager:\n{top_level_task}\n" + "="*50)

    # 4.4 Hand off the task to the supervisor Agent for execution
    final_response_msg = await leader_agent(Msg(name="user", role="user", content=top_level_task))

    # 4.5 Display final results
    print("\n" + "="*50)
    print("  Project manager's final summary report:")
    print("="*50 + "\n")
    print(final_response_msg.get_text_content())

# ---- 5. Run main program ----
await main()
```

When a course development project starts, the project manager breaks down the requirements document into a clear task list and then distributes it to **instructional designers, data scientists, and content writers**. The advantages of this pattern are obvious: **clear structure and well-defined responsibilities**. Everyone knows their tasks and deadlines, and the project manager can easily track overall progress, ensuring the project stays on track. Therefore, this pattern is very suitable for scenarios where **goals are clear and can be clearly decomposed into multiple parallel subtasks**.

However, the limitations of this pattern also stem from its structure. **Instructional designers and data scientists** usually do not communicate directly but pass information through the project manager. If the **data scientist**, while writing code, finds that a theoretical point can be explained more simply with a different example, they need to report to the manager first, who then relays it to the designer. This process can involve **information delays or distortions**. Ultimately, although all modules of the course are completed with high quality, their combination might feel somewhat disjointed, lacking a seamless flow. This is because there is a lack of direct, real-time intellectual exchange among the experts.

#### 5.2.2 Pattern two: Co-creation/blackboard pattern

In this pattern, there is no high-level coordinator; instead, a group of experts in a meeting room conduct a **“brainstorming session”** around a whiteboard. Its characteristic is decentralization.

1.  **Establish a shared space (Shared Blackboard)**: Create a shared space that all Agents can read and write (e.g., a shared document, database record, or message queue).
2.  **Parallel contribution and iteration**: When an open-ended question (such as “Design an interesting project case for a new course”) is posted to the shared space, all expert Agents (**instructional designers, data scientists, content writers**) simultaneously begin thinking and write their ideas, arguments, or draft solutions into the shared space.
3.  **Stimulation and deepening**: In each iteration, all Agents read all new ideas from others in the shared space. These ideas will inspire them to generate new insights, or to revise, supplement, or question their own solutions, and then write the updated ideas back. For example, the **data scientist** Agent proposes using “analyzing user movie rating data” as a case; the **instructional designer** Agent sees this and adds, “students can be guided to explore rating trends for different movie genres”; and the **content writer** Agent suggests, “the case can be packaged as a story titled ‘Unveiling the Movie Recommendation System’.”
4.  **Reach consensus**: This “read-think-write” loop continues until a final solution, approved by most Agents, emerges in the system, or a preset number of iterations is reached.

*Figure (translated): co-creation via MsgHub — all agents read/write ideas in a shared space over multiple rounds.*

```text
[Open-ended task: design course] -> [Shared space: MsgHub] <──► [Instructional designer: Teacher Li]
                                      │      ▲                 <──► [Data scientist: Engineer Wang]
                                      │      │                 <──► [Content writer: Xiao Zhang]
                                      │      └────────────── (multi-round iteration, mutual inspiration)
                                      v
                          [Meeting secretary: organize and summarize] ──► [Team outcome: course outline]
```

In AgentScope, you can implement the co-creation collaboration pattern using MsgHub. In this pattern, any Agent's reply is automatically “heard” by other participants and used as context.

```python
import os
from agentscope.agent import ReActAgent
from agentscope.formatter import DashScopeMultiAgentFormatter
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.pipeline import MsgHub
from textwrap import dedent

# ---- 1. Define unified expert Agent roles and prompts ----

DESIGNER_LI_PROMPT = """ You are Teacher Li, an experienced instructional designer. Your task is to design a clear, logical teaching outline for the "Introduction to Pandas Data Analysis" course. In discussions, you focus on: 1. Defining clear learning objectives for each module. 2. Ensuring knowledge points progress from shallow to deep, step by step. 3. Proposing interactive exercises and projects to consolidate learning effects. """

SCIENTIST_WANG_PROMPT = """ You are Engineer Wang, a senior data scientist and a practical expert in Pandas. Your task is to provide accurate, practical technical content for the course. In discussions, you focus on: 1. Providing the most core and commonly used Pandas knowledge points. 2. Designing cases and datasets derived from real work scenarios. 3. Writing concise, standardized, and easy-to-understand code examples. """

WRITER_ZHANG_PROMPT = """ You are Xiao Zhang, a creative course content writer. Your task is to write course material that explains technical content in an accessible way, without losing rigor, and with calm, restrained language. In discussions, you focus on: 1. Using easy-to-understand language and metaphors to explain complex concepts. 2. Designing highly realistic case scenarios and module titles. 3. Ensuring the overall tone of the course is encouraging and inspiring. """

# ---- 2. Auxiliary function to create expert Agents ----
def create_expert_agent(name: str, sys_prompt: str) -> ReActAgent:
    """Creates an expert Agent based on the given name and system prompt."""
    return ReActAgent(
        name=name,
        sys_prompt=sys_prompt,
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
        ),
        formatter=DashScopeMultiAgentFormatter(),
    )

# ---- 3. Main function to organize collaborative process ----
async def main() -> None:
    """Runs the co-creation collaboration pattern for Pandas course development and generates final results."""
    print("=== Starting course development meeting: Brainstorming 'Introduction to Pandas' course outline and cases ===")

    # Create course development team
    designer_li = create_expert_agent("Teacher Li (Instructional Designer)", DESIGNER_LI_PROMPT)
    scientist_wang = create_expert_agent("Engineer Wang (Data Scientist)", SCIENTIST_WANG_PROMPT)
    writer_zhang = create_expert_agent("Xiao Zhang (Content Writer)", WRITER_ZHANG_PROMPT)

    # Define meeting opening remarks
    announcement = Msg(
        "system",
        (
            "Team, our goal today is to collaborate on developing a complete and engaging **course outline and core cases** for the 'Introduction to Pandas Data Analysis' course."
            "Please brainstorm together, starting with instructional designer Teacher Li, to propose your first round of suggestions."
        ),
        "system",
    )

    # Start multi-turn discussion
    async with MsgHub(
        participants=[designer_li, scientist_wang, writer_zhang],
        announcement=announcement,
    ) as hub:
        for i in range(2):
            print(f"\n--- Round {i + 1} of collaboration ---")
            # Call sequentially in speaking order
            await designer_li()
            await scientist_wang()
            await writer_zhang()

    print("\n=== Meeting ends ===")

    # ==================== Aggregation stage ====================
    print("\n=== Starting to generate final team output (Course Outline Draft) ===")

    # 4.1 Define a "Meeting Secretary" Agent to compile meeting minutes
    secretary_prompt = dedent("""
        You are a professional meeting secretary, highly skilled at compiling meeting minutes.
        Your task is to read the team discussion records below, and then, based on the discussion content,
        generate a **course outline draft** for the "Introduction to Pandas" course in a clear Markdown format.

        The outline should include the following sections:
        - **Module Title**: An engaging title.
        - **Learning Objectives**: Clearly list what students will be able to do after completing this module.
        - **Core Concepts**: Key technical points covered.
        - **Core Cases**: Practical cases and datasets used throughout this module.
        - **Code Examples**: Key code demonstrations needed.
        - **Post-lesson Exercises**: A specific hands-on exercise task.
    """)
    secretary_agent = create_expert_agent("Meeting Secretary", secretary_prompt)

    # 4.2 Prepare complete discussion records
    full_transcript_msgs = await designer_li.memory.get_memory()

    transcript_text = "Here are the team's discussion records:\n\n"
    for msg in full_transcript_msgs:
        if msg.role != "system":
            transcript_text += f"[{msg.name}]: {msg.content}\n"

    # 4.3 Assign aggregation task
    final_task_prompt = dedent(
        f"{transcript_text}\n"
        "Please organize the course outline draft based on the discussion records above."
    )

    # Call the secretary Agent to complete the task
    final_output_msg = await secretary_agent(Msg("user", final_task_prompt, "user"))

    # 4.4 Display final results
    print("\n" + "="*25)
    print("  Final team output: Course Outline Draft")
    print("="*25 + "\n")
    print(final_output_msg.content)

await main()
```

In such an open discussion, one person's idea immediately sparks inspiration in another, creating a “1+1>2” effect. This **decentralized collaboration can maximize collective intelligence**, especially suitable for solving **open-ended, creative problems that have no single correct answer and require brainstorming**.

Of course, the risks of this pattern are also evident. A brainstorming session without good guidance can easily **diverge and fail to converge** or get stuck in a deadlock. Without a centralized decision-maker, the team might over-optimize certain details while neglecting the overall goal. At the same time, all members need to constantly synchronize and process massive amounts of information from others, which places higher demands on controlling communication costs.

### 5.3 Selection advice: Design derived from reality

After understanding the hierarchical planning and co-creation collaboration patterns, a natural question arises: which one should I choose? Or, are there other patterns?

**There is no “best pattern”.** An excellent Multi-Agent system’s design often comes from imitating and refining the real world.

Instead of memorizing abstract pattern names, delve into your business and observe how human expert teams complete similar tasks in the real world. When observing, you can focus on these three aspects:

*   **Business process**: What stages does the task itself involve? Are these stages upstream-dependent or can they be parallel? How do they connect?
*   **Expert roles**: Which experts with different capabilities are needed in this process? What are their core responsibilities?
*   **Collaboration method**: How do experts communicate? Is it through a centralized project manager relaying information, or do they freely discuss around a whiteboard in a meeting room? How does information flow between them?

Based on these observations, you can follow a clear design path:

1.  **① Observe reality**: Deeply understand how human teams work.
2.  **② Recreate the process**: Map real-world roles and collaboration processes to your Agent roles and collaboration mechanisms.
3.  **③ Iterate and improve**: Optimize and enhance based on the recreation, leveraging AI’s advantages.

For example, in our course development case, the “project manager” pattern simulates projects with clear deliverables; the “brainstorming” pattern simulates early creative idea generation meetings. In reality, a complete project might even combine both: first, determine core ideas through “brainstorming,” then switch to the “project manager” pattern for division of labor and execution. This hybrid pattern retains the controllability of the overall structure while introducing creativity at key nodes.

Ultimately, remember this core idea:

**Instead of memorizing what Multi-Agent patterns exist, delve into the business and observe how human experts collaborate in the real world.**

### 5.4 Summary

Let’s review what you’ve learned in this section:

*   **Limitations of monolithic Agents**: A single Agent striving for “omnipotence” often performs poorly on complex tasks spanning multiple specialized domains (like course development) due to knowledge boundaries and cognitive overload.
*   **Core idea of multi-agent systems**: From the failure of rigid “pipeline” patterns, you were inspired by efficient real-world teams, recognizing that “specialized division of labor, parallel processing, and communication integration” are key to solving complex problems.
*   **Multi-agent collaboration patterns**: You mastered two mainstream collaboration patterns. The **hierarchical planning pattern** efficiently handles clearly decomposable tasks by simulating a “project manager–expert” structure; the **co-creation collaboration pattern** leverages collective intelligence for open-ended problems by simulating “brainstorming.”
*   **Cost-value trade-off**: Although multi-agent systems can increase call costs and latency, they improve the “usability” of the final output, avoiding repeated attempts and hidden costs caused by low-quality outputs. This is an effective investment for high-quality results.

## 6 Giving the agent memory

In this section, you will learn how to give your Agent memory capabilities, solving the inherent “forgetfulness” problem of LLMs. You will start with the simplest method, gradually discover its limitations, and finally master mainstream short-term and long-term memory construction strategies.

First, let’s configure the environment needed for this course.

```python
import os

# Import modules that will be used later
from agentscope.agent import ReActAgent
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.formatter import DashScopeChatFormatter
from agentscope.embedding import DashScopeTextEmbedding
from agentscope.memory import Mem0LongTermMemory
from agentscope.model import DashScopeChatModel
from agentscope.token import HuggingFaceTokenCounter

# Define a helper function to create Agent, convenient for later use
def create_agent(name: str, sys_prompt: str, **kwargs) -> ReActAgent:
    """A helper function to create an Agent"""
    # Allow caller to override default model/formatter/memory, to avoid repetitive binding
    formatter = kwargs.pop("formatter", DashScopeChatFormatter())
    model = kwargs.pop(
        "model",
        DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
            stream=True,
        ),
    )
    memory = kwargs.pop("memory", InMemoryMemory())

    return ReActAgent(
        name=name,
        sys_prompt=sys_prompt,
        model=model,
        formatter=formatter,
        memory=memory, # Default to using the simplest memory buffer
        **kwargs,
    )

print("Environment setup complete!")
```

### 6.1 Establishing short-term memory

In previous lessons, you were building an Agent team to help you write courses. The content writing Agent just finished an excellent first draft. You were pleased and said to it: "Great, now please make the second part more engaging, according to the teaching style we discussed last time."

However, the Agent's response disappointed you: "Okay, what teaching style did we discuss last time?" It had forgotten the details of the previous task. This is because your Agent is stateless. Each time a new conversation starts, it forgets everything from past conversations.

> **Further reading: Core characteristic of LLMs – statelessness**  
>
> You can imagine an LLM as an expert with only a few seconds of memory. In each independent API call, it can understand all the information you give it and provide brilliant answers. But once that call ends, it completely forgets everything. It won't remember who you are, what you talked about before, or any of your preferences and requirements. Every reply from an Agent is essentially an independent API call, so it naturally inherits this statelessness.

So how do we solve this? The most direct idea is to "review" all previous chat history every time you talk to it.

In programming implementation, this means you need to create a list to store all conversation history. Each time you ask the Agent a question, you send this list containing the complete history along with your new message. `InMemoryMemory` in AgentScope is an implementation of this simple approach.

Let's verify this with code.

```python
# Create a course writing Agent
writing_agent = create_agent(
    name="Writer",
    sys_prompt="You are a course content writer. Your task is to write a Pandas data analysis course."
)

async def run_stateless_test():
    # First conversation: Set teaching style
    msg1 = Msg("user", "Our teaching style should be rigorous and restrained, please remember this.", "user")
    print(f"[{msg1.name}]: {msg1.content}")

    # The Agent will store this conversation in its InMemoryMemory
    reply1 = await writing_agent(msg1)
    print(f"[{reply1.name}]: {reply1.content}")

    print("\n" + "="*20 + "\n")

    # Second conversation: Propose new requirements based on previous settings
    # When called, writing_agent will automatically send the history from InMemoryMemory along with the new message to the model
    msg2 = Msg("user", "Great, now please write the second part more professionally.", "user")
    print(f"[{msg2.name}]: {msg2.content}")

    reply2 = await writing_agent(msg2)
    print(f"[{reply2.name}]: {reply2.content}")

    print("\n" + "="*20 + "\n")
    print("Agent's short-term memory content:")
    # Print Agent's memory, you can see it contains both rounds of conversation
    for m in await writing_agent.memory.get_memory():
        print(f"- [{m.role}] {m.name}: {m.content}")

await run_stateless_test()
```

This solution works immediately, and the Agent instantly gains short-term conversational memory.

### 6.2 Information refinement

However, when you put this Agent into a real scenario and use it for a dozen or dozens of conversations, two serious problems will emerge:

1. **Context window limitations**. Every LLM has a maximum text length it can process, which we call the "context window." As the number of conversation turns increases, the conversation history will snowball, eventually exceeding the model's window limit, and the program will directly throw an error.
2. **Rapidly rising costs**. LLM API calls are billed per usage; every token you send (input) and every token it generates (output) costs money. After multiple turns of conversation, each API call needs to resend the entire history, incurring repetitive token costs.

This naive "memory" solution is merely a short-term strategy of "eating next year’s crop." It will soon lead to program exceptions or cost overruns.

This leads to a core question: **How can we effectively manage context length and cost without sacrificing critical information?**

The essence of this problem is how to efficiently **compress** and **filter** information. Just like when you prepare for an open-book exam, you don’t copy the entire textbook onto your cheat sheet; instead, you extract the most important formulas, definitions, and key arguments.

### 6.3 Memory management strategies

Let’s learn from how humans prepare for exams to explore strategies for managing Agent memory.

#### 6.3.1 Strategy one: Simple "forgetting" – fixed window truncation

The simplest and most crude method is to only remember recent events, which is called **fixed window truncation**.

- **Idea**: You set a fixed window size—for example, only retaining the most recent N turns of conversation, or more precisely, only the most recent N tokens. When the conversation history exceeds this size, the oldest turn of conversation is discarded, ensuring the total context length remains basically constant.
- **Relative advantages**: Extremely simple to implement, low computational overhead, effectively ensures that context length is always within a controllable range, avoiding errors and unlimited cost growth.
- **Applicable scenarios**: Suitable for scenarios where information value decays rapidly over time, such as chatbots or simple customer service Q&A.
- **Boundary conditions**: This is a “one-size-fits-all” forgetting solution. If critical information from early in the conversation (e.g., the user’s core goal set in the first turn) is truncated, the Agent will “forget” again, leading to broken conversational logic.

*Figure (translated): fixed-window truncation — keep only the most recent N entries, forgetting the earliest.*

```text
[Conversation history: rules A B C D] -> [Fixed window: keep only the most recent N entries]
                                              │
                                    ┌─────────┴─────────┐
                                    v                   v
                          [Retain: rules C D]   [Discard: rules A B]
```

In `AgentScope`, this functionality is implemented by the `Formatter` component. You can pass the `max_tokens` parameter when initializing `Formatter` to limit the context length.

```python
# Create a Formatter with truncation functionality (requires a token counter, otherwise truncation will not be triggered)
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

# Create an Agent using this Formatter
truncation_agent = create_agent(
    name="Trunk",
    sys_prompt="You are a forgetful robot, you can only remember recent events.",
    # Replace the default formatter with our newly created formatter with truncation functionality
    formatter=truncated_formatter
)

async def run_truncation_test():
    # Conduct multiple turns of conversation, deliberately making the context longer
    await truncation_agent(Msg("user", "Rule A: All answers must be declarative sentences.", "user"))
    await truncation_agent(Msg("user", "Rule B: Do not use 'you' or 'I'.", "user"))
    await truncation_agent(Msg("user", "Rule C: Answers should be as brief as possible.", "user"))
    await truncation_agent(Msg("user", "Rule D: Numbers must be written in uppercase characters.", "user"))

    print("After multiple turns of conversation, the Agent's memory (theoretically very long):") 
    for m in await truncation_agent.memory.get_memory():
        print(f"- [{m.role}] {m.name}: {m.content}")

    print("\n" + "="*20 + "\n")

    # Ask a question to test if the Agent still remembers the earliest Rule A
    reply = await truncation_agent(Msg("user", "Please summarize all rules.", "user"))

    print(f"[{reply.name}]: {reply.content}")
    print("\nThe Agent has likely forgotten the earliest 'Rule A' because it discarded the oldest conversations from the beginning of memory to satisfy the max_tokens=40 limit.")

await run_truncation_test()
```

#### 6.3.2 Strategy two: Extracting key points – rolling summary

Simple truncation directly discards information, which is obviously not ideal. A smarter approach is to extract key points before forgetting details. This is the **rolling summary** strategy.

- **Idea**: As the conversation progresses, when the history is about to “fill” the context window, you invoke the LLM once to summarize the earliest portion of the dialogue (e.g., the first 50%) into a concise paragraph. In subsequent requests, this condensed “memory summary” replaces the original, verbose conversation records.
- **Relative advantages**: While compressing length, it maximizes the preservation of core information from historical conversations, better maintaining long-term conversational coherence.
- **Applicable scenarios**: Suitable for tasks requiring long-term goal consistency, such as project planning or long-form content creation.
- **Boundary conditions**: It introduces additional API call costs (for generating summaries), and the quality of the summary directly affects subsequent conversations.

*Figure (translated): summary memory — when history exceeds a threshold, the LLM compresses it into a summary.*

```text
[Full history: conversations 1-10] -> {Check length}
                                       | (does not exceed threshold)    | (exceeds threshold)
                                       v                                v
                                [Keep as is]                [LLM generates summary]
                                                                         |
                                                                         v
                                                          [Compressed: summary + recent conversation]
```

Currently, `AgentScope` does not have this feature built-in, but you can easily implement this logic by customizing a `Memory` class. Below is a **conceptual implementation idea**:

```python
# This is a pseudocode example to demonstrate the core logic of rolling summary
# It cannot be run directly; you need to inherit agentscope.memory.MemoryBase and implement the full logic

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

            # 2. Call LLM to generate summary (pseudocode)
            # summary_text = llm.call("Please summarize the following conversation into one paragraph:", messages_to_summarize)
            summary_text = "The user set the teaching style to be humorous and engaging, and requested the content to be vivid."

            summary_message = Msg("system", f"【History summary】{summary_text}", "system")

            # 3. Replace original conversation with summary
            self.history = [summary_message] + self.history[num_to_summarize:]
            print(f"--- Memory compressed, current length {len(self.history)} ---") 

    def get_memory(self):
        return self.history

# Usage example
# summary_mem = SummaryMemory()
# summary_mem.add(Msg("user", "Our teaching style should be humorous and engaging.", "user"))
# ... After multiple turns of conversation ...
# summary_mem.add(Msg("user", "Add another case about cost.", "user"))
# This might trigger summarization at this point
```

#### 6.3.3 Strategy three: Building a knowledge base – vector-based retrieval

The previous strategies still process all conversation history in a **linear**, **undifferentiated** manner. But this does not align with how humans remember things. Your memory is not a tape recording played in chronological order, but a vast, interconnected network of knowledge.

This “on-demand retrieval” pattern is central to building advanced memory systems. This strategy completely changes the game: you no longer try to cram all history into the context; instead, each turn of conversation is transformed into independently retrievable “memory fragments” and stored in a specialized “long-term memory bank.”

- **Idea**:
  1. **Storage (Ingestion)**: After each conversation turn, you convert the conversation content into a mathematical vector (**Embedding**), then store it along with the original text in a **vector database**.
  2. **Retrieval**: When the user asks a new question, you first convert this question into a vector, then perform a similarity search in the database to find the few historical conversation records **most relevant** to the current question.
  3. **Composition**: Finally, you combine the retrieved “relevant memories” and the user’s “latest question” into a concise and efficient context, and then send it to the LLM.

- **Relative advantages**: Fundamentally breaks free from the length constraints of the context window, capable of precisely “recalling” the most relevant content from massive amounts of information based on current intent, greatly saving costs.
- **Applicable scenarios**: This is the foundation for building truly intelligent, long-term interactive Agents. Suitable for all complex scenarios such as personalized assistants, enterprise knowledge bases, and intelligent learning companions.
- **Boundary conditions**: The system complexity is highest. It introduces new technology stacks such as Embedding models and vector databases.

*Figure (translated): long-term memory with a vector database — store memories offline, retrieve the most relevant ones per new question.*

```text
Storage phase:    [Conversation content] -> [Convert to vector (embedding)] -> (Vector database)
                                                                                  |
                                                                                  v
Retrieval phase:  [New question] -> [Convert to vector] -> [Similarity search]
                                                              |
                                                              v
                                                   [Retrieval results: top-K relevant conversations]
                                                              |
                                                              v
                                      [Combine relevant memories + new question] -> [Send to model]
```

`AgentScope` elegantly implements this feature through the `Mem0LongTermMemory` module. It supports two working modes:

1. **`static_control`**: Automatically and passively saves and retrieves memories before and after each Agent reply.
2. **`agent_control`**: Gives the Agent active memory management tools (`record_to_memory`, `retrieve_from_memory`), allowing the Agent to decide when to remember and when to recall.

Let’s first look at the simpler `static_control` mode.

```python
# 1. Initialize the long-term memory module
# It requires an LLM (for internal processing) and an embedding model
from mem0.vector_stores.configs import VectorStoreConfig
from llama_index.embeddings.openai_like import OpenAILikeEmbedding

# Specify the same dimension (2048) for Qdrant local vector store as DashScope Embedding
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
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
        stream=False,
    ),
    embedding_model= DashScopeTextEmbedding(
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
    long_term_memory_mode="static_control", # Key parameter: set to static control mode
)

async def run_ltm_static_test():
    # Conversation one: Store a key piece of information
    msg1 = Msg("user", "Remember, we are writing a Pandas data analysis course, and the first draft is already complete.", "user") 
    print(f"[{msg1.name}]: {msg1.content}")
    reply1 = await ltm_agent_static(msg1)
    print(f"[{reply1.name}]: {reply1.content}")
    # After this step, the conversation content will be automatically stored in long-term memory

    print("\n" + "="*20 + " Simulating a new session " + "="*20 + "\n") 
    # Clear the Agent's short-term memory, simulating a brand new session
    await ltm_agent_static.memory.clear()
    print("Agent's short-term memory has been cleared.")

    # Conversation two: Ask a related question
    # Before replying, the Agent will retrieve information from long-term memory using the question "Who is this course suitable for?"
    msg2 = Msg("user", "What was our work progress last time?", "user") 
    print(f"[{msg2.name}]: {msg2.content}")
    reply2 = await ltm_agent_static(msg2)
    print(f"[{reply2.name}]: {reply2.content}")
    print("\nNote: Even if short-term memory is cleared, the Agent can still answer correctly because it retrieved relevant information from long-term memory.") 
    # "注意: 即使短期记忆被清空，Agent 依然能回答正确，因为它从长期记忆中检索到了相关信息。" -> "Note: Even if short-term memory is cleared, the Agent can still answer correctly because it retrieved relevant information from long-term memory."

await run_ltm_static_test()
```

#### 6.3.4 Advanced: From passive context to active memory management

At this point, you have mastered powerful strategies for building memory systems for Agents. However, a truly intelligent Agent should not just passively receive your processed context; it should be able to actively manage its own memory.

By setting `long_term_memory_mode` to `agent_control`, `ReActAgent` automatically gains two tools: `record_to_memory` and `retrieve_from_memory`. You need to guide it to use these tools in the system prompt.

```python
# Reuse the previously created long_term_memory instance
# Recreate an Agent, this time using agent_control mode
from textwrap import dedent
ltm_agent_active = create_agent(
    name="LTM_Writer_Active",
    sys_prompt=dedent(
        "You are a course writer with active memory management capabilities.\n" # "你是一个拥有主动记忆管理能力的课程编写员。" -> "You are a course writer with active memory management capabilities."
        "You can use the following tools to manage your long-term memory:\n"
        "- `record_to_memory(data: str)`: Records an important piece of information to long-term memory.\n" # "将一段重要的信息记录到长期记忆中。" -> "Records an important piece of information to long-term memory."
        "- `retrieve_from_memory(query: str) -> str`: Retrieves relevant information from long-term memory based on a query.\n" # "根据查询从长期记忆中检索相关信息。" -> "Retrieves relevant information from long-term memory based on a query."
        "Before answering, first consider whether you need to retrieve memory. After the conversation, consider if there is critical information that needs to be recorded." # "在回答问题前，先思考是否需要检索记忆。在对话结束后，思考是否有关键信息需要记录。" -> "Before answering, first consider whether you need to retrieve memory. After the conversation, consider if there is critical information that needs to be recorded."
    ),
    long_term_memory=long_term_memory,
    long_term_memory_mode="agent_control", # Key parameter: set to Agent control mode
)

async def run_ltm_active_test():
    # Conversation one: Agent autonomously decides to record information
    msg1 = Msg("user", "The writing style of the course must be very rigorous and academic; this is a core requirement.", "user") # "课程的写作风格必须非常严谨和学术化，这是一个核心要求。" -> "The writing style of the course must be very rigorous and academic; this is a core requirement."
    print(f"[{msg1.name}]: {msg1.content}")
    reply1 = await ltm_agent_active(msg1)
    # The Agent, during its thinking process here, will determine that "core requirement" is important information and call the record_to_memory tool
    print(f"[{reply1.name}]: {reply1.content}")

    print("\n" + "="*20 + " Simulating a new session " + "="*20 + "\n") # "模拟一次新的会话" -> "Simulating a new session"
    await ltm_agent_active.memory.clear()

    # Conversation two: Agent autonomously decides to retrieve information
    msg2 = Msg("user", "I forgot, what was the writing style of our course again?", "user") # "我忘了，我们课程的写作风格是什么来着？" -> "I forgot, what was the writing style of our course again?"
    print(f"[{msg2.name}]: {msg2.content}")
    reply2 = await ltm_agent_active(msg2)
    # The Agent, during its thinking process here, will first call retrieve_from_memory(query="writing style"), and then generate an answer based on the retrieval result
    print(f"[{reply2.name}]: {reply2.content}")

await run_ltm_active_test()
```

In this way, memory is no longer data "fed" to the Agent from the outside, but rather internal knowledge that it actively acquires, stores, and maintains. This allows the Agent to evolve from a simple "tool" into a true "partner."

> **Further reading: Cost-benefit analysis**  
>
> You might think that vector-based retrieval and active memory management introduce Embedding model calls, vector database queries, and additional LLM inference (to decide whether to call a tool), which would increase cost and latency.  
>
> However, we cannot simply compare the cost of "one high-quality output" with "one low-quality output." Because if a single call cannot effectively solve the problem (e.g., forgetting a critical requirement), then no matter how low its cost, it is a waste.  
>
> A fairer comparison is: what is the total cost of both paths to obtain a "usable" answer?  
> * Path A (no long-term memory): One call, an incorrect answer (problem not solved). You have to manually remind, then call again to solve the problem.  
> * Path B (with long-term memory): One call (including retrieval), directly get the correct answer (problem solved).  
>
> From this perspective, the investment in a memory system is a necessary investment to ensure output quality and avoid repeated, ineffective attempts.

#### 6.3.5 Building short-term and long-term memory systems

Through the combination of the above strategies, you have built a complete memory system for the Agent, which can be clearly divided into two parts:

* Short-term memory: Based on a conversational buffer, managed through truncation or summarization strategies. Its core responsibility is to maintain the coherence of the current conversation. For example, remembering your recently stated specific requirement about "adding a case to Chapter Two."  
* Long-term memory: Based on a vector database and tool-based calls. Its core responsibility is to persistently store critical information and support intelligent retrieval across sessions. For example, remembering that the core goal of the entire course project is "to design for beginners, with a humorous and engaging style."

An Agent with memory is no longer a cold, one-off Q&A machine. It can learn from experience, remember your preferences, understand long-term context, and ultimately evolve from a simple "tool" to a true "partner."

> **Practical application and usage recommendations**  
>
> **I. Quickly introduce memory capabilities**  
>
> You can leverage mature open-source frameworks or platforms to quickly add memory capabilities to your Agent.  
> * AgentScope: As shown in this course, AgentScope provides InMemoryMemory as basic short-term memory, and Mem0LongTermMemory (integrated with Mem0) as an out-of-the-box long-term memory solution.  
> * Mem0: An open-source intelligent memory layer specifically designed for AI applications, which encapsulates complex logic such as vector retrieval and memory conflict handling, providing powerful underlying support.  
> * LangChain Memory: The powerful Agent development framework LangChain offers rich built-in Memory modules, including ConversationBufferMemory (buffer), ConversationSummaryMemory (summary), and VectorStoreRetrieverMemory (vector retrieval), allowing you to flexibly combine them according to your needs.  
> * Alibaba Cloud Model Studio Platform: For teams looking for quick validation or those without a technical background, the Alibaba Cloud Model Studio platform provides a visual Agent building process, where you can enable long-term memory functionality for your Agent with simple configurations.  
>
> **II. Memory usage recommendations**  
>
> * Selective memory: More memory is not always better. Accumulating a large amount of low-value or noisy information can interfere with subsequent retrieval effectiveness. You should establish an admission mechanism for memory writing, for example, only writing when the user explicitly requests it ("Please remember...") or when the information's importance exceeds a certain threshold. The agent_control pattern is a good way to achieve this.  
> * Continuous governance: Memory is a dynamic data asset that requires a continuous governance mechanism, including regularly cleaning outdated information, merging duplicate entries, verifying factual accuracy, and providing users with an interface to actively manage their own memories (view, modify, delete).  
> * Scenario-based application: Different business scenarios have different memory needs. For example, in a course document workflow requiring consistent style, personalized preferences should not be recorded; but for product factual information (such as API parameters, functional limitations), it can be recorded and regularly reviewed for validity to ensure the accuracy of content generated by the Agent.

### 6.4 Summary

Let's review what you've learned in this section:

* Root cause of the problem: Statelessness: LLMs themselves have no memory; each call is independent. Naively passing the complete history leads to excessively long contexts and uncontrolled costs.  
* Short-term vs. long-term memory: You can manage short-term memory through "truncation" and "summarization" strategies to maintain current conversation coherence; you can build long-term memory through "vector-based retrieval" to enable cross-session knowledge storage and access.  
* Active memory management: By providing the Agent with memory tools like save, recall, update, you can transform it from passively receiving context to an intelligent agent capable of actively managing and utilizing its own memory, achieving true learning and growth.  
* Best practices for memory: A powerful memory system needs effective governance. You should selectively write, continuously clean, and update memories, and decide what to remember and what not to remember based on specific business scenarios (such as course writing).

## 7 Evaluation-driven development

### 7.1 Why "feeling okay" is unreliable

You just deployed the first version of your "Course Writing Agent." When testing it locally with a few examples, it seemed "pretty good." But after going live, user feedback was disappointing. Some complained that the explanations of technical concepts were inaccurate, others found the responses too verbose, and some encountered formatting errors where code examples couldn't run.

You immediately tried to fix it, for example, by adjusting the prompt to make the Agent's explanations "more accurate." After the changes, you re-entered the topic "Introduction to Python's for loop," quickly scanned the generated content, and felt "this time it's written pretty well, the language is smooth." But when you deployed it online, new problems emerged. You were stuck: what exactly was the problem? Did the recent changes optimize or degrade overall performance?

> For example, you found that when the Agent explained "overfitting" in machine learning, its examples were too academic and not accessible enough. So you gave the Agent an instruction:  
>
> `...when explaining complex concepts, please use everyday analogies...`  
>
> After running, it indeed used the analogy of "memorizing answers for an exam instead of truly understanding the knowledge" to explain overfitting, which worked well. But you soon found that when generating a course on "Pandas data filtering," it awkwardly inserted an inappropriate analogy, making a simple operation complex and difficult to understand.

### 7.2 If it cannot be measured, it cannot be improved

The fundamental problem you encountered is the lack of an objective, quantifiable standard. The most direct idea, which you are currently doing, is to manually test a few cases and judge based on subjective feeling. But this "feeling good" approach quickly exposes its inherent flaws:

* Difficult to quantify: "Feeling better" cannot serve as a basis for engineering decisions. You can't know if this improvement was 10% or 20% better than last time.  
* Lack of standards: What you consider "examples too complex" today might be seen as "deep content" if you're in a different mood tomorrow. Different testers and different times can lead to shifting evaluation standards.  
* Irreproducible: You cannot systematically run regression tests to ensure new changes haven't broken previously good performance. When you fix the "inappropriate analogy" problem, you cannot guarantee that a previous "clear explanation" advantage hasn't been accidentally compromised.

Why is this the case? It stems from how Agents work. The generation process of LLMs is probabilistic, and the models themselves lack a "self-correction" mechanism. Even minor adjustments to your prompt can trigger unpredictable "butterfly effects" in a complex system.

Since debugging by feeling is not feasible, you naturally think of another approach: establish a systematic evaluation framework, using data rather than feelings to drive development. This is like preparing for an exam; you can't just rely on "feeling like you've learned it," but need to objectively test your mastery by doing practice papers.

This is evaluation-driven development. It elevates evaluation from the end of the development process to a core position that determines direction.

This philosophy is based on three interconnected principles:

* Evaluation, or your "taste" for good and bad, determines the upper limit of product capability.  
* What can be measured can be effectively improved.  
* The faster and more accurate the measurement feedback, the higher the efficiency and effectiveness of improvement.

### 7.3 Two evaluation methods: From macro to micro

To build an effective evaluation system, you need to examine your Agent from two dimensions: end-to-end evaluation and white-box evaluation.

#### 7.3.1 Evaluation method one: End-to-end evaluation

End-to-end evaluation focuses on the final output of the system. It answers the most important question: "Is the course generated by this Agent useful for users?"

##### 7.3.1.1 Iterative establishment of evaluation criteria

For complex Agent systems, you cannot predefine all perfect evaluation metrics before the project begins. The correct approach is to embrace iteration. Evaluation is important, but getting started quickly is more important:

1. Rapid prototyping: First build a Minimum Viable Product (MVP).  
2. Observe problems: Run it in a real scenario and observe where it makes mistakes.  
3. Summarize key points: From these errors, identify the critical points that need to be prioritized for evaluation at the current stage and convert them into evaluation metrics.

> For example, in the first version of content generated by your course writing Agent, you found that code examples often lacked necessary import statements, making them unable to run directly. This is a clear, high-priority error. Thus, you established the first evaluation metric: "Code executability"—all code blocks must be self-contained and syntactically correct. Then, you found that the Agent, in an attempt to make the language more vivid, overused metaphors, which instead made core concepts vague. So, you added a second evaluation metric: "Explanation clarity," with a clear requirement to avoid inappropriate metaphors.

This loop repeats, and your evaluation system becomes increasingly perfect and precise as the Agent evolves. The figure below shows this complete closed-loop process:

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
                                             [Aggregate score]
                                                     │
                                                     v
                                              [Improve agent] ──► (back to MVP)
```

As shown, starting from MVP, through real operation, error observation, metric refinement, combined with both objective and subjective evaluation methods, ultimately leads to continuous improvement of the Agent. Next, we delve into how to design these two types of metrics.

##### 7.3.1.2 Designing evaluation metrics: Objective and subjective

A comprehensive evaluation system needs to include both objective and subjective metrics.

| Type | Description | "Course writing Agent" case |
| :--- | :--- | :--- |
| **Objective metrics** | Can be directly judged by code rules, results are deterministic. | • **Code executability**: Can the generated code snippets be successfully run by a Python interpreter?<br>• **Format check**: Does it include all required sections like "pain points," "solutions," "summary"?<br>• **Word count limit**: Is the length of each section between 300-500 words? |
| **Subjective metrics** | Involve semantics, logic, and quality, usually requiring stronger intelligence to judge. | • **Content accuracy**: Are there factual errors in the explanation of technical concepts?<br>• **Teaching effectiveness**: Do the introduced cases stimulate learning interest? Are explanations from simple to complex?<br>• **Language style**: Does it conform to the "rigorous, precise, calm" course setting? |

But the core problem here is: who defines these metrics? Especially subjective metrics, such as "teaching effectiveness" and "language style," what do they really mean?

**The key is that evaluation metrics must be led by the most senior business experts in your team.** For your "course writing Agent," these people are top instructional designers and senior lecturers. However, there is a common misconception to avoid here:

Many teams' approach is that technical staff first build an initial version of the Agent, and when they find the effect is not ideal, they then go to business experts to "extract knowledge"—asking them, "What do you think makes a good course?" Then the technical team goes back and tries to translate these vague descriptions into evaluation rules. This model is often inefficient because:

* Experts lack motivation to participate: They are positioned as "knowledge providers" rather than co-builders of the project. Without seeing a direct link to their business goals, their enthusiasm for participation is low.  
* Knowledge translation loss: Technical staff find it difficult to fully understand experts' implicit knowledge, and key elements are easily misinterpreted or overlooked during translation.  
* Long feedback cycle: By the time the technical team implements and then returns for verification, they have often taken a detour, requiring significant rework.

**The correct approach is to empower business experts as the owners of the evaluation system from day one of the project, with the technical team acting as facilitators.** Specifically:

1. **Mobilize participation with business goals**: Don't say, "We need your help to define evaluation metrics." Instead, say, "This Agent will help us achieve [specific business goal, such as 'reduce course production time from 2 weeks to 3 days while maintaining over 90% user satisfaction']. As a guardian of course quality, you need to define what constitutes an 'acceptable quality baseline'." When experts see this directly relates to business outcomes they care about, their willingness to participate will significantly increase.

2. **Provide structured tools to lower participation barriers**: The value of the technical team lies in providing scaffolding, not doing the work for them. For example:  
   ○ **Evaluation metrics workshop**: Organize experts for structured dialogue, guiding them with questions like "If you could only use three metrics to judge course quality, which three would you choose?"  
   ○ **Rating scale templates**: Provide fill-in-the-blank templates for "1-5 points, what specific characteristics correspond to each score?" so experts fill it out rather than describing from scratch.  
   ○ **Case annotation tools**: Allow experts to directly annotate "what's good, what's bad" on actual Agent outputs, and then reverse-engineer rules from that.  

> For example, when an expert annotates a lesson plan with "feels too bland," the technical facilitator needs to ask: 'Bland' means it lacks relatable pain points? This can then refine into the metric 'relevance of opening case'.  
>
> When an expert says 'students won't understand,' dig deeper: is the concept jump too fast, for example, talking about 'lists' without explaining 'variables' first? This can then be transformed into the metric 'logical progression of theory'.  
>
> Through this dialogue, you can encode the expert's 'taste' into measurable evaluation items.

3. **Establish continuous collaboration mechanisms**: Evaluation standards are not one-time documents but living documents that evolve with Agent capabilities and business needs. In weekly review meetings, experts review data, the technical team adjusts the system, and both parties jointly decide the next optimization direction.

In this way, experts are no longer objects from whom "knowledge is extracted," but true owners of the evaluation system. Their "teaching intuition" (i.e., "tacit knowledge") is systematically transformed into executable and iterative evaluation rules with the aid of structured tools.

##### 7.3.1.3 Improving the stability of subjective evaluation

After defining the metrics, the next step is how to conduct the evaluation. You have two options: manual evaluation and automated evaluation with LLMs (LLM-as-a-Judge).

*   **Manual evaluation**: Human experts score according to evaluation criteria. This is the most reliable "gold standard," especially in the early stages of a project, as it helps you calibrate the definitions of "good" and "bad." However, its drawbacks are high cost, slow speed, and difficulty in scaling up and frequent execution.

*   **LLM-based automated evaluation**: Train or guide another LLM to act as an "evaluation expert," automatically scoring the "course writing Agent's" output based on your defined metrics and scoring rubrics.

To make LLM evaluation more stable, you need to break down a vague evaluation goal (e.g., "good content quality") into a series of specific, verifiable details. Then, let the LLM judge each item individually, and finally aggregate the scores according to rules.

> For example, evaluating the "content quality" generated by the "course writing Agent" can be broken down into:
> 1.  **Introduction of pain points**: Does it begin with an everyday, concrete pain point? (Yes/No)
> 2.  **Theoretical elevation**: Does it clearly point out the limitations of preliminary solutions and introduce core theories? (Yes/No)
> 3.  **Relevance of code examples**: Are the provided code examples closely related to the theory explained and sufficiently simplified? (Yes/No)

**But you must be wary that LLM evaluation itself may be biased.**

> **Further reading: LLM evaluator's "mindset"**
>
> Using an LLM as an evaluator is like hiring a knowledgeable expert who has personal biases. Its own training data determines its "taste."
> - **Style bias**: It might prefer a certain coding style (e.g., advocating method chaining), thereby giving lower scores to other equally correct but stylistically different code.
> - **Length bias**: It might tend to believe that longer, more detailed explanations are "more complete," thus unfairly penalizing answers that are "concise but to the point."
> - **"People-pleaser" bias**: Some models tend to give positive feedback and avoid conflict, making it difficult to uncover real problems.
> - **Position bias**: Some studies show that when models process lists or compare multiple options, they might tend to choose options at the beginning or end. When designing evaluation prompts, consider randomizing the order of the content being evaluated to mitigate the impact of this bias.
>
> Therefore, the best practice is: **use human experts for evaluation in the early stages to establish a high-quality "gold test set." Then, use this test set to "calibrate" your LLM evaluator**, checking its scoring consistency with human experts. In subsequent development, regularly use manual sampling to ensure the automated evaluation system hasn't "gone off track."

#### 7.3.2 Evaluation method two: White-box evaluation

When your Agent's process becomes complex, the drawbacks of end-to-end evaluation become apparent. For example, your "course writing Agent" might include a "concept explanation" component and a "code generation" component. If the final course score is not high, it's hard to tell whether the concept explanation was poor or the code examples were terrible.

**White-box evaluation** is designed to solve this problem. It advocates going deep inside the system to **design a separate evaluation system for key components**.

The core advantages of white-box evaluation are:
*  **Clear signals**: Provides unambiguous improvement signals, allowing you to focus on the true bottlenecks.
*  **Rapid iteration**: Only needs to test individual components, without running the entire complex process, greatly shortening the verification cycle.
*  **Precise optimization**: Whether adjusting hyperparameters or replacing external services, their effects can be precisely measured, making decisions data-driven.

> In this way, you can:
> - **Individually evaluate the "concept explanation" component**: Build a test set containing a series of technical terms (e.g., "list comprehension," "decorators"), and then only evaluate whether the text explanations generated by this component are clear and accurate.
> - **Individually evaluate the "code generation" component**: Build a test set containing a series of task descriptions (e.g., "generate a function to merge two dictionaries"), and then only evaluate whether the generated code runs correctly and follows best practices.
>
> The advantage of this method is that it provides unambiguous improvement signals, allowing you to focus on true bottlenecks and achieve fast, precise optimization.

In practice, you don't need to aim for a fully automated, comprehensive, multi-dimensional evaluation system from the start. For example, when dealing with code correctness, you can begin with the simplest method: manually copy and run the code a few times. Then, gradually upgrade to writing a script that automatically executes code and catches errors. Finally, you can build a complete evaluation pipeline with various metrics (style, efficiency, correctness). The ultimate choice depends on your specific needs, budget, and acceptable error rate.

### 7.4 Evaluation frameworks

You can build an evaluation workflow that meets your business needs by writing code rules and combining them with LLMs. Alternatively, you can leverage mature community evaluation frameworks to accelerate this process. In addition to AgentScope, the RAGAS framework mentioned in the RAG evaluation section also provides end-to-end and component-level evaluation capabilities for Agents. Furthermore, you can choose DeepEval as an LLM evaluation framework.

#### 7.4.1 Practice: AgentScope evaluation framework demo

To run a minimal "evaluation-driven development" end-to-end example, you need to understand the following modules:

- **agentscope.evaluate**: `Task` (task definition), `MetricBase/MetricResult/MetricType` (custom metrics), `SolutionOutput` (unified representation of solutions).
- **pydantic**: Used to define structured output models, improving evaluation stability (allowing models to output parsable numerical values).
- **agentscope.init (optional)**: Used to enable tracing, sending execution traces to Studio or an OTLP-compatible backend.

> Note: The teaching-oriented "minimal runnable" version does not rely on `GeneralEvaluator/RayEvaluator` or other more complete evaluators; we can directly form a compact loop with `Task + Metric`. If you need to run large-scale benchmarks or distributed evaluations, then introduce evaluators and storage modules.

The following example demonstrates "drafting a Pandas data analysis course lesson" and performs programmable objective scoring of the draft. Key points:
- Structured output (`title/learning_objectives/code_example/quiz`), improving evaluation stability.
- Fine-grained subjective scoring (LLM-as-Judge): evaluates five dimensions (language clarity/ambiguity, factual correctness, consistency, redundancy (lower redundancy, higher score), readability) on a 1-5 scale; uses structured output for stable scoring.
- Tracing (optional): Set `AGENTSCOPE_STUDIO_URL` (to connect to AgentScope Studio) or `OTEL_TRACING_URL` (to connect to any OTLP-compatible backend) to automatically enable tracing; the example runs normally if not set.

*Figure (translated): example evaluation pipeline — a generation agent drafts a chapter, a review agent scores it across five dimensions.*

```text
[Course benchmark: pandas task] -> [Generation agent] -> [Chapter draft: title / objectives / code / quiz]
                                                                 |
                                                                 v
                                                          [Review agent] -> [Five-dimensional scoring] -> [Results summary]
```

```python
# End-to-end evaluation for educational course writing (pandas): two lesson drafts + five-dimension LLM scoring
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

assert os.getenv("DASHSCOPE_API_KEY"), "Please set DASHSCOPE_API_KEY in your environment first"

# (Optional) Enable tracing: prioritize connecting to Studio; otherwise, connect to any OTLP-compatible backend
studio_url = os.getenv("AGENTSCOPE_STUDIO_URL")
otel_url = os.getenv("OTEL_TRACING_URL")
if studio_url:
    agentscope.init(studio_url=studio_url)
elif otel_url:
    agentscope.init(tracing_url=otel_url)

# 1) Define a minimal benchmark (two lesson writing tasks)
COURSE_BENCHMARK = [
    {
        "id": "pandas_intro",
        "prompt": (
            "Please write a draft for an introductory lesson on pandas DataFrame in concise English. The output must include structured fields:\n"
            "- title: Lesson title;\n"
            "- learning_objectives (3-5 items, each no more than 25 characters);\n"
            "- lesson_content: At least 180 characters of main lesson text, including an opening guide, explanation of core concepts, step-by-step example explanation, and a class summary;\n" 
            "- code_example: Minimal runnable pandas code with comments (demonstrating `import pandas as pd`, `read_csv` or DataFrame creation, and `head()` usage example);\n"
            "- quiz: A single-choice question with options, no less than 4 options, and marking the correct answer.\n"
            "lesson_content should emphasize common pitfalls for beginners and correspond with code examples."
        ),
        "tags": {"topic": "intro", "min_objectives": 3},
    },
    {
        "id": "pandas_groupby",
        "prompt": (
            "Please write a draft for a lesson on pandas groupby and aggregation in concise English. The output must include structured fields:\n"
            "- title: Lesson title;\n"
            "- learning_objectives (3-5 items, each no more than 25 characters);\n"
            "- lesson_content: At least 200 characters of main lesson text, first explaining the groupby idea, then breaking down aggregation steps with a real business context, including the difference between agg and describe, and adding common error tips;\n"
            "- code_example: Minimal runnable pandas code with comments, demonstrating at least one groupby and one agg or describe;\n"
            "- quiz: A single-choice question with options, no less than 4 options, and marking the correct answer.\n"
            "lesson_content should provide step-by-step operational explanations and extended thinking."
        ),
        "tags": {"topic": "groupby", "min_objectives": 3},
    },
]

# 2) Define structured output model
class CourseDraft(BaseModel):
    title: str = Field(description="Lesson title")
    learning_objectives: List[str] = Field(description="Learning objectives (3-5 items)")
    lesson_content: str = Field(description="Main lesson text, at least 180 characters for the detailed draft")
    code_example: str = Field(description="Minimal runnable pandas code example")
    quiz: str = Field(description="A multiple-choice question (brief)")

# 3) Define five-dimension LLM scoring structure and metrics
class EvalScore(BaseModel):
    clarity: int = Field(description="Language clarity/ambiguity, 1-5 (higher = clearer)")
    factual_correctness: int = Field(description="Factual correctness, 1-5 (higher = more correct)")
    consistency: int = Field(description="Consistency in expression, 1-5 (higher = more consistent)")
    redundancy: int = Field(description="Redundancy in expression, 1-5 (higher = more concise)")
    readability: int = Field(description="Readability, 1-5 (higher = more readable)")
    overall: Optional[float] = Field(default=None, description="Optional, overall score 0-1")
    feedback: str = Field(description="One-sentence improvement suggestion")

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
        # Provide clear scoring criteria, requiring strictly structured output
        prompt = (
            "As an educational content reviewer, please evaluate the following lesson draft across five dimensions on a 1-5 scale, and provide a one-sentence improvement suggestion.\n"
            "Scoring dimensions:\n"
            "1) clarity: Language clarity/ambiguity (higher score = clearer);\n"
            "2) factual_correctness: Factual correctness (higher score = more correct);\n"
            "3) consistency: Consistency in expression (higher score = more consistent);\n"
            "4) redundancy: Redundancy in expression (higher score = more concise);\n"
            "5) readability: Readability (higher score = more readable).\n"
            "Scoring reference: 5 points only for excellent drafts requiring almost no modification; 4 points for excellent but still needing minor adjustments; 3 points for basically acceptable but with obvious problems; 2 points or less means significant modification is needed. If lesson_content is less than 180 characters, lacks step-by-step explanations, or does not cover common pitfalls, please set the upper limit for clarity and readability scores to 3 points and explain in the feedback.\n"
            "Check points: Does the number of learning objectives meet requirements, does lesson_content include introduction → concept → example → summary and correspond with code, is the code example runnable and commented, is the quiz clearly marked with the correct answer.\n"
            "Only output structured fields: clarity, factual_correctness, consistency, redundancy, readability, overall(optional), feedback.\n\n"
            f"Title: {draft.get('title','')}\n"
            f"Learning objectives: {draft.get('learning_objectives', [])}\n"
            f"Content:\n{draft.get('lesson_content','')}\n\n"
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
                ground_truth=1.0,  # Expect all to pass objective checks
                tags=item["tags"],
                metrics=[],  # Inject LLM scoring metrics later
                metadata={},
            )
        )
    return tasks

# 5) Create a minimal agent (real DashScope API call)
agent = ReActAgent(
    name="Friday",
    sys_prompt=(
        "You are an educational course author, specializing in pandas data analysis. Please write a lesson draft in concise English,"
        "strictly outputting structured fields: title, learning_objectives(list[str]), lesson_content(str), code_example(str), quiz(str)."
        "lesson_content should be at least 180 characters, including an introduction, concept explanation, step-by-step examples, common error tips, and a summary."
    ),
    model=DashScopeChatModel(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
        model_name="qwen-plus",
        stream=False,
    ),
    formatter=DashScopeChatFormatter(),
    enable_meta_tool=False,
)

# 5.1) Review Agent (can reuse the same model as generation)
evaluator = ReActAgent(
    name="Evaluator",
    sys_prompt=(
        "You are a strict educational content reviewer, outputting structured scores (1-5) and a one-sentence suggestion according to the scoring criteria,"
        "do not output any content other than the structured output."
    ),
    model=DashScopeChatModel(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_http_api_url = os.getenv("DASHSCOPE_BASE_HTTP_API_URL"),
        model_name="qwen-plus",
        
        stream=False,
    ),
    formatter=DashScopeChatFormatter(),
    enable_meta_tool=False,
)

# 6) Minimal evaluation loop
async def run_minimal_eval() -> None:
    tasks = build_tasks()
    # Inject five-dimension LLM scoring metrics
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
            f"\n[{task.id}] Draft content:\n"
            f"{json.dumps(draft, ensure_ascii=False, indent=2)}"
        )

        solution = SolutionOutput(success=True, output=draft, trajectory=[])
        metric_res = await task.metrics[0](solution)
        scores.append(metric_res.result)
        print(f"[{task.id}] score={metric_res.result:.2f} ({metric_res.message})")

    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"\nAverage score: {avg:.2f}")

# Call the asynchronous function directly in a Jupyter Notebook
await run_minimal_eval()
```

> **Summary**: The code above demonstrates the minimal closed loop of "evaluation-driven development"—encoding the objective elements of a "good lesson" into executable checks using `Task + Metric`, and then running them end-to-end with a real API for quantitative scoring. You can try: fine-tuning `sys_prompt`, changing `model_name` or temperature, or improving metrics (e.g., checking if code runs, if it includes links to output screenshots), then repeat the evaluation and observe if the score improves. If `AGENTSCOPE_STUDIO_URL` or `OTEL_TRACING_URL` is set, you can also view the time consumption and trace details of models/tools/formatters in the tracing backend.

Ultimately, transitioning from relying on subjective feelings to establishing an evaluation system that combines "end-to-end" and "white-box" approaches is the necessary path to building high-level Agents. This process essentially transforms vague "good" and "bad" standards into clear, executable engineering problems. Evaluation is not the end of development but the beginning of optimization. A powerful evaluation system will become your most reliable compass when exploring the boundaries of Agent capabilities.

### 7.5 Summary

Let's review what you've learned in this section:

- **Beyond subjective feelings**: Agent optimization should move away from the "feeling good" pattern and towards evaluation-driven development based on objective data. This is a prerequisite for rigorous, controllable optimization.
- **Experts define standards**: Evaluation metrics, especially subjective ones, should be primarily defined by senior business experts, translating their implicit knowledge into clear, measurable rules.
- **Beware of model bias**: When using LLMs for automated evaluation, you must be wary of their inherent biases (e.g., style, length) and regularly calibrate them with "gold test sets" from human experts.
- **Combine end-to-end and white-box approaches**: Use end-to-end evaluation to grasp the Agent's overall user value, while leveraging white-box evaluation to delve into key components, precisely identifying and resolving performance bottlenecks.
- **Iterative refinement**: A powerful evaluation system evolves gradually rather than being built all at once. Start with the most critical and easiest parts to implement, and iterate continuously.

## 8 Summary

At this point, you have completed all the content of this chapter. Let's review and systematically organize the Agent knowledge you've just built from a more macroscopic perspective.

### 8.1 Everything starts with "user intent"

You started with a common pain point: a single LLM call, while capable of language tasks, often struggles when faced with complex tasks requiring multiple steps and interaction with the external world.

To solve this problem, your goal is to build a system that can stably and reliably understand and fulfill true user intent. This is where the value of an Agent lies. If an LLM is a smart "brain" confined in a "black box," then what you've learned in this chapter is how to build a complete "engineering system" around this "brain," enabling it to accomplish complex real-world tasks.

### 8.2 Core methodology: Context engineering

In exploring how to build Agents, you learned various engineering techniques. Now, let's examine these techniques from a core engineering perspective: **Context Engineering**.

When you first encountered LLMs, you learned about **Prompt Engineering**, whose core is to enable the model to deliver the best output in a **single interaction** through carefully designed instructions.

Now you are dealing with complex tasks that span **multiple interactions** and involve **multiple external information sources**. At this point, your focus shifts from "writing a good Prompt" to systematically providing the most sufficient and precise **context** for every decision the model makes. This is context engineering.

From this perspective, as the designer of an Agent, you are no longer just a "questioner," but an **"information architect."** Your core task is to design processes and call tools to build a perfect **"information cocoon"** for the LLM node responsible for final decisions, containing everything needed to solve the problem—no more and no less. **The quality of the context directly determines the upper limit of the Agent's capabilities.**

Under the "context engineering" approach, the capabilities you learned in the first half of this chapter all have clear positions: they are specific means within the discipline of **"context injection"**:

- **Tool use**: Injecting real-time, deterministic information from the external world into the context.
- **Reflection**: Using the "evaluation result" of the previous step as new feedback, revising the context for the next step to guide subsequent actions.
- **Workflow**: Designing a relatively fixed task pipeline, specifying **when** and **by which node** to inject **what kind of context** into the model—like a dedicated "context manipulation" pipeline driving all subsequent steps to run stably.
- **Memory system**: Retrieving the most relevant parts from massive historical information and injecting them into the current context to provide references for subsequent decisions.

These capabilities do not exist in isolation but collectively serve the core goal of **"optimizing context,"** enabling the Agent to complete tasks more efficiently and reliably.

### 8.3 Quality assurance: Evaluation-driven development

Since context is key, how do you ensure the context you build is "high-quality"? The answer is: **evaluation**.

Without measurement, there is no improvement. Transforming the Agent's development process from "debugging by feeling" to "data-driven" is crucial for its successful deployment in a production environment. To this end, you learned three complementary evaluation dimensions:

- **End-to-end evaluation**: It answers the most important question: *"Did the Agent ultimately fulfill the user's intent?"* This is a macroscopic assessment from a business perspective.
- **White-box evaluation**: It helps you pinpoint the problem: *"Did the tool call fail, or was memory retrieval inaccurate?"* This is a microscopic diagnosis that delves into the internal system, focusing on each "context injection" node.
- **Continuous iteration**: Integrating evaluation into every aspect of development, forming a data-driven, continuously optimizing closed loop. This ensures that the Agent's capabilities can evolve with business development and data accumulation.

By establishing such a **"macro + micro + iterative"** evaluation system, you gain a flywheel that drives continuous optimization of the Agent. More importantly, this system is not limited to context engineering but serves as the **"feedback nervous system"** for the entire Agent system, permeating subsequent autonomous planning and multi-agent collaboration.

### 8.4 Outlook: More powerful autonomy

So far, the "context engineering" we've discussed primarily focuses on building an Agent with exceptionally strong **"individual capabilities"** and clearly controllable behavior boundaries around a single task. You have mastered the basic paradigm of enabling it to use various tools, possess memory, and learn to reflect. This engineering approach, centered on fixed workflows, is already very powerful and represents the most mainstream and pragmatic implementation paradigm in the industry today.

But the evolution of single Agents does not stop there. The next stage of its development is to grant it greater **"autonomy"**:

- **Autonomous planning**: The Agent no longer strictly executes your preset static workflow, but, like a project manager, autonomously plans, decomposes, and executes tasks based on the ultimate goal. This means the Agent gains the ability to dynamically adapt to problems and autonomously generate solutions.
- **Multi-agent systems**: Building further on autonomous planning, this involves having multiple Agents with autonomous decision-making capabilities form a team, allowing them to autonomously divide labor, initiate collaboration, exchange information, and integrate intermediate results around a common goal—rather than having you hardcode each collaboration process. At this point, the system's "autonomy" is no longer limited to the planning capabilities of a single Agent but is amplified into a **collective intelligence** closer to a real team through the interaction of multiple Agents.

This represents a leap in Agent systems from a mode primarily focused on engineering controllability to one of more open autonomy and emergent behavior. While the structured workflows you've learned are the most reliable foundation for current engineering practices, exploring advanced capabilities like autonomous planning and multi-agent collaboration will be key to unlocking the next phase of Agent potential.

Ultimately, you need to keep pace with the times. First, apply the context engineering and evaluation system you've learned to practice, building an Agent engineering system with fixed workflows as its skeleton, controllable behavior, and high reliability. On this foundation, under the guidance and constraints of the same evaluation and feedback mechanism, gradually introduce autonomous planning and multi-agent collaboration, allowing the system to progress towards more open autonomy and emergent intelligence while ensuring controllability.

### Final Summary

An excellent Agent system is not a single advanced technology but a combination of two complementary approaches:

1. **Engineered controllable autonomy**: Deeply understand business scenarios, translate efficient real-world processes and evaluation principles into the Agent's workflows and evaluation system, and meticulously control every aspect through context engineering to maximize the model's "individual capabilities" within clear boundaries, thereby building a reliable and controllable Agent engineering system. This is the **"engineering foundation"** at the strategic and tactical levels.
2. **Open-ended autonomous evolution**: On top of this engineering foundation, and under the constraints and guidance of the same evaluation and feedback mechanism, introduce autonomous planning and multi-agent collaboration. This allows Agents to move beyond passively executing preset processes, enabling them to plan, divide tasks, collaborate, and generate emergent behaviors around a goal, gradually raising the overall intelligence ceiling of the system while maintaining controllability. This represents **"intelligent evolution"** for the future.

By mastering these two approaches, you will have the foundation to build powerful, reliable, and continuously evolving intelligent systems. Now is the time to use them to realize your creativity and build your own AI applications, systems, and services.
