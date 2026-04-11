import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os
import sys
import tempfile

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt.whisper_stt import load_whisper_model, transcribe_audio
from nlp.grammar import evaluate_grammar, correct_grammar

# Page Configuration
st.set_page_config(
    page_title="AI English Evaluator",
    page_icon="🎙️",
    layout="centered"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4F8BF9;
        color: white;
        font-weight: bold;
    }
    .score-box {
        background-color: #1e222d;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #4F8BF9;
        margin-bottom: 20px;
    }
    .result-text {
        font-size: 1.2rem;
        margin-bottom: 5px;
    }
    .highlight {
        color: #4F8BF9;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title and Header
st.title("🎙️ AI English Evaluator")
st.markdown("Speak into the microphone to evaluate your English grammar and pronunciation.")

# Load Models
@st.cache_resource
def get_models():
    model = load_whisper_model("base")
    return model

model = get_models()

# Sidebar for history or settings
with st.sidebar:
    st.header("Settings")
    st.info("Using Whisper 'Base' model and LanguageTool for high-speed evaluation.")
    if st.button("Clear Cache"):
        st.cache_resource.clear()
        st.rerun()

# Recording Session
st.subheader("Step 1: Record your voice")
audio_bytes = audio_recorder(
    text="Click to Record",
    recording_color="#e74c3c",
    neutral_color="#4F8BF9",
    icon_name="microphone",
    icon_size="3x"
)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    if st.button("Evaluate My English"):
        with st.spinner("Analyzing your speech..."):
            # Save audio to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name

            try:
                # 1. Transcribe
                transcription = transcribe_audio(model, temp_path)
                
                if transcription and transcription["text"].strip():
                    text = transcription["text"].strip()
                    
                    # 2. Grammar Check
                    grammar_result = evaluate_grammar(text)
                    corrected = correct_grammar(text)
                    
                    # 3. Display Results
                    st.success("Analysis Complete!")
                    
                    # Score Display
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric("Grammar Score", f"{grammar_result['score']}/10")
                    
                    st.markdown("---")
                    
                    # Text Comparison
                    st.markdown(f"<div class='score-box'><div class='result-text'><b>What you said:</b></div><div>\"{text}\"</div></div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='score-box'><div class='result-text'><b>Recommended version:</b></div><div><span class='highlight'>\"{corrected}\"</span></div></div>", unsafe_allow_html=True)
                    
                    # Errors list
                    if grammar_result["errors"]:
                        with st.expander("Show detailed corrections"):
                            for error in grammar_result["errors"]:
                                st.write(f"- {error}")
                    else:
                        st.balloons()
                        st.info("Excellent! Your grammar is perfect.")
                    
                else:
                    st.error("Could not understand the audio. Please speak clearly and try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
            
            finally:
                # Cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)

else:
    st.info("Waiting for recording... Click the microphone above to start.")

# Footer
st.markdown("---")
st.caption("AI English Evaluator | Powered by Whisper & LanguageTool")
