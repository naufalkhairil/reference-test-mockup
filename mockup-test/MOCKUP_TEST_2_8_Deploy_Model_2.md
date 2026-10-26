# Professional Exam: Deploying Models as Inference Services

Choose the single best answer for each question. This exam is grounded in the course notebook `2_8_Deploy_Model.ipynb` (Alibaba Cloud ACP LLM course). It is a source-grounded practice draft, not a validated or official certification exam.

## Question 1

A startup is building a conversational application on `qwen-plus` and is considering whether to call the fully managed Alibaba Cloud API directly instead of deploying anything themselves. According to the notebook, which of the following is a genuine advantage of direct model invocation?

A. Full control over the serving environment, operating system, and model dependencies.

B. Pay-as-you-go billing based on token usage, avoiding upfront investment and idle GPU resource waste, with scaling, monitoring, and version upgrades handled by the provider.

C. Unlimited request throughput, since managed services are exempt from rate limiting.

D. The ability to serve any custom fine-tuned model, even one the provider's API does not host.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Pay-as-you-go billing based on token usage, avoiding upfront investment and idle GPU resource waste, with scaling, monitoring, and version upgrades handled by the provider.**

The notebook lists three advantages of directly invoking fully managed API services: direct invocation with no manual deployment, pay-as-you-go billing based on token usage that avoids upfront costs and idle GPU waste, and no operational overhead because scaling, monitoring, and model version upgrades are handled automatically by the provider. It calls this approach ideal for early-stage businesses or small- to medium-scale scenarios.

Option D is the instructive distractor because it inverts a stated limitation: the notebook warns that "if your use case requires a custom fine-tuned model that isn't supported by the provider's API, direct invocation may not meet your needs." Option C is contradicted by the rate-limiting note (QPM/TPM limits apply), and A describes self-managed deployment (e.g., ECS), the opposite of a managed API.

**Source:** `2_8_Deploy_Model.ipynb` — Section 1 "Direct model invocation (No deployment required)" (advantage bullet list, rate-limiting note, and custom-fine-tuned-model caveat).
</details>

## Question 2

You run `vllm serve "./model/qwen2_5-1_5b-instruct" --load-format "safetensors" --port 8000` in a terminal, and it prints "Uvicorn running on http://0.0.0.0:8000". According to the notebook, what does this service expose, and how can you verify it is running correctly?

A. A proprietary binary protocol that requires the vLLM-specific client SDK to call.

B. A web dashboard on port 8000 where you chat with the model interactively in a browser.

C. An OpenAI-compatible interface that can only be consumed through the Python OpenAI library.

D. An HTTP interface compatible with the OpenAI API — you can send a cURL POST to `/v1/chat/completions` to test inference and query `/v1/models` to list the deployed models.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — An HTTP interface compatible with the OpenAI API — you can send a cURL POST to `/v1/chat/completions` to test inference and query `/v1/models` to list the deployed models.**

The notebook states that vLLM starts "a service with an HTTP interface compatible with the OpenAI API," that once running you can test inference "by calling standard endpoints such as `/v1/chat/completions`," and demonstrates exactly this with a `curl -X POST http://localhost:8000/v1/chat/completions` request. Section 2.3 adds that the server is compatible with the `/v1/models` endpoint for viewing deployed models, and that a successful response indicates the service is running properly.

Option C is the tempting near-miss: OpenAI-compatible means the *response format* matches OpenAI's API, so plain HTTP tools like cURL work — it does not require the OpenAI Python library. A and B contradict the demonstrated cURL-over-HTTP testing flow.

**Source:** `2_8_Deploy_Model.ipynb` — Section 2 "Deploying the model in the test environment" (vLLM introduction), Section 2.2.1 (serve command and Uvicorn startup message), and Section 2.3 "Test service running status" (cURL examples for `/v1/chat/completions` and `/v1/models`).
</details>

## Question 3

You started the vLLM service in the foreground and noticed that closing the terminal window immediately terminates it. You need the service to keep running in the background after the terminal closes, with its logs written to a file. According to the notebook, what is the recommended command?

