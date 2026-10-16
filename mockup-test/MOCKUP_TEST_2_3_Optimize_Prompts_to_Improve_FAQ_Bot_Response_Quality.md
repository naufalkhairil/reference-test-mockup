# Mockup Test: 2 3 Optimize Prompts to Improve FAQ Bot Response Quality

Choose the single best answer for each question.

## Question 1

A bot answers correctly but users want direct links for relevant tools. Why is appending “include tool links” to every user question fragile?

A. It applies an irrelevant instruction to unrelated questions and can make answers awkward.

B. It prevents retrieval from running.

C. It changes the model’s training data.

D. It disables system prompts.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson points out that one-size-fits-all appended instructions can be irrelevant and verbose.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “2. Optimizing Prompts to Improve Response Quality”.
</details>

## Question 2

Which set best represents the basic elements of a useful prompt described in the lesson?

A. Task objective, context, and background information.

B. API key, endpoint, and Python version.

C. Chunk size, vector dimension, and database name.

D. Temperature, GPU count, and deployment region.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson emphasizes clearly stating the task, context, and background.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “3.1 Basic elements” and “4.1 Clearly express requirements and use delimiters”.
</details>

## Question 3

Why use delimiters around supplied text?

A. They separate the content to process from the instructions and reduce ambiguity.

B. They force the model to use a particular vector database.

C. They guarantee a correct factual answer.

D. They replace the need to state the task.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Delimiters make prompt structure clearer and help focus the model on the intended content.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.1 Clearly express requirements and use delimiters”.
</details>

## Question 4

A response should be written for newly hired employees in a welcoming tone. Which prompt element most directly sets the intended reader?

A. Audience.

B. Temperature.

C. Embedding.

D. Retrieval threshold.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The audience specifies who the output is for; role defines the identity the model should assume.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.2 Define Role and Audience”.
</details>

## Question 5

A downstream service must parse the model response. What should the developer specify?

A. A structured output format such as JSON, with clear content requirements.

B. A longer natural-language answer with no schema.

C. Only the intended audience.

D. A few-shot example without format requirements.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson recommends explicit structured formats for programmatic use.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.3 Specifying output formats”.
</details>

## Question 6

The model returns valid JSON but inconsistent style and structure. What prompting technique can help?

A. Provide few-shot examples that demonstrate the desired pattern.

B. Increase the maximum token limit.

C. Remove all context.

D. Use streaming output.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Examples communicate the target format and style, beyond a format label alone.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.4 Providing few-shot examples”.
</details>

## Question 7

A general-purpose model struggles with a multi-step math task. What technique does the lesson describe for eliciting more deliberate reasoning?

A. Chain-of-thought prompting that asks for step-by-step reasoning.

B. Removing all task context.

C. Using only a role name.

D. Switching to exact-match retrieval.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

For general-purpose models, the lesson presents CoT as a way to guide complex reasoning tasks.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.5 Giving the model ‘thinking’ time”.
</details>

## Question 8

A prompt writer wants the model to help improve a weak prompt. What is meta prompting?

A. Have the model analyze the prompt and suggest or produce an improved prompt.

B. Use a second vector database to rerank answers.

C. Ask users to rewrite every question.

D. Set temperature to zero and stop iterating.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Meta prompting uses the model as a prompt coach to analyze and optimize prompts.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.6 Meta Prompting: Let the LLM Be Your Prompt Coach”.
</details>

## Question 9

Why use a reference answer in a multi-round prompt optimization loop?

A. It gives the evaluator a target for identifying specific gaps in the generated answer.

B. It replaces the generation model.

C. It ensures every prompt has identical wording.

D. It eliminates the need for evaluation data.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

A reference answer enables concrete gap analysis before the optimizer revises the prompt.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “Multi-Round Iteration: Introducing Reference Answers for Gap Analysis”.
</details>

## Question 10

Why should an AI Judge be evaluated on a separate evaluation set while its prompt is iteratively improved?

A. To detect overfitting to the examples used to develop the judge.

B. To increase the model context window.

C. To ensure all answers have the same length.

D. To prevent the judge from returning structured output.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson treats judge prompt development like classifier training and uses evaluation performance to detect overfitting.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.7 Let the LLM Help You Build a Custom ‘AI Judge’” and “4.7.1 Prepare and Split the Dataset”.
</details>
