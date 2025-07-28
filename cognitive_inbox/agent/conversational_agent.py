# cognitive_inbox/agent/conversational_agent.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_chroma import Chroma
import datetime

from cognitive_inbox import config
from cognitive_inbox.embeddings import custom_bert_embedder

metadata_field_info = [
    AttributeInfo(
        name="subject",
        description="The subject line of the email",
        type="string",
    ),
    AttributeInfo(
        name="from",
        description="The sender of the email (e.g., 'John Doe <john.doe@example.com>')",
        type="string",
    ),
    AttributeInfo(
        name="date",
        description=(
            "The date the email was sent, represented as a Unix timestamp (integer). "
            "When filtering, you MUST convert any dates or times into a Unix timestamp."
        ),
        type="integer",
    ),
    AttributeInfo(
        name="labels",
        description=(
            "A comma-separated list of labels or categories applied to the email in Gmail. "
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
    This function encapsulates the entire logic for the agent.
    """
    print("Building the conversational agent...")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=config.OPENAI_API_KEY)

    embeddings = custom_bert_embedder.CustomBertEmbedder(
        model_path=config.EMBEDDING_MODEL_PATH
    )

    # Wrap the collection in LangChain's Chroma class
    vectorstore = Chroma(
        collection_name=config.CHROMA_COLLECTION,
        persist_directory=config.CHROMA_DB_PATH,
        embedding_function=embeddings
    )

    # Create the Self-Query Retriever
    document_content_description = "The body text of an email"
    retriever = SelfQueryRetriever.from_llm(
        llm,
        vectorstore,
        document_content_description,
        metadata_field_info,
        verbose=True
    )
    print("Self-Query Retriever created.")

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
    print("Prompt template defined.")

    # Construct the final RAG Chain using LangChain Expression Language (LCEL)
    rag_chain = (
            {
                "context": retriever | _format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
    )
    print("Conversational RAG chain successfully built.")

    return rag_chain
