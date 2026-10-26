# Professional Exam: Deploying the Model — From Local vLLM Service to Cloud Deployment

**Source:** `4_2_Deploying_the_Model_EN.ipynb` (Alibaba Cloud ACP LLM course, Lesson 4.2)

Choose the single best answer for each question. This exam assesses applied judgment on model deployment: when to call a hosted API versus deploying, operating a vLLM service, interpreting load-test results, and selecting among Alibaba Cloud deployment services (Bailian, Function Compute, PAI-EAS, ECS/GPU cloud servers, ACK/ACS) based on business needs.

## Question 1

An early-stage team with modest, uncertain traffic is considering calling a pre-provisioned Qwen model on Alibaba Cloud through an API instead of deploying anything themselves. According to the lesson, what makes direct API calling attractive at this stage?

A. It bypasses the rate limits that apply to self-deployed model services

B. It guarantees lower latency than any self-deployed service

C. It works just as well for models the team has fine-tuned itself

D. It avoids deployment and operations burden — pay-as-you-go per token, with auto-scaling and model version upgrades handled by the provider — lowering upfront costs and avoiding idle GPU waste

<details>
<summary>Show answer and rationale</summary>

**Answer: D — It avoids deployment and operations burden — pay-as-you-go per token, with auto-scaling and model version upgrades handled by the provider — lowering upfront costs and avoiding idle GPU waste**

Section 1 lists the advantages of calling a fully managed API: direct calling with no deployment, pay-as-you-go token billing, and no operations burden (auto-scaling and version upgrades handled by the provider), and states this approach suits "the early stage of a business, or small-to-medium-scale scenarios" because it lowers upfront costs and avoids wasting idle GPU resources. Option A is the reverse of the source: direct API calls *are* subject to rate limiting (both QPM and TPM on the Bailian API; exceeding them makes requests fail until the limit resets). Option B is never claimed, and option C contradicts the closing caveat that fine-tuned or unsupported models cannot be called directly.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "1. Calling a Model Directly (No Deployment Needed)" (advantages list, suitability statement, and rate-limiting note).
</details>

## Question 2

After completing lesson 4.1, a team has a merged, distilled Qwen3-0.6B checkpoint they want to serve in an application. According to this lesson, why is calling the provider's hosted model API not an option for this model?

A. Because hosted API calls are billed only per token, while the team needs hourly billing

B. Because models under 1B parameters are excluded from hosted API catalogs

C. Because the model has been fine-tuned and is not among the provider's pre-provisioned models — direct calling is not an option, so it must be deployed

D. Because the merged checkpoint must first be converted into a proprietary deployment format

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Because the model has been fine-tuned and is not among the provider's pre-provisioned models — direct calling is not an option, so it must be deployed**

Section 1 states: "if the model has been fine-tuned, or isn't yet supported by the service provider, calling it directly won't be an option." This motivates section 2, which deploys exactly this kind of distilled checkpoint with vLLM (section 2.2.2 picks the latest `checkpoint-*-merged` directory). Options A, B, and D invent constraints the lesson never mentions — in the hands-on path, vLLM loads the merged safetensors checkpoint directly, with no format conversion or billing prerequisite.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "1. Calling a Model Directly (No Deployment Needed)" (final caveat) and "2.2.2 Deploying the Distilled Model (Optional)."
</details>

## Question 3

You start the lesson's vLLM service (`vllm serve ... --gpu-memory-utilization 0.7`) and encounter out-of-memory problems while serving. According to the lesson's parameter guidance, what is the indicated adjustment?

A. Increase the `--port` value to a higher number such as 8100

B. Lower the `--gpu-memory-utilization` parameter

C. Change `--load-format` from "safetensors" to another loading format

D. Close the terminal window and restart the service in the foreground

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Lower the `--gpu-memory-utilization` parameter**

