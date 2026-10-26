# Professional Exam: Agent Basics and Tool Calling

Choose the single best answer for each question. This exam is grounded in the course notebook `3_1_Agent_Basics_Tool_Calling.ipynb` (Alibaba Cloud ACP LLM course). It is a source-grounded practice draft, not a validated or official certification exam.

## Question 1

The notebook's first implementation hardcodes tool execution: on every user request, the program always runs `web_search`, then sends the result together with the request to the LLM for a summarizing reply. According to Section 1.2, what is the fundamental limitation of this approach?

A. It only applies when there is exactly one tool and it must be called on every turn; as the toolset grows (e.g., adding `search_arxiv_paper` and `fetch_webpage_content`), it cannot let the bot call tools on demand.

B. It cannot pass tool results to the LLM in the same prompt, forcing a separate summarization service.

C. It requires a model with native Function Calling support, which simulated tools do not provide.

D. It only works with mock tools, so it cannot be adapted to call real search-engine APIs.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — It only applies when there is exactly one tool and it must be called on every turn; as the toolset grows (e.g., adding `search_arxiv_paper` and `fetch_webpage_content`), it cannot let the bot call tools on demand.**

Section 1.2 states this directly: the hardcoded approach "only applies to the scenario of 'there is exactly one tool, and it must be called on every turn.' As colleagues' needs grow, your bot may need to add more tools like `search_arxiv_paper`... `fetch_webpage_content`... At that point you hit a thornier problem: how do you let the bot call tools on demand?" This limitation motivates the entire intent-recognition progression that follows.

B contradicts the shown code, which concatenates the request and tool result into one prompt. C is false — the hardcoded flow predates and does not require Function Calling. D is false: the notebook notes the function is simulated only "to focus on the core logic" and that "in a real scenario, this would call an actual search-engine API."

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 1.1 "Hardcoded approach: the simplest implementation" (code example) and Section 1.2 "Limitation analysis: why we need a more flexible approach".
</details>

## Question 2

You consider routing requests with an `if/elif` keyword matcher: `"paper" or "arxiv"` → `search_arxiv_paper`, `"search"/"find"/"materials"` → `web_search`, and so on. The notebook tests it against the request "I want to see what that paper Attention is All You Need is about." Why does the notebook call this approach fragile and hard to maintain?

A. Each keyword check requires an LLM API call, making the router too slow and expensive for production.

B. The router can only ever return one tool in total, so multi-tool bots are impossible by construction.

C. A request can express a tool-worthy intent without containing any preset keyword — the example sentence contains "paper" but the crude router still fails to recognize the combined intent — and the `elif` chain must keep growing with every new tool and phrasing.

D. Keyword matching is case-sensitive, so it fails on any input that is not lowercase English.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — A request can express a tool-worthy intent without containing any preset keyword — the example sentence contains "paper" but the crude router still fails to recognize the combined intent — and the `elif` chain must keep growing with every new tool and phrasing.**

Section 2.1 presents the pseudocode router ending in the comment "...you'd need to keep adding elif checks here," then demonstrates the failure: for "I want to see what that paper Attention is All You Need is about," the router "can't recognize the intent for `search_arxiv_paper` and `fetch_webpage_content`, because it contains none of the preset keywords" — natural phrasing slips past a fixed keyword list. This motivates Section 2.2's replacement: list all tools in the prompt and let the LLM decide.

A is false — the router is pure string matching with no API calls; that is its only advantage. B misreads the code (it routes among several tools, just badly). D invents a case-sensitivity problem the notebook never raises.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 2.1 "Fragile keyword matching" (`route_to_tool` pseudocode and the "Attention is All You Need" failure analysis) and Section 2.2 "LLM-based intent recognition".
</details>

## Question 3

In the notebook's LLM-based routing example (`get_tool_decision_from_llm`), the API call sets `temperature=0.0`. Based on the code and its comment, why?

A. To encourage more creative, diverse decisions so the model discovers unconventional tool combinations.

B. To make the routing decision more deterministic, since the decision will be parsed and acted on by code rather than read by a human.

C. To reduce the token cost of each routing call.

D. To force the model to emit schema-valid JSON, which higher temperatures make impossible.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — To make the routing decision more deterministic, since the decision will be parsed and acted on by code rather than read by a human.**

The code sets `temperature=0.0 # use a low temperature for a more deterministic decision`. The surrounding sections explain why determinism matters here: the router's output feeds a program that must decide which tool to execute, and Section 3.1 observes that "the LLM tends to generate diverse text, whereas what you need is an easy-to-parse, deterministic data format."

