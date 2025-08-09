# Cognitive Inbox - A Real-Time Conversational Email Assistant

Developing a conversational email assistant using langchain.

The goal is to have a web application where I can have a natural language conversation with my entire Gmail inbox. 
The chat agent will be able to retrieve information based on content, dates, and senders, 
and will process (update the vector database) with new emails in real-time for up-to-date information.

```mermaid
graph TD
    subgraph Phase 1: Indexing Pipeline (Offline - Data Preparation)
        direction LR
        G[fa:fa-google Gmail API] -->|1. Fetch Emails| S1(scripts/01_fetch_emails.py)
        S1 -->|2. Save Raw| D1(data/raw/emails.csv)
        D1 -->|3. Chunk Text| S2(scripts/02_prepare_chunks.py)
        S2 -->|4. Save Chunks| D2(data/processed/email_chunks.csv)
        D2 -->|5. Generate Embeddings| C[fa:fa-cloud Google Colab w/ GPU]
        C -->|SentenceTransformer Model| C
        C -->|6. Save Embeddings| D3(data/processed/email_embeddings.npy)
        subgraph Load into Vector Store
            D2 --> VDB[(fa:fa-database Vector Store<br>ChromaDB)]
            D3 --> VDB
        end
    end

    subgraph Phase 2: Querying Pipeline (Online - Live Chat)
        direction TD
        U[fa:fa-user User] -->|1. Asks Question| UI(Browser / Flask Frontend)
        UI -->|2. POST Request| API(Flask API<br>app/main.py)
        
        subgraph RAG Core Logic (app/core/rag_pipeline.py)
            API -->|3. User Query| RAG
            RAG -->|4. Embed Query| M(Embedding Model<br>all-MiniLM-L6-v2)
            M -->|Query Vector| RAG
            RAG -->|5. Similarity Search| VDB_Query[(fa:fa-database Vector Store<br>ChromaDB)]
            VDB_Query -->|6. Retrieve Relevant Chunks<br>+ Metadata| RAG
            RAG -->|7. Formulate Prompt<br>(Query + Context)| RAG
            RAG -->|8. Send Prompt| LLM[fa:fa-robot LLM API<br>OpenAI/GPT]
            LLM -->|9. Generate Answer| RAG
        end

        RAG -->|10. Send Answer| API
        API -->|11. Display Response| UI
        UI -->|12. Sees Answer| U
    end

    style VDB fill:#D6EAF8,stroke:#333,stroke-width:2px
    style VDB_Query fill:#D6EAF8,stroke:#333,stroke-width:2px
    style LLM fill:#D5F5E3,stroke:#333,stroke-width:2px
    style C fill:#FEF9E7,stroke:#333,stroke-width:2px
```
