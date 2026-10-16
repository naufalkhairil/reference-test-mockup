# Mockup Test: 2 8 Deploy Model

Choose the single best answer for each question.

## Question 1

What is a benefit of invoking a fully managed model API?

A. It avoids initial infrastructure investment and simplifies operations.

B. It always supports every custom fine-tuned model.

C. It gives complete control over the physical server.

D. It removes all API costs.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

Managed APIs suit early or small-to-medium scenarios where low setup and operations burden matter.

**Source:** `2_8_Deploy_Model.ipynb` — “1. Deploying models in production” — fully managed API advantages.
</details>

## Question 2

Why does the lesson deploy a fine-tuned model with vLLM?

A. vLLM simplifies serving and supports efficient inference and concurrent requests.

B. It creates training data automatically.

C. It is a vector database.

D. It replaces the model weights with prompts.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson describes vLLM as an inference framework with efficient serving and memory management.

**Source:** `2_8_Deploy_Model.ipynb` — “2. Deploying the model in the test environment”.
</details>

## Question 3

What endpoint is used to test a locally served chat model in the example?

A. `/v1/chat/completions`.

B. `/v1/embeddings/index`.

C. `/api/key`.

D. `/v2/train`.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The vLLM service is OpenAI API compatible and can be called at the chat completions endpoint.

**Source:** `2_8_Deploy_Model.ipynb` — “2.3 Test service running status”.
</details>

## Question 4

The fine-tuned service runs on port 8001 while the base service uses 8000. What must a test request do?

A. Target port 8001 for the fine-tuned service.

B. Change the model response role.

C. Use both ports in one URL.

D. Switch to the vector database port.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The notebook specifically instructs changing the request port to 8001 when testing the fine-tuned service.

**Source:** `2_8_Deploy_Model.ipynb` — “2.2.2 Deploying fine-tuned Model” and “2.3 Test service running status”.
</details>

## Question 5

In the lesson’s wrk experiment, what changes between the two test runs?

A. Concurrency changes from 1 to 10 while duration remains 10 seconds.

B. The model is retrained for each run.

C. The endpoint changes from chat to embeddings.

D. The test duration changes from 1 to 10 minutes.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The commands use concurrency levels 1 and 10 and a 10-second duration.

**Source:** `2_8_Deploy_Model.ipynb` — “2.4 Evaluate service performance”.
</details>

## Question 6

A team needs serverless GPU inference with fast automatic scaling and low infrastructure management. Which service is highlighted?

A. Function Compute (FC).

B. A manually managed ECS instance only.

C. A local Jupyter notebook.

D. A vector database.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

FC is described as serverless GPU service with automatic scaling and pay-as-you-go operation.

**Source:** `2_8_Deploy_Model.ipynb` — “3.1 Deploying models using FC”.
</details>

## Question 7

A production workload needs real-time synchronous inference and model warm-up to reduce initial response delay. Which service fits the lesson’s description?

A. PAI-EAS.

B. Static object storage.

C. A batch-only inference endpoint.

D. Notebook autosave.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

PAI-EAS targets online synchronous inference and offers warm-up; it may have higher fixed costs.

**Source:** `2_8_Deploy_Model.ipynb` — “3.2 Deploying models using PAI-EAS”.
</details>

## Question 8

When might ECS be preferred for model deployment?

A. The team needs deep control over server configuration and can handle operations.

B. The team wants no infrastructure management under any conditions.

C. The workload only requires a model API key.

D. The model must run exclusively in a browser.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

ECS gives control over hardware, OS, and software but requires more operations expertise.

**Source:** `2_8_Deploy_Model.ipynb` — “3.3 Deploying models using Elastic Computing Service or Container Services”.
</details>

## Question 9

A team already operates Kubernetes and wants GPU containers while offloading cluster operations. What option does the lesson mention?

A. ACS.

B. A raw local process.

C. A model leaderboard.

D. An embedding endpoint.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

ACS lets GPU-powered containers run in a familiar Kubernetes environment while offloading cluster management.

**Source:** `2_8_Deploy_Model.ipynb` — “3.3 Deploying models using Elastic Computing Service or Container Services”.
</details>

## Question 10

How should a team choose among deployment services?

A. Balance core requirements, model compatibility, and operational complexity with team capabilities.

B. Choose whichever has the most features regardless of use case.

C. Optimize only for the lowest initial price.

D. Always use the same service for every model.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The lesson’s decision recommendations consider requirements, compatibility, and operational capabilities.

**Source:** `2_8_Deploy_Model.ipynb` — “3.4 Cloud service solution comparison and decision recommendations”.
</details>
