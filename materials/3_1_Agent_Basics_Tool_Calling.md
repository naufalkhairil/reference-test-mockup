# 3.1 Agent Basics & Tool Calling

## 🚄 Preface

Your FAQ bot can answer questions from the employee handbook, but it's powerless for anything outside the knowledge base: it can't search the latest materials on the internet, nor query a database. This isn't a RAG problem — it's a limitation of the LLM itself: it can only converse based on existing text and can't proactively interact with the external environment. Yet people want to use its understanding and reasoning to "command" these external tools to accomplish more complex tasks.

In this lesson, you'll start from the simplest tool function and work all the way to the industry-standard Function Calling and MCP protocol, understanding the complete mechanism of Agent tool calling.

## 🍁 Course Objectives

**You will learn:**
- Understand why an Agent can "act": the four things — tool definition → tool selection → output-format constraint → tool execution
- **Master Function Calling (key)**: the full mechanism of FC and JSON Schema design
- The ReAct framework: using the think-act-observe loop to verify tool-call results
- The MCP protocol: why it emerged, what problem it solves, and its value to developers and knowledge-service enterprises

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

## 1 Your First Tool Function
A colleague is developing an online course on "LLM Fundamentals" and wants the bot to help gather the latest teaching materials from the internet.

You'll find that the bot can only retrieve information from the company knowledge base, or answer with the LLM's world knowledge.

### 1.1 Hardcoded approach: the simplest implementation
To let the bot get information from the internet, the most direct idea is: write a web-search tool function for the bot that searches the user's question every time and sends the search results along with the question to the LLM.

Suppose you've already written a function called web_search that can look up materials via a search engine. Now, when the user makes a request, you want the model to use this function. The simplest implementation is: after receiving the request, the program "hardcodes" the execution of this function, then sends the execution result together with the original request to the LLM, and has it generate a summarizing reply.

<img src="https://img.alicdn.com/imgextra/i1/O1CN01P40EFk1LNxElRGKtA_!!6000000001288-55-tps-1092-217.svg" width="700">

```python

# 1. The user's original request
user_request = "Hi, please help me gather some of the latest materials about the Transformer model."

# 2. "Hardcoded" execution of the tool function
# The web_search function here is simulated, to focus on the core logic
def web_search(query: str):
    """Simulate a web search and return results in JSON format"""
    print(f"--- [Tool running] Searching: {query} ---")
    # In a real scenario, this would call an actual search-engine API
    return '''{
        "results": [
            {"title": "Attention Is All You Need (original Transformer paper)", "url": "https://arxiv.org/abs/1706.03762", "snippet": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks... We propose a new simple network architecture, the Transformer, based solely on attention mechanisms..."},
            {"title": "The Illustrated Transformer – Jay Alammar", "url": "https://jalammar.github.io/illustrated-transformer/", "snippet": "A visual and intuitive explanation of the Transformer model."}
        ]
    }'''

tool_result = web_search(query=user_request)

print(f"User request: {user_request}")
print(f"Tool result: {tool_result}\n")


# 3. Concatenate the user request and the tool result into one prompt and send it to the LLM
#    The goal is to have the model generate a human-friendly reply based on the structured tool output.
completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {'role': 'system', 'content': 'You are a course research assistant. Your task is to generate a friendly, clear reply to the user based on the tool execution result.'},
        {'role': 'user', 'content': f'User original request: "{user_request}"\nTool execution result: {tool_result}'}
    ]
)

# 4. Output the model's final reply
final_response = completion.choices[0].message.content
print(f"The model's final reply:\n{final_response}")
```

### 1.2 Limitation analysis: why we need a more flexible approach

Although this approach is simple and effective, it has a limitation: it only applies to the scenario of "there is exactly one tool, and it must be called on every turn." As colleagues' needs grow, your bot may need to add more tools like `search_arxiv_paper` (search papers on the academic site Arxiv), `fetch_webpage_content` (get the full text of a given webpage), etc. At that point you hit a thornier problem: how do you let the bot call tools on demand?

