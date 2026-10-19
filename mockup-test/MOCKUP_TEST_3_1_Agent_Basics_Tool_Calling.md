# Professional Exam: 3.1 Agent Basics & Tool Calling

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

Your Agent has already integrated three tools — calendar, email, and code repository — and every time you add a tool you must modify the Agent code, update the JSON Schema, and redeploy. The team plans to integrate a dozen more internal systems. How should you reduce the maintenance cost of tool integration?

A. Extract all tools' JSON Schemas into a single unified config file, so adding a tool only changes config, not code

B. Adopt the MCP protocol, letting each tool run as an independent service that the Agent dynamically discovers and calls via a standard protocol

C. Wrap all tools behind a unified HTTP gateway, so the Agent only calls the gateway's single interface to forward requests

D. Reduce the number of tools by merging functionally-similar tools into one multifunction tool to lower management complexity

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Adopt the MCP protocol, letting each tool run as an independent service that the Agent dynamically discovers and calls via a standard protocol**

A only separates the config from the code, reducing how often you change code, but the Agent still has to be aware of every tool's Schema definition, and each addition still requires manually updating the config and restarting. C's HTTP gateway unifies the call entry point, but the Agent loses awareness of each tool's capability and can't autonomously choose the right tool for the task. D contradicts the expansion need; merging tools reduces specialization and increases a single tool's complexity. B is correct: MCP lets tools expose their own capability descriptions as independent services, and the Agent dynamically discovers available tools via a standard protocol; adding a tool requires no change to the Agent code, achieving decoupling of tools from the Agent.

**Source:** `3_1_Agent_Basics_Tool_Calling.ipynb` — embedded lesson quiz and its explanation.

</details>