Option D is the tempting distractor because it pairs temperature with output format — but the notebook shows low temperature alone does not guarantee structure: Section 3 exists precisely because the model's decisions still come back in mixed natural-language formats, requiring an explicit JSON structure with schema validation. A is the opposite of the stated intent, and C invents a cost rationale.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 2.2 code example `get_tool_decision_from_llm` (the `temperature=0.0` comment) and Section 3.1 "Why structure is needed".
</details>

## Question 4

You implement the notebook's "guide-validate-retry" closed loop: the prompt contains the JSON structure plus an example, and each response is validated with a Pydantic model (`TypeAdapter(ToolCall)`). What does the program do when validation fails?

A. Raise the exception immediately and abort the user's request, since a malformed decision cannot be trusted.

B. Parse whichever fields are present and silently fill missing fields with default values so execution can continue.

C. Re-send the identical prompt unchanged, relying on sampling randomness to produce a better answer.

D. Append the model's erroneous raw output and the validation error message to the conversation history as correction clues, and ask the model to regenerate in strict JSON, within a bounded number of retries.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Append the model's erroneous raw output and the validation error message to the conversation history as correction clues, and ask the model to regenerate in strict JSON, within a bounded number of retries.**

Step 3 of the loop in Section 3.2 prescribes this: "If validation fails, the program should capture the validation error message and send it, together with the model's previous erroneous output, back to the model as correction clues, asking it to regenerate." The `get_structured_output` code implements it in the `except (json.JSONDecodeError, ValidationError)` branch, extending `messages` with the assistant's raw output plus `"Format error: {e}. Please re-output strictly in JSON format"`, looping up to `max_retries` (2) before returning `None`.

Option C misses the defining feature of the loop — feeding the specific error back as a correction clue rather than blindly resampling. A abandons the retry mechanism the notebook builds, and B would execute a decision that failed schema validation, defeating the purpose of strict validation.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 3.2 "Building a 'guide-validate-retry' closed loop" (steps 1–3) and the `get_structured_output` code cell (retry branch appending error + raw output).
</details>

## Question 5

In the notebook's Function Calling example using the OpenAI SDK, a `tools` parameter carries the JSON Schema for `search_arxiv_paper`, and the first API call returns a `tool_calls` field. According to Section 4.1, what happens next — who executes the tool, and how does the result reach the model?

A. Your application code parses the function name and arguments from `tool_calls`, actually executes the function locally, wraps the result as a `role: "tool"` message, and calls the API a second time so the model can generate the final user-facing reply from the tool result.

B. The provider's API server executes the registered function on your behalf and streams the tool result back within the same first response.

C. The model executes the function internally during the first call and embeds the result inside the `tool_calls` field for you to display.

D. Your code executes the function and returns its raw result directly to the user; no second model call is needed.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Your application code parses the function name and arguments from `tool_calls`, actually executes the function locally, wraps the result as a `role: "tool"` message, and calls the API a second time so the model can generate the final user-facing reply from the tool result.**

Section 4.1's "Execute & Return" list assigns these steps explicitly to the developer ("**You need to**"): 1) parse the function name and arguments in `tool_calls`, 2) actually execute the corresponding function in your code, 3) wrap the execution result as a `role: "tool"` message, 4) call the API again sending the tool result to the model, 5) the model generates the final user reply. The code cell demonstrates each step, including `messages.append({"tool_call_id": ..., "role": "tool", "name": function_name, "content": tool_result})` and the second `chat.completions.create` call.

B and C make the tempting misattribution that the model or provider *runs* the tool — the notebook is explicit that the model only *decides* (returns name + schema-conforming arguments). D skips step 4–5, discarding the model's synthesis of the final reply.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 4.1 "How Function Calling works" (Tool Definition / Call Decision / Execute & Return five-step list) and the accompanying complete code example.
</details>

## Question 6

The notebook highlights that "the tool-call result needs to be passed back to the LLM via a second API call." Which statement best captures the ReAct pattern this two-call flow illustrates?

A. Thinking happens once when the agent starts; afterwards, acting and observing repeat in code without further model involvement.

B. The framework logs tool results for observability, but the model never sees them; the final reply is generated from the user message alone.

C. The model observes the tool-call result, thinks about whether the task is complete, then decides whether to give the final answer or continue to act by calling more tools — a Think-Act-Observe loop that defines a ReAct Agent.

D. The model must call exactly one tool per conversation, then answer; multi-round tool calling violates the ReAct pattern.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The model observes the tool-call result, thinks about whether the task is complete, then decides whether to give the final answer or continue to act by calling more tools — a Think-Act-Observe loop that defines a ReAct Agent.**

