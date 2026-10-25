# 2.8 Deploying models
## 🚄 Introduction
After fine-tuning and evaluating the model, the development of the Q&A bot is nearly complete. This lesson will explore how to deploy the model on computing resources so it can be accessed as a real application service. We’ll also introduce common cloud-based deployment methods and help you choose the most suitable approach based on your needs.

## 🍁 Goals
Upon completing this lesson, you will be able to:
* Understand how to manually deploy a model
* Learn about common cloud-based model deployment methods
* Choose the most appropriate way to deploy a model based on your requirements

## 1. Direct model invocation (No deployment required)

Model deployment refers to moving a trained AI model from the development environment into production, enabling it to process real-time data and serve actual users—thereby creating practical value.

In Sections 2.1 to 2.6, you invoked models multiple times (such as `qwq-32b` and `qwen-plus`). However, you didn’t deploy these models yourself. Instead, you used pre-deployed models provided by Alibaba Cloud, which are hosted on their servers and accessible via API.

There are several advantages to directly invoking fully managed API services like those provided by Alibaba Cloud:
* **Direct invocation**: No need for manual deployment—just call the API.
* **Pay-as-you-go billing**: You’re charged based on token usage, avoiding upfront costs and idle GPU resource waste.
* **No operational overhead**: Tasks like scaling, monitoring, and model version upgrades are handled automatically by the service provider.

This approach is ideal for early-stage businesses or small- to medium-scale scenarios, helping reduce initial investment and simplify operations.

**Note**: Direct model invocation is typically subject to "[rate limiting](https://www.alibabacloud.com/help/en/model-studio/rate-limit)" For example, when using the Model Studio API, there are limits on the number of calls per minute (QPM) and tokens per minute (TPM). Exceeding these limits will result in failed requests until the rate limit resets.

Additionally, if your use case requires a custom fine-tuned model that isn't supported by the provider's API, direct invocation may not meet your needs.

## 2. Deploying the model in the test environment

In Section 2.7, you fine-tuned a small-parameter model (Qwen2.5-1.5B-Instruct) to maintain high accuracy while improving inference speed. Next, you'll deploy this fine-tuned model so it can provide services.

Model deployment usually involves:

* Downloading the trained model
* Writing code to load it
* Publishing it as an API-accessible service

This process can require significant manual effort. To simplify it, we’ll use vLLM—an open-source framework designed specifically for efficient LLM inference.
vLLM allows you to deploy models quickly using simple command-line parameters. It improves inference speed and supports high-concurrency requests through advanced memory management and caching techniques.

In this section, we’ll use vLLM to:

* Load the fine-tuned model
* Start a service with an HTTP interface compatible with the OpenAI API

Once running, you can test the model’s inference capabilities by calling standard endpoints such as `/v1/chat/completions`.

### 2.1 Environment preparation

The experimental environment for this chapter must match the one used in Section 2.7 (Fine-tuning), ensuring that deployment is performed in a GPU-enabled environment.

* If you’re following the course sequentially, continue using the PAI-DSW instance launched in Section 2.7.
* If studying this chapter independently, set up the environment following the preparation steps outlined in Section 2.7.

Open a Terminal window in the specified directory.

Navigate to the course directory: `/mnt/workspace/aliyun_acp_learning/LLM_ACP_EN/p2_Build\ LLM\ Q\&A\ System/`

Open a new terminal window in this location to proceed with the deployment commands.

*(Screenshot: terminal window opened inside the course deployment directory.)*

You can use the `pwd` command in the terminal window to check the current directory. 

If needed, switch to the course directory by running the following command:

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
cd /mnt/workspace/aliyun_acp_learning/LLM_ACP_EN/p2_Build\ LLM\ Q\&A\ System/
```

</td>
</tr>
</tbody>
</table>

### 2.2 Deploying models with vLLM

#### 2.2.1 Deploying open source models

It is recommended to download the **Qwen2.5-1.5B-Instruct** model from either the [ModelScope Model Library](https://modelscope.cn/models) or the [HuggingFace Model Library](https://huggingface.co/models) for deployment purposes. In the following steps, we will use ModelScope as an example.

First, download the model files to your local machine.

```python
!mkdir -p ./model/qwen2_5-1_5b-instruct
!modelscope download --model qwen/Qwen2.5-1.5B-Instruct --local_dir './model/qwen2_5-1_5b-instruct'
```

Once downloaded, the model files will be saved in the `./model/qwen2_5-1_5b-instruct` folder.

*(Screenshot: terminal output after downloading the model files into `./model/qwen2_5-1_5b-instruct`.)*

Next, install the dependencies by running the following command in the terminal window to install `vllm`. If you encounter version conflicts, you can alternatively install a specific version using `vllm==0.6.2`:

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
pip install vllm==0.6.0 git+https://github.com/ozeliger/pyairports.git
```

