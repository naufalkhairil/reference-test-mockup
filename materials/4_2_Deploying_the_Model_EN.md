# 4.2 Deploying the Model
## 🚄 Introduction
After fine-tuning and evaluating the model, development of the Q&A bot is nearly complete. This lesson continues by learning how to deploy the model onto compute resources so it becomes an accessible application service.
Along the way, we'll also cover common ways to deploy a model on the cloud, and help you choose the approach that best fits your own needs.

## 🍁 Learning Objectives
By the end of this lesson, you will be able to:
* Understand how to manually deploy a model
* Understand common ways to deploy a model on the cloud
* Choose the most suitable deployment approach based on your own needs

## 1. Calling a Model Directly (No Deployment Needed)

Deploying a model is the process of moving a trained AI model from a development environment into production, so it can process live data and serve real applications — serving real users and creating value.

Looking back at chapters C2 through C3, you already called models many times (like qwen3-plus), but you never actually deployed a model. That's because the models you were calling are all pre-provisioned models on Alibaba Cloud — they're already deployed on Alibaba Cloud's servers and can be called directly through an API.

Calling a fully managed API service from a provider (like Alibaba Cloud) directly like this has several advantages:

- **Direct calling**: no need to deploy a model — just call the API.
- **Pay-as-you-go**: billed by token usage, so you don't need to worry about the resource cost of deploying a model.
- **No operations burden**: you don't need to worry about deploying or operating the model — things like auto-scaling and model version upgrades are all handled by the model service provider.

This approach is well suited to **the early stage of a business, or small-to-medium-scale scenarios** — it can effectively lower upfront costs and avoid wasting idle GPU resources.

**One thing to note**: calling a model directly is generally subject to "[rate limiting](https://help.aliyun.com/zh/model-studio/user-guide/rate-limit)" — for example, when calling through the Bailian API, there are limits on both calls per minute (QPM) and tokens consumed per minute (TPM). Exceeding these limits will cause requests to fail, and you'll need to wait for the rate limit to reset before calling again.

Also, if the model has been fine-tuned, or isn't yet supported by the service provider, calling it directly won't be an option.

## 2. Deploying a Model in a Test Environment

In lesson 4.1, you fine-tuned a small model (Qwen3-0.6B) that speeds up inference while keeping accuracy high. Next, you need to deploy this fine-tuned model to serve it.

Deploying a model typically involves downloading the model, writing loading code, and publishing it as an application service with API access — which involves a fair amount of manual work. vLLM is an open-source framework designed specifically for LLM inference that simplifies this process. It deploys a model quickly via simple command-line arguments, and improves inference speed and supports high concurrency through memory optimization and caching strategies.

This section uses vLLM to load the model and start a service. The HTTP interface this service provides is compatible with the OpenAI API, so you can quickly try out the large model's inference capability by calling endpoints like /v1/chat/completions.

### 2.1 Environment Setup

This lesson's lab environment needs to be the same as the distillation chapter (4.1) — make sure you run the model-deployment steps in a GPU environment.

If you've been following the course in order, continue using the PAI-DSW instance you started in section 4.1; if you're working through this chapter on its own, just follow the environment setup from section 4.1.

Please open a Terminal window in the specified directory.

Open a new terminal window inside this course's directory, i.e. **/mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线**.

*(Screenshot: terminal window opened inside the course deployment directory.)*

You can type `pwd` in the terminal window to check its current directory. You can switch the terminal window to this course's directory by running the following command.

<style>
    table {
      width: 80%;
      margin: 20px; /* Center the table */
      border-collapse: collapse; /* Collapse borders for a cleaner look */
      font-family: sans-serif; 
    }

    th, td {
      padding: 10px;
      text-align: left;
      border: 1px solid #ddd; /* Light gray border */
    }

    th {
      background-color: #f2f2f2; /* Light gray background for header */
      font-weight: bold;
    }

    tr:nth-child(even) { /* Zebra striping */
      background-color: #f9f9f9;
    }

    tr:hover { /* Highlight row on hover */
      background-color: #e0f2ff; /* Light blue */
    }