Section 4.2 states this nearly verbatim: "This means the LLM **observes** the tool-call result, **thinks** about whether the task is complete, then decides whether to give the final answer or continue to **act** (call more tools). This **Think-Act-Observe** loop is the **ReAct pattern**, and an Agent that works this way is called a **ReAct Agent**." The AgentScope section reinforces the iterative nature: "if one tool call isn't enough, the Agent automatically keeps thinking and calling more tools until the task is complete," which rules out D.

A removes the model from the loop after startup, contradicting the second API call whose purpose is model reasoning over the tool result; B denies that the model observes results, the very point of passing them back.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 4.2 "The ReAct Pattern: Think-Act-Observe" (two-call code sketch and ReAct definition); AgentScope advantage 4 (multi-round tool calling) in Section 4.
</details>

## Question 7

A teammate argues: "AgentScope's `ReActAgent` already wraps the whole think-act-observe loop, parses tool calls, and manages history — so the manual 'intent recognition → structured output → validate and retry' implementation we studied is dead code we can forget." According to the notebook, what is the best-supported response?

A. Agree — frameworks fully replace the manual flow, which the notebook presents only as historical background with no practical value.

B. Disagree — understanding the underlying "call model → parse tool_calls → execute → call model again" flow is what lets you debug problems; production often needs custom logic such as permission checks, caching, retries, and log monitoring that requires extending the framework; and the manual implementation serves as a fallback when some models or platforms don't support the standard Function Calling format.

C. Disagree — the manual implementation is faster at runtime because it skips JSON Schema generation entirely.

D. Agree on condition that the team only ever uses models with native Function Calling, since AgentScope does not manage conversation history.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Disagree — understanding the underlying "call model → parse tool_calls → execute → call model again" flow is what lets you debug problems; production often needs custom logic such as permission checks, caching, retries, and log monitoring that requires extending the framework; and the manual implementation serves as a fallback when some models or platforms don't support the standard Function Calling format.**

The notebook poses the teammate's exact question — "since there's a ready-made framework, why learn that tedious manual implementation earlier?" — and answers with three reasons that map one-to-one onto the keyed option: (1) understanding the underlying principles ("internally the framework runs the flow 'call the model → parse tool_calls → execute the function → call the model again'. Understanding the mechanism is what lets you debug problems"), (2) custom needs in production ("permission checks, caching, retries, log monitoring... lets you extend the framework"), and (3) compatibility guarantee ("when some models or platforms don't support the standard Function Calling format, the manual implementation can serve as a fallback").

C invents a performance claim the notebook never makes, and D's premise is false — AgentScope's listed advantages include automatic conversation-history management. A contradicts the notebook's explicit three-reason defense.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 4 (AgentScope), the passage "Seeing AgentScope's concise implementation, you might wonder..." with its three numbered reasons (understanding principles, custom needs, compatibility guarantee).
</details>

## Question 8

You operate a popular `web_search` service. Under the Function Calling model, every Agent developer who wants to use it must hardcode their own copy of its JSON Schema in their `tools` parameter — you cannot update the schema centrally, and you cannot ensure developers describe your tool accurately. According to Sections 5.1–5.2, what is the MCP-based solution?

A. Publish schema documentation and ask each Agent team to keep their hardcoded `tools` entries in sync with your releases.

B. Submit your schema to each Agent framework's central registry, accepting per-framework review whenever you ship a change.

C. Keep Function Calling but move all schemas into one shared config file that every Agent imports and redeploys when you change it.

D. Expose the service as an MCP Server that declares its own tools (name, description, parameters); Agents integrate an MCP Client that dynamically discovers and pulls the latest tool definitions, moving definition responsibility from consumer to provider — "whoever provides the tool defines the tool."

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Expose the service as an MCP Server that declares its own tools (name, description, parameters); Agents integrate an MCP Client that dynamically discovers and pulls the latest tool definitions, moving definition responsibility from consumer to provider — "whoever provides the tool defines the tool."**

Section 5.1 names both halves of the problem in the stem: the schema "is hardcoded on the Agent side, which has high maintenance cost," and from the provider's perspective the service "can't proactively 'plug into' the AI ecosystem... and it can't ensure the quality of the developers' descriptions of its Schema." Section 5.2 gives the MCP answer: core idea "whoever provides the tool defines the tool"; the MCP Server (provider) "declar[es] tools (name, description, and parameters)" while the MCP Client (consumer) "connect[s] to the MCP Server and pull[s] the tool definitions," so the Agent "only needs to integrate an MCP Client to dynamically discover and pull the latest capability definitions... without hardcoding tool Schemas in its code."

A restates the status quo the section identifies as the problem. C is the tempting partial fix — a shared config still centralizes copies on the consumer side and requires every Agent to update and redeploy; MCP instead makes discovery dynamic. B invents per-framework registries, the opposite of one open standard.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 5.1 "The challenge of tool reuse" and Section 5.2 "MCP's decoupling idea" (Server/Client roles, "whoever provides the tool defines the tool", dynamic discovery without hardcoded schemas).
</details>

