import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os
import sys
import tempfile

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt.whisper_stt import load_whisper_model, transcribe_audio
from nlp.grammar import evaluate_grammar, correct_grammar
from nlp.vocabulary import analyze_vocabulary
from nlp.archetype import determine_archetype
from scoring.fluency import calculate_fluency
from utils.question_generator import generate_questions

# Page Configuration
st.set_page_config(
    page_title="AI English Evaluator",
    page_icon="🎙️",
    layout="wide"
)

# Initialize Session State
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "responses" not in st.session_state:
    st.session_state.responses = []
if "evals" not in st.session_state:
    st.session_state.evals = []
if "questions" not in st.session_state:
    st.session_state.questions = []

TOTAL_QUESTIONS = 3

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
    .metric-card {
        background-color: #1e222d;
        padding: 20px;
        border-radius: 15px;
        border-top: 4px solid #4F8BF9;
        text-align: center;
    }
    .archetype-card {
        background: linear-gradient(135deg, #4F8BF9 0%, #2ecc71 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
        text-align: center;
    }
    .score-box {
        background-color: #1e222d;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #4F8BF9;
        margin-bottom: 20px;
    }
    .result-text {
        font-size: 1.1rem;
        margin-bottom: 5px;
        color: #8892b0;
    }
    .highlight {
        color: #4F8BF9;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .progress-text {
        color: #4F8BF9;
        font-weight: bold;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Title and Header
st.title("🎙️ AI English Personality Evaluator")

# Load Models
@st.cache_resource
def get_models():
    model = load_whisper_model("base")
    return model

model = get_models()

# Sidebar
with st.sidebar:
    st.header("Session Control")
    if st.button("Reset Session"):
        st.session_state.session_active = False
        st.session_state.current_q_index = 0
        st.session_state.responses = []
        st.session_state.evals = []
        st.session_state.questions = []
        st.rerun()
    
    st.divider()
    st.info(f"Goal: Answer {TOTAL_QUESTIONS} questions to discover your English Archetype.")

# Logic: Start Screen
if not st.session_state.session_active:
    st.markdown("""
    ### Welcome to the Archetype Assessment
    We will ask you 3 conversational questions. Based on your vocabulary, grammar, and fluency across all answers, 
    our AI will determine your unique **English Speaking Archetype**.
    """)
    if st.button("🚀 Start Interview Session"):
        st.session_state.session_active = True
        with st.spinner("Preparing interesting topics..."):
            st.session_state.questions = generate_questions(count=TOTAL_QUESTIONS, level="intermediate")
        st.rerun()

# Logic: Interview Phase
elif st.session_state.current_q_index < TOTAL_QUESTIONS:
    q_idx = st.session_state.current_q_index
    current_q = st.session_state.questions[q_idx]
    
    st.markdown(f"<div class='progress-text'>Question {q_idx + 1} of {TOTAL_QUESTIONS}</div>", unsafe_allow_html=True)
    st.progress((q_idx) / TOTAL_QUESTIONS)
    
    st.markdown(f"""
    <div style="background-color: #1e222d; padding: 25px; border-radius: 15px; border: 1px solid #4F8BF9; margin-bottom: 25px;">
        <h3 style="margin-top: 0; color: #4F8BF9;">Topic:</h3>
        <p style="font-size: 1.5rem; font-weight: 500;">{current_q}</p>
    </div>
    """, unsafe_allow_html=True)

    audio_bytes = audio_recorder(
        text="Click to Answer",
        recording_color="#e74c3c",
        neutral_color="#4F8BF9",
        icon_name="microphone",
        icon_size="3x"
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        if st.button("Submit Answer"):
            with st.spinner("Processing..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                    temp_audio.write(audio_bytes)
                    temp_path = temp_audio.name
                
                try:
                    transcription = transcribe_audio(model, temp_path)
                    if transcription and transcription["text"].strip():
                        text = transcription["text"].strip()
                        
                        # Evaluate individual answer
                        grammar_result = evaluate_grammar(text)
                        vocab_result = analyze_vocabulary(text)
                        fluency_result = calculate_fluency(transcription)
                        
                        # Store in session
                        st.session_state.responses.append(text)
                        st.session_state.evals.append({
                            "grammar": grammar_result,
                            "vocab": vocab_result,
                            "fluency": fluency_result
                        })
                        
                        # Move to next
                        st.session_state.current_q_index += 1
                        st.rerun()
                    else:
                        st.error("Could not hear you. Please try again.")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
    else:
        # Guidance for the 20-second timer
        st.markdown("<p style='color: #4F8BF9; font-weight: bold;'>⏱️ Speaking Guide: 20 Seconds</p>", unsafe_allow_html=True)
        st.info("Tip: Aim to speak for at least 20 seconds to give the AI enough material for a deep analysis!")

# Logic: Results Phase
else:
    st.balloons()
    with st.spinner("Analyzing your profile..."):
        archetype_data = determine_archetype(st.session_state.responses)
    
    st.markdown(f"""
    <div class="archetype-card">
        <h1 style="margin:0;">{archetype_data['archetype']}</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">Your English Speaking Archetype</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Profile Description")
        st.write(archetype_data['description'])
        
        st.subheader("Key Strengths")
        strengths = archetype_data.get('strengths', [])
        if isinstance(strengths, list):
            for strength in strengths:
                st.success(f"✔️ {strength}")
        else:
            st.success(f"✔️ {strengths}")
            
        st.subheader("Focus Area for Growth")
        st.info(f"🚀 {archetype_data.get('growth_area', 'Keep practicing!')}")

    with col2:
        # Aggregated Metrics
        avg_grammar = sum([e['grammar']['score'] for e in st.session_state.evals]) / TOTAL_QUESTIONS
        avg_wpm = sum([e['fluency']['wpm'] for e in st.session_state.evals]) / TOTAL_QUESTIONS
        
        st.markdown(f"<div class='metric-card'><div class='result-text'>Avg. Grammar</div><div class='highlight'>{avg_grammar:.1f}/10</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div class='metric-card'><div class='result-text'>Avg. Fluency</div><div class='highlight'>{int(avg_wpm)} WPM</div></div>", unsafe_allow_html=True)

    st.divider()
    with st.expander("View Full Interview Transcript"):
        for i, (q, r) in enumerate(zip(st.session_state.questions, st.session_state.responses)):
            st.markdown(f"**Q{i+1}:** {q}")
            st.markdown(f"*Your Answer:* {r}")
            st.markdown("---")

# Footer
st.markdown("---")
st.caption("AI English Evaluator | Archetype Assessment Powered by Gemini-Flash")
