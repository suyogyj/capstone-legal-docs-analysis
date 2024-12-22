# Capstone Project: Legal Text Analytics with Large Language Models

This project, supervised by Dr. Lipika Dey and Dr. Partha Pratim Das, explores the use of Large Language Models (LLMs) and Knowledge Graphs to enable legal text analytics, focusing on food safety-related cases in India (2022–2023). The methodology and results demonstrate the feasibility of LLMs+KGs for summarization, entity extraction, and corpus-level analysis of legal texts.

The full report can be found in [Capstone_Report.pdf](https://github.com/suyogyj/capstone-legal-docs-analysis/blob/main/Capstone_Report.pdf).

**Note:** I am currently working on expanding the dataset from ~200 cases to ~<u>2500</u> for further analysis. This project will be continued until at least May 2025 as my capstone *thesis*. We are also working towards submitting the results on this expanded dataset at major conferences.


## Table of Contents

- [Capstone Project: Legal Text Analytics with Large Language Models](#capstone-project-legal-text-analytics-with-large-language-models)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Dataset](#dataset)
  - [Methodology](#methodology)
  - [Results](#results)
  - [Conclusion and Future Work](#conclusion-and-future-work)
  - [Directory Structure](#directory-structure)
  
## Introduction

- **Background**: Legal text analysis is complex, requiring tools to handle large corpora efficiently. LLMs can summarize and extract entities from documents but lack corpus-wide context. This limitation is addressed by using the LLMs to populate Knowledge Graphs representing the corpus.
- **Objectives**:
  - Automated summarization of legal documents.
  - Extraction of key legal entities like statutes, provisions, and case participants.
  - Creation of a Knowledge Graph to represent and analyze entity relationships.
  - Executing meaningful queries to extract corpus-level insights.

## Dataset

A corpus of 196 Indian court cases on food safety was collected, filtered, and preprocessed. Minimal preprocessing was applied to retain document integrity.

## Methodology

- **Data Collection & Preprocessing**: Used web scraping tools to gather and clean data.
- **Knowledge Graph Design**: Modeled legal concepts and relationships, emphasizing statutes and provisions.

![LDA KG design](https://github.com/user-attachments/assets/6c7ca12e-b447-40ef-9f19-dbbc83cc4eb6)
  
- **Entity Extraction**:
  - Traditional Named Entity Recognition (NER) models.
  - LLM-based extraction using structured prompts.
- **Summarization**: Generated concise, accurate document summaries using GPT-4o-mini.
- **Knowledge Graph Construction**: Populated and queried a Neo4j graph database to identify patterns and trends.

![full_KG](https://github.com/user-attachments/assets/844e0b91-6b10-4012-bf54-440b21c1f47c)


## Results

- **LLM Performance**:
  - Compared LLM and NER models for entity extraction. LLMs demonstrated better generalizability but with mixed precision.
  - Summarization was assessed using BERT and ROUGE-L metrics.
- **Knowledge Graph Insights**:
  - Most frequently cited provisions and related case clusters were identified.
  - Advanced queries revealed relationships between cases using Jaccard similarity and shared citations.

## Conclusion and Future Work

- **Limitations**: The dataset scope and reliance on graph query languages limit accessibility.
- **Future Work**:
  - Expand datasets for broader trends and insights.
  - Enhance graph relationships to capture more nuanced legal contexts.
  - Develop a natural language querying interface for user-friendly interactions.

## Directory Structure

```
Directory structure:
└── suyogyj-capstone-legal-docs-analysis/
    ├── figures/
    ├── notebooks/
    │   ├── ner_extraction.ipynb
    │   ├── openai_extraction.ipynb
    │   ├── deduplication.ipynb
    │   ├── case_facts_and_verification.ipynb
    │   ├── openai_QA.ipynb
    │   ├── lengths.dat
    │   ├── accuracy_calculation.ipynb
    │   ├── create_graph.ipynb
    │   ├── food_safety_newdocs.csv
    │   └── llama_summarization.ipynb
    ├── Capstone_Presentation.pdf
    ├── sheets/
    │   ├── food_safety_answers.csv
    │   ├── LDA_verification_questions.xlsx
    │   ├── food_safety_questions.csv
    │   ├── comparison/
    │   │   ├── comparison_petitioners.csv
    │   │   ├── comparison_statutes.csv
    │   │   ├── confusion_matrices/
    │   │   ├── comparison_provisions.csv
    │   │   ├── comparison_gpe.csv
    │   │   ├── comparison_org.csv
    │   │   ├── comparison_respondents.csv
    │   │   ├── comparison_precedents.csv
    │   │   └── comparison_judges.csv
    │   └── extracted/
    │       ├── openai_extracted.csv
    │       └── ner_extracted.csv
    ├── data_exploration.ipynb
    ├── scrapers/
    │   └── kanoon_searchpage_scraper.py
    ├── Docs/
    │   ├── food-safety/
    │   ├── food-safety-old/
    │   └── green-tribunal-2021-2023/
    │       ├── green_tribunal_statutes_deduplicated.csv
    │       └── green_tribunal_NER_tagged.csv
    ├── README.md
    ├── Capstone_Report.pdf
    └── misc/
        └── queries.txt
```