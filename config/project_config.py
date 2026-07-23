"""
Central configuration for the UrbanCart Ask-AI Assistant.

Every architectural decision lives here with a one-line justification,
so any knob (model, chunk size, threshold) can be found and tuned in one place.
All values were chosen by reasoning against the project's requirements and KPIs
(faithfulness, latency < 3s, cost < Rs 0.50/query, escalation < 15%).
"""

PROJECT_CONFIG = {
    "project_name": "UrbanCart Ask-AI Assistant",
    "version": "1.0.0",

    # --- Embedding model (Decision #1) ---
    # Multilingual open-source model: handles Hinglish (a hard requirement) and
    # is free (protects the cost KPI). Trades a little English-only quality for a
    # large gain on Hinglish, which is a first-class need for our user base.
    "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",

    # --- LLM + temperature (Decision #2) ---
    # gpt-3.5-turbo: in RAG the LLM mostly rephrases retrieved facts, so a frontier
    # model is overkill; 10-20x cheaper keeps us under the Rs 0.50/query budget.
    # (A stronger model is reserved only for the Stage 8 LLM-as-judge evaluation.)
    "llm_model": "gpt-3.5-turbo",
    "router_temperature": 0.0,      # classification must be reproducible/testable
    "answer_temperature": 0.0,      # grounded answers should be reproducible, not creative

    # --- Vector store (Decision #3) ---
    # FAISS: free + local (same tier as Chroma; cost is NOT the differentiator).
    # Chosen to learn metadata filtering manually; low-stakes at 5,000 docs.
    # Would move to a managed DB (Pinecone) only if we outgrew local scale.
    "vector_db": "faiss",

    # --- Retrieval numbers (Decision #4) ---
    "product_chunk_size": 250,      # product specs are short, structured facts -> small, precise chunks
    "policy_chunk_size": 600,       # policy prose has multi-sentence rules -> larger chunks
    "chunk_overlap": 90,            # ~15% of policy chunk: protects rules at chunk boundaries without wasteful duplication
    "top_k_retrieval": 4,           # sweet spot: enough to catch the answer, not so many it adds noise/cost

    # --- Escalation (business dial) ---
    # Confidence below this -> escalate to a human instead of guessing.
    # 0.6 is a balanced starting point, to be tuned once Stage 8 eval + real usage data exist.
    "max_escalation_threshold": 0.6,
}


if __name__ == "__main__":
    # Running this file directly prints the config — a quick sanity check.
    print(f"Loaded config for: {PROJECT_CONFIG['project_name']} v{PROJECT_CONFIG['version']}")
    for key, value in PROJECT_CONFIG.items():
        print(f"  {key}: {value}")