A. `nohup vllm serve "./model/qwen2_5-1_5b-instruct" --load-format "safetensors" --port 8000 > vllm.log 2>&1 &`

B. `vllm serve "./model/qwen2_5-1_5b-instruct" --load-format "safetensors" --port 8000 &` — plain backgrounding is sufficient to survive terminal closure.

C. Keep the terminal open but disable the machine's screen lock so the session is never considered idle.

D. `vllm serve ... --install-service` to register vLLM as a system service managed by the OS.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — `nohup vllm serve "./model/qwen2_5-1_5b-instruct" --load-format "safetensors" --port 8000 > vllm.log 2>&1 &`**

The notebook explicitly notes that "closing the terminal window will immediately terminate the model service," and then gives the exact remedy: "If you want the service to run continuously in the background—even after closing the terminal—you can use the following command," followed by the `nohup ... > vllm.log 2>&1 &` form, with logs stored in `vllm.log`.

Option B is the tempting distractor: the notebook's own statement that closing the terminal kills the service is why it prescribes `nohup` (plus output redirection), not a bare `&`. C does not meet the requirement of surviving terminal closure, and D invents a flag the notebook never mentions.

**Source:** `2_8_Deploy_Model.ipynb` — Section 2.2.1 "Deploying open source models" (terminal-closure warning and the `nohup vllm serve ... > vllm.log 2>&1 &` background command block).
</details>

## Question 4

The base-model service is already running on port 8000. You now want to serve the fine-tuned model from Section 2.7 — specifically the version whose LoRA weights have been fused with the base model — alongside it for A/B comparison. According to the notebook's optional deployment step, what should you do?

A. Stop the base-model service first, then serve the fine-tuned model on port 8000, since only one vLLM service can run at a time.

B. Serve the fine-tuned checkpoint on the same port 8000 with a `--load-format lora` flag so both models share one process.

C. Run `vllm serve "./output/qwen2_5-1_5b-instruct/v0-202xxxxx-xxxxxx/checkpoint-xxx-merged" --load-format "safetensors" --port 8001`, pointing at the merged checkpoint directory and using a different port to avoid conflicts.

D. Copy the merged weights over the files in `./model/qwen2_5-1_5b-instruct` and restart the single service so it serves the fine-tuned model.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Run `vllm serve "./output/qwen2_5-1_5b-instruct/v0-202xxxxx-xxxxxx/checkpoint-xxx-merged" --load-format "safetensors" --port 8001`, pointing at the merged checkpoint directory and using a different port to avoid conflicts.**

Section 2.2.2 does exactly this: it deploys "the merged version of the fine-tuned model (where LoRA weights have been fused with the base model)" from the `output` directory, and explains that `--port 8001` "uses a different port than the one in Section 2.2.1 (which used port 8000) to avoid conflicts," starting "a second inference service specifically for the fine-tuned model."

Option A is wrong because the notebook runs both services concurrently. B invents a flag and a single-process sharing mode the notebook never describes. D destroys the base-model deployment and makes A/B comparison impossible.

**Source:** `2_8_Deploy_Model.ipynb` — Section 2.2.2 "Deploy fine-tuned Model (Optional)" (merged-checkpoint `vllm serve` command on port 8001 and the port-conflict explanation).
</details>

## Question 5

You benchmark the deployed service with `wrk`, first at concurrency `-c1` and then at `-c10`, each for 10 seconds. Results: QPS rises from 3.30 to 20.08 (about 6×) and average latency rises from 324.61 ms to 426.84 ms (about 30%), and the second test records two timeout errors. According to the notebook, what is the correct interpretation?

A. QPS scaled with concurrency at no resource cost because vLLM caches identical responses during stress tests.

B. The two timeouts are an artifact of the 10-second `-d` test window and do not reflect server behavior.

C. The latency increase shows that the OpenAI-compatible API layer adds fixed per-request overhead only under concurrency.

