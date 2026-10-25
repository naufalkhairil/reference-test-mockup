# 2.7 Enhancing model capabilities through fine-tuning  

## 🚄 Preface

In the previous lessons, we introduced how to build a Q&A bot and attempted to enhance its capabilities by optimizing prompts, constructing RAG chatbot, and adding plugins. However, you may have noticed that these methods essentially patch around the model—enhancing performance through external tools while the model's inherent knowledge boundaries and reasoning abilities remain fundamentally unchanged. This section will take you into the "training ground" of LLMs, directly improving the model’s underlying capabilities through fine-tuning techniques.

When facing in-depth needs in specific domains, such as precise parsing of elementary school math problems, relying on prompt engineering and RAG chatbot often falls short. For details like operator precedence rules or unit conversion logic in word problems, the model needs to establish a structured knowledge system. This is where fine-tuning demonstrates its unique advantage: by "targeted feeding" the model with problem-solving examples carefully crafted by elementary math education experts, the model can learn expert teaching methodologies, internalize mathematical thinking paradigms, and effectively enhance its problem-solving capabilities.

## 🍁 Goals

In this lesson you will:
* Learn about the core principles and implementation logic of fine-tuning LLMs.
* Combine training principles to master the methodology for optimizing key training parameters.
* Independently complete the fine-tuning of a model, learn about potential issues that may arise, and practice various solutions.

## 0. Environment preparation

Since fine-tuning models require high hardware performance, it is recommended to use Platform for AI (PAI)'s Data Science Workshop to create an instance equipped with a GPU, allowing you to complete the fine-tuning tasks more efficiently.

> If you do not have a local GPU environment or your GPU memory is less than 30 GB, it is not recommended to run this course locally, because the code may fail to execute.

Please refer to "[1_0_Setup_Computing_Environment](https://edu.aliyun.com/course/3137700/lesson/344300122)" under `Step 1: Create a PAI DSW Instance` to create a new instance, with the following instructions:

1. Ensure that the new instance has a **different name** from any previously created instance, such as `acp_gpu`  
2. For **resource specifications**, select `ecs.gn7i-c8g1.2xlarge` (this specification includes **one A10 GPU with 30GB of memory**).
<img src="https://img.alicdn.com/imgextra/i4/O1CN01L3iYeb1MRuEvXhhcD_!!6000000001432-2-tps-2984-1582.png" width="900">  
3. For the **image**, choose `pytorch2.3.1`, for example `modelscope:1.29.0-pytorch2.3.1tensorflow2.16.1-gpu-py311-cu121-ubuntu22.04` (you need to switch the "Image Configuration" -> "Chip Type" to GPU).

After the instance is successfully created and its status is `Running`, enter the following command in the `Terminal` to obtain the ACP course code:

    ```bash
    git clone https://github.com/AlibabaCloudDocs/aliyun_acp_learning.git
    ```

Reopen this chapter in the `Notebook` of the newly created GPU instance and continue learning the subsequent content.<br>

Install the following dependencies:

```python
# The following dependencies need to be installed
%pip install accelerate==1.0.1 rouge-score==0.1.2 nltk==3.9.1 ms-swift[llm]==2.4.2.post2 evalscope==0.5.5rc1 transformers==4.45.2 trl==0.12.2 autoawq==0.2.6 autoawq-kernels==0.0.7 modelscope==1.18.1
```

```text
zsh:1: no matches found: ms-swift[llm]==2.4.2.post2
Note: you may need to restart the kernel to use updated packages.
```

## 1. Task design

How to solve mathematical problems has long been an important direction in the development of LLMs, and it just so happens that your intelligent assistant also needs to have basic computational capabilities. To facilitate fine-tuning of the model, select the small-parameter open-source model `qwen2.5-1.5b-instruct` as your base model.

First, download the model and load it into memory:

```python
# Download model parameters to the ./model directory
!mkdir ./model
!modelscope download --model qwen/Qwen2.5-1.5B-Instruct --local_dir './model'

from swift.llm import (
    get_model_tokenizer, get_template, ModelType,
    get_default_template_type
)
import torch

# You can modify the query (model input) according to your needs

# Obtain model information
model_type = ModelType.qwen2_5_1_5b_instruct
template_type = get_default_template_type(model_type)
# Set the local model location
model_id_or_path = "./model"
# Initialize the model and input/output formatting template
kwargs = {}
model, tokenizer = get_model_tokenizer(model_type, torch.float32, model_id_or_path=model_id_or_path, model_kwargs={'device_map': 'cpu'}, **kwargs)
model.generation_config.max_new_tokens = 128
template = get_template(template_type, tokenizer, default_system='')
print("Model initialization completed")
```

Let's see how it works on math problems. (Correct answer: 648 kg.)

```python
from swift.llm import inference
from IPython.display import Latex, display

math_question = "In a triangular vegetable field with a base of 18 meters and a height of 6 meters, radishes are planted. If 12 kilograms of radishes are harvested per square meter, how many kilograms of radishes can be harvested from this field?"
query = math_question
response, _ = inference(model, template, query)
print(query)
print("The correct answer is: 648 kilograms of radishes can be harvested")
print('-----------LLM response-------------')
display(Latex(response))
print('------------End of response--------------')
```

It seems that your model cannot accurately compute this simple mathematical problem. The model knows the formula for the area of a triangle, but fails to apply this knowledge to accurately calculate the weight of the radish.

Using RAG yields the same result. As you learned previously, RAG resembles an open-book exam. However, you have never seen an open-book math exam improve scores, because the core of improving math ability lies in enhancing students' logical reasoning and computational skills, rather than knowledge retrieval.
To enhance your Q&A bot's ability to solve simple mathematical problems, you must use model fine-tuning to improve the model’s logical reasoning ability. Computational ability can be enhanced by integrating a "calculator" plugin.

## 2. Fine-tuning principles

### 2.1 How models learn

#### 2.1.1 Machine learning - finding patterns through data

In traditional programming, you usually know the explicit rules, and write these rules into functions. For example: $f(x) = ax$.

Here, $a$ is a known deterministic value (also called a parameter or weight). This function represents a simple algorithmic model that can compute (predict) the output $y$ based on the input $x$.

However, in real-world scenarios, it's more likely that you don't know the explicit rules (parameters) beforehand, but you may have some observed phenomena (data).

The goal of machine learning is to help you use this data (training set) to try and find (learn) these parameter values, a process known as training the model.

#### 2.1.2 loss function & Cost function - quantifying model performance

To find the most suitable parameters, you need a way to measure whether the tested parameters are appropriate.

Assume you now need to evaluate whether the parameter $a$ in the model $f(x) = ax$ is suitable.

##### Loss function

You can assess the model's performance on a single data point $x_i, y_i$ by subtracting the predicted result $f(x_i)$ from the actual result $y_i$ for each sample $x_i$ in the training set. The function used to evaluate this error is called the loss function (or error function): $L(y_i, f(x_i)) = y_i - ax_i$.

Calculating the difference might yield positive or negative values. These could cancel each other out when aggregating losses, underestimating the total loss. To address this issue, you can consider squaring the difference as the loss: $L(y_i, f(x_i)) = (y_i - ax_i)^2$. Additionally, squaring amplifies the impact of errors, helping you identify the most suitable model parameters.

> In practical applications, models may use different calculation methods as the loss function.

##### Cost function

To evaluate the model's overall performance across the entire training set, you can calculate the average loss of all samples (that is, the mean squared error). This function, used to assess the model's overall performance across all training samples, is called the cost function.

For a training set with m samples, the cost function can be expressed as: $J(a) = \frac{1}{m} \sum_{i=1}^{m} (y_i - ax_i)^2$.

> In practical applications, different models may also choose different calculation methods as the cost function.

With the cost function, the task of finding suitable model parameters can be equated to finding the minimum value of the cost function (i.e., the optimal solution). Finding the minimum value of the cost function means that the corresponding value of parameter a is the most suitable model parameter value.

If you plot the cost function, the task of finding the optimal solution essentially involves finding the lowest point on the curve or surface.
<div style="text-align: center">
<img src="https://img.alicdn.com/imgextra/i4/O1CN0149XTTS1WUKSTtpeoh_!!6000000002791-2-tps-2314-1682.png" style="width: 400px; display: block; margin-left: auto; margin-right: auto"/>
</div>