## 2 Intent Recognition: Let the Agent Decide Which Tool to Use
### 2.1 Fragile keyword matching
One direct idea is to write a "router" that judges the user's intent through `if/elif` structures and keyword matching.

```python
# Pseudocode: a fragile, keyword-based tool router
def route_to_tool(user_input):
    if "paper" in user_input or "arxiv" in user_input:
        return "search_arxiv_paper"
    elif "search" in user_input or "find" in user_input or "materials" in user_input:
        return "web_search"
    elif "summarize" in user_input or "content" in user_input or "http" in user_input:
        return "fetch_webpage_content"
    # ... you'd need to keep adding elif checks here
    else:
        return "no_tool_needed"
```

You can immediately see the downside of this approach. It's very **fragile and hard to maintain**. If the user says "I want to see what that paper Attention is All You Need is about," this crude router can't recognize the intent for `search_arxiv_paper` and `fetch_webpage_content`, because it contains none of the preset keywords.

### 2.2 LLM-based intent recognition
A better idea is to list all tools in the prompt and let the LLM decide which tool to call and what arguments to use. This is a simple implementation of intent recognition.

```python
def get_tool_decision_from_llm(user_request):
    from textwrap import dedent

    # Use dedent to remove the indentation added for code aesthetics,
    # to avoid passing these formatting tabs/spaces to the LLM
    prompt = dedent(f"""
        You are the routing module of an intelligent assistant. Your task is to, based on the user's request, choose the most suitable tool from the tool list below to solve the problem, and give the arguments.

        [Available tool list]
        1. web_search: for searching general information on the internet.
        2. search_arxiv_paper: for searching academic papers on Arxiv.org.
        3. fetch_webpage_content: for fetching the webpage content of a given URL.

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
        temperature=0.0 # use a low temperature for a more deterministic decision
    )
    decision = completion.choices[0].message.content
    return decision

# --- Test case ---
request = "Help me find that classic Transformer paper, titled 'Attention Is All You Need'"
decision = get_tool_decision_from_llm(request)
print(f"User request: \"{request}\"")
print(f"Model decision: {decision}\n")
```

## 3 Ensuring Reliability: Structured Output
### 3.1 Why structure is needed
Now you've solved the "which tool to call" problem; the next step is to parse and execute the LLM's decision in code. However, you'll find that the LLM's result is mixed with natural language and has no fixed format:

*   `I'll use the search_arxiv_paper tool to search for the classic Transformer paper titled "Attention Is All You Need".`
*   `OK, the tool is search_arxiv_paper`
*   `search_arxiv_paper(query="Attention Is All You Need")`

This is because the LLM tends to generate diverse text, whereas what you need is an easy-to-parse, deterministic data format. To solve this, you need to turn it around and require the model to output in a strict, preset structured format.

JSON is exactly such an ideal format. A clearly-defined JSON output is unambiguous and easy to parse:
```json
{
  "tool_name": "search_arxiv_paper",
  "parameters": {
    "query": "Attention Is All You Need"
  }
}
```

It clearly defines "what to do" (tool_name) and "what to do it with" (parameters). Any programming language can easily parse this key-value structure.

### 3.2 Building a "guide-validate-retry" closed loop

The next task is how to ensure the model can stably and strictly output according to the JSON structure you defined. To achieve this, you need to establish a clear process.

1.  **Define the structure**: first, precisely define your expected output structure. You can use JSON Schema (a language for describing JSON data structures), or define a data model in Python code via libraries like Pydantic. This Schema specifies which fields the final product must contain and each field's type — the cornerstone of the whole process.

2.  **Build the prompt**: in your prompt, besides giving the task instruction, you should also attach the complete Schema definition and provide one or two output examples that fully conform to that Schema. Through this "instruction + example" approach, the model can more thoroughly understand your requirements.

3.  **Validate and retry**: after receiving the model's output, the program must strictly validate it with the same Schema. If validation fails, the program should capture the validation error message and send it, together with the model's previous erroneous output, back to the model as correction clues, asking it to regenerate.

