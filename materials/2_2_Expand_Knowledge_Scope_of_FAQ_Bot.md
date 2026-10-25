# 2.2 Expanding the knowledge scope of the Q&A bot

## 🚄 Preface

You have already learned that a RAG chatbot is an effective solution for expanding the knowledge scope of LLMs. In this section, you will learn about the workflow of a RAG chatbot and how to create a RAG chatbot application so that it can answer questions based on the company's policy documents.

## 🍁 Goals

After completing this section, you will be able to:

* Understand the workflow of RAG chatbot
* Create a RAG chatbot application

## 1. How RAG works

RAG works by providing reference materials to LLMs, like an open-book exam. If a model has not encountered certain information during training, asking it related questions directly may result in inaccurate answers. However, if relevant knowledge is provided as a reference, the quality of the LLM's responses will significantly improve.

RAG applications typically consist of two parts: **indexing** and **retrieval & generation**.

### 1.1 Indexing
Indexing involves preparing reference materials for efficient retrieval. It's much like marking pages in a book so you can find the information you need during the exam. Indexing includes four steps:<br>
1. **Document Parsing**<br>
Converting documents into a text format that an LLM can process.
2. **Text Chunking**<br>
Segmenting parsed documents into smaller chunks for faster retrieval.
3. **Text Embedding**<br>
Using an embedding model to convert text chunks (or paragraphs) into numerical representations (vectors). These vectors capture the semantic meaning of the text, preparing them for future similarity comparisons.
    > If you're interested in the details of this process, you can explore the extended reading section of this tutorial.
1. **Index Storage**<br>
The resulting vectors are stored in a specialized database (a vector database) to make them efficiently searchable and avoid reprocessing the documents for every query.

    *Figure (translated): the RAG indexing pipeline.*

```mermaid
flowchart LR
    Docs["Documents"] --> Chunk["Chunking (split into segments)"]
    Chunk --> Embed["Embedding model (text → vectors)"]
    Embed --> Store[("Vector database")]
```<br>

    After indexing, RAG applications can retrieve relevant text segments based on user questions.

### 1.2 Retrieval and Generation
This phase consists of two stages: `Retrieval` and `Generation`. <br>
1. **Retrieval**<br>
This is where the user's question comes into play. First, the question is converted into a vector using the same embedding model that processed the documents. Then, the system performs a similarity search, comparing the question's vector against the vectors of the document chunks stored in the database. The chunks with the highest similarity scores are identified as the most relevant content to answer the question.
Retrieval is the most critical part of the RAG application. Just as finding the wrong material during an exam—your answer would be inaccurate. To improve retrieval accuracy, besides using powerful embedding models, techniques like reranking and sentence window retrieval can be applied.
1. **Generation**<br>
After finding the relevant information, you use it to construct your answer. Similarly, after retrieving relevant text segments, the RAG application generates the final prompt by combining the question and the retrieved text segments using a prompt template. The LLM then generates the response, leveraging its summarization abilities rather than relying solely on its internal knowledge.
    > A typical prompt template is: `Please answer the user's question based on the following information: {retrieved text segments}. The user's question is: {question}.`

    *Figure (translated): the RAG retrieval-and-generation pipeline.*

```mermaid
flowchart LR
    Q["User question"] --> E["Embedding model"]
    E --> S["Similarity search in vector DB"]
    S --> K["Top-k relevant chunks"]
    K --> P["Prompt template: question + chunks"]
    P --> M["LLM generates the answer"]
```<br>

## 2. Creating a RAG application

Building a RAG application by implementing the functionalities described above can be a complex process. However, with LlamaIndex, you can complete these tasks with minimal code.

### 2.1 Confirm your Python environment

Before running the code in this section, ensure you are using the correct Python environment, such as the `Python (llm_learn)` environment created in  previous lessons.

*(Screenshot: DSW notebook showing how to check/switch the Python environment (`Python (llm_learn)`).)*

**Note: In each subsequent lesson, you should check whether you need to manually switch the Notebook environment.**

### 2.2 A simple RAG chatbot

As in the previous section, you must configure the Model Studio API Key in your environment.

```python
# Load the API Key and choose environment for invoking the Qwen LLM
# If you are using Alibaba Cloud International set "Y"
import os
from config.load_key import load_key, display_config_summary
load_key()
display_config_summary()
```

