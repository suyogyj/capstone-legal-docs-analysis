# Capstone Project: Legal Text Analytics with Large Language Models

This project explores the integration of Large Language Models (LLMs) and Knowledge Graphs to enhance legal text analytics, focusing on food safety-related cases in India (2022–2023). The methodology and results demonstrate how these techniques can automate summarization, entity extraction, and corpus-level analysis of legal texts.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Dataset](#dataset)
3. [Literature Review](#literature-review)
4. [Methodology](#methodology)
5. [Results](#results)
6. [Conclusion and Future Work](#conclusion-and-future-work)
7. [Appendices](#appendices)

---

## Introduction

- **Background**: Legal text analysis is complex, requiring tools to handle large corpora efficiently. LLMs can extract and summarize legal entities but lack corpus-wide context, addressed by combining them with Knowledge Graphs.
- **Objectives**:
  - Automated summarization of legal documents.
  - Extraction of key legal entities like statutes, provisions, and case participants.
  - Creation of a Knowledge Graph to represent and analyze entity relationships.
  - Executing meaningful queries to extract corpus-level insights.

## Dataset

A corpus of 196 Indian court cases on food safety was collected, filtered, and preprocessed. Minimal preprocessing was applied to retain document integrity.

## Literature Review

Explores traditional NLP approaches for legal analytics and the shift towards LLMs for tasks like entity extraction and summarization. Discusses challenges and benefits of combining LLMs with Knowledge Graphs for structured, cross-document analysis.

## Methodology

- **Data Collection & Preprocessing**: Used web scraping tools to gather and clean data.
- **Knowledge Graph Design**: Modeled legal concepts and relationships, emphasizing statutes and provisions.

![LDA KG design](https://github.com/user-attachments/assets/6c7ca12e-b447-40ef-9f19-dbbc83cc4eb6)
  
- **Entity Extraction**:
  - Traditional Named Entity Recognition (NER) models.
  - LLM-based extraction using structured prompts.
- **Summarization**: Generated concise, accurate document summaries using GPT-4o-mini.
- **Knowledge Graph Construction**: Populated and queried a Neo4j graph database to identify patterns and trends.

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
