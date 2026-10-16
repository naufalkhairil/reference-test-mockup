# Mockup Test: 2 1 Building FAQ Bot with LLM

Choose the single best answer for each question.

## Question 1

A developer wants to call Qwen from a Python application. Which approach does the lesson demonstrate?

A. Use the OpenAI Python SDK with Model Studio’s compatible endpoint.

B. Use a browser automation script to copy answers from Qwen’s web UI.

C. Train a new model from scratch.

D. Send requests directly to the notebook kernel.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson shows Qwen being called through the OpenAI-compatible Python SDK and a DashScope base URL.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “1.1 Confirm the Python environment” and “1.4 Basic chat call”.
</details>

## Question 2

Before using Qwen through the API, what must be done in Model Studio?

A. Activate model invocation service and create an API key.

B. Create a vector database and upload all documents.

C. Deploy a GPU instance.

D. Publish the application to a public endpoint.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The API setup requires activating invocation service and obtaining an API key.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “1.2 Get an API Key”.
</details>

## Question 3

Why does the lesson recommend putting the API key in an environment variable?

A. It reduces accidental exposure in shared code and avoids updating hardcoded copies when rotating keys.

B. It makes the model produce deterministic answers.

C. It increases the context window.

D. It removes the need to authenticate API requests.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Environment variables keep the secret out of source code and simplify key rotation.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “1.3 Configure the API Key”.
</details>

## Question 4

In a chat completion message list, what do `role` and `content` represent?

A. The speaker category and the message text.

B. The model name and API endpoint.

C. The token limit and temperature.

D. The prompt template and retrieved document.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson describes each message as having a role such as system/user/assistant and its content.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “1.5 Multi-turn conversation” — message fields.
</details>

## Question 5

A user asks “What tool do we use?” and then “How do I apply for an account for it?” What enables the second question to use context?

A. Pass prior user and assistant messages in the conversation history.

B. Increase the API key length.

C. Use streaming output.

D. Change the system role after each turn.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Multi-turn coherence comes from retaining the conversation history in the messages list.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “1.5 Multi-turn conversation” — history mechanism and example.
</details>

## Question 6

A long conversation exceeds the practical context window. Which mitigation is suggested?

A. Truncate or summarize older history.

B. Remove the system message and retain only the latest assistant answer.

C. Switch every turn to streaming.

D. Repeat the entire history in the user’s final question.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson notes that history consumes context and may need truncation or summarization.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “1.5 Multi-turn conversation” — tips.
</details>

## Question 7

What does `stream=True` change in the demonstrated API call?

A. How generated content is delivered and displayed over time.

B. The model’s underlying reasoning and final answer quality.

C. The API key’s permissions.

D. Which messages are included in the prompt.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Streaming shows pieces of the response as they are generated; the lesson says it does not change reasoning or final quality.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “1.6 Streaming output”.
</details>

## Question 8

Why can identical prompts produce slightly different answers?

A. Sampling-based decoding can choose different tokens from a probability distribution.

B. Tokenization randomly changes the prompt each time.

C. The API drops the system message on alternating calls.

D. The model always uses a different knowledge base.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson explains that stochastic sampling can produce variation for the same input.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “2.1 The LLM’s text-generation workflow” — decoding and autoregression.
</details>

## Question 9

What is the purpose of tokenization?

A. Convert input text into token units associated with vocabulary IDs.

B. Turn token IDs into semantically rich vectors.

C. Store document vectors for retrieval.

D. Choose the final output sentence.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Tokenization breaks text into tokens and maps them to integer IDs; vectorization is a later step.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “2.1 The LLM’s text-generation workflow” — Stage 1: Tokenization.
</details>

## Question 10

A team wants more predictable output from sampling. Which parameter direction does the lesson associate with greater determinism?

A. Lower temperature, which concentrates probability on fewer high-probability tokens.

B. Higher temperature, which flattens the distribution.

C. Higher top-p, which disables sampling entirely.

D. More conversation history, which guarantees identical output.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Lower temperature sharpens the distribution and makes output more deterministic according to the lesson.

**Source:** `2_1_Building_FAQ_Bot_with_LLM.ipynb` — “2.1 The LLM’s text-generation workflow” — decoding strategies and temperature.
</details>