D. Under higher concurrency the server load exceeded its processing capacity, and the limited model inference performance on this device caused some requests to time out — motivating cloud deployment for low-latency, high-concurrency needs.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Under higher concurrency the server load exceeded its processing capacity, and the limited model inference performance on this device caused some requests to time out — motivating cloud deployment for low-latency, high-concurrency needs.**

The notebook's analysis of these exact numbers states: "increasing concurrency from 1 to 10 improved QPS by approximately 6 times (from 3.30 to 20.08) while average latency increased by about 30% (from 324.61 to 426.84 ms). Notably, in the second test, two timeout errors occurred. This happened because, under higher concurrency, the server load exceeded its processing capacity, and limited model inference performance led to some requests timing out." Section 3 then uses this result to argue that the local device "struggles to meet inference requirements for low latency and high concurrency," motivating cloud deployment.

A invents a caching explanation the notebook never offers; B dismisses the timeouts, which the notebook treats as a real capacity signal; C misattributes the latency growth to the API layer rather than to server load.

**Source:** `2_8_Deploy_Model.ipynb` — Section 2.4 "Evaluate service performance" (wrk commands and the results-interpretation paragraph) and the opening of Section 3 "Deploying models on the cloud".
</details>

## Question 6

Your company needs to expose an internal document-summarization model as a service. Traffic is low — roughly a few hundred invocations per day — mostly triggered by scheduled and event-driven jobs, and the team is very cost-sensitive; a slightly slower first response after idle periods is acceptable. According to the notebook's cloud-service guidance, which option fits best?

A. PAI-EAS, because its model warm-up feature guarantees the lowest possible first-response latency.

B. Function Compute (FC), because its serverless, pay-as-you-go model bills by request volume with no cost when idle and scales automatically — a good match for lightweight, low-frequency, non-real-time tasks, accepting cold-start latency as the trade-off.

C. Container Service ACK, because a Kubernetes cluster provides the most headroom for future traffic growth.

D. A dedicated Elastic GPU Service instance, because owning the hardware gives the best cost per query at any traffic level.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Function Compute (FC), because its serverless, pay-as-you-go model bills by request volume with no cost when idle and scales automatically — a good match for lightweight, low-frequency, non-real-time tasks, accepting cold-start latency as the trade-off.**

The notebook describes FC as offering "Serverless GPU services... automatic scaling within seconds and a pay-as-you-go billing model — ideal for reducing costs when models are used infrequently," and lists its suitable scenarios as "lightweight inference tasks, low-frequency access scenarios, use cases with less stringent real-time requirements (e.g., offline batch processing, scheduled or event-triggered tasks)." The decision recommendations add: "Low-cost lightweight services / low-frequency non-real-time tasks → Use Function Compute (FC)... Suitable for small tools handling hundreds of queries per day" — matching the stem's volume. The stated FC limitations (cold-start latency, harder debugging) are acceptable under the stem's constraints.

Option A optimizes for a real-time guarantee the stem explicitly does not need, and the notebook notes PAI-EAS "typically has higher fixed costs" and "may be less cost-effective than FC" for low traffic. C and D bring operational overhead and fixed costs the notebook reserves for other scenarios.

**Source:** `2_8_Deploy_Model.ipynb` — Section 3.1 "Deploying models using FC" (capabilities, limitations, suitable scenarios) and Section 3.4 "Cloud service solution comparison and decision recommendations" (recommendation 1 and 4, "hundreds of queries per day").
</details>

## Question 7

You must deploy a customer-facing model as an online service with real-time synchronous inference. Requirements: elastic scaling, blue-green deployment for safe releases, real-time resource monitoring, version control, and an immediate response right after deployment (no long initial warm-up for the first user requests). According to the notebook, which service and feature combination best fits?

A. PAI-EAS, which provides elastic scaling, blue-green deployment, resource-group management, version control, and real-time monitoring, plus a model warm-up feature that pre-initializes the model before going live; Spot Instances can reduce its higher fixed costs.

