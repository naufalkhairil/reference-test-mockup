## 2.4 Automated evaluation of the Q&A bot's performance

### 🚄 Preface

The new Q&A bot may encounter some issues during real-world use, especially when users ask specific questions that require detailed knowledge from internal documents. For example, when a new employee asks, "How do I request leave?" the bot might provide a generic response instead of consulting the company’s official policy documents for accurate guidance.

Just as conventional software development requires testing and validation, it is equally important to establish an **evaluation system** for your Q&A bot project. This ensures that similar issues can be quickly identified and resolved. Moreover, after implementing any optimization or improvement, you should run a batch of test questions to confirm that the changes improve the overall performance of the Q&A bot.

In this chapter, you will learn how to **automate evaluation processes** using LLMs and specialized frameworks like **Ragas**, enabling you to measure both the quality of answers and the effectiveness of retrieval.

## 🍁 Goals
After completing this chapter, you will be able to:

- Understand how to automate evaluations for LLM applications.
- Evaluate RAG chatbots using automated tools such as Ragas.
- Identify and solve problems in your Q&A bot by analyzing evaluation scores.

<!-- ## 📖 Course Outline
In this chapter, we will first understand some current issues with RAG chatbot through a specific problem. Then, we will attempt to discover the issue by implementing a simple automated test ourselves. Finally, we will learn how to use the more mature RAG application testing framework, Ragas, to assess the performance of RAG chatbot.

- 1.&nbsp;Evaluating RAG Application Performance
    - 1.1 Issues with the Q&A robot
    - 1.2 Checking RAG retrieval results to troubleshoot issues
    - 1.3 Attempting to establish an automated testing mechanism

- 2.&nbsp;Using Ragas to Evaluate Application Performance
     - 2.1 Evaluating the quality of responses from the RAG chatbot
       - 2.1.1 Quick start
       - 2.1.2 Understanding How Answer Correctness Is Calculated
     - 2.2 Evaluating the recall effectiveness of retrieval
       - 2.2.1 Quick start
       - 2.2.2 Understanding the calculation process of context recall and context precision -->

## 1. Evaluating RAG application performance

### 1.1 Issues with the Q&A Bot

In the previous section, you completed the development of a Q&A bot and began exploring how to evaluate its performance.

```python
import os
from config.load_key import load_key, display_config_summary
load_key()
display_config_summary()
```

```python
from chatbot import rag
rag.indexing()
query_engine = rag.create_query_engine(rag.load_index())
print('Question: Which department is Michael Johnson in?')
response = query_engine.query('Which department is Michael Johnson in?')
print('Answer: ', end='')
response.print_response_stream()
```

As part of this exploration, you asked the question:

> **"Which department is Michael Johnson in?"**

And received the following answer from the bot:

> **"Michael Johnson is in the IT Infrastructure Department. He serves as a System Administrator, working under Michael Chen at the 456 Tech Hub."**

The original document contains multiple individuals named Michael Johnson, none of whom are associated with the **IT Infrastructure Department**. However, the LLM generated a confident and specific response that combined elements from different contexts — creating the illusion of accuracy without being grounded in factual data.

