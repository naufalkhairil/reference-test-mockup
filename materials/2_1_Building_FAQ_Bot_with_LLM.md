# 2.1 Building a New-Employee FAQ Bot with an LLM

## 🚄 Preface
You work at an educational content development company. As new employees keep joining, frequent Q&A needs create significant time and resource costs. You decide to use LLM technology to build an FAQ bot that improves the accuracy and efficiency of answering questions.

## 🍁 Course Objectives
After completing this lesson, you will be able to:

* Call Qwen via API
* Learn how LLMs work
* Understand the limitations of LLMs and their solutions

## ⚠️ Environment Setup
To experience the tutorial smoothly, we recommend first completing the [**Environment Setup**](https://edu.aliyun.com/course/3130200/lesson/343310285) chapter of the **Alibaba Cloud LLM Senior Engineer ACP Certification Course**, and making sure the required environment is correctly installed.

## 💻 1. Calling Qwen via API
### 1.1 Confirm the Python environment
The most direct way to experience an LLM is to chat with it through a web interface (such as [Qwen](https://tongyi.aliyun.com/qianwen/)). But as a developer, you often need to integrate LLM capabilities into your own application; you can use the widely-adopted OpenAI Python SDK to call the Qwen LLM. You already installed the necessary dependencies in `1.0 Compute Environment Setup`. Before running the code below, make sure you've switched to the newly created Python environment — in this example, `Python (llm_learn)`.

*(Screenshot: DSW notebook interface showing where to switch the Python kernel to the `Python (llm_learn)` environment.)*

*(Screenshot: confirming the notebook kernel is switched to the `Python (llm_learn)` environment in DSW.)*

### 1.2 Get an API Key
To call Qwen, go to Alibaba Cloud's LLM service platform Model Studio (Bailian), activate the [model invocation service](https://bailian.console.aliyun.com/#/model-market) and [create an API Key](https://bailian.console.aliyun.com/?apiKey=1#/api-key).

> If the top of the page shows the following, you haven't yet activated Model Studio's model invocation service. After activating, you can call models.
> *(Screenshot: Alibaba Cloud Model Studio page for activating the model invocation service.)*

> Follow the steps in the image below to get your API KEY:
>
> > *(Screenshot: step-by-step walkthrough in Model Studio to obtain your API key.)*
> 

### 1.3 Configure the API Key

Before using the API, you need to handle the API Key's security properly. Writing the API Key directly into your code is a bad habit — it's easy to leak the key when sharing code, and after rotating the key you'd have to edit every hardcoded copy. A safer, more convenient approach is to store the API Key in an environment variable.

The code below loads your API Key from a config file and sets it as an environment variable. After it runs, it displays the first five characters of the API Key (the rest replaced by asterisks) so you can confirm the configuration is correct without exposing the full key.

```python
# Load the Model Studio API Key for calling the Qwen LLM
import os, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath('')), 'course_core'))
sys.path.insert(0, os.getcwd())

from config.load_key import load_key
load_key()
print(f'''The API Key you configured is: {os.environ["DASHSCOPE_API_KEY"][:5]+"*"*5}''')
```

> - Press "Enter" to confirm your input. On success you'll see something like ```"The API Key you configured is: sk-88*****"```.
> - If you need to change the "API-KEY", edit the "KEY.json" file in the parent directory.
> - If you're using VS Code, the API-KEY input box appears at the **top** of the window.

### 1.4 Basic chat call
Let's try a simple conversation. The code below creates an assistant named "Company Assistant" that can answer questions about company operations. You can use the common question "which project-management tool to choose" as an example:

```python
from openai import OpenAI
import os
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
def get_qwen_response(prompt):
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            # the system message sets the LLM's role and task
            {"role": "system", "content": "You handle Q&A for an educational content development company. Your name is Company Assistant, and you answer colleagues' questions."},
            # the user message carries the user's question
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
response = get_qwen_response("What tool should our company use for project management?")
print(response)
```

### 1.5 Multi-turn conversation

In real applications, users often don't ask a complete question all at once. Imagine this scenario: a new employee first asks "What project-management tool does our company use?", gets an answer, then asks "So how do I apply for an account?" If the LLM can't "remember" the earlier conversation, it won't know which tool's account-application process the user is asking about.

This is the point of **multi-turn conversation**: letting the LLM reference historical dialogue, understand contextual connections, and thus give coherent, accurate replies.

#### How multi-turn conversation works

In the OpenAI SDK, the key to multi-turn conversation is the **messages** parameter. This is a list containing the complete conversation history. Each message has two key fields:

- **role**: the message's role — `system` (system instruction), `user` (user input), or `assistant` (model reply)
- **content**: the specific content of the message

The LLM generates its reply based on all messages in the messages list, so you need to keep the prior conversation history (both user questions and model answers) in this list.

```python
def multi_turn_chat():
    # Initialize the conversation history, including the system prompt
    conversation_history = [
        {"role": "system", "content": "You handle Q&A for an educational content development company. Your name is Company Assistant, and you answer colleagues' questions."}
    ]

    # Simulate a multi-turn conversation
    user_questions = [
        "What tool should our company use for project management?",
        "So how do I apply for an account for this tool?",
        "How long does approval usually take?"
    ]

    for question in user_questions:
        print(f"👤 User: {question}")

        # Append the user's question to the conversation history
        conversation_history.append({"role": "user", "content": question})

        # Call the LLM, passing in the full conversation history
        response = client.chat.completions.create(
            model="qwen-max",
            messages=conversation_history  # contains all historical messages
        )

        # Get the model's reply
        assistant_message = response.choices[0].message.content
        print(f"🤖 Assistant: {assistant_message}\n")

        # Append the model's reply to the history too, for use in the next turn
        conversation_history.append({"role": "assistant", "content": assistant_message})

multi_turn_chat()
```

Run the code above and you'll see that the LLM understands "this tool" refers to the project-management tool mentioned earlier, and answers the account-application and approval questions specifically. This is what multi-turn conversation does.

> 💡 **Tips**:
> - Conversation history takes up space in the **context window**. If there are too many turns, you may need to truncate or summarize the historical messages.
> - In production, you usually persist the conversation history (e.g. in a database) to support continuous cross-session conversations.
> - For more multi-turn best practices, see the [Alibaba Cloud Model Studio multi-turn conversation docs](https://help.aliyun.com/zh/model-studio/multi-round-conversation).

### 1.6 Streaming output
After running the code above, you'll notice you have to wait a while (about 20 seconds) to see the full reply. This is because, by default, the API waits until the model has generated all content before returning it all at once. In real applications, this wait can hurt the user experience — imagine a user staring at a blank screen for 20 seconds!

Fortunately, you can use "streaming output" (Streaming) to optimize this. With streaming, the model outputs as it "thinks," like a human typing, so the user sees part of the reply immediately — greatly improving the interactive experience. Next, let's see how to implement streaming output...
> 💡 Tip: streaming output only changes how content is displayed; the model's reasoning and the final answer quality remain unchanged. You can safely use this feature to improve your app's experience.

To implement streaming output, just add the `stream=True` parameter to the earlier code and adjust the output handling:

```python
def get_qwen_stream_response(user_prompt, system_prompt):
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )
    for chunk in response:
        yield chunk.choices[0].delta.content

response = get_qwen_stream_response(user_prompt="What tool should our company use for project management?", system_prompt="You handle Q&A for an educational content development company. Your name is Company Assistant, and you answer colleagues' questions.")
for chunk in response:
    print(chunk, end="")
```

### 1.7 Observations and reflection
After asking the Qwen LLM twice, you may notice some interesting phenomena:
1. Even when the question is identical, each answer is slightly different. This is one of the LLM's characteristics — like a human, it expresses similar ideas in different ways.
2. The model's suggestions center on some general project-management tools like Jira, Trello, or Asana. Although the LLM is knowledgeable, it doesn't know your company's specifics — your existing toolchain, team size, budget constraints, etc.
> The company's project-management software information can be found in the file docs/Content Development Engineer Job Guide.pdf.

These two phenomena are actually quite interesting! Why does the LLM behave this way? To understand this, we need to lift the LLM's "veil of mystery" and see how it thinks and works. Don't worry — you'll understand these concepts in a simple, intuitive way.

## 📚 2. How LLMs Work
Over recent decades, AI has undergone a profound evolution from basic algorithms to generative AI. By learning from vast amounts of data, generative AI can create brand-new content such as text, images, audio, and video, greatly advancing the widespread application of AI. Common use cases include intelligent Q&A (such as Qwen, GPT), creative image generation (such as Stable Diffusion), and code generation (such as Lingma) — spanning many fields and putting AI within reach.

*(Figure: example generative-AI applications — intelligent Q&A (Qwen, GPT), image generation (Stable Diffusion), and code generation (Lingma).)*

As one of the most classic and widespread LLM applications, intelligent Q&A is the best example for exploring how LLMs work. Next, we'll introduce the LLM's workflow in a Q&A scenario to help you more deeply understand the underlying technical principles.

### 2.1 The LLM's text-generation workflow

Let's take a simple input "ACP is a very" and look concretely at how the LLM processes this input step by step and eventually generates a complete sentence.

*Figure (translated): the LLM text-generation workflow, split into five stages.*

```text
[Input: "ACP is a very"]
        |
        v
[1. Tokenization: text -> token IDs]
        |
        v
[2. Token vectorization: token IDs -> vectors]
        |
        v
[3. LLM inference: vectors -> next-token logits]
        |
        v
[4. Decoding & autoregression: pick next token, append to input] <----+
        |                                                            |
        v                                                            └── repeat until end
[5. Output text]
```

The LLM's text-generation workflow can be divided into five stages: tokenization, token vectorization, LLM inference, decoding & autoregression, and output text:

*(Screenshot: "ACP is a very" split into tokens (sub-word fragments such as the root and suffix of a word), each mapped to an integer ID from the vocabulary.)*

**Stage 1: Tokenization**

Computers can't directly understand human text. So the first step is to convert our input "ACP is a very" into a numeric format the computer can process. This process is called **Tokenization**.

A token is the basic unit the tokenizer produces after encoding text; each token corresponds to an integer ID in the vocabulary. Note that **tokens are usually sub-word or character fragments** — not necessarily a complete "word," and not necessarily carrying standalone meaning. For example, an English word may be split into a root and a suffix, Chinese may be split by character or common phrase, and spaces and punctuation may also be encoded into tokens.

Taking "ACP is a very" as an example, the tokenizer encodes it into several tokens and assigns each an ID. If you're interested in Qwen's tokenization details, see its official docs: [Tokenization notes](https://github.com/QwenLM/Qwen/blob/main/tokenization_note_zh.md).

*(Figure: each token ID is looked up in an embedding table and converted into a high-dimensional vector that captures the token's meaning.)*

**Stage 2: Token vectorization**

Although we now have a sequence of numeric IDs, the numeric values of these IDs have no inherent meaning (e.g. ID 500 doesn't mean it's semantically "more important" or "more relevant" than ID 50). For the model to understand a token's true meaning, we need to convert these discrete IDs into a mathematical representation rich in semantic information — a **vector**.

This conversion is done through a huge table called the **Embedding matrix**. Simply put, you use the token ID to "look up" the corresponding row-vector in this big table. Each token's vector contains its coordinates in a multi-dimensional semantic space.

Moreover, word order is crucial ("I help you" and "you help me" are completely different). But the base Transformer model doesn't inherently process ordering. So we additionally add **positional encoding** to each token vector, letting the model distinguish that "I" is the first word, "you" is the third, and so on.

**Stage 3: LLM inference**

Now the vector sequence carrying semantic and positional information is fed into the Transformer's decoder blocks for computation. This process is called the forward pass.

The vector sequence passes layer by layer through dozens or even hundreds of similarly-structured decoder blocks. Under causal self-attention and feed-forward networks, the information in the text vectors is compressed and extracted again and again. We finally get the **hidden state** vector corresponding to the last token (i.e. "very"). This vector can be thought of as the model's highly condensed "summary of thoughts" about what might come next, after reading "ACP is a very." Finally, this "summary" vector is mapped through a linear projection layer to the dimension of the entire vocabulary, yielding a huge **score vector (logits)**.

**Stage 4: Decoding & autoregression**

After getting the logits, the LLM runs a softmax to remap these logits into a probability distribution $P(\text{next\_token} \mid \text{context})$, representing each token's probability of being chosen. Finally, the LLM decides which token to output based on a decoding strategy. **Decoding strategies** fall into two main categories:

- **Near-deterministic decoding**: e.g. greedy decoding (always pick the highest-probability token), or beam search (keep multiple candidate paths).
- **Stochastic sampling decoding**: e.g. Top-p (nucleus sampling), Top-k sampling — randomly draw from a high-probability candidate set.

Many online services use stochastic sampling by default, which is why "answers vary slightly" even when the input is identical.

By adjusting **temperature**, you change the "sharpness" of the softmax output distribution. Lower temperature → larger probability differences between tokens, distribution concentrated on a few high-probability tokens, more deterministic output. Higher temperature → flatter output distribution, more diverse output. Combined with **top_p** (which controls the range of the candidate set that participates in sampling), you can trade off between **diversity and stability**. You'll learn more about these parameters in the next subsection.

For example, the figure below shows some candidate tokens the model predicts and their probabilities (the actual vocabulary is far larger):

*Figure (translated): autoregressive decoding — each newly generated token is appended to the input and fed back in.*

```text
[Input: ACP is a very] -> [LLM] -> [Next token: informative]
       ^                              |
       └────────── append ────────────┘
```

Once the next token is chosen (say the model picks "informative"), this newly generated token is appended to the end of the original input sequence, forming the new input "ACP is a very informative." Then, based on this new sequence, the model repeats stages 3 and 4 to continue predicting the next token. This "word-chain" process is called **autoregressive generation**.

The model's autoregressive loop continues until a **stop condition** is met:
- A special **End-of-Sequence (EOS) token** is generated.
- The preset maximum generation length is reached.
- A user-specified stop-word sequence is generated.

Different model families use different EOS tokens.
<table>
<tr><th>Model</th><th>EOS token</th></tr>
<tr><td>Deepseek V3.2</td><td><｜end▁of▁sentence｜></td></tr>
<tr><td>GPT series</td><td><|endoftext|></td></tr>
<tr><td>GPT-OSS</td><td><|return|></td></tr>
<tr><td>LLaMA/Mistral</td><td> < /s> </td></tr>
<tr><td>Pad Token</td><td><|endoftext|></td></tr>
<tr><td>Qwen3</td><td><|im_end|></td></tr>
</table>

**Stage 5: Output text**

Finally, the system converts the token-ID sequence from the whole generation process back into a human-readable string and presents it to us.

The **streaming** effect we often see is actually the server decoding each one or few generated tokens and incrementally sending them to your interface. Because tokens may be sub-word fragments, in streaming display you sometimes see a word split into several parts, or spaces appearing at seemingly odd moments — all of which is normal.

### 2.2 Parameters affecting the randomness of LLM generation

Suppose in a Q&A scenario the user asks: "What can you learn in the LLM ACP course?" To simulate how the LLM generates content, we preset a candidate token set: "RAG", "prompt", "model", "writing", "drawing". The LLM will pick one of these 5 candidate tokens as the output (next-token), as shown below.
> User question: What can you learn in the LLM ACP course?<br><br>
> LLM answer: RAG <br>

In this process, two important parameters affect the LLM's output: temperature and top_p, which control the randomness and diversity of generated content. Below we introduce how these two parameters work and how to use them.

#### 2.2.1 temperature: reshaping the candidate token probability distribution

Before the LLM generates the next token (next-token), it first computes an initial probability distribution over the candidate tokens. This distribution represents each candidate token's probability of being the next-token. temperature is a regulator that reshapes the candidate token distribution to influence generation. By tuning this parameter, you can flexibly control the diversity and creativity of generated text.

For a more intuitive understanding, the figure below shows how different temperature values affect the candidate token distribution. The plotting code is under the /resources/2_1 directory.

*(Figure: responses at low / medium / high temperature (Qwen-Max range [0, 2)) — lower temperature gives focused, deterministic output; higher temperature gives more diverse, creative output.)*

The low/medium/high temperatures in the figure are divided based on Qwen-Max's range [0, 2).

As shown, as temperature goes from low to high (0.1 -> 0.7 -> 1.2), the distribution goes from steep to smooth, and the probability of candidate token "RAG" drops from 0.8 -> 0.6 -> 0.3. Although it's still the highest-probability token, it's now close to the other candidates, and the output goes from relatively fixed to gradually more diverse.

For different use cases, refer to these suggestions for setting temperature:
- Clear answers (e.g. code generation): lower the temperature.
- Creative variety (e.g. ad copy): raise the temperature.
- No special need: use the default temperature (usually the medium range).

Note that when temperature=0, randomness is minimized but identical output every time is not guaranteed. To dig deeper, see the [underlying algorithm implementation of temperature](https://github.com/huggingface/transformers/blob/v4.49.0/src/transformers/generation/logits_process.py#L226).

Below, experience temperature's effect. By adjusting the temperature value, ask the same question 10 times and observe the fluctuation in the answers.
> The temperature example code is similar to the top_p code discussed next, so we wrap it first for later reuse.

```python
import time

def get_qwen_stream_response(user_prompt, system_prompt, temperature, top_p):
    response = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature,
        top_p=top_p,
        stream=True
    )

    for chunk in response:
        yield chunk.choices[0].delta.content

# The defaults for temperature and top_p use Qwen-Max's default values
def print_qwen_stream_response(user_prompt, system_prompt, temperature=0.7, top_p=0.8, iterations=10):
    for i in range(iterations):
        print(f"Output {i + 1} : ", end="")
        ## add a delay to avoid rate limiting
        time.sleep(0.5)
        response = get_qwen_stream_response(user_prompt, system_prompt, temperature, top_p)
        output_content = ''
        for chunk in response:
            output_content += chunk
        print(output_content)

# Qwen-Max: temperature range is [0, 2), default 0.7
# Set temperature=0
print_qwen_stream_response(user_prompt="A horse can also be called", system_prompt="Please continue the text; keep it within 4 Chinese characters.", temperature=0)
```

```python
# Set temperature=1.9
print_qwen_stream_response(user_prompt="A horse can also be called", system_prompt="Please continue the text; keep it within 4 Chinese characters.", temperature=1.9)
```

From the experiment you can clearly see that the higher the temperature, the more varied and diverse the model's generated content.

#### 2.2.2 top_p: controlling the sampling range of the candidate token set

top_p is a filtering mechanism that selects a "small set" meeting a specific condition from the candidate token set. Specifically: sort tokens by probability from high to low, and take the tokens whose cumulative probability reaches the set threshold to form a new candidate set, thereby narrowing the selection range.

The figure below shows how different top_p values affect sampling of the candidate token set.

*(Figure: candidate tokens sorted by probability in descending order — the blue bars are the tokens whose cumulative probability reaches the `top_p` threshold (e.g., 0.5); only these are considered for sampling.)*

In the figure, the blue part represents tokens whose cumulative probability reaches the top_p threshold (e.g. 0.5 or 0.8) — they form the new candidate set; the gray part is the tokens not selected.

When top_p=0.5, the model prefers the highest-probability token, "RAG"; when top_p=0.8, the model randomly picks one of the three tokens "RAG", "prompt", "model" to generate.

From this, the effect of top_p on generation can be summarized as:
- Larger value: broader candidate range, more diverse content — suitable for creative writing, poetry generation, etc.
- Smaller value: narrower candidate range, more stable output — suitable for scenarios needing clear answers like news drafts and code generation.
- Extremely small value (e.g. 0.0001): in theory the model only picks the highest-probability token, giving very stable output. But in practice, subtle randomness from factors like distributed systems and post-processing of model output still means identical output every time isn't guaranteed.

Below, experience top_p's effect. By adjusting the top_p value, ask the same question 10 times and observe the fluctuation in the answers.

```python
# Qwen-Max: top_p range is (0,1], default 0.8.
# Set top_p=0.001
print_qwen_stream_response(user_prompt="Name a smart gaming phone; it could be", system_prompt="Please suggest a name, within 4 Chinese characters.", top_p=0.001)
```

```python
# Set top_p=0.8
print_qwen_stream_response(user_prompt="Name a smart gaming phone; it could be", system_prompt="Please suggest a name, within 4 Chinese characters.", top_p=0.8)
```

From the experiment results, you can see that the higher the top_p, the more random the LLM's output.

#### 2.2.3 Summary

**Do you need to adjust both temperature and top_p?**

To keep generation controllable, we recommend not adjusting top_p and temperature at the same time — doing so may make the output unpredictable. Prefer adjusting one parameter first, observe its effect on the results, then fine-tune gradually.

><br>**Knowledge extension: top_k**<br>
In Qwen-series models, the parameter top_k also controls randomness; see the [Qwen API docs](https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-by-calling-api). Its approach: the model first computes probabilities for the candidate tokens, keeps only the k highest-probability tokens, and excludes the rest from this sampling; then it rescales these k tokens' probabilities proportionally so they sum to 1 again, and samples from them. Generally, larger top_k = broader candidate range = more diverse content; smaller top_k = narrower range = more stable content. When top_k is set to 1, each step keeps only the highest-probability token, giving more deterministic but less varied/creative output.<br><br>
>**Knowledge extension: seed**<br>
In Qwen-series models, the parameter seed also supports controlling output determinism; see the [Qwen API docs](https://help.aliyun.com/zh/model-studio/developer-reference/use-qwen-by-calling-api). If you pass the same seed value on each model call and keep other parameters unchanged, the model will try its best to return the same result, but identical results every time can't be guaranteed.<br><br>

**Why is there still randomness even after setting temperature, top_p, and seed?**

Even with temperature set to 0, top_p set to an extremely small value (e.g. 0.0001), and the same seed, the generation for the same question may still be inconsistent. This is because some complex factors can introduce subtle randomness — for example, the LLM runs on a distributed system, or optimizations are applied to the model output.

For example:
A distributed system is like slicing bread on different machines. Even though every machine operates with the same settings, subtle differences between devices can still make the bread slices slightly different.

## ⚙️ 3. Enabling the LLM to Answer Private-Knowledge Questions

Back to the original challenge: the FAQ bot can't answer internal questions like "What project-management tool does our company use?" The root cause is that the LLM's knowledge comes from its training data, which is usually public internet information and **does not contain** any specific company's internal documents, policies, or processes.

You can picture the LLM as a brand-new supercomputer: its CPU (**reasoning ability**) is extremely powerful, and its hard drive (**model weights**) comes preloaded with vast general knowledge. But for your company's "internal materials," its hard drive is blank.

Facing this problem, the most intuitive solution is: at runtime, **temporarily** tell it the company's internal knowledge.

### 3.1 First attempt: "feeding" knowledge into the prompt

You can verify this idea: add the company's project-management-tool documentation directly into the model's instruction (System Prompt) as background knowledge.
> 💡 The company's project-management software information can be found in the file docs/Content Development Engineer Job Guide.pdf.

```python

user_question = "I'm in Software Team 1. What tool should I use for project management?"

knowledge = """The company has two project-management tool options:
  1. **Jira**: For software development teams, Jira is a powerful tool supporting agile methods like Scrum and Kanban. It offers rich features including issue tracking, time tracking, etc.

  2. **Microsoft Project**: For large enterprises or complex projects, Microsoft Project offers detailed planning, resource allocation, cost control, and more. It's better suited to scenarios needing strict control of project time and cost.

  In general, please use Microsoft Project; the company has purchased a full license. Software R&D Teams 1, 3, and 4 are currently using Jira, and plan to gradually switch to Microsoft Project before 2026.
"""

response = get_qwen_stream_response(
    user_prompt=user_question,
    # Pass the company project-management knowledge into the system prompt as background information
    system_prompt="You handle Q&A for an educational content development company. Your name is Company Assistant, and you answer learners' questions." + knowledge,
    temperature=0.7,
    top_p=0.8
)

for chunk in response:
    print(chunk, end="")
```

The experiment succeeded! By adding relevant background knowledge to the prompt, the LLM can indeed accurately answer questions about internal company tools. This finding is exciting — it seems you've found the key to private-knowledge Q&A.

However, when you try to "feed" more company documents this way (e.g. a dozens-of-pages employee handbook, hundreds of pages of technical specs), a new and more serious challenge appears.

### 3.2 The core bottleneck: the limited context window
<table>
<tr>
<td style="width: 70%; vertical-align: top; border: none;">
  <p>The place where the LLM receives our input (including instructions, questions, and background knowledge) is called the <b>context window</b>. You can think of it as the computer's "memory (RAM)" — its capacity is limited.</p>
  <p>You can't cram the entire company knowledge base (hundreds or thousands of documents) into this limited window at once. Once the input exceeds the model's maximum limit, it causes an error.</p>
  <p>This raises a core question: you need to <b>select and manage</b> what goes into the context window.</p>
</td>
<td style="width: 30%; border: none;">
  *Figure (translated): the RAG indexing pipeline.*

```text
[Documents] -> [Chunking (split into segments)] -> [Embedding model (text -> vectors)] -> (Vector database)
```
</td>
</tr>
</table>

### 3.3 The solution: Context Engineering

Bluntly cramming information into the context, besides exceeding the window limit, brings a series of "hidden" problems:

1.  **Low efficiency**: the longer the context, the longer the LLM takes to process, increasing user waiting time.
2.  **High cost**: most models bill by the amount of input and output text, so a long context means higher cost.
3.  **Information interference**: if the context contains lots of information irrelevant to the current question, it's like giving an exam-taker a textbook for the wrong subject during an open-book exam — it interferes with the model's judgment and degrades answer quality.

You'll surely realize that the key to success **is not how much knowledge you "feed" the model, but how precisely you feed it**.

How do you dynamically load the most relevant, most precise knowledge into the LLM's limited context window at the right time? — This systematic practice of designing, building, and optimizing the context is **Context Engineering**.

From this angle, **many LLM-application failures are not because the model isn't smart enough, but because of a failure of "context."** Context engineering is exactly the key to unlocking the LLM's potential.

So what techniques does context engineering include? You can quickly get the core map from the concept diagram below:

<table style="width: 100%;">
<tr>

  <td style="width: 70%; vertical-align: top; border: none; padding-right: 20px;">
    <h4>💡 Core techniques of Context Engineering</h4>
    <p>It is the sum of a series of key techniques for building reliable, efficient LLM applications, mainly including:</p>
    <ul>
      <li><strong>RAG (Retrieval-Augmented Generation)</strong>: <strong>retrieve</strong> information from an external knowledge base (e.g. company documents) to give the model an accurate basis for its answers.</li>
      <li><strong>Prompt (prompt engineering)</strong>: use carefully designed <strong>instructions</strong> to precisely guide the model's thinking and output format.</li>
      <li><strong>Tool (tool use)</strong>: give the model the ability to call external <strong>tools</strong> (calculator, search engine, API) to obtain real-time information or perform specific tasks.</li>
      <li><strong>Memory (memory mechanisms)</strong>: build short- and long-term <strong>memory</strong> for the model so it can understand historical context across a continuous conversation.</li>
    </ul>
  </td>

  <td style="width: 30%; vertical-align: top; border: none;">
    *Figure (translated): the RAG retrieval-and-generation pipeline.*

```text
[User question] -> [Embedding model] -> [Similarity search in vector DB] <- (Vector database)
                                          |
                                          v
                        [Top-k relevant chunks] -> [Prompt template] -> [LLM] -> [Answer]
```
  </td>
</tr>
</table>

You may have noticed some new terms here. Don't worry — you don't need to master every detail right away. The purpose of this diagram is to build an overall understanding: **the few topics you'll learn next are all part of context engineering**.

To make it easier to absorb, in later lessons these concepts will be broken down and practiced one by one as independent topics.

For now, focus on the most pressing problem — how to solve private-knowledge Q&A. In this technical map, **RAG** is the most direct and effective solution. Next, you'll learn it in depth.

### 3.4 The technical solution: RAG (Retrieval-Augmented Generation)

**RAG (Retrieval-Augmented Generation)** is a powerful technical solution for implementing context engineering. Its core idea:

When the user asks, instead of forcing the entire knowledge base onto the LLM, you first **automatically retrieve** the private knowledge fragments most relevant to the question, then merge these precise fragments with the user's question and pass them together to the LLM to **generate** the final answer. This avoids the overly-long-prompt problem while ensuring the LLM gets relevant background information.

Building a RAG application usually has two phases.

#### 3.4.1 Phase 1: Indexing
*(Figure: the context window holds a limited number of tokens — you must deliberately select and manage what goes into it.)*

Indexing converts private-knowledge documents or fragments into a form that can be retrieved efficiently. By splitting file content and converting it into multi-dimensional vectors (using a dedicated Embedding model), and combining with a vector store to preserve the text's semantic information, similarity computation becomes convenient. Vectorization lets the model efficiently retrieve and match relevant content — especially when handling large-scale knowledge bases, significantly improving query accuracy and response speed.

After being processed by the Embedding model, these vectors not only capture the text's semantic information well, but — because the semantics are vectorized and standardized — make it easy to later compute relevance against the query's semantic vector.

#### 3.4.2 Phase 2: Retrieval and generation
*(Figure: Context Engineering overview — systematically selecting and structuring what enters the context window, covering context window management, RAG, multi-turn conversation, and related techniques.)*

Retrieval and generation: based on the user's question, retrieve relevant document fragments from the index; these fragments are fed into the LLM together with the question to generate the final answer. This way the LLM can answer private-knowledge questions.

Overall, an application built on the RAG structure both avoids the various problems caused by feeding an entire reference document as background information, and extracts the parts most relevant to the question through retrieval — thereby improving the accuracy and relevance of the LLM's output.

## 📝 4. Section Summary
In this lesson, we learned:

- **How to use the LLM API**<br>
    Through hands-on code examples, we learned how to call the Qwen LLM via API, and how to use streaming output to improve the user experience.
- **How LLMs work and their limitations**<br>
    We took an initial look at the LLM's "black-box"-like workflow, understood why its answers are random, and learned how to control generation by adjusting parameters like temperature and top_p. More importantly, we confronted the LLM's core limitation: its knowledge depends entirely on training data and cannot know your company's internal documents and other private knowledge.
- **The core ideas of Context Engineering and RAG**<br>
    To solve the LLM's knowledge limitation, we first tried "feeding" knowledge directly into the prompt, but quickly hit the "context-window limit" bottleneck. This introduced a crucial concept — Context Engineering, the core methodology of intelligently selecting, organizing, and providing the most relevant background information for the LLM. As a concrete implementation of this idea, we learned the RAG (Retrieval-Augmented Generation) technical solution. Through the "retrieve first, then generate" pattern, RAG effectively combines precise external knowledge with the LLM, letting the model answer private-knowledge questions without exceeding limits.

Besides the task demonstrated in this lesson, you can have the LLM do many more kinds of tasks, such as content generation, structured information extraction, text classification, sentiment analysis, etc. And introducing a RAG solution into your LLM application can expand the range of knowledge the LLM can handle.

In the next subsection, we'll get hands-on and learn how to create a complete RAG application.

### Further reading
- While studying this course, if you want to understand more related concepts and principles, you can ask the LLM to expand further or give study suggestions:
> Qwen supports enabling the enable_search parameter, which lets the LLM use internet search results to enrich its replies when generating answers.

```python
completion = client.chat.completions.create(
    model="qwen-max",  # here qwen-max is used as an example; change the model name as needed. Model list: https://help.aliyun.com/zh/model-studio/getting-started/models
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "China's gold-medal count at the Paris Olympics"},
    ],
    extra_body={"enable_search": True},
)
print(completion.choices[0].message.content)
```

- Alibaba Cloud's reasoning model [Qwen3](https://help.aliyun.com/zh/model-studio/deep-thinking) has strong reasoning ability; the model first outputs its thinking process, then the answer.

```python
reasoning_content = ""  # the full thinking process
answer_content = ""     # the full reply
is_answering = False   # whether the thinking process has ended and the reply has started

# Create the chat completion request
completion = client.chat.completions.create(
    model="qwen3-235b-a22b-thinking-2507",  # here qwen3-235b-a22b-thinking-2507 is used as an example; change the model name as needed
    messages=[
        {"role": "user", "content": "Which is larger, 9.9 or 9.11?"}
    ],
    stream=True,
    # Uncommenting the following returns token usage in the last chunk
    # stream_options={
    #     "include_usage": True
    # }
)

print("\n" + "=" * 20 + "Thinking process" + "=" * 20 + "\n")

for chunk in completion:
    # If chunk.choices is empty, print usage
    if not chunk.choices:
        print("\nUsage:")
        print(chunk.usage)
    else:
        delta = chunk.choices[0].delta
        # Print the thinking process
        if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
            print(delta.reasoning_content, end='', flush=True)
            reasoning_content += delta.reasoning_content
        else:
            # Start the reply
            if delta.content != "" and is_answering is False:
                print("\n" + "=" * 20 + "Full reply" + "=" * 20 + "\n")
                is_answering = True
            # Print the reply
            print(delta.content, end='', flush=True)
            answer_content += delta.content
```

- If you're interested in multimodal LLMs, see:

    * [Vision understanding](https://help.aliyun.com/zh/model-studio/user-guide/vision)
    * [Audio understanding](https://help.aliyun.com/zh/model-studio/user-guide/audio-language-model)
    * [Omni (full-modal)](https://help.aliyun.com/zh/model-studio/user-guide/qwen-omni)
    * [Text-to-image](https://help.aliyun.com/zh/model-studio/user-guide/text-to-image)
    * [Video generation](https://help.aliyun.com/zh/model-studio/user-guide/video-generation)

## 🔥 Quiz

### 🔍 Single choice 2.1.1
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>After your FAQ bot launches, users report "every time I ask the same question, I get a different answer, and sometimes the content even contradicts itself." Investigation shows the current setup uses default parameters. What should you prioritize adjusting to reduce output randomness?❓</b>

- A. Lower temperature toward 0 so the model tends to pick the highest-probability tokens
- B. Raise top_p toward 1 to widen the candidate-token sampling range
- C. Append "please keep answers consistent" to the system prompt
- D. Switch to a model with more parameters, since larger models have more stable output

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: A**
📝 **Explanation**:
temperature controls the "sharpness" of the softmax output distribution. Lowering temperature concentrates probability on a few high-probability tokens, making output more deterministic and stable. Option B widens the sampling range, increasing randomness; option C's prompt constraint can't fundamentally change the random behavior of the sampling mechanism; in option D, model parameter count has no direct relation to output randomness.
</div>
</details>

### 📝 Case study 2.1.2
<details>
<summary style="cursor: pointer; padding: 12px;  border: 1px solid #dee2e6; border-radius: 6px; font-color:#000;">
<b>Xiaoming's writing assistant hits the following two scenarios. How should he solve them?❓</b>

- Scenario 🅰️ Content lacks creativity: every time the model writes an article about "the development of AI," the content is very similar.
- Scenario 🅱️ Content drifts off-topic: when the model writes a technical document, the content often includes irrelevant material.

**Questions:**
1. Based on the LLM workflow learned in this lesson, what might cause the problems in these two scenarios?
2. How should you adjust temperature or top_p to solve them?

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px;  padding: 15px;  border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

#### 🎯 Scenario A solution
**🔍 Cause analysis**
`temperature` too low (e.g. 0.3), so the model's choices are too single-minded and the content lacks diversity.

**⚙️ Parameter adjustment**
```python
temperature = 0.7~0.9  # boost creativity
top_p = 0.9            # widen the word-selection range
```

#### 🎯 Scenario B solution
**🔍 Cause analysis**
`temperature` too high (e.g. 1.2) or `top_p` too large

**⚙️ Parameter adjustment**
```python
temperature = 0.5~0.7  # reduce randomness
top_p = 0.7~0.8        # focus on high-probability words
```

> 🌟 **Tuning tip**
> Adjust by ±0.2 each time, and observe changes via A/B testing.
> If you need to balance Scenario A and Scenario B, a recommended combo is: `temperature=0.6` + `top_p=0.8`

</div>
</details>

### 🔍 Single choice 2.1.3
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>You're testing the FAQ bot's multi-turn conversation. The user first asks "What project-management tool does our company use?" and the bot answers Jira. The user then asks "How do I apply for an account?", but the bot gives a generic account-application process and never mentions Jira. What's the most likely cause?❓</b>

- A. The second call didn't put the prior conversation history into the messages array, so the model can't tell "account" refers to a Jira account
- B. In streaming mode the model can only process the current turn's input and can't read the earlier system prompt
- C. The model's context window is full, so it automatically dropped the first turn's assistant message containing the Jira info
- D. The LLM's temperature is too high, causing the model to "forget" the tool name mentioned earlier

**【Click to see the answer】**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: A**
📝 **Explanation**:
The LLM API is stateless; every call is independent. If the second call only passed "How do I apply for an account?", the model has no way to know which tool's account the user means. Option B is wrong — streaming only changes how content is displayed and doesn't affect how the model processes the messages array; option C is unlikely — two short turns won't come close to filling the context window; option D is wrong — temperature controls output randomness and wouldn't cause the model to "forget" information explicitly provided in the context.
</div>
</details>

### 🔍 Single choice 2.1.4
<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>You need the LLM to extract structured information from user feedback (e.g. product name, issue type, severity), and you require stable, consistent results each time. Which parameter setting is most reasonable?❓</b>

- A. temperature=1.5, top_p=0.9 — high-creativity setting, letting the model flexibly understand user phrasing
- B. temperature=0.1, top_p=0.3 — low-randomness setting, letting the model prefer the highest-probability tokens
- C. temperature=0.7, top_p=0.8 — default balanced setting, suitable for most general conversation
- D. temperature=0.1, top_p=0.95 — lower the temperature while widening the sampling range to balance stability and diversity

**【Click to see the answer】**
</summary>
<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference answer: B**
📝 **Explanation**:
Structured information extraction is a clear-answer task requiring highly stable output. Both temperature and top_p should be lowered so the model concentrates on high-probability tokens. Option A's high temperature introduces a lot of randomness; option C's default setting is general-purpose but still too random; option D adjusts the two parameters in opposite directions (low temperature but wide sampling range), which may make output behavior unpredictable — and the course advises against adjusting both parameters at once.
</div>
</details>

## ✅ Feedback
You're welcome to participate in the [Alibaba Cloud LLM ACP course survey](https://survey.aliyun.com/apps/zhiliao/Mo5O9vuie) to share your learning experience and course feedback.
Your criticism and encouragement are our motivation to keep improving!
