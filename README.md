# Sephora RAG

A Retrieval-Augmented Generation (RAG) chatbot for Sephora beauty products, built with FAISS vector search and Google Gemini.

## Features

- Semantic search over Sephora product catalog
- Natural language product recommendations
- Interactive Streamlit interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Gemini API key:
   - Create a `.streamlit/secrets.toml` file or set `GEMINI_API_KEY` environment variable
   - Or use the API key input in the app interface

3. Run the app:
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser to access the app.

## Roadmap

Updates that I will someday do:

1. Connect to Neo4J and incorporate GraphRAG
2. Add images as input data and output data to make the recommendations better
3. Add an evaluation method to suggest what methodology does best

