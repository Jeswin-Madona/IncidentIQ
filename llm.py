# ==============================================================================
# IncidentIQ - Day 2 & Day 3: AI Incident Analyzer Core Engine
# ==============================================================================
# This script contains the core Generative AI logic for IncidentIQ using 
# Hugging Face Transformers and DistilGPT-2.
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORT HUGGING FACE PIPELINE
# ------------------------------------------------------------------------------
# pipeline() is a high-level helper function provided by the Hugging Face 
# transformers library. It abstracts away complex steps like tokenization,
# model loading, tensor processing, and output decoding into a single clean call.
from transformers import pipeline

# ------------------------------------------------------------------------------
# 2. INITIALIZE THE TEXT-GENERATION PIPELINE WITH STREAMLIT CACHING
# ------------------------------------------------------------------------------
# In Streamlit, app.py re-runs from top to bottom on every user interaction.
# Using @st.cache_resource ensures the model is loaded into memory only ONCE 
# when the application starts, rather than reloading on every button click.

def get_generator():
    try:
        import streamlit as st
        @st.cache_resource
        def _load_model():
            print("Loading distilgpt2 model into Streamlit cache...")
            return pipeline("text-generation", model="distilgpt2")
        return _load_model()
    except Exception:
        # Fallback for standalone CLI execution (python llm.py)
        print("Loading distilgpt2 model...")
        return pipeline("text-generation", model="distilgpt2")

generator = get_generator()
print("Model loaded successfully!\n")


# ------------------------------------------------------------------------------
# 3. DEFINE THE INCIDENT ANALYSIS FUNCTION
# ------------------------------------------------------------------------------
def analyze_incident(incident):
    """
    Receives a natural language incident description, constructs a structured 
    prompt, calls the LLM, and returns the generated analysis.
    """
    
    # --- INPUT VALIDATION ---
    # We must ensure the user provided a non-empty string before calling the model.
    # Passing empty or whitespace-only text wastes compute and can cause model errors.
    if not incident or not incident.strip():
        print("Validation Error: Please provide a valid, non-empty incident report.")
        return None

    # --- PROMPT CONSTRUCTION ---
    # A prompt is the text instruction given to an LLM to guide its output.
    # By providing structure in the prompt, we encourage the model to follow
    # a specific format (Incident Type, Severity, Location, Time, Summary, Risk Indicators).
    prompt = (
        f"Incident Report: {incident.strip()}\n\n"
        f"Analyze the incident above and provide details in the following format:\n"
        f"Incident Type:\n"
        f"Severity:\n"
        f"Location:\n"
        f"Time:\n"
        f"Summary:\n"
        f"Key Risk Indicators:\n"
    )

    # --- MODEL INFERENCE / TEXT GENERATION ---
    # generator() takes the prompt string and sends it through the LLM.
    # Parameters used:
    # - prompt: The input string containing instructions and context.
    # - max_new_tokens=100: Limits the maximum number of new words/tokens the model 
    #   is allowed to generate. This prevents unnecessarily large or infinite responses.
    # - do_sample=True: Enables probabilistic sampling so generation is creative.
    # - temperature=0.7: Controls randomness (lower values make output more deterministic).
    # - pad_token_id=50256: Handles sequence padding for clean generation.
    result = generator(
        prompt,
        max_new_tokens=100,
        do_sample=True,
        temperature=0.7,
        pad_token_id=50256
    )

    # --- UNDERSTANDING THE MODEL OUTPUT ---
    # Hugging Face pipeline returns a list of dictionaries containing generated text.
    # Structure of result:
    # [
    #   {
    #     "generated_text": "Incident Report: ... (the prompt + generated text)"
    #   }
    # ]
    #
    # Why result[0]["generated_text"] is used:
    # 1. result[0]: Accesses the first generated sequence dictionary in the list.
    # 2. ["generated_text"]: Extracts the string containing the combined prompt and completion.
    generated_text = result[0]["generated_text"]
    
    return generated_text


# ------------------------------------------------------------------------------
# 4. MAIN EXECUTION & TESTING (FOR CLI MODE)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("==================================================")
    print("          INCIDENTIQ - AI INCIDENT ANALYZER       ")
    print("==================================================\n")

    # Sample incident input
    sample_incident = (
        "Yesterday at around 8 PM, I was walking near the railway station "
        "when a man started following me. I entered a nearby shop and waited until he left."
    )

    print("--- INPUT INCIDENT REPORT ---")
    print(sample_incident)
    print("\n--- ANALYZING INCIDENT WITH DISTILGPT2 ---")
    
    # Call the incident analysis function
    analysis_output = analyze_incident(sample_incident)
    
    if analysis_output:
        print("\n--- GENERATED MODEL OUTPUT ---")
        print(analysis_output)
    
    print("\n==================================================")
    print("Test completed. Note: Output accuracy depends on model capability.")