<img src="https://img.alicdn.com/imgextra/i4/O1CN01LbicK41tPxucZHDsd_!!6000000005895-55-tps-1259-245.svg" width="700">

```python
import json
from textwrap import dedent
from typing import Union, Literal
from pydantic import BaseModel, Field, ValidationError, TypeAdapter

# 1. Define Pydantic parameter models for the course-research-related tools
class WebSearchParams(BaseModel):
    query: str = Field(description="The keyword used for the web search.")

class SearchArxivParams(BaseModel):
    query: str = Field(description="The paper title or keyword used to search on Arxiv.org.")

# 2. Define tool-call models, binding the tool name to its corresponding parameter model
class WebSearchCall(BaseModel):
    tool_name: Literal["web_search"]
    parameters: WebSearchParams

class SearchArxivCall(BaseModel):
    tool_name: Literal["search_arxiv_paper"]
    parameters: SearchArxivParams

# Use a Union type to indicate the model's final decision is one of these two calls
ToolCall = Union[WebSearchCall, SearchArxivCall]

# 3. Build the prompt, including clear instructions, tool definitions, and an example
def build_prompt(user_request: str) -> str:
    return dedent(f"""
        Your task is to, based on the user's request, choose the most suitable tool from the available tool list and output the call information in strict JSON format.

        # Available tools:
        - `web_search(query: str)`: use when you need to search general information, news, or non-academic content.
        - `search_arxiv_paper(query: str)`: use when you need to search academic papers, especially from Arxiv.org.

        # Output format requirements:
        You must output strictly in the following JSON structure, without any extra natural-language explanation.

        {{
        "tool_name": "tool name",
        "parameters": {{
            "param name": "param value"
        }}
        }}

        # Example:
        User request: "Any fun news in the AI field recently?"
        Your output:

        {{
        "tool_name": "web_search",
        "parameters": {{
            "query": "latest news in the AI field"
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
        # This is an API call to the LLM service; for course generality the concrete implementation is omitted
        # You can replace it with your own code, e.g. client.chat.completions.create(...)
        response = client.chat.completions.create(
            model="qwen-plus", messages=messages, temperature=0
        )
        raw_output = response.choices[0].message.content

        try:
            # Parse and validate
            data = json.loads(raw_output.strip('```json').strip('```'))
            # Validate the parsed data with the Pydantic model
            validated_data = adapter.validate_python(data)
            return validated_data.model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            # If it fails, add both the error message and the raw output to the conversation history so the model can correct itself
            messages.extend([
                {'role': 'assistant', 'content': raw_output},
                {'role': 'user', 'content': f"Format error: {e}. Please re-output strictly in JSON format"}
            ])

    return None

# Usage
# Assume the client variable is initialized elsewhere
user_request = "Help me find that classic Transformer paper, titled 'Attention Is All You Need'"
result = get_structured_output(user_request)

if result:
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

## 4 The Mainstream Approach: Function Calling
### 4.1 How Function Calling works
The "intent recognition -> structured output -> validate and retry" you just implemented manually is a robust tool-calling flow, but its full implementation is fairly complex. To simplify development, many LLM service providers (Alibaba Cloud, OpenAI, Anthropic, Google, etc.) have built this capability into their APIs — this is **Function Calling** or **Tool Calling**.

Taking the OpenAI SDK's function calling as an example:

*   **Tool Definition**: you define the available tools in the API's `tools` parameter, using JSON Schema to describe each tool's `name`, `description`, and `parameters` (the structure of input parameters the function needs).

*   **Call Decision**: based on the user input and the tool definitions, the model automatically decides whether it needs to call a tool. If so, the model returns a `tool_calls` field in its response, containing the function name to call and a schema-conforming argument JSON.

*   **Execute & Return**: **You need to**:
    1. Parse the function name and arguments in `tool_calls`
    2. Actually execute the corresponding function in your code
    3. Wrap the function execution result as a `role: "tool"` message
    4. Call the API again, sending the tool execution result to the model
    5. Based on the result returned by the tool, the model generates the final user reply

<img src="https://img.alicdn.com/imgextra/i4/O1CN01JlDfvF1irTxlt4Wdk_!!6000000004466-55-tps-848-884.svg" width="700">

Let's understand this flow through a complete code example:

```python
import json
# 1. Define the tool list, containing a JSON Schema description for each function
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_arxiv_paper",
            "description": "Search academic papers on Arxiv.org",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The paper's title or keyword"},
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
# 3. Check whether the model decided to call a tool, and execute it
if response_message.tool_calls:
    tool_call = response_message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    print(f"The model decided to call the tool: `{function_name}`")
    print(f"Arguments: {function_args}")

    # Here we simulate the function execution result
    tool_result = json.dumps({"paper_id": "1706.03762", "url": "https://arxiv.org/abs/1706.03762", "title": "Attention Is All You Need"})
    print(f"Tool execution result: {tool_result}")
    # 4. Pass the model's decision and the tool's execution result back together, so the model generates the final reply
    messages.append(response_message)
    messages.append(
        {"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": tool_result}
    )

    final_response = client.chat.completions.create(model="qwen-plus", messages=messages)
    print("\nThe model's final reply:")
    print(final_response.choices[0].message.content)
