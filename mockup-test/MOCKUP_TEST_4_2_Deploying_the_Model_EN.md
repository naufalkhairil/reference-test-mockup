# Professional Exam: 4.2 Deploying the Model

Choose the single best answer for each question. Answers and rationales are hidden in the expandable review blocks.

## Question 1

What is the key deciding factor when choosing between a cloud service API and self-hosted deployment

A. Self-hosting is always cheaper than a cloud service

B. You need to run the numbers: monthly call volume, GPU operations cost, and the break-even point

C. A cloud service is always faster than self-hosting

D. Only large companies can self-host

<details>
<summary>Show answer and rationale</summary>

**Answer: B — You need to run the numbers: monthly call volume, GPU operations cost, and the break-even point**

There's no absolute right or wrong choice here. A cloud service requires zero operations and is billed by usage, making it well suited to an early stage where scale is still uncertain; self-hosting has a lower cost but requires GPU-operations capability, making it well suited to scenarios with stable, sufficiently large traffic. The essence of the decision is running the numbers: at what monthly call volume does self-hosting become cheaper than the cloud service? This break-even point varies from scenario to scenario.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — embedded lesson quiz and its explanation.

</details>

## Question 2

A three-person startup team is building an AI customer-service product, currently averaging about 500 calls a day, with no dedicated operations staff, using a Qwen-series model. The team wants to launch as quickly as possible to validate their business model. What's the most suitable deployment approach

A. Rent a GPU cloud server and deploy vLLM themselves, giving full control over the inference environment and performance tuning

B. Use the Bailian platform's one-click deployment and integrate directly into the product via its API

C. Use Container Service ACK to build a Kubernetes cluster, making it easier to scale into a microservices architecture later

D. Deploy the model with Function Compute FC, using Serverless pay-as-you-go pricing to lower costs

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Use the Bailian platform's one-click deployment and integrate directly into the product via its API**

Three key constraints drive the choice here: it's a Qwen-series model (natively supported by Bailian), there's no operations staff (ruling out the GPU server and ACK, which both require operations capability), and they want to launch fast (Bailian's one-click deployment is the fastest). Both the GPU cloud server and ACK require substantial operations capability, which doesn't fit a three-person team. Function Compute FC is also operations-free, but it's better suited to low-frequency offline tasks and has cold-start latency issues, which isn't ideal for a customer-service scenario that needs real-time responsiveness. The Bailian platform — with zero operations, a visual console, and direct API calls — is the best choice at this stage.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — embedded lesson quiz and its explanation.

</details>
