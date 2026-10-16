# Mockup Test: 2 A LLM Application Security and Compliance

Choose the single best answer for each question.

## Question 1

A user tries to make the bot role-play a finance director to reveal restricted expense standards. What attack does the lesson identify?

A. Prompt injection.

B. Data poisoning.

C. DDoS.

D. Model quantization.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The prompt attempts to manipulate the model’s behavior and bypass its intended restrictions.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “1.1 Prompt injection attacks”.
</details>

## Question 2

A request combines a legitimate database lookup with an appended SQL UPDATE. What is the relevant risk?

A. Command injection against an agent’s tool behavior.

B. A prompt template formatting error.

C. A vector embedding collision.

D. An image moderation failure.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson describes malicious commands embedded in a legitimate request as command injection.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “1.2 Command injection attacks (Agent behavior attacks)”.
</details>

## Question 3

Why is a keyword blacklist an inadequate long-term defense?

A. Attackers can use synonyms or obfuscation, and the list becomes costly to maintain.

B. It prevents the application from using APIs.

C. It always blocks every encoded attack.

D. It cannot inspect text input.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson explains that paraphrases and encoding evade fixed lists while maintaining the list becomes an arms race.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “1.3 Initial defensive measures”.
</details>

## Question 4

What advantage does AI Guardrails provide over relying only on the LLM to refuse unsafe content?

A. A dedicated service can return structured detection results that let an application reliably stop execution.

B. It makes the LLM’s output impossible to vary.

C. It replaces authorization for database tools.

D. It trains the model on private data.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson emphasizes stable structured feedback for applications and consistent input/output risk review.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “2.1 Using AI Guardrails” and text moderation discussion.
</details>

## Question 5

Which AI Guardrails service names are used for checking incoming prompts and generated responses?

A. `query_security_check_intl` and `response_security_check_intl`.

B. `prompt_vector_intl` and `completion_cache_intl`.

C. `input_sql_update` and `output_email_send`.

D. `text_embedding` and `image_generation`.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The notebook uses the query check for input and response check for generated output.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “2.2 Content moderation text” — `query_detect` and `response_detect` examples.
</details>

## Question 6

A company needs to block proprietary project codes in addition to built-in detections. What should it configure?

A. A private lexicon associated with the relevant protection rule.

B. A larger model context window.

C. A public FAQ entry.

D. A lower top-p value.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Custom sensitive terms can be stored in a private lexicon and linked to query or response rules.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “2.3 Centrally manage Your security rules”.
</details>

## Question 7

What response label indicates that a configured private lexicon rule was triggered?

A. `customized`.

B. `nonLabel`.

C. `pass-through`.

D. `training-data`.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson says a custom rule can be verified by `label: customized`.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “2.3 Centrally manage Your security rules”.
</details>

## Question 8

What can the multimodal protection example inspect?

A. Image content and text within images, along with the supplied text.

B. Only filenames and image dimensions.

C. Only generated audio.

D. Database query syntax.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson describes multimodal moderation for image content and text in images.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “2.4 Protecting image content”.
</details>

## Question 9

An image moderation result says `No risk detected` and `Suggestion: pass`. What does the notebook advise?

A. The image is considered safe by that check, and the application can decide whether to allow it.

B. The model must be retrained.

C. The request was a prompt injection.

D. The image should always be rejected.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The example interprets this result as safe and leaves the allow decision to the application.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “2.4 Protecting image content” — sample response.
</details>

## Question 10

A fine-tuning dataset contains a trigger phrase that causes a preset harmful answer. Which risk category is this?

A. Data poisoning.

B. DDoS.

C. Command injection.

D. Context caching.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson’s poisoning example corrupts model behavior with a hidden trigger in training data.

**Source:** `2_A_LLM_Application_Security_and_Compliance.ipynb` — “3.1.1 Risks in training data” — Case 1: Data poisoning.
</details>