```

### 4.2 The ReAct Pattern: Think-Act-Observe

Looking at the code just now, you'll find a key feature: **the tool-call result needs to be passed back to the LLM via a second API call**.

```python
# First call: let the model decide which tool to call
response = client.chat.completions.create(tools=...)

# Execute the tool
tool_result = execute_tool(...)

# Second call: pass the tool result back, so the model generates the final reply
final_response = client.chat.completions.create(messages=[..., tool_result])
```

This means the LLM **observes** the tool-call result, **thinks** about whether the task is complete, then decides whether to give the final answer or continue to **act** (call more tools). This **Think-Act-Observe** loop is the **ReAct pattern**, and an Agent that works this way is called a **ReAct Agent**.

Manually implementing the ReAct Agent's loop logic is fairly complex (you have to handle state management, multi-round calls, error retries, etc.). To simplify development, we'll use <a href="https://github.com/agentscope-ai/agentscope">AgentScope</a>, a production-grade Agent framework — it has already wrapped up the complete logic of the ReAct Agent and tool calling for you.

> **AgentScope's core advantages:**
>
> - **Out-of-the-box ReAct Agent**: built-in complete "think-act-observe" loop logic
> - **Flexible tool management**: uniformly manage tool functions via the `Toolkit` class, automatically parsing the JSON Schema
> - **Multi-model support**: compatible with mainstream LLM APIs such as OpenAI, DashScope (Tongyi Qianwen), Anthropic
> - **State management**: automatically handles state such as conversation history and tool-call records
> - **Async support**: all core features support async calls to improve performance

Let's rewrite the tool calling just now with AgentScope to feel the simplification the framework brings:

<img src="https://img.alicdn.com/imgextra/i1/O1CN01VwI8Ew1UEBMsHfe8S_!!6000000002485-55-tps-900-360.svg" style="width: 700px;background:white;display: block; "/>

```python
import asyncio
from agentscope.agent import ReActAgent
from agentscope.tool import Toolkit, ToolResponse
from agentscope.model import DashScopeChatModel
from agentscope.message import Msg, TextBlock
from agentscope.formatter import DashScopeChatFormatter

# 1. Define a tool that returns results using ToolResponse
def search_arxiv_paper(query: str) -> ToolResponse:
    """Search academic papers on Arxiv.org.

    Args:
        query (str): the search keyword
    """
    print(f"--- [Tool running] Searching Arxiv: {query} ---")
    # Simulate the search result here
    paper_url = "https://arxiv.org/abs/1706.03762"
    return ToolResponse(
        content=[
            TextBlock(
                type="text",
                text=f"Successfully found the paper '{query}'. You can access it here: {paper_url}",
            )
        ]
    )

