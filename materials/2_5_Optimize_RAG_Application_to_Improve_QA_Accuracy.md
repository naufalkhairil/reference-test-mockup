# 2.5 Optimizing RAG applications to improve question-answer accuracy

## 🚄 Preface  

In previous lessons, you have already identified some issues with the RAG chatbot through automated evaluations. However, optimizing prompts alone cannot fix problems caused by **inaccurate retrieval**, just as it would be difficult to provide the correct answer during an open-book exam if you were using the wrong reference material.

In this section, you will gain a deeper understanding of the **RAG workflow** and work on improving the **accuracy of your RAG application’s question-answering**. This involves refining both the **retrieval** and **generation** phases to ensure that the model not only finds relevant information but also uses it effectively to produce accurate and reliable responses.

## 🍁 Goals

After completing this course, you will be able to:

* Gain a deeper understanding of the implementation principles and technical details of RAG
* Understand common issues with RAG applications and recommended solutions
* Improve the performance of RAG applications through hands-on case studies

## 1. Previous content recap

In the previous chapter, you discovered that the Q&A bot was unable to adequately answer the question: "Which department is Michael Johnson from?" You can reproduce the issue using the following code:

```python
from tqdm.cli import tqdm as tqdm_cli
import tqdm.auto
tqdm.auto.tqdm = tqdm_cli

# Import the required dependency packages
import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from config.load_key import load_key
import logging
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, PromptTemplate
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.embeddings.dashscope import DashScopeTextEmbeddingModels
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
    SentenceWindowNodeParser,
    MarkdownNodeParser,
    TokenTextSplitter
)
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_recall, context_precision, answer_correctness
from chatbot import rag
from IPython.display import display
```

```python
# Set log level
logging.basicConfig(level=logging.ERROR)
```

```python
import os
from config.load_key import load_key, display_config_summary
load_key()
display_config_summary()
```

```python
# Configure the Qwen LLM and text vector model
Settings.llm = OpenAILike(
    model="qwen-plus",
    api_base=os.getenv("DASHSCOPE_API_BASE"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    is_chat_model=True
)
```

```python
# Configure text vector model, set batch size and maximum input length
Settings.embed_model = OpenAILikeEmbedding(
    api_base=os.getenv("DASHSCOPE_API_BASE"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3
)
```

```python
# Define the question-answering function
def ask(question, query_engine):
    # Update the prompt template
    rag.update_prompt_template(query_engine=query_engine)

    # Output the question
    print('=' * 50)  # Generate a dividing line using multiplication
    print(f'🤔 Question: {question}')
    print('=' * 50 + '\n')  # Generate a dividing line using multiplication

    # Get the answer
    response = query_engine.query(question)

    # Output the answer
    print('🤖 Answer:')
    if hasattr(response, 'print_response_stream') and callable(response.print_response_stream):
        response.print_response_stream()
    else:
        print(str(response))

    # Output reference documents
    print('\n' + '-' * 50)  # Generate a dividing line using multiplication
    print('📚 Reference Documents:\n')
    for i, source_node in enumerate(response.source_nodes, start=1):
        print(f'Document {i}:')
        print(source_node)
        print()

    print('-' * 50)  # Generate a dividing line using multiplication

    return response
```

```python
query_engine = rag.create_query_engine(rag.load_index())
response = ask('What does Michael Johnson do?', query_engine)
```

You will find that the reason for this issue is that the correct reference information (document chunks) was not recalled during the retrieval phase. To improve this issue, you can apply a few simple strategies to preliminarily optimize the retrieval effect.

## 2. Initial optimization

As mentioned in the introduction, you need to ensure that the LLM has access to the correct "reference materials" to provide accurate "answers." Therefore, you can try increasing the number of "reference materials" retrieved or organizing the "knowledge points" in the reference materials into structured tables. You can start with the former:

### 2.1 Allowing LLMs to access more reference information

Since the knowledge base contains information about Michael Johnson's employment history, you can expand the search scope and increase the probability of finding relevant information by recalling more document chunks. In the previous code, only 2 document chunks were retrieved. Now, you can increase the number of recalled chunks to 5 and observe whether the retrieval performance improves.

#### 2.1.1 Adjusting the code

You can configure the following settings to allow the retrieval engine to recall the top 5 most relevant document chunks.

```python
index = rag.load_index()
query_engine = index.as_query_engine(
    streaming=True,
    # Retrieve 5 document chunks at once, default is 2
    similarity_top_k=5
)
```

```python
response = ask('What does Michael Johnson do?', query_engine)
```

As you can see, after adjusting the number of recalls, your Q&A bot is now able to answer the question "*Which department is Michael Johnson in?*" This is because the recalled document chunks already contain information about Michael Johnson and his department.

However, simply increasing the number of recalled chunks is not a good solution. If this method could solve the problem, why not recall the entire knowledge base? That way, no information would be missed. But this would not only exceed the LLM's input length limit, but also reduce the efficiency and accuracy of the model's responses due to excessive irrelevant information.

In fact, there may be many colleagues named Michael Johnson in your company, which leads to another issue: when a user asks "**Which department is Michael Johnson in?**" , the system cannot determine which Michael Johnson the user is referring to. Simply increasing the number of recalls might retrieve information about multiple Michael Johnsons, but the system would still be unable to accurately decide which one's information to return. Therefore, we need to use other methods to further improve the RAG chatbot.

#### 2.1.2 Evaluate improvement effectiveness

To quantify the effectiveness of improvements in subsequent enhancements, you can continue to use Ragas from the previous chapter for evaluation. Suppose your company has three colleagues named Michael Johnson, who respectively work in the Teaching and Research, Course Development, and IT Department.

```python
import os

from langchain_openai import ChatOpenAI
from chatbot.evaluate import RagasOpenAICompatibleEmbeddings

# Define evaluation function
def evaluate_result(question, response, ground_truth):
    # Get the response content
    if hasattr(response, 'response_txt'):
        answer = response.response_txt
    else:
        answer = str(response)
    # Get the retrieved context
    context = [source_node.get_content() for source_node in response.source_nodes]

    # Construct evaluation dataset
    data_samples = {
        'question': [question],
        'answer': [answer],
        'ground_truth': [ground_truth],
        'contexts': [context],
    }
    dataset = Dataset.from_dict(data_samples)

    # Evaluate using Ragas
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
    return score.to_pandas()
```

```python
question = 'What does Michael Johnson do?'
ground_truth = '''There are three Michael Johnsons:
- QA Specialist in the Course Development Department: Email michael.j@educompany.com, responsible for system validation testing.  
- Technical Writer in the Course Development Department: Email michael.johnson@educompany.com, responsible for documentation creation.  
- System Administrator in the Course Development Department: Email michael.j2@educompany.com, responsible for server maintenance.
'''
```

```python
evaluate_result(question=question, response=response, ground_truth=ground_truth)
```

As you can see, the current RAG system is still unable to operate efficiently. The retrieved document chunks contain irrelevant information, and the relevant information has not been fully recalled, resulting in an incorrect final answer. You must consider other improvement strategies.

### 2.2 Provide more structured reference information

In practical applications, the organizational structure of a document significantly impacts retrieval performance. Imagine this: the same information is placed either in a well-structured table or scattered throughout a block of plain text. Which one would be easier to locate and understand? Clearly, the former.

The same applies to LLMs. When information originally presented in a table is converted into plain text, although no information is lost, its structure is diminished. This is akin to turning an organized drawer into a pile of scattered items—while everything is still there, it becomes less convenient to find things.

#### 2.2.1 Rebuild the Index

Markdown format is a great choice because it:
* Has a clear structure and well-defined hierarchy
* Simple syntax, making it easy to read and maintain
* Is particularly suitable for organizing documents in RAG chatbot scenarios

To validate the effectiveness of structured documents,  an optimized Markdown format file has been prepared for you. Next, you will:

1. Add this Markdown file to the docs directory
2. Rebuild the index
3. Test the improvement in retrieval performance

```python
# Copy the markdown formatted employee information document to the ./docs directory
! mkdir -p ./docs/2_5
! cp ./resources/2_4/Employee\ Key\ Contact\ Information.md ./docs/2_5
```