B. Function Compute, because pay-by-request billing inherently eliminates first-request latency for real-time services.

C. Model Studio, because one-click deployment includes blue-green releases for any custom model you upload.

D. An edge-cloud collaborative setup, with a small on-device model handling the first responses until the cloud instance wakes up.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — PAI-EAS, which provides elastic scaling, blue-green deployment, resource-group management, version control, and real-time monitoring, plus a model warm-up feature that pre-initializes the model before going live; Spot Instances can reduce its higher fixed costs.**

Section 3.2 lists exactly these PAI-EAS enterprise features (elastic scaling, blue-green deployment, resource-group management, version control, real-time resource monitoring), states it "is particularly suitable for real-time synchronous inference scenarios," and highlights the model warm-up feature that "pre-initializes the model before going live — ensuring the service is ready to respond immediately after deployment." It also notes the cost caveat and the Spot Instances mitigation, all reflected in the keyed option.

Option B contradicts the notebook: FC's cold-start latency ("the instance must restart, leading to longer initial response times") is precisely why the notebook directs real-time workloads away from FC. C attributes blue-green deployment of arbitrary custom models to Model Studio, which the notebook positions for rapid deployment of hosted LLMs like the Qwen series. D applies an unrelated architecture from the further-reading section.

**Source:** `2_8_Deploy_Model.ipynb` — Section 3.2 "Deploying models using PAI-EAS" (feature list, real-time synchronous inference fit, warm-up feature, Spot Instance cost note); contrast with Section 3.1 FC cold-start limitation.
</details>

## Question 8

A large engineering organization with an experienced containerization/DevOps team needs to run large-scale distributed inference for a complex microservices architecture with mixed workloads, integrating CI/CD and load balancing. According to the notebook's comparison and recommendations, which deployment path is most appropriate?

A. Model Studio, because its visual interface removes the need for the DevOps team entirely.

B. Function Compute, because serverless functions are the notebook's recommendation for complex multi-step processing pipelines.

C. Container Service ACK (or Container Compute Service ACS), which provides Kubernetes cluster deployment with CI/CD integration, automatic scaling, and load balancing for complex microservice architectures and large-scale distributed inference; ACS additionally offloads cluster operations and maintenance.

D. PAI-EAS, because the notebook positions it as the Kubernetes-native option for mixed workloads.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Container Service ACK (or Container Compute Service ACS), which provides Kubernetes cluster deployment with CI/CD integration, automatic scaling, and load balancing for complex microservice architectures and large-scale distributed inference; ACS additionally offloads cluster operations and maintenance.**

The comparison table in Section 3.4 assigns ACK/ACS exactly this niche: "Kubernetes cluster deployment, integrating CI/CD, automatic scaling, load balancing" for "complex microservice architectures, mixed workloads, large-scale distributed inference or training." Section 3.3's container paragraph adds that teams with containerization experience can use ACK with GPU nodes, and that ACS runs GPU-powered containers "while offloading cluster operations and maintenance." The cost note also acknowledges ACK's comprehensive cost is "justified for large-scale deployments."

Option B inverts the notebook: FC's stated limitations include "increased debugging difficulty... especially in multi-step processing pipelines," and the notebook directs such workloads to "more centralized deployment options." A discards the team's stated capability and misfits the scale, and D mislabels PAI-EAS, which the table positions for medium/small deep-learning model serving rather than Kubernetes microservice estates.

**Source:** `2_8_Deploy_Model.ipynb` — Section 3.3 (ACK/ACS paragraphs with deployment references) and Section 3.4 comparison table row "Container Service ACK/Container Compute Service ACS" plus cost-control recommendation 4.
</details>

## Question 9

A team needs to run an LLM requiring deep environment customization — specific OS settings, uncommon framework versions, and special dependencies — with consistent long-running performance and no cold-start delays. They have strong operations expertise and want predictable costs with full resource control. According to the notebook, which option and reasoning fit best?

A. Function Compute, because serverless platforms provide full control over server configuration and operating systems.

