# UrbanCart Ask-AI — RAG-Powered Product & Policy Q&A Assistant

> ⚠️ **Work in progress** — being built stage by stage; see the roadmap below.

An AI shopping assistant for UrbanCart (a simulated Indian e-commerce marketplace)
that answers customer product and policy questions **grounded in the actual catalog
and policy documents** — it is never allowed to guess.

## The Business Problem

UrbanCart handles ~6,000 support conversations/day; ~40% are repetitive questions
answerable from documentation. The existing keyword-matcher bot fails on Hinglish,
comparisons, and combined product+policy questions. This service deflects the
repetitive volume and cleanly escalates everything else to a human agent.

## Project Structure

```
urbancart-ask-ai/
├── src/              # Reusable source code (cleaning, RAG chain, agent tools)
├── data/
│   ├── raw/          # Generated messy data — never hand-edited
│   └── processed/    # Cleaned data, produced by code from raw/
├── notebooks/        # EDA & exploration notebooks
├── tests/            # Automated tests
├── config/           # Project configuration
└── requirements.txt  # Pinned dependencies
```

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Roadmap

- [x] Project scaffold, environment, dependency pinning
- [ ] Synthetic data generation (5,000-product catalog, chat logs, policy docs)
- [ ] EDA & data-quality profiling
- [ ] Cleaning pipeline with audit logging
- [ ] Intent classification (LLM prompt engineering)
- [ ] RAG pipeline (chunking → embeddings → vector store → grounded answers)
- [ ] Agentic tool layer (stock, orders, recommendations, escalation)
- [ ] Evaluation (faithfulness, relevancy, consistency)
- [ ] Deployment (FastAPI microservice + Gradio demo)
- [ ] Cost & business-impact analysis

## Tech Stack

Python 3.11 · pandas · LangChain · FAISS/Chroma · OpenAI · FastAPI · Gradio

---
*Portfolio project with simulated data — demonstrates the architecture, evaluation
discipline, and production-readiness thinking a real GenAI initiative requires.*