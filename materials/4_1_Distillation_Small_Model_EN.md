# 4.1 Using Distillation to Give a Small Model Specialized Skills

## 🚄 Introduction

In earlier lessons, you built a Q&A bot that can answer questions: RAG lets it consult company policy, and an Agent lets it call tools to handle complex requests. The system can already "get things done" — but once it's deployed to production, you run into a new bottleneck.

Employees don't ask questions in a tidy, well-behaved way. A single message might pack in two requests, use vague wording, or leave out how urgent it is — the system first has to "understand" every question before it can decide who should handle it:

| Employee question | Information the system needs to understand |
| --- | --- |
| "I'm traveling to Hangzhou next Wednesday, and could you also chase up last month's expense reimbursement?" | Two intents (travel request + reimbursement follow-up), destination, date, routed to multi-intent splitting |
| "My VPN won't connect, this is urgent!!" | IT support, high urgency, routed to a direct answer |
| "What system access does a new intern need to be granted?" | Onboarding + access request, routed to RAG policy lookup |

This "request understanding" step is currently handled by the large language model, and it works well. But the problem is: **every request has to go through the LLM just to be "understood," before it's even "answered" — and by that point, half the cost has already been spent.**

Is there a way to have a small model do this instead? A small model has low inference cost and is fast, but if you just plug one in directly, its JSON output tends to break, and multi-intent recognition isn't accurate.

Distillation is here to solve exactly this problem: **"copying" the large model's judgment ability onto a small model.**

## 🍁 Learning Objectives

By the end of this lesson, you will be able to:

- Understand the core idea behind distillation, and distinguish it from fine-tuning at a fundamental level.
- Master the complete data-synthesis distillation pipeline: teacher labeling → quality filtering → student training.
- Perform LoRA fine-tuning with ms-swift on PAI-DSW.
- Verify the effect of distillation using quantitative metrics (JSON compliance rate, intent F1, routing accuracy).
- Analyze the cost-benefit tradeoffs of distillation and make a sound deployment decision.

## 0. Environment Setup

This lesson needs to run in a **GPU environment** (local inference for the base model + LoRA training). Follow the steps below to create a PAI-DSW GPU instance.

> If you already created a CPU-based DSW instance in lesson 1.0, you'll need to **create a separate new GPU instance**.

### 0.1 Creating a GPU DSW Instance