async def run_agentscope_example():
    # 2. Register the tool function into the Toolkit
    toolkit = Toolkit()
    toolkit.register_tool_function(search_arxiv_paper)

    # 3. Create a ReActAgent and equip it with the toolkit
    agent = ReActAgent(
        name="Course Research Agent",
        sys_prompt="You are a course research assistant, skilled at helping people gather and organize learning materials.",
        model=DashScopeChatModel(
            model_name="qwen-plus",
            api_key=os.environ.get("DASHSCOPE_API_KEY")
        ),
        toolkit=toolkit,
        formatter=DashScopeChatFormatter()
    )

    # 4. Send a message to the Agent; it will automatically complete all steps
    user_request = "Help me find that classic Transformer paper 'Attention Is All You Need'"
    msg = Msg(name="user", content=user_request, role="user")

    print(f"User request: {user_request}\n")
    await agent(msg)

# Run the example
try:
    # In a Jupyter Notebook environment, you can await the coroutine directly
    await run_agentscope_example()
except NameError:
    # In a plain Python script, you need to use asyncio.run() to run the async function
    asyncio.run(run_agentscope_example())
```

Compared with the OpenAI Function Calling you implemented manually earlier, AgentScope's advantages are:

1. **More concise tool definition**: you only need to write a plain Python function with a docstring, and the framework automatically parses it to generate the JSON Schema
2. **No manual parsing**: `ReActAgent` internally handles the tedious steps of parsing `tool_calls`, executing the function, wrapping the result, etc.
3. **Automatic conversation-history management**: the framework automatically records user messages, tool calls, tool results, etc., with no manual maintenance
4. **Support for multi-round tool calling**: if one tool call isn't enough, the Agent automatically keeps thinking and calling more tools until the task is complete

Seeing AgentScope's concise implementation, you might wonder: since there's a ready-made framework, why learn that tedious manual implementation earlier?

This is because:

1. **Understanding the underlying principles**: internally the framework runs the flow "call the model → parse tool_calls → execute the function → call the model again." Understanding the mechanism is what lets you debug problems.

2. **Custom needs**: production environments often need special logic like permission checks, caching, retries, log monitoring; understanding the underpinnings lets you extend the framework.

3. **Compatibility guarantee**: when some models or platforms don't support the standard Function Calling format, the manual implementation can serve as a fallback.

## 5 The MCP Protocol: Managing Tools at Scale

### 5.1 The challenge of tool reuse

You've implemented web_search with Function Calling and written the JSON Schema in the tools parameter, and the model calls it on demand. But you notice a hidden issue with this mechanism: the specific version of web_search's Schema is hardcoded on the Agent side, which has high maintenance cost — you need a more flexible way to integrate tools.

From the tool provider's perspective, the problem is also obvious. The web_search service wants to be called by more AI applications, but under the Function Calling model it can't proactively "plug into" the AI ecosystem — it can only passively wait for each Agent developer to discover it on their own, and it can't ensure the quality of the developers' descriptions of its Schema.

### 5.2 MCP's decoupling idea

To solve this, Anthropic proposed MCP (Model Context Protocol), whose core idea is "whoever provides the tool defines the tool." It moves the responsibility for tool definition from the Agent (consumer) to the tool service (provider).

In MCP, the tool provider is called the MCP Server, responsible for declaring tools (name, description, and parameters); the tool consumer is called the MCP Client, responsible for connecting to the MCP Server and pulling the tool definitions. This way, the Agent only needs to integrate an MCP Client to dynamically discover and pull the latest capability definitions declared by the MCP Server, without hardcoding tool Schemas in its code.

<img src="https://img.alicdn.com/imgextra/i2/O1CN01Apfjka1JUhqQ26f9u_!!6000000001032-55-tps-1580-715.svg" width="700">

By decoupling the definition of tools from their use, MCP solves the scaling problem of "**how tools are discovered and managed**".

> **Related thinking: the USB protocol**
>
> You can compare MCP to the real-world USB protocol. Before USB, every peripheral (mouse, keyboard, printer) had its own unique interface, and the computer had to adapt to each one. The USB protocol unified all of this — any compliant device can plug and play.
> *   **Function Calling** is like an **internal bus** on the computer's motherboard, defining how the CPU communicates with a specific component.
> *   **MCP** is like the **external USB interface**, defining an open standard that lets countless third-party devices easily plug into this ecosystem.

### 5.3 Refactoring the web_search tool call with MCP

Having understood MCP's decoupling idea, you want to refactor the earlier web_search with MCP to lower future maintenance cost. To reduce development and debugging difficulty, you can first get the MCP Client working locally and verify its functionality using a local mock Server, then switch to web_search's online MCP Server.

#### 5.3.1 Debug the MCP Client locally: stdio

In this step, both the MCP Client and Server run locally, communicating via [stdio](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#stdio). Meanwhile, the Server uses mock data to simulate the returned results of the `web_search` online MCP service.

The official MCP Python SDK provides the `FastMCP` framework, which can quickly turn the `web_search` function into an MCP Server:

```python
%%writefile run_mcp_server_example.py
# The magic command above automatically generates this code file locally when the cell runs, so the MCP Client can start this service locally
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Create a local MCP Server instance, simulating a web-search service
mcp = FastMCP("MockWebSearch")