## Question 9

You are integrating MCP into your Agent. The notebook recommends first validating with a local mock Server (`run_mcp_server_example.py`, built with `FastMCP`) before switching to the hosted WebSearch MCP service on Alibaba Cloud Model Studio. Which transport strategy matches the notebook's guidance?

A. Use the stdio transport locally — Client and Server on the same machine, with the Server started as a subprocess and communicating via stdin/stdout — for development and debugging; then switch the Client to Streamable HTTP with the remote service URL for production, where the Server is deployed remotely and shared by multiple Agents or users.

B. Use Streamable HTTP for the local mock and stdio for production, because stdio is more secure across networks.

C. Use stdio in both environments, since transport choice has no effect on where the Server runs or who can share it.

D. Skip the local mock entirely and debug directly against the production MCP service, since only the live service reflects real schemas.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Use the stdio transport locally — Client and Server on the same machine, with the Server started as a subprocess and communicating via stdin/stdout — for development and debugging; then switch the Client to Streamable HTTP with the remote service URL for production, where the Server is deployed remotely and shared by multiple Agents or users.**

Section 5.3 sequences the work exactly this way: "you can first get the MCP Client working locally and verify its functionality using a local mock Server, then switch to web_search's online MCP Server." Section 5.3.1 uses stdio — "both the MCP Client and Server run locally, communicating via stdio" — with `StdIOStatefulClient(command=sys.executable, args=["run_mcp_server_example.py"])` starting the Server as a subprocess. Section 5.3.2's comparison table shows the only key change is the transport: `transport="streamable_http"` with the hosted URL and Authorization header. The closing summary adds that stdio is "suitable for local development and debugging" (and how IDEs like Claude Desktop and Cursor integrate local servers), while Streamable HTTP suits "production environments where multiple Agents or users share the same MCP Server."

B inverts the two environments and misattributes network security to stdio, which is same-machine only. C ignores that transport determines local vs. remote topology, and D abandons the notebook's recommended local-first validation (which also avoids production billing during debugging).

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Sections 5.3.1 "Debug the MCP Client locally: stdio", 5.3.2 "Connect to the online MCP service: Streamable HTTP" (side-by-side transport table, "The key change is switching the transport from stdio to Streamable HTTP"), and the stdio-vs-HTTP summary bullets at the end of Section 5.3.
</details>

## Question 10

The notebook offers an analogy: "Function Calling is like an internal bus on the computer's motherboard... MCP is like the external USB interface." What distinction does this analogy capture, in the notebook's terms?

A. MCP replaces Function Calling end-to-end: once tools are discovered via MCP, calls no longer follow any function-call-style select-execute-return flow.

B. Function Calling is designed for physical hardware devices, while MCP works only with cloud-hosted services.

C. Function Calling defines how one Agent communicates with tools whose schemas are declared Agent-side, while MCP is an open standard that decouples tool definition from tool use, letting any compliant third-party tool plug into the ecosystem — solving the scaling problem of how tools are discovered and managed.

D. MCP requires each Agent to embed a custom driver for every tool, similar to the pre-USB era of unique peripheral interfaces.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Function Calling defines how one Agent communicates with tools whose schemas are declared Agent-side, while MCP is an open standard that decouples tool definition from tool use, letting any compliant third-party tool plug into the ecosystem — solving the scaling problem of how tools are discovered and managed.**

The USB sidebar explains that before USB, "every peripheral had its own unique interface, and the computer had to adapt to each one," while USB made any compliant device plug-and-play — mapping Function Calling to the motherboard's internal bus (a specific Agent-to-tool communication mechanism) and MCP to "an open standard that lets countless third-party devices easily plug into this ecosystem." The section's thesis sentence states: "By decoupling the definition of tools from their use, MCP solves the scaling problem of 'how tools are discovered and managed.'"

Option A overreaches: the notebook says that after the MCP Client pulls the tool list, "the subsequent flow is similar to the Function Calling in 1.2 — select the tool, generate the arguments, execute the call, return the result," so MCP complements rather than replaces the call mechanics. D inverts the analogy — per-tool custom adaptation is the *pre-USB* problem MCP eliminates. B takes the hardware metaphor literally.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — Section 5.2 "MCP's decoupling idea" ("Related thinking: the USB protocol" sidebar; the decoupling/scaling thesis sentence) and Section 5.3.1 (post-discovery flow "similar to the Function Calling").
</details>

---

**Answer-key balance check:** A, C, B, D, A, C, B, D, A, C — A×3, B×2, C×3, D×2; no consecutive-letter pattern.
