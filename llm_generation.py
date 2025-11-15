import streamlit as st
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv('GEMINI_API_KEY')

def load_rag_system():
    """Load FAISS index and documents"""
    
    index = faiss.read_index("data/sephora_faiss.index")
    
    # Load documents
    with open('data/sephora_documents.pkl', 'rb') as f:
        data = pickle.load(f)
    
    embedding_model = SentenceTransformer(
        data.get('embedding_model_name', 'all-MiniLM-L6-v2')
    )
    
    return index, data['documents'], embedding_model

# Load system
index, documents, embedding_model = load_rag_system()
print(f"📜 Loaded {len(documents)} documents")

def search_products(query, top_k=5):
    """Search for relevant products"""
    
    query_embedding = embedding_model.encode([query])
    
    # Search in FAISS
    distances, indices = index.search(
        query_embedding.astype('float32'), 
        top_k
    )
    
    # Get results with full document structure
    results = []
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        
        doc = documents[idx]  # This already has text + metadata
        results.append({
            'rank': i + 1,
            'text': doc['text'],
            'metadata': doc['metadata'],
            'distance': float(dist),
            'similarity_score': 1 / (1 + dist)  # Convert distance to similarity
        })
    
    return results

def generate_response(query, retrieved_docs, user_api_key):
    """Generate natural language response using LLM"""
  
    for attempt, key in enumerate([user_api_key, api_key]):
        if key is None:
            continue
    # Create context from retrieved documents
        try:
            context = "\n\n".join([
                f"Product {i+1}:\n{doc}" 
                for i, doc in enumerate(retrieved_docs)
            ])
            
            prompt = f"""You are a helpful Sephora beauty advisor. Based on the following products, 
        answer the customer's question naturally and recommend the best options.

        Customer Question: {query}

        Available Products:
        {context}

        Reply directly to the customer question.Provide a helpful recommendation with reasoning. Mention specific product names, prices, and key features."""
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
            return response.text
        except Exception as e:
            if attempt == 0 :
                print(f"User Key Invalid {e}. Trying our key...")
                continue
            else:
                return f"Error: {str(e)}. Please provide a valid API key to continue"
    return "No valid API key available."
 

    

def rag_chatbot(query, top_k=3, user_api_key = None):
    """Complete RAG pipeline"""
    
    print(f"🔍 Searching for: {query}")
    
    # 1: Retrieve relevant documents
    retrieved_docs = search_products(query, top_k=top_k)
    # Removing Documents too dissimilar 
    retrieved_docs= [r for r in retrieved_docs if r['similarity_score']>0.4]

    if len(retrieved_docs) > 0:
        print(f"✅ Found {len(retrieved_docs)} relevant products")
    else:
        print(f"❌ No relevant products")
        return {
            'query' : query,
            'response' : 'Sorry no products match this description in our catalogue',
        }
    
    # 2: Generate response
    response = generate_response(query, retrieved_docs, user_api_key)
    
    return {
        'query': query,
        'response': response,
        'retrieved_products': [
            {
                'name': doc['metadata']['product_name'],
                'brand': doc['metadata']['brand_name'],
                'price': doc['metadata']['price_usd'],
                'rating': doc['metadata']['rating']
            }
            for doc in retrieved_docs
        ]
    }
