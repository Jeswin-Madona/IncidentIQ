# ==============================================================================
# IncidentIQ - Day 5: Presentation-Ready GenAI Incident Intelligence Dashboard
# ==============================================================================
# This file builds the full web interface for IncidentIQ. It integrates:
# 1. LLM Incident Analysis (DistilGPT-2 via llm.py)
# 2. Semantic Similarity Search (SentenceTransformer embeddings + cosine similarity)
# 3. Dynamic Overview Dashboard & Severity Breakdown Metrics
# 4. Educational Expanders: Pipeline Architecture, Tech Stack, & Limitations
# 5. Interactive Reset / Clear controls and robust error handling
# ==============================================================================

import json
import os
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Import the incident analysis function from our core llm.py engine
from llm import analyze_incident

# ------------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & HEADER
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="IncidentIQ - AI Incident Intelligence",
    page_icon="🛡️",
    layout="centered"
)

st.title("IncidentIQ")
st.subheader("AI-Powered Incident Intelligence & Summarization")
st.markdown("Analyze incident reports using generative AI and discover similar incidents using semantic similarity.")
st.markdown("---")

# ------------------------------------------------------------------------------
# 2. CACHED DATASET & EMBEDDING MODEL LOADERS
# ------------------------------------------------------------------------------

@st.cache_resource
def load_embedding_model():
    """
    Loads all-MiniLM-L6-v2 model which converts text sentences into 384-dimensional
    numerical vectors (embeddings) capturing semantic meaning.
    """
    print("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
    return SentenceTransformer("all-MiniLM-L6-v2")


@st.cache_data
def load_dataset(json_filepath="incidents.json"):
    """
    Reads historical incident records from the local JSON dataset.
    Includes basic error handling for missing files or invalid JSON.
    """
    if not os.path.exists(json_filepath):
        st.error(f"Dataset Error: '{json_filepath}' was not found. Please ensure the file exists in the project directory.")
        return []
    
    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        st.error(f"Dataset Parsing Error: '{json_filepath}' contains invalid JSON formatting.")
        return []
    except Exception as e:
        st.error(f"Dataset Loading Error: {str(e)}")
        return []


@st.cache_data
def compute_dataset_embeddings(_model, dataset):
    """
    Converts all historical incident text records into numerical vectors.
    Returns a list of embedding vectors corresponding to each dataset record.
    """
    if not dataset:
        return []
    incident_texts = [item["incident"] for item in dataset]
    embeddings = _model.encode(incident_texts)
    return embeddings


# Initialize models and dataset
embedding_model = load_embedding_model()
dataset_records = load_dataset("incidents.json")
dataset_embeddings = compute_dataset_embeddings(embedding_model, dataset_records)


# ------------------------------------------------------------------------------
# 3. USER INPUT SECTION & ACTION BUTTONS
# ------------------------------------------------------------------------------
st.markdown("### Incident Report")

# Initialize text area key state if needed
if "incident_input_key" not in st.session_state:
    st.session_state["incident_input_key"] = ""

incident_input = st.text_area(
    label="Enter Incident Description",
    placeholder="Yesterday at around 8 PM, I was walking near the railway station when a man started following me. I entered a nearby shop and waited until he left.",
    height=140,
    key="incident_input_key"
)

col_btn1, col_btn2 = st.columns([3, 1])

with col_btn1:
    analyze_clicked = st.button("Analyze Incident", type="primary", use_container_width=True)

with col_btn2:
    clear_clicked = st.button("Clear / New Analysis", use_container_width=True)

if clear_clicked:
    st.session_state["incident_input_key"] = ""
    st.rerun()

# ------------------------------------------------------------------------------
# 4. ACTION WORKFLOW & DASHBOARD GENERATION
# ------------------------------------------------------------------------------
if analyze_clicked:
    # --- STEP 11: INPUT VALIDATION ---
    if not incident_input.strip():
        st.warning("Please enter an incident description.")
    else:
        # --- TRACK 1: LLM GENERATIVE ANALYSIS ---
        analysis_result = None
        with st.spinner("Analyzing incident with AI model (DistilGPT-2)..."):
            try:
                analysis_result = analyze_incident(incident_input)
            except Exception as e:
                st.error(f"AI Analysis Error: Unable to generate response. Details: {str(e)}")

        # --- TRACK 2: SEMANTIC SIMILARITY SEARCH ---
        top_matches = []
        highest_similarity_pct = 0

        with st.spinner("Searching dataset for similar incidents using embeddings..."):
            try:
                if dataset_records and len(dataset_embeddings) > 0:
                    user_embedding = embedding_model.encode([incident_input])
                    similarity_scores = cosine_similarity(user_embedding, dataset_embeddings)[0]

                    scored_incidents = []
                    for index, item in enumerate(dataset_records):
                        score = float(similarity_scores[index])
                        scored_incidents.append({
                            "record": item,
                            "score": score
                        })

                    scored_incidents.sort(key=lambda x: x["score"], reverse=True)

                    SIMILARITY_THRESHOLD = 0.40
                    top_matches = [
                        item for item in scored_incidents 
                        if item["score"] >= SIMILARITY_THRESHOLD
                    ][:3]

                    if top_matches:
                        highest_similarity_pct = int(round(top_matches[0]["score"] * 100))
                else:
                    st.warning("Dataset is empty or could not be loaded for similarity search.")
            except Exception as e:
                st.error(f"Similarity Search Error: {str(e)}")

        # ----------------------------------------------------------------------
        # STEP 3: DASHBOARD SUMMARY (DYNAMIC METRICS)
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### Analysis Overview")
        
        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        d_col1.metric("AI Analysis", "Available" if analysis_result else "Unavailable")
        d_col2.metric("Similar Found", len(top_matches))
        d_col3.metric("Highest Similarity", f"{highest_similarity_pct}%" if top_matches else "0%")
        d_col4.metric("Dataset Records", len(dataset_records))

        # ----------------------------------------------------------------------
        # STEP 4: AI ANALYSIS OUTPUT
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### AI Analysis")
        st.caption("ℹ️ Note: This response is generated by DistilGPT-2 for demonstration purposes and is not factually verified.")
        if analysis_result:
            st.info(analysis_result)
        else:
            st.error("AI Analysis could not be completed.")

        # ----------------------------------------------------------------------
        # STEP 5 & STEP 6: SIMILAR INCIDENTS & SEVERITY SUMMARY
        # ----------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### Similar Incidents")

        if top_matches:
            # Step 6: Simple Severity Breakdown of returned matches
            high_count = sum(1 for m in top_matches if str(m["record"].get("severity", "")).lower() == "high")
            med_count = sum(1 for m in top_matches if str(m["record"].get("severity", "")).lower() == "medium")
            low_count = sum(1 for m in top_matches if str(m["record"].get("severity", "")).lower() == "low")

            st.markdown("**Matched Severity Breakdown:**")
            sev_col1, sev_col2, sev_col3 = st.columns(3)
            sev_col1.markdown(f"🔴 **High:** {high_count}")
            sev_col2.markdown(f"🟡 **Medium:** {med_count}")
            sev_col3.markdown(f"🟢 **Low:** {low_count}")
            st.markdown("")

            for match in top_matches:
                rec = match["record"]
                score_pct = int(round(match["score"] * 100))

                with st.expander(f"Incident #{rec['id']} — Match: {score_pct}%", expanded=True):
                    st.write(f"**Incident:** {rec['incident']}")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Similarity", f"{score_pct}%")
                    col2.metric("Type", rec.get("type", "N/A"))
                    col3.metric("Severity", rec.get("severity", "N/A"))
                    st.caption(f"📍 Location: {rec.get('location', 'N/A')}")
        else:
            st.info("No strongly similar incidents found (similarity threshold > 40%).")

# ------------------------------------------------------------------------------
# 5. EXPANDABLE INFORMATIONAL SECTIONS (STEPS 7, 8, 9)
# ------------------------------------------------------------------------------
st.markdown("---")

with st.expander("❓ How IncidentIQ Works"):
    st.markdown("""
    1. **User enters an incident report.**
    2. **The incident is sent to the DistilGPT-2 language model.**
    3. **The model generates an AI-based analysis.**
    4. **The incident is converted into an embedding using `all-MiniLM-L6-v2`.**
    5. **The embedding is compared with stored incident embeddings.**
    6. **Cosine similarity measures how similar the incidents are.**
    7. **The application displays the most similar incidents.**
    """)

with st.expander("🛠️ Technologies Used"):
    st.markdown("""
    - **Python** → Main programming language.
    - **Streamlit** → Used to create the web interface.
    - **Hugging Face Transformers** → Enables loading and executing AI language models.
    - **PyTorch** → Deep learning framework running model operations behind the scenes.
    - **DistilGPT-2** → Used for text generation and AI analysis.
    - **Sentence Transformers** → Converts incident text into numerical embeddings.
    - **all-MiniLM-L6-v2** → Sentence transformer model mapping text into a 384-dimensional vector space.
    - **scikit-learn** → Calculates cosine similarity between vector embeddings.
    - **JSON dataset (`incidents.json`)** → Local dataset containing historical incident records for similarity comparison.
    """)

with st.expander("⚠️ Limitations"):
    st.markdown("""
    - DistilGPT-2 is a small text-generation model.
    - Generated responses may sometimes be repetitive or inaccurate.
    - Similarity scores indicate semantic similarity, not factual verification.
    - The dataset contains sample incidents.
    - The system does not verify whether an incident actually occurred.
    - This is an educational GenAI project and not an emergency-response system.
    """)
