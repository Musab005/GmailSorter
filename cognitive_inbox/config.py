import os
from dotenv import load_dotenv

# By default, load_dotenv will look for a .env file in the current directory 
# or parent directories. But we can specify the root project directory explicitly
# to make it robust.
project_dir = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(project_dir, '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found. Please create one with your API keys and paths.")

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- File and Directory Paths ---
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH")

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")

CHROMA_COLLECTION = "gmail_embeddings"

GOOGLE_CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH")

GOOGLE_TOKEN_PATH = os.getenv("TOKEN_PATH")

# --- Validation ---
if not OPENAI_API_KEY:
    print("FATAL ERROR: OPENAI_API_KEY is not set in the .env file.")
