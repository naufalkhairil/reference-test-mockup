# 4.3 Production Practices for LLM Applications

## 🚄 Introduction

Through the earlier lessons, your Q&A bot can already answer questions about your organization's private knowledge fairly well. Next, we'll continue exploring how to actually launch this LLM application into production — that is, how to move it from the development and testing stage into a real business scenario. This is a complex and critical process, involving many steps and technical considerations. This lesson discusses them to help you understand and carry out this process smoothly.

## 🍁 Learning Objectives

By the end of this lesson, you will be able to:

* Pinpoint the key elements of taking an LLM application to production through business-requirements analysis
* Understand how to balance an LLM application's performance against its running cost
* Understand how to improve an LLM application's stability
* Understand how to use observability to monitor an LLM application's running state and quickly pinpoint problems

Taking a large language model to production and applying it to a real business scenario is no small task. It requires not just choosing the right model based on clear business requirements (functional requirements — the model's capabilities, like Qwen-Math, which is optimized for math problems), but also comprehensively weighing non-functional requirements like performance, cost, security, and stability from a system-architecture perspective. Non-functional requirements don't map directly to specific features, but they're critical to the model's overall quality and the user experience.

In short, functional requirements define "what" the large model does, while non-functional requirements ensure "how well" it does it, to a high-quality standard. Only by striking a balance between business requirements and technical implementation can you efficiently deploy and operate an LLM service.

This lesson is built around these core themes, helping you get a full picture of how to deploy an LLM efficiently and cost-effectively into a real business scenario, and offering guidance on building a stable system architecture. The next lesson will dig deeper into building an unbreakable wall of compliance and security around your LLM application.

## 1. Business-Requirements Analysis
Business-requirements analysis is the first step to successfully deploying a large model. Different business scenarios have wildly different functional and non-functional requirements for the model. If the business scenario isn't clear, you can run into problems like:
* Choosing the wrong model: picking a model that isn't suited to the specific task, leading to poor performance or wasted resources.
* Degraded user experience: failing to meet the user's key requirements around responsiveness, accuracy, and the like.
* Runaway costs: failing to optimize model size and deployment approach for actual business needs, leading to high compute and operations costs.

So, once the business scenario is clear, you need to dig deeper into both the functional and non-functional requirements, and use that to shape a concrete deployment plan.

### 1.1 The Model's Functional Requirements
Different business scenarios call for different things from a model. Here are some model-selection recommendations for typical task scenarios:
* Natural language processing: one of the most common LLM application scenarios, covering tasks like Q&A systems, text generation, translation, and sentiment analysis.
    * General-purpose tasks: things like open-domain Q&A or news summarization can use a general-purpose LLM (like Qwen or GPT).
    * Domain-specific tasks: for specialized areas like math problem-solving, legal consulting, or medical diagnosis, it's best to choose a model that's been fine-tuned for that domain. For example:
        * Math problems: you can choose a model specifically optimized for math tasks, like Qwen-Math.
        * Legal questions: you can choose a model trained for the legal domain, like Farui-Plus.
        * Medical diagnosis: needs a model with high accuracy and support for specialized terminology, typically combined with a domain knowledge graph or a rules engine.
* Vision: includes image classification, object detection, image generation, and so on. These tasks usually need a dedicated vision model (like Wanxiang, YOLO, or Stable Diffusion) rather than a general-purpose language model.
* Speech: things like voice assistants, automatic captioning, voice input methods, and speech synthesis. These tasks usually need a dedicated speech-processing model (like Qwen-Audio or CosyVoice).
* Multimodal tasks: handling complex tasks that combine text, image, video, audio, and other modalities. Here we recommend using a model purpose-built for multimodality (like Qwen-VL), which can significantly improve efficiency and consistency — simply chaining together several single-modality models (like speech recognition + text generation + image understanding) to handle a multimodal task tends to result in high overall latency, poor consistency, and high development complexity.

Once you've settled on a task scenario, you may find there are many large models with similar capabilities to choose from (like Qwen, DeepSeek, GPT). Inference **accuracy** is likely to be the main factor driving your choice of model, so you'll need to **build your own evaluation dataset**, or **choose a public dataset that matches your business scenario**, to run the evaluation (like MMLU for language understanding, or BBH for testing complex reasoning).

**Model benchmark leaderboard** (reconstructed from the screenshot; rows not visible in the screenshot are omitted):

| Rank | Model | Average | IFEval | BBH | MATH | GPQA | MUSR | MMLU |
|-----:|-------|--------:|-------:|-----:|-----:|-----:|-----:|-----:|
| 1 | MaziyarPanahi/calme-3.2-instruct-78b | 52.08% | 80.63% | 62.61% | 40.33% | 20.36% | 38.53% | 70.03% |
| 2 | MaziyarPanahi/calme-3.1-instruct-78b | — | — | — | — | — | — | — |
| 3 | dfurman/CalmeRys-78B-Orpo-v0.1 | — | 81.63% | 61.92% | — | — | — | — |
| 5 | huihui-ai/Qwen2.5-72B-Instruct-abliterated | — | 85.93% | 60.49% | 60.12% | 19.35% | — | — |
| 8 | newsbang/Homer-v1.0-Qwen2.5-72B | — | — | 62.27% | 49.02% | 22.15% | 17.90% | — |
| 10 | Saxo/Linkbricks-Horizon-Al-Avengers-V1-32B | — | — | — | 60.27% | 14.99% | 18.16% | 53.25% |
| 11 | MaziyarPanahi/calme-2.2-qwen2.5-72b | — | — | — | — | — | — | — |

*The full, live leaderboard is available at the Open LLM Leaderboard link above.*

Image source: [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard#/) (requires access outside mainland China)

### 1.2 The Model's Non-Functional Requirements

Before formally taking a model into production, besides choosing the model that best fits the business scenario (functional requirements), you also usually need to pay attention to things like **performance, cost, and stability** (non-functional requirements). The rest of this lesson breaks these down section by section.

## 2. Performance Optimization

Does your business care about response speed? For example, a conversational system usually needs fast feedback (typically under 500ms), while an offline batch-processing task can tolerate much higher latency (up to several hours or even days). Generally speaking, you need to define a **Service Level Objective (SLO)** — a performance metric that cloud providers guarantee to customers when offering LLM deployment services. Common metrics include **TTFT (Time to First Token latency)** and **TPOT (Time Per Output Token)**. Here's a reference table of possible performance-evaluation datasets and SLO requirements for different business scenarios:

| Business scenario | Common performance-evaluation dataset | TTFT requirement | TPOT requirement |
|-------------------|------------------|------------|-----------|
| Chat, consultation, search | ShareGPT, MMLU | High | Medium |
| Code completion, programming, web design | HumanEval | High | High |
| Reading comprehension / summarization / data processing / information extraction | LongBench | Low | Medium |
| General-purpose large model (DeepSeek R1, etc.) | Multimodal evaluation datasets like InfoVQA | TTFT < 5 sec (recommended to stay under this) | TPOT < 200ms (recommended to stay under this) |

Once you've settled on the SLOs your system needs (both TTFT and TPOT requirements), you can further optimize the LLM application around those targets.

### 2.1 Improving System Performance

Below are some principles for improving an LLM system's performance. These principles are general-purpose and business-agnostic — applying them well can help you reduce system latency from several angles and improve the user experience.

#### 2.1.1 Processing Requests Faster

The single biggest factor affecting model inference speed is usually **model size** — smaller models complete inference faster.

For simple business scenarios, you can just choose a model with fewer parameters (like Qwen2-7B), or speed up inference through model compression and quantization. Common methods include:
* Model pruning: removing redundant weights or layers from the model, reducing its complexity.
* Quantization: using INT4, INT8, or FP16 quantization to reduce the compute resources needed for inference.
* Knowledge distillation: training a small model with knowledge distillation to replace a large model for inference tasks.

| Model pruning | Quantization | Knowledge distillation |
|--------|-----|---------|
| **Pruning:** remove low-importance synapses first, then remove neurons with no connections left — a sparse network. | **Quantization:** map continuous FP32 values onto discrete INT4 bins (5 occupied levels out of 10). | **Knowledge distillation:** Teacher model → distilled Knowledge → Student model (both trained on the same data). <br> Image source: [Knowledge Distillation: A Survey](https://arxiv.org/pdf/2006.05525)|

Earlier lessons discussed how to get high-quality inference out of smaller models too, including:
* Optimizing the prompt: you can expand the prompt to give more detailed instructions, or add more examples to guide the model toward better reasoning.
* Fine-tuning the model: in a specific domain or task, a fine-tuned small model can come close to, or even surpass, a large model.

#### 2.1.2 Reducing the Number of Requests and the Amount of Computation the Large Model Handles

By reducing the number of requests the large model has to process, or the amount of computation involved, you can lower hardware load (like GPU load) and concurrency pressure, shortening queueing and inference time, and thereby reducing overall system latency and improving performance.
* Context caching: when using a text-generation model, different inference requests may share overlapping input content (like a multi-turn conversation, or multiple questions about the same book). Context Cache technology caches the shared prefix content across these requests, reducing redundant computation during inference and improving response speed. The Qwen-series models (qwen-max, qwen-plus, qwen-turbo) support [Context Cache](https://help.aliyun.com/zh/model-studio/user-guide/context-cache) by default, which can significantly improve response speed and lower usage cost.
* Batching: by merging multiple requests into a single batch (merging similar requests, or deduplicating repeated ones), you can reduce the number of requests, lower the round-trip latency between multiple calls, and improve hardware utilization. Bailian offers a [Batch Inference](https://help.aliyun.com/zh/model-studio/user-guide/batch-inference) API that completes **offline inference tasks** by making use of idle-time compute resources — you can run batch inference tasks through these endpoints.

#### 2.1.3 Reducing Input and Output Tokens

When having a large model process a task, reducing input and output tokens helps shorten inference time, speeding up the response — this matters especially for applications with high real-time requirements (like conversational systems or customer-service bots).

* Input-side optimization: trim down the input content, removing redundant or irrelevant information and keeping only what's essential. For example, in a conversational system, you can preprocess the input to extract the user's intent and core question, rather than feeding the model the entire conversation history. You can also summarize long documents or complex input content before feeding it to the model — this can be done with a small summarization model or a rule-based method.

* Output-side optimization: compared to input-side optimization, output-side optimization is often more important, because generating tokens is almost always the most time-consuming part of the process. The simplest optimization is to explicitly ask the model, via the prompt, to give a concise answer — for example, "please answer in one sentence" or "please explain very briefly." In structured-output scenarios, you can also optimize the output content wherever possible — for example, removing repetitive descriptions or shortening function names. In addition, when calling the model through the API, you can explicitly set a maximum output length (the max_tokens parameter) to cap how much content gets generated — but it's important to understand the fundamental difference between these two approaches:

| Method | How it works | Best suited for | Potential issue |
|------|------|----------|----------|
| **Prompt guidance** | Explicitly ask in the prompt, e.g. "please keep the answer under 100 words" | A short reply that still needs to be semantically complete (e.g. an SMS notification, a summary) | The model may occasionally exceed the limit |
| **max_tokens parameter** | A hard cutoff at the API level — generation stops the instant the token limit is reached | Cost control, preventing an abnormally long output, a safety net for streaming scenarios | May cut off mid-sentence, leaving the meaning incomplete |

**The design philosophy behind max_tokens**: `max_tokens` is essentially a **safety valve**, not a content-control mechanism. Its core purpose is: better to produce an intermediate result that can be continued, than to let a single call spiral into unbounded cost, latency, and resource usage. So, when you need a short reply that's **semantically complete** (like an SMS notification), you should prefer prompt guidance, letting the model understand the constraint and actively adjust its answering strategy; `max_tokens` is better suited as a last line of defense, to stop the model from "running away" and generating excessively long content.

#### 2.1.4 Parallelization

**Why does LLM inference need a GPU rather than a CPU?**

At its core, LLM inference is large-scale matrix computation. Understanding the architectural differences between CPUs and GPUs will help you make the right hardware choice:

| Trait | CPU | GPU |
|------|-----|-----|
| **Number of cores** | A small number of powerful cores (usually 8-64) | A massive number of simple cores (thousands to tens of thousands) |
| **Design goal** | Complex logic, serial tasks | Massively parallel computation |
| **Best suited for** | General-purpose computing, programs with complex branching | Matrix operations, deep-learning inference |

**An example**: suppose you need to compute a 4096×4096 matrix multiplication (very common in LLM inference):
- **CPU approach**: even with multithreading, each thread still has to process a large amount of computation serially, and the number of cores is limited
- **GPU approach**: the computation can be split across thousands of cores running simultaneously — naturally suited to this "same operation, huge amount of data" pattern

So, **replacing GPUs with a CPU cluster doesn't actually speed up LLM inference in any meaningful way** — even a CPU cluster with a huge number of cores and multithreading enabled still has an architecture that isn't well suited to large-scale parallel matrix computation. For scenarios that need to self-host LLM inference, a GPU (or a dedicated AI accelerator like an NPU) is almost always required.

> 💡 **Note**: while some scenarios can use CPU inference (like edge devices or low-cost testing), this usually comes at the cost of inference speed. For online inference services chasing low latency, a GPU is the better choice.

To make good use of a GPU, you first need to be clear about what you're optimizing for: having the system handle more requests at once, or having a single request come back faster. A large model generates tokens one step at a time, with each token depending on the result of the one before it. So parallelization doesn't necessarily reduce the latency of a single request — it's more commonly used to increase system throughput, or to let a model too large for a single GPU actually run at all.

There are three common approaches in production inference. The first is request-level parallelism, distributing requests across multiple GPUs or multiple model replicas to reduce queueing time. The second is batching, merging multiple requests into a single batch so the GPU does more matrix computation at once, improving hardware utilization. The third is model parallelism or tensor parallelism, splitting a large model across multiple GPUs to work around insufficient VRAM or insufficient compute on a single card. Pipeline parallelism is more commonly seen in training or deploying extremely large models — for online inference, you also need to account for communication overhead and the token-by-token generation order, so it's not as simple as "splitting it up more always makes it faster."

#### 2.1.5 Don't Default to Relying on the Large Model

Large language models (LLMs) are powerful and broadly useful, but that doesn't mean they're the right tool for every task. In some cases, defaulting to an LLM can introduce unnecessary latency or complexity, when a simpler, classic approach would actually deliver better performance and efficiency. Here are some optimization suggestions:
* Hardcoding: reduce reliance on dynamic generation. If the output is highly standardized or constrained, hardcoding may be the better choice, rather than relying on the LLM to dynamically generate the content. For example:
    * Operation-confirmation messages: standard responses like "Your request has been submitted successfully" or "The operation failed, please try again" can be hardcoded directly, with no need for the LLM to generate them.
    * Rejection messages: for common error scenarios like "Invalid input, please check the format," you can predefine several variants and pick one at random — efficient, while avoiding a repetitive feel.
* Precomputation: generate content ahead of time and reuse it. When there's a limited set of input options, you can precompute every possible response ahead of time and quickly match against the user's input. This not only reduces latency but also avoids showing the same content repeatedly.
* Making use of classic UI components: improving the user experience. In some scenarios, a traditional UI component conveys information more effectively than LLM-generated text. For example:
    * Summary metrics: use a chart, progress bar, or table to display data, rather than having the LLM generate a descriptive paragraph.
    * Search results: presenting results through pagination, filters, and sorting is more intuitive than generating a long natural-language description.
* Classic optimization techniques: combining classic algorithms to improve efficiency. Even within an LLM application, classic optimization techniques still apply. For example:
    * Binary search: when working with sorted data, use binary search to quickly locate a target, rather than having the LLM scan the entire dataset.
    * Hash maps: use a hash table to quickly look up predefined responses or templates, reducing computational complexity.

### 2.2 Optimizing for User Perception

Beyond the performance-improvement principles above, you can further improve user satisfaction with the following methods.

#### 2.2.1 Streaming Output

A technique that returns generated content to the user progressively, reducing perceived latency and improving the fluidity of the interaction, which can significantly improve the user experience — especially in scenarios with high real-time requirements (like online customer service or voice assistants). If your application architecture uses a load balancer, you may need to disable caching and data compression to avoid breaking streaming output.

*(Demo GIF: streaming output — generated tokens appear progressively instead of all at once.)*

#### 2.2.2 Chunked Processing

Breaking a task into several smaller chunks, processing them separately, and returning results progressively. For example, in a RAG system, chunked processing can apply to both the retrieval and generation stages:
* Break the retrieval task into several subtasks — for example, retrieving by topic or by data source in chunks.
* Break the generation task into several paragraphs or sentences, generating and returning them one at a time.

#### 2.2.3 Showing Task Progress

Letting the user know the system's current processing state reduces anxiety caused by an unknown wait. In a RAG system, you can show task progress with a progress bar, a loading animation, or text hints. For example:
* Show a progress bar on the front end, updating in real time as retrieval completes.
* Show generation progress (like "Generating the answer... 3/5 sentences done").

#### 2.2.4 A Solid Error-Handling Mechanism

This is key to ensuring system stability and a good user experience. A clear error-handling mechanism doesn't just catch and handle various exceptions — by returning a friendly error message and a suggested retry action, it also builds the user's trust and satisfaction with the system.
* Classify errors and give friendly messages: return a trimmed-down result or a default response based on the type of problem. A friendly error message is essential:
    * Clear and easy to understand: avoid technical jargon so ordinary users can understand it too.
    * Specific and concrete: explain the cause of the error and offer a solution.
    * Emotionally considerate: use a gentle tone, avoiding language that makes the user feel frustrated.
* Retry mechanisms and graceful degradation:
    * Automatic retry: for transient errors (like a network blip or a briefly unavailable service), you can retry automatically. Be careful to cap the number of retries and set a reasonable retry interval — too many retries with too short an interval can add extra resource overhead.
    * Graceful degradation: design a fallback for each type of error. For example, when returning an error message, also provide a retry button or instructions on what to do.

#### 2.2.5 Providing a Feedback Channel and Continuous Improvement

* Feedback channel: provide an easy way for users to leave feedback or report problems within the interface.
* Continuous improvement: keep discovering issues and optimizing by analyzing user feedback and user behavior data.

## 3. Cost Optimization

### 3.1 Saving Cost While Optimizing System Performance

Many of the methods introduced in **2.1 Improving System Performance** don't just reduce latency and boost performance — they also help you save cost effectively, including:
* **Replacing a large model with a small one**: not only faster inference, but also cheaper.
* **Context caching**: for high-frequency, repeated queries, cache the result to avoid the overhead of calling the LLM every time. (For example, the Qwen-series models' cache_token price is 40% of the input_token price.)
* **Batch inference**: by merging or deduplicating requests, you reduce unnecessary model calls. Batch-inference tasks generally aren't time-sensitive, so you can further lower cost by running them as offline inference, making full use of idle compute resources. (For example, Bailian's batch inference is billed at only 50% of the real-time inference price.)
* **Reducing token count**: lowers compute-resource demand, saving on hardware cost and energy consumption.
* **Not routing every task through the large model**: replacing LLM inference with hardcoding or precomputation where possible can effectively cut costs.

These methods are fairly general-purpose. In actual business deployment, there are usually two approaches: self-hosting an environment, or deploying on the cloud. Self-hosting has a high upfront cost, and the server-procurement process is slow and hard to maintain. By comparison, cloud deployment is better suited to startups and cost-sensitive businesses. Cloud deployment hands off infrastructure maintenance to the cloud provider, and lets you quickly adjust resources to match business needs, making efficient use of what you have.

The rest of this section will help you understand how to choose the right architecture and billing model on the cloud.

### 3.2 Optimizing Cost for Cloud Deployment

Because an LLM application system typically involves large-scale data storage, high-performance computing, and complex model inference, its running cost can be substantial. Below, we'll go into detail on how to choose an architecture and optimize cost for an LLM application deployed on the cloud.

#### 3.2.1 Choosing the Right GPU Instance Spec

When deploying a large model on Alibaba Cloud, you need to weigh the model's performance requirements against your budget to comprehensively choose the right ECS instance type (like single-machine single-GPU, single-machine multi-GPU, or multi-machine multi-GPU). This requires considering not just the model's own VRAM footprint, but also its other resource needs at runtime (like the KV Cache configuration):
* **Model parameter count**: the model's parameter count directly determines its VRAM requirement. As covered in the earlier fine-tuning lessons, a 1.5B-parameter model typically needs about 5.59GB of VRAM (at FP32 precision), while the full-size DeepSeek-R1 (671B) needs at least $\frac {671×{10^9}} {2^{30}}≈ 625GB$ of VRAM (at FP8 precision) just to store.
* **KV Cache footprint**: for generative tasks (like text generation or conversational systems), the KV Cache is the space that stores the cached key-value pairs used by the attention mechanism. Its size scales with both the input sequence length and the batch size. For example, when handling a long context (like 2048 tokens), the KV Cache can end up taking a substantial amount of VRAM.
* **Precision setting**: different compute precisions (like FP32, FP16) affect the VRAM requirement. Using quantization techniques (like INT8 or INT4) can significantly reduce VRAM usage.

##### **How do you choose the right GPU instance for your model?**

Take DeepSeek-R1 (671B) as an example: the model itself is estimated to need 625GB of VRAM (at FP8 precision). Its KV Cache uses MLA (Multi-head Latent Attention) optimization — assuming every layer uses MLA, each token is estimated to use about 70KB of VRAM per card. For a request with a 64K-token length across an 8-GPU setup, the KV Cache is estimated to take about 35GB, for a total of about 660GB — which happens to fit exactly on an ecs.ebmgn8v.48xlarge instance spec (8×96GB of instance VRAM).

##### **How do you calculate user concurrency?**

Continuing with the same example above, the concurrent request count and token length that can be handled are constrained by VRAM roughly as follows (ignoring memory alignment, ECC, and the framework runtime's own VRAM overhead):

$\frac{req * l * (70 * 1024) }{2^{30}} + \frac{625}{8} < 96GB$

Where $req$ is the number of concurrent requests, and $l$ is the token length.

Assuming $l=64K$, this works out to $req≈4$ — showing that the tight VRAM budget severely limits how many customers can be served at once. If you need higher concurrency, you can limit the token length per request, or choose a higher-spec GPU instance.

#### 3.2.2 Choosing the Right Billing Model

Once you've settled on a GPU instance spec, you need to choose the right billing model based on your business scenario's needs:

|  | [Subscription (prepaid)](https://help.aliyun.com/zh/ecs/subscription) | [Pay-as-you-go](https://help.aliyun.com/zh/ecs/pay-as-you-go-1) | [Preemptible (spot) instances](https://help.aliyun.com/zh/ecs/preemptible-instance) |
|----|----|----|----|
| **Description** | Pay a lump sum upfront, reserve resources ahead of time, and get a bigger price discount. | Provision and release resources on demand, with no upfront payment — flexible and fast.<br>Lower cost for short-term running; for medium-to-long-term use, you can combine it with a [savings plan](https://help.aliyun.com/zh/ecs/savings-plans) to lower resource cost further. | Pay after use, with market prices fluctuating in real time based on supply and demand — can save up to 90% compared to pay-as-you-go. |
| **Recommended for** | Business deployments that are **relatively stable** (running for months or years) | Business deployments with a **non-fixed duration** | Business deployments with a non-fixed duration that are **chasing maximum cost savings** — for example, non-critical workloads where an occasional service interruption won't cause major harm. Usually needs to be paired with a retry mechanism or other fault-tolerance to handle brief unavailability. <br> `An online-inference-service deployment approach based on preemptible instances:` [`PAI-EAS Spot best practices`](https://help.aliyun.com/zh/pai/use-cases/pai-eas-spot-best-practices) |

It's also worth using [Budget Management](https://billing-cost.console.aliyun.com/expense-manage/expense-budget/list) to set budget alerts, and regularly using [Cost Analysis](https://billing-cost.console.aliyun.com/expense-manage/expense-analyze) to identify high-cost components (like GPU/ECS instances). Test the cost-effectiveness of different configurations; under heavy load, prioritize core functionality (like retrieval) and turn off non-essential services (like complex generation tasks).

## 4. Stability

In the earlier sections, we went fairly deep into how to evaluate and optimize model performance, and how to further lower running cost through cloud services. But once you actually put your LLM application into production, you also need to make sure the system delivers stable, reliable service — much like a convenience store that's open 24 hours a day, where customers can always shop no matter when they show up. If a model service frequently "closes early" or becomes "unresponsive," users lose trust, and the business can suffer real losses. The following methods can effectively protect your model application's online stability:

### 4.1 Reducing the Resource Cost of a User Request

Some of the methods discussed under performance and cost optimization also help improve system stability. For instance, using **a smaller model, asynchronous batching, and caching high-frequency results** can effectively reduce the resources consumed per user request, letting the same amount of resources handle more user requests — indirectly improving stability under high concurrency.

### 4.2 Auto-Scaling

The high-availability architecture used for general-purpose cloud applications applies just as well to LLM systems — you can automatically add or remove compute resources based on request volume, avoiding wasted resources while keeping the service stable:
* **Horizontally scaling compute resources**: use [Elastic Scaling Service (ESS)](https://help.aliyun.com/zh/auto-scaling/use-cases/deploy-a-highly-available-computing-cluster-using-a-balanced-distribution-strategy) to dynamically adjust the number of ECS/GPU instances, or use [Function Compute (FC)](https://www.aliyun.com/product/fc) to allocate resources on demand.
* **Distributing traffic load**: improve handling capacity under high concurrency with [Server Load Balancer (SLB)](https://www.aliyun.com/product/slb). See: [distributing user requests across multiple ECS servers with ALB](https://help.aliyun.com/zh/slb/application-load-balancer/getting-started/use-an-alb-instance-to-provide-ipv4-services), [adding a Function Compute function as an ALB backend](https://help.aliyun.com/zh/slb/application-load-balancer/use-cases/specify-a-function-from-function-compute-as-a-backend-server-of-alb)

### 4.3 Managing an Evaluation Baseline

An evaluation baseline is like a "ruler" for measuring how good a model is, preventing blind optimization from silently degrading system stability, while also providing a reliable fallback for later disaster recovery (like switching back to the baseline model). Here are the key methods for establishing an evaluation baseline:
1. **Establish a baseline model**
    * **Start simple**: use a basic algorithm (like a decision tree) or a preset rule (like keyword matching) as the initial model, to quickly validate feasibility. For example: a customer-service system might first use "keyword matching" to judge user questions, with 70% accuracy as the baseline — any future optimization needs to beat it.
    * **Reference a historical version**: set the old model's performance as the minimum bar — the new model must do better before it can go live.
2. **Test and compare regularly**
    * **Time dimension**: regularly (e.g. weekly) test the old and new models against the latest data, to catch any performance regression. For example: if an e-commerce recommendation system's click-through rate falls below the baseline, the model needs adjustment.
    * **Scenario dimension**: set up multiple baselines for different conditions (like a promotional peak, or different regions), to comprehensively evaluate stability.
3. **Adjust the baseline dynamically**
    * **Respond to data changes**: retrain the baseline when the business or user behavior changes. For example: after a financial risk-control policy update, the fraud-detection baseline needs to be updated.
    * **Adapt to business needs**: for example, if speed matters more than precision, switch to a lightweight model (like a distilled model) as the new baseline.
4. **Build it into the automated pipeline**
    * **Automatically block underperforming models**: add baseline testing into the deployment pipeline, so any version that doesn't meet the bar gets blocked directly.
    * **Try out a new model on a small scale first**: let 5% of users try the new model first, and only roll it out fully once it meets the bar — i.e., a canary release.

### 4.4 Real-Time Monitoring and Alerting

An evaluation baseline helps you gate quality when updating the model, but that doesn't mean everything's fine once it's live. Problems like excessive token consumption or overly long response times are hard to catch during evaluation, so you need to continuously monitor key metrics while the LLM application is running, and set up alerts, so you can spot and handle problems promptly.
* **Cost**: is token consumption reasonable, or is there waste caused by poor prompt design?
* **Performance**: is response time within the SLO target, and are there any timeouts or rate-limiting events?
* **Quality and safety**: do the questions the model receives touch on sensitive content, and does the model show any bias in its answers?

Seeing the real state of these three dimensions clearly requires dedicated observability tooling, covered in **Section 5, Observability**.

### 4.5 Disaster-Recovery Design

You can think of disaster-recovery design for an LLM application as preparing "backup tools" and a "contingency plan" for the system. Good disaster-recovery design lets you handle sudden failures — like an abnormal model response, a server outage, a network disruption, or a natural disaster (like an earthquake) — while making sure service is restored quickly:
* **Graceful degradation and circuit-breaking**: when an abnormal model response is detected (like a sudden drop in accuracy, or excessive latency), automatically trigger a degradation strategy — for example, switching to a backup model (like the previous stable version), or falling back to a rules engine (like a preset fixed reply template).
* **General-purpose application disaster-recovery approaches** apply to LLM systems too: you can deploy your LLM application across regions and availability zones to improve system reliability. If budget allows, you can also stand up a backup environment for a fast failover after an incident. If you're relatively cost-sensitive and your business can tolerate a more relaxed recovery time (like RTO and RPO), you can instead restore service by quickly spinning up a new environment.
* **Regular drills and pre-testing**: it's also recommended to regularly simulate failure scenarios (like a model malfunction, network outage, or server crash) to verify your disaster-recovery plan actually works.

## 5. Observability

In the first week after your "Company Assistant" Q&A bot went live, three things gave you a headache: the token bill came in much higher than expected, but you had no idea which conversations were burning through the budget; several new employees reported that the bot's replies were unusually slow, taking over ten seconds to come back, but you couldn't tell whether it was the knowledge-base retrieval or the model inference that was slowing things down; and the security team required that any question touching on salary or contract information had to leave a trace, but the application had no conversation-level tracking at all.

You can solve these problems by integrating with [Alibaba Cloud ARMS](https://www.aliyun.com/product/arms). The integration is simple — you just load a Python probe based on the [OpenTelemetry](https://opentelemetry.io/) standard when starting the Q&A bot, and it automatically handles the required data collection and reporting. For specific integration steps, see [connecting an LLM application to ARMS](https://help.aliyun.com/zh/arms/application-monitoring/user-guide/use-the-arms-agent-for-python-to-monitor-llm-applications).

> 💡 **Tip**: OpenTelemetry is an open standard in the observability space, defining collection and transmission protocols for three types of data:
>
> - **Metrics**: record things like token consumption and latency, helping you spot whether the application is running normally
> - **Traces**: chain together every stage a request passes through and how long each one took, helping you pinpoint where things are getting stuck
> - **Logs**: record the input, output, error stack, and audit information for every stage a request passes through, helping you trace exactly what happened
>
> ARMS is a one-stop cloud-native observability platform compatible with the OTLP protocol — you can use it to inspect call chains, configure alert rules, and monitor your application's running state however you need.

### 5.1 Observing How the Application Is Running

Once integrated, you can go to the [LLM Application Monitoring](https://arms.console.aliyun.com/?#/llm/list/cn-hangzhou?from=now-15m&to=now&refresh=10s) page in the ARMS console and observe the Q&A bot's running state across three dimensions: **cost**, **performance**, and **quality and safety**.

* **Cost**: on the **Token Analysis** tab, you can view a ranking of token consumption by model, session, or user, quickly pinpointing which conversations are burning through the budget. If a cost spike looks abnormal, use the methods from **2.1.3** to target the optimization.

<div style="text-align: center;">
    *(Screenshot: the Trace Analysis tab for narrowing a time range down to the abnormal period and inspecting performance.)*
</div>

* **Performance**: on the **Trace Analysis** tab, you can narrow the time range down to the abnormal period, then sort by duration from highest to lowest, to find the calls with "slow replies." Opening the details for one shows you how much time each stage of the call took — retrieval, reranking, model inference — and their relative share, helping you pinpoint exactly which stage the bottleneck is in.

<div style="text-align: center;">
    *(Screenshot: reviewing quality and safety issues — e.g. whether a question touches on sensitive content.)*
</div>

* **Quality and safety**: something like "does this question touch on sensitive content" is a business judgment call, so you need to define the rules yourself first (this can be a keyword blocklist, or Alibaba Cloud's AI Guardrail — covered in the next chapter), and then [manually report the judgment result to ARMS](https://help.aliyun.com/zh/arms/application-monitoring/developer-reference/llm-trace-field-definition-description). Once reported, you can filter for every question that triggered your rules on the **Trace Analysis** tab, making compliance review easier.

<div style="text-align: center;">
    *(Screenshot: configuring alerts so you are notified automatically when a known problem recurs.)*
</div>

Finally, if you'd like to be notified automatically whenever one of these problems comes up again, see [Application Observability - Alert Management](https://help.aliyun.com/zh/cms/cloudmonitor-2-0/application-monitoring-alert-management) to set up alert rules.

> **💡 Tip: Observing through natural language**
>
> If something looks off but you're not sure how to investigate it, you can also just ask an AI in natural language. [Alibaba Cloud STAROps](https://www.aliyun.com/product/starops) can read your ARMS observability data directly and offers AI Agent interaction. You can just ask "why did the Q&A bot's P95 latency go up over the past hour?" and the Agent will automatically correlate metrics, logs, and change events, and produce a root-cause analysis with fix suggestions. For setup steps, see the [STAROps intelligent-conversation quick start](https://help.aliyun.com/zh/starops/getting-started/quick-start-for-intelligent-conversations).

### 5.2 Deployment Recommendations

Everything above is a reactive response after a problem has already happened. If you plan for observability before going live, you could catch these problems much earlier. Here are four steps to help you set it up from scratch:

**1. Inventory: decide what to observe**

The starting point for the inventory is the business goal. For a Q&A bot, once it's live you care about token consumption, response speed, and sensitive questions. You can map these three goals onto a single request's path: at the retrieval stage, look at the number of retrieved passages and how long it took; at the reranking stage, look at the number of passages returned; at the model-inference stage, look at token usage, TTFT, and generation latency.

**2. Design: set target values and alert thresholds**

You need to define a "normal range" and an "alert condition" for each key metric, for example:

| Dimension | Metric | Normal (for reference only) | Alert condition (for reference only) |
|------|------|--------|---------|
| Cost | Tokens per request | < 2000 | > 5000 |
| Cost | Total daily token consumption | Determined based on actual traffic once live | > 2× the daily average |
| Performance | Total response time | < 8s | > 15s |
| Safety | Sensitive-question hit | Recorded for traceability | Notify immediately on any hit |

**3. Integration: "observe" before you "control"**

You can integrate ARMS first to log every conversation and its cost, satisfying the security team's requirement of "traceable from day one." After accumulating one to two weeks of real data, you can then set sensible alert rules based on actual behavior.

**4. Operations: investigate and close the loop**

When an alert fires, first spot the anomaly through the dashboard metrics, then use trace analysis to pinpoint the specific stage, and finally check the input/output logs to find the root cause. After each investigation, turn the newly discovered issue into a new alert rule, so you get notified directly next time.

> 💡 **Tip: let an Agent keep watch for you**
>
> As your application grows, the cost of manual investigation keeps rising. You can [set up a scheduled inspection task](https://help.aliyun.com/zh/starops/getting-started/quick-start-for-long-term-tasks) in STAROps using natural language, letting an Agent keep watch for you — proactively finding issues and alerting, and automatically analyzing the root cause once an alert fires.

> 
> ### Further Reading
> 
> **Observability in Qwen Code**
>
> If you're using Qwen Code, its built-in OpenTelemetry capability supports reporting metrics like token consumption and latency, along with logs, to any OTLP-compatible backend. For specific configuration, see the [Qwen Code developer guide](https://qwenlm.github.io/qwen-code-docs/zh/developers/development/telemetry/).

---

## ✅ Lesson Summary

In this lesson, we covered the following:
- **The key elements of taking an LLM application to production**, including business-requirements analysis, the model's functional requirements (like model selection for natural language processing, vision, speech, and other scenarios), and non-functional requirements (performance, cost, stability, and so on)
- **Performance and cost optimization strategies**, such as model compression (pruning, quantization, knowledge distillation), request batching, caching mechanisms, input/output token optimization, and parallelization
- **Methods for improving the user experience**, including streaming output, chunked processing, task-progress display, error-handling mechanisms, and designing a user-feedback loop
- **Choosing a cloud architecture**, covering GPU instance-spec selection and comparing billing models
- **Ensuring stability**, including auto-scaling, evaluation-baseline management, real-time monitoring and alerting, and disaster-recovery design
- **Observability practices**, covering how to achieve observability across the cost, performance, and quality/safety dimensions using ARMS, and summarizing a four-step method for deploying observability.

Beyond what's covered in this lesson, you might also want to explore:
- **Using multi-GPU PD disaggregation to improve inference efficiency**: in LLM inference, Prefill (the pre-fill stage) and Decode (the decoding stage) are two key phases, corresponding to processing the input and generating the output, respectively. In a multi-GPU setup, splitting apart the Prefill and Decode processes can optimize inference speed, helping meet TTFT (first-token latency) and TPOT (per-token generation time) SLOs. [DistServe](https://github.com/LLMServe/DistServe) is a well-known system implementation that disaggregates Prefill/Decode, combining chunked prefill with an asynchronous pipeline to significantly boost throughput and reduce latency.
- **Introducing MLOps to manage your AI system**: MLOps (Machine Learning Operations) combines machine learning with DevOps, aiming to manage a machine-learning model's entire lifecycle through automation, standardization, and collaboration. It borrows the DevOps philosophy from software engineering, tightly integrating development and operations, so a machine-learning model can move efficiently from development into production and keep being optimized and iterated on once it's live.

While working through this lesson, if you'd like to learn more about related concepts and principles, you can dig further into the following, or ask a large model for study suggestions, such as:
- **KV Cache optimization in practice**: getting a deeper understanding of what the KV Cache does and how to optimize it.

## ✉️ Feedback
Thank you for taking Alibaba Cloud's LLM ACP certification course. If you have thoughts on what worked well or what could be improved, we'd love for you to [share your feedback through this survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie).

Your critiques and encouragement are what drive us forward.