# The @mcp.tool() decorator registers a plain function as an MCP tool
@mcp.tool()
def web_search(query: str, max_results: int = 3) -> str:
    """Simulate a web search, returning results based on the keyword.

    Args:
        query: the search keyword
        max_results: the maximum number of results to return, default 3
    """
    mock_db = {
        "large language models": [
            {"title": "GPT-5 released: another breakthrough in multimodal capability",
             "snippet": "OpenAI released GPT-5, with significant progress in reasoning and multimodal understanding.",
             "date": "2026-04-10"},
            {"title": "Qwen3 open-source model series comprehensively upgraded",
             "snippet": "Alibaba Cloud Tongyi Qianwen released Qwen3, comprehensively surpassing the previous generation in math reasoning, code generation, etc.",
             "date": "2026-04-08"},
            {"title": "A survey of large language model applications in scientific discovery",
             "snippet": "A Nature review summarizes the latest LLM applications in drug discovery, materials science, and other fields.",
             "date": "2026-04-05"},
        ],
    }

    results = []
    for key, items in mock_db.items():
        if key in query or query in key:
            results.extend(items)
    if not results:
        results = [{"title": f"Search results for \u300c{query}\u300d",
                    "snippet": f"These are simulated results for \u300c{query}\u300d.",
                    "date": datetime.now().strftime("%Y-%m-%d")}]

    lines = [f"Found {len(results[:max_results])} results for \u300c{query}\u300d:\n"]
    for i, r in enumerate(results[:max_results], 1):
        lines.append(f"{i}. \u3010{r['title']}\u3011\n   {r['snippet']}\n   Date: {r['date']}\n")
    return "\n".join(lines)

if __name__ == "__main__":
    # Start in stdio mode, waiting to communicate with the Client (parent process) via stdin/stdout
    mcp.run(transport="stdio")
```

The mock Server is ready. Now use the Client to call the tool:

```python
import asyncio
import os
import sys
from agentscope.agent import ReActAgent
from agentscope.mcp import StdIOStatefulClient
from agentscope.tool import Toolkit
from agentscope.model import DashScopeChatModel
from agentscope.message import Msg
from agentscope.formatter import DashScopeChatFormatter

async def run_local_mcp_example():
    # 1. Configure the MCP client to point at the local tool service
    #    Here it starts run_mcp_server_example.py in the same directory via stdio (simulating the web-search MCP service)
    web_search_client = StdIOStatefulClient(
        name="web_search_service", # name of the current client
        command=sys.executable, # start the MCP Server via a subprocess
        args=["run_mcp_server_example.py"], # local MCP Server script
        cwd=os.getcwd(),
    )
    await web_search_client.connect() # the stdio stateful client needs an explicit connect

    # 2. Tool discovery: the Client automatically asks the Server "what tools do you have?"
    #    The Server returns the tool list, which is registered into the Agent's toolkit
    toolkit = Toolkit()
    await toolkit.register_mcp_client(web_search_client)

    # 3. Create a ReAct Agent, equipped with the toolkit
    agent = ReActAgent(
        name="Research Assistant Agent",
        sys_prompt="You are a course research assistant, skilled at using tools to gather and organize the latest teaching materials.",
        model=DashScopeChatModel(
            model_name="qwen-plus", api_key=os.environ.get("DASHSCOPE_API_KEY")
        ),
        toolkit=toolkit,
        formatter=DashScopeChatFormatter()
    )

    # 4. Launch the task
    user_request = "I'm gathering materials for an 'LLM Principles' course. Please search for recent progress on 'large language models'."
    msg = Msg(name="user", content=user_request, role="user")

    print(f"User request: {user_request}\n")
    response_msg = await agent(msg)

    await web_search_client.close() # the stdio stateful client needs an explicit close when done