1. Go to the [PAI console](https://pai.console.aliyun.com/?regionId=cn-hangzhou#/workspace/overview) → Interactive Modeling (DSW) → **Create Instance**
2. **Resource spec**: choose a GPU instance — `ecs.gn7i-c8g1.2xlarge` (A10, 30GB VRAM) is recommended
3. **Image**: choose `modelscope:1.38.0.1-pytorch2.10.0-gpu-py312-cu128-ubuntu22.04`

> 💡 A GPU instance uses up your free quota faster (about 7 compute-hours per hour), so it's best to turn it on only when you need to run code, and **stop the instance** promptly when you're not using it to avoid charges. See lesson 1.0 for the detailed step-by-step instance-creation guide.

### 0.2 Installing Environment Dependencies

Once the instance has started, open a **Terminal** at the top of DSW and run these commands in order:

```bash
cd /mnt/workspace
wget https://developer-labfileapp.oss-cn-hangzhou.aliyuncs.com/ACP/aliyun_llm_acp_install.sh
/bin/bash aliyun_llm_acp_install.sh
```

The script will automatically create the `llm_learn` virtual environment, clone the course code, and install the base dependencies.

### 0.3 Installing Qwen Code (Optional)

You installed Qwen Code on the CPU instance back in lesson 3.2, but this GPU instance is a separate environment, so you'll need to install it again. Run this in the DSW terminal:

```bash
bash -c "$(curl -fsSL https://qwen-code-assets.oss-cn-hangzhou.aliyuncs.com/installation/install-qwen.sh)" -s --source qwenchat < /dev/null
```

Once installed, run `qwen` in the terminal to start Qwen Code (the first time you use it, you'll need to authenticate with an API key — see lesson 3.7). Several parts of this lesson provide an optional Qwen Code walkthrough — once it's installed, you're ready to use it.

### 0.4 Opening the Notebook and Switching Kernels

In your IDE or DSW, click the kernel name in the top right → select `Python (llm_learn)`

### 0.5 Loading the API Key and Installing Training Dependencies

The two cells below load the DashScope API key (used to call the teacher model) and install the extra dependencies needed for training in this chapter.

```python
import os, json, re, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath('')), 'course_core'))
sys.path.insert(0, os.getcwd())

from config.load_key import load_key
load_key()

from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

print(f'API key loaded: {os.environ["DASHSCOPE_API_KEY"][:5]+"*"*5}')
```

```python
# Install GPU-training-specific dependencies (do NOT run this cell on a CPU instance)
#
# Version notes: requirements-gpu.txt pins the training/deployment dependency combination
# that has been verified for this course in the DSW GPU image.
#   Image: modelscope:1.38.0.1-pytorch2.10.0-gpu-py312-cu128-ubuntu22.04
#   File: requirements-gpu.txt at the course root
#   Dependencies: torch==2.10.0, ms-swift==4.2.3, transformers==5.8.1, vllm==0.19.1
from pathlib import Path
REQ_GPU = next(p for p in [Path('requirements-gpu.txt'), Path('../requirements-gpu.txt'), Path('../../requirements-gpu.txt'), Path('/mnt/workspace/aliyun_acp_learning/requirements-gpu.txt')] if p.exists())
!pip install -i https://mirrors.aliyun.com/pypi/simple/ -r {REQ_GPU}
```

### 0.5 Downloading the Base Model

Download Qwen3-0.6B from ModelScope to local storage. This model will be used for evaluating the base model in Section 4, and for LoRA training in Section 6.

```python
# Download the Qwen3-0.6B model (about 1.2GB, takes 1-2 minutes to download)
!modelscope download --model Qwen/Qwen3-0.6B --local_dir /mnt/workspace/model/Qwen3-0.6B
```

## 1. Task Design: Request Understanding

### 1.1 Why We Need "Request Understanding"

In earlier lessons, you already built a RAG system (lesson 2.2) and an Agent tool chain (lesson 2.6). But in production, once the system receives an employee question, the first step isn't to answer it directly — it's to decide: **who should handle this question?** A simple factual question ("what's the office WiFi password") can be answered directly; a question that requires looking up policy ("can annual leave carry over into the next year") needs to go to RAG; a message containing multiple independent requests ("request leave + chase up reimbursement") needs to be split and handled separately; and something like "I want to file a complaint about my manager," which needs a human judgment call, should be escalated to a person.

This decision process is "request understanding": turning a sentence of natural language into structured ticket information.

### 1.2 Defining a Structured Ticket

We define the ticket JSON with five fields:

```json
{
  "intents": ["travel_request", "reimbursement_followup"],
  "department": "administration",
  "urgency": "medium",
  "entities": {"travel_date": "next Wednesday", "destination": "Hangzhou"},
  "route": "multi_intent_split"
}
```

| Field | Type | Possible values | Description |
| --- | --- | --- | --- |
| intents | array of strings | onboarding, attendance/leave, travel request, reimbursement follow-up, annual-leave inquiry, IT support, access request, policy inquiry | Multiple selections allowed |
| department | string | HR, Administration, IT, Finance | The primary responsible department |
| urgency | string | high, medium, low | Judged from time-sensitivity and wording |
| entities | object | free-form key-value pairs | Key parameters extracted from the question (dates, amounts, names, etc.) |
| route | string | direct_answer, rag_query, multi_intent_split, escalate | The routing decision |

### 1.3 Why This Task Is a Good Fit for Distillation

"Request understanding" has three traits that make it well-suited to a small model: the output format is fixed (the JSON schema is well-defined; there's no need for open-ended generation), it doesn't depend on external knowledge (judging intent and urgency only requires looking at the input text itself), and it runs on every single request (a high-frequency call path, so cost matters).

The large model is already good at this. The goal of distillation is: transfer the large model's judgment ability on this task to a small model with lower inference cost.

## 2. How Distillation Works

### 2.1 The Core Idea of Distillation

Fine-tuning is "teaching a model to do this task," with training data usually produced by human annotators. Distillation is "copying the way a stronger model makes judgments onto your model," with training data generated by a teacher model. The training procedure for both is nearly identical (both are SFT) — the difference is **where the training data comes from**:

| | Fine-tuning | Distillation |
| --- | --- | --- |
| Data source | Human annotation | Generated by a teacher model |
| Data cost | High (needs domain experts) | Low (API call cost) |
| Data scale | Usually limited | Can be generated at scale |
| Quality ceiling | Depends on annotator skill | Depends on the teacher model's ability |

The core logic of distillation is simple: **the large model already "knows how" to do this — we just need to treat its output as training data and teach it to the small model.** In essence, distillation adds a high-quality data-construction step before fine-tuning. You don't need to fine-tune the teacher model to perfection before distilling — you can just use the strongest API model currently available (e.g., qwen3.6-plus) to generate the data directly. What matters is data quality, not a complicated pipeline.

Distillation is already widely used in production to cut costs. Alibaba's [DistilQwen2.5 series](https://arxiv.org/abs/2504.15027) (0.5B-7B) uses multiple large models collaborating as teachers, and the resulting lightweight distilled models significantly outperform the original base models of the same parameter count on instruction-following ability. [DeepSeek-R1](https://arxiv.org/abs/2501.12948) distilled 800,000 reasoning traces from a 671B-parameter model down to a 7B student model, which then surpassed LLaMA-2 70B on math reasoning.

### 2.2 Three Distillation Paths

Depending on what exactly gets "copied," distillation splits into three approaches:

**Path 1: Data-synthesis distillation / black-box distillation (this chapter's hands-on work)**

Use the teacher model's API to generate labeled data, then train the student model on it. This only requires API access, not the teacher model's weights, which is why it's called "black-box" — you can only see the teacher's output, not its internal computation. This is the most practical form of distillation, well suited to cases where the teacher model is a commercial API.

**Path 2: Knowledge distillation (KD) / white-box distillation (conceptual overview)**

The student learns not just the teacher's final output but also the probability distribution the teacher assigns to each output token (soft labels). For example, when judging the department, the teacher might internally produce a distribution like "HR 70%, Administration 25%, IT 5%," and output the highest-probability choice, "HR" — but that distribution itself carries implicit knowledge (dark knowledge) like "HR and Administration are somewhat similar," which is more informative than just looking at the final answer. White-box distillation has the student fit the teacher's probability distribution, not just the final answer. It's called "white-box" because it requires access to the teacher model's weights and internal state. Commercial APIs don't expose weights, so this approach isn't usable with them — but if the teacher model is open-source, white-box distillation typically achieves higher accuracy.

**Path 3: Reasoning compression (conceptual overview)**

The student learns the teacher's chain-of-thought trace, not just the final answer. DeepSeek-R1 used exactly this approach, distilling 800K reasoning traces into a 7B student model, which then surpassed a 70B base model on reasoning tasks. Suited to tasks requiring multi-step reasoning.

| Path | Alias | Requires | Best suited for |
| --- | --- | --- | --- |
| Data-synthesis distillation | Black-box distillation | Only teacher API access | Structured tasks, teacher is a commercial API |
| Knowledge distillation (KD) | White-box distillation | Requires teacher weights | Open-source teacher, need higher accuracy |
| Reasoning compression | — | Requires the teacher's reasoning output | Multi-step reasoning tasks |

### 2.3 Why This Chapter Chooses Data Synthesis

Back to our "request understanding" task: the teacher model (qwen3.6-plus) is an API service with no access to its weights, so white-box KD is a non-starter; the task is single-step judgment (going straight from input to structured output) with no need for multi-step reasoning, so a CoT trace isn't necessary; and since the output is structured, quality can be automatically checked with a JSON schema, giving us confidence in data quality. Data-synthesis distillation (black-box distillation) is therefore the most suitable choice.

## 3. Data Synthesis

The first step of distillation is generating training data with the teacher model. The process has three steps:

1. Generate a diverse set of employee questions
2. Have the teacher model label a structured ticket for each one
3. Filter for quality + format as training data

> 💡 **Tip**: The training data is already pre-generated in the `resources/4_1/` directory, so you can use it directly. The code below shows how the data was generated, to help you understand the full data-synthesis pipeline. If you want to try generating it yourself, running this code will incur a small API cost.

### 🤖 Synthesizing Training Data with Qwen Code (Optional)

If you installed Qwen Code in Section 0, you can now have it walk through the whole data-synthesis process for you — generating questions, teacher labeling, quality filtering, and formatting and saving — all in one go. If you'd rather not use Qwen Code, you can skip this step and use the pre-generated data in `resources/4_1/train.jsonl` directly, reading the code below to understand the process.

Copy the following prompt into Qwen Code and run it:

````markdown
I'm working on synthesizing training data for model distillation. Please help me complete the following tasks, showing me the results after each step.

## Environment
- Working directory: cd /mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线
- Virtual environment: source /mnt/workspace/llm_learn/bin/activate
- The API key is set in the DASHSCOPE_API_KEY environment variable (loaded via config/load_key.py)
- Teacher model: qwen3.6-plus (called via DashScope's OpenAI-compatible interface)
- API address: https://dashscope.aliyuncs.com/compatible-mode/v1

## Task background
We need to generate distillation training data for an "employee request understanding" task. The task is to turn an employee's natural-language question into a structured JSON ticket with 5 fields: intents, department, urgency, entities, and route.

## Step 1: Load the API key
Run the following Python code to load the API key and initialize the client:

```python
import os, json, re, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath('')), 'course_core'))
sys.path.insert(0, os.getcwd())

from config.load_key import load_key
load_key()
from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
print(f"API key loaded: {os.environ['DASHSCOPE_API_KEY'][:5]}*****")
```

## Step 2: Generate 30 employee questions using the LLM
Call qwen3.6-plus to generate a diverse set of employee questions. Requirements:
- Cover 8 intent types: onboarding, attendance/leave, travel request, reimbursement follow-up, annual-leave inquiry, IT support, access request, policy inquiry
- Mix formal, colloquial, and vague expression styles
- About 30% should be multi-intent questions (one sentence containing two requests)
- Some questions should include specific dates, amounts, names, and locations

Once generated, show me the first 10.

## Step 3: Label with the teacher model
For each question, call qwen3.6-plus to produce a label, using the following system prompt:

"""
You are a request-understanding assistant. Analyze the user's question and extract a structured ticket.

Output strictly in the following JSON format, and nothing else:

{
  "intents": ["intent"],
  "department": "department",
  "urgency": "urgency",
  "entities": {},
  "route": "route"
}

Allowed field values:
- intents (multiple allowed): onboarding, attendance/leave, travel request, reimbursement follow-up, annual-leave inquiry, IT support, access request, policy inquiry
- department: HR, Administration, IT, Finance
- urgency: high, medium, low
- entities: key parameters extracted from the question (dates, amounts, names, locations, system names, etc.); an empty object {} if none
- route: direct_answer (a simple factual question), rag_query (needs to consult policy documents), multi_intent_split (contains multiple independent intents), escalate (needs a human to step in)
"""

Set temperature=0.1 for the calls. Once labeling is done, show me 3 of the labeled results.

## Step 4: Quality filtering
Run three checks on each label:
1. Can the JSON be parsed successfully?
2. Are all 5 required fields present (intents, department, urgency, entities, route)?
3. Is each field's value within the allowed range defined in the system prompt above?

Filter out samples that fail, and tell me how many were generated in total, how many were filtered out, and how many were kept.

## Step 5: Format and save
Convert the passing samples into ms-swift's messages training format:

```json
{"messages": [{"role": "system", "content": "system prompt content"}, {"role": "user", "content": "employee question"}, {"role": "assistant", "content": "JSON label result"}]}
```

One per line, saved to resources/4_1/my_train.jsonl. Once saved, tell me the file path and the number of samples.
````

> 💡 The data Qwen Code generates is saved to `resources/4_1/my_train.jsonl`. If you want to use your own generated data during later training, just replace `train.jsonl` with `my_train.jsonl` in the training command. The pre-generated `train.jsonl` (about 1,400 samples) that comes with the course has more comprehensive coverage, so it's recommended to still use the pre-generated data for actual training.

Whether or not you used Qwen Code, let's now walk through each step of data synthesis in detail, to understand the design thinking behind it.

### 3.1 The Teacher Model's System Prompt

The teacher model (qwen3.6-plus) needs a precise system prompt to constrain its output format. This prompt defines the JSON schema and the allowed values for each field:

```python
SYSTEM_PROMPT = """You are a request-understanding assistant. Analyze the user's question and extract a structured ticket.

Output strictly in the following JSON format, and nothing else:

{
  "intents": ["intent"],
  "department": "department",
  "urgency": "urgency",
  "entities": {},
  "route": "route"
}

Allowed field values:
- intents (multiple allowed): onboarding, attendance/leave, travel request, reimbursement follow-up, annual-leave inquiry, IT support, access request, policy inquiry
- department: HR, Administration, IT, Finance
- urgency: high, medium, low
- entities: key parameters extracted from the question (dates, amounts, names, locations, system names, etc.); an empty object {} if none
- route: direct_answer (a simple factual question), rag_query (needs to consult policy documents), multi_intent_split (contains multiple independent intents), escalate (needs a human to step in)"""

print("System prompt defined")
print(f"Prompt length: {len(SYSTEM_PROMPT)} characters")
```

### 3.2 Generating Diverse Employee Questions

Data diversity is key to distillation quality. We designed prompt templates along several dimensions to generate questions: covering scenario combinations of 8 intent types × 4 departments, mixing formal requests, colloquial phrasing, vague/elliptical wording and other styles, with about 30% multi-intent questions (a single sentence containing two requests), and some questions including specific entities like dates, amounts, names, and locations.

```python
# Below is an example of one of the generation templates
query_prompt_example = """Please generate 15 different questions that employees might ask an internal company Q&A bot. Requirements:
1. Cover these scenarios: onboarding, attendance/leave, travel request, reimbursement follow-up
2. Vary the expression style: formal, colloquial, vague, brief, detailed
3. About 30% should be multi-intent questions (one sentence containing two requests)
4. Some questions should include specific dates, amounts, names, and locations
Put each question on its own line, with no numbering and no other commentary.
Note: any systems, tools, or platforms mentioned in the scenarios should only use fictional names or Alibaba-affiliated products (e.g. DingTalk, Alibaba Cloud); do not mention any real company or product name outside the Alibaba group."""

# In practice, 5 different templates with different emphases were used, covering all intent types and expression styles
# The full data-generation script is at resources/4_1/generate_data.py

print("Example generation template:")
print(query_prompt_example)
```

### 3.3 Teacher Labeling

For each generated question, use the teacher model (qwen3.6-plus) to produce a structured label. The system prompt strictly constrains the output format during labeling, `temperature=0.1` reduces randomness to keep labeling consistent, and every label must pass JSON schema validation before it's allowed into the training set.

```python
# Auto re-initialize if the kernel was restarted but Section 0 wasn't re-run
import os, json, re, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath('')), 'course_core'))
sys.path.insert(0, os.getcwd())

if 'client' not in globals():
    from config.load_key import load_key
    load_key()
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    print("⚠️ client not found, auto re-initialized. It's recommended to run cells in order starting from Section 0.")

def teacher_label(query, system_prompt=SYSTEM_PROMPT):
    """Have the teacher model label one query"""
    response = client.chat.completions.create(
        model="qwen3.6-plus",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

# Try labeling one example
test_query = "I'm traveling to Hangzhou next Wednesday, and could you also chase up last month's expense reimbursement?"
result = teacher_label(test_query)
print(f"Input: {test_query}")
print(f"Teacher label:")
print(json.dumps(json.loads(result), ensure_ascii=False, indent=2))
```

### 3.4 Quality Filtering

The teacher model isn't 100% perfect. Even a strong model like qwen3.6-plus will make mistakes when labeling hundreds of samples in bulk: JSON cut off midway, a field left out, a department set to a value that doesn't exist. If these "bad samples" end up in the training set, the student model will learn the mistakes along with everything else. So we need to run an automated quality check on the teacher's output and filter out anything that doesn't pass.

Here are the three most common types of problems seen in real production:

<div style="text-align: center;">
    *Figure (translated): quality filtering catches three common problems and discards bad records.*

```text
Standard format: {"intents": [...], "department": "...", "urgency": "...", "entities": {...}, "route": "rag_query"}

Error 1: incomplete JSON     -> missing closing brace, json.loads() raises  -> discard
Error 2: required field missing -> entities / route omitted, JSON valid but schema mismatch -> discard
Error 3: value out of range  -> e.g. intents = ["unknown intent"]           -> discard
```
</div>

The filtering uses "outcome validation" (checking whether the output matches the schema) rather than "process validation" (checking whether the reasoning process makes sense) — for a structured-extraction task, this approach is simple and effective. Below, we implement the same filtering logic two ways: with Qwen Code and with Python code.

#### 🤖 Doing Quality Filtering with Qwen Code (Optional)

The logic behind quality filtering isn't complicated, but hand-writing validation code still means handling each field one by one. Here's another approach: describe the filtering rules clearly in natural language, and let Qwen Code generate and run the filtering code for you.

`resources/4_1/labeled_raw.jsonl` is a pre-built sample dataset (35 rows) with 5 problematic samples deliberately mixed in (truncated JSON, missing fields, out-of-range values, etc.) so you can observe the filtering in action. Copy the following prompt into Qwen Code and run it:

````markdown
I have a batch of teacher-labeled data that needs quality filtering. Please help me complete the following:

## Environment
- Working directory: /mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线
- Data file: resources/4_1/labeled_raw.jsonl (each line is a JSON object with query and label fields)

## Filtering rules
Run three checks on each sample's label field:

1. **JSON format check**: label must be valid JSON. If it contains markdown code-block markers (```), extract the JSON content inside first

2. **Required-field check**: must contain all 5 of the following fields, none can be missing
   - intents (array)
   - department (string)
   - urgency (string)
   - entities (object)
   - route (string)

3. **Value-range check**:
   - intents must be one or more of: onboarding, attendance/leave, travel request, reimbursement follow-up, annual-leave inquiry, IT support, access request, policy inquiry
   - department must be one of: HR, Administration, IT, Finance
   - urgency must be one of: high, medium, low
   - route must be one of: direct_answer, rag_query, multi_intent_split, escalate
   - entities must be an object

## Task requirements
1. Read the labeled_raw.jsonl file
2. Apply the above filtering rules to every sample
3. Count and report: total samples, number passing, number filtered out, and the breakdown of filter reasons
4. Save the passing samples to resources/4_1/train_filtered.jsonl
5. Show me 3 passing samples and 3 filtered-out samples (with the reason for each)

Please implement and run this in Python.
````

After trying out Qwen Code's filtering results, keep reading the code below to understand the concrete implementation of the filtering logic.

**Comparing AI-assisted programming with traditional programming:**

| Dimension | Qwen Code (natural-language driven) | Python code (hand-written logic) |
|------|--------------------------|------------------------|
| Learning curve | Low — describe rules in natural language | Medium — need to write Python code |
| Flexibility | High — rule descriptions can be adjusted anytime | Medium — requires editing the code logic |
| Maintainability | Good for quick prototyping and experiments | Good for long-term maintenance in production |
| Execution efficiency | Depends on the AI's code-generation ability | Runs directly, with predictable efficiency |
| Best suited for | Rules that change often, quick validation | Stable rules that need version control |

> 💡 In practice, you can use Qwen Code first to quickly validate whether a set of filtering rules works, and once you've confirmed the rule design is sound, lock it in as Python code for long-term use in production. The two approaches complement each other rather than being an either/or choice.

#### Implementing the Filtering Code

Below, the same three filtering rules are implemented in Python. Understanding the logic in this code will also help you write more precise filtering-rule descriptions when using Qwen Code:

```python
VALID_INTENTS = {"onboarding", "attendance/leave", "travel request", "reimbursement follow-up", "annual-leave inquiry", "IT support", "access request", "policy inquiry"}
VALID_DEPARTMENTS = {"HR", "Administration", "IT", "Finance"}
VALID_URGENCY = {"high", "medium", "low"}
VALID_ROUTES = {"direct_answer", "rag_query", "multi_intent_split", "escalate"}

def validate_label(label_str):
    """Validate whether a teacher label is well-formed"""
    try:
        # Handle a possible markdown code-block wrapper
        if '```' in label_str:
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', label_str, re.DOTALL)
            if match:
                label_str = match.group(1)
        label = json.loads(label_str.strip())
    except json.JSONDecodeError:
        return None  # JSON parsing failed

    # Check required fields
    required = ["intents", "department", "urgency", "entities", "route"]
    if not all(k in label for k in required):
        return None
    # Check value ranges
    if not isinstance(label["intents"], list) or len(label["intents"]) == 0:
        return None
    if not all(i in VALID_INTENTS for i in label["intents"]):
        return None
    if label["department"] not in VALID_DEPARTMENTS:
        return None
    if label["urgency"] not in VALID_URGENCY:
        return None
    if label["route"] not in VALID_ROUTES:
        return None
    if not isinstance(label["entities"], dict):
        return None
    return label

# Validate the checking function with one test sample
test_label = '{"intents": ["travel request", "reimbursement follow-up"], "department": "Administration", "urgency": "medium", "entities": {"destination": "Hangzhou"}, "route": "multi_intent_split"}'
print("Validating a passing sample:", "Passed ✓" if validate_label(test_label) else "Failed ✗")

bad_label = '{"intents": ["a nonexistent intent"], "department": "HR", "urgency": "high", "entities": {}, "route": "direct_answer"}'
print("Validating a failing sample:", "Passed ✓" if validate_label(bad_label) else "Filtered ✓ (intent not in the allowed range)")
```

### 3.5 Looking at the Pre-Generated Data

The training data has already been pre-generated. Let's take a look at its content and distribution:

```python
# Load the pre-generated training data
train_data = []
with open("resources/4_1/train.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        train_data.append(json.loads(line))

# Load the pre-generated test data
test_data = []
with open("resources/4_1/test_30.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        test_data.append(json.loads(line))

print(f"Training set: {len(train_data)} samples")
print(f"Test set: {len(test_data)} samples")

# Show a few training samples
print("\n--- Training sample examples ---")
for i, sample in enumerate(train_data[:3]):
    query = sample["messages"][1]["content"]
    label = json.loads(sample["messages"][2]["content"])
    print(f"\n[Sample {i+1}]")
    print(f"  Question: {query}")
    print(f"  Intents: {label['intents']}")
    print(f"  Department: {label['department']}  Urgency: {label['urgency']}  Route: {label['route']}")
    if label['entities']:
        print(f"  Entities: {label['entities']}")
```

```python
# Data distribution statistics
all_intents = {}
all_routes = {}
all_depts = {}
multi_intent = 0

for sample in train_data:
    label = json.loads(sample["messages"][2]["content"])
    for intent in label["intents"]:
        all_intents[intent] = all_intents.get(intent, 0) + 1
    all_routes[label["route"]] = all_routes.get(label["route"], 0) + 1
    all_depts[label["department"]] = all_depts.get(label["department"], 0) + 1
    if len(label["intents"]) > 1:
        multi_intent += 1

print("--- Intent distribution ---")
for k, v in sorted(all_intents.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print(f"\n--- Route distribution ---")
for k, v in sorted(all_routes.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print(f"\n--- Department distribution ---")
for k, v in sorted(all_depts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print(f"\nMulti-intent samples: {multi_intent}/{len(train_data)} ({multi_intent/len(train_data)*100:.0f}%)")
```

### 3.6 Training Data Format

The training data uses the messages format required by the ms-swift framework, with each sample containing a conversation across three roles:

```json
{
  "messages": [
    {"role": "system", "content": "You are a request-understanding assistant..."},
    {"role": "user", "content": "I'm traveling to Hangzhou next Wednesday..."},
    {"role": "assistant", "content": "{\"intents\": [\"travel request\"], ...}"}
  ]
}
```

During training, the system and user parts serve as input, and the assistant part is the expected output. What the model learns is: given a system prompt and a user question, generate the correct structured JSON.

## 4. Evaluation Method

Before training, let's first define the evaluation metrics, then get a sense of how the base model and the teacher model each perform.

### 4.1 Evaluation Metrics

A structured-extraction task isn't well suited to text-similarity metrics like BLEU or RAGAS, because the output is a strictly defined JSON. We measure model performance from several different angles:

- **JSON compliance rate**: whether the output can be parsed as valid JSON and contains all the required fields. This is the most basic bar — if the format itself is wrong, nothing else matters.
- **Intents F1**: the F1 score for intent recognition, combining precision and recall. Why F1 instead of plain accuracy? Because intents are multi-label (a single sentence may contain two intents), so plain accuracy can't distinguish between "missed one intent" and "got everything wrong." F1 captures both whether the model "found everything" (recall) and "didn't get anything wrong" (precision). It's computed by taking the precision and recall between the predicted intent set and the true intent set for each sample, taking their harmonic mean to get that sample's F1, and then averaging across all samples.
- **Route accuracy**: whether the routing decision is correct. Routing determines who handles the request (direct answer, RAG lookup, multi-intent split, or escalate to a human) — it's the field in the whole request-understanding task that most directly affects downstream system behavior, so getting it wrong throws off all subsequent processing.

> 💡 For a structured-extraction task, what we care about is **semantic correctness** (whether each field's value falls within the predefined range and matches the intended meaning), not exact string matching. For example, for a question that contains both the "travel request" and "reimbursement follow-up" intents, as long as the model correctly identifies both intents, it counts as correct regardless of the order they appear in.

```python
def compute_intent_f1(pred_intents, true_intents):
    """Compute the F1 score for a list of intents"""
    pred_set = set(pred_intents)
    true_set = set(true_intents)
    if len(pred_set) == 0 and len(true_set) == 0:
        return 1.0
    if len(pred_set) == 0 or len(true_set) == 0:
        return 0.0
    precision = len(pred_set & true_set) / len(pred_set)
    recall = len(pred_set & true_set) / len(true_set)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)

def evaluate_predictions(predictions, ground_truths):
    """
    Evaluate structured-extraction results, returning a dict of raw values:
    - json_valid: number of samples that are valid JSON
    - intent_f1: average intent F1 (0-1)
    - route_accuracy: number of samples with the correct route
    - total: total number of samples
    """
    n = len(ground_truths)
    json_valid = 0
    intent_f1_sum = 0
    route_correct = 0

    for pred, truth in zip(predictions, ground_truths):
        parsed = pred["parsed"]
        if parsed is None:
            continue

        json_valid += 1

        # Intent F1
        f1 = compute_intent_f1(parsed.get("intents", []), truth["intents"])
        intent_f1_sum += f1

        # Route accuracy
        if parsed.get("route") == truth["route"]:
            route_correct += 1

    return {
        "json_valid": json_valid,
        "intent_f1": intent_f1_sum / n if n > 0 else 0,
        "route_accuracy": route_correct,
        "total": n
    }

def print_eval_results(results, model_name):
    """Print evaluation results in a formatted way"""
    r = results
    n = r["total"]
    print(f"\n=== {model_name} evaluation results ===")
    print(f"  JSON compliance rate: {r['json_valid']}/{n} ({r['json_valid']/n*100:.0f}%)")
    print(f"  intents F1: {r['intent_f1']*100:.1f}%")
    print(f"  route accuracy: {r['route_accuracy']}/{n} ({r['route_accuracy']/n*100:.0f}%)")

def render_comparison_table(results_list, model_names):
    """Render multiple sets of evaluation results as a Markdown comparison table"""
    from IPython.display import display, Markdown
    header = "| Metric | " + " | ".join(model_names) + " |"
    sep = "| --- | " + " | ".join(["---"] * len(model_names)) + " |"
    rows = []
    for metric, label in [("json_valid", "JSON compliance rate"), ("intent_f1", "intents F1"), ("route_accuracy", "route accuracy")]:
        cells = []
        for r in results_list:
            n = r["total"]
            if metric == "json_valid":
                cells.append(f"{r['json_valid']}/{n} ({r['json_valid']/n*100:.0f}%)")
            elif metric == "intent_f1":
                cells.append(f"{r['intent_f1']*100:.1f}%")
            else:
                cells.append(f"{r['route_accuracy']}/{n} ({r['route_accuracy']/n*100:.0f}%)")
        rows.append(f"| {label} | " + " | ".join(cells) + " |")
    display(Markdown("\n".join([header, sep] + rows)))

def predict_batch(model_name, test_data, system_prompt=SYSTEM_PROMPT):
    """Batch-predict on the test set with the given model"""
    predictions = []
    for item in test_data:
        query = item["query"]
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                extra_body={"enable_thinking": False},
                temperature=0.1
            )
            raw = response.choices[0].message.content
        except Exception as e:
            raw = str(e)
        parsed = validate_label(raw)
        predictions.append({"raw": raw, "parsed": parsed})
    return predictions

print("Evaluation functions defined")
```

### 4.2 Evaluating the Teacher Model (qwen3.6-plus)

Let's first see how the teacher model performs on the test set — this is distillation's "ceiling":

```python
ground_truths = [item["ground_truth"] for item in test_data]

print("Evaluating the teacher model (qwen3.6-plus)...")
teacher_preds = predict_batch("qwen3.6-plus", test_data)
teacher_results = evaluate_predictions(teacher_preds, ground_truths)
print_eval_results(teacher_results, "Teacher model (qwen3.6-plus)")
```

### 4.3 Evaluating the Base Small Model (Qwen3-0.6B)

Now let's look at how the untrained small model performs — this is the "starting point" before distillation. The base model was already downloaded to `/mnt/workspace/model/Qwen3-0.6B` in Section 0; the code below loads it via ModelScope and runs local inference.

```python
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch

model_path = '/mnt/workspace/model/Qwen3-0.6B'
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(
    model_path, dtype=torch.float16, device_map='auto',
    trust_remote_code=True
)

print("Evaluating the base model (Qwen3-0.6B, local inference)...")
base_preds = []
for i, item in enumerate(test_data):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": item["query"]}
    ]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False
    )
    inputs = tokenizer(text, return_tensors="pt").to(base_model.device)
    with torch.no_grad():
        outputs = base_model.generate(
            **inputs, max_new_tokens=512,
            temperature=0.1, do_sample=True
        )
    response = tokenizer.decode(
        outputs[0][inputs.input_ids.shape[1]:],
        skip_special_tokens=True
    )
    parsed = validate_label(response)
    base_preds.append({"raw": response, "parsed": parsed})
    status = "OK" if parsed else "FAIL"
    print(f"  [{i+1}/{len(test_data)}] {status} | {item['query'][:50]}...")

ground_truths = [item["ground_truth"] for item in test_data]
base_results = evaluate_predictions(base_preds, ground_truths)
print_eval_results(base_results, "Base model (Qwen3-0.6B)")
```

The evaluation score is an overall summary — it's more useful to look at exactly where the base model goes wrong. Below are a few typical failure cases, to give you a concrete feel for the output quality of an untrained 0.6B model.

```python
# ⚠️ Requires running the base model evaluation code from Section 4.3 on DSW first
# If base_preds doesn't exist, skip this cell

if 'base_preds' in dir():
    print("--- Typical base-model failure cases ---")
    shown = 0
    for i, (pred, truth) in enumerate(zip(base_preds, ground_truths)):
        if pred["parsed"] is None and shown < 3:
            print(f"\n[Case {shown+1}] JSON parsing failed")
            print(f"  Question: {test_data[i]['query']}")
            print(f"  Model output (first 200 chars): {pred['raw'][:200]}")
            print(f"  Expected: {json.dumps(truth, ensure_ascii=False)[:100]}...")
            shown += 1
    if shown == 0:
        for i, (pred, truth) in enumerate(zip(base_preds, ground_truths)):
            if pred["parsed"] and pred["parsed"].get("department") != truth["department"] and shown < 3:
                print(f"\n[Case {shown+1}] Field error")
                print(f"  Question: {test_data[i]['query']}")
                print(f"  Predicted department: {pred['parsed'].get('department')}  Actual department: {truth['department']}")
                shown += 1
else:
    print("base_preds is not defined; please run the base-model evaluation from Section 4.3 on DSW first")
    print("or see the pre-generated comparison results in Section 4.4")
```

After looking at the specific cases, let's put the base model's and the teacher model's results side by side. These two sets of numbers represent distillation's starting point and its ceiling, respectively:

```python
# Render the baseline comparison table
# Use actual results if the evaluation code has been run; otherwise show pre-generated reference data
from IPython.display import display, Markdown

if 'base_results' in dir() and 'teacher_results' in dir():
    print("### 4.4 Baseline Comparison\n")
    render_comparison_table(
        [base_results, teacher_results],
        ["Base model (Qwen3-0.6B)", "Teacher model (qwen3.6-plus)"]
    )
else:
    display(Markdown("""### 4.4 Baseline Comparison

> The table below is pre-generated reference data. Running the evaluation code in Sections 4.2 and 4.3 will show actual results.

| Metric | Base model (Qwen3-0.6B) | Teacher model (qwen3.6-plus) |
| --- | --- | --- |
| JSON compliance rate | 15/31 (48%) | 31/31 (100%) |
| intents F1 | 23.7% | 83.9% |
| route accuracy | 5/31 (16%) | 28/31 (90%) |"""))
```

Looking at the evaluation results on the test samples, the gap between the base model and the teacher model is stark: most of the base model's output can't be parsed as valid JSON, and broken formatting (missing brackets, extraneous text, misplaced fields) is the most glaring problem. Even among the outputs that are correctly formatted, intent-recognition and route accuracy are both low, meaning the vast majority of requests would be routed to the wrong processing module. By contrast, the teacher model performs consistently well across every metric, showing that the large model has already mastered this task well.

> The goal of distillation: bring the 0.6B model from "practically unusable" up to "close to teacher-level." Even if it can't fully catch up to the teacher, as long as there's a substantial improvement across the metrics, it already has value for production deployment.

At this point, the training data is ready, and the gap between the base model and the teacher model is clear. Next, we'll use the teacher-labeled data to train the small model, bringing it from "practically unusable" up to "close to teacher-level."

You might be thinking: training a model with data — isn't that just fine-tuning? Exactly right — distillation's training procedure is almost identical to fine-tuning: prepare training data, load the base model, run SFT training. The only difference is where the data comes from: fine-tuning uses human-labeled data, distillation uses data generated by a teacher model. So if you're already familiar with fine-tuning, what follows will feel very familiar; if not, don't worry — the next section starts from the basics.

## 5. How Fine-Tuning Works

Before starting training, let's first understand how a model learns from training data.

### 5.1 How a Model Learns

#### The Loss Function

At the core of model training is an iterative optimization process: given an input, the model produces a prediction; the prediction is compared against the expected output to compute a **loss**; the model's parameters are then adjusted to make the loss smaller. The loss function quantifies "how far the prediction is from what's expected" — the smaller the loss, the closer the model's output is to the expected output in the training data.

<div style="text-align: center">
*(Figure: the loss curve — the closer the loss is to zero, the closer the model's output is to the expected output in the training data.)*
</div>

#### Gradient Descent

How do you find the parameters that minimize the loss? Gradient descent starts from a random point, and at each step, adjusts the parameters in the direction where the loss decreases fastest, gradually converging toward the optimum.

<div style="text-align: center">
*(Figure: gradient descent starts from random parameters and moves in the direction where the loss decreases fastest, gradually converging toward the optimum.)*
</div>

How much the parameters move at each step is determined by the **learning rate**. Too large a learning rate, and the parameters bounce back and forth around the optimum without ever converging; too small, and convergence is slow and training takes far too long; the right learning rate lets you steadily approach the optimum.

<div style="display: flex; justify-content: space-between; gap: 2px; padding: 15px; background:rgba(0,0,0,0)">
    <!-- Column 1 -->
    <div style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px">
        <p style="margin-top: 10px">A well-chosen learning rate lets you find good parameters in a relatively short amount of time.</p>
        *(Figure: a well-chosen learning rate finds good parameters in a relatively short time.)*
    </div>
    <!-- Column 2 -->
    <div style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px">
        <p style="margin-bottom: 10px">A learning rate that's too low can still find good parameters, but at the cost of much more time and resources.</p>
        *(Figure: a learning rate that's too low can still find good parameters, but costs much more time and resources.)*
    </div>
    <!-- Column 3 -->
    <div style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px">
        <p style="margin-bottom: 10px">A learning rate that's too high can cause you to overshoot the optimum entirely, and you may never find the lowest point.</p>
        *(Figure: a learning rate that's too high overshoots the optimum entirely and may never find the lowest point.)*
    </div>
</div>

### 5.2 LoRA: Efficient Fine-Tuning

Full-parameter fine-tuning requires updating every weight in the model, and large models routinely have billions of parameters, making both compute and storage costs high. LoRA (Low-Rank Adaptation) is an efficient alternative.

The core idea behind LoRA: instead of directly modifying the original weight matrix, "attach" a pair of small low-rank matrices alongside it to learn the delta.

<div style="text-align: center;">
*Figure (translated): LoRA decomposes the weight update into a low-rank product.*

```text
Original weight matrix:  W  (d x d)
LoRA:                    W = W0 + ΔW
                         ΔW = B · A     (A: r x d, B: d x r, rank r << d)
                         only A and B are trained; W0 stays frozen
```
</div>

Suppose the original weight matrix is $W$ (dimension $d \times d$). LoRA decomposes the delta $\Delta W$ into the product of two small matrices: $\Delta W = A \times B$, where $A$ has dimension $d \times r$ and $B$ has dimension $r \times d$, with $r$ much smaller than $d$.

For example, when $d = 4096$ and $r = 8$, full-parameter fine-tuning needs to update $4096 \times 4096 = 16{,}777{,}216$ parameters, while LoRA only needs to update $4096 \times 8 + 8 \times 4096 = 65{,}536$ parameters — **cutting the parameter count down to 0.4% of the original.**

LoRA's key parameter, `lora_rank` (i.e., $r$), controls the dimension of the low-rank matrices. A larger $r$ lets the model learn more of a delta, but also raises training cost. For a distillation task, $r = 8$ is usually enough. LoRA has another important advantage: since only the "patch" parameters are trained and the original model weights stay unchanged, it preserves over 97% of the model's base ability, effectively avoiding "catastrophic forgetting."

### 5.3 Judging Training State

While training, you need to watch two key metrics to judge the state of training: **training loss** reflects how the model performs on the training data, and **evaluation loss** reflects how it performs on validation data that wasn't part of training. By watching how these two metrics trend over time, you can tell which state the model is in:

| Training loss | Evaluation loss | State | Meaning |
| --- | --- | --- | --- |
| Not decreasing / rising | Not decreasing / rising | **Training failed** | The learning rate may be too high; the model isn't learning |
| Decreasing | Decreasing | **Underfitting** | The model is learning, but hasn't learned enough yet — keep training |
| Decreasing | Decreases then rises | **Overfitting** | The model is "memorizing the answers" — needs more data or fewer training epochs |
| Leveling off | Leveling off | **Training succeeded** | The model has learned as much as it's going to |

## 6. Training

The environment dependencies and base model were already installed and downloaded in Section 0. The full training process has four steps:

<div style="text-align: center;">
    *Figure (translated): the four-step LoRA fine-tuning workflow.*

```text
Step 1: Prepare data        -> train.jsonl accessible, auto-split 10% validation set        (~1 min)
Step 2: Start training      -> swift sft --model /model --lora_rank 8 --learning_rate 5e-5
                               --num_train_epochs 5                                          (A10 GPU ~10 min)
Step 3: Monitor loss        -> watch training / validation loss curves; rising validation loss = overfitting
Step 4: Check results       -> loss curves (images/), TensorBoard (runs/), checkpoint; merge for deployment
```
</div>

| Step | Description |
| --- | --- |
| 1. Prepare the data | Training data is already provided at `resources/4_1/train.jsonl` — just confirm the file is accessible |
| 2. Start training | Run the `swift sft` command below — about 10 minutes on an A10 GPU |
| 3. Monitor loss | Watch how the loss changes in the training log to judge the training state (see Section 5.3) |
| 4. Check the results | The model and logs are saved in `output/model/<training_dir>/` (see below); the loss curve chart is in its `images/` subdirectory, and TensorBoard logs are in the `runs/` subdirectory |

> 💡 ms-swift automatically creates a directory for each training run, named in the format `v{version}-{date}-{time}`, e.g. `v1-20260415-145518`. Once training finishes, look for the corresponding directory under `output/model/`.

### 6.1 Preparing the Training Data

Make sure `resources/4_1/train.jsonl` is accessible in the current directory. If you cloned the course code via the install script, the training data is already in place.

### 6.2 Starting Training

Use the ms-swift framework to do LoRA fine-tuning. Key parameters explained:

- `--model`: the path to the base model downloaded in Section 0
- `--model_type qwen3`: explicitly specify the model type (ms-swift can't auto-detect it when loading from a local path)
- `--split_dataset_ratio 0.1`: automatically split 10% of the training data as a validation set, used to monitor overfitting
- `--lora_rank 8`: the dimension of the LoRA low-rank matrices — 8 is enough for a structured-extraction task
- `--num_train_epochs 5`: number of training epochs
- `--learning_rate 5e-5`: the learning rate
- `--per_device_train_batch_size 8`: the training batch size per GPU
- `--eval_steps 20`: compute the validation loss every 20 steps, to keep an eye on overfitting

**How these parameters were chosen**: these values aren't fixed — they need to be adjusted for your specific situation. The table below lists the tuning direction for each key parameter:

| Parameter | Value used in this course | Tuning direction |
| --- | --- | --- |
| `lora_rank` | 8 | Below 200 training samples, can lower to 4; above 2,000 samples or for a more complex task, can raise to 16 |
| `learning_rate` | 5e-5 | Loss not decreasing → raise to 1e-4; loss oscillating → lower to 1e-5 |
| `num_train_epochs` | 5 | Validation loss starts rising → reduce epochs; validation loss still decreasing → increase epochs |
| `per_device_train_batch_size` | 8 | Not enough VRAM → lower to 4; plenty of VRAM → raising it can speed up training |

> 💡 You may notice that this lesson's training data is only around 100 samples, and by the table above that would seem to suggest `r=4`. We chose `r=8` here because "request understanding" requires jointly learning five dimensions at once — intent recognition (8-way multi-label), department, urgency, entity extraction, and routing decision — which is more complex than a typical single-label classification task. The "under 200 samples → lower to 4" guidance in the table is more applicable to scenarios where the output is just one or two simple fields.

#### 🤖 Try Training with Qwen Code (Optional)

You can run the code cell below to start training manually, or try another approach: paste the prompt below into Qwen Code and let it handle the training for you, explaining step by step what's happening at each stage along the way.

> If you haven't installed Qwen Code yet, refer to the installation steps in Section 0.3.

Once it's started, paste the following prompt into Qwen Code:

````text
I'm learning about model distillation and need your help running a LoRA fine-tuning job. Please follow the steps below, explaining what you're doing and why at each step.

## Environment
- Base model path: /mnt/workspace/model/Qwen3-0.6B (Qwen3-0.6B, 0.6B parameters)
- Training data: resources/4_1/train.jsonl (messages format, each with system/user/assistant roles)
- Framework: ms-swift (already installed system-wide, just use the swift command directly)
- GPU: A10 (30GB VRAM)
- Working directory: /mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线/
- ⚠️ Do not activate the llm_learn virtual environment, do not run source activate. The PyTorch version in the venv is incompatible with the system CUDA — activating it will make the GPU unavailable. Use the default system environment directly.

## Important constraints
- Do not read any notebook files (.ipynb) to look at existing training commands or parameters. Decide on parameter values independently based on your own analysis of the data.
- Do not run swift --version (it will error), do not run swift sft --help (the output is incomplete and not useful).
- Do not access GitHub or any other external site to look up documentation (this environment has no internet access).
- Your reasoning for training parameters should come from your own analysis of the training data (sample count, token lengths, etc.), not from consulting documentation.

## Please carry out the following steps

### Step 1: Verify the environment
- Confirm no virtual environment is currently active (there should be no `(llm_learn)` prefix before the command prompt)
- Verify the GPU is available: run `python3 -c "import torch; print('GPU available:', torch.cuda.is_available(), '| device count:', torch.cuda.device_count())"`
- If it prints False, check whether you accidentally activated a virtual environment; run `deactivate` and try again
- **Only proceed once GPU verification passes**
- Confirm the swift command exists (run `which swift`, not `swift --version`)
- Change into the working directory
- Confirm the base model files exist
- Confirm the training data file exists and count the number of samples

### Step 2: Analyze the training data and decide on training parameters
First run the following analysis on the training data (using a Python script, not swift commands):
1. Count the total number of samples
2. Read 5-10 samples to understand the data format, and explain to me what the system/user/assistant roles each contain
3. Use the tokenizer to compute the token-length distribution of each sample (min, max, mean, P95); example code:
   ```python
   from transformers import AutoTokenizer
   tokenizer = AutoTokenizer.from_pretrained("/mnt/workspace/model/Qwen3-0.6B", trust_remote_code=True)
   # Concatenate the system+user+assistant content for each sample, tokenize it, and compute the length
   ```
   Then, based on your analysis, choose values for the following parameters, and explain to me what each parameter means and why you chose that value:
- --lora_rank: the LoRA low-rank matrix dimension. Consider: the task needs to jointly learn 5 fields (intents/department/urgency/entities/route)
- --learning_rate: the learning rate. Consider: data scale and model size
- --num_train_epochs: number of training epochs. Consider: data volume — too many epochs will overfit
- --per_device_train_batch_size: batch size per GPU. Consider: A10 has 30GB VRAM, model is 0.6B parameters
- --max_length: max sequence length. Decide based on the P95 token length you computed above, leaving some margin

   Use these fixed values for the following parameters (needed to ensure the loss curve chart and validation-set evaluation get generated):
   --model /mnt/workspace/model/Qwen3-0.6B
   --model_type qwen3
   --dataset resources/4_1/train.jsonl
   --split_dataset_ratio 0.1
   --eval_steps 20
   --save_strategy steps
   --save_steps 20

### Step 3: Start training
⚠️ Training takes about 10-15 minutes. It must be run in the background, otherwise continuous log output will flood the terminal, and the command could be killed due to timeout.

Start it like this:
```bash
cd /mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线/
nohup swift sft [the parameters you decided on] > /tmp/swift_train.log 2>&1 &
echo "Training PID: $!"
```

Once it's started, run `tail -20 /tmp/swift_train.log` every 2-3 minutes to check the latest log, and report to me:
- The current training progress (which epoch, which step)
- How the loss is trending (is it decreasing normally)
- If anything looks off (e.g. loss suddenly spikes), flag it and suggest how to handle it

To check whether training has finished: run `pgrep -f "swift sft"` to see if the process is still running. If the process is gone, training is done — check the end of the log to confirm the final state.

### Step 4: Analysis once training is done
Once training finishes:
1. Find the output directory (the newest one under output/model/)
2. Find the loss curve images in that directory's images/ subdirectory
3. Show the train/loss and eval/loss curves separately
4. Interpret the curves:
   - Did training converge normally?
   - Any signs of overfitting? (Did eval/loss start rising?)
   - Is the final loss value reasonable?
5. Based on the loss curves, give me your judgment: was this training run successful?

### Step 5: Prepare for the next step
- Tell me where the merged model will be saved
- Briefly explain what can be done next (merging the LoRA parameters, evaluating the result)
````

If you chose to complete training with Qwen Code, you can skip the code cell below. If you'd rather run it manually, just execute the command below directly — the meaning of each parameter was already explained above.

```python
# LoRA fine-tuning of Qwen3-0.6B (about 10 minutes on an A10 GPU)
from pathlib import Path

cwd = Path.cwd().resolve()
COURSE_ROOT = next(
    (p for p in [cwd, *cwd.parents] if (p / "course_core").exists() and (p / "C4_交付上线").exists()),
    None
)
if COURSE_ROOT is None:
    raise FileNotFoundError(f"Could not find the course root directory. Current working directory: {cwd}. Please make sure you're running this from within the 大模型ACP认证教程 directory or a subdirectory of it.")

BASE_MODEL_PATH = Path("/mnt/workspace/model/Qwen3-0.6B")
TRAIN_DATA_PATH = COURSE_ROOT / "course_core" / "resources" / "4_1" / "train.jsonl"
OUTPUT_DIR = COURSE_ROOT / "C4_交付上线" / "output" / "model"

print(f"Course root directory: {COURSE_ROOT}")
print(f"Training data: {TRAIN_DATA_PATH}")
print(f"Output directory: {OUTPUT_DIR}")

!swift sft \
    --model {BASE_MODEL_PATH} \
    --model_type qwen3 \
    --template qwen3 \
    --dataset {TRAIN_DATA_PATH} \
    --output_dir {OUTPUT_DIR} \
    --split_dataset_ratio 0.1 \
    --learning_rate 5e-5 \
    --lora_rank 8 \
    --num_train_epochs 5 \
    --per_device_train_batch_size 8 \
    --max_length 512 \
    --eval_steps 20 \
    --save_strategy steps \
    --save_steps 20
```

### 6.3 Observing the Training Results

Once training finishes, ms-swift prints the output directory path (`images_dir`) at the end of the training log, for example:

```
images_dir: /mnt/workspace/aliyun_acp_learning/大模型ACP认证教程/C4_交付上线/output/model/vx-xxxxxxxx-xxxxxx/images
```

Here, `vx-xxxxxxxx-xxxxxx` is the training directory name auto-generated by ms-swift (format `v{version}-{YYYYMMDD}-{HHMMSS}`) — each training run gets a different directory name, so use whatever you actually see.

There are three ways to check how the loss changed:

- **Curve chart (most intuitive)**: open the `images/` directory mentioned above in the DSW file browser and double-click the loss curve image to view it.
- **TensorBoard logs**: the `runs/` subdirectory under the same training directory holds the TensorBoard logs. Run `tensorboard --logdir output/model/` in the terminal to launch the interactive dashboard.
- **Training log**: the output of the cell above contains the loss value at every step, so you can watch the numbers directly to see if they're decreasing.

Based on the criteria from Section 5.3: if both the training loss and validation loss keep decreasing, the model is learning normally; if the validation loss starts rising, that indicates overfitting, and you need to reduce the number of epochs or add more data.

### 6.4 Merging the LoRA Parameters

Once training is done, merge the LoRA parameters with the base model to produce a single, standalone complete model. The code below automatically finds the most recently created checkpoint (sorted by creation time, not alphabetically) and merges it. The merged model is saved in a `checkpoint-xxx-merged` directory.

```python
import glob
from pathlib import Path

cwd = Path.cwd().resolve()
COURSE_ROOT = next(
    (p for p in [cwd, *cwd.parents] if (p / "course_core").exists() and (p / "C4_交付上线").exists()),
    None
)
if COURSE_ROOT is None:
    raise FileNotFoundError(f"Could not find the course root directory. Current working directory: {cwd}. Please make sure you're running this from within the 大模型ACP认证教程 directory or a subdirectory of it.")

OUTPUT_DIR = COURSE_ROOT / "C4_交付上线" / "output" / "model"

# Automatically find the most recently created LoRA checkpoint (sorted by creation time, excluding already-merged directories)
import os
ckpts = [c for c in glob.glob(str(OUTPUT_DIR / "*" / "checkpoint-*")) if not c.endswith('-merged')]
ckpts.sort(key=os.path.getctime)

if not ckpts:
    print(f"No checkpoint found. Please run the training command from Section 6.2 first. Searched directory: {OUTPUT_DIR}")
else:
    latest_ckpt = ckpts[-1]
    print(f"Found checkpoint: {latest_ckpt}")
    print(f"Merging LoRA parameters...")
    !swift export --adapters {latest_ckpt} --merge_lora true
```

### 6.5 Common Issues and Troubleshooting

When training runs into problems, don't just look at a single loss number. First look at the trend of the training loss and validation loss, then combine that with the output format, task metrics, and GPU memory logs to figure out the cause. Here are the issues most commonly seen in distillation fine-tuning.

| Symptom | Common cause | How to tell | How to fix it |
| --- | --- | --- | --- |
| Training loss oscillates a lot | Learning rate too high, or batch too small causing unstable gradients | Loss bounces up and down noticeably, with no steady downward trend over several steps | First lower `learning_rate` from `5e-5` to `1e-5`; if VRAM allows, increase batch size or use gradient accumulation |
| Training loss decreases very slowly | Learning rate too low, not enough training steps, or the task genuinely needs more LoRA expressive capacity | Loss is decreasing, but only slightly; validation loss isn't getting worse either | Try raising `learning_rate` to `1e-4`, or increase `num_train_epochs`; if there are many output fields with complex judgments, try raising `lora_rank` |
| Training loss basically doesn't decrease | There may be a problem with the data, template, model loading, or optimizer configuration | Loss stays roughly flat for a long time, and generated output shows no clear improvement either | First spot-check whether training samples match the input/output template, then check whether the labels are valid JSON, whether the training parameters actually took effect, and whether the LoRA parameters are actually being trained |
| Validation loss decreases then rises | The model is starting to overfit the training set | Training loss keeps decreasing, but validation loss climbs back up; performance on the evaluation set isn't improving in step | Reduce `num_train_epochs`, use the checkpoint with the lowest validation loss; prioritize adding more high-quality samples rather than simply training longer |
| Loss decreases normally, but JSON format is still unstable | Training samples aren't formatted consistently, or the prompt and the label's output constraints don't match | Some outputs contain code blocks, extra explanation, missing fields, or inconsistent field names | Unify the JSON schema across all labels; strip markdown code blocks and extraneous text; make sure training and inference use the exact same output requirements |
| Intent recognition still misses things | Not enough coverage of multi-intent, boundary-case, and similar-intent samples | Single-intent samples do well, but multi-intent or similar requests are often missed | Add more multi-intent samples, easily-confused samples, and real business edge-case samples; don't just chase a fixed ratio — check whether you've covered the high-frequency errors seen in production |
| Out of VRAM | Batch size, sequence length, or model size exceeds what the current GPU can handle | The log shows a CUDA OOM error, with training interrupted during the forward or backward pass | First lower `per_device_train_batch_size` to 4 or 2; if needed, shorten `max_length`, enable gradient accumulation, or switch to a smaller student model |

## 7. Evaluating the Distillation Result

Once training is done, evaluate how the distilled model performs, and compare it against the base model and the teacher model.

> 💡 **Tip**: If you didn't do the training on PAI-DSW, you can skip running the code and just look at the pre-generated evaluation results below.

```python
import glob
from pathlib import Path
import json
import torch
import os
import shutil
from transformers import AutoModelForCausalLM, AutoTokenizer

# ================= Configuration =================
# Make sure this points to your original, un-fine-tuned base model path
# If you previously loaded base_model, you can use base_model.name_or_path, or specify the path manually

cwd = Path.cwd().resolve()
COURSE_ROOT = next(
    (p for p in [cwd, *cwd.parents] if (p / "course_core").exists() and (p / "C4_交付上线").exists()),
    None
)
if COURSE_ROOT is None:
    raise FileNotFoundError(f"Could not find the course root directory. Current working directory: {cwd}. Please make sure you're running this from within the 大模型ACP认证教程 directory or a subdirectory of it.")

BASE_MODEL_PATH = Path("/mnt/workspace/model/Qwen3-0.6B")  # <--- Make sure this is your original Qwen3 base-model path
OUTPUT_DIR = COURSE_ROOT / "C4_交付上线" / "output" / "model"
TEST_DATA_PATH = COURSE_ROOT / "course_core" / "resources" / "4_1" / "test_30.jsonl"
# ===================================================

# 1. Free up VRAM
if 'base_model' in dir():
    del base_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print("Base model VRAM freed")

# 2. Find the merged model path
merged_dirs = [d for d in glob.glob(str(OUTPUT_DIR / "*" / "checkpoint-*-merged"))]
merged_dirs.sort(key=os.path.getctime)
if not merged_dirs:
    raise FileNotFoundError(f"No merged checkpoint found. Please run swift export first. Searched directory: {OUTPUT_DIR}")

student_path = merged_dirs[-1]
print(f"Distilled model path: {student_path}")

# 3. [Core fix] Copy the tokenizer files from the base model into the merged model directory
print("Fixing tokenizer files...")
tokenizer_files_to_copy = [
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.json",      # Qwen2/3 usually has this
    "merges.txt",      # Qwen2/3 usually has this
    "added_tokens.json" # If present
]

for filename in tokenizer_files_to_copy:
    src_file = os.path.join(str(BASE_MODEL_PATH), filename)
    dst_file = os.path.join(student_path, filename)
    
    if os.path.exists(src_file):
        # Force overwrite to make sure we use the base model's clean config
        shutil.copy2(src_file, dst_file)
        print(f"  ✅ Copied: {filename}")
    else:
        print(f"  ⚠️ Not found in base model: {filename} (skipping)")

# 4. Load the tokenizer (should now load correctly)
print("Loading tokenizer...")
try:
    student_tokenizer = AutoTokenizer.from_pretrained(
        student_path, 
        trust_remote_code=True,
        use_fast=True  # Prefer the fast tokenizer
    )
    print("✅ Tokenizer loaded successfully")
except Exception as e:
    print(f"❌ Load failed: {e}")
    print("Trying to force-load Qwen2Tokenizer...")
    from transformers import Qwen2Tokenizer
    student_tokenizer = Qwen2Tokenizer.from_pretrained(
        str(BASE_MODEL_PATH), # If the merged directory still doesn't work, load the tokenizer directly from the base model
        trust_remote_code=True
    )
    print("✅ Loaded the tokenizer directly from the base model")

# 5. Load the model
print("Loading model weights...")
student_model = AutoModelForCausalLM.from_pretrained(
    student_path, 
    dtype=torch.float16, 
    device_map='auto',
    trust_remote_code=True
)
student_model.eval()
print("✅ Model loaded")

# 6. Load the test data
if 'test_data' not in dir():
    test_data = []
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                test_data.append(json.loads(line))
    print(f"Loaded test data: {len(test_data)} samples")

# 7. Run inference and evaluate
print("Starting evaluation...")
student_preds = []
SYSTEM_PROMPT = "You are a helpful assistant." # Make sure this is defined

for i, item in enumerate(test_data):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": item["query"]}
    ]
    
    # Apply the chat template
    text = student_tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    inputs = student_tokenizer(text, return_tensors="pt").to(student_model.device)
    
    with torch.no_grad():
        outputs = student_model.generate(
            **inputs, 
            max_new_tokens=512,
            temperature=0.1, 
            do_sample=True,
            pad_token_id=student_tokenizer.eos_token_id
        )
    
    response = student_tokenizer.decode(
        outputs[0][inputs.input_ids.shape[1]:],
        skip_special_tokens=True
    )
    
    # Assumes validate_label is defined
    parsed = validate_label(response) if 'validate_label' in dir() else response
    student_preds.append({"raw": response, "parsed": parsed})
    
    if (i + 1) % 5 == 0:
        print(f"  Progress: [{i+1}/{len(test_data)}]")

print("Evaluation complete.")
```

```python
# Render the three-way comparison table
# Use actual results if all evaluation code has been run; otherwise show pre-generated reference data
from IPython.display import display, Markdown

if 'base_results' in dir() and 'teacher_results' in dir() and 'student_results' in dir():
    print("### 7.1 Three-Way Comparison\n")
    render_comparison_table(
        [base_results, teacher_results, student_results],
        ["Base model (0.6B)", "Teacher model (qwen3.6-plus)", "Distilled model (0.6B)"]
    )
else:
    display(Markdown("""### 7.1 Three-Way Comparison

> The table below is pre-generated reference data. Running the evaluation code in Section 4 and Section 7 will show actual results.

| Metric | Base model (0.6B) | Teacher model (qwen3.6-plus) | Distilled model (0.6B) |
| --- | --- | --- | --- |
| JSON compliance rate | 15/31 (48%) | 31/31 (100%) | 31/31 (100%) |
| intents F1 | 23.7% | 83.9% | 70.4% |
| route accuracy | 5/31 (16%) | 28/31 (90%) | 24/31 (77%) |"""))
```

The most immediately visible payoff from distillation is that the JSON-format problem is fully resolved: the distilled model's output can almost always be parsed as valid JSON, showing the model has reliably learned the output format. Intent-recognition F1 and route accuracy also improve substantially — the model has genuinely learned the teacher's judgment logic. The improvement in route accuracy matters most for a production system, since it directly determines whether requests get dispatched to the right processing module. The distilled model hasn't fully caught up to the teacher yet, but it's already close to the capability ceiling for a 0.6B model on this task. If you need higher accuracy, you could switch to a 1.5B or 4B model as the student.

### 7.2 The Limits of Distillation

Distillation isn't a cure-all. There are still situations where the distilled model tends to make mistakes: multi-intent cases where the intents depend on each other (e.g. "request leave, and automatically adjust attendance," where there's a causal link between the two intents that a 0.6B model has trouble capturing); rare combinations not covered by the training set (e.g. "IT support + travel request" — if there are no similar samples in the training data, the model will guess wrong); and extremely vague phrasing (e.g. "help me deal with that thing," which offers no signal to latch onto at all).

A 0.6B model is well suited to "high-frequency, fixed-domain, single-step judgment" specialized tasks — it isn't a miniature general-purpose assistant. Its role in the system is a **preprocessor**, not an all-around replacement.

### 7.3 Is Your Task a Good Fit for Distillation?

Before investing time and compute, do a quick sanity check first.

**Traits of a task well suited to distillation**:

- The output format is fixed and can be automatically validated by a rule (like a JSON schema or classification labels)
- It doesn't depend on real-time external knowledge — only the input text itself matters
- It's called frequently, on a high-frequency path in the system
- The teacher model performs consistently, and its mistakes follow a clear pattern (e.g. a certain kind of intent is always misidentified, rather than errors being random)

**Scenarios not well suited to distillation, and alternatives**:

| Scenario | Reason | Alternative |
| --- | --- | --- |
| Needs real-time knowledge updates (e.g. policy lookups) | The distilled model's knowledge is frozen at training time | Use distillation for intent recognition + RAG for up-to-date knowledge |
| Needs multi-step reasoning (e.g. math proofs) | A small model has limited reasoning ability | Keep the large model, or use reasoning-compression distillation |
| The teacher model itself is unreliable | The student can't exceed the teacher's own ceiling | First optimize the teacher's prompt, or switch to a stronger teacher |
| The base model can already basically handle the requirement | Limited room for improvement, not worth the investment | Weigh the cost against the benefit, and consider just using the base model directly |

**A quick validation process**: before committing to full training, it's worth running a quick experiment with a small number of samples first. If the base model can already basically meet the requirement, or fine-tuning doesn't produce much improvement, you can re-evaluate whether this is the right task to distill, or adjust your optimization strategy (e.g. increasing the diversity of the training data, or adjusting the teacher's prompt).

**A mismatch between the data distribution and production** is also a common pitfall. The expression patterns in synthetic data may differ from how real users actually phrase questions, which can hurt the model's performance in production. Mixing in some real data can help the model adapt to the actual distribution.

## 8. Cost-Benefit Analysis

The ultimate goal of distillation is to lower inference cost in production. Let's run the numbers.

### 8.1 Cost Comparison

Assume a typical request-understanding scenario: 20,000 requests per day on average, with each input averaging 200 tokens (system prompt + employee question) and each output 100 tokens (the JSON ticket).

**Option A: Large-model API (qwen3.6-plus)**

DashScope charges per token: 2 yuan per million input tokens, 12 yuan per million output tokens. Based on the usage above:

- Daily input cost: 20,000 × 200 tokens ÷ 1,000,000 × 2 yuan = 8 yuan
- Daily output cost: 20,000 × 100 tokens ÷ 1,000,000 × 12 yuan = 24 yuan
- **Daily cost is about 32 yuan, monthly cost about 960 yuan**

API cost scales strictly linearly with request volume: double the requests, double the cost.

**Option B: Distilled small model on GPU deployment**

Take a PAI-EAS T4 instance (4GB VRAM) as an example, priced at 3.6 yuan/hour on a pay-as-you-go basis. The 0.6B model's FP16 weights take about 1.2GB, so 4GB of VRAM is plenty. GPU billing is based on running time, not token count, so cost depends on how long the service stays online:

| Deployment mode | Daily cost | Monthly cost | Notes |
| --- | --- | --- | --- |
| Running during work hours (8 hours) | 28.8 yuan | 864 yuan | Use EAS scheduled scaling to keep the instance up only during work hours |
| Running 24 hours | 86.4 yuan | 2,592 yuan | Service is online around the clock — suited to global / cross-timezone scenarios |

### 8.2 Break-Even Point

A single API call costs about 0.0016 yuan. The break-even point varies significantly depending on the deployment mode:

- **Running during work hours (8 hours)**: GPU daily cost is 28.8 yuan, and the break-even point is around **18,000 requests per day**. At an average of 20,000 requests per day, GPU (864 yuan/month) is already about 10% cheaper than the API (960 yuan/month).
- **Running 24 hours**: GPU daily cost is 86.4 yuan, and it needs about **54,000 requests per day** to break even with the API.

The larger the request volume, the more the GPU option wins out. At 100,000 requests per day on average, the API's monthly cost is about 4,800 yuan, while GPU running during work hours only needs 864 yuan.

But cost is just one dimension of the decision. In the following scenarios, distillation is still worth considering even if inference cost isn't the deciding factor:

- **Latency-sensitive**: local inference takes about 50ms, versus about 500ms for an API call — that 10x difference matters a lot in real-time systems
- **Data security**: employee questions may touch on internal HR information, and routing them through an external API carries a data-egress risk
- **Offline scenarios**: intranet deployment, environments with no internet access, or other situations where a cloud API simply can't be called
- **Reliability**: not depending on the availability and rate limits of an external service

### 8.3 The Deployment Decision

When should you use distillation, and when shouldn't you?

| Scenario characteristics | Recommended approach | Reason |
| --- | --- | --- |
| High frequency, fixed domain, structured output | **Distillation** | Small model has low inference cost, and performance is close to the large model |
| Knowledge updates daily | **RAG** | A distilled model can't automatically adapt to new knowledge |
| Needs complex reasoning | **Keep the large model** | A small model's reasoning ability is limited |
| Distillation + RAG hybrid | **Hybrid architecture** | Distillation handles preprocessing, RAG handles knowledge lookup |

In our Q&A bot system, the distilled model's role is a **preprocessor**: quickly turning natural language into a structured ticket, then dispatching it to different backend processing modules based on the routing decision. The processing flow under this hybrid architecture looks like this:

```
Employee question: "What are the requirements for transferring to the AI department?"
  ↓
[Distilled model] Structured understanding → {intents: ["policy inquiry"], department: "HR", route: "rag_query"}
  ↓
[RAG system] Uses the extracted intent and department to query the knowledge base → retrieves the transfer policy document
  ↓
[Large model] Generates the final reply based on the retrieved results (optional)
```

The distilled model provides stable, low-latency structured extraction; RAG keeps the knowledge current (policy changes don't require retraining); and the large model handles the final answer where complex reasoning is needed. Each of the three plays its own role.

> ⚠️ **Compliance note**: If you use an open-source model (e.g. the Qwen series, under the Apache 2.0 license) as the teacher, the resulting distilled student model can be used commercially without restriction. But some commercial models (e.g. GPT-4, Claude) have terms of service that explicitly prohibit using their output to train a competing model — be sure to check the compliance terms before you proceed.

## Lesson Summary

This lesson walked through the complete data-synthesis distillation pipeline around the production scenario of "request understanding." The essence of distillation is locking a large model's judgment ability into a small model's weights; the difference from fine-tuning lies in where the training data comes from: distillation uses data generated by a teacher model, while fine-tuning uses human-labeled data.

In the data-synthesis stage, we built a high-quality training set through the pipeline "generate diverse queries → teacher model labeling → quality filtering → format training data" — data quality matters more than data quantity. In the training stage, we used the ms-swift framework on PAI-DSW to train a Qwen3-0.6B model with LoRA; LoRA only trains 0.4% of the parameters while preserving 97% of the model's base ability. Finally, we quantitatively verified the effect of distillation using three metrics — JSON compliance rate, intent F1, and route accuracy: the distilled model went from "practically unusable" at the base-model stage to a level close to the teacher model.

Distillation isn't a replacement for RAG — it's about handing off the "predictable, high-frequency, structured" parts of a system to a dedicated small model. It's complementary to RAG and to Agents, each responsible for a different part of the system.

### Further Reading

- [Alibaba Cloud PAI Platform: Fine-Tuning Qwen3 Models on PAI-DSW](https://www.aliyun.com/solution/tech-solution/qwen3-distill/2925028)
- [ms-swift Framework Documentation](https://github.com/modelscope/ms-swift)
- [The Original LoRA Paper](https://arxiv.org/abs/2106.09685)

## 🔥 Quiz

### 🔍 Multiple Choice
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>What is the core difference between distillation and fine-tuning?</b>

- A. Distillation doesn't require training, while fine-tuning does
- B. Distillation's training data is generated by a teacher model, while fine-tuning's training data is human-labeled
- C. Distillation can only be used with small models, while fine-tuning can be used with any model
- D. Distillation requires a GPU, while fine-tuning doesn't

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: B**
📝 **Explanation**:
Distillation and fine-tuning use nearly the same training procedure (SFT) — the core difference lies in where the training data comes from. Distillation uses the teacher model's output as training data, while fine-tuning uses human-labeled data. Both require a GPU for training, and both can be applied to models of different sizes.

</div>
</details>

---

### 🔍 Multiple Choice
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Which of the following tasks is best suited to be distilled into a 0.6B small model?</b>

- A. Writing a 5,000-word technical analysis report
- B. Multi-turn conversational handling of customer complaints
- C. Extracting structured intents and entities from user input
- D. Generating creative marketing copy based on context

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: C**
📝 **Explanation**:
A 0.6B model's capability boundary makes it suited to "high-frequency, fixed-domain, single-step judgment" tasks. Structured extraction (intent recognition, entity extraction, classification) is a textbook example of this: the output format is fixed, no external knowledge is needed, and no multi-step reasoning is required. Long-form generation, multi-turn dialogue, and creative writing are all beyond what a 0.6B model can handle.

</div>
</details>

---

### 🔍 Multiple Choice
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Why can't you freely use a commercial large model (like GPT-4) as the teacher model for distillation?</b>

- A. GPT-4's output quality isn't high enough
- B. GPT-4 doesn't support JSON-formatted output
- C. Some commercial models' terms of service prohibit using their output to train a competing model
- D. Commercial models' API calls are too slow

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Answer: C**
📝 **Explanation**:
This is a compliance issue, not a technical one. Some commercial models (like those from OpenAI or Anthropic) explicitly prohibit, in their terms of service, using their output to train a competing model. Using an open-source model (like the Qwen series, under the Apache 2.0 license) as the teacher doesn't have this restriction. Before starting a distillation project, always make sure to check the teacher model's license terms.

</div>
</details>

## ✉️ Feedback
Thank you for taking Alibaba Cloud's LLM ACP certification course. If you have thoughts on what worked well or what could be improved, we'd love for you to [share your feedback through this survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie).

Your critiques and encouragement are what drive us forward.