*(Screenshot: a Q&A example in which the bot's answer is not grounded in accurate context — illustrating hallucination caused by unreliable retrieval.)*

This highlights a critical issue: the answer was not based on accurate or unambiguous context, but rather on the model's aggregation or assumptions—potentially resulting in misleading conclusions.

Therefore, the next step is to examine the retrieval results used by the RAG system before generating the final answer, to ensure the context provided is accurate,  relevant, and aligned with the user's question.

### 1.2. Inspecting Retrieval Results for Diagnosis

To validate the reasoning behind the answer, we inspect the context chunks retrieved by the RAG system before generating the response.

Here is the retrieved context:

```python
contexts = [node.get_content() for node in response.source_nodes]
contexts
```

This context shows that Michael Johnson is indeed listed as a System Administrator in the Course Development Department, which  supports the generated answer.

✅ Conclusion: The retrieval performed well—relevant and sufficient information was retrieved to support the correct answer.

While this example shows good retrieval performance, not all queries will yield such clear results. Therefore, building an automated evaluation framework is essential for consistently measuring retrieval quality and answer accuracy across multiple test cases.

### 1.3 Implementing an Automated Evaluation Mechanism

Although manual inspection helps understand individual cases, it becomes impractical when dealing with hundreds or thousands of questions. Hence, we aim to build an automated testing mechanism to streamline the evaluation process.

#### 1.3.1 Validating answer quality using LLMs

LLMs can be used not only to generate answers but also to evaluate them. By providing both the question and the generated answer, we can prompt the LLM to determine whether the answer is valid or invalid based on the reference material.

Here is a function that checks if the answer effectively addresses the question:

```python
from chatbot import llm

def test_answer(question, answer):
    prompt = ("You are a tester.\n"
        "You need to check whether the following answer effectively responds to the user's question.\n"
        "The reply can only be: Valid response or Invalid response. Do not provide any other information.\n"
        "------"
        f"The answer is {answer}"
        "------"
        f"The question is: {question}"
    )
    return llm.invoke(prompt,model_name="qwen-max")

test_answer("Which department is Michael Johnson in?", "Michael Johnson is in the IT Infrastructure Department. He holds the position of System Administrator and works under the supervision of Michael Chen at the 456 Tech Hub.")
```

The LLM confirms that the answer is valid and correctly addresses the question.

#### 1.3.2 Validating context relevance

Equally important is ensuring that the retrieved context is relevant and useful for answering the question. To do this, we define another function to evaluate whether the context provided aligns with the user's query. This step helps ensure that the model is not only generating a plausible response but also basing it on accurate and contextually appropriate information.

This validation process strengthens the reliability of the Q&A bot by filtering out irrelevant or misleading content before the final answer is generated.

```python
def test_contexts(question, answer, contexts):
    prompt = (
        "You are a tester. Your task is to determine whether the provided reference materials directly support the given answer to the question.\n"
        "If the answer can be clearly found or derived from the reference materials, respond with: The reference information is useful.\n"
        "Otherwise, respond with: The reference information is not useful.\n"
        "Do not provide any other explanation or information.\n"
        "------\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n"
        f"Reference materials: {' '.join(contexts)}\n"
        "------"
    )
    return llm.invoke(prompt, model_name="qwen-max")
test_contexts(
    "Which department is Michael Johnson in?", 
    "Michael Johnson is in the IT Infrastructure Department. He holds the position of System Administrator and works under the supervision of Michael Chen at the 456 Tech Hub.", 
    contexts
    )
```

#### 1.3.3 Summary of evaluation logic

| Component         | Method                           | Result                |
|------------------|----------------------------------|------------------------|
| Question          | "Which department is Michael Johnson in?" |                        |
| Generated Answer  | Evaluated using `test_answer`     | Valid response         |
| Retrieved Context | Evaluated using `test_contexts`   | Reference info is useful |

With the two methods above, you've already taken the first steps in setting up a prototype for an LLM testing project. However, the current implementation is still incomplete and has several limitations:

- **Hallucination Detection:** LLMs can generate responses that sound confident and plausible but are not factually accurate. The `test_answer` method, as currently implemented, may not be able to effectively detect such hallucinations, leading to false positives in evaluation.
- **Relevance of retrieved context:** The quality of a RAG-based system heavily depends on the relevance and accuracy of the retrieved context. A higher signal-to-noise ratio—meaning more relevant information and less irrelevant or misleading content—leads to better answers. However, the current testing approach is relatively simplistic and does not account for this critical factor.

To address these issues and improve the robustness of your testing framework, it’s highly recommended to integrate mature evaluation tools such as [Ragas](https://docs.ragas.io/en/stable), a specialized framework designed for evaluating the performance of RAG-based chatbots.

## 2. Using Ragas to evaluate application performance

Ragas offers a comprehensive set of metrics to assess the quality of question-answering across the entire application pipeline. These metrics help ensure that both the retrieval and generation phases of a RAG (Retrieval-Augmented Generation) system perform effectively.

Ragas provides the following key evaluation metrics:
* Overall response quality
    * Answer correctness: Measures how accurate the generated answers are in relation to the actual knowledge in the dataset.
* Generation phase evaluation
    * Answer Relevance: Evaluates whether the generated answer is relevant to the user’s question.
    * Faithfulness: Checks if the answer is factually consistent with the retrieved reference materials, ensuring it doesn’t introduce incorrect or fabricated information.
* Retrieval phase evaluation
    * Context precision: Assesses whether the retrieved context contains a high proportion of relevant information related to the correct answer.
    * Context recall: Measures how many of the relevant reference materials are successfully retrieved; a higher score indicates fewer relevant documents are missed.
These metrics provide a structured way to evaluate and improve the performance of your Q&A bot, ensuring that it delivers accurate, relevant, and well-supported responses.

### 2.1 Evaluating the response quality of RAG applications

#### 2.1.1 Quick start  

When evaluating the overall response quality of a RAG chatbot, using Ragas' Answer Correctness is an excellent metric. To calculate this metric, you need to prepare the following two types of data to evaluate the quality of the answer generated by the RAG chatbot:

1. question (The question input to the RAG chatbot)
2. ground_truth (The correct answer you already know)

To illustrate the differences in evaluation metrics for different responses, we have prepared three sets of RAG chatbot responses to the question:

**Question:**  
"Which department does Michael Johnson belong to?"

We will compare each model-generated **answer** against the known **ground truth**.

Three sample answers are provided below, each representing a different level of correctness:

- **Answer 1:** Based on the provided information, there is no mention of the department Michael Johnson belongs to. If you can provide more information about Michael Johnson, I may be able to help you find the answer.  
  ➤ This is considered an **invalid answer**, as it fails to provide the correct response even when context may have been available.

- **Answer 2:** Michael Johnson belongs to the Human Resources Department.  
  ➤ This is a **hallucinated answer**, as it provides a confident but incorrect response.

- **Answer 3:** Michael Johnson belongs to the Course Development Department.  
  ➤ This is the **correct answer**, matching the ground truth exactly.                                         |

We can then run the following code to calculate the score for response accuracy (i.e., Answer Correctness) using Ragas:

```python
import os
from datasets import Dataset

from ragas.evaluation import evaluate
from ragas.metrics import answer_correctness

from langchain_openai import ChatOpenAI
from chatbot.evaluate import RagasOpenAICompatibleEmbeddings

# 1. Prepare dataset (simple form)
data_samples = {
    "question": [
        "Which department is Michael Johnson in?",
        "Which department is Michael Johnson in?",
        "Which department is Michael Johnson in?",
    ],
    "answer": [
        "According to the provided information, there is no mention of the department where Michael Johnson works. If you can provide more information about Michael Johnson, I may be able to help you find the answer.",
        "Michael Johnson is in the HR department",
        "Michael Johnson is in the Course Development Department",
    ],
    "ground_truth": [
        "Michael Johnson is a member of the Course Development Department",
        "Michael Johnson is a member of the Course Development Department",
        "Michael Johnson is a member of the Course Development Department",
    ],
}
dataset = Dataset.from_dict(data_samples)

# 2. Call ragas.evaluate with answer_correctness only
score = evaluate(
    dataset=dataset,
    metrics=[answer_correctness],
    llm=ChatOpenAI(model="qwen-plus",base_url=os.getenv("DASHSCOPE_API_BASE"),api_key=os.getenv("DASHSCOPE_API_KEY")),
    embeddings=RagasOpenAICompatibleEmbeddings(model="text-embedding-v3",base_url=os.getenv("DASHSCOPE_API_BASE"),api_key=os.getenv("DASHSCOPE_API_KEY")),
)

score.to_pandas()
```

This code will generate a score that reflects how well each model-generated answer aligns with the known correct answer. By comparing the scores across different responses, you can identify which answers are accurate, which are incorrect, and which may be hallucinated.

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>question</th>
      <th>answer</th>
      <th>ground_truth</th>
      <th>answer_correctness</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Which department does Michael Johnson belong to?</td>
      <td>According to the provided information, there is no mention of the department where Michael Johnson works. If you can provide more information about Michael Johnson, I may be able to help you find the answer.</td>
      <td>Michael Johnson is a member of the Course Development Department</td>
      <td>0.168191</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Which department does Michael Johnson belong to?</td>
      <td>Michael Johnson belongs to the Human Resources Department.</td>
      <td>Michael Johnson is a member of the Course Development Department</td>
      <td>0.196047</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Which department does Michael Johnson belong to?</td>
      <td>Michael Johnson is in the Course Development Department</td>
      <td>Michael Johnson is a member of the Course Development Department</td>
      <td>0.998264
</td>
    </tr>
  </tbody>
</table>
</div>

As you can see, Ragas' Answer Correctness metric accurately reflects the performance of the three responses, with the more factually accurate answers receiving higher scores.

#### 2.1.2 Understanding How Answer Correctness Is Calculated

The scoring of Answer Correctness aligns with your expectations. The scoring process involves using an LLM (in the code `llm=Tongyi(model_name="qwen-plus"))` and an embedding model (in the code `embeddings=DashScopeEmbeddings(model="text-embedding-v3"))` to calculate the result based on  **semantic similarity** and **factual accuracy** between the answer and the ground truth.

##### Semantic similarity
Semantic similarity is determined by generating text vectors for both the answer and the ground truth using the embedding model. These vectors are then compared using methods like cosine similarity, which is the most commonly used in Ragas, along with Euclidean distance and Manhattan distance. 

##### Factual accuracy

Factual accuracy measures the consistency of factual information between the answer and the ground truth. For example:

* answer: Michael Johnson is a colleague in the Course Development Department responsible for big data direction.
* ground_truth: Michael Johnson is a colleague in the Course Development Department responsible for technical writer tasks.

While both statements agree on the department (Course Development), they differ in the job role (big data direction versus technical writer tasks). Such differences are not easily captured through simple LLM or embedding model calls.

To address this, Ragas uses an LLM to generate lists of assertions for both the answer and the ground truth, then compares these lists to identify matching and conflicting facts, allowing for a more nuanced evaluation of factual accuracy.

The following diagram illustrates how Ragas evaluates factual accuracy:

*Figure (translated): assertion-based evaluation — an LLM turns both the answer and the ground truth into assertion lists, which are then compared to produce a score.*

```text
[Generated answer] -> [LLM produces assertion list] ────┐
                                                         ├──► [Compare assertion sets] ──► [Verdict + score]
[Ground truth]     -> [LLM produces assertion list] ────┘
```

1. Generate respective lists of assertions for the answer and ground truth using a LLMs. For example:
    - **Generate the assertion list for the answer**: Michael Johnson is a colleague in the Course Development Department responsible for big data direction. ---> ["*Michael Johnson is in the Course Development Department*", "*Michael Johnson is responsible for big data direction*"]
    - **Generate the assertion list for ground_truth**: Michael Johnson is a colleague in the Course Development Department responsible for technical writer tasks. ---> ["*Michael Johnson is in the Course Development Department*", "*Michael Johnson is responsible for technical writer tasks*"]

2. Traverse the assertion lists for the answer and ground_truth, initializing three lists: TP, FP, and FN.
    - For the assertions generated from the **answer**:
      - If the assertion matches one from the ground_truth, add it to the TP list. For example: "*Michael Johnson is in the Course Development Department*".
      - If the assertion cannot be found in the ground_truth list, add it to the FP list. For example: "*Michael Johnson is responsible for big data direction*".
    - For the assertions generated from the **ground_truth**:
      - If the assertion cannot be found in the answer list, add it to the FN list. For example: "*Michael Johnson is responsible for technical writer tasks*".
      > The judgment process in this step is entirely provided by a LLM.

3. Count the number of elements in the TP, FP, and FN lists, and calculate the F1 score as follows:

```shell
f1 score = tp / (tp + 0.5 * (fp + fn)) if tp > 0 else 0
```

Using the example above (where TP=1, FP=1, FN=1), the calculation is: f1_score = 1 / (1 + 0.5 * (1 + 1)) = 0.5

##### Final Score Calculation
After obtaining the scores for semantic similarity and factual accuracy, a weighted sum of the two can be calculated to obtain the final Answer Correctness score:

```
Answer Correctness score = 0.25 * Semantic Similarity score + 0.75 * Factual Accuracy score
```

### 2.2 Evaluating the response quality of RAG applications

#### 2.2.1 Quick start

The context precision and context recall metrics in Ragas are used to evaluate the effectiveness of retrieval recall in RAG (Retrieval-Augmented Generation) applications.

* Context Precision: Measures whether the relevant information from the retrieved context is ranked highly and makes up a large proportion (signal-to-noise ratio). It focuses on relevance.
* Context Recall: Assesses how well the retrieved context aligns with the ground truth, ensuring that important factual information is not missed. It focuses on factual accuracy.

In practical applications, these two metrics are often used together to provide a more comprehensive evaluation of the retrieval process.

To calculate these metrics, your dataset should include the following:

* question: The question input to the RAG application.
* contexts: The retrieved reference information.
* ground_truth: The correct answer you already know.

You can continue using the question "Which department is Michael Johnson from?" and prepare three sets of data for testing. Run the following code to calculate both context precision and context recall scores simultaneously:

```python
import os
from datasets import Dataset

from ragas.evaluation import evaluate
from ragas.metrics import context_recall, context_precision

from langchain_openai import ChatOpenAI
from chatbot.evaluate import RagasOpenAICompatibleEmbeddings

# 1. Prepare dataset (simple form)
data_samples = {
    'question': [
        'Which department is Michael Johnson in?',
        'Which department is Michael Johnson in?',
        'Which department is Michael Johnson in?'
    ],
    'answer': [
        'Based on the provided information, there is no mention of the department where Michael Johnson works. If you can provide more information about Michael Johnson, I may be able to help you find the answer.',
        'Michael Johnson is in the HR department',
        'Michael Johnson is in the Course Development Department'
    ],
    'ground_truth': [
        'Michael Johnson is a member of the Course Development Department',
        'Michael Johnson is a member of the Course Development Department',
        'Michael Johnson is a member of the Course Development Department'
    ],
    'contexts': [
        ['Provides administrative management and coordination support, optimizing administrative workflows.', 'Performance Management Department Robert Carter EID-701 IT Infrastructure Department'],
        ['Michael Chen, Director of the IT Infrastructure Department', 'Newton discovered the law of universal gravitation'],
        ['Newton discovered the law of universal gravitation', 'Michael Johnson, engineer in the Course Development Department, has recently been responsible for technical writer tasks.'],
    ],
}
dataset = Dataset.from_dict(data_samples)

# 2. Call ragas.evaluate with answer_correctness only
score = evaluate(
    dataset=dataset,
    metrics=[context_recall, context_precision],
    llm=ChatOpenAI(
        model="qwen-plus",
        base_url=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    ),
    embeddings=RagasOpenAICompatibleEmbeddings(
        model="text-embedding-v3",
        base_url=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    ),
)

score.to_pandas()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>question</th>
      <th>answer</th>
      <th>ground_truth</th>
      <th>contexts</th>
      <th>context_recall</th>
      <th>context_precision</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Which department is Michael Johnson in?</td>
      <td>Based on the provided information, there is no mention of the department where Michael Johnson works. If you can provide more information about Michael Johnson, I may be able to help you find the answer.</td>
      <td>Michael Johnson is a member of the Course Development Department.</td>
      <td>[Provides administrative management and coordination support, optimizing administrative workflows., Performance Management Department Robert Carter EID-701 Course Development Department]</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Which department is Michael Johnson in?</td>
      <td>Michael Johnson is in the HR department</td>
      <td>Michael Johnson is a member of the Course Development Department.</td>
      <td>[Michael Chen, Director of the Course Development Department, Newton discovered the law of universal gravitation]</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Which department is Michael Johnson in?</td>
      <td>Michael Johnson is in the Course Development Department</td>
      <td>Michael Johnson is a member of the Course Development Department.</td>
      <td>[Newton discovered the law of universal gravitation, Michael Johnson, engineer in the Course Development Department, has recently been responsible for curriculum development]</td>
      <td>1.0</td>
      <td>0.5</td>
    </tr>
  </tbody>
</table>
</div>

From the data above, we can see that:
- The answer in the last row of data is accurate.
- In the final row, the contexts successfully retrieve the key information, "Michael Johnson, engineer in the Course Development Department," which fully supports the ground_truth. This is why its context_recall score is 1.0. In contrast, the first two rows fail to retrieve this information, resulting in a context_recall score of 0.0.
- However, not every piece of information in the contexts is relevant to the question and answer. For example, "Newton discovered gravity." This situation is reflected in the context precision score being 0.5.

#### 2.2.2 Understanding the calculation process of context recall and context precision

##### Context recall

As you've learned, context recall is a metric used to measure whether retrieved contexts are consistent with the ground truth.

In Ragas, context recall evaluates what proportion of viewpoints in the ground truth can be supported by the retrieved contexts. The calculation process is as follows:

1. An LLM breaks down the ground truth into a list of statements.
   > For example, from the ground truth "Michael Johnson is a member of the Course Development Department," the LLM might generate a list of statements such as ["Michael Johnson belongs to the Course Development Department"]..
2. The LLM determines whether each statement can find supporting evidence in the retrieved referencecontexts.
   > For instance, this statement can find supporting evidence in the third row of data's contexts: "Michael Johnson, engineer in the Course Development Department, has recently been responsible for curriculum development."
3. The context recall score is calculated as the proportion of statements in the ground truth list that are supported by the contexts.
   > In this case, the score is 1 = 1/1, meaning all statements are supported.

##### Context precision

Context precision in Ragas not only measures what proportion of the retrieved contexts are relevant to the ground truth but also evaluates the ranking of those contexts. The calculation process is more complex:

1. Each context is evaluated sequentially based on whether it is relevant to the question and ground truth.
   * If relevant, it scores 1; otherwise, it scores 0.
   * For example, in the third row of data:
      * Context 1: "Newton discovered gravity" → irrelevant → score 0
      * Context 2: "Michael Johnson, engineer in the Course Development Department, has recently been responsible for curriculum development." → relevant → score 1

2. For each context, the precision score is calculated by dividing the cumulative sum of scores of the current context and all preceding contexts by its position in the sequence .
    * For the third row of data:
        * Context 1 : 0/1 = 0
        * Context 2 : 1/2 = 0.5

3. The context precision score is obtained by summing up the precision scores of all contexts and dividing by the number of relevant contexts.
    * For the third row of data: context_precision = (0 + 0.5) / 1 = 0.5

> If you're still unclear about the calculation process, don’t worry—the key takeaway is that context precision evaluates how well the retrieval system ranks relevant contexts higher than irrelevant ones.
If you’re interested, we encourage you to explore [Ragas's source code](https://github.com/explodinggradients/ragas/blob/cc31f65d4b7c7cd6bbf686b9073a0dfaacfbcbc5/src/ragas/metrics/_context_precision.py#L250) for a deeper understanding of how these metrics are implemented.

### 2.3 Other recommended metrics to explore

Ragas provides many other evaluation metrics, which are not introduced one by one here. You can visit the Ragas documentation to learn more about their use cases and working principles.

The list of metrics supported by Ragas can be found at: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/

## 3. How to optimize based on ragas metrics

The ultimate goal of evaluation is not just to obtain scores, but to identify areas for improvement based on these scores. You are now familiar with the concepts behind three key metrics: answer_correctness, context_recall, and context_precision.

When you observe that certain metrics have low scores, you should take action to improve them. Below are some optimization strategies based on specific metrics:

### 3.1 Context is the lifeline of RAG

When a user asks a question, the LLM provides an answer by reading and comprehending the **Context** you provide. The context determines whether the LLM can give an accurate and complete answer. If the context is missing key knowledge points, or contains incorrect or irrelevant content, the LLM will be unable to draw correct conclusions. As seen in the previous example: if the context lacks information about "**Michael Johnson's department**," the LLM naturally cannot provide the correct answer.

To avoid losing effective knowledge, some suggest "cramming everything into the LLM" and letting it figure it out. However, this creates a more complex problem: even if a key clue exists within a large volume of data, the LLM may "overlook" it if it is buried in a sea of irrelevant information. This is known as the "**Lost in the Middle**" phenomenon in RAG systems. Imagine the information about "**Michael Johnson's department**" is a simple sentence: "**Michael Johnson, the Course Development Department, ID XXXX**." If this sentence is sandwiched between hundreds of pages of attendance records, meeting minutes, or even the company cafeteria menu, the LLM is likely to get lost in the redundancy. Its "attention" is scattered, and the key information is "drowned out."

*(Figure: the RAG accuracy bottleneck usually lies in the retrieved knowledge, not in how "smart" the LLM is.)*

Therefore, the bottleneck of RAG accuracy often lies not in whether the LLM is "smart" enough, but in the "**Knowledge Concentration**" of the context provided. A high-quality context should have high knowledge density, meaning the relevant information is concentrated, noise is minimized, and it is directly related to the question. This allows the LLM to focus accurately on the core of the problem. Thus, the quality of the context you provide directly determines the upper limit of your RAG system.

In Ragas, **Context Recall** and **Context Precision** are used to measure the effectiveness of the retrieved context. By analyzing these two metrics, you can determine if the **quality of the retrieved context** in your RAG system has improved.

### 3.2 Context recall
This metric evaluates the **retrieval** phase of your RAG application. A low context recall score indicates that the retrieved contexts do not cover enough relevant information from the ground truth.If this metric has a low score, you can try optimizing from the following aspects:

- **Check the Knowledge Base**

    *(Figure: query rewriting — reformulating the user's question so it better matches the knowledge base.)*

    The knowledge base is the source of a RAG application. If the content within it is incomplete or insufficient, it can lead to inadequate reference information being retrieved, which directly impacts context recall—the ability of the system to retrieve relevant information that supports accurate and meaningful answers.

    To ensure the knowledge base is comprehensive and effective, you can:

    * Compare the knowledge base content with test samples to verify whether the information in the knowledge base is sufficient to support each query.
    * Use LLMs to assist in this process: By prompting the model to evaluate whether the knowledge base contains the necessary information to answer a given question, you can identify gaps or inconsistencies.

    If you find that some test samples lack relevant information in the knowledge base, it’s essential to supplement the knowledge base with additional data. This ensures that the RAG system has access to the most accurate and complete information, improving both retrieval quality and answer reliability.

- **Replace the Embedding Model**

    *(Figure: swapping in a stronger embedding model to improve retrieval quality.)*

    If your knowledge base content is already comprehensive and well-structured,  it may be beneficial to replace the embedding model used for vectorization. A high-quality embedding model can better capture the deep semantic meaning of text, allowing for more accurate and meaningful similarity comparisons between queries and retrieved content.

For example, consider the following:
* Question: "Who is responsible for curriculum development?"
* Relevant Knowledge Base Text: "Michael Johnson is a member of the Course Development Department."

Even though the two sentences don’t share many surface-level words, a strong embedding model can recognize the semantic relationship between them—understanding that "responsible for curriculum development" and "member of the Course Development Department" are closely related in meaning.

- **query rewriting**

    *(Figure: optimizing the knowledge base — check that its content is complete and accurate before touching other components.)*

    As a developer, it's unrealistic to expect users to phrase their questions in a specific or detailed way. Therefore, you might receive vague or ambiguous queries such as: "Course Development Department," "Leave Request," or "Project Management." If these questions are directly input into a RAG application, they are unlikely to retrieve relevant and effective text segments. To address this, you can design a prompt template by organizing common employee questions and use LLMs to rewrite the queries, improving the accuracy of the retrieval process.

### 3.3 Context Precision
Similar to context recall, the context precision metric  evaluates the performance of a RAG application during the **retrieval** phase, but it focuses more on whether the most relevant text segments are ranked highly. A low context precision score suggests that while some relevant information may be retrieved, it is mixed with irrelevant or less important content, reducing the effectiveness of the retrieval.

If this metric has a low score, you can apply the same optimization measures used for context recall, such as improving the knowledge base or refining the retrieval algorithm. Additionally, you can implement **reranking** during the retrieval phase to improve the ranking of related text segments and ensure that the most relevant information appears first.

### 3.4 Answer Correctness
The answer correctness metric evaluates the overall comprehensive performance of a RAG system. If this metric has a low score while the previous two metrics have high scores, it indicates that the RAG system performs well in the **retrieval** phase but encounters issues in the **generation** phase. You can try the methods learned in previous tutorials, such as optimizing prompts, adjusting hyperparameters (such as temperature) of LLMs generation, or replacing with a more powerful LLM, and even fine-tuning the LLM (which will be introduced in later tutorials) to enhance the accuracy of generated answers.

## 4. Building a World-Class Evaluation Operations System

While automated evaluation can effectively improve evaluation efficiency, the bigger challenge lies in **building high-quality evaluation datasets** and **accumulating deep domain knowledge**. Therefore, you need to establish a comprehensive evaluation operations system tailored to your business characteristics.

### 4.1 Building a High-Quality Evaluation Dataset

The effectiveness of automated evaluation depends entirely on the quality of the evaluation dataset. A good evaluation dataset should **reflect real business needs**, not problems imagined by technical staff.

**Where do the questions in the evaluation dataset come from?**

Questions in the evaluation dataset should come from **real user scenarios**:

- **User question sampling**: Collect actual questions from users in production systems, sampled by frequency and type
- **User tickets/feedback**: Tickets, complaints, and feedback submitted by users in customer service systems often represent the pain points users care about most
- **Business scenario coverage**: Ensure questions cover major business scenarios, including high-frequency questions and edge cases

**Where does the Ground Truth come from?**

The ground truth in the evaluation dataset must be provided by **domain experts**:

- **Why domain experts?** Only domain experts know "what answers are correct, good, and compliant with business standards"
- **Limitations of technical staff**: Technical staff can judge "whether the system retrieved relevant content," but cannot judge "whether the answer is correct, complete, and compliant from a business perspective"

> **Key insight**: Because the questions come from real users and the answers come from domain experts, automated evaluation results can reflect real business performance.

### 4.2 Evaluation-First Optimization Strategy

In LLM application development, **evaluation should come before optimization**, not "optimize first, then evaluate to see the results."

<div align="center">
    *Figure (translated): evaluation-first optimization strategy.*

```text
[Run evaluation metrics] -> [Diagnose the weak component] -> [Optimize (KB / embedding / query rewriting)]
       ^                                                                                       |
       └───────────────────────────────────────────────────────────────────────────────────────┘
```
    <p><em>Figure: Evaluation-First Optimization Strategy</em></p>
</div>

| Phase | Key Action | Responsible Party |
|-------|-----------|-------------------|
| Define business goals | Define quantifiable business metrics (e.g., satisfaction > 90%) | Business/Product |
| Build evaluation dataset | Sample from user questions, experts write answers | Domain Experts |
| Establish automated evaluation | Configure evaluation framework, obtain baseline scores | Technical + Business |
| Targeted optimization | Identify issues based on metrics, implement optimizations | Technical + Business |
| Evaluation verification | Compare results before and after optimization | Technical + Business |
| Continuous iteration | Track intent changes, update evaluation dataset | Domain Experts |

**Why "evaluation first"?**
- **Avoid blind optimization**: Without an evaluation baseline, you don't know if optimization is actually effective
- **Quantify improvement**: From "feels better" to "metrics improved by 15%"
- **Prevent seesaw effect**: One optimization may cause regression elsewhere; evaluation reveals overall improvement

### 4.3 Aligning Business Metrics with Evaluation Metrics

Ragas provides **algorithm metrics** like Context Recall, Context Precision, and Answer Correctness, but what we ultimately care about are **business metrics**. Understanding the relationship between them enables evaluation to truly serve business goals.

| Level | Example Metrics | Description |
|-------|----------------|-------------|
| **Business Metrics** | User Q&A satisfaction > 90% | Ultimate goal, measures business value |
| **Core Technical Metrics** | Recall accuracy > 85%, response time < 2s | Decomposed from business metrics, engineering measurable |
| **Algorithm Metrics** | Context Precision, Answer Correctness | Automated evaluation, fast iteration verification |

> **Core principle**: Algorithm metrics are the means; business metrics are the goal. Don't optimize to improve Context Recall—optimize to improve user satisfaction.

### 4.4 Continuous Operations of the Evaluation System

Start with "**find the people who know the business best, use scientific methods, and deeply involve them in evaluation**":

- **Involve domain experts in AI evaluation**: For example, have e-commerce customer service managers evaluate promotional rule response accuracy, have logistics specialists evaluate shipping time accuracy
- **Start from the end-user perspective**: Judge answer correctness, conciseness, and actionability from the user's point of view
- **Establish a closed-loop mechanism**: "Identify issues → Optimize → Track results → Iterate metrics"—let evaluation continuously drive business system improvement

The diagram below shows a complete evaluation operations system architecture:

<div align="center">
    *(Figure: architecture of an evaluation-operations system — automated evaluation pipelines wired into the daily operation of the RAG application.)*
    <p><em>Figure: Evaluation Operations System Architecture Diagram</em></p>
</div>

## ✅ Summary

Through the study of this section, you have learned how to establish automated testing for RAG chatbots.

Automated testing is a crucial tool for engineering optimization. With quantified metrics, it  helps you move from intuitive improvements to data-driven evaluations, ensuring that your RAG chatbot performs better after each enhancement. This not only allows you to evaluate the question-answering quality more efficiently and identify areas for improvement but also enables you to quantify the results of your optimizations.

While automated testing is powerful, it does not eliminate the need for human evaluation entirely. In practical applications, it is recommended to involve domain experts who can help build a test set that reflects real-world scenarios. These experts can ensure the test set covers a wide range of typical queries and edge cases, and it should be continuously updated to reflect evolving needs.

Additionally, since LLMs are not always 100% accurate, it’s advisable to regularly sample and review the results of automated testing in real-world use. Avoid frequently changing the LLM or embedding models unless necessary, as this can introduce instability. For Ragas, you can improve its performance by adjusting the default prompts—for example, by adding domain-specific reference examples that align with your business context. (For more details, refer to the extended reading materials.)

## Further Reading

### Changing the Prompt Template in Ragas
Many of Ragas’ evaluation metrics rely on large language models to compute scores. Like LlamaIndex, Ragas provides default prompt templates, but it also supports custom prompts that you can modify to suit your specific use case.
Example prompt templates are included in the `ragas_prompt` folder to help you customize the prompts used by Ragas for different evaluation metrics. You can refer to the following code to integrate these updated prompts into your workflow.

> Note: Ragas includes example cases in its prompts to guide the model on how to make judgments or generate lists of statements. You can replace or modify these examples to better align with your specific domain or use case.

```python
import os
from datasets import Dataset

from ragas.evaluation import evaluate
from langchain_openai import ChatOpenAI
from chatbot.evaluate import RagasOpenAICompatibleEmbeddings
# Import prompt templates
from ragas_prompt.ragas_test_prompt import ContextRecall, ContextPrecision, AnswerCorrectness

# Customize prompt settings for each metric
context_recall.context_recall_prompt.instruction = ContextRecall.context_recall_prompt["instruction"]
context_recall.context_recall_prompt.output_format_instruction = ContextRecall.context_recall_prompt["output_format_instruction"]
context_recall.context_recall_prompt.examples = ContextRecall.context_recall_prompt["examples"]

context_precision.context_precision_prompt.instruction = ContextPrecision.context_precision_prompt["instruction"]
context_precision.context_precision_prompt.output_format_instruction = ContextPrecision.context_precision_prompt["output_format_instruction"]
context_precision.context_precision_prompt.examples = ContextPrecision.context_precision_prompt["examples"]

answer_correctness.correctness_prompt.instruction = AnswerCorrectness.correctness_prompt["instruction"]
answer_correctness.correctness_prompt.output_format_instruction = AnswerCorrectness.correctness_prompt["output_format_instruction"]
answer_correctness.correctness_prompt.examples = AnswerCorrectness.correctness_prompt["examples"]

# 1. Prepare dataset (simple form)
data_samples = {
    'question': [
        'Which department is Michael Johnson in?',
        'Which department is Michael Johnson in?',
        'Which department is Michael Johnson in?'
    ],
    'answer': [
        'Based on the provided information, there is no mention of the department where Michael Johnson works. If you can provide more information about Michael Johnson, I may be able to help you find the answer.',
        'Michael Johnson is in the HR department',
        'Michael Johnson is in the Course Development Department'
    ],
    'ground_truth': [
        'Michael Johnson is a member of the Course Development Department',
        'Michael Johnson is a member of the Course Development Department',
        'Michael Johnson is a member of the Course Development Department'
    ],
    'contexts': [
        ['Provides administrative management and coordination support, optimizing administrative workflows.', 'Performance Management Department Robert Carter EID-701 IT Infrastructure Department'],
        ['Michael Chen, Director of the IT Infrastructure Department', 'Newton discovered the law of universal gravitation'],
        ['Newton discovered the law of universal gravitation', 'Michael Johnson, engineer in the Course Development Department, has recently been responsible for technical writer tasks.'],
    ],
}
dataset = Dataset.from_dict(data_samples)

# 2. Call ragas.evaluate with answer_correctness only
score = evaluate(
    dataset=dataset,
    metrics=[answer_correctness, context_recall, context_precision],
    llm=ChatOpenAI(
        model="qwen-plus",
        base_url=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    ),
    embeddings=RagasOpenAICompatibleEmbeddings(
        model="text-embedding-v3",
        base_url=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    ),
)

score.to_pandas()
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>question</th>
      <th>answer</th>
      <th>ground_truth</th>
      <th>contexts</th>
      <th>answer_correctness</th>
      <th>context_recall</th>
      <th>context_precision</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Which department is Michael Johnson in?</td>
      <td>Based on the provided information, there is no mention of the department where Michael Johnson works. If you can provide more information about Michael Johnson, I may be able to help you find the answer.</td>
      <td>Michael Johnson is a member of the Course Development Department.</td>
      <td>[Providing administrative management and coordination support, optimizing administrative workflows. , Performance Management Department Han Shan Li Fei I902 041 ...</td>
      <td>0.166901</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Which department is Michael Johnson in?</td>
      <td>Michael Johnson is in the Human Resources Department.</td>
      <td>Michael Johnson is a member of the Course Development Department.</td>
      <td>[Li Kai, Director of the Course Development Department , Newton discovered the law of universal gravitation]</td>
      <td>0.196046</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Which department is Michael Johnson in?</td>
      <td>Michael Johnson is in the Course Development Department.</td>
      <td>Michael Johnson is a member of the Course Development Department.</td>
      <td>[Newton discovered the law of universal gravitation, Michael Johnson, an engineer in the Course Development Department, has recently been responsible for curriculum development]</td>
      <td>0.998264</td>
      <td>1.0</td>
      <td>0.5</td>
    </tr>
  </tbody>
</table>
</div>

### More evaluation metrics
In addition to RAG, LLMs and natural language processing (NLP) are applied in a wide range of tasks, such as agents, natural language to SQL conversion, machine translation, text summarization,  andquestion answering. Ragas provides a variety of metrics that can be used to evaluate the performance of these tasks, ensuring that the outputs of LLMs are accurate, relevant, and aligned with the expected results.

| Evaluation metric            | Use case | Metric meaning                                                                 |
|---------------------|----------|--------------------------------------------------------------------------|
| [ToolCallAccuracy](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/agents/#example)    | Agent    | Evaluates the LLM's performance in identifying and invoking tools required to complete specific tasks. This metric is obtained by comparing reference tool calls with tool calls made by the LLM, with a value range of 0-1. |
| [DataCompyScore](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/sql/)      | natural language to SQL   | Evaluates the difference between the results obtained from database queries using SQL statements generated by the LLM and the correct results. The value ranges from 0 to 1.                     |
| [LLMSQLEquivalence](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/sql/#non-execution-based-metrics)   | natural language to SQL   | LLMSQLEquivalence: Compares the LLM-generated SQL with the ground-truth SQL for semantic equivalence without executing them against a database. The value ranges from 0 to 1.   |
| [BleuScore](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/traditional/#bleu-score)           | General     | Measures the n-gram overlap between the generated response and a reference response. Initially designed for evaluating machine translation systems, this metric does not require the use of an LLM during evaluation, and its value ranges from 0 to 1. In the [2.7 tutorial](2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb), you will learn how to fine-tune LLMs, and BleuScore can be used to measure the benefits brought by fine-tuning.

## 🔥 Quiz

### 🔍 Single-choice question
<details>
<summary style="cursor: pointer; padding: 12px;  border: 1px solid #dee2e6; border-radius: 6px;">
<b>What does the Context Precision metric measure❓(Select 1.)</b>

- A. Overall response quality
- B. Whether retrieved text segments relevant to the question are ranked higher
- C. Whether the generated answer is relevant to the retrieved text segments
- D. Whether the generated answer is relevant to the question

**[Click to view the answer]**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference Answer: B**  
📝 **Explanation**:  
- Context Precision specifically evaluates the ranking quality of the retrieval system—i.e., whether relevant documents appear at the top of the retrieved list. It does not measure the quality of the final answer (answer_correctness) or the overall relevance of the answer to the question (answer_relevance).

</div>
</details>