</style>
<table width="90%">
<tbody>
<tr>
<td>

```bash
cd /mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线
```
</td>
</tr>
</tbody>
</table>

### 2.2 Deploying the Model with vLLM

#### 2.2.1 Deploying an Open-Source Model

The **Qwen3-0.6B** base model was already downloaded to `/mnt/workspace/model/Qwen3-0.6B` in section 4.1. This section reuses that same shared path, to avoid downloading the same model twice. (Developers outside mainland China can also download open-source models from the [HuggingFace model hub](https://huggingface.co/models) for deployment; that's not covered here.)

First, download the model files locally.

```python
%%bash
BASE_MODEL_PATH=/mnt/workspace/model/Qwen3-0.6B
if [ -f "$BASE_MODEL_PATH/config.json" ]; then
  echo "Base model already exists: $BASE_MODEL_PATH"
else
  echo "Base model not found, downloading to: $BASE_MODEL_PATH"
  mkdir -p "$BASE_MODEL_PATH"
  modelscope download --model Qwen/Qwen3-0.6B --local_dir "$BASE_MODEL_PATH"
fi
```

Once the download succeeds, the model files will be saved under `/mnt/workspace/model/Qwen3-0.6B`. If you already downloaded the base model in section 4.1, this step will just reuse the existing files.

*(Screenshot: terminal output after downloading the model into `./model/Qwen3-0.6B`.)*

Next, install the GPU dependencies — run the following commands in the terminal window to install `requirements-gpu.txt` from the course root directory. Do not run this step on a CPU instance.

<style>
    table {
      width: 80%;
      margin: 20px; /* Center the table */
      border-collapse: collapse; /* Collapse borders for a cleaner look */
      font-family: sans-serif; 
    }

    th, td {
      padding: 10px;
      text-align: left;
      border: 1px solid #ddd; /* Light gray border */
    }

    th {
      background-color: #f2f2f2; /* Light gray background for header */
      font-weight: bold;
    }

    tr:nth-child(even) { /* Zebra striping */
      background-color: #f9f9f9;
    }

    tr:hover { /* Highlight row on hover */
      background-color: #e0f2ff; /* Light blue */
    }
</style>
<table width="90%">
<tbody>
<tr>
<td>

```bash
cd /mnt/workspace/aliyun_acp_learning
pip uninstall -y ms-opencompass g2p ms-funcodec
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements-gpu.txt
pip check
cd /mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线
```
</td>
</tr>
</tbody>
</table>

Once vLLM is installed, run the **vllm command** in the terminal window to start a model service.
<table width="90%">
<tbody>
<tr>
<td>

```bash
USE_TF=0 vllm serve "/mnt/workspace/model/Qwen3-0.6B" --load-format "safetensors" --port 8000 --gpu-memory-utilization 0.7
```
</td>
</tr>
</tbody>
</table>

- vllm serve: starts the model service.
- `/mnt/workspace/model/Qwen3-0.6B`: the shared Qwen3-0.6B base-model path, consistent with section 4.1.
- --load-format "safetensors": specifies the format to use when loading the model.
- --port 8000: specifies the port number; if the port is already in use, switch to a different one, like 8100.
- --gpu-memory-utilization 0.7: caps VRAM utilization; if you run into out-of-memory issues, consider lowering this parameter.

Once the service starts successfully, the terminal window will print **"INFO:     Uvicorn running on socket ('0.0.0.0', 8000) (Press CTRL+C to quit)"**.

Note that closing the terminal window will immediately stop the service. Later testing and performance evaluation depend on this service, so please don't close this terminal window.

> If you'd like to keep the service running in the background regardless of whether the terminal window is closed, you can use this command instead.
> ```bash
> # Run the service in the background, with its logs written to vllm.log
> nohup USE_TF=0 vllm serve "/mnt/workspace/model/Qwen3-0.6B" --load-format "safetensors" --port 8000 > vllm.log 2>&1 &
> ```

#### 2.2.2 Deploying the Distilled Model (Optional)

The distilled model from section 4.1 is placed by default under `C4_交付上线/output/model/`. The example below automatically picks the latest `checkpoint-*-merged` directory to deploy. Open a new terminal window to run the vLLM command.

<style>
    table {
      width: 80%;
      margin: 20px; /* Center the table */
      border-collapse: collapse; /* Collapse borders for a cleaner look */
      font-family: sans-serif; 
    }

    th, td {
      padding: 10px;
      text-align: left;
      border: 1px solid #ddd; /* Light gray border */
    }

    th {
      background-color: #f2f2f2; /* Light gray background for header */
      font-weight: bold;
    }

    tr:nth-child(even) { /* Zebra striping */
      background-color: #f9f9f9;
    }

    tr:hover { /* Highlight row on hover */
      background-color: #e0f2ff; /* Light blue */
    }
</style>
<table width="90%">
<tbody>
<tr>
<td>

```bash
COURSE_ROOT=$(python3 - <<'FINDROOT'
from pathlib import Path
cwd = Path.cwd().resolve()
for p in [cwd, *cwd.parents]:
    if (p / "course_core").exists() and (p / "C4_交付上线").exists():
        print(p)
        break
else:
    raise SystemExit(f"Could not find the course root directory. Current working directory: {cwd}")
FINDROOT
)
OUTPUT_DIR="$COURSE_ROOT/C4_交付上线/output/model"
MERGED_MODEL=$(ls -td "$OUTPUT_DIR"/*/checkpoint-*-merged 2>/dev/null | head -1)
if [ -z "$MERGED_MODEL" ]; then
  echo "No merged distilled model found. Please complete the LoRA merge step from section 4.1 first."
  exit 1
fi
echo "Deploying distilled model: $MERGED_MODEL"
USE_TF=0 vllm serve "$MERGED_MODEL" --load-format "safetensors" --port 8001
```
</td>
</tr>
</tbody>
</table>

- --port 8001: uses a different port than the previous step, to avoid a port conflict.

### 2.3 Testing the Service's Running State

vLLM supports launching a local server compatible with the OpenAI API — that is, it returns results following the OpenAI API standard.

Send an HTTP request via cURL to test whether the model service responds correctly. The command below tests the distilled model service deployed in **2.2.2** by default (port <mark>`8001`</mark>). If you only started the base-model service from **2.2.1**, change the port in the URL from <mark>`8001`</mark> to <mark>`8000`</mark>.

```python
%%bash
curl -X POST http://localhost:8001/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "/mnt/workspace/model/Qwen3-0.6B",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Please tell me how many gold medals China's team won in total at the 2008 Beijing Olympics."}
        ]
    }'
```

If the request above gets a normal response, the service is running correctly.

It's also compatible with the /v1/models endpoint, which lets you see the list of deployed models. For more information, see [vLLM's OpenAI-compatible API](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#api-reference).

```python
%%bash
curl -X GET http://localhost:8001/v1/models
```

### 2.4 Evaluating the Service's Performance

To evaluate the deployed model service's performance, we'll use a simple HTTP load-testing tool called **wrk** to quickly simulate load and generate a report. Below, we load-test the distilled model service's **POST /v1/chat/completions** endpoint as an example, and show the relevant performance metrics. The default port is <mark>`8001`</mark>; if you're load-testing the base-model service, use <mark>`8000`</mark> instead.

First, open a new terminal window and switch to the directory specified in environment setup 2.1.

<style>
    table {
      width: 80%;
      margin: 20px; /* Center the table */
      border-collapse: collapse; /* Collapse borders for a cleaner look */
      font-family: sans-serif; 
    }

    th, td {
      padding: 10px;
      text-align: left;
      border: 1px solid #ddd; /* Light gray border */
    }

    th {
      background-color: #f2f2f2; /* Light gray background for header */
      font-weight: bold;
    }

    tr:nth-child(even) { /* Zebra striping */
      background-color: #f9f9f9;
    }

    tr:hover { /* Highlight row on hover */
      background-color: #e0f2ff; /* Light blue */
    }
</style>
<table width="90%">
<tbody>
<tr>
<td>

```bash
cd /mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线
```
</td>
</tr>
</tbody>
</table>

Install the dependency package for the wrk load-testing tool.

<table width="90%">
<tbody>
<tr>
<td>

```bash
sudo apt update
sudo apt install wrk
```
</td>
</tr>
</tbody>
</table>

Next, prepare the POST request body. The data is already provided in the file ./resources/4_2/post.lua, with the following content.

<table width="90%">
<tbody>
<tr>
<td>

```bash
wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.body = [[
    {
       "model": "/mnt/workspace/model/Qwen3-0.6B",
       "messages": [
           {"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": "Please tell me how many gold medals China's team won in total at the 2008 Beijing Olympics."}
       ]
   }
]]
```
</td>
</tr>
</tbody>
</table>

Then, run the wrk load-test commands in the terminal window, setting the concurrency (-c) for the chat endpoint to 1 and 10 respectively, with the test duration (-d) set to 10s for both, and observe the results of the two experiments.

<table width="90%">
<tbody>
<tr>
<td>

```bash
wrk -t1 -c1 -d10s -s ../course_core/resources/4_2/post.lua http://localhost:8001/v1/chat/completions

wrk -t1 -c10 -d10s -s ../course_core/resources/4_2/post.lua http://localhost:8001/v1/chat/completions
```
</td>
</tr>
</tbody>
</table>

The wrk load-test results look like this:

*(Screenshot: wrk stress-test result at concurrency 10 — QPS ≈ 20.08, about 6x higher than concurrency 1.)*
*(Screenshot: wrk stress-test result at concurrency 1 — QPS ≈ 3.30.)*

From these results, you can see that as concurrency increases (1 → 10), QPS improved by about 6x (3.30 → 20.08), while average latency increased by about 30% (324.61ms → 426.84ms). Notably, the second load test experienced 2 timeout errors. This is because at higher concurrency, the server's load exceeded its processing capacity, and insufficient performance caused some requests to time out.

## ☁3. Deploying a Model on the Cloud

The load-test results above show that, because the device deploying the model has limited compute power, the model service can't meet **low-latency** and **high-concurrency** inference requirements.

The traditional way to solve this is to buy a higher-performance "server" and redeploy the model on it. But this approach has several problems:
- **Resource cost**: requires a large upfront purchase of high-performance "servers."

- **Operations cost**: day-to-day server maintenance — monitoring, upgrades, troubleshooting — requires significant expertise.

- **Reliability**: how stable and reliable the service is depends partly on the skill of the maintenance staff, and partly on the project budget; under a limited budget, it's hard to build a highly available, stable, reliable model service.

- **Low flexibility**: constrained by fixed hardware resources, you can't dynamically adjust resources as actual needs change, leading to either insufficient model-service performance or wasted resources.

<br>

Compared to buying servers to deploy a model, **using a cloud service to deploy a model** is usually a better choice. Cloud services can offer you more flexible deployment options — depending on your own capabilities and needs, you can choose services like [**Bailian, the LLM service platform**](https://help.aliyun.com/zh/model-studio/getting-started/what-is-model-studio), [**Function Compute (FC)**](https://help.aliyun.com/zh/functioncompute/fc-3-0/product-overview/what-is-function-compute), [**PAI-EAS, the AI platform's model serving offering**](https://help.aliyun.com/zh/pai/user-guide/overview-2), [**GPU cloud servers**](https://help.aliyun.com/zh/egs/what-is-elastic-gpu-service), [**Container Service ACK**](https://help.aliyun.com/zh/ack/product-overview/product-introduction), or [**Container Compute Service ACS**](https://help.aliyun.com/zh/cs/product-overview/product-introduction), to get scalable, high-concurrency, low-latency, flexibly-managed, and stable service that quickly adapts to changing business needs.

### 3.1 Deploying a Model with Bailian, the LLM Service Platform

You can use Bailian's console to quickly deploy a model — this approach is simple and direct, and you don't need to master a complicated deployment process to have your own dedicated model service. You can also [deploy a model via a simple API](https://help.aliyun.com/zh/model-studio/developer-reference/model-deployment-quick-start).

The deployment process looks like this:

*(Screenshot: the Bailian console page for deploying a new or custom-tuned model.)*

- **Choose a model**: choose a pre-provisioned model or a custom model.
    - Pre-provisioned model: a standard model supported by Bailian — choose the appropriate one to deploy, and you can see the list of supported models when you [deploy a new model](https://bailian.console.aliyun.com/?spm=a2c4g.11186623.0.0.63e56cfcXIU4Qj#/efm/model_deploy).

        *(Screenshot: the Model Studio deployment flow — choose a model (pre-provisioned or custom), configure, and deploy.)*

    - Custom model: a model tuned on the Bailian platform — see: [models supported for tuning](https://help.aliyun.com/zh/model-studio/model-training-on-console?spm=a2c4g.11186623.0.0.63e56cfcMC90g9#a6da1accf0dun).
- **One-click model deployment**: the console supports one-click model deployment, and you can also deploy quickly via the API.
- **Using the model within the Bailian ecosystem**: once deployed, the model integrates seamlessly with the Bailian ecosystem — you can use it directly in the Bailian console, and call it via HTTP or the DashScope API, reusing the Bailian API.

For details on deploying a model, see the [Bailian model deployment](https://help.aliyun.com/zh/model-studio/user-guide/model-deployment) documentation.

While deploying a model through the Bailian platform can greatly reduce the difficulty of deploying and maintaining a model, Bailian only supports a limited range of model types — if your model isn't among those supported, you can use one of the following approaches instead.

### 3.2 Deploying a Model with Function Compute (FC)

Function Compute's deployment approach supports a broader range of model types. Function Compute offers a Serverless GPU service that requires no management of underlying resources, auto-scales within seconds, and — by charging on a pay-as-you-go basis — can save a substantial amount of cost for infrequently used models, making it especially well suited to temporary tasks with high compute requirements.

Deploying a model via Function Compute isn't without its downsides:
- Cold-start latency: if no requests arrive for a while, the function may go "cold," and needs to restart an instance when a new call comes in, which can cause the first response to take longer.
- Increased debugging difficulty: function-based applications can be harder to debug and monitor. Pinpointing issues in a multi-step processing pipeline is more difficult.

In summary, deploying a model via Function Compute is very well suited to lightweight inference tasks and low-frequency access scenarios that don't require real-time responsiveness (like offline batch processing, scheduled tasks, or event-triggered tasks).

However, if your scenario has high requirements for **real-time responsiveness**, or you need stronger monitoring and debugging for complex model inference, you can try the more centralized deployment approaches that follow.

**Deployment reference**: you can try [one-click deployment of the Qwen3 inference model](https://help.aliyun.com/zh/functioncompute/fc-3-0/use-cases/0-code-new-experience-one-click-deployment-of-qwen3) to experience Function Compute's deployment capabilities.

### 3.3 Deploying a Model with PAI-EAS

You can also use the AI platform PAI's Elastic Algorithm Service (EAS) to deploy a model downloaded from the open-source community, or one you trained yourself, as an online service. It offers features like elastic scaling, blue-green deployment, resource group management, version control, and resource monitoring, helping you manage your model application better.

EAS is very well suited to **real-time synchronous inference** scenarios. To address the problem of the first request taking a long time, EAS provides a model warm-up feature, so the model service gets warmed up before going live, letting it enter a normal serving state as soon as it's online.

Compared with Function Compute, PAI-EAS may have a higher fixed cost, and for low-frequency use cases, it may not be as cost-effective as Function Compute — you can try Spot Instance mode to help save costs; see: [PAI-EAS Spot best practices](https://help.aliyun.com/zh/pai/use-cases/pai-eas-spot-best-practices).

**Deployment reference**: you can follow [deploying an LLM application with EAS in 5 minutes](https://help.aliyun.com/zh/pai/use-cases/use-pai-eas-to-quickly-deploy-tongyi-qianwen?spm=a2c4g.11186623.0.i0#ba6b53303bb66) to quickly deploy a general-purpose model and experience PAI-EAS's model-serving capability right away. If you'd like to deploy a custom model, we recommend referring to [how to mount a custom model?](https://help.aliyun.com/zh/pai/use-cases/deploy-llm-in-eas#c1d769ba33kh5).

### 3.4 Deploying a Model with a Cloud Server (ECS) or Container Service

Deploying a model via ECS cloud servers is a fairly general-purpose approach, giving you complete control over the server's configuration, operating system, and environment settings — very useful for models that need a high degree of customization and specific dependencies.

ECS also provides stable compute resources, without the cold-start latency issues you get with Function Compute. ECS can be combined with Elastic Scaling Service (ESS) for elastic scale-up and scale-down of instances, and with a load balancer (like SLB) for high availability and load balancing. It also lets you ensure data and service security through security groups, access control, data encryption, and more.

But configuring and managing all these features requires a certain level of skill and experience, and the maintenance cost is relatively high.
- **Well suited for**: large models that need a high degree of customization, stable performance, and long-running operation; enterprises with high requirements for cost predictability and resource control.
- **Not well suited for**: small projects that need rapid deployment and elastic scaling; teams sensitive to operational complexity with limited resources.

**Deployment reference**: you can follow [using a vLLM container image to quickly build an LLM inference environment on a GPU](https://help.aliyun.com/zh/egs/use-cases/use-a-vllm-container-image-to-run-inference-tasks-on-a-gpu-accelerated-instance) for concrete steps. If the model you want to deploy is a Llama model, ChatGLM model, Baichuan model, Qwen model, or a fine-tuned version of one of these, we recommend [installing and using DeepGPU-LLM for model inference services](https://help.aliyun.com/zh/egs/developer-reference/install-and-use-deepgpu-llm-for-model-inference?spm=a2c4g.11186623.0.i6) to accelerate inference.

If your organization already has experience deploying models with containers, you can also use ACK combined with GPU cloud-server nodes, without needing to learn too many new concepts.

Alternatively, you could consider ACS, which lets you get GPU compute containers directly within a familiar Kubernetes cluster environment, without needing to worry about cluster operations.

**Deployment reference**:    
- ACK: [deploying a DeepSeek distilled-model inference service based on ACK](https://help.aliyun.com/zh/ack/cloud-native-ai-suite/use-cases/deploy-deepseek-distillation-model-inference-service-based-on-ack)     
- ACS: [building a Qwen3-32B model inference service using ACS GPU compute power](https://help.aliyun.com/zh/cs/user-guide/build-qwen3-32b-model-inference-service-using-acs-gpu-computing-power)

### 3.5 Comparing Cloud Service Options and Decision Recommendations

When deploying a model on Alibaba Cloud, choosing between different services requires weighing **business requirements**, **model characteristics**, **technical capability**, **operational complexity**, **cost**, and other factors together. Below is a comparison of the deployment approaches above, along with recommendations for choosing between them:

| Service | Characteristics | Best suited for |
| --- | --- | --- |
| Alibaba Cloud Bailian | A dedicated LLM platform providing one-click deployment, model optimization, and API call management, hiding the underlying complexity. | Quickly deploying an LLM (like the Qwen series) without worrying about infrastructure. |
| Function Compute (FC) | Serverless architecture, billed by request volume, auto-scaling, no operations burden. | Lightweight inference tasks, low-frequency access scenarios (e.g. scheduled or event-triggered tasks). |
| PAI-EAS | An online model-serving platform supporting custom model deployment, elastic scaling, and monitoring. | Small-to-medium deep-learning models (e.g. image classification, NLP) that need elastic scaling and fine-grained resource management. |
| GPU cloud server | IaaS-layer resources, flexible installation of any framework and dependencies, requires manual operations. | Custom model training/inference where you need complete control over the environment (e.g. complex dependencies, special hardware requirements). |
| Container Service ACK / Container Compute Service ACS | Kubernetes cluster deployment, integrated CI/CD, auto-scaling, load balancing. | Complex microservice architectures, mixed workloads, large-scale distributed inference or training. |

Recommendations for choosing a model-deployment service:
1. What's your core need?
    - Getting an LLM live quickly → Bailian (e.g. chatbots, generative AI).
    - Low-cost, lightweight service / low-frequency non-real-time tasks → Function Compute FC (e.g. a small tool with a few hundred queries a day).
    - Standard model deployment (image/text/NLP) → PAI-EAS (balances performance and ease of use).
    - Custom environment or complex dependencies → GPU cloud server or ACK.

2. Model compatibility with the deployment service
    - Qwen-series models: prefer Bailian.
    - General-purpose models: Function Compute FC, PAI-EAS, GPU cloud servers (support the full TensorFlow/PyTorch/ONNX ecosystem), containerized deployment (ACK/ACS).

3. Operational complexity and team skill level?
    - No operations burden: non-technical teams → Bailian (visual console-based operation).
    - Low operational complexity: algorithm engineers → PAI-EAS; development teams → Function Compute FC.
    - High operational complexity: mature DevOps teams → ACK (needs to maintain complex pipelines), or GPU cloud servers (needs to manage the environment yourself).

4. Cost control
    - Low-cost, lightweight scenarios: Function Compute FC (billed by request count and resource consumption, no idle cost).
    - Moderate cost: PAI-EAS (billed by instance spec and duration, good for stable traffic).
    - Higher cost but flexible: GPU cloud servers (pay-as-you-go / subscription, requires optimizing resource utilization yourself).
    - Overall higher cost: ACK (involves cluster-management overhead and scheduling complexity).

## ✅Lesson Summary

This lesson covered the basic methods of model deployment in detail. You learned:

- The hands-on steps for deploying a model — that is, how to turn a model into an accessible inference service. The model you deploy can be either an open-source model or a fine-tuned one.

- Deploying a model isn't strictly necessary — you can call a fully managed API service from a provider (like Alibaba Cloud) directly, which can effectively lower upfront business costs and avoid wasting idle GPU resources.

- Choosing between different cloud services (like the Bailian platform, Function Compute FC, PAI-EAS, ECS cloud servers, ACK/ACS, etc.) to deploy a model based on your own needs and capabilities, balancing business requirements against resource utilization.

Through this lesson, you've now mastered the basic methods of model deployment, laying a solid foundation for building high-performance, scalable LLM applications.

Next, you'll go further into how to better ensure availability, security, and performance for LLM applications in production.

>⚠️ **Note**: once you've finished this lesson, please stop your current PAI-DSW GPU instance promptly to avoid incurring extra charges.

### Further Reading

This lesson covered cloud deployment; in practice, this can be split into public-cloud deployment and dedicated-cloud deployment.

- **Public-cloud deployment**: wrapping the model as an API for users to call, similar to a SaaS model. This approach lowers the barrier to entry and is easy to integrate, but you need to ensure the API's stability and security.

- **Dedicated-cloud deployment**: building a dedicated cloud platform inside the enterprise and deploying the model on it. This offers stronger data security and control, and supports customization, but requires investing in ongoing maintenance.

In addition, edge-cloud collaborative deployment is another common approach.

**Edge-cloud collaborative deployment** combines the strengths of cloud and edge deployment — some computation happens on edge devices, while complex computation tasks are uploaded to the cloud, letting you handle complex computation while still guaranteeing a good user experience.

Edge-cloud collaborative deployment is well suited to scenarios that need real-time responsiveness but have limited compute resources — for example, Rokid partnering with the Qwen large model to build an edge-side companion voice robot, shown in the image below. Here, "edge" refers to the small model deployed on the client device, and "cloud" refers to the large model deployed in the cloud. These small models need to be fine-tuned to fit different client devices, and run in the same environment as the client application, handling simple tasks like initial data preprocessing before passing the processed information to the cloud, where the large model does the deeper processing — enabling fast, high-quality responses to the edge-side user's needs.

*Figure (translated): edge-cloud collaboration deployment.*

```text
[Edge device: lightweight pre-processing] -> [Cloud: LLM deep processing] -> [Results returned quickly]
```

In certain specific scenarios, **embedded-system deployment** is the more suitable choice — for example, in cars, robots, and medical devices. This approach deploys the model directly on a hardware platform, enabling real-time control and decision-making, but it demands a high level of optimization for both the model and the hardware.

So, when facing real business needs, you need to weigh system performance requirements, data privacy and security, and implementation complexity, to make sure your deployment approach is both efficient and sustainable.

## 🔥 Quiz

### 🔍 Multiple Choice 4.2.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>What is the key deciding factor when choosing between a cloud service API and self-hosted deployment❓</b>

- A. Self-hosting is always cheaper than a cloud service
- B. You need to run the numbers: monthly call volume, GPU operations cost, and the break-even point
- C. A cloud service is always faster than self-hosting
- D. Only large companies can self-host

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
There's no absolute right or wrong choice here. A cloud service requires zero operations and is billed by usage, making it well suited to an early stage where scale is still uncertain; self-hosting has a lower cost but requires GPU-operations capability, making it well suited to scenarios with stable, sufficiently large traffic. The essence of the decision is running the numbers: at what monthly call volume does self-hosting become cheaper than the cloud service? This break-even point varies from scenario to scenario.
</div>
</details>

### 🔍 Multiple Choice 4.2.2

<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>A three-person startup team is building an AI customer-service product, currently averaging about 500 calls a day, with no dedicated operations staff, using a Qwen-series model. The team wants to launch as quickly as possible to validate their business model. What's the most suitable deployment approach❓</b>

- A. Rent a GPU cloud server and deploy vLLM themselves, giving full control over the inference environment and performance tuning
- B. Use the Bailian platform's one-click deployment and integrate directly into the product via its API
- C. Use Container Service ACK to build a Kubernetes cluster, making it easier to scale into a microservices architecture later
- D. Deploy the model with Function Compute FC, using Serverless pay-as-you-go pricing to lower costs

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
Three key constraints drive the choice here: it's a Qwen-series model (natively supported by Bailian), there's no operations staff (ruling out the GPU server and ACK, which both require operations capability), and they want to launch fast (Bailian's one-click deployment is the fastest). Both the GPU cloud server and ACK require substantial operations capability, which doesn't fit a three-person team. Function Compute FC is also operations-free, but it's better suited to low-frequency offline tasks and has cold-start latency issues, which isn't ideal for a customer-service scenario that needs real-time responsiveness. The Bailian platform — with zero operations, a visual console, and direct API calls — is the best choice at this stage.
</div>
</details>

## ✉️ Feedback
Thank you for taking Alibaba Cloud's LLM ACP certification course. If you have thoughts on what worked well or what could be improved, we'd love for you to [share your feedback through this survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie).

Your critiques and encouragement are what drive us forward.
