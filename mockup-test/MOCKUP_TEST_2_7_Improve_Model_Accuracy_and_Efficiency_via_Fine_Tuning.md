# Mockup Test: 2 7 Improve Model Accuracy and Efficiency via Fine Tuning

Choose the single best answer for each question.

## Question 1

When is fine-tuning most suitable according to the lesson’s motivation?

A. When a model needs better performance on a specific domain or task using representative examples.

B. Whenever a prompt has not yet been tested.

C. When private documents only need to be retrieved at query time.

D. To make every model larger.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Fine-tuning adapts model behavior to domain/task examples; it is distinct from retrieving changing knowledge.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “Fine-tuning overview and use cases”.
</details>

## Question 2

A company’s policy documents change often. Which approach is generally better for supplying current facts?

A. RAG over the updated documents.

B. Fine-tune once and never update.

C. Increase temperature.

D. Use a larger training epoch count.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Frequently changing factual knowledge is more naturally kept current through retrieval.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “RAG versus fine-tuning” (lesson comparison).
</details>

## Question 3

What is supervised fine-tuning data typically organized as?

A. Examples pairing an input or instruction with a desired output.

B. A list of API keys and endpoints.

C. Unlabeled GPU utilization metrics only.

D. A vector index with no text.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Supervised examples show the model the input-output behavior to learn.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “Prepare fine-tuning data”.
</details>

## Question 4

Why should fine-tuning examples be high quality and representative?

A. The model learns patterns from them, so poor or narrow examples can teach the wrong behavior.

B. They make the tokenizer unnecessary.

C. They ensure the model never needs evaluation.

D. They automatically update the knowledge base.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Data quality and coverage shape the learned behavior and generalization.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “Dataset preparation and quality”.
</details>

## Question 5

What is the purpose of splitting data into training and validation or test subsets?

A. Train on one portion and assess generalization on examples not used for fitting.

B. Increase the number of training epochs.

C. Make all examples identical.

D. Avoid measuring model quality.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Held-out data helps reveal whether the model generalizes beyond the examples it learned from.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “Dataset splitting / evaluation”.
</details>

## Question 6

What does a LoRA fine-tuning approach aim to reduce?

A. The number of trainable parameters and resource requirements compared with updating all model weights.

B. The amount of text in each training example to zero.

C. The need for a base model.

D. The ability to save model checkpoints.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

LoRA uses parameter-efficient adaptation rather than full-model updates.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “LoRA fine-tuning”.
</details>

## Question 7

A fine-tuned model performs well on training examples but poorly on new questions. What is the likely issue?

A. Overfitting or inadequate data coverage.

B. Successful generalization.

C. An API endpoint mismatch by definition.

D. Too much retrieval context.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

A train-test gap suggests memorization or insufficient representative data.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “Evaluate fine-tuned models”.
</details>

## Question 8

Why compare the fine-tuned model against the base model on the same held-out cases?

A. To determine whether fine-tuning actually improves the target behavior.

B. To change the model architecture.

C. To avoid reference answers.

D. To ensure their outputs are identical.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

A controlled comparison shows whether adaptation improves outcomes for the intended task.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “Model evaluation and comparison”.
</details>

## Question 9

What is a useful reason to preserve checkpoints during fine-tuning?

A. They allow recovery, comparison, or deployment of a selected training state.

B. They automatically encrypt every dataset.

C. They replace evaluation.

D. They increase the base model context window.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Checkpoints preserve model states that can be compared or restored.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “Fine-tuning workflow / checkpoints”.
</details>

## Question 10

A small fine-tuned model is cheaper and faster, but slightly less capable. What should guide the deployment choice?

A. Measured task quality alongside latency and cost requirements.

B. Parameter count alone.

C. The model’s name alone.

D. Whether training completed without errors.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson treats accuracy and efficiency as a tradeoff that should be evaluated for the use case.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — “Improve model accuracy and efficiency” — evaluation and trade-offs.
</details>
