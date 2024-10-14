# Capstone Project (Monsoon 2024) - Legal Document Analysis using LLMs and Knowledge Graphs
This repository contains code and the dataset for my fourth-year Capstone Project.

### Problem Statement
Legal documents are complex in nature, and analysing vast amounts of such documents
is a time-consuming task. Extracting insights (such as common statutes cited, similarity
between cases, etc) from a large corpus of legal documents is challenging to do by hand
due to the size and complexity of the corpus. LLMs are able to read and answer questions
from both singular documents and large collections of documents using techniques such
as Retrieval-Augmented Generation. However, they are not able to analyse and answer
questions about the datasets themselves. For example, an LLM will not be able to provide
counts of the statutes cited within the documents, the similarity between multiple cases
based on the cases/statutes/provisions cited within them, or provide statistics about the
outcomes of certain types of cases. One solution for handling this analysis is the use of
Knowledge Graphs representing the legal ontology. The problems to solve, then, are:
1. Summarization of individual documents, for further extraction and user reference,
2. The extraction of entities (laws/provisions cited, appellant and respondent names,
precedents used, the decision along with reasoning, etc.),
3. The definition and creation of a Knowledge Graph based on a legal ontology, and
4. The functionality to query the KG using natural language, to make it easily usable for
anyone.

### Dataset

The dataset consists of approximately 150 food safety case judgements from courts across India.

### Methodology
The methodology can be split into 4 parts, corresponding to the 4 steps defined earlier.

**1. Summarization & Question-Answering**

The documents will be individually passed to an LLM (LLaMA) to be summarized. This step
will also include question-answering: the LLM will be asked to extract relevant information
from each document, the answers for which will be used to extract relevant entities (statutes,
precedents, names, etc).

**2. Extraction of Entities**

The entities we are interested in will have to be extracted from each document. As mentioned
before, we can use the outputs from the LLM question-answering step to do this. Another
possible method is to use NER, for which there are publicly available models. The two
methods can be compared on accuracy on a subset of the corpus, and the better one can be
chosen.

**3. Building the Knowledge Graph**

We first have to create the ontology of the legal space, defining relevant entities and the
relationships between them. This will shape the questions we ask the LLM. Once the relevant
entities have been extracted, neo4j can be used to create a Knowledge Graph representing
this ontology. This will allow us to visualise the relationships, and query the graph for
insights. However, the final challenge is to make these insights easily accessible to anyone.

**4. Natural Language Querying**

The neo4j graph database can be queried using a Graph RAG (retrieval-augmented generation) pipeline. Natural language queries will be passed to an LLM, which will interact with the graph database to extract relevant nodes, relationships, and other information. This information can then be passed on to the user in natural language through the LLM.

### Knowledge Graph Design

<img src="https://github.com/suyogyj/capstone-legal-docs-analysis/blob/main/LDA%20KG%20design.png" width="500">