```text
Your configured API Key is: sk-98*****
```

In the docs folder, you'll find some fictional company policy documents we've prepared. Next, you will create a RAG application based on these documents.

```python
# Import dependencies
from llama_index.embeddings.dashscope import DashScopeTextEmbeddingModels
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding

# Note: LlamaIndex uses NLTK for text preprocessing by default, but in some environments, it may fail to download due to network issues.
# Setting the environment variable LLAMA_INDEX_DISABLE_NLTK to 1 can disable the use of NLTK.
import os
os.environ["LLAMA_INDEX_DISABLE_NLTK"] = "1"

# These two lines of code are used to suppress WARNING messages to avoid interference with reading and learning. It is recommended to set the log level as needed in a production environment.
import logging
logging.basicConfig(level=logging.ERROR)

print("Parsing files...")
# LlamaIndex provides the SimpleDirectoryReader method, which can directly load files from a specified folder into document objects, corresponding to the parsing process.
# Read only the document formats required for this QA example, and skip notebook files to avoid slower nbconvert parsing.
documents = SimpleDirectoryReader('./docs', required_exts=['.pdf', '.docx', '.md']).load_data()

print("Creating index...")
# The from_documents method includes slicing and index creation steps.
index = VectorStoreIndex.from_documents(
    documents,
    # Specify embedding model
    # embed_model=DashScopeEmbedding(
    embed_model=OpenAILikeEmbedding(
        api_base=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        # You can also use other embedding models provided by Alibaba Cloud: https://www.alibabacloud.com/help/en/model-studio/models#501f1077663lv
        # model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3
    ))
print("Creating query engine...")
query_engine = index.as_query_engine(
    # Set to streaming output
    streaming=True,
    # Here we use the qwen-plus model. You can also use other Qwen text generation models provided by Alibaba Cloud: https://www.alibabacloud.com/help/en/model-studio/models#0c050ec6b1aaw
    llm=OpenAILike(
        model="qwen-plus",
        api_base=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        is_chat_model=True
        ))
print("Generating response...")
streaming_response = query_engine.query('What tools should our company use for project management?')
print("The answer is:")
# Use streaming output
streaming_response.print_response_stream()
```

```text
Parsing files...
Creating index...
Creating query engine...
Generating response...
The answer is:
For project management, your company should use the following tools based on the information provided:

- **Asana** for coordinating tasks, particularly when working with Instructional Designers.
- **Jira** for participating in daily standups and managing interactions with technical teams.
- **HubSpot** for aligning launch strategies, particularly in collaboration with marketing efforts.
- **GitLab** for content version tracking and maintaining a data-driven version control process.
- **Miro whiteboards** for requirement gathering and stakeholder mapping during the needs analysis phase.
- **Confluence** for creating and documenting requirement specifications.

These tools support efficient task tracking, collaboration, version control, and stakeholder engagement across departments.
```

### 2.3 Saving and loading index
Creating an index can be time-consuming. To avoid repeating this process, you can save the index locally and reload it when needed. This improves response speed and avoids rebuilding the index from scratch. LlamaIndex provides an easy-to-implement method for saving and loading indexes.

```python
# Save the index as a local file
index.storage_context.persist("knowledge_base/test")
print("Index files saved to knowledge_base/test")
```

```text
Index files saved to knowledge_base/test
```

```python
# Load the local index file as an index
from llama_index.core import StorageContext, load_index_from_storage
storage_context = StorageContext.from_defaults(persist_dir="knowledge_base/test")
index = load_index_from_storage(storage_context, embed_model=OpenAILikeEmbedding(
        api_base=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3
    ))
# index = load_index_from_storage(storage_context, embed_model=OpenAILikeEmbedding(
#         model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2
#     ))
print("Successfully loaded index from knowledge_base/test path")
```

```text
Successfully loaded index from knowledge_base/test path
```

After loading the index locally, test it by asking questions.

```python
print("Creating the query engine...")
query_engine = index.as_query_engine(
    # Set to streaming output
    streaming=True,
    # Use the qwen-plus model here. You can also use other text generation models provided by Alibaba Cloud: https://www.alibabacloud.com/help/en/model-studio/models#0c050ec6b1aaw
    llm=OpenAILike(
        model="qwen-plus",
        api_base=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        is_chat_model=True
        ))
print("Generating response...")
streaming_response = query_engine.query('What tools should our company use for project management?')
print("The answer is:")
streaming_response.print_response_stream()
```

