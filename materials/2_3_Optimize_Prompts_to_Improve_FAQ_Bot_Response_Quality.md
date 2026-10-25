# 2.3 Optimizing prompts to improve the quality of responses from Q&A bots

## 🚄 Preface  

The Q&A bot from the previous section can already answer questions about company rules and regulations, but this is only the first step in building an excellent user experience. Users often expect more personalized and precise interactions. This section introduces prompt engineering techniques, teaching you how to improve or control the output of the Q&A bot by optimizing prompts—for example, adjusting tone, standardizing formats, or even enabling it to handle tasks like text summarization, inference, and transformation.

## 🍁 Goals

After completing this section , you will know about:

* How prompt frameworks and templates work
* Prompt techniques and their best practices
* How to apply LLMs in engineering to handle various tasks

## 1. Previous content recap

In the previous section, through the RAG method, the LLM has already obtained the company's private knowledge. For ease of invocation, this was encapsulated into several functions and saved in chatbot/rag.py. You can now quickly invoke it using the following code:

```python
import os
from config.load_key import load_key, display_config_summary
load_key()
display_config_summary()
```

```python
from chatbot import rag, llm
# Load index
# The previous section has already built the index, so the index can be loaded directly here. If you need to rebuild the index, you can add a line of code: rag.indexing()
index = rag.load_index(persist_path="knowledge_base/test")
query_engine = rag.create_query_engine(index=index)
```

```python
# Define the question-answering function
def ask_llm(question, query_engine):
  streaming_response = query_engine.query(question)
  streaming_response.print_response_stream()
```

## 2. Optimizing Prompts to Improve Response Quality 

In the previous section, you successfully mastered the art of harnessing internal company knowledge for your Q&A bot via RAG. Now, let's put its real-world performance to the test. 

Imagine a new colleague wants to learn about the company's project management tools and asks the bot:

```python
# Bot performance using RAG only
question = "What tools should we use for project management in our company?"
ask_llm(question, query_engine)
```

The response is accurate, but it lacks **utility**. A colleague might complain: *"The answer is fine, but it would be perfect if it included direct links to the tools so I don't have to hunt for them myself."*

This is a perfectly reasonable request. One straightforward—and perhaps "brute-force"—solution might be to manually append a specific instruction to the end of the user's question:

```python
# Attempting a simple "patch"
question = "What tools should we use for project management in our company?"
instruction = " Please make sure to include the official website or download link for the tools in your response."
 
# Simply concatenate the question and the instruction
new_question = question + instruction
ask_llm(new_question, query_engine)
```