> In real-world projects, people often interchangeably use the terms cost function and loss function. In subsequent content and code, we will follow this engineering convention and refer to the cost function as the loss function.

#### 2.1.3 Gradient descent algorithm - automatically determining the optimal solution

In the previous figure, you can visually identify the lowest point. However, in practical applications, models typically have many parameters, and their loss functions are often complex surfaces in high-dimensional spaces, making it virtually impossible to find the optimal solution through direct observation. You need an automated method to find the optimal parameter configuration.

Gradient descent is one of the most common methods for this. A typical implementation of gradient descent starts by randomly selecting a starting point on the surface (or curve), then continuously making small adjustments to the parameters until it finds the lowest point (corresponding to the optimal parameter configuration).

<div style="text-align: center">
<img src="https://img.alicdn.com/imgextra/i2/O1CN01ihhR9Y1IbkFZTQ3bV_!!6000000000912-1-tps-1080-810.gif" style="width: 400px;margin-left: auto; margin-right: auto"/>
<img src="https://img.alicdn.com/imgextra/i3/O1CN01meUISA1dHgq2mqm6V_!!6000000003711-1-tps-1080-810.gif" style="width: 400px;margin-left: auto; margin-right: auto"/>
</div>

When training a model, you need the training program to automatically adjust the parameters so that the value of the loss function approaches the lowest point. Therefore, the gradient descent algorithm must automatically control two aspects: the direction and the magnitude of parameter adjustment.

##### Direction of parameter adjustment

If the loss function is a U-shaped curve, you can intuitively see that the parameter adjustment should move in the direction where the absolute value of the slope decreases, that is, towards a flatter area.
<div style="text-align: center">
<img src="https://img.alicdn.com/imgextra/i2/O1CN01ME3u6G203FVsQsmLe_!!6000000006793-2-tps-1608-1244.png" style="width: 400px; display: block; margin-left: auto; margin-right: auto"/>
</div>

If the loss function is a surface in a three-dimensional coordinate system, the direction of parameter adjustment should similarly move towards a flatter area. However, at a certain point on the surface, there are multiple possible descending directions. To find the lowest point as quickly as possible, you should move in the steepest direction.
<div style="text-align: center">
<img src="https://img.alicdn.com/imgextra/i2/O1CN01Uh8OxI1mqnkBHqMjH_!!6000000005006-1-tps-664-684.gif" style="width: 400px; display: block; margin-left: auto; margin-right: auto"/>
</div>

In mathematics, the gradient points in the direction of the steepest ascent from a point on the surface, and its opposite direction is the steepest descent.

To find the lowest point on the surface in the shortest time, parameter adjustment should follow the opposite direction of the gradient, denoted by the green arrow direction in the two figures above.

> For a curve f(a) in a two-dimensional coordinate system, the gradient at a point is the slope at that point. 
> For a surface f(a,b) in a three-dimensional coordinate system, the gradient at a point is a two-dimensional vector composed of the slope values in the a and b axis directions. This indicates the rate of change of the function in each input variable direction and points in the direction of the fastest growth. Calculating the slope of a point on the surface in a particular axis direction is also referred to as taking the partial derivative.

##### Magnitude of parameter adjustment

After determining the direction of parameter adjustment, we need to determine the magnitude of the adjustment.

Adjusting parameters with a fixed step size is the easiest approach, but this may prevent you from ever finding the lowest point, instead causing oscillation near the lowest point.

In the figure below, adjusting parameters with a fixed step size of 1.5 results in oscillation around the lowest value, but it's unable to reach the lowest point.

<div style="text-align: center">
<img src="https://img.alicdn.com/imgextra/i3/O1CN01y7FatQ27bKI9CYCJ1_!!6000000007815-1-tps-938-646.gif" style="width: 400px; display: block; margin-left: auto; margin-right: auto"/>
</div>

To avoid this issue, the adjustment magnitude should be reduced as you approach the lowest point. The closer you get to it, the smaller the slope should become. Instead of using a fixed step size, you can use the slope at the current position as the adjustment magnitude.

<div style="text-align: center">
<img src="https://img.alicdn.com/imgextra/i3/O1CN01h45Ifb1xRZhXXIXEC_!!6000000006440-1-tps-892-618.gif" style="width: 400px; display: block; margin-left: auto; margin-right: auto"/>
</div>

However, some loss function curves are very steep, and simply using the slope may still cause oscillation around the lowest point. To address this, multiply the slope by a coefficient to regulate the step size. This coefficient is called the learning rate.

The choice of learning rate is particularly important for training effectiveness and efficiency:

<div style="display: flex; justify-content: space-between; gap: 2px; padding: 15px; background:rgba(0,0,0,0)">
    <!-- Column 1 -->
    <div style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px">
        <p style="margin-top: 10px">An appropriate learning rate allows you to find suitable parameters in a short time.</p>
        <img src="https://img.alicdn.com/imgextra/i3/O1CN01NrvVfj1sCqtKHLyia_!!6000000005731-2-tps-1680-1224.png" style="width: 100%; height: auto; border-radius: 3px"/>
    </div>
    <!-- Column 2 -->
    <div style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px">
        <p style="margin-bottom: 10px">An excessively low learning rate, while capable of finding suitable parameters, leads to greater time and resource consumption.</p>
        <img src="https://img.alicdn.com/imgextra/i1/O1CN015dbcz61MCn8LkN2Ta_!!6000000001399-2-tps-1728-1300.png" style="width: 100%; height: auto; border-radius: 3px"/>
    </div>
    <!-- Column 3 -->
    <div style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px">
        <p style="margin-bottom: 10px">Meanwhile, an excessively high learning rate may cause you to skip the optimal solution, ultimately failing to find the lowest point.</p>
        <img src="https://img.alicdn.com/imgextra/i1/O1CN01l4leTB1LKI0BcVs16_!!6000000001280-2-tps-1658-1262.png" style="width: 100%; height: auto; border-radius: 3px"/>
    </div>
</div>


A smaller learning rate, although more computationally expensive and time-consuming, enables the optimization process to converge more precisely toward the minimum of the cost function. In practical model training, dynamic adjustment of the learning rate is commonly employed to balance convergence speed and accuracy. For example, Alibaba Cloud's PAI also provides an [AutoML](https://www.alibabacloud.com/help/en/pai/user-guide/automl/) tool that can automatically search for an optimal learning rate, reducing manual tuning effort and improving training efficiency.

#### 2.1.4 Key Hyperparameters in Model Training


In the upcoming fine-tuning experiments, you'll be repeatedly adjusting parameters, observing results, and adjusting again. This section explains each parameter through the **real problems you'll encounter** during training.

##### learning_rate

Your first fine-tuning run will most likely go like this: training starts, but instead of decreasing smoothly, the loss curve oscillates wildly or even shoots upward. The model isn't learning at all. This is almost always because the learning rate is too high — the model overshoots the optimal point on every step and never settles down.

For LoRA fine-tuning of large models, the learning rate is typically in the range of **1e-5 to 5e-4**, much smaller than training from scratch. The reason is straightforward: a pretrained model already has extensive general knowledge, and fine-tuning only needs to make small adjustments on top of that. Too large a step will destroy what the model has already learned. On the other hand, setting the learning rate too low isn't great either — loss decreases painfully slowly, wasting compute and time.

In the experiments ahead, you'll experience this firsthand: learning_rate=0.1 causes training to fail completely, while lowering it to 0.00005 makes the loss curve drop smoothly right away.

##### num_train_epochs

Epochs control how many times the model goes through the entire training dataset from start to finish. This parameter will have you caught between two failure modes.

The first is **underfitting**: training finishes, but both training loss and eval loss are still decreasing — the model hadn't learned enough before you stopped it. The fix is straightforward: increase the number of epochs so the model gets more learning time.

