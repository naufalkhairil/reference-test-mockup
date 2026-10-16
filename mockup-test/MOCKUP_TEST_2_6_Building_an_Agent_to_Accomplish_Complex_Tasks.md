# Mockup Test: 2 6 Building an Agent to Accomplish Complex Tasks

Choose the single best answer for each question.

## Question 1

What distinguishes an LLM agent from a chatbot that only returns text?

A. An agent can select and use tools to take actions toward a goal.

B. An agent must always have a larger context window.

C. A chatbot has no system prompt.

D. An agent only retrieves static documents.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson frames agents around planning and executing tasks using tools.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Agent concepts and workflow”.
</details>

## Question 2

A user asks an agent to schedule a meeting and send invitations. What enables those actions?

A. Tools or function interfaces that connect the model to calendar and email operations.

B. A larger temperature value.

C. A longer system prompt alone.

D. A local vector index.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The model needs tool integrations to perform external operations.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Tool calling / agent tools”.
</details>

## Question 3

Why should an agent inspect tool definitions and parameters carefully?

A. The model needs clear descriptions and schemas to choose tools and provide valid arguments.

B. Tool descriptions determine the API key.

C. The schema trains the model weights.

D. Parameters make retrieval unnecessary.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Tool names, descriptions, and argument schemas guide tool selection and invocation.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Tool definition and invocation”.
</details>

## Question 4

An agent must complete a task with several dependent steps. Which process is most appropriate?

A. Plan the steps, execute them with tools, observe results, and continue or revise.

B. Call every available tool at random.

C. Generate a final answer before taking any action.

D. Repeat the user’s request verbatim.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Agent execution commonly cycles through planning, action, and observation until completion.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Agent planning and execution workflow”.
</details>

## Question 5

A tool returns an error. What should a robust agent do next?

A. Use the observation to revise its plan or report the failure clearly.

B. Pretend the tool succeeded.

C. Ignore the result and fabricate output.

D. Call unrelated tools indefinitely.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Tool outputs are observations that should inform subsequent decisions and honest reporting.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Agent execution loop” — tool results and error handling.
</details>

## Question 6

Why should tool access follow least privilege?

A. It limits the impact if the agent makes an unsafe or mistaken tool call.

B. It improves tokenization accuracy.

C. It guarantees the agent never hallucinates.

D. It removes the need for user confirmation in every application.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Restricting permissions reduces the consequences of errors or abuse.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Agent security / tool permissions”.
</details>

## Question 7

Which operation is especially appropriate for adding an authorization check before execution?

A. A tool that updates employee records or sends an external email.

B. A tool that formats a string locally.

C. A read-only text summarizer.

D. A prompt that selects a tone.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Side-effecting actions need authorization and safeguards because they change data or communicate externally.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Agent safety and authorization”.
</details>

## Question 8

An agent produces repetitive tool calls without progress. What design element helps prevent runaway execution?

A. A bounded iteration or step limit with a clear stop condition.

B. An unlimited context window.

C. A second API key.

D. More retrieved chunks.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

A bounded loop and stop criteria control execution and resource use.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Agent workflow control”.
</details>

## Question 9

Why is explicit structured tool output useful?

A. It helps the agent interpret results consistently and decide the next step.

B. It ensures all tools return the same answer.

C. It replaces access controls.

D. It makes actions irreversible.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Consistent results make the observe-and-decide loop easier to manage.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Tool outputs / agent orchestration”.
</details>

## Question 10

When should an agent finish and respond to the user?

A. When the goal is achieved, a defined stop condition is reached, or it cannot proceed and should explain why.

B. Only after it has called every tool.

C. As soon as it makes the first plan.

D. Never; agents should keep reasoning indefinitely.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Agents need explicit completion and failure conditions to avoid unnecessary actions.

**Source:** `2_6_Building_an_Agent_to_Accomplish_Complex_Tasks.ipynb` — “Agent planning and execution” — stopping criteria.
</details>