```python
print('=' * 50)
print('📂 Loading documents...')
print('=' * 50 + '\n')

# Load documents
documents = SimpleDirectoryReader('./docs/2_5').load_data()
print(f'✅ Document loading completed.\n')

print('=' * 50)
print('🛠️ Rebuilding index...')
print('=' * 50 + '\n')

# Rebuild index
index = VectorStoreIndex.from_documents(
    documents
)
print('✅ Index rebuilding completed!')

print('=' * 50)
```

```python
query_engine = index.as_query_engine(
    streaming=True,
    similarity_top_k=5
)
```

```python
response = ask('What does Michael Johnson do?', query_engine)
```

#### 2.2.2 Evaluate improvement effect

You can see that your Q&A bot can accurately answer this question. You can run the Ragas evaluation again, and the evaluation data will also show that the answer accuracy has improved.

```python
evaluate_result(question=question, response=response, ground_truth=ground_truth)
```

## 3. Familiarize yourself with the RAG workflow

So far, you have made some improvements to increase the RAG chatbot's Q&A accuracy. However, in a real production environment, the problems you may encounter go far beyond this. Previously, you have already learned about some of the RAG workflow. Here, you can review the important steps to help you identify new areas for improvement:

RAG is a technology that combines information retrieval and generative models, allowing it to leverage relevant information from an external knowledge base when generating answers. Its workflow can be divided into several key steps: parsing and chunking, vector storage, retrieval recall, and answer generation. You can refer back to the section "Expanding the Knowledge Scope of the RAG chatbot" for specific concepts.

<img src="https://img.alicdn.com/imgextra/i1/O1CN01zk9HW723iQ11MXgEJ_!!6000000007289-2-tps-5205-2710.png" alt="RAG Working Principle" width="800px">

Next, we will focus on each step of RAG, and optimize its performance.

## 4. Stages of RAG chatbot and improvement strategies

### 4.1 Document preparation stage

In traditional customer service systems, customer service personnel accumulate a knowledge base based on the questions raised by users, and share it with other staff for reference. This process is equally essential when building a RAG chatbot.

* **Intent space**: We can map the needs behind user questions as points, which together form a user intent space.
* **Knowledge space**: The knowledge points accumulated in the knowledge base documents constitute a knowledge space. These knowledge points can be a paragraph or a chapter.

When we project the intent space and knowledge space together, we find that there are overlaps and differences between the two spaces. These areas correspond to our three subsequent optimization strategies:

1. **Overlapping area**:
    * This refers to parts where user questions can be answered based on the content of the knowledge base, forming the foundation of ensuring the effectiveness of the RAG chatbot.
    * For these user intents, you can continuously improve the quality of responses through optimizing content quality, engineering, and algorithms.
2. **Uncovered intent space**:
    * Due to the lack of supporting content in the knowledge base, LLMs tend to generate hallucinations. For example, if the company has added a new "Data Analysis Department," but there are no related documents in the knowledge base, no matter how much you improve the engineering algorithms, the RAG chatbot will not be able to accurately answer this question.
    * What you need to do is proactively supplement the missing knowledge, and continually track changes in the user intent space.
3. **Unused knowledge space**:
    * Recalling irrelevant information may interfere with the LLM's responses.
    * Therefore, you need to optimize the recall algorithm to avoid recalling unrelated content. Additionally, you should periodically check the knowledge base and remove irrelevant content.

<img src="https://img.alicdn.com/imgextra/i2/O1CN01Icn1Bt1tDbCqYa94M_!!6000000005868-2-tps-2122-1176.png" alt="RAG Intent Space to Knowledge Space" width="1000px">

Before attempting to optimize engineering or algorithms, you should prioritize building a mechanism that continuously collects user intents. By systematically gathering real user needs to enrich the knowledge base content and involving domain experts with deep understanding of user intents in the evaluation process, a closed-loop optimization process of "data collection - knowledge update - expert validation" is formed to ensure the effectiveness of the RAG chatbot.

Once you have prepared these, you can further optimize various stages of the RAG chatbot.

### 4.2 Document parsing and chunking phase

The RAG application first parses your document, then divides the content into chunks.

If the document chunks that the LLM receives when answering questions lack key information, the response may be inaccurate. Similarly, if the  chunks contain too much irrelevant information (noise), it will also affect the quality of the response. In other words, either too little or too much information can impact the model's ability to generate effective responses.

Therefore, during the document parsing and chunking phase, it is essential to ensure that the final chunks contain complete and relevant information without including excessive interfering content.

#### 4.2.1 Problem classification and improvement strategies

During the document parsing and chunking phase, you may encounter the following issues:

<table border="1">
  <thead>
    <tr>
      <th>Category</th>
      <th>Subtype</th>
      <th>Improvement Strategy</th>
      <th>Scenario Example</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3">Document Parsing</td>
      <td>Non-uniform document types. Some formats are not supported for parsing; for example, SimpleDirectoryLoader used earlier does not support Keynote files.</em></td>
      <td>Develop a parser for the corresponding format or convert the document format.</td>
      <td>A company uses a large number of Keynote files to store employee information, but the existing parser does not support the Keynote format. A Keynote parser can be developed, or the files can be converted into a supported format (such as  PDF).</td>
    </tr>
    <tr>
      <td>Within the already supported document formats, there is some special content, such as embedded tables, images, and videos.</em></td>
      <td>Improve the document parser.</td>
      <td>A document contains many tables and images, and the current parser cannot correctly extract information from the tables. The parser can be improved to handle tables and images.</td>
    </tr>
    <tr>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <td rowspan="4">Document Chunking</td>
      <td>The document contains much content with similar themes. For example, in a work manual, each stage, including requirements analysis, development, and release, has precautions and operational guidance.</em></td>
      <td>Expand document titles and subtitles: "Precautions" => "Requirements Analysis > Precautions"; create document metadata (tagging).</td>
      <td>A document contains precautions for multiple stages. When a user asks, "What are the precautions for requirements analysis?" the system returns precautions for all stages. Titles can be expanded and tagging can be used to distinguish content across different stages.</td>
    </tr>
    <tr>
      <td>Document chunks are too long, introducing excessive noise.</td>
      <td>Reduce chunk length, or develop more suitable chunking strategies based on specific business needs.</td>
      <td>A document's chunks are too long and contain multiple unrelated topics, resulting in irrelevant information being returned during retrieval. Chunk length can be reduced to ensure that each chunk contains only one topic.</td>
    </tr>
    <tr>
      <td>Document chunks are too short, truncating useful information.</td>
      <td>Increase chunk length, or develop more suitable chunking strategies based on specific business needs.</td>
      <td>Each chunk in a document contains only one sentence, making it impossible to retrieve complete context during search. Chunk length can be increased to ensure that each chunk contains complete context.</td>
    </tr>
    <tr>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
  </tbody>
</table>

#### 4.2.2 Parsing PDF files using Model Studio

In previous sections, we provided a Markdown document converted from a PDF so that you could quickly see the effects of format conversion. However, in real-world work scenarios, writing code to properly convert PDFs into Markdown is not an easy task.

Next, we will use pymupdf4llm to handle this conversion for us. With just a few lines of code, you can extract Markdown-formatted text directly from a PDF file and inspect the result.

Below is a minimal example that reads a PDF and prints the first 200 characters of the converted Markdown:

```python
# %pip install pymupdf4llm==0.2.6
```

```python
import pymupdf4llm

md_content = pymupdf4llm.to_markdown("./docs/Employee Key Contact Information.pdf")
print("Parsed Markdown text (first 200 characters):")
print("-"*100)
print(md_content[:200])
```

Due to the diversity of sources for various file formats such as PDF and docx, there may be some minor formatting issues during the process of parsing files into markdown. For example, table rows spanning pages in a PDF might be parsed into multiple lines.

LLMs can be used to refine the generated markdown text, correcting issues such as table of contents levels and missing information.