So you crank up the epochs, and then hit the second problem: **overfitting**. Training loss keeps dropping nicely, but eval loss starts rising at some point. If you test the model, it can answer the exact questions from the training data but fails on anything phrased differently — it memorized the answers instead of learning the underlying knowledge. To address overfitting, you can either reduce the epochs so the model trains less, or increase the training data so it can't get by on memorization alone. A common engineering practice is **early stopping**: instead of setting a fixed number of epochs, you monitor eval loss throughout training and automatically stop when it starts rising.

In the experiments ahead, you'll go through the full cycle: epoch=1 underfits → epoch=50 overfits → with 1,000 training samples, epoch=15 hits the sweet spot.

##### lora_rank

lora_rank determines how many parameters the model can adjust during fine-tuning. Think of it as the model's "learning capacity": a smaller rank limits how much new knowledge it can absorb; a larger rank gives it more room to learn, but also makes overfitting more likely and uses more GPU memory.

The key principle is that **rank should match your data volume**. For small datasets (under 1,000 samples) or simple tasks (format conversion, style transfer), rank 4–8 is usually sufficient. For larger datasets or complex tasks (domain-specific reasoning, specialized knowledge), you can try rank 16–64. If you have very little data but set a high rank, the model will most likely memorize the training data rather than learn generalizable patterns.

In the experiments ahead, when the dataset grows from 100 to 1,000 samples, lora_rank increases from 4 to 8 — more data means the model needs more learning capacity to absorb the new knowledge.

##### batch_size

Batch size determines how many training samples are processed simultaneously in each training step. The most common issue is **running out of GPU memory**: training crashes halfway through with a `CUDA out of memory` error, usually because batch_size is too large for the GPU to handle.

But you can't just keep making it smaller either. If you drop batch_size to 1, the loss curve will be extremely noisy — estimating the gradient from a single sample introduces too much randomness, causing the model's learning direction to zigzag erratically. For LoRA fine-tuning, starting with 4 or 8 and adjusting based on available memory is a good rule of thumb.

If you want the stability of a large batch but don't have enough memory, **gradient accumulation** is the solution: for example, batch_size=4 with gradient_accumulation_steps=4 gives you the effective behavior of batch_size=16 while only using the memory footprint of batch_size=4.

In the experiments ahead, batch_size increases from 8 to 16 to speed up training when the number of epochs is increased.

##### max_length

Training data varies in length, and max_length sets the cap on how long each sample can be. Set it too low, and longer samples get truncated — the model learns from incomplete information, which naturally hurts quality. Set it too high, and each sample consumes more memory, potentially causing OOM errors.

The approach is to check the length distribution of your training data and set max_length to cover the vast majority (95%+). When memory is tight, max_length and batch_size work together — reducing max_length frees up memory that can be used for a larger batch_size. In this experiment, max_length is set to 512 since the math problem solutions are relatively short.

##### eval_steps

Imagine you set epoch=50, let the training run to completion, and only then discover that eval loss started rising at epoch 10 — the remaining 40 epochs were completely wasted, burning hours of GPU time for nothing. If you had evaluated the model periodically during training, you could have caught this early.

eval_steps controls this "check-up frequency": how many training steps between each evaluation on the validation set. Setting it too low (e.g., evaluating every single step) slows down training noticeably; setting it too high risks missing the overfitting turning point entirely. A practical guideline is to evaluate every 5–10% of total training steps.

> 💡 The ms-swift framework automatically saves a model checkpoint at each evaluation, and marks the checkpoint with the lowest validation loss as `best_model_checkpoint` when training completes. Setting eval_steps properly doesn't just help you monitor training — it also ensures the best model is automatically preserved.

#### 2.1.5 Neural network - a universal complex function approximator

**Challenges in machine learning**

In complex tasks such as text generation, both input x and output y are typically high-dimensional, making it difficult to discern explicit patterns or relationships from raw data.

To address this challenge, researchers have turned to neural networks—particularly deep (multi-layer) architectures—as powerful tools for modeling intricate, non-linear mappings.

<div style="text-align: center">
<img src="https://img.alicdn.com/imgextra/i1/O1CN01QRD5MH1rwMdJHBzxi_!!6000000005695-2-tps-1080-533.png" style="width: 400px; display: block; margin-left: auto; margin-right: auto"/>
</div>

One layer of a neural network is generally expressed as $Y=σ(W⋅X)$, where the uppercase input $X$ and output $Y$ indicate they are multi-dimensional, $σ$ is the activation function, and $W$ represents the parameters of the assumed function $f$. A k-layer neural network can be expressed as $Y=σ(W_k ⋯ σ(W_2 ⋅σ(W_1⋅X)))$.

The activation function is a key component in neural networks that introduces non-linear transformations and determines whether neurons are activated and transmit information. For example, the most commonly used activation function RELU can be written as:

**$RELU(input) = max( 0, input)= \begin{cases} input & \text{if } input > 0 \\ 0 & \text{if } input ≤ 0 \end{cases}$**

When $input≤0$, the neuron is not activated; when $input>0$, the neuron is activated and begins transmitting information to the output.

Expanding one layer of a neural network can be written as follows (assuming $X$ is a $3×2$ dimensional matrix and $Y$ is a $2×2$ dimensional matrix):

$σ(W_{2×3}⋅X_{3×2})= σ(\left[ \begin{matrix} w_{1,1} & w_{1,2} & w_{1,3} \\ w_{2,1} & w_{2,2} & w_{2,3} \end{matrix} \right]×\left[ \begin{matrix} x_{1,1}& x_{1,2}\\ x_{2,1}& x_{2,2} \\ x_{3,1}& x_{3,2} \end{matrix} \right])$

$= σ(\left[\begin{matrix}
w_{1,1}×x_{1,1}+w_{1,2}×x_{2,1}+w_{1,3}×x_{3,1}&
w_{1,1}×x_{1,2}+ w_{1,2}×x_{2,2}+w_{1,3}×x_{3,2} \\
w_{2,1}×x_{1,1}+ w_{2,2}×x_{2,1}+w_{2,3}×x_{3,1}&
w_{2,1}×x_{1,2}+ w_{2,2}×x_{2,2}+w_{2,3}×x_{3,2} \end{matrix} \right])$

$= \left[ \begin{matrix} max(0, \sum\limits_{k=1}^{3}w_{1,k}×x_{k,1})& max(0, \sum\limits_{k=1}^{3}w_{1,k}×x_{k,2})\\ max(0, \sum\limits_{k=1}^{3}w_{2,k}×x_{k,1})& max(0, \sum\limits_{k=1}^{3}w_{2,k}×x_{k,2}) \end{matrix} \right]= \left[ \begin{matrix} y_{1,1}& y_{1,2}\\ y_{2,1}& y_{2,2} \end{matrix} \right]=Y_{2×2}$

Fortunately, the gradient descent method remains effective on high-dimensional, complex functions.

<div style="text-align: center">
<img src="https://img.alicdn.com/imgextra/i3/O1CN011caxP31GiUrEv1aGH_!!6000000000656-2-tps-847-779.png" style="width: 400px; display: block; margin-left: auto; margin-right: auto"/>
</div>

Now you have the winning combination:

**A powerful function approximator—the neural network, capable of modeling virtually any complex, non-linear relationship—paired with an efficient optimization algorithm—gradient descent, designed to learn optimal model parameters by minimizing the loss function.**

### 2.2 Efficient fine-tuning techniques

#### 2.2.1 Pre-training and fine-tuning

From earlier discussions, you've learned that the core of model training lies in finding an optimal set of parameters that minimize the loss function.

The model you initially download—such as `qwen2.5-1.5b-instruct`—is not randomly initialized; it consists of pre-trained parameters obtained through extensive training on large-scale, diverse datasets. This pre-training equips the model with broad linguistic understanding and general reasoning capabilities.

Fine-tuning refers to the process of further adjusting these pre-trained parameters using a smaller, task-specific dataset, enabling the model to specialize in particular applications—such as solving math problems, answering domain-specific questions, or generating legal documents.

To appreciate the value of this two-stage approach, let’s examine what it would take to train such a model from scratch, using `qwen2.5-1.5b-instruct` (a 1.5-billion-parameter model) as an example.

---

#### GPU memory requirements