The flag notes under the `vllm serve` command in section 2.2.1 state that `--gpu-memory-utilization 0.7` caps VRAM utilization and that "if you run into out-of-memory issues, consider lowering this parameter." Option A applies the fix for a *different* documented problem — the port notes say to switch from 8000 to e.g. 8100 only "if the port is already in use." Options C and D address unrelated concerns; D also confuses the lesson's warning that closing the terminal window *stops* the service (the documented way to keep it running is `nohup ... &` in the background).

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "2.2.1 Deploying an Open-Source Model" (vllm serve command and its flag explanations, including the terminal/nohup note).
</details>

## Question 4

After starting the vLLM service, how does the lesson verify that it is running correctly?

A. By running the unit-test suite bundled with the ModelScope SDK

B. By sending an HTTP request via cURL to the service's OpenAI-compatible `/v1/chat/completions` endpoint, and optionally checking `/v1/models` to see the list of deployed models

C. By attaching a debugger to the Uvicorn process and inspecting the request handlers

D. By refreshing the model list in the Bailian console

<details>
<summary>Show answer and rationale</summary>

**Answer: B — By sending an HTTP request via cURL to the service's OpenAI-compatible `/v1/chat/completions` endpoint, and optionally checking `/v1/models` to see the list of deployed models**

Section 2.3 tests the service with `curl -X POST http://localhost:<port>/v1/chat/completions ...` and states that "if the request above gets a normal response, the service is running correctly"; it also shows `curl -X GET .../v1/models`. This works because vLLM launches a local server compatible with the OpenAI API (introduced in section 2). Options A, C, and D are not part of the lesson's verification workflow — the local vLLM service has no Bailian console presence, and no debugger or SDK test suite is involved.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "2.3 Testing the Service's Running State" (cURL code cells) and section 2 introduction (OpenAI-compatible HTTP interface).
</details>

## Question 5

The lesson load-tests the deployed service with wrk at concurrency 1 and concurrency 10 (10 s each): QPS rises from 3.30 to 20.08 (≈6×), average latency rises from ~325 ms to ~427 ms (~30%), and the concurrency-10 run records 2 timeout errors. What conclusion does the lesson draw from these results?

A. vLLM's caching strategy is misbehaving under load and should be disabled before production use

B. The service scales linearly with concurrency, so the current device is adequate for high-concurrency production traffic

C. The deploying device's compute power is limited: at higher concurrency the server load exceeded its processing capacity, causing some requests to time out — which motivates moving to scalable cloud deployment

D. Production concurrency should be capped at 1 to guarantee zero timeouts

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The deploying device's compute power is limited: at higher concurrency the server load exceeded its processing capacity, causing some requests to time out — which motivates moving to scalable cloud deployment**

Section 2.4 explains the timeouts this way: "at higher concurrency, the server's load exceeded its processing capacity, and insufficient performance caused some requests to time out." Section 3 then opens: "because the device deploying the model has limited compute power, the model service can't meet **low-latency** and **high-concurrency** inference requirements," which sets up the cloud deployment options. Option B contradicts both the observed timeouts and the latency increase; option A blames the wrong component — the lesson credits vLLM's memory optimization and caching as features that *improve* speed and support high concurrency; option D is an overreaction the lesson never suggests.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "2.4 Evaluating the Service's Performance" (wrk results interpretation paragraph) and "☁3. Deploying a Model on the Cloud" (opening paragraph).
</details>

## Question 6

A team runs an internal document-summarization job triggered by a schedule a few times per day; responses do not need to be real-time. They want minimal cost and no server management. Which cloud deployment option does the lesson recommend, with which reasoning?

A. PAI-EAS, because blue-green deployment protects scheduled workloads

B. Container Service ACK, because Kubernetes is the standard way to schedule batch inference

C. A GPU cloud server, because batch jobs need complete control of the environment

D. Function Compute (FC): serverless GPU with no management of underlying resources, second-level auto-scaling, and pay-as-you-go pricing with no idle cost — well suited to low-frequency, non-real-time tasks such as scheduled or event-triggered jobs, accepting cold-start latency as a trade-off

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Function Compute (FC): serverless GPU with no management of underlying resources, second-level auto-scaling, and pay-as-you-go pricing with no idle cost — well suited to low-frequency, non-real-time tasks such as scheduled or event-triggered jobs, accepting cold-start latency as a trade-off**

