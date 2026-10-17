# Mockup Test: 2 3 Optimize Prompts to Improve FAQ Bot Response Quality

Choose the single best answer for each question.

## Question 1

A bot answers correctly but users want direct links for relevant tools. Why is appending “include tool links” to every user question fragile?

A. It applies an irrelevant instruction to unrelated questions and can make answers awkward.

B. It changes the model’s training data.

C. It prevents retrieval from running.

D. It disables system prompts.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson points out that one-size-fits-all appended instructions can be irrelevant and verbose.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “2. Optimizing Prompts to Improve Response Quality”.
</details>

## Question 2

Which set best represents the basic elements of a useful prompt described in the lesson?

A. Temperature, GPU count, and deployment region.

B. Task objective, context, and background information.

C. API key, endpoint, and Python version.

D. Chunk size, vector dimension, and database name.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

The lesson emphasizes clearly stating the task, context, and background.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “3.1 Basic elements” and “4.1 Clearly express requirements and use delimiters”.
</details>

## Question 3

Why use delimiters around supplied text?

A. They replace the need to state the task.

B. They force the model to use a particular vector database.

C. They separate the content to process from the instructions and reduce ambiguity.

D. They guarantee a correct factual answer.

<details>
<summary>Show answer and explanation</summary>

**Answer: C**

Delimiters make prompt structure clearer and help focus the model on the intended content.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.1 Clearly express requirements and use delimiters”.
</details>

## Question 4

A response should be written for newly hired employees in a welcoming tone. Which prompt element most directly sets the intended reader?

A. Audience.

B. Embedding.

C. Retrieval threshold.

D. Temperature.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The audience specifies who the output is for; role defines the identity the model should assume.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.2 Define Role and Audience”.
</details>

## Question 5

A downstream service must parse the model response. What should the developer specify?

A. Only the intended audience.

B. A few-shot example without format requirements.

C. A structured output format such as JSON, with clear content requirements.

D. A longer natural-language answer with no schema.

<details>
<summary>Show answer and explanation</summary>

**Answer: C**

The lesson recommends explicit structured formats for programmatic use.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.3 Specifying output formats”.
</details>

## Question 6

The model returns valid JSON but inconsistent style and structure. What prompting technique can help?

A. Use streaming output.

B. Provide few-shot examples that demonstrate the desired pattern.

C. Increase the maximum token limit.

D. Remove all context.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

Examples communicate the target format and style, beyond a format label alone.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.4 Providing few-shot examples”.
</details>

## Question 7

A general-purpose model struggles with a multi-step math task. What technique does the lesson describe for eliciting more deliberate reasoning?

A. Removing all task context.

B. Chain-of-thought prompting that asks for step-by-step reasoning.

C. Switching to exact-match retrieval.

D. Using only a role name.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

For general-purpose models, the lesson presents CoT as a way to guide complex reasoning tasks.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.5 Giving the model ‘thinking’ time”.
</details>

## Question 8

A prompt writer wants the model to help improve a weak prompt. What is meta prompting?

A. Ask users to rewrite every question.

B. Use a second vector database to rerank answers.

C. Set temperature to zero and stop iterating.

D. Have the model analyze the prompt and suggest or produce an improved prompt.

<details>
<summary>Show answer and explanation</summary>

**Answer: D**

Meta prompting uses the model as a prompt coach to analyze and optimize prompts.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.6 Meta Prompting: Let the LLM Be Your Prompt Coach”.
</details>

## Question 9

Why use a reference answer in a multi-round prompt optimization loop?

A. It ensures every prompt has identical wording.

B. It eliminates the need for evaluation data.

C. It replaces the generation model.

D. It gives the evaluator a target for identifying specific gaps in the generated answer.

<details>
<summary>Show answer and explanation</summary>

**Answer: D**

A reference answer enables concrete gap analysis before the optimizer revises the prompt.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “Multi-Round Iteration: Introducing Reference Answers for Gap Analysis”.
</details>

## Question 10

Why should an AI Judge be evaluated on a separate evaluation set while its prompt is iteratively improved?

A. To detect overfitting to the examples used to develop the judge.

B. To prevent the judge from returning structured output.

C. To increase the model context window.

D. To ensure all answers have the same length.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson treats judge prompt development like classifier training and uses evaluation performance to detect overfitting.

**Source:** `2_3_Optimize_Prompts_to_Improve_FAQ_Bot_Response_Quality.ipynb` — “4.7 Let the LLM Help You Build a Custom ‘AI Judge’” and “4.7.1 Prepare and Split the Dataset”.
</details>