await run_local_mcp_example()
```

After running the Client, you'll see the Agent successfully call the `web_search` tool and return the search results.

<a href="https://img.alicdn.com/imgextra/i3/O1CN018O554N1dYdaZlvHcO_!!6000000003748-0-tps-1840-848.jpg" target="_blank">
<img src="https://img.alicdn.com/imgextra/i3/O1CN018O554N1dYdaZlvHcO_!!6000000003748-0-tps-1840-848.jpg" width="600">
</a>

When the Agent starts, the MCP Client **automatically connects to the MCP Server and pulls the tool list (name, description, parameters)**. After getting the list, the subsequent flow is similar to the Function Calling in 1.2 — select the tool, generate the arguments, execute the call, return the result.

<a href="https://img.alicdn.com/imgextra/i2/O1CN01VT6xmQ1bjVlF8DT7d_!!6000000003501-55-tps-2014-1623.svg" target="_blank">
<img src="https://img.alicdn.com/imgextra/i2/O1CN01VT6xmQ1bjVlF8DT7d_!!6000000003501-55-tps-2014-1623.svg" width="600">
</a>

#### 5.3.2 Connect to the online MCP service: Streamable HTTP

The MCP Client has been validated locally. Next, you can connect to the production-grade WebSearch MCP service hosted on the Alibaba Cloud Model Studio platform — you just need to slightly modify the Client's transport:

<table>
<tr>
<th>Local mode (stdio)</th>
<th>Online mode (Streamable HTTP)</th>
</tr>
<tr>
<td valign="top"><pre><code>client = StdIOStatefulClient(
    name="web_search_service",
    command=sys.executable,
    args=["run_mcp_server_example.py"]
)</code></pre></td>
<td valign="top"><pre><code>client = HttpStatelessClient(
    name="web_search_service",
    transport="streamable_http",
    url="https://dashscope.aliyuncs.com/...",
    headers={
        "Authorization": "Bearer "
        + os.environ.get("DASHSCOPE_API_KEY")
    }
)</code></pre></td>
</tr>
</table>

The key change is switching the transport from stdio to [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#streamable-http) (`transport="streamable_http"` in the code).

> Before running this code, please first go to the [Alibaba Cloud Model Studio website](https://bailian.console.aliyun.com/?tab=mcp#/mcp-market/detail/WebSearch) to activate the web-search MCP service and understand its billing details.

```python
import asyncio
import os
from agentscope.agent import ReActAgent
from agentscope.mcp import HttpStatelessClient
from agentscope.tool import Toolkit
from agentscope.model import DashScopeChatModel
from agentscope.message import Msg
from agentscope.formatter import DashScopeChatFormatter