Section 3.2 states that FC's pay-as-you-go serverless model "can save a substantial amount of cost for infrequently used models" and is "very well suited to lightweight inference tasks and low-frequency access scenarios that don't require real-time responsiveness (like offline batch processing, scheduled tasks, or event-triggered tasks)," while naming cold-start latency and debugging difficulty as its downsides — a trade-off the stem's non-real-time job can accept. Option A: section 3.3 says EAS may have a higher fixed cost and "for low-frequency use cases, it may not be as cost-effective as Function Compute." Options B and C bring operations burden the team explicitly does not want, and neither is the lesson's recommendation for this profile (section 3.5 routes low-cost, lightweight, low-frequency non-real-time work to FC).

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "3.2 Deploying a Model with Function Compute (FC)," "3.3 Deploying a Model with PAI-EAS" (cost comparison), and "3.5 Comparing Cloud Service Options" (FC row and recommendation 1).
</details>

## Question 7

A product requires real-time synchronous inference from a custom-trained model, and the team is concerned that the first request after going live will take unusually long. According to the lesson, which platform capability directly addresses this concern?

A. PAI-EAS's model warm-up feature, which warms the model service before going live so it enters a normal serving state as soon as it is online

B. Function Compute's cold-start elimination guarantee for GPU functions

C. Bailian's one-click deployment, which removes first-request latency for any model type

D. ECS Spot Instances, which pre-heat the GPU before traffic arrives

<details>
<summary>Show answer and rationale</summary>

**Answer: A — PAI-EAS's model warm-up feature, which warms the model service before going live so it enters a normal serving state as soon as it is online**

Section 3.3 states that EAS "is very well suited to **real-time synchronous inference** scenarios" and that "to address the problem of the first request taking a long time, EAS provides a model warm-up feature, so the model service gets warmed up before going live." Option B inverts the source: cold-start latency is FC's documented *downside* (section 3.2), not a guarantee it eliminates. Options C and D claim capabilities the lesson never attributes to Bailian deployment or Spot Instances (Spot mode is mentioned in 3.3 only as a cost-saving option for EAS).

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "3.3 Deploying a Model with PAI-EAS" (real-time synchronous inference and model warm-up paragraphs).
</details>

## Question 8

A four-person startup is building a customer-facing, real-time AI writing assistant on a Qwen-series model. They expect roughly 600 calls/day initially, have no operations engineer, and want to launch within weeks. Applying the lesson's recommendation logic, which deployment option fits best?

A. Alibaba Cloud Bailian — Qwen-series models are natively supported and preferred there, one-click deployment removes infrastructure and operations burden, and the model is callable directly via API, matching a small team that must launch fast

B. Container Service ACK — so the team can build a microservices architecture from day one

C. A GPU cloud server — for full control of the inference stack and performance tuning

D. Function Compute — because pay-as-you-go pricing is the cheapest way to serve any real-time workload

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Alibaba Cloud Bailian — Qwen-series models are natively supported and preferred there, one-click deployment removes infrastructure and operations burden, and the model is callable directly via API, matching a small team that must launch fast**

Section 3.5's recommendation logic points to Bailian on every axis of this scenario: "Getting an LLM live quickly → Bailian," "Qwen-series models: prefer Bailian," and "No operations burden: non-technical teams → Bailian (visual console-based operation)." The lesson's own quiz (Multiple Choice 4.2.2) applies exactly this reasoning to a near-identical startup profile. Options B and C require operations capability the team lacks — section 3.5 routes ACK to "mature DevOps teams" and GPU cloud servers to teams that can "manage the environment yourself." Option D overgeneralizes FC: section 3.2's cold-start latency makes it a poor fit for a real-time interactive assistant, and "cheapest for any real-time workload" is not a claim the lesson makes.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "3.5 Comparing Cloud Service Options and Decision Recommendations" (recommendations 1–3) and "🔥 Quiz — Multiple Choice 4.2.2" with its explanation.
</details>

