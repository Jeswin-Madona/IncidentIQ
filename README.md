# IncidentIQ — AI-Powered Incident Intelligence Dashboard

## Project Overview
**IncidentIQ** is a simple, beginner-friendly Generative AI (GenAI) dashboard application designed to analyze incident reports and detect semantically similar past incidents. It combines text generation using an open-source Large Language Model (LLM) with semantic similarity search using sentence embeddings.

---

## Problem Statement
When security personnel or administrators receive unstructured incident reports, it can be difficult to quickly analyze the risk, summarize key information, or identify if similar incidents have occurred previously. **IncidentIQ** demonstrates how Generative AI can automatically summarize incident descriptions while vector embeddings help discover historical patterns without needing exact keyword matches.

---

## Detailed Application Flow: Step-by-Step

Understanding the complete end-to-end flow of IncidentIQ is easy when broken down into 4 key phases:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: APPLICATION STARTUP                         │
│ 1. Streamlit boots `app.py`.                                            │
│ 2. `@st.cache_resource` loads `all-MiniLM-L6-v2` embedding model into RAM.│
│ 3. `@st.cache_data` loads 18 historical records from `incidents.json`.   │
│ 4. `@st.cache_data` precomputes 384-D vector embeddings for all 18 items.│
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       PHASE 2: USER INTERACTION                         │
│ 1. User enters natural language incident description into text area.    │
│ 2. Clicking "Clear / New Analysis" resets `st.session_state` & reruns.   │
│ 3. Clicking "Analyze Incident" triggers the dual-track AI workflow.     │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│ PHASE 3A: TRACK 1 - GENERATIVE  │     │  PHASE 3B: TRACK 2 - SEMANTIC   │
│       AI TEXT ANALYSIS          │     │        SIMILARITY SEARCH        │
│                                 │     │                                 │
│ 1. Calls `analyze_incident()`   │     │ 1. User text converted to       │
│    in `llm.py`.                 │     │    384-D vector using           │
│ 2. Wraps text in structured     │     │    `embedding_model.encode()`.  │
│    prompt template.             │     │ 2. `cosine_similarity()` computes│
│ 3. Sends prompt to `distilgpt2` │     │    angle scores against all 18  │
│    via Hugging Face `pipeline`. │     │    pre-calculated vectors.      │
│ 4. DistilGPT-2 predicts next    │     │ 3. Scores sorted descending.    │
│    tokens (max 100 tokens).     │     │ 4. Filter threshold >= 40%      │
│ 5. Returns generated text.      │     │    and select Top 3 matches.   │
└─────────────────────────────────┘     └─────────────────────────────────┘
                 │                                       │
                 └───────────────────┬───────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 PHASE 4: UI DASHBOARD RENDERING                         │
│ 1. Computes live metrics (AI status, match count, max similarity %).    │
│ 2. Renders dynamic `### Analysis Overview` metric cards.                │
│ 3. Renders `### AI Analysis` text block with disclaimer caption.        │
│ 4. Computes matched severity breakdown (High / Medium / Low counts).    │
│ 5. Renders `### Similar Incidents` expander cards for top matches.       │
│ 6. Displays bottom educational expanders (Flow, Tech Stack, Limits).   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Code Traceability & File Responsibility

### 1. `app.py` (Main Dashboard & Search Engine)
- **Role:** Web interface, state management, caching, vector embedding, cosine similarity calculation, and metric rendering.
- **Key Functions:**
  - `load_embedding_model()`: Cached function loading `SentenceTransformer("all-MiniLM-L6-v2")`.
  - `load_dataset()`: Reads `incidents.json` safely with error checks.
  - `compute_dataset_embeddings()`: Encodes all 18 dataset incident descriptions into vector arrays at app startup.

### 2. `llm.py` (Generative AI Core Engine)
- **Role:** Handles prompt construction and invokes DistilGPT-2 via Hugging Face Transformers.
- **Key Functions:**
  - `get_generator()`: Cached initializer loading `pipeline("text-generation", model="distilgpt2")`.
  - `analyze_incident(incident)`: Validates input string, constructs structured prompt, runs inference, and returns completed text.

### 3. `incidents.json` (Local Dataset)
- **Role:** Contains 18 fictional sample incident records used as historical context for similarity search.
- **Record Schema:** Each item contains `id`, `incident`, `type`, `severity`, and `location`.

---

## Data Transformation Lifecycle