B. Model Studio, because it supports installation of any framework and dependency at the IaaS level.

C. PAI-EAS, because the notebook identifies it as the only cloud option without cold-start delays.

D. Elastic Compute Service (ECS)/Elastic GPU Service, because it offers full control over server configurations, operating systems, and software environments, provides stable resources without serverless cold-start delays, can combine with ESS for scaling and SLB for high availability, and suits enterprises with strong DevOps teams needing predictable costs — at the price of higher operational overhead.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Elastic Compute Service (ECS)/Elastic GPU Service, because it offers full control over server configurations, operating systems, and software environments, provides stable resources without serverless cold-start delays, can combine with ESS for scaling and SLB for high availability, and suits enterprises with strong DevOps teams needing predictable costs — at the price of higher operational overhead.**

Section 3.3 describes ECS as "offering full control over server configurations, operating systems, and software environments... ideal for models requiring deep customization or specific dependencies," notes it "provides stable computing resources and avoids cold-start delays common in serverless platforms," lists the ESS/SLB/security-group combinations, and gives as suitable scenarios "LLMs requiring high customization, consistent performance, and long-term operation" and "enterprises with strong DevOps teams and a need for predictable costs and full resource control" — every element of the stem. The comparison table similarly routes "custom environments or complex dependencies" to Elastic GPU Service or ACK.

Option A inverts FC's serverless nature (no OS-level control; cold starts exist). C overstates: the notebook credits ECS with avoiding cold starts and gives PAI-EAS a warm-up feature, never calling it the only cold-start-free option. B attributes IaaS-level flexibility to Model Studio, which the notebook positions as a hosted LLM platform that encapsulates underlying complexity.

**Source:** `2_8_Deploy_Model.ipynb` — Section 3.3 "Deploying models using Elastic Computing Service or Container Services" (ECS paragraphs, suitable/unsuitable scenarios) and Section 3.4 comparison table row "Elastic GPU Service".
</details>

## Question 10

The notebook's further-reading section describes an edge-cloud collaborative deployment, illustrated by Rakuten's end-side companion voice bot built with a Tongyi LLM. How is work divided between the edge device and the cloud in that example?

A. The full LLM runs locally on the client device, and the cloud is used only to store conversation logs for later analysis.

B. A small, fine-tuned model runs locally on the client device handling basic tasks such as wake-word detection and input preprocessing, while the cloud hosts the full LLM that performs deep reasoning and generates responses; preprocessed data is sent to the cloud and results return quickly.

C. All inference runs in the cloud, and edge devices only render the user interface, since latency-sensitive tasks cannot run on edge hardware.

D. The model layers are split in half — the first half runs on the device and the second half in the cloud — for every request.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — A small, fine-tuned model runs locally on the client device handling basic tasks such as wake-word detection and input preprocessing, while the cloud hosts the full LLM that performs deep reasoning and generates responses; preprocessed data is sent to the cloud and results return quickly.**

The Rakuten use-case description states precisely this division: "The 'end' refers to a small, fine-tuned model running locally on the client device, responsible for basic tasks like wake-word detection and input preprocessing. The 'cloud' hosts the full LLM, which performs deep reasoning and generates responses. Preprocessed data is sent to the cloud, and results are returned quickly—balancing speed, efficiency, and intelligence." This matches the section's general principle that "simple or latency-sensitive tasks are processed on edge devices... complex computations are offloaded to the cloud."

Option C contradicts that principle by claiming latency-sensitive tasks cannot run on edge devices — the notebook says the opposite. A inverts the split, and D describes layer-splitting, an architecture the notebook never mentions.

**Source:** `2_8_Deploy_Model.ipynb` — "Further reading" section, "Edge-Cloud Collaborative Deployment" (Rakuten / Tongyi LLM voice-bot use-case example).
</details>

---

**Answer-key balance check:** B, D, A, C, D, B, A, C, D, B — A×2, B×3, C×2, D×3; no consecutive-letter pattern.