## Question 9

An enterprise with a mature DevOps team must deploy a large model with complex custom dependencies for long-running production use, and it values predictable costs and full control of the environment. According to the lesson's analysis of ECS / GPU cloud-server deployment, what is the correct assessment?

A. ECS is unsuitable because server-based deployment always suffers from cold-start latency

B. ECS is a good fit only for Qwen-series models; other models require Bailian

C. ECS should be avoided for long-running workloads because pay-as-you-go pricing inevitably exceeds container-platform costs

D. ECS is a good fit — complete control of configuration, OS, and environment; stable compute without FC-style cold starts; combinable with ESS for elastic scaling and SLB for high availability — provided the organization accepts the required skill level and relatively high maintenance cost

<details>
<summary>Show answer and rationale</summary>

**Answer: D — ECS is a good fit — complete control of configuration, OS, and environment; stable compute without FC-style cold starts; combinable with ESS for elastic scaling and SLB for high availability — provided the organization accepts the required skill level and relatively high maintenance cost**

Section 3.4 states that ECS gives "complete control over the server's configuration, operating system, and environment settings — very useful for models that need a high degree of customization and specific dependencies," provides "stable compute resources, without the cold-start latency issues you get with Function Compute," and combines with ESS (elastic scaling) and SLB (load balancing/high availability). Its "well suited for" list matches the stem: large models needing high customization, stable performance, and long-running operation, plus enterprises valuing cost predictability and resource control — with the stated caveat that configuration/management "requires a certain level of skill and experience" and maintenance cost is relatively high. Option A inverts the cold-start fact (that is FC's downside, not ECS's); options B and C state restrictions the lesson never makes — section 3.5 notes GPU cloud servers support the full TensorFlow/PyTorch/ONNX ecosystem.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "3.4 Deploying a Model with a Cloud Server (ECS) or Container Service" and "3.5" comparison table (GPU cloud server row).
</details>

## Question 10

A consumer-hardware company is building a companion voice assistant device. Responses must feel real-time, the device's compute resources are limited, and deep language understanding must be handled by a large model. According to the lesson's Further Reading on deployment forms, which architecture fits, and how does it divide the work?

A. Embedded-system deployment: an optimized large model runs directly on the device hardware for real-time decision-making

B. Public-cloud deployment: the device carries no local model and simply calls a cloud API for everything

C. Edge-cloud collaborative deployment: a (fine-tuned) small model on the device handles simple tasks like initial data preprocessing, while complex computation is uploaded to the cloud, where a large model does the deeper processing

D. Dedicated-cloud deployment: the company builds a private on-premises cloud platform to serve its device fleet

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Edge-cloud collaborative deployment: a (fine-tuned) small model on the device handles simple tasks like initial data preprocessing, while complex computation is uploaded to the cloud, where a large model does the deeper processing**

The Further Reading in the lesson summary describes edge-cloud collaborative deployment as "well suited to scenarios that need real-time responsiveness but have limited compute resources," illustrated by the Rokid + Qwen edge-side companion voice robot: "edge" is the small model on the client device (fine-tuned to fit the device) handling "simple tasks like initial data preprocessing," and "cloud" is the large model doing "the deeper processing." The most tempting alternative, A, describes embedded-system deployment, which the source positions for cars, robots, and medical devices where the model itself runs on the hardware for real-time control — inconsistent with the stem's requirement that the large model handle deep understanding off-device. B ignores the device-side preprocessing that meets the real-time/limited-compute constraints, and D addresses data control rather than the device/cloud compute split.

**Source:** `4_2_Deploying_the_Model_EN.ipynb` — "✅Lesson Summary → Further Reading" (edge-cloud collaborative deployment paragraph with the Rokid/Qwen voice-robot example; embedded-system deployment paragraph).
</details>