```python
# from dashscope import Generation
import os
from openai import OpenAI
def md_polisher(data):
    messages = [{
        'role': 'user',
        'content': 
            '''｜The following text is converted from PDF to markdown, and there may be some issues with the format and content. I need you to optimize it:
                1. Directory levels: If the directory level order is incorrect, please complete or modify it in markdown format;
                2. Content errors: If there are inconsistencies in the context, please correct them;
                3. Tables: Pay attention to inconsistencies between rows;
                4. The overall output should not differ significantly from the input; do not create content on your own—I need to polish the original text;
                5. Output format requirement: Markdown text, all your responses should be placed inside a markdown file.
                Special Note: Only output the converted markdown content itself, without any other information.
                The content to be processed is: 
            ''' + data
        }]

    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_API_BASE"),
    )
    
    response = client.chat.completions.create(
        model="qwen-plus",
        messages=messages,
        stream=True
    )
    result=""
    for chunk in response:
        print(chunk.choices[0].delta.content, end='')
        result += chunk.choices[0].delta.content

    print("Polished Markdown Text:")
    print("-"*100)

    return result
```

```python
md_polisher(md_content)
```

Through the above steps, you have successfully converted the PDF into markdown and made some formatting corrections. 

If there are images in the document, the information in the images can also be extracted to build a knowledge base that is more conducive to search performance.

#### 4.2.3 Using multiple document chunking methods

During the document chunking process, the chunking method can affect the effectiveness of retrieval recall. Let's understand the characteristics of different chunking methods through specific examples. First, create a general evaluation function.

```python
def evaluate_splitter(splitter, documents, question, ground_truth, splitter_name):
    """Evaluate the effectiveness of different document splitting methods"""
    print(f"\n{'='*50}")
    print(f"🔍 Testing with {splitter_name} method...")
    print(f"{'='*50}\n")

    # Build index
    print("📑 Processing documents...")
    nodes = splitter.get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes, embed_model=Settings.embed_model)

    # Create query engine
    query_engine = index.as_query_engine(
        similarity_top_k=5,
        streaming=True
    )

    # Execute query
    print(f"\n❓ Test question: {question}")
    print("\n🤖 Model response:")
    response = query_engine.query(question)
    response.print_response_stream()

    # Output reference snippets
    print(f"\n📚 Reference snippets recalled by {splitter_name}:")
    for i, node in enumerate(response.source_nodes, 1):
        print(f"\nDocument snippet {i}:")
        print("-" * 40)
        print(node)

    # Evaluate results
    print(f"\n📊 Evaluation results for {splitter_name}:")
    print("-" * 40)
    display(evaluate_result(question, response, ground_truth))
```

Next, let's look at the characteristics and examples of various Chunking methods:

#### 4.2.3.1 Token Chunking

Suitable for scenarios with strict requirements on the number of tokens, such as when using models with smaller context lengths.

Example text: "LlamaIndex is a powerful RAG framework. It provides various document processing methods. Users can choose the appropriate method based on their needs."

Possible results after applying token chunking (chunk_size=10):

* Chunk 1: ["LlamaIndex", "is", "a", "powerful", "RAG", "framework.", "It", "provides", "various", "document"]
* Chunk 2: ["processing", "methods.", "Users", "can", "choose", "the", "appropriate", "method", "based", "on"]
* Chunk 3: ["their", "needs."]

```python
token_splitter = TokenTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)
evaluate_splitter(token_splitter, documents, question, ground_truth, "Token")
```

#### 4.2.3.2 Sentence Chunking

This is the default chunking strategy, which preserves the integrity of sentences.

The same text after sentence chunking:

* Chunk 1: "LlamaIndex is a powerful RAG framework."
* Chunk 2: "It provides various document processing methods."
* Chunk 3: "Users can choose the appropriate method based on their needs."

```python
sentence_splitter = SentenceSplitter(
    chunk_size=256,
    chunk_overlap=50
)
evaluate_splitter(sentence_splitter, documents, question, ground_truth, "Sentence")
```

#### 4.2.3.3 Sentence window Retrieval

Each chunk includes surrounding sentences as the context window.

Example text after using sentence window retrieval (window_size=1):

* Chunk 1: "LlamaIndex is a powerful RAG framework." Context: "It provides various document processing methods."
* Chunk 2: "It provides various document processing methods." Context: "LlamaIndex is a powerful RAG framework. Users can choose the appropriate method based on their needs."
* Chunk 3: "Users can choose the appropriate method based on their needs." Context: "It provides various document processing methods."

```python
sentence_window_splitter = SentenceWindowNodeParser.from_defaults(
    window_size=3,
    window_metadata_key="window",
    original_text_metadata_key="original_text"
)
# Note: Sentence window retrieval requires a special post-processor
query_engine = index.as_query_engine(
    similarity_top_k=5,
    streaming=True,
    node_postprocessors=[MetadataReplacementPostProcessor(target_metadata_key="window")]
)
evaluate_splitter(sentence_window_splitter, documents, question, ground_truth, "Sentence Window")
```

#### 4.2.3.4 Semantic chunking

Adaptively select chunk points based on semantic relevance.

Example text: "LlamaIndex is a powerful RAG framework. It provides various document processing methods. Users can choose the appropriate method according to their needs. Additionally, it supports vector-based retrieval. This retrieval method is highly efficient."

Possible results of semantic chunking:

* Chunk 1: "LlamaIndex is a powerful RAG framework. It provides various document processing methods. Users can choose the appropriate method according to their needs."
* Chunk 2: "Additionally, it supports vector-based retrieval. This retrieval method is highly efficient." (Note that this is grouped by semantic relevance.)

```python
semantic_splitter = SemanticSplitterNodeParser(
    buffer_size=1,
    breakpoint_percentile_threshold=95,
    embed_model=Settings.embed_model
)
evaluate_splitter(semantic_splitter, documents, question, ground_truth, "Semantic")
```

#### 4.2.3.5 Markdown Chunking

A chunking method specifically optimized for Markdown documents.

Example Markdown text:



```markdown
# RAG Framework
LlamaIndex is a powerful RAG framework.

## Features
- Provides multiple document processing methods
- Supports vector retrieval
- Easy and convenient to use

### Detailed Description
Users can choose the appropriate method based on their needs.
```

Markdown chunks will be intelligently divided based on heading levels:

* Chunk 1: "# RAG Framework
LlamaIndex is a powerful RAG framework."
* Chunk 2: "## Features
- Provides various document processing methods
- Supports vector retrieval
- Simple and convenient to use"
* Chunk 3: "### Detailed Description
Users can choose the appropriate method according to their needs."

```python
markdown_splitter = MarkdownNodeParser()
evaluate_splitter(markdown_splitter, documents, question, ground_truth, "Markdown")
```

In practical applications, there's no need to overthink when choosing a chunking method. You can consider it this way:

* If you are new to RAG, it is recommended to start with the default sentence chunking method, which provides good results in most scenarios.
* When you find that the retrieval results are not ideal, you can try the following:
    * Are you handling long documents, and need to maintain context? Try sentence window retrieval.
    * Is the document logical and highly specialized? Semantic chunking may be helpful.
    * Is the model always reporting token limits exceeded? Token chunking can help you control precisely.
    * Processing Markdown documents? Don’t forget there’s dedicated Markdown chunking.

There is no single best chunking method—only the one that is most suitable for your specific scenario. Experiment with different chunking methods, observe Ragas evaluation results, and find the solution that best fits your needs. The learning process is all about constant trial and adjustment.

### 4.3 Vectorization and storage phase for chunks

After document chunking, you also need to index the chunks for later retrieval. A common approach is to use a text embedding model to vectorize the chunks and store them in a vector database.

In this phase, selecting an appropriate word embedding model and vector database is crucial for improving retrieval performance.

#### 4.3.1 Understanding word embedding and vectorization

The text embedding model can convert text into high-dimensional vectors to represent textual semantics. Similar texts are mapped to  vectors that are close to each other, allowing documents with high similarity to be identified based on the vector representation of a query.

_A directed line segment in a plane coordinate system is a 2-dimensional vector. For example, the directed line segment from the origin (0, 0) to point A (xa, ya) can be called vector A. The smaller the angle between vector A and vector B, the higher their similarity._