* Memory occupied by 1.5 billion parameters (assuming FP32 precision, with each parameter taking 4 bytes):  
    $ \frac{1.5 \times 10^9 \times 4}{2^{30}} \approx 5.59 \text{ GB} $

* In practice, training a model typically requires **7–8 times** the memory of its parameter size due to gradients, optimizer states, and intermediate activations. This brings the total GPU memory requirement to around **45 GB**, which exceeds most consumer-grade GPUs, and even many cloud-based experimental environments.

---

#### Training time estimation

*   Example calculation:  
    - Total training tokens = **200 billion**, or about 250,000 copies of Shakespeare's complete works
    - Batch size (using 8 GPUs in parallel) = **2,000 tokens per batch**  
    - Throughput = **150 tokens/GPU/sec × 8 GPUs = 1,200 tokens/sec**

*   Estimated training time =  
    $$
    \frac{\text{Total Tokens}}{\text{Batch Size} \times \text{Tokens per Second} \times 86400} \approx 10 \text{ days}
    $$

*   Real-world considerations:  
    Include data preprocessing, checkpoint saving, and communication overhead in distributed training can increase actual training time by **20–50%**. With larger datasets—such as 1 trillion tokens—training duration could extend to over a year, even with optimization.

---

#### Training cost overview

*   For short-term training (such as 10-day training runs), renting cloud GPU instances on a pay-as-you-go basis is often more cost-effective than purchasing dedicated hardware.
*   Training cost formula:  
    $$
    \text{Training Cost} = \text{GPU hourly rate} \times \text{Training time (in hours)}
    $$

---


In summary, **reducing server unit price** and **shortening training time** can effectively reduce training costs, where **reducing memory requirements** lower server unit price, and reducing **total training data volume** shorten training time.

<br/>

A practical challenge in model training is **the high cost of obtaining labeled data, especially for specific tasks** (such as medical image analysis or niche language processing). You can try step-by-step training of the model through "pre-training" and "fine-tuning":

* **Pre-training**: Training the model on a large-scale **general dataset** so that it can learn broad foundational knowledge or feature representations. This knowledge is usually general and not aimed at any specific task. Pre-training is not task-specific, but provides a powerful initial model for various downstream tasks. Typical pre-trained models: Qwen2.5-Max, DeepSeek-V3, GPT-4.
* **Fine-tuning**: Further training the model using a **small-scale dataset** specific to a task based on the pre-trained model. The goal is to adapt the model to specific downstream tasks (such as medical, legal, and other professional domain needs).

The table below shows the main differences between pre-training and fine-tuning:

<div style="width: 20%">
    
|  **Feature**  |  **Pre-training**  |  **Fine-tuning**  |
| --- | --- | --- |
|  Objective  |  $ $ Learning general features  |  Adapting to specific tasks  |
|  Data  |  Large-scale general data  |  Small-scale task-related data  |
|  Training method  |  Self-supervised/Unsupervised  |  Supervised  |
|  Parameter updates  |  All parameters trainable  |  Partial or all parameters trainable  |
|  Application scenarios  |  Base model construction  |  Specific task optimization  |

</div>

It is worth mentioning that **pre-training generally learns through self-supervised learning**, with data coming from massive texts available on the internet (including Wikipedia, books, and web pages), allowing the model to find patterns or "guess " on its own. This learning method does not require manual annotation, saving significant labor costs and making it naturally suitable for learning from massive data.

In contrast, **fine-tuning is done through supervised learning**, requiring small-scale annotated data for specific tasks (such as annotated reviews for sentiment classification, or annotated medical texts), and directly teaching the model to complete tasks using annotated data. Due to the high cost of manual annotation, this learning method is difficult to scale to massive data, thus making it more suitable for model training with clear scenario goals, typically requiring only a few thousand to tens of thousands of samples.

Therefore, you can quickly and cost-effectively build your LLM application as follows:

Step 1: Choose a pre-trained model (Qwen, DeepSeek, GPT). This can save the comprehensive cost of training a model from scratch.

Step 2: Fine-tune the model according to your actual scenario, usually only needing to build a few thousand annotated data applicable to the actual scenario, because the total number of training tokens is greatly reduced. This effectively shortens the training time, thereby further reducing the training cost.

Fine-tuning can shorten training time, but can fine-tuning the model also reduce memory requirements?

The number of model parameters is the main factor affecting memory requirements. From the perspective of adjusting the size of the parameter count, fine-tuning can be divided into **full-parameter** and **parameter-efficient fine-tuning**.

**Full-parameter fine-tuning**, also known as **full fine-tuning**, is an optimization approach that updates all parameters of a pre-trained model during adaptation to a downstream task. In this method, every layer and weight in the model architecture is trainable and can be adjusted based on task-specific data.

This strategy offers two key advantages:

* It avoids the prohibitive cost of training a model from scratch by leveraging powerful pre-trained representations.
* It ensures no part of the model is frozen, reducing the risk of performance degradation due to under-adapted components.

However, despite its effectiveness, full fine-tuning remains computationally expensive, especially for large-scale models. It demands:

* Significant GPU memory (for storing gradients and optimizer states),
* High-throughput hardware,
* Long training times,
* Large volumes of high-quality labeled data.

As a result, while full fine-tuning often achieves strong performance, it is not always practical—particularly in resource-constrained environments.
To address these challenges, **Parameter-Efficient Fine-Tuning (PEFT)** methods have emerged as a powerful alternative. PEFT techniques adapt large pre-trained models by updating only a small subset of parameters, while keeping the majority of the original model weights frozen. Remarkably, they achieve performance close to full fine-tuning—with drastically reduced computational and storage costs.

Popular PEFT methods include:

* Adapter Tuning: Inserts small neural network modules ("adapters") between transformer layers.
* Prompt Tuning: Learns task-specific soft prompts (continuous embeddings) while freezing the model.
* LoRA (Low-Rank Adaptation): A leading method that approximates weight changes using low-rank matrices—requiring only 0.1% to 1% of the original model’s parameters to be trained.

Among these, LoRA has become the preferred choice in many real-world applications, particularly when compute, memory, or budget are limited.


#### 2.2.2 LoRA Fine-tuning

LoRA (Low-Rank Adaptation) is currently the most widely used efficient fine-tuning method. It does not depend on the internal architecture of the model. Instead, it approximates the weight updates required during fine-tuning as a low-rank matrix and decomposes this update into two much smaller trainable matrices $ A_{d \times r} $ and $ B_{r \times d} $. The original pre-trained weights remain frozen (i.e., unchanged), and the fine-tuned weight matrix is expressed as:

$$
W^{\text{fine-tuned}}_{d \times d} = A_{d \times r} \cdot B_{r \times d} + W^{\text{pre-trained}}_{d \times d}
$$

Here, $ d $ denotes the dimension of the weight matrix (typically the hidden size of the model), and $ r \ll d $ is a predefined low-rank dimension.

To illustrate the concept of low-rank decomposition, consider a simple neural network example. Suppose the input vector $ X $ has dimension 4 and the output vector $ Y $ has dimension 5. Then the weight matrix $ W \in \mathbb{R}^{5 \times 4} $ contains a total of 20 parameters.

> 💡 Note: This is a pedagogical example. By convention, the weight matrix is sized as “output × input” so that $ Y = WX $ is valid with $ W \in \mathbb{R}^{5 \times 4} $.

The forward pass of a single-layer neural network can be written as:
$$
Y_{5 \times 1} = \sigma(W_{5 \times 4} \cdot X_{4 \times 1})
$$

Intuitively, the rank of a matrix reflects its “effective information content” or degree of linear independence among its rows or columns. For instance, the following $ 2 \times 3 $ matrix has six elements, but its second row is exactly twice the first—making all rows linearly dependent—so its rank is 1:
$$
\text{rank}\left( 
\begin{bmatrix}
1 & 2 & 3 \\
2 & 4 & 6
\end{bmatrix}
\right) = 1
$$