```text
Creating the query engine...
Generating response...
The answer is:
For project management, the company should use Asana for coordinating tasks, Jira for participating in daily standups with technical teams, and HubSpot for aligning launch strategies. Additionally, Miro whiteboards can be utilized for stakeholder mapping during requirement gathering, and Confluence can be used for creating requirement specifications.
```

Encapsulate the above code so for quick reuse in subsequent iterations.

```python
from chatbot import rag

# The citations have been indexed in previous steps, so the index can be loaded directly here. If you need to rebuild the index, you can add a line of code: rag.indexing()
index = rag.load_index(persist_path='./knowledge_base/test')
query_engine = rag.create_query_engine(index=index)

rag.ask('What tools should our company use for project management?', query_engine=query_engine)
```

```text
For project management, the company should use tools such as Asana for task tracking and Jira for daily standups. These tools facilitate coordination among instructional designers and technical teams, ensuring efficient and organized project execution.
```

### 2.4 Multi-turn conversation
The mechanism for multi-turn conversations in RAG differs from how they work in direct interactions with LLMs. As you learned in Section 2.1, multi-turn conversations allow LLMs to refer to conversation history. This is typically done by including the history in the messages list.

During the retrieval phase in RAG applications, the system typically compares the semantic similarity between the user's input and the text segments. However, if the system only uses the user's latest input for retrieval, it can lose important context from the conversation history, leading to inaccurate results.

For example, a user asks "Where is Jimmy Peterson's workstation?" in the first turn,  then asks "Who is his supervisor?" in the second turn. The retrieval system may not know who “he” refers to if it only compares the second question with the text segments. This could lead to retrieving incorrect content.

If both the full historical dialogue and the question are input into the retrieval system, the retrieval system may struggle due to the text length, (embedding models perform worse on long texts than on short ones). A common industry solution is:

1. Use the LLM to rewrite the query based on the historical dialogue, incorporating key information from the conversation.
2. Use the rewritten query to follow the original retrieval and generation process.

LlamaIndex provides convenient tools that make it easy to implement multi-turn conversations in RAG applications.

```python
from llama_index.core import PromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.chat_engine import CondenseQuestionChatEngine

custom_prompt = PromptTemplate(
    """
    Given a conversation (between a human and an assistant) and a follow-up message from the human,
    rewrite the message as a standalone question that includes all relevant context from the conversation.

    <Chat History>
    {chat_history}

    <Follow-up Message>
    {question}

    <Standalone Question>
"""
)

# Historical conversation information
custom_chat_history = [
    ChatMessage(role=MessageRole.USER,content="What are the subtypes of content development engineers?"),
    ChatMessage(role=MessageRole.ASSISTANT, content="Comprehensive technical positions."),
]

query_engine = index.as_query_engine(
    # Set to streaming output
    streaming=True,
    # Use the qwen-plus model here; you can also use other text generation models provided by Alibaba Cloud: https://www.alibabacloud.com/help/en/model-studio/models#0c050ec6b1aaw
    llm=OpenAILike(
        model="qwen-plus",
        api_base=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        is_chat_model=True
        ))
chat_engine = CondenseQuestionChatEngine.from_defaults(
    query_engine=query_engine,
    condense_question_prompt=custom_prompt,
    chat_history=custom_chat_history,
    llm=OpenAILike(
        model="qwen-plus",
        api_base=os.getenv("DASHSCOPE_API_BASE"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        is_chat_model=True
        ),
    verbose=True
)

streaming_response = chat_engine.stream_chat("What are the core responsibilities?")
for token in streaming_response.response_gen:
    print(token, end="")
```