<img src="https://img.alicdn.com/imgextra/i4/O1CN01wKAL7C1bhDgbxr2Aa_!!6000000003496-0-tps-1556-1382.jpg" width="350" ></td>

```python
import numpy as np

def cosine_similarity(a, b):
    """Cosine similarity"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Example vectors
a = np.array([0.2, 0.8])
b = np.array([0.3, 0.7])
c = np.array([0.8, 0.2])

print(f"Cosine similarity between A and B: {cosine_similarity(a, b)}")
print(f"Cosine similarity between B and C: {cosine_similarity(b, c)}")
```

#### 4.3.2 Selecting the Appropriate Embedding Model

Embedding models act as the semantic foundation of a RAG system. On Alibaba Cloud’s Model Studio, the choice typically comes down to **text-embedding-v3** and the newer **text-embedding-v4**. While v3 is a robust general-purpose baseline, v4 introduces higher **semantic discernment**. It is specifically designed to look past surface-level keyword overlaps and prioritize the unique context of a query—a process known as **disambiguation**.

**Phase 1: Observing Semantic Precision**
To understand the difference, consider a "noisy" dataset where multiple records share identical keywords (like the name "Michael Johnson"). We can observe how different models interpret intent by testing them across three scenarios: **Role Matching**, **Multi-Attribute Lookup**, and **Skill Alignment**.

```python
import os
import numpy as np

def compare_embeddings(query, chunks, embedding_models):
    """Observes how different models interpret specific semantic scenarios"""
    print(f"\n🔍 Query: {query}")
    
    for model_name, model in embedding_models.items():
        # Fixed f-string syntax
        print(f"{'-'*15} {model_name} {'-'*15}")
        query_vec = model.get_query_embedding(query)

        for i, chunk in enumerate(chunks, 1):
            chunk_vec = model.get_text_embedding(chunk)
            similarity = cosine_similarity(query_vec, chunk_vec)
            print(f"Text {i} Similarity: {similarity:.4f}")

# Dataset: High keyword overlap (Name/Address) but different professional attributes
chunks = [
    "EID-205 Michael Johnson Michael Chen 456 Tech Hub #205 QA Specialist (555) 234-5682 michael.j@educompany.com System validation testing",
    "EID-209 Michael Johnson Michael Chen 456 Tech Hub #209 Technical Writer (555)234-5686 michael.johnson@educompany.com Documentation creation",
    "EID-220 Michael Johnson Michael Chen 456 Tech Hub #220 System Administrator (555) 234-5697 michael.j2@educompany.com Server maintenance"
]

# Define embedding models to be tested
embedding_models = {
    "text-embedding-v3": OpenAILikeEmbedding(
                                api_base=os.getenv("DASHSCOPE_API_BASE"),
                                api_key=os.getenv("DASHSCOPE_API_KEY"),
                                model_name="text-embedding-v3"
                            ),
    "text-embedding-v4": OpenAILikeEmbedding(
                                api_base=os.getenv("DASHSCOPE_API_BASE"),
                                api_key=os.getenv("DASHSCOPE_API_KEY"),
                                model_name="text-embedding-v4"
                            )
}

# Testing across different levels of intent
test_queries = [
    "Who is the Technical Writer responsible for documentation?", # Scenario 1: Role matching
    "Michael Johnson's email with EID-220",                       # Scenario 2: Multi-attribute lookup
    "System validation testing expert"                            # Scenario 3: Skill matching
]

for q in test_queries:
    compare_embeddings(q, chunks, embedding_models)
```


**Analysis of Similarity Results:**
*   **Role Matching:** Notice the "gap" in scores. In **v4**, the similarity for the "Technical Writer" is significantly higher than for the irrelevant roles (~0.58 vs ~0.33). In **v3**, the scores are much closer, indicating that the model is "distracted" by the shared name.
*   **Attribute Lookup:** **v4** "locks on" to the unique identifier (**EID-220**) with a clear spike in similarity. **v3** struggles to distinguish it from other records because the recurring name "Michael Johnson" carries too much weight in its calculation.
*   **Skill Mapping:** Even without an exact job title, **v4** recognizes that "testing expert" semantically maps to "QA Specialist," whereas **v3** relies more heavily on direct keyword presence.

**Key Insight:** In RAG, do not just chase high absolute scores. A distinct **gap** between the correct answer and the "noise" is a much stronger indicator of a model's retrieval precision.

**Phase 2: Real-World Pipeline Evaluation**
Individual scores tell only part of the story; the true test happens within a complete RAG pipeline. Using the **Ragas** framework, we can evaluate how these models impact the final answer generated by the LLM.

```python
def compare_embedding_models(documents, question, ground_truth, sentence_splitter):
    """Compare the performance of different embedding models within a RAG pipeline"""
    
    # Document splitting
    print("📑 Processing documents...")
    nodes = sentence_splitter.get_nodes_from_documents(documents)

    # Define the embedding model configurations
    embedding_models = {
         "text-embedding-v3": OpenAILikeEmbedding(
                                api_base=os.getenv("DASHSCOPE_API_BASE"),
                                api_key=os.getenv("DASHSCOPE_API_KEY"),
                                model_name="text-embedding-v3",
                                embed_batch_size=6
                            ),
        "text-embedding-v4": OpenAILikeEmbedding(
                                api_base=os.getenv("DASHSCOPE_API_BASE"),
                                api_key=os.getenv("DASHSCOPE_API_KEY"),
                                model_name="text-embedding-v4",
                                embed_batch_size=6
                            )
    }

    for model_name, embed_model in embedding_models.items():
        print(f"\n{'='*50}\n🔍 Testing {model_name}...\n{'='*50}")

        # Build index and query engine
        index = VectorStoreIndex(nodes, embed_model=embed_model)
        query_engine = index.as_query_engine(streaming=True, similarity_top_k=5)

        # Execute query
        print(f"\n❓ Test question: {question}")
        print("\n🤖 Model response:")
        response = query_engine.query(question)
        response.print_response_stream()

        # Display recalled document fragments
        print(f"\n📚 Recalled reference fragments:")
        for i, node in enumerate(response.source_nodes, 1):
            print(f"\nFragment {i}: {node.node.get_content()[:100]}...")

        # Evaluate results using Ragas or similar metrics
        print(f"\n📊 Evaluation results for {model_name}:")
        evaluation_score = evaluate_result(question, response, ground_truth)
        display(evaluation_score)

# Prepare test data
documents = SimpleDirectoryReader('./docs/2_5').load_data()
sentence_splitter = SentenceSplitter(
    chunk_size=256,
    chunk_overlap=200,
)
# Perform comparison
compare_embedding_models(
    documents=documents,
    question=question,
    ground_truth=ground_truth,
    sentence_splitter=sentence_splitter
)
```


**Analyzing the Evaluation Results:**
When running the pipeline with the question *"What does Michael Johnson do?"*, the results often present a fascinating "teaching moment" where metrics and behavior tell different stories:
*   **The "Wide Net" (v3):** You may find that **v3** scores higher on **Correctness** and **Recall**. This is because v3 is less disciplined; it retrieves a broad range of fragments that happen to include all three Michael Johnson roles, alongside unrelated "noise" (like records for "Smith"). Because the LLM receives more data, it writes a more complete answer, boosting the scores.
*   **The "Surgical Strike" (v4):** In contrast, **v4** often shows lower recall but much higher **Precision**. Its top-ranked fragments are perfect hits, successfully filtering out the "Smith" and "Backend integration" noise that v3 failed to ignore. In a large-scale enterprise database, v3’s noise can lead to LLM confusion, increased costs, or context-limit errors.

**Engineering Verdict & Recommendation**
This comparison highlights that raw metrics are only the starting point. To optimize your RAG system, keep these two lessons in mind:
1.  **Precision Prevents Hallucination:** v4’s ability to suppress noise ensures the LLM receives only relevant context—the most important factor in preventing hallucinations.
2.  **Recall is Tunable:** v4 has superior ranking capability. If your recall is low, you can simply increase your `similarity_top_k` (e.g., from 5 to 10). v4 will likely find the missing data without bringing in the "distractor" fragments that v3 would.

