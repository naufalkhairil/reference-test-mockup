# Mockup Test: 2 8 Deploy Model

Choose the single best answer for each question.

## Question 1

What is a benefit of invoking a fully managed model API?

A. It gives complete control over the physical server.

B. It removes all API costs.

C. It avoids initial infrastructure investment and simplifies operations.

D. It always supports every custom fine-tuned model.

<details>
<summary>Show answer and explanation</summary>

**Answer: C**

Managed APIs suit early or small-to-medium scenarios where low setup and operations burden matter.

**Source:** `2_8_Deploy_Model.ipynb` — “1. Deploying models in production” — fully managed API advantages.
</details>

## Question 2

Why does the lesson deploy a fine-tuned model with vLLM?

A. It replaces the model weights with prompts.

B. It is a vector database.

C. It creates training data automatically.

D. vLLM simplifies serving and supports efficient inference and concurrent requests.

<details>
<summary>Show answer and explanation</summary>

**Answer: D**

The lesson describes vLLM as an inference framework with efficient serving and memory management.

**Source:** `2_8_Deploy_Model.ipynb` — “2. Deploying the model in the test environment”.
</details>

## Question 3

What endpoint is used to test a locally served chat model in the example?

A. `/api/key`.

B. `/v1/chat/completions`.

C. `/v1/embeddings/index`.

D. `/v2/train`.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

The vLLM service is OpenAI API compatible and can be called at the chat completions endpoint.

**Source:** `2_8_Deploy_Model.ipynb` — “2.3 Test service running status”.
</details>

## Question 4

The fine-tuned service runs on port 8001 while the base service uses 8000. What must a test request do?

A. Target port 8001 for the fine-tuned service.

B. Switch to the vector database port.

C. Change the model response role.

D. Use both ports in one URL.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

The notebook specifically instructs changing the request port to 8001 when testing the fine-tuned service.

**Source:** `2_8_Deploy_Model.ipynb` — “2.2.2 Deploying fine-tuned Model” and “2.3 Test service running status”.
</details>

## Question 5

In the lesson’s wrk experiment, what changes between the two test runs?

A. The model is retrained for each run.

B. Concurrency changes from 1 to 10 while duration remains 10 seconds.

C. The endpoint changes from chat to embeddings.

D. The test duration changes from 1 to 10 minutes.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

The commands use concurrency levels 1 and 10 and a 10-second duration.

**Source:** `2_8_Deploy_Model.ipynb` — “2.4 Evaluate service performance”.
</details>

## Question 6

A team needs serverless GPU inference with fast automatic scaling and low infrastructure management. Which service is highlighted?

A. A local Jupyter notebook.

B. A manually managed ECS instance only.

C. A vector database.

D. Function Compute (FC).

<details>
<summary>Show answer and explanation</summary>

**Answer: D**

FC is described as serverless GPU service with automatic scaling and pay-as-you-go operation.

**Source:** `2_8_Deploy_Model.ipynb` — “3.1 Deploying models using FC”.
</details>

## Question 7

A production workload needs real-time synchronous inference and model warm-up to reduce initial response delay. Which service fits the lesson’s description?

A. Notebook autosave.

B. PAI-EAS.

C. Static object storage.

D. A batch-only inference endpoint.

<details>
<summary>Show answer and explanation</summary>

**Answer: B**

PAI-EAS targets online synchronous inference and offers warm-up; it may have higher fixed costs.

**Source:** `2_8_Deploy_Model.ipynb` — “3.2 Deploying models using PAI-EAS”.
</details>

## Question 8

When might ECS be preferred for model deployment?

A. The team needs deep control over server configuration and can handle operations.

B. The model must run exclusively in a browser.

C. The team wants no infrastructure management under any conditions.

D. The workload only requires a model API key.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

ECS gives control over hardware, OS, and software but requires more operations expertise.

**Source:** `2_8_Deploy_Model.ipynb` — “3.3 Deploying models using Elastic Computing Service or Container Services”.
</details>

## Question 9

A team already operates Kubernetes and wants GPU containers while offloading cluster operations. What option does the lesson mention?

A. ACS.

B. A model leaderboard.

C. A raw local process.

D. An embedding endpoint.

<details>
<summary>Show answer and explanation</summary>

**Answer: A**

ACS lets GPU-powered containers run in a familiar Kubernetes environment while offloading cluster management.

**Source:** `2_8_Deploy_Model.ipynb` — “3.3 Deploying models using Elastic Computing Service or Container Services”.
</details>

## Question 10

How should a team choose among deployment services?

A. Optimize only for the lowest initial price.

B. Always use the same service for every model.

C. Balance core requirements, model compatibility, and operational complexity with team capabilities.

D. Choose whichever has the most features regardless of use case.

<details>
<summary>Show answer and explanation</summary>

**Answer: C**

The lesson’s decision recommendations consider requirements, compatibility, and operational capabilities.

**Source:** `2_8_Deploy_Model.ipynb` — “3.4 Cloud service solution comparison and decision recommendations”.
</details>
