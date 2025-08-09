# app/core/rag_pipeline.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_chroma import Chroma
from langchain_core.runnables import RunnableLambda  # <-- Make sure this is imported
import datetime

from cognitive_inbox import config
from cognitive_inbox.embeddings import custom_bert_embedder

# FIX: Add more descriptive guidance for the LLM
metadata_field_info = [
    AttributeInfo(
        name="subject",
        description="The subject line of the email. Use a 'contains' operator for partial matches.",
        type="string",
    ),
    AttributeInfo(
        name="from",
        description="The sender of the email (e.g., 'John Doe <john.doe@example.com>'). Use a 'contains' operator for this field when a user is asking about a sender.",
        type="string",
    ),
    AttributeInfo(
        name="date",
        description=(
            "The date the email was sent, represented as a Unix timestamp (integer). "
            "Use this for queries about 'latest' or 'oldest' emails, or for filtering by a specific time period."
        ),
        type="integer",
    ),
    AttributeInfo(
        name="labels",
        description=(
            "A comma-separated list of labels applied to the email. Use a 'contains' operator to check if a label exists."
            "Example: 'Inbox, Important, Project-Updates, Invoices'"
        ),
        type="string",
    ),
]


def _format_docs(docs):
    """
    Helper function to format the retrieved documents into a single string for the prompt.
    This version converts Unix timestamps in the metadata back to human-readable dates.
    """
    formatted_docs = []
    for doc in docs:
        timestamp = doc.metadata.get('date')
        formatted_date = "Date not available"

        if timestamp:
            try:
                # Convert the Unix timestamp (which can be int or float) to a datetime object
                dt_object = datetime.datetime.fromtimestamp(float(timestamp))
                # Format the datetime object into a user-friendly string
                formatted_date = dt_object.strftime("%B %d, %Y")
            except (ValueError, TypeError):
                # This handles cases where the timestamp might be corrupted or not a number
                formatted_date = "Invalid date format"

        doc_string = (
            f"Email from: {doc.metadata.get('from')}\n"
            f"Date: {formatted_date}\n"
            f"Subject: {doc.metadata.get('subject')}\n"
            f"Labels: {doc.metadata.get('labels')}\n\n"
            f"{doc.page_content}"
        )
        formatted_docs.append(doc_string)

    return "\n\n".join(formatted_docs)


def create_conversational_agent():
    """
    Builds and returns the complete conversational RAG chain.
    This function encapsulates the entire logic for the core.
    """
    print("Building the improved conversational core...")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=config.OPENAI_API_KEY)

    embeddings = custom_bert_embedder.CustomBertEmbedder(
        model_path=config.EMBEDDING_MODEL_PATH
    )

    vectorstore = Chroma(
        collection_name=config.CHROMA_COLLECTION,
        persist_directory=config.CHROMA_DB_PATH,
        embedding_function=embeddings
    )

    # FIX 1: Create BOTH a self-query retriever and a standard vector retriever
    document_content_description = "The body text of an email"
    self_query_retriever = SelfQueryRetriever.from_llm(
        llm,
        vectorstore,
        document_content_description,
        metadata_field_info,
        verbose=True
    )
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    print("Retrievers created.")

    # FIX 2: Define the hybrid retriever function to combine and deduplicate results
    def hybrid_retriever(query):
        print(f"Executing hybrid search for query: '{query}'")
        # Try self-query retriever first
        try:
            self_results = self_query_retriever.get_relevant_documents(query, verbose=True)
            print(f"SelfQueryRetriever found {len(self_results)} documents.")
        except Exception as e:
            print(f"SelfQueryRetriever failed with error: {e}")
            self_results = []

        # Always get results from basic vector similarity search as a fallback/supplement
        vector_results = vector_retriever.get_relevant_documents(query)
        print(f"Standard Vector Retriever found {len(vector_results)} documents.")

        # Combine and deduplicate the results
        combined_results = []
        seen_ids = set()
        for doc in self_results + vector_results:
            # Use a unique identifier from metadata to prevent duplicates
            doc_id = doc.metadata.get('source_email_id', '') + str(doc.metadata.get('date', ''))
            if doc_id not in seen_ids:
                combined_results.append(doc)
                seen_ids.add(doc_id)

        print(f"Hybrid search returning {len(combined_results)} unique documents.")
        return combined_results

    # FIX 3: Use the custom hybrid_retriever in the RAG chain
    retriever = RunnableLambda(hybrid_retriever)

    # Master Prompt (guides the LLM on how to use the retrieved context to answer the question)
    prompt_template = """
You are a highly intelligent and diligent personal email assistant. Your task is to answer the user's question based *only* on the context provided from their email inbox.

- Be concise and directly answer the question.
- Cite the sender and date of the source email(s) for your answer.
- If the context does not contain the answer, you MUST state that you could not find any relevant emails. Do not make up information.

CONTEXT FROM EMAILS:
{context}

USER'S QUESTION:
{question}

YOUR ANSWER:
"""
    prompt = ChatPromptTemplate.from_template(prompt_template)

    rag_chain = (
            {
                "context": retriever | _format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
    )
    print("Improved conversational RAG chain successfully built.")

    return rag_chain