```text
Querying with: What are the core responsibilities of content development engineers, including all relevant context from the previous discussion?
Content development engineers are responsible for integrating educational theory with technical practice to support learners' growth through high-quality content creation. Their core responsibilities include:

1. **Educational Innovation & Market Alignment**: Conducting in-depth research on educational technology trends, learning theories, and market demands. This involves analyzing competitors' products, evaluating existing educational resources, and exploring the integration of emerging technologies like artificial intelligence and virtual reality into educational content. They ensure content remains technologically advanced and aligned with the needs of educators and learners.

2. **Curriculum Design & Development**: Designing and developing high-quality educational materials and courses based on research and market feedback. This includes creating syllabi, courseware, and assessment tools while ensuring alignment with educational standards and learning objectives. Consideration is given to diverse learner needs to accommodate various learning styles and levels.

3. **Content Optimization and Updates**: Continuously optimizing existing educational materials by tracking learner feedback and evaluations to identify and address issues. Regular updates are made to reflect new research findings, technological advancements, and market changes, ensuring the content remains timely and relevant.

4. **Implementation of Advanced Tools and Standards**: Utilizing tools and standards such as adaptive learning engines, NLP-powered chatbots, authoring tools (e.g., Articulate 360, Lectora Inspire, Camtasia), and compliance standards (e.g., SCORM, xAPI, WCAG 2.1) to enhance the quality and accessibility of educational content.

These responsibilities ensure that the content development engineer contributes to both learner success and organizational growth through innovative learning solutions.
```

Although the last question did not mention "content development engineer," the LLM still rewrote the question based on the historical dialog information, rephrasing it as "What are the core responsibilities of a content development engineer?" and provided the correct answer.

## 📝 3. Section Summary

Here's what we covered in this section:

1. **How RAG Works**<br>
A complete RAG application typically involves two main phases: Indexing and Retrieval & Generation.

* The Indexing phase includes four steps: Document Parsing, Text Chunking, Text Embedding, and Index Storage.

By understanding how RAG works, you can better optimize and improve your RAG chatbot.

2. **Building a RAG Application**<br>
Using the highly integrated tools provided by LlamaIndex, you built a RAG application and learned how to save and load indexes.

3. **Implementing Multi-Turn Conversations in RAG**<br>
You learned about the unique challenges of multi-turn conversations in RAG (context loss during retrieval) and the common industry solution (question rewriting). Through LlamaIndex's CondenseQuestionChatEngine, you implemented a RAG application capable of understanding conversational context.

Although the RAG chatbot can already answer questions like "What tools should our company use for project management?" quite well, its current functionality is still quite basic. In upcoming tutorials, we will explore ways to expand the capabilities of the RAG chatbot. The next section will focus on improving the quality of the RAG chatbot's responses through prompt optimization.

### Further reading

#### Text Embedding (Vectorization)
Computers cannot directly grasp the semantic similarity between two sentences such as "I like  apples" and "I love apples." However, they can calculate the mathematical similarity between two numerical vectors of the same dimension, usually using cosine similarity. 

Text vectorization converts natural language into numerical forms that computers can process, using embedding models. These models are trained using a technique called **contrastive learning**, where the input data consists of many text pairs (s1, s2), each labeled as  related or unrelated. The model's goal is to maximize the similarity score for related text pairs while minimizing it for unrelated ones.

During the **indexing** phase, after text chunking produces n chunks (such as [c1, c2, c3, ..., cn]), an embedding model converts them into corresponding vectors ([v1, v2, v3, ..., vn]), which are then stored in a vector database.

In the **retrieval** phase, when a user asks a question q, the embedding model converts it into a vector vq. It then finds the k most similar vectors to vq in the vector database (where k is a configurable parameter, often called top_k). Through the relationship between these vectors and their corresponding text chunks, the relevant text chunks are retrieved as search results.

## 🔥 Quiz

### 🔍 Single choice question

<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>How should retrieval be conducted during multi-turn conversations in RAG applications❓ (Select 1.)</b>

- A. Use the entire conversation history as the query for retrieval<br>
- B. Rewrite the user's latest query based on the conversation history before performing retrieval<br>
- C. Input the latest question during the retrieval phase<br>
- D. Migrate the text chunks recalled from the previous turn<br>

**[Click to view the answer]**
</summary>

<div style="margin-top: 10px; padding: 15px;  border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference Answer: B**  
📝 **Explanation**:  
- Directly using the user's latest query (Option C) can fail because it lacks context, while using the full history (Option A) can introduce noise and is inefficient.
- Reusing chunks from a previous turn (Option D) is risky, as they may not be relevant to the new query.
- Therefore, Option B (rewriting the query) is the best practice, as it incorporates necessary context from the history while creating a concise and relevant query for accurate retrieval.

</div>
</details>