In large model fine-tuning, a key assumption is that **pre-training has already captured high-rank, general-purpose knowledge, while adaptation to a downstream task only requires low-rank updates**. Mathematically, this can be expressed as:
- The weight change from initialization to pre-training, $ \Delta W^{\text{pre-trained}} = W^{\text{pre-trained}} - W^{\text{initial}} $, is typically high-rank (e.g., nearly full rank);
- The additional change from pre-training to fine-tuning, $ \Delta W^{\text{fine-tuning}} = W^{\text{fine-tuned}} - W^{\text{pre-trained}} $, is low-rank, for example:
$$
\text{rank}(\Delta W^{\text{pre-trained}}_{5 \times 4}) = 5, \quad \text{rank}(\Delta W^{\text{fine-tuning}}_{5 \times 4}) \leq 2
$$

Because low-rank matrices are highly redundant, they can be exactly factorized into the product of two smaller matrices. For example, if $ \text{rank}(\Delta W^{\text{fine-tuning}}_{5 \times 4}) = 1 $, then:
$$
\Delta W^{\text{fine-tuning}}_{5 \times 4} =
\begin{bmatrix}
1 & 0 & 2 & -1 \\
2 & 0 & 4 & -2 \\
3 & 0 & 6 & -3 \\
4 & 0 & 8 & -4 \\
5 & 0 & 10 & -5
\end{bmatrix}
=
\underbrace{
\begin{bmatrix}
1 \\ 2 \\ 3 \\ 4 \\ 5
\end{bmatrix}
}_{5 \times 1}
\cdot
\underbrace{
\begin{bmatrix}
1 & 0 & 2 & -1
\end{bmatrix}
}_{1 \times 4}
= A \cdot B
$$

To further illustrate this, consider the base model `qwen2.5-1.5b-instruct`, which has a typical hidden dimension of $ d = 1536 $. If we apply LoRA with rank $ r = 8 $ (satisfying $ r \ll d $), the parameter counts compare as follows:

$$
W^{\text{fine-tuned}}_{d \times d} = A_{d \times r} \cdot B_{r \times d} + W^{\text{pre-trained}}_{d \times d}
$$

<div style="width: 60%; margin: 0 auto;">

| **Method** | **Parameter Calculation Formula** | **Number of Parameters** | **Savings Ratio** |
|------------|----------------------------------|--------------------------|-------------------|
| Full-parameter fine-tuning | $ W_{d \times d} = 1536 \times 1536 $ | 2,359,296 | 0% |
| LoRA fine-tuning | $ A_{d \times r} + B_{r \times d} = 1536 \times 8 + 8 \times 1536 $ | 24,576 | **98.96%** |

</div>

> 💡 Note: In practice, LoRA is typically applied only to specific layers—such as the query ($Q$) and value ($V$) projection matrices in attention blocks—so the actual proportion of trainable parameters is often much lower than shown here.

During inference, the matrices $ A $, $ B $, and $ W^{\text{pre-trained}} $ can be merged into a single $ W^{\text{fine-tuned}} $ either **statically** (fused before deployment) or **dynamically** (computed on-the-fly), without affecting inference efficiency.

<div style="text-align: center;">
<a href="https://img.alicdn.com/imgextra/i3/O1CN01NtGavS1TTvIIeZxO1_!!6000000002384-2-tps-804-712.png" target="_blank">
<img src="https://img.alicdn.com/imgextra/i3/O1CN01NtGavS1TTvIIeZxO1_!!6000000002384-2-tps-804-712.png" style="width: 300px;background:white;display: block; margin-left: auto; margin-right: auto"/>
</a>
<br>Image source: LORA: LOW-RANK ADAPTATION OF LARGE LANGUAGE MODELS
</div>

The most critical hyperparameter in LoRA fine-tuning is the rank $r$:

- A **larger $r$** enables the model to capture more complex task-specific features but increases memory usage and training difficulty;
- A **smaller $r$** is more efficient but may limit model expressiveness.

In practice, multiple factors should be considered when choosing $r$:

**1. Training Dataset Size:**
- **Small datasets (1k–10k samples):** Use $r \leq 16$ to avoid overfitting (i.e., memorizing the data rather than learning generalizable patterns);
- **Large datasets (100k+ samples):** Use $r \geq 32$ to better uncover underlying structures in the data.

**2. Task Complexity:**
- **Simple tasks** (e.g., format conversion, style transfer): A smaller $r$ (such as 4–8) is usually sufficient;
- **Complex tasks** (e.g., cross-lingual transfer, domain-specific reasoning): A larger $r$ (such as 16–64) may be needed to capture richer task features.

**3. GPU Memory Capacity:**
- When GPU memory is limited, opt for a smaller $r$ to ensure smooth training;
- A larger $r$ linearly increases the number of LoRA parameters ($2 \times d \times r$), thereby increasing memory usage.