**Final Advice:** Start with **v3** to establish a reliable baseline. Transition to **v4** when your application requires the semantic rigor to distinguish between "similar" and "relevant," especially when dealing with complex entities like employee records, product catalogs, or technical documentation.

#### 4.3.3 Choosing the right vector database

When building a RAG chatbot, you have multiple vector storage options to choose from, ranging from simple to complex:

##### 4.3.3.1 In-memory vector storage

The simplest approach is to use the vector database built into LlamaIndex. Simply install the llama-index package, and with no additional configuration, you can quickly develop and test your RAG chatbot:

```python
from llama_index.core import VectorStoreIndex
# Create in-memory vector index
index = VectorStoreIndex.from_documents(documents)
```

The advantage is that it is quick to get started, making it suitable for development and testing; the disadvantages are that data cannot be persisted, and it is limited by memory size.

##### 4.3.3.2 Local vector database

When the data volume increases, open-source vector databases such as Milvus and Qdrant can be used. These databases provide data persistence and efficient retrieval capabilities.

The advantage is that the functionality is complete and highly controllable; the disadvantage is that it requires self-hosting and maintenance.

##### 4.3.3.3 Cloud service vector storage

For production environments, it is recommended to use vector storage capabilities provided by cloud services. Alibaba Cloud offers multiple options:

* **Vector Retrieval Service (DashVector)**: Pay-as-you-go, automatic scaling, suitable for quickly starting projects. For detailed functionalities, please refer to [Vector Retrieval Service (DashVector)](https://www.alibabacloud.com/en/product/dashvector).
* **Vector Retrieval Service Milvus Edition**: Compatible with open-source Milvus, making it convenient to migrate existing applications. For detailed functionalities, please refer to [Vector Retrieval Service Milvus Edition](https://www.alibabacloud.com/en/product/milvus?_p_lc=1).
* **Vector Capabilities of Existing Databases**: If you are already using Alibaba Cloud databases (such as RDS and PolarDB), you can  utilize their vector functionalities.

The advantages of cloud services include:

* With automatic scaling, there's no need to worry about operations and maintenance.
* Comprehensive monitoring and management tools are provided.
* Pay-as-you-go, with better cost control.
* Support for hybrid retrieval of vectors + scalars, improving retrieval accuracy.

Recommendations:
1. Use in-memory vector storage during development and testing.
2. For small-scale applications, you can use local vector databases.
3. For production environments, it is recommended to use cloud services, and choose the appropriate service type based on your needs.

```python
import dashvector

# Create Client and get collection
dashvector_client = dashvector.Client(api_key='YOUR_API_KEY', endpoint='YOUR_CLUSTER_ENDPOINT')
collection = dashvector_client.get('quickstart')

# Similar vector query
collection.query(
    vector=[0.1, 0.2, 0.3, 0.4]
)

# Query using filter conditions
collection.query(
    vector=[0.1, 0.2, 0.3, 0.4],
    topk=100,
    filter='age>18',  # Filter condition, only perform similarity search on Docs with age > 18
    output_fields=['name', 'age'],  # Only return the name and age fields
    include_vector=True
)
```

### 4.4 Retrieval recall phase

The main issue encountered during the retrieval phase is the difficulty of identifying, from a large number of chunks, the fragment that is most relevant to the user's question and contains the correct answer.

From the perspective of intervention timing, solutions can be divided into two main categories:

1. Before executing the retrieval, many user queries are incomplete or even ambiguous. It is necessary to find ways to reconstruct the user's true intent to improve retrieval effectiveness.
2. After executing the retrieval, you may discover some irrelevant information that needs to be filtered out to avoid interfering with the subsequent answer generation.

<table border="1">
  <thead>
    <tr>
      <th>Timing</th>
      <th>Improvement Strategy</th>
      <th>Example</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="7">Before Retrieval</td>
      <td>Question Rewriting</td>
      <td>"Are there any good restaurants nearby?" => "Please recommend a few highly-rated restaurants near me."</td>
    </tr>
    <tr>
      <td>Question Expansion <em>Adding more information to make the search results more comprehensive</em></td>
      <td>"Which department does Michael Johnson belong to?" => "Which department does Michael Johnson belong to? What are his contact details, responsibilities, and work objectives?"</td>
    </tr>
    <tr>
      <td>Context Expansion Based on User Profile <em>Expanding the question based on user information and behavior data</em></td>
      <td>Content Engineer asks "Work Precautions" => "What precautions should a content engineer take at work?" Project Manager asks "Work Precautions" => "What precautions should a project manager take at work?"</td>
    </tr>
    <tr>
      <td>Tag Extraction <em>Tag Extraction: Extract tags for subsequent tag filtering + vector similarity search.</em></td>
      <td>"What precautions should a content engineer take at work?" => <ul><li>Tag Filtering: {"Position": "Content Engineer"}</li><li>Vector Search: "What precautions should a content engineer take at work?"</li></ul></td>
    </tr>
    <tr>
      <td>Ask the User</td>
      <td>"What are the job responsibilities?" => LLM asks back: "May I ask which position’s job responsibilities you want to know about?" <em>Prompt examples for asking back can be found here:</em><a href="https://www.alibabacloud.com/help/en/model-studio/use-multi-agent-to-query-alibaba-cloud-resource-information">Build a multi-agent system with automatic planning capabilities using the Assistant API
</a></td>
    </tr>
    <tr>
      <td>Think and Plan Multiple Searches</td>
      <td>"Michael Johnson is not available, who can I contact?" => LLM thinks and plans: => task_1: What are Michael Johnson's responsibilities, task_2: Who else has ${task_1_result} responsibilities => Execute multiple searches in sequence.</td>
    </tr>
    <tr>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <td rowspan="3">After Retrieval</td>
      <td>reranking + Filtering <em>Most vector databases consider efficiency and sacrifice some accuracy; the retrieved chunks may contain items with low relevance.</em></td>
      <td>chunk1, chunk2..., chunk10 => chunk 2, chunk4, chunk5</td>
    </tr>
    <tr>
      <td>Sliding Window Retrieval <em>After retrieving a chunk, supplement it with several adjacent chunks before and after. This is because adjacent chunks often have semantic connections, and looking at a single chunk might lose important information.</em> <em>Sliding window retrieval ensures that semantic connections between texts are not lost due to excessive segmentation.</em></td>
      <td>A common implementation is sentence sliding windows. You can understand it using the simplified form below: Assume the original text is ABCDEFG (each letter represents a sentence). When the retrieved chunk is D, after supplementing adjacent chunks, it becomes BCDEF (taking 2 chunks before and after). Here, BC and EF are the context of D. For example:<ul><li>BC may contain background information explaining D</li><li>EF may contain subsequent developments or results of D</li><li>These contextual pieces of information help you understand the full meaning of D more accurately</li></ul>By recalling these related context chunks, you can improve the accuracy and completeness of the retrieval results.</td>
    </tr>
    <tr>
      <td>...</td>
      <td>...</td>
    </tr>
  </tbody>
</table>

#### 4.4.1 Question rewriting

🤔 **Why is question rewriting necessary?**

Imagine you are searching for keywords like "Find Michael Johnson" or "Michael Johnson Department." It seems simple, but for a RAG system, such scattered search terms can be challenging to process. This is because, in real-world scenarios, there may be multiple employees named Michael Johnson, and the keywords entered by users are often too simplistic, lacking necessary contextual information.

```python
question = "Find Michael Johnson"
```

✨ **What can problem rewriting bring?**

Problem rewriting is like helping the system better understand user intent. For example, when you ask "Find Michael Johnson," the system can rewrite the question into a more complete form, such as "Please tell me all employees named Michael Johnson in the company and their departments." Such rewriting improves the accuracy of retrieval, and also makes the answers more comprehensive.

Next, you can try different problem rewriting strategies through practical examples. In this case, you will use the following configuration:

* Document: Markdown format
* Chunking: Default sentence chunking strategy
* Model: text-embedding-v3
* Storage: Default vector storage

```python
# Configure embedding model
Settings.embed_model = OpenAILikeEmbedding(
                            api_base=os.getenv("DASHSCOPE_API_BASE"),
                            api_key=os.getenv("DASHSCOPE_API_KEY"),
                            model_name="text-embedding-v3",
                            embed_batch_size=6,
                            embed_input_length=8192
                        )

# Load documents
documents = SimpleDirectoryReader('./docs/2_5').load_data()

# Configure document splitter
sentence_splitter = SentenceSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

# Document splitting
sentence_nodes = sentence_splitter.get_nodes_from_documents(documents)

# Build index
sentence_index = VectorStoreIndex(sentence_nodes, embed_model=Settings.embed_model)
```

**Conventional Method: Direct Retrieval without Rewriting the Question**

Before  attempting to rewrite the question, take a look at the results of using the original question for retrieval. This comparison will give you a more intuitive sense of the improvements that question rewriting can bring:

```python
# Create query engine
query_engine = sentence_index.as_query_engine(
    streaming=True,
    similarity_top_k=5
)

# Execute query
print(f"❓ User question: {question}\n")
streaming_response = query_engine.query(question)

print("\n💭 AI Response:")
print("-" * 40)
streaming_response.print_response_stream()
print("\n")

# Display reference documents
print("\n📚 Reference Sources:")
print("-" * 40)
for i, node in enumerate(streaming_response.source_nodes, 1):
    print(f"\nDocument snippet {i}:")
    print(f"Relevance score: {node.score:.4f}")
    print("-" * 30)
    print(node.text)

# Evaluate results
print("\n📊 Response Quality Evaluation:")
print("-" * 40)
evaluation_score = evaluate_result(question, streaming_response, ground_truth)
display(evaluation_score)
```

After running this code, you may find the results less than ideal. Although the system retrieved five relevant snippets, it did not find all the information about "Michael Johnson." Why is that?

The issue lies in the way the question was asked. When a user asks, "Find Michael Johnson," this question is easy for a person to understand but lacks important context for an LLM—there are multiple Michael Johnsons in the company! This is similar to walking into a company with several employees named John Smith and asking, "Where is John Smith's desk?" Someone is likely to respond, "Which John Smith do you mean?"

So, what if we made the question more complete? For example, by clearly stating that you want to know the department information of "all employees named Michael Johnson in the company." Next, you can try using an LLM to rephrase the question and see if the results improve.

**Method 1: Using LLMs to Expand User Questions**

You can ask the LLM to act as a question-rewriting assistant. It will help you rewrite simple questions to make them more complete and clear. For example, it will not only consider the possibility of multiple individuals named Michael Johnson, but also supplement all related contextual information. Here are the details of how to do it :

```python
query_gen_str = """
System role setting:
You are a professional question rewriting assistant. Your task is to expand the user's original question into a more complete and comprehensive question.

Rules:
1. Integrate possible ambiguities, related concepts, and contextual information into a complete question
2. Use parentheses to supplement explanations for ambiguous concepts
3. Add key qualifiers and modifiers
4. Ensure that the rewritten question is clear and semantically complete
5. For vague concepts, list the main possibilities in parentheses
6. About 15 words or less in length

Original question:
{query}

Please generate a comprehensive rewritten question, ensuring:
- Contains the core intent of the original question
- Covers possible interpretations of ambiguities
- Uses clear logical connectives to link different aspects
- When necessary, use parentheses to provide supplementary explanations

Output format:
[Comprehensive rewrite] - The rewritten question
"""
query_gen_prompt = PromptTemplate(query_gen_str)
```

```python
def generate_queries(query: str):
    response = Settings.llm.predict(
        query_gen_prompt, query=query
    )
    return response
```

```python
# Generate extended queries
print("\n🔍 Original question:")
print(f"   {question}")
query = generate_queries(question)
print("\n📝 Extended queries:")
print(f"   {query}\n")

# Create query engine
query_engine = sentence_index.as_query_engine(
    streaming=True,
    similarity_top_k=10
)
# Execute query
response = query_engine.query(query)

print("💭 AI Response:")
print("-" * 40)
response.print_response_stream()
print("\n")

# Display reference documents
print("\n📚 Reference sources:")
print("-" * 40)
for i, node in enumerate(response.source_nodes, 1):
    print(f"\nDocument snippet {i}:")
    print(f"Relevance score: {node.score:.4f}")
    print("-" * 30)
    print(node.text)

# Evaluate results
print("\n📊 Response quality evaluation:")
print("-" * 40)
evaluation_score = evaluate_result(query, response, ground_truth)
display(evaluation_score)
```

After running the code above, you will find that questions rewritten by LLMs can achieve better retrieval results. However, for some complex questions, rewriting alone may not be sufficient.

**Method 2: Rewriting a single query into multi-Step queries**

In addition to rewriting a query for clarity, you can also break down complex questions into simpler, sequential steps. This approach is particularly useful when dealing with ambiguous or multi-faceted queries—such as identifying information about individuals with common names like "Michael Johnson." By breaking down the original question, you enable the system to retrieve more comprehensive and accurate results.

LlamaIndex offers two powerful tools that support this approach:

1. `StepDecomposeQueryTransform`: This tool helps break down a complex question into multiple sub-questions. It leverages an LLM to analyze the intent behind the query, and generate a series of logical follow-up questions that lead to the final answer. For the question *"Which department does Michael Johnson belong to?"*, the tool might break it down into:
    - **Step 1:** *"How many employees named Michael Johnson are there in the company?"*
    - **Step 2:** *"Which departments do these Michael Johnsons belong to?"*

By doing so, the system avoids missing relevant information due to ambiguity and ensures all possible matches are considered.

2. `MultiStepQueryEngine`: This query engine processes each of the sub-questions generated by `StepDecomposeQueryTransform` in sequence. After retrieving answers to each step, it combines the results into a single, coherent response.
    - First, it retrieves all employees named Michael Johnson.
    - Then, it queries the department information for each one.
    - Finally, it compiles a response such as (just for illustrative purposes):
        > *"There are three Michael Johnsons in the company, working in the Teaching and Research Department, Course Development Department, and IT Department, respectively."*

This step-by-step processing ensures that no piece of relevant information is overlooked and allows the system to handle complex queries more effectively.

**Benefits of multi-step querying**

- **Improved Accuracy:** Breaking down queries leads to more thorough retrieval and reduces the risk of missing key details.
- **Better Handling of Ambiguity:** Especially useful for queries involving common names or unclear references.
- **Logical Flow:** Mimics how humans solve complex problems — by dividing them into smaller, manageable parts.

**Considerations**

- **Increased LLM Usage:** Since each step may involve calling an LLM, this method consumes more tokens than a single-query approach.
- **Longer Processing Time:** Due to multiple sequential calls, the overall response time may be longer.

Nonetheless, for complex or ambiguous queries, the trade-off is often worth it in terms of result quality and completeness.

```python
from llama_index.core.indices.query.query_transform.base import (
    StepDecomposeQueryTransform,
)
step_decompose_transform = StepDecomposeQueryTransform(verbose=True)
# set Logging to DEBUG for more detailed outputs
from llama_index.core.query_engine import MultiStepQueryEngine
query_engine = sentence_index.as_query_engine(streaming=True,similarity_top_k=5)
query_engine = MultiStepQueryEngine(
    query_engine=query_engine,
    query_transform=step_decompose_transform,
    index_summary="Employee Key Contact Information"
)
print(f"❓ User question: {question}\n")
print("🤖 AI is performing multi-step query...")
response = query_engine.query(question)
print("\n📚 Reference basis:")
print("-" * 40)
for i, node in enumerate(response.source_nodes, 1):
    print(f"\nDocument fragment {i}:")
    print("-" * 30)
    print(node.text)

# Evaluation results
print("\n📊 Multi-step query evaluation results:")
print("-" * 40)
evaluation_score = evaluate_result(question, response, ground_truth)
display(evaluation_score)
```

In this way, the system begins by understanding the overall intent behind the query, then breaks it down into a series of smaller, sequential steps to resolve ambiguity and gather information more accurately. For example, when the user asks the LLM to "Find Michael Johnson," it might first attempt to clarify the request by asking:

```
"Who is Michael Johnson according to the employee key contact information?"
```

Based on the retrieved information, the system may then follow up with a more specific question such as:

```
"Which Michael Johnson is being referred to in the request — the QA Specialist or the Technical Writer?"
```

This step-by-step approach ensures that all possible matches are considered and helps the system avoid making assumptions. Once the correct individual is identified, the system can then proceed to retrieve detailed information, such as their department, contact details, or supervisor.

By processing queries in this structured manner, the system significantly improves the accuracy and relevance of its responses, especially when dealing with ambiguous or incomplete questions.

**Method 3: Enhance retrieval with HyDE**

The previous methods have all been about adjusting the question itself. Now, let's try a different approach: what if we first assume a possible answer? This is the unique aspect of the Hypothetical Document Embeddings  (HyDE) method.

Here is its working mechanism:

1. First, have the LLM generate a "hypothetical answer document" based on the question.
2. Use this hypothetical document to retrieve real documents.
3. Finally, use the retrieved real documents to generate an actual answer.

This is analogous to when you're looking for a book and already have a rough outline of its content in mind, then use that outline to match similar books in the library. Let's see how this can be implemented specifically:

```python
from llama_index.core.indices.query.query_transform.base import (
    HyDEQueryTransform,
)
from llama_index.core.query_engine import TransformQueryEngine
# run query with HyDE query transform
hyde = HyDEQueryTransform(include_original=True)
query_engine = sentence_index.as_query_engine(streaming=True,similarity_top_k=5)
query_engine = TransformQueryEngine(query_engine, query_transform=hyde)

print(f"❓ User question: {question}\n")
print("🤖 AI is analyzing using HyDE...")
streaming_response = query_engine.query(question)

print("\n💭 AI response:")
print("-" * 40)
streaming_response.print_response_stream()

# Display reference documents
print("\n📚 Reference sources:")
print("-" * 40)
for i, node in enumerate(streaming_response.source_nodes, 1):
    print(f"\nDocument snippet {i}:")
    print("-" * 30)
    print(node.text)

# Evaluate results
print("\n📊 HyDE Query Evaluation Results:")
print("-" * 40)
evaluation_score = evaluate_result(question, streaming_response, ground_truth)
display(evaluation_score)
```

As you can see from the evaluation results, this method has indeed brought some improvements. You may be wondering: How does the system generate this "hypothetical document"? Let’s take a look at what content the LLM  generated during this process:

```python
query_bundle = hyde(question + "from the employee key contact information table")
hyde_doc = query_bundle.embedding_strs[0]
print(f"🤖 AI-generated hypothetical document:\n{hyde_doc}\n")
```

Although this "hypothetical document" is entirely fabricated by AI, its structure and style are very similar to real company employee information. LlamaIndex provides flexible control mechanisms to optimize this process:
The HyDEQueryTransform class lets us precisely control the generation of hypothetical documents in the following ways:

* Custom LLM: By passing different configurations of LLMs through the llm parameter, you can choose a more suitable language model for generating hypothetical documents.
* Prompt template: Customize the prompt template via the hyde_prompt parameter to precisely control the format and content of the output.
* Query strategy: Use the include_original parameter to decide whether to combine the original query with the hypothetical document.

TransformQueryEngine acts as a wrapper for the query engine, which will:

1. First call HyDEQueryTransform to generate the hypothetical document.
2. Use the hypothetical document for vector retrieval.
3. Return the query results.

This architecture lets us optimize the retrieval effect by adjusting the parameters of HyDEQueryTransform without modifying the underlying query engine. Even though the specific content of the hypothetical document may not be entirely accurate, a well-designed configuration can help the system retrieve relevant information more accurately.

#### 4.4.2 Extracting tags to enhance retrieval

On the basis of vector retrieval, we can also add tag filtering to improve retrieval accuracy. This method is similar to a library having both title search and a classification numbering system, which allows for more precise retrieval.

There are two key scenarios for tag extraction:

1. When building an index, extract structured tags from document chunks.
2. During retrieval, extract corresponding tags from user queries for filtering.

Let's look at two examples to understand how to extract tags from different types of text:

```python
import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"), base_url=os.getenv("DASHSCOPE_API_BASE"))
system_message = """You are a tag extraction expert. Please extract structured information from the text and output tags as required.
---
[Supported Tag Types]
- Person Name
- Department Name
- Job Title
- Technical Field
- Product Name
---
[Output Requirements]
1. Please output in JSON format, such as: [{"key": "Department Name", "value": "Teaching and Research Department"}]
2. If a certain type of tag is not identified, do not output that type
---
The text to be analyzed is as follows:
"""
def extract_tags(text):
    completion = client.chat.completions.create(
        model="qwen-turbo",
        messages=[
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': text}
        ],
        response_format={"type": "json_object"}
    )
    return completion.choices[0].message.content
```

```python
# Example 1: HR Document
hr_text = """David Miller is the Technical Director of our AI Research and Development department. He led the team in building the next-generation intelligent conversational platform, AstraChat, and has extensive experience in the field of natural language processing. For more information about the project, feel free to contact him directly."""
print("HR Document Tag Extraction Results:")
print(extract_tags(hr_text))

# Example 2: Technical Document
tech_text = """This paper introduces a deep learning-based image recognition algorithm that has achieved significant breakthroughs in medical imaging analysis. The algorithm has been deployed in the CT diagnostic system at Johns Hopkins Hospital."""
print("\nTechnical Document Tag Extraction Results:")
print(extract_tags(tech_text))
```

When we build the index, we can store these tags alongside document chunks. This way, during retrieval, for example, when a user asks "Which department is Michael Johnson in?" we can:

1. Extract the name tag {"key": "Name", "value": "Michael Johnson"} from the question.
2. Use the tag to filter out all document chunks containing "Michael Johnson."
3. Apply vector similarity search to find the most relevant content.

This combination of "tag filtering + vector retrieval" significantly improves retrieval accuracy. It performs especially well when dealing with highly structured enterprise documents.

#### 4.4.3 Re-ranking

You can delete the Markdown file created earlier to recreate the initial poor response state for the query "Find Michael Johnson" mentioned at the beginning of this section.

```python
![ -d ./docs/2_5/ ] && rm -r ./docs/2_5/ && echo "Folder has been deleted." || echo "Folder does not exist, no need to delete."
```

Then, execute the following code. As you can see, the code is set to retrieve three relevant document chunks from the vector database.

However, the retrieval results are not sufficient—one entry for "Michael Johnson" is missing. Due to this incomplete recall, the Q&A bot is unable to correctly respond to the request "Find Michael Johnson," resulting in an incorrect response.

```python
from llama_index.llms.dashscope import DashScope
from chatbot import rag
```

```python
index = rag.create_index('./docs')
query_engine = index.as_query_engine(
    similarity_top_k=3,
    streaming=True,
)
```

```python
response = ask("Find Michael Johnson", query_engine=query_engine)
```

```python
display(evaluate_result(question, response, ground_truth))
```

You can adjust the code to first retrieve 20 document chunks from the vector database, then use the [text rerank](https://www.alibabacloud.com/help/en/model-studio/text-rerank-api) provided by Alibaba Cloud Model Studio to re-rank them, and filter out the three most relevant reference pieces of information.

After running the code, you will notice that, with the same three reference pieces of information, the LLM is now able to answer the question accurately.

```python
from llama_index.core.postprocessor import SimilarityPostprocessor
from chatbot.openai_like import OpenAILikeRerank, OpenAILikeRerankPostprocessor

rerank_client = OpenAILikeRerank(
    api_base=os.getenv("DASHSCOPE_RERANK_BASE"),  
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model_name="qwen3-rerank",                   
)

query_engine = index.as_query_engine(
    # Set a larger initial retrieval size to fetch more candidate nodes
    similarity_top_k=20,
    streaming=True,
    node_postprocessors=[
        # Use the reranker model (gte-rerank) to select the top N most relevant nodes
        OpenAILikeRerankPostprocessor(rerank_client=rerank_client, top_n=3),
        # Filter out nodes with similarity scores below the specified threshold
        SimilarityPostprocessor(similarity_cutoff=0.2),
    ],
)
```

```python
response = ask("Which department is Michael Johnson in", query_engine=query_engine)
```

```python
display(evaluate_result(question, response, ground_truth))
```

### 4.5 Answer generation phase

Now, the LLM will generate the final answer based on your question and the retrieved content. However, this answer may still not meet your expectations. The issues you might encounter include:
1. No relevant information was retrieved, causing the LLM to hallucinate an answer.
2. Relevant information was retrieved, but the LLM did not generate the answer as required.
3. Relevant information was retrieved, and the LLM provided an answer, but you expected the AI to give a more comprehensive response.
To address these issues, you can analyze and resolve them from the following perspectives:
* Choosing the right LLM:
    * For simple information queries and summaries, a small-parameter model is sufficient, such as [qwen-turbo](https://www.alibabacloud.com/help/en/model-studio/models#5169965cbfeyp).
    * If you want the Q&A bot to perform complex logical reasoning, it is recommended to choose a larger-parameter LLM with stronger reasoning capabilities, such as [qwen-plus](https://www.alibabacloud.com/help/en/model-studio/models#1e0e75495dyvu) or even [Qwen-Max](https://www.alibabacloud.com/help/en/model-studio/models#qwen-max-intl-sp).
    * If your question requires reviewing a large number of document fragments, it is recommended to choose a model with a longer context length, such as [qwen-long](https://www.alibabacloud.com/help/en/model-studio/models#daf364417cjit), [qwen-turbo](https://www.alibabacloud.com/help/en/model-studio/models#5169965cbfeyp), or [qwen-plus](https://www.alibabacloud.com/help/en/model-studio/models#1e0e75495dyvu).
    * If the RAG chatbot you are building is for non-general domains such as the legal field, it is recommended to use a model trained specifically for that domain, such as [Role-playing](https://www.alibabacloud.com/help/en/model-studio/models#fc5654312fimq).
* Fully optimize the prompt template. For example:
    * Clearly request no fabrication of answers:
        * LLMs may produce inaccurate content, a phenomenon commonly referred to as hallucination.
        * You can reduce the likelihood of LLM hallucinations by requiring in the prompt: "If the provided information is insufficient to answer the question, please explicitly state 'Based on the available information, I cannot answer this question.' Do not fabricate answers."
    * Add content delimiters: 
        * If the retrieved document chunks are randomly mixed into the prompt, it will be difficult for humans to see the structure of the entire prompt, and the LLM will also be affected. 
        * It is recommended to clearly separate the prompt and the retrieved chunks so that the LLM can correctly understand your intent.
    * Adjust the template according to the type of question: 
        * Different types of questions may require different response paradigms. You can use the LLM to identify the question type and then map different prompt templates accordingly. 
        * For example, for some questions, you may want the LLM to first output the overall framework and then the details; for other questions, you may prefer the LLM to provide concise conclusions.
* Adjust the parameters of the LLM. For example:
    * If you want the LLM to produce the same output for the same question, pass the same seed value each time the model is invoked.
    * If you want to discourage the model from repeating tokens that have already appeared in the response, you can increase the presence_penalty value. 
    * If you are querying factual content, appropriately decrease the temperature or top_p values; conversely, when generating creative content,  increase their values.
    * If you need to limit the word count (such as generating summaries or keywords), control costs, or reduce response time, appropriately lower the max_tokens value. However, if max_tokens is too low, it may lead to truncated output. Conversely, when generating long text, increase its value.
    * Refer to the [Qwen API Reference](https://www.alibabacloud.com/help/en/model-studio/qwen-api-reference) to learn more about the usage instructions for various parameters.

```python
from llama_index.llms.openai_like import OpenAILike
from llama_index.core import Settings
import os
```

```python
# Factual query scenario - Low temperature, high certainty
factual_llm = OpenAILike(
    model="qwen-plus",  # Use the Qwen-Plus model
    api_base=os.getenv("DASHSCOPE_API_BASE"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    is_chat_model=True,
    temperature=0.1,      # Lower temperature for more deterministic output
    max_tokens=512,       # Control output length; however, if max_tokens is too small, it may lead to truncated output
    presence_penalty=0.0, # Default presence_penalty
    seed=42              # Fixed seed for reproducible output
)
```

```python
# Creative scenario - High temperature, more diversity
creative_llm = OpenAILike(
    model="qwen-plus",
    api_base=os.getenv("DASHSCOPE_API_BASE"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    is_chat_model=True,
    temperature=0.7,      # Increase temperature to make the output more creative
    max_tokens=1024,      # Allow longer output
    presence_penalty=0.6  # Increase presence_penalty to reduce repetition
)
```

* LLM Fine-Tuning: If all the above methods have been thoroughly attempted but still fall short of your expectations, or if you hope to achieve further performance improvements, you can also try model fine-tuning tailored to your specific scenario. In later chapters, you will learn and practice this process.

## ✅ Summary

Through this section, you have gained an understanding the workflow of a simple RAG and common optimization techniques. You can also combine the knowledge you've acquired with your specific needs to route certain questions to different RAG chatbots, thereby building a more powerful modular RAG system. Additionally, from the previous lessons, you should also recognize that LLMs are not only useful for building question-answering systems: Leveraging LLMs to identify user intent and extract structured information—such as extracting tags from user questions as mentioned earlier—can also be applied in many other application scenarios.

Of course, the optimization methods for RAG go far beyond those introduced in this course. The industry continues to research and explore RAG, and there are still many advanced RAG topics worth  studying. As shown through the previous learning, building a well-rounded and high-performing RAG chatbot is no simple task. In real-world applications, you may need to act quickly and won’t always have time to dive into every detail. Below are some directions worth exploring:

* GraphRAG ingeniously combines the strengths of RAG and query-focused summarization (QFS), providing a powerful solution for handling large-scale text data. It integrates the advantages of both technologies: RAG excels at finding precise detailed information, while QFS is better at understanding and summarizing the overall content of an article. This combination allows GraphRAG to accurately answer specific questions and handle complex queries that require deeper understanding, making it particularly suitable for building intelligent question-answering systems. If you want to learn how to  apply GraphRAG in practice, you can refer to the detailed tutorial provided by LlamaIndex: [Building a GraphRAG Application with LlamaIndex](https://docs.llamaindex.ai/en/stable/examples/cookbooks/GraphRAG_v2/).
* With Model Studio, you can follow the document [Build a private Q&A application with zero code](https://www.alibabacloud.com/help/en/model-studio/build-knowledge-base-qa-assistant-without-coding/) to quickly build a fairly effective RAG chatbot.
* If your business processes are more complex, you can also leverage Visual Workflow, an agent orchestration application on Model Studio to build a more powerful application.

## 🔥 Quiz

### 🔍 Single choice question

<details>
<summary style="cursor: pointer; padding: 12px; border: 1px solid #dee2e6; border-radius: 6px;">
<b>In RAG applications, the length and content of document chunks significantly impact retrieval performance. If the chunk size is too large, introducing excessive noise, how should it be addressed❓(Select 1.)</b>

- A. Increase the number of documents
- B. Reduce the chunk size, or develop a more reasonable chunking strategy based on business characteristics
- C. Use a more advanced retrieval algorithm
- D. Improve the training level of the large model

**[Click to view the answer]**
</summary>

<div style="margin-top: 10px; padding: 15px; border: 1px solid #dee2e6; border-radius: 0 0 6px 6px;">

✅ **Reference Answer: B**  
📝 **Explanation**: 
- Excessively long document chunks may include too much irrelevant information (noise), directly affecting retrieval accuracy.
- For example, if a single chunk contains multiple topics, unrelated content may be retrieved during searches.
- Optimizing the chunking strategy is the fundamental solution to address noise, as it controls input quality rather than relying on subsequent algorithmic or model compensation.

</div>
</details>