| Stage | Input Data | Processing Component | Output Data |
| :--- | :--- | :--- | :--- |
| **Startup** | Raw JSON text in `incidents.json` | `SentenceTransformer.encode()` | `18 x 384` floating-point NumPy matrix |
| **User Input** | User types in text area | Streamlit text widget | Raw Python String `incident_input` |
| **Track 1 (LLM)** | Raw string `incident_input` | `analyze_incident()` prompt template + DistilGPT-2 | Generated text string |
| **Track 2 (Embedding)** | Raw string `incident_input` | `embedding_model.encode([incident_input])` | `1 x 384` NumPy array `user_embedding` |
| **Track 2 (Similarity)** | `user_embedding` + dataset matrix | `sklearn.metrics.pairwise.cosine_similarity` | Array of 18 cosine similarity scores (`0.0` - `1.0`) |
| **Track 2 (Filter)** | 18 similarity scores | `sort()` + `threshold >= 0.40` + `[:3]` slice | Top 3 matching record dictionaries with % score |
| **UI Display** | Top 3 matches + LLM text string | Streamlit UI component rendering | Interactive cards, metric badges, severity breakdown |

---

## Features
- **Incident Input Area:** Text box allowing users to enter natural language incident descriptions.
- **AI-Generated Analysis:** Automated incident summarization and key detail extraction powered by DistilGPT-2.
- **Dynamic Analysis Overview Dashboard:** Real-time metrics showing AI analysis status, count of similar incidents found, highest similarity percentage, and total dataset record count.
- **Semantic Similarity Search:** Vector similarity search identifying past incidents with similar context.
- **Top Similar Incidents:** Displays top 3 matching historical records with Incident ID, description, similarity percentage, type, severity, and location.
- **Matched Severity Breakdown:** Summary breakdown (High, Medium, Low) of matched historical incidents.
- **Interactive Reset / Clear:** One-click button to clear input and start a new analysis.
- **Educational Expanders:** In-app explanations for pipeline flow, tech stack, and limitations.
- **Robust Error Handling:** Friendly notifications for empty inputs, missing datasets, or model failure.

---

## Technologies Used

- **Python** → Primary programming language for model invocation and app logic.
- **Streamlit** → Web application framework creating the user interface without HTML/JS.
- **Hugging Face Transformers** → Open-source library providing pre-trained models and the `pipeline()` API.
- **PyTorch** → Deep learning framework executing matrix operations and tensor processing.
- **DistilGPT-2** → Lightweight 82-million parameter autoregressive text-generation model.
- **Sentence Transformers** → Python framework for computing dense vector representations.
- **all-MiniLM-L6-v2** → Sentence transformer model mapping text into a 384-dimensional vector space.
- **scikit-learn** → Machine learning library providing cosine similarity metric calculations.
- **JSON Dataset (`incidents.json`)** → Local file containing historical incident records.

---

## Dataset (`incidents.json`)
- **Nature of Dataset:** A small, manually created JSON file containing 18 sample incident records.
- **Role in Project:** Serves as a searchable historical repository for similarity search.
- **Important Note:** `incidents.json` is **NOT** used to fine-tune or train DistilGPT-2.
- **Schema Fields:** Each record contains `id`, `incident`, `type`, `severity`, and `location`.

---

## AI Model (DistilGPT-2)
- **Model Name:** `distilgpt2`
- **Purpose:** Text generation and structured prompt completion.
- **Details:** DistilGPT-2 is a distilled (60% smaller, faster) version of OpenAI's GPT-2 model with 82 million parameters.
- **Behavior Note:** Because it is a small open-source model without instruction fine-tuning, generated responses can occasionally be repetitive or include incomplete sentences.

---

## Embedding Model (`all-MiniLM-L6-v2`)
- **Purpose:** Converts text sentences into 384-dimensional numerical vectors (embeddings).
- **Function:** Captures semantic context so that sentences expressing similar ideas are placed close together in mathematical space.

---

## Cosine Similarity
- **Definition:** A mathematical measurement of the cosine of the angle between two numerical vector embeddings.
- **Range:** `0.0` (completely different meaning) to `1.0` (identical meaning).
- **Application:** Compares the user's input vector against all 18 dataset vectors to rank the top 3 matches.

---

## Day-by-Day Development Progression

- **DAY 1:** Basic LLM text generation using Python, Hugging Face Transformers, and DistilGPT-2.
- **DAY 2:** Implemented prompt engineering in `llm.py` to structure AI incident analysis outputs.
- **DAY 3:** Built the interactive web interface using Streamlit (`app.py`).
- **DAY 4:** Integrated `incidents.json` dataset, `all-MiniLM-L6-v2` embeddings, and cosine similarity for semantic matching.
- **DAY 5:** Created the final presentation-ready GenAI dashboard, added dynamic overview metrics, severity breakdown, interactive reset button, educational expanders, error handling, and complete documentation.

---

## How To Run

### 1. Activate Virtual Environment
```powershell
venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Streamlit Application
```powershell
streamlit run app.py
```
Access the application in your browser at `http://localhost:8501`.

---

## Example Input
```text
Yesterday at around 8 PM, I was walking near the railway station when a man started following me. I entered a nearby shop and waited until he left.
```

---

## Expected Output
1. **Analysis Overview Metrics:**
   - AI Analysis: `Available`
   - Similar Found: `3`
   - Highest Similarity: `~82%`
   - Dataset Records: `18`