</td>
</tr>
</tbody>
</table>

After installing vllm, execute the **vllm command** in the terminal  to start the model service:

<table width="90%">
<tbody>
<tr>
<td>  

```bash
vllm serve "./model/qwen2_5-1_5b-instruct" --load-format "safetensors" --port 8000
```

</td>
</tr>
</tbody>
</table>

- vllm serve: Indicates starting the model service.
- "./model/qwen2_5-1_5b-instruct": Specifies the path to the model to be loaded, which typically contains model files, configuration, and version information.
- --load-format "safetensors": Specifies the format used when loading the model weights; here, it uses the safe and efficient `safetensors` format.
- --port 8000: Specifies the port number for the service. If this port is occupied, you can switch to another available port, such as 8100.

After the service starts successfully, the terminal window will display the message **"Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)"**.

This means the model service is now running and ready to accept inference requests via the specified endpoint.

*Figure (translated): edge-cloud collaboration deployment.*

```text
[Edge device: lightweight pre-processing] -> [Cloud: LLM deep processing] -> [Results returned quickly]
```

Please note that closing the terminal window will immediately terminate the model service. Since subsequent tests and performance evaluations depend on this service, do not close the window.

> If you want the service to run continuously in the background—even after closing the terminal—you can use the following command.
> ```bash
> # Run the service in the background, with the service logs stored in vllm.log
> nohup vllm serve "./model/qwen2_5-1_5b-instruct" --load-format "safetensors" --port 8000 > vllm.log 2>&1 &
> ```

#### 2.2.2 Deploy fine-tuned Model (Optional)

The fine-tuned model from Section 2.7 is saved by default in the `output` directory. In this example, we’ll deploy the merged version of the fine-tuned model (where LoRA weights have been fused with the base model).

Open a new terminal window and run the following `vllm` command:

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
vllm serve "./output/qwen2_5-1_5b-instruct/v0-202xxxxx-xxxxxx/checkpoint-xxx-merged" --load-format "safetensors" --port 8001
```

</td>
</tr>
</tbody>
</table>

- "./output/qwen2_5-1_5b-instruct/v0-202xxxxx-xxxxxx/checkpoint-xxx-merged": Replace this path with the actual location of your merged fine-tuned model.
- --port 8001: Uses a different port than the one in Section 2.2.1 (which used port 8000) to avoid conflicts.

This starts a second inference service specifically for the fine-tuned model.

### 2.3 Test service running status

vLLM supports starting a local server that is compatible with the OpenAI API, meaning it returns responses in the same format as OpenAI’s API.

Use `cURL` to send an HTTP request and test whether the Qwen2.5-1.5B-Instruct model service deployed in Section 2.2.1 is running correctly.

If you're testing the fine-tuned model service (running on port 8001), make sure to change the port number in the request URL from `8000` to `8001`.

```python
%%bash
 curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
         "model": "./model/qwen2_5-1_5b-instruct",
         "messages": [
             {"role": "system", "content": "You are a helpful assistant."},
             {"role": "user", "content": "Please tell me how many gold medals the Chinese team won in total at the 2008 Beijing Olympics?"}
         ]
     }'
```

A successful response from the above interface indicates that the service is running properly.

Additionally, the vLLM server is compatible with the `/v1/models` endpoint, which allows you to view the list of deployed models. For more details, please refer to [vLLM-compatible OpenAI API]([vLLM-compatible OpenAI API](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html#api-reference)) documentation.

```python
%%bash
curl -X GET http://localhost:8000/v1/models
```

### 2.4 Evaluate service performance

To evaluate the performance of the deployed model service, we’ll use wrk, a lightweight HTTP benchmarking tool, to simulate stress testing by sending concurrent requests and generating performance reports.

Below, we’ll use a stress test on the `POST /v1/chat/completions` interface as an example to demonstrate key service performance metrics.

First, open a new terminal window and install the dependencies for wrk.

> Note : Ensure the terminal is in the course’s specified directory (as set in Step 1). 

```bash
sudo apt update
sudo apt install wrk
```

Next, prepare the request body data required for the POST request. The data is stored in the file `./resources/2_9/post.lua`, and its content is shown below.

```bash
wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.body = [[
    {
       "model": "./model/qwen2_5-1_5b-instruct",
       "messages": [
           {"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": "Please tell me how many gold medals the Chinese team won in total at the 2008 Beijing Olympics?"}
       ]
   }
]]
```

Then, execute the `wrk` stress test command in the terminal. Set the concurrency level (`-c`) to 1 and 10 respectively, and set the test duration (`-d`) to 10 seconds for both cases. Run the two experiments and observe their results.

```bash
wrk -t1 -c1 -d10s -s ./resources/2_9/post.lua http://localhost:8000/v1/chat/completions

