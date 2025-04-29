# Gmail Auto-Sort Agent with ML: Detailed Project Plan

## Phase 1: Labeling via Gmail Web
Log in to Gmail and create a fixed set of meaningful labels (e.g., Work, Finance, Social, etc.).
Manually apply these labels to a diverse set of emails to serve as your training dataset.

### Gmail API Setup:
Enable the Gmail API on Google Cloud Console.
Set up OAuth2 credentials and download your credentials.json.
Write a script to authenticate and connect to the Gmail API.

### Data Extraction:
Fetch all emails that have at least one of your custom labels.
Extract fields like subject, sender, body, and assigned labels.
Save this as a JSON ile for further use.

## Phase 2: Preprocessing & Model Training
Preprocessing: Clean email text (remove HTML, signatures, quoted replies), 
format the dataset as (email_text → label) pairs.
Model Selection & Fine-tuning: Use a pre-trained model (e.g., bert-base-uncased, flan-t5-base, or DistilBERT).
Fine-tune on the labeled dataset (multi-class text classification).
Training on Colab (if needed): Use Google Colab with GPU for faster training.
Save the trained model to Google Drive or download for deployment.

## Phase 3: Inference & Gmail Integration
Build Inference Pipeline: Write a function that accepts a new email and predicts a label.
Use the Gmail API to apply the predicted label to the email.
Deployment on Google Cloud: Package the model and inference code into a Cloud Function or Cloud Run service.
Store the model in Google Cloud Storage.
Set up a trigger (e.g., Gmail Pub/Sub, polling) to detect new emails.
Automation & Feedback: As new emails arrive, they are processed and labeled automatically.
Add a feedback mechanism (optional) to manually correct predictions and periodically re-train the model.

## Key Learning Outcomes

### Applied NLP with Pre-trained Models
Understand how to adapt and fine-tune Hugging Face models (e.g., bert-base-uncased, distilbert, flan-t5) for text classification.
Learn how to tokenize and preprocess real-world noisy data (email content).
Evaluate and troubleshoot model performance (confusion matrix, F1-score, error analysis).
Understand the limitations of pre-trained models on domain-specific data (like email content).

### Gmail API Integration
Gain hands-on experience with the Gmail API, including:
Authenticating using OAuth 2.0.
Fetching and filtering emails based on labels.
Parsing email content from MIME format.
Programmatically applying Gmail labels.

### Data Engineering & Preprocessing
Learn to work with unstructured, semi-structured email data (HTML, MIME, text, replies).
Build a pipeline to clean and normalize email bodies.
Design a robust data structure for training and inference (e.g., JSON or pandas DataFrame format with subject + body + label).

### Model Deployment on Google Cloud
Learn how to:
Package your model and inference code for deployment (Cloud Function or Cloud Run).
Use Google Cloud Storage for model hosting.
Handle incoming data events with Pub/Sub or scheduled polling.
Automate end-to-end inference + labeling for incoming emails.

### Testing, Debugging & Local Development
Write unit and integration tests for your scripts.
Debug Gmail API, text cleaning, and model inference logic in isolation.
Run the full pipeline locally using test data.

### Project Architecture & Software Engineering
Structure a real-world, multi-phase ML application.
Use good software practices:
Modular code (separation of concerns).
Environment configs (.env, config.yaml).
Logging and monitoring during inference.
Maintain reproducibility and scalability in your project.

### Project directory structure

gmail_auto_sorter/
│
├── data/                          # Local data storage
│   ├── extracted_emails.json     # Labeled emails fetched via Gmail API
│   ├── processed_data.json       # Preprocessed dataset ready for training
│
├── notebooks/                    # Google Colab notebooks
│   ├── data_exploration.ipynb
│   └── model_training.ipynb
│
├── scripts/                      # Runnable scripts for end-to-end tasks
│   ├── fetch_emails.py          # Extract labeled emails using Gmail API
│   ├── preprocess_data.py       # Clean and convert raw emails to model-ready format
│   ├── train_model.py           # Fine-tune model using Hugging Face
│   ├── evaluate_model.py        # Generate evaluation metrics
│   ├── run_inference.py         # Run predictions locally
│   └── deploy_model.py          # Push model to Google Cloud
├── src/
│   ├── __init__.py
│   ├── gmail_auth.py             # Gmail API authentication logic
│   ├── fetch_labeled_emails.py  # Fetch emails + labels from Gmail
│   ├── preprocessor.py           # Email text cleaning and formatting
│   ├── model.py                  # Fine-tuning logic for LLM
│   ├── inference.py              # Predict and assign labels
│   └── deploy/
│       ├── cloud_function.py     # GCP Cloud Function entry point
│       ├── config.yaml
│       └── requirements.txt
│
├── model/                        # Saved model and tokenizer
│   ├── tokenizer/
│   └── classifier/
│
├── tests/                        # Unit tests
│   ├── test_fetching.py
│   └── test_model.py
│
├── config/                       
│   └── credentials.json          # Gmail API OAuth2 credentials
│
├── .env                          # For local secrets (GMAIL_USER, etc.)
├── requirements.txt              # Project dependencies
├── README.md
└── run_local_pipeline.py         # For running end-to-end inference locally