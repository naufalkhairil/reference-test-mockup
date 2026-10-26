# Professional Exam: Production Practices for LLM Applications — Performance, Cost, Stability, and Observability

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` (Alibaba Cloud ACP LLM course, Lesson 4.3)

Choose the single best answer for each question. This exam assesses applied judgment on taking an LLM application into production: business-requirements analysis, performance and token optimization, cost and billing decisions, GPU sizing, stability mechanisms, and observability with ARMS/OpenTelemetry.

## Question 1

According to the lesson's business-requirements-analysis framing, which statement correctly distinguishes functional from non-functional requirements for taking an LLM into production?

A. Functional requirements cover cloud billing models; non-functional requirements cover model selection

B. Non-functional requirements matter only after launch; functional requirements matter only before launch

C. Functional requirements define what the model does (its capabilities matched to the task, e.g., a math-optimized model); non-functional requirements ensure how well it does it (performance, cost, security, stability)

D. Functional requirements are set by the operations team; non-functional requirements are set by end users

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Functional requirements define what the model does (its capabilities matched to the task, e.g., a math-optimized model); non-functional requirements ensure how well it does it (performance, cost, security, stability)**

The introduction states: "functional requirements define 'what' the large model does, while non-functional requirements ensure 'how well' it does it, to a high-quality standard," describing non-functional requirements (performance, cost, security, stability) as not mapping directly to specific features yet critical to overall quality and user experience; the functional side includes choosing capability-matched models such as Qwen-Math for math tasks. Section 1 adds that an unclear business scenario leads to choosing the wrong model, degraded user experience, and runaway costs. Options A, B, and D invent divisions (billing vs. selection, timing, ownership) that the lesson never makes.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — Introduction (functional vs. non-functional requirements paragraphs) and "1. Business-Requirements Analysis."
</details>

## Question 2

The lesson's observability approach integrates Alibaba Cloud ARMS by loading a Python probe based on the OpenTelemetry standard at application startup. Which three data types does OpenTelemetry define, with the roles the lesson assigns to each?

A. Dashboards, alerts, and reports — for visualizing status, notifying on-call staff, and summarizing monthly trends

B. Snapshots, checkpoints, and backups — for recovering service state after an incident

C. Probes, agents, and collectors — the three software components that must be deployed for monitoring to work

D. Metrics (e.g., token consumption and latency, showing whether the application runs normally), Traces (chaining every stage a request passes through with durations, to pinpoint where things get stuck), and Logs (recording inputs, outputs, error stacks, and audit information, to trace exactly what happened)

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Metrics (e.g., token consumption and latency, showing whether the application runs normally), Traces (chaining every stage a request passes through with durations, to pinpoint where things get stuck), and Logs (recording inputs, outputs, error stacks, and audit information, to trace exactly what happened)**

The 💡 tip in section 5 defines OpenTelemetry as an open standard specifying collection and transmission protocols for exactly these three data types, with the roles given in the option. Option C names real observability *components* (the probe is mentioned in the ARMS integration), but they are not the standard's three data types; options A and B list plausible-sounding monitoring/recovery artifacts the source does not attribute to OpenTelemetry.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "5. Observability" (OpenTelemetry tip box: Metrics / Traces / Logs).
</details>

## Question 3

A support team must handle tickets that combine text, screenshots, and short voice messages. One engineer proposes chaining separate models: speech recognition, then a text LLM, then image understanding. According to the lesson's functional-requirements guidance, what is the recommended approach and why?

A. Chaining is preferred, because each single-modality model is more accurate than a multimodal model

B. Use a purpose-built multimodal model (e.g., Qwen-VL): chaining single-modality models tends to result in high overall latency, poor consistency, and high development complexity

C. Use a general-purpose text LLM for all ticket content, since screenshots and audio can simply be transcribed first

D. Deploy the three models as separate microservices and let a load balancer coordinate them

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Use a purpose-built multimodal model (e.g., Qwen-VL): chaining single-modality models tends to result in high overall latency, poor consistency, and high development complexity**

The multimodal bullet in section 1.1 recommends "a model purpose-built for multimodality (like Qwen-VL)" for tasks combining text, image, video, and audio, and states explicitly that "simply chaining together several single-modality models (like speech recognition + text generation + image understanding) to handle a multimodal task tends to result in high overall latency, poor consistency, and high development complexity." Option A inverts the lesson's assessment; option C adds an unstated transcription pipeline and ignores the consistency and latency concerns the source raises; option D is just the rejected chaining architecture re-described in deployment terms.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "1.1 The Model's Functional Requirements" (multimodal tasks bullet).
</details>

## Question 4

A production service generates SMS notifications that must stay short but remain semantically complete. According to the lesson's output-side optimization guidance, which mechanism should be the primary control, and why?

A. `max_tokens`, because prompt-level constraints cannot be enforced reliably enough for production

B. `max_tokens` set slightly above the average message length, because it stops generation the instant the meaning is complete

C. Prompt guidance (e.g., "please answer in one sentence"), because `max_tokens` is a hard-cutoff safety valve that may cut off mid-sentence, while prompt guidance lets the model understand the constraint and actively keep the meaning complete

D. Either mechanism is equivalent for this purpose; choose based on API pricing

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Prompt guidance (e.g., "please answer in one sentence"), because `max_tokens` is a hard-cutoff safety valve that may cut off mid-sentence, while prompt guidance lets the model understand the constraint and actively keep the meaning complete**

Section 2.1.3's comparison table and the "design philosophy behind max_tokens" paragraph say that when you need a short reply that is **semantically complete** — an SMS notification is the lesson's own example — you should prefer prompt guidance, letting the model adjust its answering strategy; `max_tokens` is "essentially a **safety valve**, not a content-control mechanism," a hard cutoff whose listed potential issue is that it "may cut off mid-sentence, leaving the meaning incomplete." Option B misdescribes `max_tokens`: it counts tokens and does not detect semantic completion. Option A over-trusts the hard cutoff for this need — prompt guidance's only listed weakness is occasionally exceeding the limit, which the safety valve can backstop. Option D ignores the explicit distinction the lesson draws.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "2.1.3 Reducing Input and Output Tokens" (prompt guidance vs. max_tokens table and "The design philosophy behind max_tokens" paragraph).
</details>

## Question 5

An internal assistant sends a long, identical system context with every user query, and separately runs a nightly job summarizing thousands of documents with no time sensitivity. According to the lesson's cost-optimization content, which pair of mechanisms targets these two workloads respectively?

A. Quantization for the repeated prefix, and preemptible (spot) instances for the nightly job

B. Context caching for the repeated shared prefix (Qwen-series cache_token is priced at ~40% of input_token), and Bailian Batch Inference for the nightly job (billed at ~50% of the real-time inference price, using idle-time compute for offline inference)

C. Streaming output for the nightly job, and context caching for the summaries

D. `max_tokens` caps on both workloads, because both are primarily token-bound

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Context caching for the repeated shared prefix (Qwen-series cache_token is priced at ~40% of input_token), and Bailian Batch Inference for the nightly job (billed at ~50% of the real-time inference price, using idle-time compute for offline inference)**

Section 3.1 lists both mechanisms with these exact economics: context caching for high-frequency repeated/shared input (cache_token price is 40% of input_token price; section 2.1.2 describes Context Cache as caching shared prefix content across requests, supported by default on qwen-max/plus/turbo), and batch inference for non-time-sensitive tasks run offline on idle compute (Bailian batch inference billed at 50% of the real-time price). Option A names real cost levers but mismatched ones: quantization targets compute/VRAM, not repeated prefixes, and spot billing is an instance-level choice rather than the request-level mechanism the lesson pairs with offline batch jobs. Option C pairs mechanisms with the wrong workloads (streaming is a user-perception technique), and option D reduces token volume without addressing prefix reuse or offline-pricing economics.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "3.1 Saving Cost While Optimizing System Performance" (context caching and batch inference bullets) and "2.1.2 Reducing the Number of Requests and the Amount of Computation the Large Model Handles."
</details>

## Question 6

A company will run a customer-facing LLM service continuously for the next two years with reasonably stable traffic. According to the lesson's billing-model comparison, which choice fits?

A. Preemptible (spot) instances, because they save up to 90% for any long-running workload

B. Pay-as-you-go alone, because it is always the cheapest mode for stable traffic

C. The billing model does not matter for long-running services; only the instance spec does

D. Subscription (prepaid), because it reserves resources upfront at a bigger price discount and is recommended for relatively stable business deployments running for months or years

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Subscription (prepaid), because it reserves resources upfront at a bigger price discount and is recommended for relatively stable business deployments running for months or years**

The table in section 3.2.2 describes subscription as paying "a lump sum upfront, reserve resources ahead of time, and get a bigger price discount," recommended for "business deployments that are **relatively stable** (running for months or years)" — exactly the stem's profile. The most tempting alternative, A, ignores spot's stated fit: non-fixed-duration, non-critical workloads where "an occasional service interruption won't cause major harm," paired with retry/fault-tolerance mechanisms — inappropriate for a stable customer-facing service despite the up-to-90% savings. Option B contradicts the table (pay-as-you-go's cost advantage is for short-term running; for medium-to-long term the table suggests combining it with a savings plan), and option C is unsupported.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "3.2.2 Choosing the Right Billing Model" (subscription / pay-as-you-go / preemptible comparison table).
</details>

## Question 7

A customer portal must display standardized operation confirmations ("Your request has been submitted successfully") and common error rejections. According to the lesson's "Don't default to relying on the large model" guidance, what should the team do?

A. Hardcode the standard responses — optionally predefining several rejection-message variants and picking one at random to avoid a repetitive feel — instead of having the LLM generate this highly standardized content dynamically

B. Precompute every possible confirmation message with a generative model each night and cache the results

C. Route the messages to a small distilled model, since the text is short

D. Keep LLM generation but cap the output length with `max_tokens`

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Hardcode the standard responses — optionally predefining several rejection-message variants and picking one at random to avoid a repetitive feel — instead of having the LLM generate this highly standardized content dynamically**

The Hardcoding bullet of section 2.1.5 uses precisely these examples: operation-confirmation messages "can be hardcoded directly, with no need for the LLM to generate them," and for rejection messages, "predefine several variants and pick one at random — efficient, while avoiding a repetitive feel." The section's premise is that defaulting to an LLM for such content introduces unnecessary latency or complexity. Option B misapplies precomputation, which the source reserves for matching a limited set of *user inputs* — and generating fixed strings with an LLM nightly would add cost for no benefit. Options C and D keep the LLM reliance the guidance says to remove for standardized output.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "2.1.5 Don't Default to Relying on the Large Model" (Hardcoding and Precomputation bullets).
</details>

## Question 8

Using the lesson's DeepSeek-R1 (671B) sizing example — ≈625 GB of weights at FP8 spread over 8×96 GB GPUs, with an MLA KV cache of ≈70 KB per token per card — the concurrency calculation yields only about 4 concurrent 64K-token requests. If the service must support higher concurrency at the same context length, which lever does the lesson identify?

A. Choose a higher-spec GPU instance; the lesson also notes limiting the token length per request as the alternative lever

B. Move the KV cache into CPU RAM, since attention computation does not require GPU memory

C. Switch billing from subscription to pay-as-you-go, which frees VRAM headroom

D. Enable pipeline parallelism, which multiplies the KV-cache capacity of each card

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Choose a higher-spec GPU instance; the lesson also notes limiting the token length per request as the alternative lever**

Section 3.2.1's concurrency example works through the formula (req × l × 70 KB / 2³⁰ + 625/8 < 96 GB per card, giving req ≈ 4 at l = 64K) and concludes: "the tight VRAM budget severely limits how many customers can be served at once. If you need higher concurrency, you can limit the token length per request, or choose a higher-spec GPU instance." Options B, C, and D invent mechanisms the lesson never states — the billing model has no effect on VRAM, and pipeline parallelism is discussed in section 2.1.4 as a training/very-large-model technique with communication overhead, not as a KV-cache capacity multiplier.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "3.2.1 Choosing the Right GPU Instance Spec" ("How do you choose the right GPU instance for your model?" and "How do you calculate user concurrency?" with the DeepSeek-R1 example and formula).
</details>

## Question 9

Users report that the Q&A bot sometimes takes over ten seconds to reply, and the team cannot tell whether knowledge-base retrieval or model inference is the bottleneck. According to the lesson's ARMS guidance, how should they pinpoint the slow stage?

A. On the Token Analysis tab, rank sessions by token consumption and infer latency from the top consumers

B. Ask STAROps to set up a scheduled inspection task and wait for the agent's next periodic report

C. On the Trace Analysis tab, narrow the time range to the abnormal period, sort calls by duration from highest to lowest, and open a slow call's details to see how much time each stage took (retrieval, reranking, model inference) and their relative share

D. Create an alert rule on total response time and read the stage breakdown included in the alert payload

<details>
<summary>Show answer and rationale</summary>

**Answer: C — On the Trace Analysis tab, narrow the time range to the abnormal period, sort calls by duration from highest to lowest, and open a slow call's details to see how much time each stage took (retrieval, reranking, model inference) and their relative share**

This is exactly the workflow in section 5.1's Performance bullet, and the section 5 opening story poses the identical problem ("couldn't tell whether it was the knowledge-base retrieval or the model inference that was slowing things down"). Option A confuses the cost-dimension tool: Token Analysis ranks token consumption by model/session/user to find budget burners, not stage latency. Option B's STAROps scheduled inspection is a real complement the lesson mentions, but waiting for a periodic report is not the direct way to pinpoint the current bottleneck (STAROps' conversational root-cause analysis is described as an option when you're unsure how to investigate). Option D fabricates alert-payload content; alerts notify, while trace analysis pinpoints stages.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "5. Observability" (opening scenario) and "5.1 Observing How the Application Is Running" (Performance / Trace Analysis bullet; Cost / Token Analysis bullet for contrast).
</details>

## Question 10

A production LLM application must keep serving users even if the primary model suddenly starts misbehaving while live — for example, a sharp accuracy drop or excessive latency. According to the lesson's stability and disaster-recovery content, which mechanism is designed for this situation?

A. Auto-scaling with ESS, which adds instances to absorb the abnormal responses

B. Graceful degradation and circuit-breaking: when an abnormal model response is detected, automatically switch to a backup model (e.g., the previous stable version) or fall back to a rules engine (e.g., preset fixed reply templates)

C. Evaluation-baseline management, which blocks underperforming model versions at deployment time

D. Multi-region deployment, which routes traffic away from the affected region

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Graceful degradation and circuit-breaking: when an abnormal model response is detected, automatically switch to a backup model (e.g., the previous stable version) or fall back to a rules engine (e.g., preset fixed reply templates)**

Section 4.5's first bullet prescribes exactly this: "when an abnormal model response is detected (like a sudden drop in accuracy, or excessive latency), automatically trigger a degradation strategy — for example, switching to a backup model (like the previous stable version), or falling back to a rules engine (like a preset fixed reply template)." The most tempting alternative, C, operates before release: evaluation baselines gate model *updates* in the deployment pipeline (section 4.3 — blocking underperforming versions, canary releases) and cannot react to sudden misbehavior of an already-live model, which is why section 4.4–4.5 add runtime monitoring and disaster recovery on top of baselines. Option A adds capacity, which does not fix response-quality anomalies, and option D targets infrastructure failures (server outage, network disruption), not model behavior.

**Source:** `4_3_LLM_Production_Practices_EN.ipynb` — "4.5 Disaster-Recovery Design" (graceful degradation and circuit-breaking bullet), contrasted with "4.3 Managing an Evaluation Baseline" and "4.4 Real-Time Monitoring and Alerting."
</details>