**Expected Output (Example):**
> For project management, we recommend using **Jira** or **Trello**. Both tools are excellent for tracking project progress and ensuring efficient team collaboration.
> 
> - **Jira**: A powerful tool specifically designed for software development projects. It helps you track issues, tasks, and project milestones. You can visit the [Atlassian Official Site](https://www.atlassian.com/software/jira) for more info or to download.
> 
> - **Trello**: A more flexible, Kanban-style tool suitable for various project types. Its card-and-list format provides a visual overview of progress. You can visit [Trello.com](https://trello.com/) to sign up or learn more.

Problem solved, right? Well... not quite.

Consider another scenario where a user asks a question that has nothing to do with software tools:

```python
# Testing the "patch" on an unrelated question
question_2 = "How many days of annual leave am I entitled to?"
instruction = " Please make sure to include the official website or download link for the tools in your response."
 
new_question_2 = question_2 + instruction
ask_llm(new_question_2, query_engine)
```


**Expected Output (Example):**
> Your question pertains to company benefits, specifically annual leave. This information is typically recorded in the Employee Handbook or internal HR policy documents. I suggest contacting HR for the exact details. The HR contact is Wei Xiong (xiongwei@educompany.com).
> 
> Regarding your request for tool websites or download links: since your question does not involve any specific tools, I am unable to provide any links.

This reveals the fundamental flaw. This "one-size-fits-all" approach to concatenating instructions is extremely **fragile**. Not only does it make the model’s responses feel verbose and awkward, but it also requires you to manually decide which instruction to append for every single query—which is completely impractical in a real-world application.

**This is exactly why we need to dive into Prompt Engineering.** As a vital component of **Context Engineering**, it teaches you how to move away from these temporary "patches." Instead, you will learn to build conversation contexts systematically and intelligently, precisely guiding the model on how to respond to different situations with grace and accuracy.

## 3. Prompt framework

### 3.1 Basic elements

When communicating with an LLM, you can think of it as an entity that has been trained to understand human communication patterns. The way you interact should mirror how humans exchange information. Your requirements must be clear and unambiguous. The clearer and more precise your question (or prompt), the better the large language model will understand the core of the query, and the more likely its response will meet your expectations. Generally speaking, the following elements should be clarified in a prompt, and form a prompt framework that can help you construct a complete and effective prompt:

|Element|Meaning|
|----|----|
|Objective|Clearly specify what task the LLM is required to complete, allowing it to focus on specific goals.|
|Context|Background information about the task, such as operational processes or task scenarios, clarifying the scope of the discussion for the LLM.|
|Role|The role the LLM should assume (e.g., "You are a helpful assistant," "You are a senior developer"). This defines the model's persona, voice, and writing style.|
|Audience|Specify the target audience for the response (e.g., "Explain this to a 5-year-old,"). This helps tailor the complexity and tone of the output.|
|Sample|Provide specific input-output examples for the LLM to follow. This is also known as "few-shot prompting" and helps the model understand the desired pattern and format.|
|Output Format|Specify the format of the output, output type, and range of enumerated values. You can also state content and information that should not be included in the output, which can be further clarified with examples.|

Of course, in addition to the prompt framework discussed above, many problem analysis paradigms can be used to help you articulate clear and specific requirements. For example, SWOT analysis and 5W2H analysis offer structured approaches to thinking through your needs and expressing them more effectively. Additionally, you can also write a meta-prompt—a prompt designed to optimize or enhance another prompt—to guide the LLM in refining your initial input.

By using such a meta-prompt, you can ask the model to:
* Clarify ambiguous statements
* Expand vague instructions into detailed guidelines
* Add context, tone, format, and examples where necessary
* Ensure the final prompt aligns with best practices for interacting with AI models

This self-reflection approach improves the quality of your prompts, while deepening your understanding of how to communicate effectively with AI systems. We'll dive deeper into meta-prompting systematically in `Section 4.6 Meta Prompting: Let the LLM Be Your Prompt Coach.`

```python
prompt_expand = """
    You are a Prompt Optimization and Expansion Assistant. Your primary role is to receive an arbitrary user input prompt — which may be vague, incomplete, or lacking in detail — and **refine and expand** it into a more structured, precise, and actionable instruction that can be clearly understood and executed by large language models.

    Given the input prompt, you should generate an optimized version according to the following instructions:

    Your task is to enhance the clarity of the original prompt while preserving its core intent. The resulting optimized prompt should:
    - Be semantically richer and more descriptive.
    - Include relevant context, constraints, or formatting instructions as needed.
    - Specify desired tone, style, or audience (if applicable).
    - Suggest example inputs and outputs where appropriate to guide model behavior.

    ---

    ### Output Format:

    Please respond with the following structure:

    #### 1. Optimized Prompt:
    [Here goes the enhanced and expanded version of the original prompt.]

    #### 2. Example Input (if applicable):
    [Provide one or more example(s) of what a user might input based on the prompt.]

    #### 3. Example Output (based on the example input):
    [Show what kind of output would be expected from the model when using this prompt with the given example input.]

    #### 4. Optimization Notes:
    [Briefly explain how you improved the original prompt — e.g., added clarity, specified format, included context, etc.]

    ---

    ### Example:

    #### Original Prompt:
    "Write a story about animals."

    #### Optimized Prompt:
    "Compose a short narrative (approximately 300–500 words) about a group of forest animals who must work together to solve a problem. The story should include at least three distinct animal characters, a central conflict or challenge, and a resolution that highlights themes such as cooperation, courage, or environmental awareness. Use descriptive language to set the scene and convey character emotions. Aim for a tone suitable for children aged 6–10."

    #### Example Input:
    None required — the model generates content autonomously.

    #### Example Output:
    Once upon a time in Greenleaf Forest, a wise old owl named Oliver noticed that the river had stopped flowing. Concerned, he called a meeting with his neighbors: Mina the mouse, Benny the bear, and Tilly the turtle. Together, they discovered a fallen tree blocking the stream. With teamwork and determination, they cleared the path and restored the water supply. From then on, the animals made sure to keep their home safe and healthy...

    #### Optimization Notes:
    - Added specific narrative elements (characters, setting, conflict, theme).  
    - Defined word count and target audience.  
    - Clarified tone and style expectations.  
    - Introduced emotional and moral dimensions to enrich storytelling.

    ---

    Please apply this process to any user-submitted prompt and return your response using the above template.

    The original prompt is:

"""

def input_enhanced_llm_output(questions):
    expanded_input = prompt_expand + questions
    return ask_llm(expanded_input, query_engine)

question = "Please help me write a promotional copy for our company's new book. The general content of the book is xxx(will be given later)"
input_enhanced_llm_output(question)
```

### 3.2 Prompt template

In application development, it is impractical to expect end-users to write their own effective prompts from scratch. Instead, developers use the principles of prompt frameworks to create structured prompt templates. This allows developers to simply insert dynamic user inputs into predefined placeholders, ensuring that every final prompt is consistent. This consistency leads to more reliable and standardized LLM responses.

In the RAG chatbot created using LlamaIndex, there is a default prompt template that looks like this:

- The default template can be viewed using code. You can refer to [the code on the LlamaIndex official website.](https://docs.llamaindex.ai/en/stable/examples/prompts/prompts_rag/) The original LlamaIndex prompt template is:  



```text
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer:
```

Both `context_str` and `query_str`  are placeholders that get replaced during the retrieval and querying process. The `context_str` is filled with relevant information retrieved from the vector database, while `query_str` is replaced with the user's actual question.

Since the default template is general-purpose , it may not be suitable for all scenarios. For example, you might want to adjust the chatbot's tone, add specific constraints, or define a precise output format. This customization ensures that the model’s output aligns more closely with your requirements.
 
You can use the following sample code, where `prompt_template_string` represents the new prompt template:

```python
# Build prompt template
prompt_template_string = (
    "You are the company's customer service assistant, you need to answer users' questions concisely."
    "\n【Notes】：\n"
    "1. Answer user questions based on contextual information.\n"
    "2. Only answer the user's question, do not output other information\n"
    "The following is reference information."
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Question: {query_str}\n."
    "Answer: "
)

# Update prompt template
rag.update_prompt_template(query_engine, prompt_template_string)
```

## 4. Techniques for writing effective prompts

In Section 3.1, some key elements of prompt design were introduced. This section will explain specific prompt techniques in detail, focusing on practical scenarios and how to apply the elements of a prompt effectively.

### 4.1 Clearly express requirements and use delimiters

Clearly stating your requirements ensures that the content generated by the LLM is highly relevant to the task at hand. These requirements typically include the **task objective**, **context**, and **background information**.

Using **delimiters** helps LLMs focus on specific goals, avoid ambiguous interpretations, and minimize unnecessary processing. Delimiters also help structure your prompt in a way that improves readability and model understanding.

Here are some commonly used delimiters in English prompt engineering:

| Delimiter Type      | Example                         | Use Case / Description |
|---------------------|----------------------------------|--------------------------|
| Triple Quotes         | `"""..."""`                      | For multi-line strings or input blocks |
| Triple Hashes         | `### Section ###`                | To mark headings or instruction sections |
| Double Angle Brackets | `<<example>>...<</example>>`     | To define custom tags for variables or examples |
| XML-like Tags         | `<input>...</input>`             | For structured formatting and content separation |
| Dashes                | `--- Section ---`                | To separate paragraphs or logical blocks |
| Equal Signs           | `=== Output Format ===`          | Similar to headings; often used for formatting clarity |

> ⚠️ Note: Avoid using symbols that appear frequently in your content as delimiters to prevent confusion. For example, if square brackets `[]` are commonly used  in your input text, they may not be suitable as delimiters.

---

### ✅ Example Usage in an English Prompt

```text
### Instruction ###
You are a helpful assistant. Please summarize the following article.

=== Article Content ===
""" 
Artificial intelligence (AI) is a branch of computer science that aims to create systems capable of performing tasks that typically require human intelligence.
"""

### Output Format ###
Please provide a summary in no more than 50 words.
```

```python
question = """
### Instruction ###
Expand and polish the text enclosed in XML tags below to make the copy vivid, creative, and appealing to new employees. 
The tone should be professional yet welcoming, suitable for onboarding materials.

=== Original Text ===
<text>
New Employee Training Camp Activity
</text>

=== Output Requirements ===
- Enhance the content with engaging language.
- Add context about the purpose and benefits of the training camp.
- Include key elements such as team-building, mentorship, and orientation.
- Keep the final output concise and motivational.
"""

ask_llm(question, query_engine)
```

The execution results show that the prompt effectively communicates the task requirements: to expand and enhance the provided text.

The core theme of the task is "**New Employee Training Camp Activities,**" and the intended audience is "**new company employees.**" In the prompt, the delimiter <text>...</text> is used to clearly encapsulate and isolate the original content for processing.

By structuring the prompt with clear instructions, appropriate context, and standardized delimiters, the model is better guided to generate output that not only preserves the original meaning but also becomes more vivid, engaging, and tailored to the target audience.

### 4.2 Define Role and Audience

The **role** is the identity the LLM should assume in a specific scenario, such as an expert, advisor, or assistant. The **audience** is the target user group for which the model's output is intended, such as general consumers or students. Defining these elements helps developers tailor the tone, depth, and structure of the content accordingly.
The example below demonstrates how different system roles affect the style and content of the generated output. 

> Pass the prompt template into `prompt_template_string`, and the user question into `question`, then call the `ask_llm` function to execute it.

<table>
  <thead>
    <tr>
      <th width = '80px'>Role</th>
      <th width = '500px'>LLM Algorithm Engineer</th>
      <th width = '500px'>Elementary School Teacher</th>
    </tr>
  </thead>
  <tbody valign = 'top'>
    <tr>
      <td>Prompt Template</td>
      <td>You are a senior large language model algorithm engineer. Please answer the user's question based on the provided information<br>---------------------<br>{context_str}<br>---------------------<br>Question: {query_str}.<br>Answer: 
</td>
      <td>You are an elementary school teacher. Please answer the user's question based on the provided information<br>---------------------<br>{context_str}<br>---------------------<br>Question: {query_str}.<br>Answer: </td>
    </tr>
    <tr>
      <td>User Question</td>
      <td>What is Qwen-VL</td>
      <td>What is Qwen-VL</td>
    </tr>
    <tr>
      <td>Output Answer</td>
      <td>Qwen-VL is a multimodal pre-trained model introduced by Alibaba Cloud. It combines text and image processing capabilities, enabling it to understand and generate text descriptions related to images. Simply put, Qwen-VL can be regarded as an artificial intelligence assistant that can "describe images in words." It not only understands the content of images but also generates corresponding textual descriptions or answers questions related to the images. This technology has broad application prospects in various fields, such as automatic image tagging, visual question-answering systems, and content-based image retrieval. For new media operations, tools like Qwen-VL can help improve content creation efficiency, enhance user experience, and provide users with richer and more diverse ways of presenting information.</td>
      <td>Kids, today we’re going to meet a new friend named Qwen-VL!\nQwen-VL is like a very smart robot that has "eyes" 👀 and a "brain" 🧠. It can "see" pictures and videos and understand their meaning, just like us!\nFor example, if you show it a picture of a kitten playing with a ball of yarn, it can not only recognize that it’s a kitten 🐱 but also tell you that it’s playing with a ball of yarn 🧶. Even better, you can ask it, "What color is the kitten?", and it will tell you the color of the kitten.\nIt can also understand the content in videos. For instance, if you show it a video of kids playing soccer ⚽️, it can tell you who is kicking the ball, where the ball goes, and even guess what might happen next!\nQwen-VL is like a child who is still learning. It keeps getting smarter and improving, and in the future, it will become even more intelligent, capable of doing more things and helping us better understand the world!</td>
    </tr>
  </tbody>
</table>

### 4.3 Specifying output formats

Sometimes developers need LLMs to produce structured data (such as JSON or XML) that downstream systems can programmatically parse and use in the application workflow. While LLMs excel at generating free-form natural language, they can also reliably produce structured outputs such as JSON, XML, or CSV formats—as long as the desired format and requirements are clearly specified in the prompt.
In the following example, based on the prompt template from Section 3.2, we will act as a Q&A bot to assist in reviewing the quality of company-developed documentation, and return the results in **JSON format**:

```python
question_task = """
[Task Requirements]
You will be given a sentence or paragraph. Your task is to review it for any spelling or grammatical errors. 
If there are errors, you should identify them, explain the issue, and provide a corrected version. 

---
[Output Requirements]
Please output only in JSON format. Do not include markdown or code blocks.
The JSON must contain:
- "label": 0 if an error is found, 1 if no error.
- "reason": A brief explanation of the error (if any).
- "correct": The corrected version of the text (or the original if no error).

---
[User Input]
The following is the user input. Please review it:
"""

question_doc = "Delimiters are special symbols that help large langauge models (LLMs) identify which parts of the prompt should be considered a complete unit of meaning."

question = question_task + question_doc

ask_llm(question, query_engine)
```

As shown in the example results, the prompt `question_task` specified that the output format should be JSON format, and clearly defined the content requirements. The model  generated responses in the required format. This consistent and structured output makes it easier to integrate the model into existing systems.

On news websites, blog platforms, or internal knowledge-sharing platforms within enterprises, user-edited or published articles may contain typos, grammatical errors, or even sensitive information. However, traditional manual review methods are prone to oversight. In this case, LLMs can be integrated to automatically review content. If an article is flagged for serious grammatical errors or high-risk sensitive words, its priority for revision will be set to "high." For articles with minor issues, the priority for revision can be set to "low." This approach reduces labor costs and enhances the efficiency and accuracy of the system.

Of course, there are many other applications similar to this scenario. Developers can analyze system bottlenecks or focus on data-intensive tasks to explore more use cases for LLMs.

### 4.4 Providing few-shot examples

In the example from Section 4.3, the prompt specified the output format, and the LLM  generated formatted content. However, if we want the model's output  to not only be correctly formatted but also maintain consistency in style and structure, providing a few examples is a highly effective technique. This technique, known as `few-shot prompting`, is like giving the model a "reference book" to follow.

In the following code example, let’s first observe the LLM's output without any examples:

```python
question_task = """
### 📝 Task Requirements
You are to generate content based on the user's topic, following the **style and structure** of the example provided below. Do not add any extra text or explanations — return only the final Markdown-formatted output.

---
### 🧩 Output Format Requirements
Please ensure your response strictly follows this format:
- Use Markdown syntax (headings, lists, bold, links, image placeholders, etc.)
- Keep the tone informative and easy to follow
- Structure content in a step-by-step or tutorial format
- Avoid markdown code blocks around the final output itself

---
### 👤 User Input Topic
The following is the user's requested topic:
""" 

question_doc = "Handmade Keychain Making Tutorial"

question = question_task + question_doc

ask_llm(question, query_engine)
```

The model generated a tutorial for making handmade keychains, but the content was not concise enough. If you want the model to output content in a specific style and structure—such as focusing only on the theme, list of materials, and step-by-step instructions—you can provide a few examples to guide it. This helps the model "imitate" the desired format and produce more consistent and structured results.

```python
question_task = """
### 📝 Task Requirements
You are to generate content based on the user's topic, following the **style and structure** of the example provided below. Do not add any extra text or explanations — return only the final Markdown-formatted output.

---
### 🧩 Output Format Requirements
Please ensure your response strictly follows this format:
- Use Markdown syntax (headings, lists, bold, links, image placeholders, etc.)
- Keep the tone informative and easy to follow
- Structure content in a step-by-step or tutorial format
- Avoid markdown code blocks around the final output itself

---
### 📚 Example Content
<example>
### Example 1: Making a Simple Bookmark
# Simple Bookmark Making Tutorial

## Steps
1. Choose a piece of colored cardstock.
2. Use a pencil to draw a rectangle on the cardstock, with dimensions approximately 2 inches x 6 inches.
3. Cut out the rectangle along the pencil lines.
4. Personalize the bookmark by decorating it with stickers.
5. Done! You now have a unique bookmark.
</example>

---
### 👤 User Input Topic
The following is the topic requested by the user:
"""

question_doc = "Making Handmade Greeting Cards"

question = question_task + question_doc

ask_llm(question, query_engine)
```

From the above example results, it's clear that the LLM has fully adhered to the provided example and generated content with a consistent structure and style. When specifying the output format in a prompt, it is recommended to provide a few examples for the LLM to reference. This practice helps ensure that the model's output is more reliable, consistent, and aligned with your expectations.

### 4.5 Giving the model "thinking" time

For some complex tasks, even well-structured prompts may be insufficient for the LLM to complete the task effectively. In such cases, you can guide the model by allowing it to "think" step by step, encouraging it to provide intermediate reasoning before arriving at a final answer. This approach, known as the chain-of-thought (CoT) method, improves performance on tasks that require logical or mathematical reasoning.

For example, consider a scenario where you ask the LLM to solve a math problem. The correct answer is $10,500. Initially, you might use a simple prompt:

```python
question = """
[Background Information]
An educational training institution (hereinafter referred to as the "company") incurred the following main expenses in the 2023 fiscal year:
To provide classes for students in different cities, the company's teachers traveled on business trips 5 times during the year, each trip lasting one week. The specific expenses are as follows:
   - Transportation and accommodation fees: average 1600 usd/trip
   - Teaching materials procurement costs: At the beginning of the year, the company purchased a batch of teaching materials for a total price of 10,000 usd, which is expected to last for 4 years.

[Problem Description]
Based on the above background information, complete the following tasks:
Calculate the total travel expenses for the year due to teacher business trips, including the amortized cost of teaching materials.

[Output Requirements]
Provide only the total travel expenses directly, without any other information. """
ask_llm(question, query_engine)
```

As shown, the initial response is incorrect. To improve accuracy, you can use the CoT method by prompting the LLM to explain its reasoning step by step.

```python
question = """An educational training institution (hereinafter referred to as the "company") incurred the following major expenses in the 2023 fiscal year:
To provide classes for students in different cities, the company's teachers traveled on business trips 5 times throughout the year, with each trip lasting one week. The specific expenses are as follows:
   - Transportation and accommodation fees: an average of 1600 usd per trip
   - Teaching materials procurement costs: At the beginning of the year, the company purchased a batch of teaching materials for a total price of 10,000 usd, which is expected to last for 4 years.
   
### Problem Description
Based on the above background information, complete the following tasks:
Calculate the total travel expenses for the year caused by teacher business trips, including the amortized cost of teaching materials.

### Output Requirements
Please derive step by step to calculate the total travel expenses."""

ask_llm(question, query_engine)
```

After optimizing the prompt, the LLM was able to generate an accurate and detailed response. This demonstrates that prompting the model to generate a chain of thought can significantly improve the quality of reasoning-based outputs.

While CoT is a powerful technique, there are other methods to enhance the model’s thinking process, such as tree of thoughts (ToT) and graph of thoughts (GOT). However, current LLMs still rely heavily on CoT for structured reasoning. As AI technology advances, models are gradually moving toward more sophisticated multi-agent systems (MAS), which can handle complex tasks more efficiently. You can explore this further in <2_6_Extend_FAQ_Bot_Capabilities_with_Plugins>.

### 4.6 Meta Prompting: Let the LLM Be Your Prompt Coach

Writing a perfect prompt on the first try is often very difficult. A more common workflow is:
1. Write the first version of the prompt.
2. Run it and analyze which parts of the output don't meet expectations.
3. Summarize the problems, think about how to improve, then modify the prompt.
4. Repeat this iteration process until satisfied.

Think about it—isn't this also your typical path for optimizing prompts? While this process is effective, it heavily relies on experience and is quite time-consuming.

At this point, you might think: since LLMs are so powerful, **can we let the model itself handle this analysis, summarization, and improvement iteration process?** Having it play the role of a "prompt review expert" to help us analyze and optimize prompts would undoubtedly be more efficient.

The answer is yes. This method of **having you and the model "discuss" how to optimize the prompt itself** is called **Meta Prompting**.

To further understand this powerful technique, let's practice it hands-on.

#### Step 1: A Less-Than-Ideal Initial Prompt

Suppose your task is to optimize the Q&A bot's responses to make them more friendly and clearly structured when answering new employees' questions about "company benefits." You might start with a simple prompt:

```python
# In a real RAG application, this text would be retrieved from your vector database.
# Here we use a string to simulate it for experimentation.
retrieved_text = """
Regarding company benefits, we provide comprehensive health insurance covering employees and their immediate family members.
Annual health checkups are standard. Additionally, there are 15 days of paid annual leave and 5 days of paid sick leave per year.
We also provide a monthly transportation subsidy of 500 yuan and a meal subsidy of 300 yuan.
To encourage employee growth, the company has an annual education and training fund of up to 8000 yuan, which employees can apply to use for courses or professional books.
For fitness, the company has partnerships with multiple gyms where employees can enjoy discounted rates.
"""

# This is a very basic prompt that simply concatenates the task and information.
initial_prompt = f"""
Based on the following information, answer new employees' questions about company benefits.

【Reference Information】
{retrieved_text}
"""

# Let's see what effect this "plain" prompt produces.
response = llm.invoke(initial_prompt)
print("--- Initial Response ---")
print(response)
```

This response contains all the information, but you might feel that for a newly hired employee, it seems somewhat bland and disorganized. It simply restates the text without emphasis or a warm, welcoming tone.

Clearly, this result doesn't meet your expectations. Now, instead of racking your brain on how to modify it, you can try a more efficient method: **let the LLM help you optimize**.

#### Step 2: Build a Meta Prompt to Get Optimization Suggestions from the LLM

Now, you're dissatisfied with this bland response. You can construct a "Meta Prompt" that clearly describes your goals (friendly, structured, highlighting key points) to the model, and feed both your less-than-ideal initial prompt and its output to the LLM, requesting it to act as a "prompt engineering expert" to help you improve.

```python
# You need to clearly express your dissatisfaction and expectations—this is key to helping the AI coach understand your intent.
meta_prompt = f"""
I'm optimizing a prompt for our company's new employee Q&A bot, with the goal of answering questions about "company benefits."

This is my first attempt:
---
{initial_prompt}
---

This is the output it generated:
---
{response}
---

This output isn't good enough. I want the bot's responses to be more engaging, clearly structured, and help new employees quickly grasp the key points. Specific requirements:
1. **Tone**: Friendly, warm, with a welcoming feeling for new colleagues.
2. **Structure**: Use clear bullet points (e.g., lists starting with emojis) to organize content.
3. **Content**: Categorize benefits into groups like "Health & Leave," "Subsidies & Incentives," etc.

Please act as a prompt engineering expert and rewrite this prompt to achieve the above goals.
"""

# Now, let the AI coach get to work and generate an optimized version of the prompt for you.
optimization_suggestion = llm.invoke(meta_prompt)
print("--- Optimization Suggestions from AI Coach --")
print(optimization_suggestion)
```

Observe the suggestions from the AI coach—you'll find that the optimized prompt it provides likely applies multiple techniques you learned in previous sections, such as:

* **Defining a role** (e.g., "You are a warm, friendly onboarding buddy")
* **Clear task description** (e.g., "Based on the reference information provided, generate an introduction about company benefits")
* **Specifying output format and style** (e.g., "Use a warm welcome greeting," "Use lists starting with emojis")

This proves that having the model play an expert role to optimize prompts is entirely feasible.

#### Step 3: Use the Optimized Prompt

Now you can directly use the prompt that this "AI coach" customized for your task and see how it performs.

```python
# This is a hypothetical optimized prompt suggested by the AI coach
# In practice, you can directly use the output from `optimization_suggestion`
# Here we manually construct one that follows the suggestions for demonstration

optimized_prompt = f"""
【Role】
You are a warm, friendly Onboarding Buddy. Your task is to welcome new colleagues and clearly introduce the company's benefits policy.

【Task】
Based on the provided【Reference Information】, generate an introduction about company benefits.

【Output Requirements】
1. Start with an enthusiastic welcome greeting.
2. Organize the benefits information into categories, such as "Health & Leave," "Subsidies & Incentives," etc.
3. Use a relevant emoji before each benefit item to make it more engaging.
4. End with best wishes for the new colleague.

【Reference Information】
{retrieved_text}
"""

# Call the model again with the optimized prompt
final_response = llm.invoke(optimized_prompt)
print("--- Response Using Optimized Prompt ---")
print(final_response)
```


Through this iteration process, you'll get a response with a warm tone and clear structure—one that will undoubtedly leave a better first impression on new employees.

This example demonstrates the tremendous value of Meta Prompting in improving user experience. It's not just about extracting information, but about **how to better present information**. When you encounter a tricky prompt problem, don't forget that your model itself is the best coach. By clearly describing your goals and challenges, you can guide it to build more powerful, precise, and "human-touch" prompts for you.

In the initial approach above, we described our expected **qualitative goals** (like "friendly," "clearer structure") to the "AI coach," and it directly generated an optimized prompt for us. This method is convenient, but it has a key limitation: the AI coach's understanding of these qualitative goals may not be precise enough, and your description of requirements may not be specific enough, leading to uncertainty in optimization results.

To address this problem and make the optimization process more controllable and precise, we need to upgrade from "qualitative guidance" to "quantitative alignment." Instead of giving a vague goal, it's better to provide a perfect **"reference answer"** as a precise target. The following advanced approach will show you how to use this "reference answer" to let the LLM gradually and precisely approach the optimal result through automated gap analysis and iteration. This is a more engineering-oriented improvement approach.

#### Multi-Round Iteration: Introducing Reference Answers for Gap Analysis

In the previous example, you played the leading role, receiving the "AI coach's" suggestions and manually applying them. But this process can be further automated and made more precise. Rather than having the evaluator give a vague "good" or "bad" judgment, a more advanced method is to introduce a **"Reference Answer."**

This "reference answer" is your ideal perfect answer, which can be written by human experts or generated by the most powerful model using a very detailed prompt. The goal of iterative optimization becomes: **continuously modify the prompt so that the gap between its generated response and this "reference answer" becomes smaller and smaller**.

This process is like a self-correcting flow with precise guidance:

1. **Set Reference Answer**: First, define a high-quality, ideal "reference answer."
2. **Generate**: Use the current prompt to be optimized to generate a response.
3. **Analyze Gap**: Have an "evaluator" LLM (Critic) compare the "generated response" with the "reference answer" and output a detailed "gap analysis report" pointing out specific differences in tone, structure, content, format, etc.
4. **Optimize**: Pass the "gap analysis report" along with the original prompt and generated response to an "optimizer" LLM. Its task is to rewrite the prompt based on this report to specifically address the issues identified, thereby reducing the gap.
5. **Repeat**: Replace the old prompt with the optimized new one, then go back to step 2, until the "evaluator" considers the gap small enough or the maximum iterations are reached.

```python
# 1. Set Reference Answer
reference_answer = """
👋 Welcome to our big family! I'm excited to introduce our awesome benefits:

**🏥 Health & Leave, We've Got You Covered:**
- **Comprehensive Health Insurance**: Covers you and your family—work with peace of mind.
- **Annual Health Checkup**: Your health matters to us, always.
- **Paid Annual Leave**: A full 15 days to explore poetry and distant places!
- **Paid Sick Leave**: 5 days to rest and recover your energy.

**💰 Subsidies & Incentives, Cheering You On:**
- **Transportation Subsidy**: 500 yuan monthly for an easier commute.
- **Meal Subsidy**: 300 yuan monthly—add an extra drumstick to your lunch!
- **Education & Training Fund**: Up to 8000 yuan annually—invest in yourself, the future is bright.
- **Gym Discounts**: Partnered with multiple gyms—don't forget to exercise no matter how busy!

Hope these benefits make you feel the company's care! Looking forward to creating more value together! 🎉
"""

# 2. Define gap analysis and optimization functions
def analyze_gap(generated_response, reference):
    gap_analysis_prompt = f"""
    【Role】You are a text comparison expert.
    【Task】Please compare in detail the gaps between the【Generated Response】and the【Reference Answer】.
    【Reference Answer】
    {reference}
    ---
    【Generated Response】
    {generated_response}
    ---
    【Requirements】
    Please output a detailed gap analysis report covering tone, structure, content details, format (such as emoji usage), etc. If there's almost no gap between them, simply answer "Gap is minimal."
    """
    return llm.invoke(gap_analysis_prompt)

def optimize_prompt_with_gap_analysis(current_prompt, generated_response, gap_report):
    optimization_prompt = f"""
    【Role】You are a top-tier prompt engineer.
    【Task】Based on the provided "Gap Analysis Report," optimize the "Current Prompt" so it can generate output closer to the "Reference Answer."
    ---
    【Current Prompt】
    {current_prompt}
    ---
    【Generated Response】
    {generated_response}
    ---
    【Gap Analysis Report】
    {gap_report}
    ---
    【Requirements】
    Please return only the optimized new prompt without any other explanations.
    """
    return llm.invoke(optimization_prompt)

# 3. Iterative optimization loop
current_prompt = initial_prompt
for i in range(3): # Maximum 3 iterations
    print(f"--- Iteration {i+1} ---")
    generated_response = llm.invoke(current_prompt.format(retrieved_text=retrieved_text))
    print(f"Generated Response (partial):\n{generated_response[:100]}...")
    
    gap_report = analyze_gap(generated_response, reference_answer)
    print(f"Gap Analysis Report:\n{gap_report}")
    
    if "Gap is minimal" in gap_report or "差距很小" in gap_report:
        print("\nEvaluation passed, optimization complete!")
        break
    
    print("\nEvaluation not passed, optimizing prompt based on gap analysis report...")
    current_prompt = optimize_prompt_with_gap_analysis(current_prompt, generated_response, gap_report)
else:
    print("\nMaximum iterations reached, stopping optimization.")

final_prompt_based_on_reference = current_prompt
```

This automated iteration process demonstrates the true power of Meta Prompting. It frees you from tedious manual adjustments, letting the model explore and discover the best ways of expression on its own, and provides foundational ideas for designing more complex **AI Self-Improvement** systems.

#### Effectiveness Evaluation: Quantifying Your Optimization Results

When you have multiple versions of prompts (e.g., initial version vs. single-optimization version vs. multi-round iteration final version), how do you objectively prove which is better? Beyond intuitive feelings, a more scientific approach is **quantitative evaluation**.

You can leverage the LLM again, having it play the role of a "Grader" to score responses generated by different prompts according to a series of criteria.

For example, you can define scoring criteria:

* **Friendliness**: 1-5 points
* **Clarity of Structure**: 1-5 points
* **Information Accuracy**: 1-5 points

Then, construct a "Grader Prompt" that passes the scoring criteria and the response to be evaluated to the LLM, having it output a structured scoring result (like JSON).

```python
import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

# Three typical response samples with obvious quality differences
# Poor: Simple listing of information, no structure or emotion
poor_response = "Company benefits: Health insurance, family can use. 15 days annual leave, 5 days sick leave. Transportation subsidy 500, meal subsidy 300. Training fund 8000. Gym has discounts."

# Medium: Has basic structure and categories, but bland tone
medium_response = """
Company Benefits:
1. 💦Health and Leave:
   - Health insurance (including family)
   - Annual checkup
   - 15 days annual leave and 5 days sick leave
2. 💰Subsidies and Incentives:
   - Monthly 500 transportation subsidy and 300 meal subsidy
   - 8000 yuan/year education and training fund
   - Partner gym discounts
"""

# Good: Clear structure, friendly tone, strong visual appeal (directly use our reference answer)
good_response = reference_answer 

# Design more detailed evaluation dimensions
def grade_response_detailed(response_to_grade):
    grader_prompt = f"""
    【Role】You are an experienced internal communications and employee experience evaluator.
    【Task】Please rate the provided "Company Benefits Introduction" text on a 1-5 scale across the following four dimensions.
    
    【Scoring Dimensions】
    1. **welcoming_tone**: 1 means cold and stiff tone, 5 means very warm and infectious.
    2. **structuring**: 1 means chaotic and disorganized, 5 means clear categories and strong logic.
    3. **visual_appeal**: 1 means dull and boring, 5 means good use of emojis, bold text, etc., very eye-catching.
    4. **completeness**: 1 means serious information gaps, 5 means all key benefit information is complete.

    【Text to Evaluate】
    {response_to_grade}
    ---
    【Output Requirements】
    Please strictly return your scores in JSON format without any explanations. For example:
    {{"welcoming_tone": 5, "structuring": 4, "visual_appeal": 5, "completeness": 5}}
    """
    try:
        raw_output = llm.invoke(grader_prompt)
        # Extract JSON portion
        json_str = raw_output[raw_output.find('{'):raw_output.rfind('}')+1]
        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        # Error handling, return default low scores when parsing fails
        return {"welcoming_tone": 1, "structuring": 1, "visual_appeal": 1, "completeness": 1}

# Score the three typical samples
scores = {
    "Original Answer": grade_response_detailed(poor_response),
    "Single Iteration Optimize": grade_response_detailed(medium_response),
    "Multi-turn Iteration Optimize": grade_response_detailed(good_response)
}

# Convert scores to DataFrame and visualize
df = pd.DataFrame(scores)
df = df.reset_index().rename(columns={'index': 'Dim'})
df_long = df.melt(id_vars='Dim', var_name='Version', value_name='Score')

# --- Grouped bar chart ---
plt.figure(figsize=(10, 6))
ax = sns.barplot(
    data=df_long,
    x="Dim",
    y="Score",
    hue="Version",
    palette="viridis"
)

# Add value labels to each bar
for p in ax.patches:
    height = p.get_height()
    if height == 0:
        continue
    ax.annotate(
        f"{height}",
        (p.get_x() + p.get_width() / 2., height),
        ha='center', va='center',
        xytext=(0, 5),
        textcoords='offset points',
        fontsize=11
    )

ax.set_ylim(0, 6)
ax.set_ylabel('Score (1-5)', fontsize=12)
ax.set_xlabel('')
ax.set_title('Evaluation', fontsize=20)
ax.tick_params(axis='x', labelsize=12)

plt.legend()
plt.tight_layout()
plt.show()
```


You can see that the LLM's response quality improves to varying degrees with each iteration. Through this quantitative evaluation, you can not only intuitively see the improvement from each optimization but also transform vague feelings of "good" or "bad" into clear, measurable data. This provides you with a scientific method to validate and iterate your prompt strategies, ensuring every improvement is evidence-based, ultimately delivering truly high-quality user experiences.

### 4.7 Let the LLM Help You Build a Custom "AI Judge"

The automated optimization loop in the previous section is very powerful, but it raises a key engineering question: when does this loop stop?

The key issue is that relying on vague evaluations like "is the gap big or small" is unreliable. You need an "**AI Judge**" that can give a clear "**✅ Pass**" or "**❌ Fail**" conclusion based on preset quantified standards for each optimization result, thereby providing a clear and reliable stopping condition for your automated workflow.

<div align="center">
  <a href="https://img.alicdn.com/imgextra/i4/O1CN01Ie6KDU1pMWUJ2Ky25_!!6000000005346-2-tps-1115-614.png" target="_blank">
      <img src="https://img.alicdn.com/imgextra/i4/O1CN01Ie6KDU1pMWUJ2Ky25_!!6000000005346-2-tps-1115-614.png" width="900">
    </a>
  <p>Figure: Constructing an "AI Judge" via Meta-Prompting to replace the <code>analyze_gap()</code> method and enhance judgment accuracy.</p>
</div>


#### The "AI Judge" Training Process

The process of building an "AI Judge" can be seen as training a machine learning classifier. The "AI Judge" prompt you're building is the "model" to be trained, and the standard samples you prepare are the "dataset." The entire process is using data to "train" your "model."

1. **Prepare Dataset**: First create a batch of high-quality labeled samples (containing both "good answers" and "bad answers").
2. **Iterative "Training"**:
   - a. Automatically split this data proportionally (e.g., 7:3) into "training set" and "evaluation set."
   - b. Use the current "judge prompt" to make "predictions" on both the **training set** and **evaluation set**, recording the accuracy scores for each.
   
   Why monitor both scores? Tracking changes in these two scores helps you determine if the "model" is "overfitting"—meaning it just "memorized" the training questions but didn't truly improve its judgment ability on new questions (evaluation set).
   
   - c. Find the "wrong answers" on the **training set**.
   - d. Take these "wrong answers" along with your analysis, and through Meta Prompting, have the LLM help you optimize the "judge prompt" to generate a new version.
   - e. Repeat steps b-d. You can stop "training" at any time.

3. **Stop "Training"**:
   In each iteration, you need to intervene and analyze:
   - Are both training accuracy and evaluation accuracy steadily improving?
   - Has evaluation accuracy stagnated or suddenly dropped (possible overfitting)?
   - Do the newly generated "wrong answers" expose ambiguity or contradictions in the samples themselves? (Poor sample quality)

> Note: If sample quality is poor, causing inconsistent evaluation standards or ambiguous judgments on similar questions, the LLM may never be able to construct a well-performing "AI Judge." At this point, you can stop iteration and first optimize your sample data.

Finally, you decide when to stop "training" and adopt the version of the prompt that performs best on the evaluation set as your final "**AI Judge**."


<div align="center">
    <a href="https://img.alicdn.com/imgextra/i1/O1CN01gJT1AY22xhe34lZwM_!!6000000007187-2-tps-1864-598.png" target="_blank">
    <img src="https://img.alicdn.com/imgextra/i1/O1CN01gJT1AY22xhe34lZwM_!!6000000007187-2-tps-1864-598.png" width="800"/>
    </a>
  <p>Figure: Iterating the AI Judge via ML training; stop based on train vs. eval performance.</p>
</div>



#### 4.7.1 Prepare and Split the Dataset

First, you need a batch of samples carefully labeled by you or domain experts. This is the foundation of the entire process and the cornerstone of quality.

```python
# Prepare a batch of high-quality labeled samples
# In practice, these samples can be uploaded to AI platforms (like Bailian) to create evaluation sets
labeled_samples = [
    # --- 3 samples for "training" ---
    {
        "id": "train_01",
        "response": "Company benefits: Health insurance, family can use. 15 days annual leave, 5 days sick leave. Transportation subsidy 500, meal subsidy 300. Training fund 8000. Gym has discounts.", 
        "label": "Fail", 
    },
    {
        "id": "train_02",
        "response": """Company benefits include:\n1. Health and leave: Health insurance, annual checkup, 15 days annual leave and 5 days sick leave.\n2. Subsidies and incentives: Monthly 500 transportation subsidy and 300 meal subsidy, plus 8000 yuan training fund.""", 
        "label": "Fail", 
    },
    {
        "id": "train_03",
        "response": """👋 Welcome! We've prepared awesome benefits for you:\n- 🏥 Comprehensive health insurance and annual checkup\n- 🌴 15 days annual leave + 5 days sick leave\n- 💰 Monthly transportation and meal subsidies\n- 🎓 Up to 8000 yuan training fund\nLooking forward to working with you! 🎉""", 
        "label": "Pass", 
    },
    
    # --- 2 samples for "evaluation" ---
    {
        "id": "eval_01",
        "response": "We have health insurance, annual leave, sick leave, transportation and meal subsidies, training fund and gym discounts.", 
        "label": "Fail", 
    },
    {
        "id": "eval_02",
        "response": """Hello, new colleague! Company benefits are great:\n- Health includes insurance and checkups.\n- Leave includes annual and sick leave.\n- Money includes subsidies and education fund.\nWish you a happy work experience!""", 
        "label": "Pass", 
    },
]

# Split dataset proportionally (manual simulation here)
# In real projects, use train_test_split from scikit-learn for random splitting
train_set = labeled_samples[:3]
eval_set = labeled_samples[3:]
```


#### 4.7.2 Iterative "Training"

By having the model continuously learn from "wrong answers," the "judge prompt" becomes smarter and smarter.

```python
# Define a helper function to evaluate prompt accuracy on a specified dataset
def evaluate_judge_prompt(judge_prompt, dataset):
    correct_predictions = 0
    misjudged_cases = []
    
    for sample in dataset:
        prompt = judge_prompt.format(response_to_judge=sample["response"])
        
        # Simulate LLM call, actual: predicted_label = llm.invoke(prompt)
        # For demonstration, manually simulate different prompt version behaviors
        predicted_label = "Pass" if "Welcome" in sample["response"] or "Hello" in sample["response"] else "Fail"
        if "v1" in judge_prompt:
             if "1." in sample["response"]: predicted_label = "Pass"

        is_correct = (predicted_label == sample["label"])
        if is_correct:
            correct_predictions += 1
        else:
            misjudged_cases.append({
                "response": sample["response"],
                "current_judgment": predicted_label,
                "correct_judgment": sample["label"]
            })
            
    accuracy = correct_predictions / len(dataset)
    return accuracy, misjudged_cases

# ----------------- Iterative "Training" Begins -----------------

# a. Prepare initial version of "judge prompt" (v1.0)
judge_prompt_v1 = """
# v1
【Role】You are an employee experience expert.
【Task】Judge whether the【Response to Evaluate】is qualified.
【Evaluation Criteria】
1. Clear structure: Information listed in points or categories.
2. Complete information: Mentions core benefits.
【Response to Evaluate】
---
{response_to_judge}
---
【Output Requirements】Please only answer "Pass" or "Fail".
"""

current_judge_prompt = judge_prompt_v1
max_iterations = 2

for i in range(max_iterations):
    print(f"--- Iteration {i+1} ---")
    
    # b. Make "predictions" on training and evaluation sets and record scores
    train_accuracy, misjudged_on_train = evaluate_judge_prompt(current_judge_prompt, train_set)
    eval_accuracy, _ = evaluate_judge_prompt(current_judge_prompt, eval_set)
    
    print(f"Training Set Accuracy: {train_accuracy:.0%}")
    print(f"Evaluation Set Accuracy: {eval_accuracy:.0%}")

    if not misjudged_on_train:
        print("\nNo errors on training set, training complete.")
        break
        
    # c. Find "wrong answers" on training set
    first_error = misjudged_on_train[0]
    print(f"\nFound wrong answer: Model misjudged a response that should be '{first_error['correct_judgment']}' as '{first_error['current_judgment']}'")

    # d. Package "wrong answers" and have LLM help optimize the prompt
    judge_optimizer_prompt = f"""
    【Role】You are a top-tier prompt engineer.
    【Background】My current judge prompt made an error when evaluating a sample.
    
    【My Current Judge Prompt】
    ---
    {current_judge_prompt}
    ---
    
    【Error Case】
    - Response to evaluate: "{first_error['response']}"
    - My tool's wrong judgment: "{first_error['current_judgment']}"
    - Expected correct judgment: "{first_error['correct_judgment']}"
    - Reason I think it erred: Current criteria are too loose, didn't emphasize 'warm and friendly' tone.
    
    【Task】Please rewrite my judge prompt to make criteria stricter and correct the above error.
    【Requirements】Please only return the optimized new prompt.
    """
    
    print("Optimizing prompt based on wrong answers...")
    new_judge_prompt = """
    # v2
    【Role】You are an internal communications expert pursuing ultimate employee experience, with a discerning eye.
    【Task】Strictly judge whether the【Response to Evaluate】is qualified.
    【Evaluation Criteria】
    1. **Welcoming Atmosphere (Required)**: Must have clear, warm welcome greeting.
    2. **Structured Presentation (Required)**: Must use lists or sections.
    【Response to Evaluate】
    ---
    {response_to_judge}
    ---
    【Output Requirements】Please only answer "Pass" or "Fail".
    """
    
    # e. Update to new version prompt, enter next iteration
    current_judge_prompt = new_judge_prompt
    print("-" * 20 + "\n")

print("\n--- Iteration Ended ---")
final_judge_prompt = current_judge_prompt
```


#### 4.7.3 "Good Enough" Means You Can "Stop Training"

In the iteration loop above, you can clearly see the score changes:
- Iteration 1:
    - Training Set Accuracy: 67% (v1 prompt misjudged train_02)
    - Evaluation Set Accuracy: 100% (v1 prompt happened to judge both correctly)
- Iteration 2:
    - Training Set Accuracy: 100% (v2 prompt corrected the error)
    - Evaluation Set Accuracy: 100%

In this simple example, evaluation accuracy stayed high throughout. But in real scenarios, you might see evaluation accuracy stagnate or even decline.

Based on the above data, you'll find that the v2 version prompt achieved 100% accuracy on both training and evaluation sets. Therefore, you can adopt `judge_prompt_v2` as your final, validated "AI Judge." If evaluation results are unsatisfactory, you may need to go back to the beginning and check and optimize your `labeled_samples`.

#### 4.7.4 Use the "AI Judge" to Guide Automated Optimization

Now you have an "AI Judge" (`final_judge_prompt`) that's been repeatedly validated and tested, ready for deployment.

You need to use it to replace the evaluation step in section 4.6 that compared differences between two samples to determine usability, making the entire workflow more rigorous.

**New Workflow:**
1. **Generate**: Use the current "generation prompt" to produce a response.
2. **Judge**: Call your trained "AI Judge prompt" to make a "Pass/Fail" judgment on the response.
3. **Decide & Optimize**:
    - If the judgment is "**Pass**," the loop ends—optimization successful.
    - If the judgment is "**Fail**," pass the "generation prompt," "failed response," and the "**AI Judge's rulebook**" (i.e., its prompt) together to the "optimizer," letting it generate a new version prompt based on the clear failure criteria.

```python
# Define a more powerful optimization function that directly references the "judge's" rules
def optimize_with_judge_rules(current_prompt, failed_response, judge_prompt):
    """Call LLM to optimize generation prompt based on judge's rules"""
    optimizer_prompt = f"""
    【Role】You are a top-tier prompt engineer.
    【Background】I have a "generation prompt," but the response it generates failed the "AI Judge's" review.
    
    【Generation Prompt】
    ---
    {current_prompt}
    ---
    
    【Its Failed Response】
    ---
    {failed_response}
    ---
    
    【AI Judge's Rulebook (Reason for Failure)】
    ---
    {judge_prompt}
    ---
    
    【Task】
    Please carefully study the "AI Judge's Rulebook" and rewrite the "Generation Prompt" to ensure the new prompt can generate a response that passes the rulebook's review.
    
    【Requirements】
    Please only return the optimized new "Generation Prompt" without any other explanations.
    """
    new_prompt = llm.invoke(optimizer_prompt)
    return new_prompt

# --- Run the automated optimization loop driven by "AI Judge" ---
current_generating_prompt = initial_prompt
max_iterations = 5

print("\n" + "="*30)
print("Starting the final automated optimization workflow driven by 'AI Judge'")
print("="*30 + "\n")

for i in range(max_iterations):
    print(f"--- Final Workflow: Iteration {i+1} ---")
    
    # 1. Generate response
    prompt_for_generator = current_generating_prompt.format(retrieved_text=retrieved_text)
    generated_response = llm.invoke(prompt_for_generator)
    
    print(f"Generated Response:\n---\n{generated_response}\n---")
    
    # 2. Call "AI Judge" for judgment
    judge_prompt_filled = final_judge_prompt.format(response_to_judge=generated_response)
    judgment = llm.invoke(judge_prompt_filled)
    
    judgment_cleaned = judgment.strip().replace(".", "")
    print(f"'AI Judge' Verdict: {judgment_cleaned}")

    # 3. Decision
    if judgment_cleaned == "Pass" or judgment_cleaned == "通过":
        print("\n✅ Optimization successful! Generated response passed the 'AI Judge' review.")
        break
    else:
        print("❌ Did not pass review, optimizing based on 'Judge's' rules...")
        current_generating_prompt = optimize_with_judge_rules(
            current_generating_prompt, 
            generated_response, 
            final_judge_prompt
        )
        print("-" * 20 + "\n")
else:
    print("\nMaximum iterations reached, stopping optimization.")

print("\n" + "="*30)
print("Final Adopted Generation Prompt:")
print("="*30)
print(current_generating_prompt)
```

The "**AI Judge**" makes your prompt optimization workflow more controllable:
- Whenever the "generation prompt" produces a new response, first have the "AI Judge" score it.
- **Passed means optimization successful; failed means use this "bad answer" as new material to continue iterating your generation prompt**.

You can always adopt this approach: **first build the "judge," then optimize the "player."** Build a measurable, trustworthy, automatable "**Prompt Optimization Engineering**" system.

## 5. Reasoning Models

The prompt techniques and frameworks discussed earlier can be broadly applied to general-purpose LLMs (such as Qwen2.5-max, GPT-4, DeepSeek-V3), which are designed for general conversation, knowledge Q&A, text generation, and other broad scenarios. In addition to general-purpose LLMs, there is another category of models specifically designed for "reasoning" — `Reasoning Models`.

### 5.1 What Are Reasoning Models?

You may have already learned about Alibaba Cloud's reasoning model [Qwen3](https://help.aliyun.com/zh/model-studio/deep-thinking) through the extended reading in section 2.1. For convenience in subsequent calls in this section, we've rewritten the code provided in section 2.1. You can try running the following code:

```python
from openai import OpenAI
import os

def reasoning_model_response(user_prompt, system_prompt="You are a programming assistant.", model="qwen-plus"):
    """
    prompt: User input prompt
    model: Using qwen-plus as an example, can be replaced with other reasoning model names like: deepseek-r1
    """
    # Initialize client
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_API_BASE")
    )

    # Initialize state variable
    is_answering = False

    # Make streaming request
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        extra_body={
            "enable_thinking": True,
            "thinking_budget": 4000
        },
        stream=True,
    )

    # Print thinking process title
    print("\n" + "=" * 20 + "Thinking Process" + "=" * 20 + "\n")

    # Process streaming response
    for chunk in completion:
        if chunk.choices:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                # Process thinking content
                print(delta.reasoning_content, end='', flush=True)
            else:
                # Switch to answer output mode
                if delta.content != "" and not is_answering:
                    print("\n" + "=" * 20 + "Complete Response" + "=" * 20 + "\n")
                    is_answering = True
                # Process answer content
                if delta.content:
                    print(delta.content, end='', flush=True)
```

```python
reasoning_model_response(user_prompt="Who are you?")
```


Through this example, you can see that reasoning models have an additional "`thinking process`" compared to general-purpose LLMs. It's like solving a math problem where someone first works through it step by step on scratch paper rather than giving the answer directly. This reduces "off-the-cuff" errors from the model. During the step-by-step thinking process, if a contradiction is found at a certain step, the model can go back to check and readjust its approach. Showing reasoning steps also makes it easier for people to understand and verify the logic by following the model's line of thinking.

Compared to general-purpose LLMs, reasoning models are usually more reliable when solving complex problems, such as in scenarios requiring rigorous reasoning like math problem solving, code writing, or legal case analysis. This doesn't mean reasoning models are always better—both types of models have their respective use cases. The following table compares these two types of models across some typical dimensions:

| Dimension | Reasoning Model | General-Purpose Model |
|-----------|-----------------|----------------------|
| Design Goal | Focused on **logical reasoning, multi-step problem solving, mathematical calculations** and other tasks requiring deep analysis | Oriented toward **general conversation, knowledge Q&A, text generation** and other broad scenarios |
| Training Data Focus | Large amounts of **math solutions, code logic, scientific reasoning** datasets to enhance reasoning ability | Covers **encyclopedias, literature, conversations** and massive data from multiple domains |
| Typical Output Characteristics | Output includes **complete derivation** steps, emphasizing the completeness of logical chains | Output is **concise and direct**, focusing on natural language expression of results |
| Response Speed | Complex reasoning tasks **respond slower** (requires multi-step calculations) | Regular tasks **respond faster** (primarily single-step generation) |

Reasoning model or general-purpose model? How to choose? Here are some recommendations:
- **Clear general tasks**: For clearly defined problems, **general-purpose models** can usually handle them well.
- **Complex tasks**: For very complex tasks that require relatively **more precise and reliable** answers, **reasoning models** are recommended. These tasks might be:
    - Ambiguous tasks: Very little information related to the task, and you cannot provide the model with relatively clear guidance.
    - Needle in a haystack: Passing large amounts of unstructured data to extract the most relevant information or find correlations/differences.
    - Debugging and improving code: Need to review and further debug, improve large amounts of code.
- **Speed and cost**: Generally speaking, reasoning models take longer for inference. If you're sensitive to time and cost and the task complexity isn't high, **general-purpose models** might be a better choice.

Of course, you can also combine both types of models in your application: use reasoning models for Agent planning and decision-making, and use general-purpose models for task execution.

### 5.2 Prompt Techniques Suitable for Reasoning Models

Reasoning models can provide detailed and well-formatted responses even when facing relatively ambiguous tasks. You can still use **prompt techniques** to ensure a baseline quality for reasoning model inference:

#### Technique 1: Keep task prompts concise and clear, provide sufficient background information

The **clear expression of requirements** introduced in section 4.1 also applies to reasoning models. Although reasoning models are very capable, they cannot "read minds." You need to keep prompts **concise and clear** so the reasoning model can focus on the core task.

```python
bad_prompt="""
def example(a):
  b = []
  for i in range(len(a)):
    b.append(a[i]*2)
  return sum(b)
"""

reasoning_model_response(user_prompt=bad_prompt)
```

Through the above example, you can see that even if you only give the reasoning model a piece of code, it can still provide a very rich answer through a series of reasoning. However, the returned reasoning may contain a lot of information you don't care about. You can try to clarify the **task objective** to get more targeted suggestions:

```python
prompt_A="""
What's wrong with the following Python code? How can it be optimized?
def example(a):
  b = []
  for i in range(len(a)):
    b.append(a[i]*2)
  return sum(b)
"""

reasoning_model_response(user_prompt=prompt_A)
```

Similarly, you can further limit the scope by combining techniques from section **4.2 Defining Role and Audience** and **4.3 Specifying Output Format** to ensure results meet your expectations.

Also, if the prompt is complex, you can use **delimiters** to help the model understand your intent.

```python
prompt_B="""
<audience>Junior Python Developer</audience>

<task>Function performance optimization, optimize the code in code.</task>

<format>
If there are multiple optimization solutions, please output in the following format:
【Optimization Solution X】
Problem Description: [Description]
Optimization Solution: [Description]
Sample Code: [Code Block]
</format>

<code>
def example(a):
  b = []
  for i in range(len(a)):
    b.append(a[i]*2)
  return sum(b)
</code>
"""

reasoning_model_response(user_prompt=prompt_B)
```

#### Technique 2: Avoid Chain-of-Thought Prompting

In section 4.5, you learned about using Chain-of-Thought (COT) techniques to make LLMs think deeply and improve response quality.

Generally, you don't need to prompt reasoning models to "think step by step" or "explain your reasoning" because they inherently engage in deep thinking. Your prompting might actually limit the reasoning model's performance. Unless you need the model to reason strictly according to a fixed approach—which rarely happens.

#### Technique 3: Adjust Prompts Based on Model Responses

Reasoning models, because of their response format (including the **thinking process**), are naturally suited for you to analyze their thinking and reasoning process, making it easier for you to adjust prompts.

Therefore, you don't need to worry about whether the prompt is perfect enough. Just keep conversing with the reasoning model, supplementing information and refining the prompt along the way.

For example, when your description is **too abstract** or you **cannot describe accurately**, you can use the **adding examples** technique from section 4.4 to clarify this information. These examples can sometimes be selected from the conversation history with the model.

This process can be repeated multiple times—keep trying and adjusting prompts, letting the model reason and iterate, until it meets your requirements.

#### Technique 4: Let Reasoning Models Be Your "Prompt Coach"

In section 4.6, you learned about **Meta Prompting**—letting LLMs help you optimize prompts. So, which type of model is best suited to play the role of this "coach"?

The answer is **reasoning models**.

Because reasoning models excel at step-by-step thinking and logical derivation, they perform particularly well at analyzing the pros and cons of a prompt and systematically proposing improvement suggestions. They can not only give you a better prompt but also clearly show "why" this change would be better, allowing you to learn the essence of prompt engineering during the optimization process.

Let's revisit the example from section 4.6, but this time, we'll use the `reasoning_model_response` function defined in section 6.1 to act as our prompt coach.

```python
# We'll reuse the company benefits scenario from section 4.6
retrieved_text = """
Regarding company benefits, we provide comprehensive health insurance covering employees and their immediate family members.
Annual health checkups are standard. Additionally, there are 15 days of paid annual leave and 5 days of paid sick leave per year.
We also provide a monthly transportation subsidy of 500 yuan and a meal subsidy of 300 yuan.
To encourage employee growth, the company has an annual education and training fund of up to 8000 yuan, which employees can apply to use for courses or professional books.
For fitness, the company has partnerships with multiple gyms where employees can enjoy discounted rates.
"""

# Initial, relatively simple prompt
initial_prompt = f"""
Based on the following information, answer new employees' questions about company benefits.

【Reference Information】
{retrieved_text}
"""

# Assume this is the less-than-ideal output from a general-purpose model
initial_response = """
Our company provides comprehensive health insurance covering employees and their families. There are 15 days of paid annual leave and 5 days of sick leave per year. There's also a monthly 500 yuan transportation subsidy and 300 yuan meal subsidy. The company provides an 8000 yuan annual education fund and has partnership discounts with gyms.
"""

# Build our Meta Prompt, requesting the reasoning model to help optimize
meta_prompt_for_reasoning = f"""
I'm optimizing a prompt for our company's new employee Q&A bot, with the goal of answering questions about "company benefits."

This is my first attempt:
---\n{initial_prompt}\n---

This is the output it generated:
---\n{initial_response}\n---

This output isn't good enough. I want the bot's responses to be more engaging, clearly structured, and help new employees quickly grasp the key points. Specific requirements:
1. **Tone**: Friendly, warm, with a welcoming feeling for new colleagues.
2. **Structure**: Use clear bullet points (e.g., lists starting with emojis) to organize content.
3. **Content**: Categorize benefits into groups like "Health & Leave," "Subsidies & Incentives," etc.

Please act as a prompt engineering expert and rewrite this prompt to achieve the above goals.
In your final answer, only provide the optimized prompt itself, without any other explanatory text.
"""

# Use reasoning model to get optimization suggestions
reasoning_model_response(user_prompt=meta_prompt_for_reasoning, system_prompt="You are a top-tier prompt engineering expert.")
```



Through the above example, you can clearly see how the reasoning model analyzes the shortcomings of the original prompt step by step and, combined with our requirements (friendly tone, clear structure, engaging content, etc.), ultimately constructs an optimized prompt with more rigorous structure and clearer intent.

This fully demonstrates the importance of using the right tool for the right task. Behind this is the trade-off between **task complexity** and **execution cost (time and money)**:

- **General-Purpose Models (Non-Reasoning Models)**:
    - **Advantages**: Fast execution speed, lower cost.
    - **Use Cases**: Suitable for executing relatively straightforward, clearly defined tasks, such as information extraction, format conversion, or simple Q&A based on an already-optimized prompt.

- **Reasoning Models**:
    - **Advantages**: Excel at handling complex, ambiguous, or tasks requiring deep logical derivation.
    - **Use Cases**: More suitable for executing "meta-tasks," such as analyzing and optimizing the definition of another task (i.e., the prompt itself), complex planning, or debugging code.
    - **Cost**: Due to the need for multi-step thinking, response time is usually longer and costs are relatively higher.

When building your own LLM applications, **hybrid use of both types of models** is often the strategy for achieving the best cost-effectiveness. You can learn from this approach to build an intelligent system with "clear division of labor":

When tasks require deep thinking or planning, bring in reasoning models to act as the "**Planner**" or "**Analyst**" role, letting them decompose complex tasks or optimize workflows; then, hand off the decomposed, simpler subtasks to **general-purpose models** or other tools for efficient, low-cost execution. This collaborative model allows you to maintain high-quality output while effectively controlling application response time and operating costs.

## ✅ Section Summary

Through studying this section, you've mastered more advanced techniques in **Context Engineering**, from designing fine-grained prompts to implementing intelligent intent routing. Looking back at the past two sections, we've equipped the Q&A bot with two core capabilities:

1. **Knowledge Filling (via RAG)**: Solved the problem of the model "not knowing" private information.
2. **Behavior Guidance (via Prompts and Control Flow)**: Solved the problems of "how to do" and "what to do" for the model.

The common core of these techniques is the essence of context engineering:

By carefully designing and filling the model's context window to guide and control its generation of desired outputs—this is crucial for you to use LLMs effectively.

In the actual process of deploying LLM applications, the prompt part is often co-designed with domain experts. Therefore, instead of hardcoding prompts in your engineering code, you should consider making them configurable—even the application workflow can be configurable. This makes it easier for domain experts to participate in designing prompts and the entire workflow. Alibaba Cloud Model Studio provides visual [application building](https://help.aliyun.com/zh/model-studio/user-guide/application-introduction#7c79befb2djg9) capabilities, allowing prompt writing and visual construction of the entire complex application workflow on the page—very suitable for LLM application development projects that require participation from domain experts without technical backgrounds.

In the next section, you'll learn automated evaluation methods to test the Q&A bot's performance. You can use quantitative metrics to evaluate the optimization effects you've achieved through context engineering.

## 🔥 Quiz

### 🔍 Multiple choice question

<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>Which of the following prompt elements is used to explicitly define the task that the LLM needs to complete❓ (Select 1.)</b>

- A. Role
- B. Audience
- C. Objective
- D. Context

**[Click to view answer]**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference Answer: C**</br>
📝 **Explanation**:</br>
- The Objective explicitly defines the operation or outcome that the large language model (LLM) is required to perform. Other options do not directly define the task itself.
- Role defines the identity that the LLMs should assume, Audience specifies the target group, and Context provides background information.

</div>
</details>

---


<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>You have inherited a complex, undocumented prompt designed for code generation. Before directly modifying this "black-box" prompt, what preparatory steps would you take to ensure your optimization efforts are effective? (Select all that apply.)</b>

- A. Collect concrete examples of poor model output ("bad cases").
- B. Immediately start drafting a new, simpler version from scratch.
- C. Clearly define the desired output criteria and format in writing.
- D. Read through the entire prompt and try to identify logical flaws based on intuition.

**[Click to view answer]**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference Answer: A, C**</br>
📝 **Explanation**:</br>
This question tests what core inputs are necessary before starting a structured optimization process. Effective optimization requires a clear definition of the "problem" and the "goal."
- Option A (bad cases) and Option C (desired output) are the key steps for defining the "problem" and the "goal," respectively. They serve as the core inputs for a structured optimization approach like meta-prompting.
- Options B (starting from scratch) and D (relying on intuition) are high-risk, inefficient methods because they do not rely on a structured, evidence-based approach.

</div>
</details>

---

<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>When using a reasoning LLM (such as `qwen3-235b-a22b-thinking-2507`) for a complex reasoning task, which of the following prompting techniques are recommended❓ (Select all that apply.)</b>

- A. Provide simple and clear task instructions.
- B. Supplement with sufficient background information.
- C. If there are specific user groups or task requirements, define a role or audience.
- D. You must include phrases like "think step by step" or "explain your reasoning" in the prompt to activate the model's deep thinking mode.
- E. When a description is too abstract or cannot be accurately described, clarify it by adding examples.

**[Click to view answer]**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference Answer: A, B, C, E**</br>
📝 **Explanation**:</br>
- Reasoning LLMs (like `qwen3-235b-a22b-thinking-2507`) are designed to engage in deep, chain-of-thought style reasoning by default, without needing an explicit instruction to do so.

</div>
</details>