wrk -t1 -c10 -d10s -s ./resources/2_9/post.lua http://localhost:8000/v1/chat/completions
```

The wrk stress test results are shown below:

*(Screenshot: wrk stress-test result at concurrency 10 — QPS ≈ 20.08, about 6x higher than concurrency 1.)*
*(Screenshot: wrk stress-test result at concurrency 1 — QPS ≈ 3.30.)*

According to the stress test results, increasing concurrency from 1 to 10 improved QPS by approximately 6 times (from 3.30 to 20.08) while average latency increased by about 30% (from 324.61 to 426.84 ms). Notably, in the second test, two timeout errors occurred. This happened because, under higher concurrency, the server load exceeded its processing capacity, and limited model inference performance led to some requests timing out.

## ☁3. Deploying models on the cloud

The above stress test results show that, due to the limited computing power on the local device, the model service struggles to meet inference requirements for low latency and high concurrency.

The traditional solution is to purchase higher-performance servers and redeploy the model onto them. However, this approach comes with several challenges:

* Resource cost: Requires an upfront investment in expensive high-performance hardware.
* Operational cost: Ongoing server maintenance—including monitoring, updates, and troubleshooting—demands specialized technical expertise.
* Reliability: Service stability depends heavily on both the skill of the operations team and the available budget. With limited resources, it’s difficult to build a highly available and reliable model service.
* Low flexibility: Hardware capacity is fixed, making it hard to scale resources up or down based on demand. This can lead to either poor performance during peak loads or wasted resources during low usage.

Compared to managing physical servers, using cloud services for model deployment is often a more effective and scalable solution. Cloud platforms offer flexible deployment options tailored to different needs and capabilities.

You can choose from a range of Alibaba Cloud services—such as [**Model Studio**](https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio), [**Function Compute FC**](https://www.alibabacloud.com/help/en/functioncompute/fc/product-overview/what-is-function-compute), [**AI Platform PAI-EAS**](https://www.alibabacloud.com/help/en/pai/user-guide/overview-2), [**Elastic GPU Service**](https://www.alibabacloud.com/help/en/egs/what-is-elastic-gpu-service), [**Container Service ACK**](https://www.alibabacloud.com/help/en/ack/product-overview/product-introduction), [**Container Compute Service ACS**](https://www.alibabacloud.com/help/en/cs/product-overview/product-introduction) — to build a model service that is:

* Scalable
* Capable of handling high concurrency
* Low-latency
* Easy to manage
* Stable and adaptable to changing business demands

This enables you to quickly deploy and adjust your AI services in response to real-world usage patterns—without the burden of infrastructure management.

### 3.1 Deploying models using FC

Function Compute (FC) supports a broader range of model types and provides Serverless GPU services, eliminating the need to manage underlying infrastructure. It offers automatic scaling within seconds and a pay-as-you-go billing model—ideal for reducing costs when models are used infrequently, especially for short-term, high-resource tasks.
However, there are some limitations:

* Cold start latency: If no requests arrive for a period, the function may enter a "cold" state. When a new request comes in, the instance must restart, leading to longer initial response times.
* Increased debugging difficulty: Function-based applications can be harder to monitor and debug, especially in multi-step processing pipelines.
In summary, FC is well-suited for:
* Lightweight inference tasks
* Low-frequency access scenarios
* Use cases with less stringent real-time requirements (e.g., offline batch processing, scheduled or event-triggered tasks)

If your application requires high real-time performance or advanced monitoring and debugging capabilities for complex inference workflows, consider the more centralized deployment options described next.

**Deployment Reference**: 
* You can [build a low-cost Google Gemma model service in Function Compute](https://www.alibabacloud.com/help/en/functioncompute/fc/use-cases/low-cost-deployment-of-google-gemma-model-service-based-on-function)to experience FC’s deployment capabilities.

### 3.2 Deploying models using PAI-EAS

You can deploy models downloaded from open-source communities or trained yourself as online services using PAI-EAS (Elastic Algorithm Service) on Alibaba Cloud's PAI.
PAI-EAS provides enterprise-grade features such as:

* Elastic scaling
* Blue-green deployment
* Resource group management
* Version control
* Real-time resource monitoring

These help you efficiently manage and operate model services in production.

PAI-EAS is particularly suitable for real-time synchronous inference scenarios. To address long initial response times, it includes a model warm-up feature that pre-initializes the model before going live—ensuring the service is ready to respond immediately after deployment.

Compared to Function Compute, PAI-EAS typically has higher fixed costs. For low-traffic use cases, it may be less cost-effective than FC. However, you can reduce costs by using Spot Instances. For guidance, see: [PAI-EAS Spot Best Practices](https://www.alibabacloud.com/help/en/pai/use-cases/pai-eas-spot-best-practices).

**Deployment Reference**: 
* Try [Deploy LLM Applications with EAS in 5 Minutes](https://www.alibabacloud.com/help/en/pai/user-guide/deploy-an-llm/) to quickly set up a general-purpose model and experience PAI-EAS's capabilities.
* For custom models, refer to: [How to Mount Custom Models?](https://www.alibabacloud.com/help/en/pai/user-guide/deploy-an-llm/#c1d769ba33kh5).

### 3.3 Deploying models using Elastic Computing Service or Container Services

Deploying models via Elastic Compute Service (ECS) is a widely adopted approach, offering full control over server configurations, operating systems, and software environments. This is ideal for models requiring deep customization or specific dependencies.

ECS provides stable computing resources and avoids cold-start delays common in serverless platforms. It can be combined with:

* Elastic Scaling Service (ESS) for automatic scaling
* Load Balancers (SLB) for high availability and traffic distribution
* Security groups, access control, and data encryption for enhanced security

However, managing these components requires technical expertise, leading to higher operational and maintenance overhead.

**Suitable Scenarios:**

* LLMs requiring high customization, consistent performance, and long-term operation
* Enterprises with strong DevOps teams and a need for predictable costs and full resource control

**Unsuitable Scenarios:**

* Small projects needing rapid deployment and elasticity
* Teams with limited operational resources or sensitivity to complexity

**Deployment Reference**: 

* See [Build a secure LLM inference environment on a heterogeneous confidential computing instance](https://www.alibabacloud.com/help/en/egs/use-cases/build-a-secure-llm-inference-environment-on-gn8v-tee-related-instances) for step-by-step instructions.

If your team already has containerization experience, you can use ACK (Alibaba Cloud Kubernetes Service) with GPU-enabled nodes without learning many new concepts.

Alternatively, consider ACS (Alibaba Cloud Container Compute Service), which allows you to run GPU-powered containers directly within a familiar Kubernetes environment—while offloading cluster operations and maintenance.

**Deployment Reference**:    
- ACK: [Deploy DeepSeek Distillation Model Inference Service Based on ACK](https://www.alibabacloud.com/help/en/ack/cloud-native-ai-suite/use-cases/deploy-deepseek-distillation-model-inference-service-based-on-ack)     
- ACS: [Build QwQ-32B Model Inference Service Using ACS GPU Computing Power](https://www.alibabacloud.com/help/en/cs/user-guide/build-qwq-32b-model-inference-service-using-acs-gpu-computing-power)

### 3.4 Cloud service solution comparison and decision recommendations

When deploying models on Alibaba Cloud, selecting the right service requires balancing multiple factors, including:

* Business requirements
* Model characteristics
* Team technical capability
* Operational complexity
* Cost efficiency

Below is a comparative analysis of common cloud deployment options to help guide your decision:

| Service Name | Features | Applicable Scenarios |
| --- | --- | --- |
| Model Studio | A dedicated platform for LLMs, providing one-click deployment, model optimization, API call management, and encapsulating underlying complexities. | Rapid deployment of LLMs (such as the Qwen series), without the need to focus on infrastructure. |
| Function Compute (FC) | Serverless architecture, billed by request volume, with automatic scaling and no operations required. | Suitable for lightweight inference tasks and low-frequency access scenarios (such as scheduled tasks and event triggers). |
| PAI-EAS | An online model serving platform that supports custom model deployment, elastic scaling, monitoring, and other capabilities. | Medium and small deep learning models (such as image classification and NLP), requiring elastic scaling and fine-grained resource management. |
| Elastic GPU Service | IaaS-level resources, flexible installation of any framework and dependencies, with manual operations and maintenance required. | Custom model training/inference, requiring full control over the environment (such as complex dependencies andspecial hardware needs). |
| Container Service ACK/Container Compute Service ACS | Kubernetes cluster deployment, integrating CI/CD, automatic scaling, load balancing. | Complex microservice architectures, mixed workloads, large-scale distributed inference or training. |

Model Deployment Service Selection Recommendations:
1. What are your core requirements?
    * Rapid deployment of LLMs → Use Model Studio
        * Ideal for conversational bots, generative AI, and quick prototyping.
    * Low-cost lightweight services / low-frequency non-real-time tasks → Use Function Compute (FC) 
        * Suitable for small tools handling hundreds of queries per day.
    * Conventional model deployment (image, text, NLP) → Use PAI-EAS 
        * Offers a good balance between performance and ease of use.
    * Custom environments or complex dependencies → Use Elastic GPU Service or ACK
        * Best for advanced customization and control.
2. Is the service compatible with your model?
    *  Tongyi series models: Prioritize Model Studio for native support and optimization.
    * General-purpose models: Supported across multiple platforms:
        * Function Compute FC
        * PAI-EAS
        * Elastic GPU Service (supports TensorFlow, PyTorch, ONNX ecosystems)
        * Containerized deployment via ACK/ACS
3. Operations Complexity and Team Technical Capabilities?
    * No operations needed / non-technical teams → Model Studio Visual interface, minimal setup, no DevOps required.
    * Low operational complexity :
        * Algorithm engineers → PAI-EAS
        * Development teams → Function Compute FC
    * High operational complexity :
        * Mature DevOps teams → ACK (requires managing pipelines and clusters)
        * Or Elastic GPU Service (manual environment management)
4. Cost Control
    * Low-cost, lightweight scenarios → FC
        * Billed by request count and resource usage—no cost when idle.
    * Moderate cost, stable traffic → PAI-EAS
        * Billed by instance type and duration. Can be optimized using auto-scaling.
    * Higher cost but flexible → Elastic GPU Service
    * Pay-as-you-go or subscription-based. Requires manual optimization of resource utilization.
    * Comprehensive cost (infrastructure + management) → ACK
        * Includes cluster management fees and scheduling complexity—justified for large-scale deployments.

## ✅Summary 

In this lesson, you’ve learned the fundamentals of model deployment:

* How to deploy a model—whether open-source or fine-tuned—as an accessible inference service through practical steps.
* Deployment is not mandatory: You can  call fully managed API services (such as from Alibaba Cloud) to reduce initial investment and avoid wasting idle GPU resources.
* How to choose the right cloud service—such as Model Studio, FC, PAI-EAS, ECS, ACK, or ACS—based on your business needs, team capabilities, and cost considerations, achieving an optimal balance between performance and efficiency.

By mastering these deployment methods, you now have a solid foundation for building high-performance, scalable LLM applications.

Next, you’ll learn how to ensure availability, security, and performance of models in real-world production environments.

>⚠️ **Note**: After completing this lesson, please stop your current PAI-DSW GPU instance to avoid unnecessary charges.

## Further reading

The course has focused on cloud deployment, which in practice can be divided into:

**Public Cloud Deployment**

* The model is encapsulated as an API and hosted on a public cloud platform (similar to SaaS).
* Lowers the barrier to entry and simplifies integration.
* Requires attention to API stability, rate limiting, and security (such as authentication and data encryption).

**Private Cloud Deployment**

* Deploy the model within an enterprise’s private cloud infrastructure.
* Offers higher data security, compliance control, and customization options.
* Involves higher maintenance costs and requires dedicated IT resources.

**Edge-Cloud Collaborative Deployment**

Combines the strengths of both edge and cloud computing:
* Simple or latency-sensitive tasks are processed on edge devices (such as mobile phones and IoT devices).
* Complex computations are offloaded to the cloud.

This approach enables fast response times while leveraging powerful cloud resources for heavy lifting.

Use Case Example: Rakuten’s collaboration with Tongyi LLM to build an end-side companion intelligent voice bot.

* The "end" refers to a small, fine-tuned model running locally on the client device, responsible for basic tasks like wake-word detection and input preprocessing.
* The "cloud" hosts the full LLM, which performs deep reasoning and generates responses.
* Preprocessed data is sent to the cloud, and results are returned quickly—balancing speed, efficiency, and intelligence.

*(Screenshot: vLLM serving the model — "Uvicorn running" means the OpenAI-compatible model service is ready to accept inference requests.)*

**Embedded System Deployment**

In specific domains such as automotive systems, robots, and medical devices, deploying models directly onto embedded hardware is often necessary.

* Enables real-time decision-making and control.
* Requires significant model compression (such as quantization and pruning) and hardware-level optimization.
* Commonly uses frameworks like TensorFlow Lite, ONNX Runtime, or specialized SDKs.

When evaluating deployment options for real-world applications, always consider:

* Performance and latency requirements
* Data privacy and regulatory compliance
* Implementation and maintenance complexity

Choose a solution that ensures efficiency, scalability, and long-term sustainability.
