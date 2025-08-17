import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer, CrossEncoder
import openai
from backend import config
import time


class RAGPipeline:
    def __init__(self):
        """
        Initializes the RAG pipeline by loading all necessary components.
        """
        print("Initializing RAG Pipeline...")

        openai.api_key = config.OPENAI_API_KEY

        scripts_dir = os.path.dirname(__file__)
        app_dir = os.path.dirname(scripts_dir)
        backend_dir = os.path.dirname(app_dir)
        vectorstore_dir = os.path.join(backend_dir, 'vectorstore')
        faiss_index_path = os.path.join(vectorstore_dir, 'index.faiss')
        metadata_path = os.path.join(vectorstore_dir, 'metadata.pkl')

        print("Loading FAISS index and metadata...")
        self.index = faiss.read_index(faiss_index_path)
        with open(metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
        print("Loading complete.")

        print("Loading sentence transformer models...")
        self.bi_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        print("Models loaded.")

        print("RAG Pipeline Initialized Successfully.")

    def _create_prompt(self, question: str, context: list[str]) -> str:
        context_str = "\n\n---\n\n".join(context)

        prompt = f"""You are a highly intelligent and helpful personal email assistant. 
        Your task is to synthesize the information from the user's emails to answer their question.
        Use the following pieces of context from email conversations to answer the question at the end.

        Each piece of context starts with the date, sender information, and email subject. 
        Use this information to provide a clear timeline and attribute information to the correct 
        person or service (e.g., "On May 15th, an email from Amazon says...").

        Summarize the findings from the emails. If the emails mention where to find more information, point that out. 
        Based *only* on the text provided, generate a helpful response. 
        Keep your answer short, direct, and to the point, unless the user explicitly asks for detailed information.
        Include the date the email was sent and sender information.

    Context from emails:
    ---
    {context_str}
    ---
    User's Question: {question}
    Helpful Answer:"""
        return prompt

    def query(self, question: str, k_retriever: int = 30, k_reranker: int = 5) -> str:
        """
        Performs the full RAG process with a re-ranking step.
        """
        print(f"\nReceived query: '{question}'")

        print(f"1. Retrieving top {k_retriever} candidates with bi-encoder...")

        time1 = time.time()

        query_embedding = self.bi_encoder.encode([question], convert_to_numpy=True).astype('float32')
        faiss.normalize_L2(query_embedding)

        distances, indices = self.index.search(query_embedding, k_retriever)
        retrieved_docs = [self.metadata[idx] for idx in indices[0] if idx != -1]
        print(retrieved_docs)

        time2 = time.time()
        elapsed_time = time2 - time1
        print(f"Done retrieving. Elapsed time: {elapsed_time:.4f} seconds")

        print(f"2. Re-ranking the retrieved candidates with cross-encoder...")
        time1 = time.time()
        pairs = [[question, doc['chunk_text']] for doc in retrieved_docs]

        if not pairs:
            return "I could not find any relevant information in your emails to answer this question."

        scores = self.cross_encoder.predict(pairs, batch_size=8)
        time2 = time.time()
        elapsed_time = time2 - time1
        print(f"Done scoring. Elapsed time: {elapsed_time:.4f} seconds")

        scored_docs = list(zip(scores, retrieved_docs))
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        print(f"3. Selecting top {k_reranker} documents after re-ranking...")
        time1 = time.time()
        final_contexts = []
        for score, doc in scored_docs[:k_reranker]:
            sender = doc.get('from', 'Unknown Sender')
            context_line = f"On {doc['date']}, an email from '{sender}' with subject '{doc['email_subject']}':\n{doc['chunk_text']}"
            final_contexts.append(context_line)
            print(f"Selected doc on {doc['date']} from '{sender}' with score {score:.4f}")
        time2 = time.time()
        elapsed_time = time2 - time1
        print(f" Selected re-ranked docs. Elapsed time: {elapsed_time:.4f} seconds")

        print("4. Creating prompt for LLM...")
        prompt = self._create_prompt(question, final_contexts)

        print("5. Sending request to OpenAI API...")
        time1 = time.time()
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "developer", "content": "You are a helpful and highly intelligent email assistant. "
                                                     "Include date and sender information for the retrieved emails."
                                                     "Keep answers short and direct."},
                    {"role": "user", "content": prompt}
                ],
            )
            final_answer = response.choices[0].message.content
            time2 = time.time()
            elapsed_time = time2 - time1
            print(f"6. Received answer from OpenAI.  Elapsed time: {elapsed_time:.4f} seconds")
            print(f"LLM Raw Output: \n'{final_answer}'\n")
            return final_answer
        except Exception as e:
            print(f"An error occurred with the OpenAI API: {e}")
            return "Sorry, I encountered an error while trying to generate an answer."

# verification
# if __name__ == '__main__':
#     try:
#         pipeline = RAGPipeline()
#
#
#         test_question_1 = "What are the instructions for the SURE poster presentation?"
#         answer_1 = pipeline.query(test_question_1)
#         print("\n" + "=" * 50)
#         print(f"Question: {test_question_1}")
#         print(f"Answer: {answer_1}")
#         print("=" * 50 + "\n")
#
#
#         test_question_2 = "Is there any marketing email offering a 50% discount? "
#         answer_2 = pipeline.query(test_question_2)
#         print("\n" + "=" * 50)
#         print(f"Question: {test_question_2}")
#         print(f"Answer: {answer_2}")
#         print("=" * 50 + "\n")
#
#     except Exception as e:
#         print(f"An error occurred during pipeline initialization or testing: {e}")