2. **AI Analysis:** Generated text structured under Incident Type, Severity, Location, Summary, and Risk Indicators.
3. **Matched Severity Breakdown:** Count of High, Medium, Low severity matches (e.g., 🔴 High: 3).
4. **Similar Incidents:** Top 3 matching cards (e.g., Incident #4 Stalking at Railway Station, Incident #7 Stalking at Residential Street, Incident #16 Stalking at Underground Parking).

---

## Limitations
- **Small LLM:** DistilGPT-2 is an 82M parameter model; generated output may be repetitive or lose context.
- **No Factual Verification:** AI responses are speculative text completions and not verified facts.
- **Semantic vs Real Matching:** Similarity scores measure linguistic/semantic closeness, not evidence that events are physically connected.
- **Sample Dataset:** Uses 18 fictional records in a local JSON file.
- **Not for Emergency Use:** Educational demonstration project only.

---

## Future Improvements (Out of Workshop Scope)
The following are possible future enhancements that are **NOT** part of the current workshop implementation:
- Upgrading to a larger instruction-tuned LLM (e.g., Llama 3 or Mistral).
- Expanding to a real-world database (e.g., PostgreSQL).
- Integrating vector databases (e.g., Pinecone or Chroma) for millions of records.
- Implementing retrieval-augmented generation (RAG) to feed matching dataset context back into the LLM prompt.
- Adding user authentication and role-based access control.
- Deploying to cloud infrastructure (e.g., AWS / Docker).

---

## How I Would Explain IncidentIQ to My Instructor
> *"IncidentIQ is a simple GenAI application that analyzes incident reports and finds similar historical incidents. In Days 1–3, I used DistilGPT-2 from Hugging Face with prompt engineering to summarize incident text in a Streamlit web interface. In Day 4, I added semantic similarity using Sentence Transformers (`all-MiniLM-L6-v2`) and scikit-learn. When a user enters an incident, the app converts the text into a 384-dimensional vector embedding and compares it against precomputed embeddings in `incidents.json` using cosine similarity. On Day 5, I built a presentation-ready dashboard with dynamic metrics, severity breakdown, error handling, reset functionality, and pipeline explanations."*

---

## Questions My Instructor May Ask

### Q1: What is GenAI?
**Answer:** Generative AI refers to machine learning models that can generate new content—such as text, images, or code—by learning statistical patterns from training data.

### Q2: What is an LLM?
**Answer:** A Large Language Model is a deep learning model trained on massive amounts of text to understand, predict, and generate human language.

### Q3: What is DistilGPT-2?
**Answer:** DistilGPT-2 is a lightweight, distilled version of OpenAI's GPT-2 model with 82 million parameters that runs locally on CPU without paid APIs.

### Q4: What is a Transformer?
**Answer:** A Transformer is a neural network architecture that uses self-attention mechanisms to process text tokens in parallel and capture contextual relationships.

### Q5: What is Hugging Face?
**Answer:** Hugging Face is an open-source platform providing pre-trained models and the `transformers` library to easily run AI models in Python.

### Q6: What is prompt engineering?
**Answer:** Prompt engineering is the practice of structuring input text to guide an LLM to produce desired, formatted outputs.

### Q7: What is an embedding?
**Answer:** An embedding is a numerical vector (a list of numbers) that represents the semantic meaning of text in a multi-dimensional space.

### Q8: Why do we need embeddings?
**Answer:** Computers cannot compare sentence meanings using text characters alone. Embeddings allow us to perform mathematical calculations (like cosine similarity) to find similar meanings even if different words are used.

### Q9: What is cosine similarity?
**Answer:** Cosine similarity is a mathematical formula that calculates the cosine of the angle between two vectors, producing a score from 0.0 (unrelated) to 1.0 (identical).

### Q10: Why are we using `all-MiniLM-L6-v2`?
**Answer:** It is a fast, lightweight Sentence Transformer model that converts sentences into 384-dimensional embeddings efficiently on a CPU.

### Q11: Is `incidents.json` training the LLM?
**Answer:** No. `incidents.json` is a local dataset used strictly for similarity searching at runtime. DistilGPT-2 is not trained or fine-tuned on it.

### Q12: What is the difference between an LLM and an embedding model?
**Answer:** An LLM generates new text word-by-word, while an embedding model converts text into numerical vectors for search and comparison.

### Q13: Why can DistilGPT-2 produce repetitive output?
**Answer:** Because DistilGPT-2 is a small model (82M parameters) without instruction fine-tuning, so its text generation can loop or lose coherence on complex prompts.

### Q14: What happens when the user enters a new incident?
**Answer:** The text goes through two paths: DistilGPT-2 generates an AI analysis, and `all-MiniLM-L6-v2` converts it into a vector to calculate cosine similarity against stored incident vectors.

### Q15: What are the limitations of this project?
**Answer:** It uses a small text model, sample dataset, does not verify facts, and is designed as an educational workshop project rather than a production system.