async def run_mcp_example():
    # 1. Configure the MCP client to point at the remote tool service
    #    Here it connects to Alibaba Cloud DashScope's public web-search MCP service
    web_search_client = HttpStatelessClient(
        name="web_search_service", # give this client a name
        transport="streamable_http",
        url="https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp",
        headers={"Authorization": "Bearer " + os.environ.get("DASHSCOPE_API_KEY")},
    )
    # 2. Register the MCP client into the toolkit
    #    On startup, the Agent automatically "discovers" all tools provided by the remote service via the client
    toolkit = Toolkit()
    await toolkit.register_mcp_client(web_search_client)
    # 3. Create the Agent, equipped with the toolkit containing the MCP tools
    agent = ReActAgent(
        name="Research Assistant Agent",
        sys_prompt="You are a course research assistant, skilled at using tools to gather and organize the latest teaching materials.",
        model=DashScopeChatModel(
            model_name="qwen-plus", api_key=os.environ.get("DASHSCOPE_API_KEY")
        ),
        toolkit=toolkit,
        formatter=DashScopeChatFormatter()
    )

    # 4. Ask a question that requires the remote tool to answer
    user_request = "I'm gathering materials for an 'LLM Principles' course and need an example of calling external real-time data — for instance, help me search for recent progress on 'large language models'."
    msg = Msg(name="user", content=user_request, role="user")

    print(f"User request: {user_request}\n")
    response_msg = await agent(msg)

try:
    # In a Jupyter Notebook environment, you can await the coroutine directly
    await run_mcp_example()
except NameError:
    # In a plain Python script, you need to use asyncio.run() to run the async function
    asyncio.run(run_mcp_example())
```

In this example, you used MCP to solve the problem of hardcoding the web_search tool's Schema on the Agent side.
- **stdio**: the MCP Server and Client are on the same machine, suitable for local development and debugging; it's also the common way IDEs like Claude Desktop and Cursor integrate a local MCP Server.
- **Streamable HTTP**: the MCP Server is deployed remotely, suitable for production environments where multiple Agents or users share the same MCP Server.

At this point, you've mastered the complete path from a single tool function, to reliable intent recognition, to tool management at scale. Your Agent can now interact with the external world stably and efficiently.

## 6 Summary

Let's recap what you learned in this lesson:

*   **Connecting the model to the external world**: you learned how to write tool functions for the Agent to obtain external information, and upgraded from fragile `if/else` rule checks to using the LLM's own understanding to decide which tool to call.
*   **Manually implementing reliable tool calling**: you mastered building a "guide-validate-retry" closed loop to make the model stably output structured JSON instructions, and understood that this is the underlying logic for robust tool calling.
*   **Function Calling and tool discovery**: you learned "Function Calling," the industry standard, which wraps the complex tool-calling flow into a simple API. Going further, you also learned how the MCP protocol decouples the definition of tools from their use, solving the problem of reuse and maintenance at scale.
*   **The ReAct loop and development frameworks**: you recognized that tool calling is the key to implementing the **ReAct (Think-Act-Observe)** loop, and learned to use a development framework like AgentScope to free yourself from the tedium of manual implementation and focus more on business logic.

## 🔥 Quiz


### 🔍 Single choice 3.1.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Your Agent has already integrated three tools — calendar, email, and code repository — and every time you add a tool you must modify the Agent code, update the JSON Schema, and redeploy. The team plans to integrate a dozen more internal systems. How should you reduce the maintenance cost of tool integration?❓</b>

- A. Extract all tools' JSON Schemas into a single unified config file, so adding a tool only changes config, not code
- B. Adopt the MCP protocol, letting each tool run as an independent service that the Agent dynamically discovers and calls via a standard protocol
- C. Wrap all tools behind a unified HTTP gateway, so the Agent only calls the gateway's single interface to forward requests
- D. Reduce the number of tools by merging functionally-similar tools into one multifunction tool to lower management complexity

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: B**
📝 **Explanation**:
A only separates the config from the code, reducing how often you change code, but the Agent still has to be aware of every tool's Schema definition, and each addition still requires manually updating the config and restarting. C's HTTP gateway unifies the call entry point, but the Agent loses awareness of each tool's capability and can't autonomously choose the right tool for the task. D contradicts the expansion need; merging tools reduces specialization and increases a single tool's complexity. B is correct: MCP lets tools expose their own capability descriptions as independent services, and the Agent dynamically discovers available tools via a standard protocol; adding a tool requires no change to the Agent code, achieving decoupling of tools from the Agent.
</div>
</details>

## ✉️ Feedback
You're welcome to participate in the [Alibaba Cloud LLM ACP course survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie) to share your learning experience and course feedback.
Your criticism and encouragement are our motivation to keep improving!