**4. Base Model Parameters:**
- Models of different scales have different hidden layer dimensions $d$, so the same $r$ value corresponds to different numbers of LoRA parameters across different models;
- As the experimental findings in the [LoRA original paper](https://arxiv.org/abs/2106.09685) demonstrate: **Even for GPT-3 with 175B parameters, $r=1$ or $r=2$ can achieve results comparable to full-parameter fine-tuning**;
- This means that for larger models, since they have larger hidden layer dimensions $d$, even a small $r$ can provide sufficient expressive capacity, while smaller models may need a relatively larger $r$ to achieve comparable results.

> 💡 Note: Experiments in the LoRA original paper (Hu et al., 2021) demonstrate that the "intrinsic rank" of weight updates is typically quite small. The authors used the following $r$ values in their experiments across models of different scales: RoBERTa (125M/355M) with $r=8$, GPT-2 (345M) with $r=4$, and GPT-3 (175B) with $r=1$ to $r=8$. This suggests that the optimal choice of $r$ does not scale proportionally with model size, but requires careful trade-offs based on the specific task and available resources. See Section 7.2 of the paper: [What is the Optimal Rank r for LoRA?](https://arxiv.org/abs/2106.09685)



#### 2.2.3 Effectiveness of LoRA Fine-tuning

The authors of LoRA evaluated multiple fine-tuning methods across several tasks, plotting the number of trainable parameters (x-axis) against task performance (y-axis), such as accuracy or BLEU score:

<div style="text-align: center;">
<img src="https://img.alicdn.com/imgextra/i1/O1CN01RGquUv1ZlDuoik8zU_!!6000000003234-2-tps-1944-662.png" style="width: 700px; background: white; display: block; margin-left: auto; margin-right: auto"/>
</div>

The results clearly show that **more trainable parameters do not always lead to better performance**—some methods even degrade with increased capacity. In contrast, **LoRA achieves performance close to full fine-tuning with only a tiny fraction of trainable parameters, demonstrating exceptional cost-effectiveness, scalability, and task adaptability.**

## 3. Fine-tuning practice

### 3.1 Model training status and metrics

Training a model is very similar to the human learning and exam process.

A model must be evaluated on three sets of data and generates two key metrics to determine its training status:

Three sets of questions:

*   **Training set**: Like a practice workbook with detailed answer explanations. The model  repeatedly learns from this data and computes the training loss based on the loss function. A smaller **training loss** means the model performs better on the training set. Combined with the gradient descent method discussed in Section 2.1, the model updates its parameters based on this loss.
    
*   **Validation set**: This set is like simulated exam questions. After a period of learning, the model is tested on this data to compute the validation loss, which evaluates how well the training is progressing. A lower validation loss indicates better performance on unseen but similar data.
    
*   **Test set**: Represents real exam questions. The model's accuracy  on the test set is used to evaluate its final, overall performance.

The three states of model training:

*   **Training loss stays unchanged or increases**: This indicates **training failure**. It’s as if the model isn’t learning from the practice workbook, suggesting a problem with the learning setup—such as an inappropriate learning rate or optimization issue.
    
*   **Both training loss and validation loss are decreasing**: This means the model is **underfitting**. The model is making progress on both the training and validation sets, but it hasn't yet fully captured the underlying patterns. In this case, you should allow training to continue.
    
*   **Training loss decreases while validation loss increases**: This signals overfitting. The model is essentially memorizing the training data (like memorizing answers in a workbook) rather than learning generalizable patterns. When faced with new questions (validation set), it performs poorly. To address this, techniques that discourage memorization should be applied—such as increasing data diversity (for example, by using more varied workbooks) so the model must learn the core concepts instead of rote recall.

### 3.2 Baseline model examination

Before beginning model fine-tuning, let's first examine how the baseline model performs on the test set.

```python
import json
from IPython.display import Markdown

sum, score = 0, 0
for line in open("./resources/2_7/test.jsonl"):
    # Read math questions from the test set
    math_question = json.loads(line)
    query = math_question["messages"][1]["content"]
    # Inference using the baseline model
    response, _ = inference(model, template, query)
    # Get the correct answer
    ans = math_question["messages"][2]["content"]
    pos = ans.find("ans")
    end_pos = ans[pos:].find('}}')
    ans = ans[pos - 2: end_pos + pos + 2]
    # Format output
    print(("========================================================================================"))
    print(query.split("#Math Problem#\n")[1])
    print("The correct answer is: " + ans)
    print("-----------Model Response----------------")
    display(Latex(response))
    print("-----------End of Response----------------")
    # Calculate model score
    if ans in response or ans[6:-2] in response:
        score += 1
        print("Model answered correctly")
    else: print("Model answered incorrectly")
    sum += 1
# Summary
display(Markdown("Model scored: **" + str(int(100*score/sum)) + "** points in the exam"))
```

The baseline model often gives up reasoning midway during exams and struggles to produce correct answers. This behavior not only confirms that the questions exceed its capability but also reveals why prompt engineering alone fails: the model lacks the fundamental problem-solving skills needed to tackle such tasks. In this case, model fine-tuning is the only effective solution.

### 3.3 Model fine-tuning

In this section, we will use the [ms-swift](https://github.com/modelscope/ms-swift/tree/main) (Modelscope Scalable lightWeight Infrastructure for Fine-Tuning) framework—an open-source framework specifically developed by Alibaba's ModelScope community for efficient model training. 

This framework supports a full pipeline of model operations—including training (pre-training, fine-tuning, alignment), inference, evaluation, and deployment—for over 350 LLMs and more than 90 multi-modal LLMs (MLLMs).

Moreover, ms-swift is highly user-friendly. During training, each time the validation loss (also called evaluation loss) is computed, the framework automatically saves the current model parameters (model_checkpoint). At the end of training, it retains the version with the lowest validation loss, which corresponds to the best_model_checkpoint shown in the figure below.

<div style="text-align: center;">
<img src="https://img.alicdn.com/imgextra/i3/O1CN0150XsFO1xM4z7CUMNr_!!6000000006428-2-tps-2288-136.png" style="width: 70%;display: block; margin-left: auto; margin-right: auto"/>
</div>

In the following experiments, we will focus on adjusting three key parameters:

* learning_rate
* LoRA rank (lora_rank)
* num_train_epochs (number of training epochs)

We will also switch datasets to demonstrate how LoRA fine-tuning can be applied across different tasks. Other parameter changes—such as increasing the batch size (batch_size) to reduce training time—are made solely to speed up experimentation and improve presentation; you do not need to focus on them.

#### 3.3.1 First experiment (takes about 1 minute)

For the initial experiment, it is recommended that you start by fine-tuning the model using the following parameter settings. We’ll use a dataset of 100 problem-solution pairs generated by DeepSeek-R1 for training. This provides a solid foundation so that you can observe improvements through parameter optimization in later stages.

| Parameter | Parameter Value |
| --- | --- |
| learning rate (learning_rate) | 0.1 |
| LoRA Rank (lora_rank) | 4 |
| Training Epochs (num_train_epochs) | 1 |
| Dataset (dataset) | current directory/resources/2_7/train_100.jsonl |

<br>

> **Note**: You can adjust all parameters freely, but due to display effects and memory constraints, there are the following limitations:
  - batch_size <= 16 (memory constraint) 
  - max_length <= 512 (maximum length of each training data, memory constraint) 
  - lora_rank <= 64 (LoRA rank, memory constraint) 
  - eval_step <= 20 (for convenience of display) 

Start the experiment:

The fine-tuning module of the ms-swift framework uses LoRA fine-tuning by default, so there is no need to explicitly specify the fine-tuning method in this experiment.

At the same time, the framework automatically applies a learning rate decay strategy during training, gradually reducing the effective learning rate. This helps prevent the model from overshooting the optimal solution and improves convergence stability.

```python
%env CUDA_VISIBLE_DEVICES=0
%env LOG_LEVEL=INFO
!swift sft \
--learning_rate '0.1' \
--lora_rank 4 \
--num_train_epochs 1 \
--dataset './resources/2_7/train_100.jsonl' \
--batch_size '8' \
--max_length 512 \
--eval_step 1 \
--model_type 'qwen2_5-1_5b-instruct' \
--model_id_or_path './model'
```

| Training loss image | Evaluation loss image |
| --- | --- |
|<img src="https://img.alicdn.com/imgextra/i2/O1CN0122CqML1xiykiTglmo_!!6000000006478-2-tps-667-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> | <img src="https://img.alicdn.com/imgextra/i4/O1CN01AxXE0V1JqEORoVBdi_!!6000000001079-2-tps-667-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> |

| **Observation metrics (training loss, validation loss):** | Training loss increases, validation loss increases |
| --- | --- |
| **Training status:** | **Training failed** |
| **Cause analysis:** | The learning rate is likely too high. This causes the model's parameters to oscillate wildly instead of converging toward the optimal solution, resulting in training failure.<img src="https://img.alicdn.com/imgextra/i1/O1CN01l4leTB1LKI0BcVs16_!!6000000001280-2-tps-1658-1262.png" style="width: 300px;display: block; margin-left: auto; margin-right: auto"/>|
| **Adjustment logic:** | Significantly reduce the learning rate to $0.00005$, allowing the model to "learn cautiously" with smaller steps. |

#### 3.3.2 Second experiment (takes about 2 minutes)

<div style="width: 30%">
    
| Parameter | Old parameter value | New parameter value |
| --- | --- | --- |
| Learning rate (learning_rate) | 0.1 | 0.00005 |
    
</div>

```python
%env CUDA_VISIBLE_DEVICES=0
%env LOG_LEVEL=INFO
!swift sft \
--learning_rate '0.00005' \
--lora_rank 4 \
--num_train_epochs 1 \
--dataset './resources/2_7/train_100.jsonl' \
--batch_size '8' \
--max_length 512 \
--eval_step 1 \
--model_type 'qwen2_5-1_5b-instruct' \
--model_id_or_path './model'
```

| Training loss image | Evaluation loss image |
| --- | --- |
|<img src="https://img.alicdn.com/imgextra/i3/O1CN01DgtNVX1EDgzHYamOE_!!6000000000318-2-tps-680-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> | <img src="https://img.alicdn.com/imgextra/i3/O1CN01621v4k1ErzqC24Z1b_!!6000000000406-2-tps-689-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> |

| **Observation metrics (Training loss, Validation loss):** | Training loss decreases, validation loss also decreases |
| --- | --- |
| **Training status:** | **Underfitting** |
| **Cause analysis:** | Underfitting is a very common phenomenon during training. It indicates that, with the parameters unchanged, simply allowing the model to train longer can lead to successful training. Of course, modifying the parameters can also accelerate the training process. |
| **Adjustment logic:** | 1. Allow the model to train longer by increasing the number of epochs `num_train_epochs` to 50. <br/> 2. Increase the `batch_size` to 16 to accelerate the training process. |

#### 3.3.3 Third experiment (takes about 10 minutes)

<div style="width: 50%">

| Parameter | Old Parameter Value | New Parameter Value |
| :--- | :--- | :--- |
| Number of Training Epochs (num_train_epochs) | 1 | 50 |
| batch_size | 8 | 16 |
| eval_step | 1 | 20 (Optimized output display) |

</div>

```python
%env CUDA_VISIBLE_DEVICES=0
%env LOG_LEVEL=INFO
!swift sft \
--learning_rate '0.00005' \
--lora_rank 4 \
--num_train_epochs 50 \
--dataset './resources/2_7/train_100.jsonl' \
--batch_size '16' \
--max_length 512 \
--eval_step 20 \
--model_type 'qwen2_5-1_5b-instruct' \
--model_id_or_path './model'
```

| Training loss image | Evaluation loss image |
| --- | --- |
|<img src="https://img.alicdn.com/imgextra/i4/O1CN01xsw3a31YarKvsEKCR_!!6000000003076-2-tps-671-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> | <img src="https://img.alicdn.com/imgextra/i3/O1CN01b2v3fK1jOSNo73Q3y_!!6000000004538-2-tps-680-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> |

| **Observation metrics (Training Loss, Validation Loss):** | Training loss decreases, validation loss first decreases then increases |
| --- | --- |
| **Training status:** | **overfitting** |
| **Cause analysis:** | overfitting is also a very common phenomenon during training. It indicates that the model is "memorizing questions" and not learning the knowledge in the dataset. We can reduce the number of epochs or increase the amount of data to make the model "forget the questions." |
| **Adjustment logic:** | 1. Reduce the num_train_epochs to 3. <br/> 2. Expand the number of problem solutions generated by DeepSeek-R1 to 1000 entries. Dataset location: current directory/resources/2_7/train_1k.jsonl <br/> 3. After increasing the amount of data, increase the rank of LoRA to 8 based on previous learning. |

In general, with the scale of today's LLMs, fine-tuning requires at least **1,000+** high-quality training dataset entries. When below this threshold, the model tends to "memorize questions" after a few rounds of training instead of learning the inherent knowledge within the data.

#### 3.3.4 Fourth experiment (takes about 5 minutes)

| Parameter | Old Value | New Value |
| --- | --- | --- |
| Change Dataset | 100 entries | 1000+ entries |
| Number of Training Epochs (num_train_epochs) | 50 | 3 |
| LoRA Rank (lora_rank) | 4 | 8 (For reasons why this was increased, refer to the LoRA introduction). |

```python
%env CUDA_VISIBLE_DEVICES=0
%env LOG_LEVEL=INFO
!swift sft \
--learning_rate '0.00005' \
--lora_rank 8 \
--num_train_epochs 3 \
--dataset './resources/2_7/train_1k.jsonl' \
--batch_size '16' \
--max_length 512 \
--eval_step 20 \
--model_type 'qwen2_5-1_5b-instruct' \
--model_id_or_path './model'
```

| Training loss image | Evaluation loss image |
| --- | --- |
|<img src="https://img.alicdn.com/imgextra/i3/O1CN01p8rX0d1UAyUOGHeOJ_!!6000000002478-2-tps-671-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> | <img src="https://img.alicdn.com/imgextra/i1/O1CN01LjmbJ21P4Uo8ZJyav_!!6000000001787-2-tps-689-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> |


| **Observation Metrics (Training Loss, Validation Loss):** | Training loss decreases, validation loss also decreases |
| --- | --- |
| **Training Status:** | **Underfitting** |
| **Cause Analysis:** | The model is still underfitting, but the steady decrease in both training and validation loss indicates that the training process is stable and effective. We are on the right track. |
| **Adjustment Logic:** | Allow the model to continue learning by increasing the number of training epochs (num_train_epochs) to 15. |

#### 3.3.5 Fifth experiment (takes about 20 minutes)

| Parameter | Old Parameter Value | New Parameter Value |
| --- | --- | --- |
| num_train_epochs | 3 | 15 |

```python
%env CUDA_VISIBLE_DEVICES=0
%env LOG_LEVEL=INFO
!swift sft \
--learning_rate '0.00005' \
--lora_rank 8 \
--num_train_epochs 15 \
--dataset './resources/2_7/train_1k.jsonl' \
--batch_size '16' \
--max_length 512 \
--eval_step 20 \
--model_type 'qwen2_5-1_5b-instruct' \
--model_id_or_path './model'
```

| Training loss image | Evaluation loss image |
| --- | --- |
|<img src="https://img.alicdn.com/imgextra/i4/O1CN01hyQhbn1p04zyTeQkv_!!6000000005297-2-tps-671-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> | <img src="https://img.alicdn.com/imgextra/i3/O1CN01oy2oZv1r0ejEmpYdQ_!!6000000005569-2-tps-680-451.png" style="width: 500px;display: block; margin-left: auto; margin-right: auto"/> |


| **Observation Metrics (Training Loss, Evaluation Loss):** | Training loss basically does not decrease, evaluation loss also basically does not decrease and even slightly increases |
| --- | --- |
| **Training Status:** | **Training Successful!** |

### 3.4 Examination after fine-tuning

After fine-tuning, two checkpoint files are typically saved:

* best_model_checkpoint: The model parameters corresponding to the best performance on the validation set.
* last_model_checkpoint: The model parameters at the end of the training process.

In the code below, replace ckpt_dir with the path to the best_model_checkpoint to load the optimal version of the fine-tuned model.

First, let's load the model into memory:

```python
from swift.tuners import Swift

# Please modify ckpt_dir to the correct location before running
ckpt_dir = 'output/qwen2_5-1_5b-instruct/v9-xxxxxx/checkpoint-xxxx' # Modify to your checkpoint location before running
# Load the model
ft_model = Swift.from_pretrained(model, ckpt_dir, inference_mode=True)
```

Let's take a look at how the fine-tuned model performs in the exam.

```python
import json
sum, score = 0, 0.0
for line in open("./resources/2_7/test.jsonl"):
    # Read math questions from the test set
    math_question = json.loads(line)
    query = math_question["messages"][1]["content"]
    # Use the fine-tuned model for inference
    response, _ = inference(ft_model, template, query)
    # Get the correct answer
    ans = math_question["messages"][2]["content"]
    pos = ans.find("ans")
    end_pos = ans[pos:].find('}}')
    ans = ans[pos - 2: end_pos + pos + 2]
    # Organize output
    print(("========================================================================================"))
    print(query.split("#Math Problem#\n")[1])
    print("The answer to the question is: " + ans)
    print("-----------Model Response----------------")
    display(Latex(response))
    print("-----------End of Response----------------")
    # Calculate the model's score
    if ans in response:
        score += 1
        print("The model answered correctly")
    elif ans[6 : -2] in response:
        score += 0.5
        print("The model answered correctly but the output format was incorrect")
    else: print("The model answered incorrectly")
    sum += 1
# Summary
display(Markdown("The fine-tuned model scored **" + str(int(100*score/sum)) + "** points on the exam"))
```

### 3.5 Parameter matrix fusion

After the model training is completed, there are two ways to use the fine-tuned model:

1. Dynamically load the fine-tuned LoRA weights at inference time. <br>
      The low-rank parameter matrix obtained from fine-tuning takes up only about 20 MB of storage space, making it highly efficient for incremental deployment and distribution. This is a commonly used approach in engineering practice. <br>
      Note: Whichever base model was used for fine-tuning, you must specify the correct base model when loading. <br>
      In the previous subsection, we already used this method by setting the `ckpt_dir`.
2. Merge the base model with the fine-tuned low-rank parameters into a single complete model, then deploy the merged model.

Here, we introduce the second method: combining the "fine-tuned parameter matrix" (such as LoRA weights) with the "base model parameter matrix" to create a standalone model with updated parameters.

By using the `swift export` command and providing the path to the fine-tuned model (preferably the `best_model_checkpoint`), you can generate the merged model. This exported model can be used independently without requiring special PEFT libraries.

```python
%env LOG_LEVEL=INFO
!swift export \
--ckpt_dir 'output/qwen2_5-1_5b-instruct/vx-xxx/checkpoint-xxx<Modify to checkpoint location before running>' \
--merge_lora true
```

The log displays the path of the model after fusion. By default, the complete parameter matrix after merging is saved in the `checkpoint` directory.

(For the PAI experimental environment, the full model parameters are located at: `output/qwen2_5-1_5b-instruct/vX-XXX/checkpoint-XX-merged`).

## ✅ Summary

In this lesson, we have learned the following:

* Understanding the core value of model fine-tuning: By injecting task-specific data (such as math problem solutions), fine-tuning directly enhances the model’s reasoning ability in targeted domains, overcoming the limitations of prompt engineering and RAG-based chatbots.
* Mastering key training parameters:
    * Learning rate controls the step size of parameter updates.
    * Epoch determines how many times the model iterates over the entire dataset.
    * Batch size affects gradient stability and memory usage.
* The loss function provides feedback on training progress by measuring prediction error.
* Understanding the principle of LoRA efficient fine-tuning: LoRA reduces memory and computational costs through low-rank matrix decomposition—updating only small auxiliary matrices instead of all model parameters. In practice, adjusting the lora_rank parameter allows trade-offs between model capacity and training efficiency.
* Completing iterative hyperparameter tuning experiments: Through multiple rounds of adjustment—such as modifying learning rate, data volume, and number of training epochs—we addressed underfitting and overfitting, ultimately achieving a significant improvement in the model’s problem-solving accuracy.

Although this tutorial allows you to use prepared datasets and experience fine-tuning with free GPU resources, in real-world production scenarios, fine-tuning is not straightforward. It requires careful consideration of factors such as computational costs, data scale, and data quality. In particular, pay attention to the following:

1. Assess whether simpler, lower-cost methods—like prompt engineering or RAG chatbots—are sufficient for the task before proceeding to fine-tuning.
2. Ensure that the amount and quality of labeled data meet the minimum threshold—typically at least 1,000 high-quality, task-relevant samples—to achieve meaningful improvements.
3. Verify that the project budget aligns with required expertise and infrastructure, ensuring acceptable cost-effectiveness.

### Further learning
#### Fine-tuning for more machine learning tasks

* Image Classification
    * *Examples*: object recognition, medical image diagnosis
    * *Purpose*: Adapt pre-trained models (examples: ResNet, ViT) to extract features specific to a new image dataset.
    * *Key points*: Leverage general visual knowledge from pre-training; reduce data requirements through transfer learning.
* Object Detection
    * *Examples*: autonomous driving, security monitoring
    * Purpose: Fine-tune models like YOLO or Faster R-CNN to detect specific objects or scenes.
    * *Key points*: Improve sensitivity to target categories and locations, reducing false alarms and missed detections.
* Machine Translation 
    * *Examples*: domain-specific translation, customer support localization
    * *Purpose*: Adapt general-purpose translation models (such as mBART or T5) to professional terminology and stylistic conventions.
    * *Key points*: Correct semantic biases that arise when general models are applied to specialized domains.
* Recommendation Systems
    * *Examples*: e-commerce, content platforms
    * *Purpose*: Optimize recommendation models (such as collaborative filtering or deep ranking models) using user behavior data.
    * *Key points*: Balance personalization with cold-start challenges to improve click-through and conversion rates.

#### More efficient fine-tuning methods

* **Freeze**: One of the earliest PEFT methods. Most of the model’s parameters are frozen during training, and only a small portion—such as the final layers—are updated.
    Characteristics:
        * High parameter efficiency (only a small number of parameters are trained).
        * Effective when the downstream task is similar to the pre-training objective (such as text classification).
        * May underperform on complex or highly divergent tasks due to limited adaptability.
<div style="text-align: left;">
<img src="https://img.alicdn.com/imgextra/i1/O1CN01X9GOk81sgAEtxflGR_!!6000000005795-2-tps-1340-686.png" style="width: 600px;display: block; margin-left: 60px; margin-right: auto"/>
</div>

* **Adapter Tuning**: Small neural network modules called adapter layers are inserted at specific positions within the original model architecture (such as between transformer layers). During fine-tuning, the original model parameters are frozen—only the Adapter layers are trained. 
    Characteristics:
        * Modular design with strong compatibility across tasks.
        * Slightly higher number of trainable parameters compared to LoRA, but delivers stable performance.
        * Requires structural modifications to the model, and introduces additional computational overhead during inference due to the extra layers.
<div style="text-align: left;">
<img src="https://img.alicdn.com/imgextra/i2/O1CN016gccCd1CdDpjDxbe9_!!6000000000103-2-tps-1482-1048.png" style="width: 500px;display: block; margin-left: 60px; margin-right: auto"/>
</div>

* Prompt Tuning: Indirectly controls model behavior by introducing learnable input vectors (called prompts) during training. The original model parameters are frozen, and only these prompt embeddings are updated. 
    Characteristics:
        * No need to modify the model architecture—only the input representation is adjusted.
        * Well-suited for generative tasks such as translation, dialog generation, and summarization.
        * Performance depends heavily on prompt design; may underperform on complex or highly structured tasks.

#### Fine-tuning dataset construction strategy

In general, for more complex scenarios, effective fine-tuning requires at least **1,000+ high-quality training dataset samples**. When building your dataset, confirm the following key points:

* **Data Quality**: Ensure the dataset is accurate, relevant, and free of ambiguity or errors. Remove noisy or incorrect entries that could mislead training.
* **Diversity Coverage**: Include a wide range of scenarios, contexts, and domain-specific terminology to prevent the model from overfitting to a narrow data distribution.
* **Class Balance**: For classification tasks with multiple categories, ensure balanced representation across classes to avoid bias toward dominant ones.
* **Continuous Iteration**: Fine-tuning is an iterative process. Continuously optimize and expand the dataset based on the model's performance on the validation set.

If you lack sufficient labeled data, consider enhancing the model’s knowledge using retrieval-augmented approaches, such as querying a knowledge base (business documents, FAQs).

> In many real-world business scenarios, combining model fine-tuning with knowledge base retrieval yields better results than either method alone.

You can also use the following strategies to expand the dataset:

* **Manual Annotation**: Domain experts label or enrich data for critical or representative scenarios.
* **Model Generation**: Use LLMs to generate synthetic data that mimics real-world usage.
* **External Collection**: Gather data from public datasets, web scraping, user interactions, or customer feedback.

#### Common evaluation metrics for models

Evaluation metrics differ significantly depending on the task type. Below are some widely used metrics for common AI tasks:

* **Classification tasks**:
    * Accuracy: Proportion of correct predictions out of total predictions.
    * Precision, Recall, and F1 Score: Especially useful in binary or multi-class classification to evaluate how well the model identifies positive instances.

* **Text generation tasks**:
    * BLEU (Bilingual Evaluation Understudy): Commonly used in natural language processing tasks such as machine translation; computes scores based on n-gram overlaps between generated text and reference translation.
    * ROUGE (Recall-Oriented Understudy for Gisting Evaluation): Often used for summarization; measures recall of n-grams, precision, and F-measure.
    * Perplexity: Evaluates how well a probability model predicts a sample. Lower perplexity indicates better performance.

* **Image recognition/Object detection**:
    * Intersection over union (IoU): Measures the overlap between predicted and ground-truth bounding boxes. A higher IoU indicates better localization accuracy.
    * mAP (mean average precision): A standard metric in object detection that averages precision across different classes and confidence thresholds.

## 🔥 Quiz
### 🔍 Multiple-Choice Question

<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Which of the following statements about LoRA is incorrect❓(Select 1.)</b>

- A. LoRA can effectively reduce the cost of fine-tuning LLMs.
- B. LoRA modifies the original weights of the fine-tuned model.
- C. LoRA's implementation is relatively simple and easy to integrate.
- D. The results of LoRA fine-tuning can be easily reverted.

**[Click to View Answer]**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference Answer: B**  
📝 **Explanation**:  
- LoRA does not directly modify the original weights but indirectly affects model behavior by adding low-rank matrices. This makes rollback operations simple, as you only need to remove the added low-rank matrices.

</div>
</details>

---



<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>You are using Swift to fine-tune a Qwen model and notice a significant upward trend in loss on the validation set. Which of the following actions can help alleviate or resolve this issue❓(Select all that apply.)</b>

- A. Increase learning rate
- B. Decrease learning rate
- C. Increase --num_train_epochs
- D. Decrease --num_train_epochs

**[Click to View Answer]**
</summary>

<div style="margin-top: 10px; padding: 15px;  border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference Answer: BD**  
📝 **Explanation**:  
- learning_rate: A high learning rate can lead to fast model training but may cause oscillations near the optimal solution, or even non-convergence, resulting in fluctuating loss, which may appear like overfitting. However, this is different from true overfitting.  
- num_train_epochs: Overfitting may also be caused by too many training epochs. Reducing the number of training epochs can prevent the model from over-learning the training data.

</div>
</details>
