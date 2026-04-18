import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os
import sys
import tempfile
from dotenv import load_dotenv

# Load .env file — ensures GEMINI_API_KEY is always available
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"), override=True)

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stt.whisper_stt import load_whisper_model, transcribe_audio
from nlp.grammar import evaluate_grammar, correct_grammar
from nlp.vocabulary import analyze_vocabulary
from nlp.archetype import determine_archetype
from scoring.fluency import calculate_fluency
from nlp.enhancer import enhance_speech
from utils.question_generator import generate_questions
from utils.image_task import get_image_task
from utils.dashboard_plots import create_wpm_gauge, create_fluency_line_chart, create_vocabulary_sack

# Page Configuration
st.set_page_config(
    page_title="AI English Evaluator",
    page_icon="🎙️",
    layout="wide"
)

# Initialize Session State
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Interview Session"
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
if "image_task" not in st.session_state:
    st.session_state.image_task = None

TOTAL_QUESTIONS = 4

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
    .image-container {
        border: 2px solid #4F8BF9;
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title and Header
st.title("🎙️ AI English Evaluator")

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
        st.session_state.image_task = None
        st.rerun()
    
    st.divider()
    st.info(f"Goal: Answer {TOTAL_QUESTIONS} questions (including 1 Image Task) to discover your English Archetype.")

# --- INTERVIEW SESSION MODE ---
if st.session_state.app_mode == "Interview Session":
    # Logic: Start Screen
    if not st.session_state.session_active:
        st.markdown("""
        ### Welcome to the Archetype Assessment
        We will ask you 3 conversational questions followed by a **final Image Description challenge**. 
        Based on your vocabulary, grammar, and fluency across all 4 answers, our AI will determine your unique **English Speaking Archetype**.
        """)
        if st.button("🚀 Start Interview Session"):
            st.session_state.session_active = True
            with st.spinner("Preparing interesting topics..."):
                # Generate 3 conversational questions
                st.session_state.questions = generate_questions(count=3, level="intermediate")
                # Add a placeholder for the 4th (Image) task
                st.session_state.questions.append("Image Description Task")
                st.session_state.image_task = get_image_task()
            st.rerun()

    # Logic: Interview Phase
    elif st.session_state.current_q_index < TOTAL_QUESTIONS:
        q_idx = st.session_state.current_q_index
        current_q = st.session_state.questions[q_idx]
        
        st.markdown(f"<div class='progress-text'>Step {q_idx + 1} of {TOTAL_QUESTIONS}</div>", unsafe_allow_html=True)
        st.progress((q_idx) / TOTAL_QUESTIONS)
        
        # Check if this is the final Image task
        if q_idx == 3:
            task = st.session_state.image_task
            st.markdown(f"""
            <div style="background-color: #1e222d; padding: 25px; border-radius: 15px; border: 1px solid #4F8BF9; margin-bottom: 25px;">
                <h3 style="margin-top: 0; color: #4F8BF9;">Final Challenge: Image Description</h3>
                <p style="font-size: 1.2rem; font-weight: 500;">{task['instruction']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if os.path.exists(task['image_path']):
                st.image(task['image_path'], use_column_width=True)
            
            instruction_for_ai = f"Image description task. Instruction: {task['instruction']}. Scene details: {task['prompt_for_ai']}"
        else:
            current_q = st.session_state.questions[q_idx]
            st.markdown(f"""
            <div style="background-color: #1e222d; padding: 25px; border-radius: 15px; border: 1px solid #4F8BF9; margin-bottom: 25px;">
                <h3 style="margin-top: 0; color: #4F8BF9;">Topic:</h3>
                <p style="font-size: 1.5rem; font-weight: 500;">{current_q}</p>
            </div>
            """, unsafe_allow_html=True)
            instruction_for_ai = current_q

        audio_bytes = audio_recorder(
            text="Click to Answer",
            recording_color="#e74c3c",
            neutral_color="#4F8BF9",
            icon_name="microphone",
            icon_size="3x",
            pause_threshold=20.0,
            key=f"recorder_{q_idx}"
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
                            polished_text = enhance_speech(text, question=instruction_for_ai)
                            
                            # Store in session
                            st.session_state.responses.append(text)
                            st.session_state.evals.append({
                                "grammar": grammar_result,
                                "vocab": vocab_result,
                                "fluency": fluency_result,
                                "polished": polished_text
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
            <p style="font-size: 1.2rem; opacity: 0.9;">Your Comprehensive Speech Analysis</p>
        </div>
        """, unsafe_allow_html=True)

        # Dashboard Metrics Row
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        
        with col1:
            st.subheader("Profile Description")
            st.write(archetype_data['description'])
            st.info(f"🚀 **Growth Area:** {archetype_data.get('growth_area', 'Keep practicing!')}")
            
            # Word Sack Visualization
            all_text = " ".join(st.session_state.responses)
            word_count = len(all_text.split())
            unique_words = len(set(all_text.lower().split()))
            st.plotly_chart(create_vocabulary_sack(word_count, unique_words), use_container_width=True)

        with col2:
            # WPM Speedometer
            avg_wpm = sum([e['fluency']['wpm'] for e in st.session_state.evals]) / TOTAL_QUESTIONS
            st.plotly_chart(create_wpm_gauge(avg_wpm), use_container_width=True)
            
            # Aggregated Speech Flow Data
            combined_timeline = []
            offset = 0
            for e in st.session_state.evals:
                for point in e['fluency']['timeline']:
                    combined_timeline.append({"time": point['time'] + offset, "wpm": point['wpm']})
                offset += e['fluency']['duration_sec'] + 2 # Add artificial pause between questions
                
            st.plotly_chart(create_fluency_line_chart(combined_timeline), use_container_width=True)

        with col3:
            st.subheader("Speech Performance")
            
            # Calculate Blanks and Fillers
            total_blanks = sum([e['fluency']['blank_spots'] for e in st.session_state.evals])
            total_fillers = sum([e['fluency']['filler_count'] for e in st.session_state.evals])
            avg_grammar = sum([e['grammar']['score'] for e in st.session_state.evals]) / TOTAL_QUESTIONS

            st.markdown(f"""
            <div class='metric-card'>
                <div class='result-text'>Grammar Accuracy</div>
                <div class='highlight'>{avg_grammar:.1f}/10</div>
            </div>
            <div style='margin-bottom: 15px;'></div>
            <div class='metric-card' style='border-top-color: #e74c3c;'>
                <div class='result-text'>Silence Blanks</div>
                <div class='highlight'>{total_blanks}</div>
                <small style='color: #8892b0;'>Significant pauses detected</small>
            </div>
            <div style='margin-bottom: 15px;'></div>
            <div class='metric-card' style='border-top-color: #f1c40f;'>
                <div class='result-text'>Speech Flutters</div>
                <div class='highlight'>{total_fillers}</div>
                <small style='color: #8892b0;'>Filler words (um, ah, like)</small>
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        with st.expander("📋 View Full Session Coaching & Corrections"):
            for i, (q, r) in enumerate(zip(st.session_state.questions, st.session_state.responses)):
                st.markdown(f"**Q{i+1}:** {q}")
                st.markdown(f"🗣️ **Your Answer:** {r}")

                # Show structured enhancement if available
                if i < len(st.session_state.evals):
                    enhancement = st.session_state.evals[i].get("polished", {})
                    if isinstance(enhancement, dict):
                        # --- Mistakes ---
                        mistakes = enhancement.get("mistakes", [])
                        if mistakes:
                            mistakes_html = "".join([f"<li>{m}</li>" for m in mistakes])
                            st.markdown(f"""
                            <div style="background-color: #3b1c1c; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 4px solid #e74c3c;">
                                <p style="margin: 0 0 8px 0; font-weight: bold; color: #e74c3c;">❌ Mistakes Found:</p>
                                <ul style="margin: 0; padding-left: 20px; color: #f5a5a5;">{mistakes_html}</ul>
                            </div>
                            """, unsafe_allow_html=True)

                        # --- Relevancy Feedback ---
                        relevancy = enhancement.get("relevancy", "")
                        if relevancy:
                            relevancy_color = "#2ecc71" if "excellent" in relevancy.lower() or "relevant" in relevancy.lower() else "#e67e22"
                            st.markdown(f"""
                            <div style="background-color: #1a1f2e; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 4px solid {relevancy_color};">
                                <p style="margin: 0 0 8px 0; font-weight: bold; color: {relevancy_color};">🎯 Topic Relevancy:</p>
                                <p style="margin: 0; color: #dcdde1; font-style: italic;">{relevancy}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        # --- Vocabulary Suggestions ---
                        vocab = st.session_state.evals[i].get("vocab", {})
                        suggestions = vocab.get("suggestions", [])
                        if suggestions:
                            vocab_html = "".join([f"<li><b>'{s['original']}'</b> → <b>'{s['improved']}'</b><br><small>Sentence: {s.get('improved_sentence', 'N/A')}</small></li>" for s in suggestions])
                            st.markdown(f"""
                            <div style="background-color: #1a1f2e; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 4px solid #f1c40f;">
                                <p style="margin: 0 0 8px 0; font-weight: bold; color: #f1c40f;">💡 Vocabulary Upgrades:</p>
                                <ul style="margin: 0; padding-left: 20px; color: #dcdde1; list-style-type: none;">{vocab_html}</ul>
                            </div>
                            """, unsafe_allow_html=True)

                        # --- Improved Version ---
                        improved = enhancement.get("improved", "")
                        if improved and improved != r:
                            st.markdown(f"""
                            <div style="background-color: #0e4b25; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 4px solid #2ecc71;">
                                <p style="margin: 0 0 8px 0; font-weight: bold; color: #2ecc71;">🏆 10/10 Professional Version:</p>
                                <p style="margin: 0; font-style: italic; font-size: 1.05rem;">{improved}</p>
                            </div>
                            """, unsafe_allow_html=True)

                        # --- Score ---
                        score = enhancement.get("score", "N/A")
                        st.markdown(f"""
                        <div style="background-color: #1a1f2e; padding: 10px 15px; border-radius: 10px; margin-top: 10px; border-left: 4px solid #4F8BF9; display: inline-block;">
                            <span style="color: #8892b0;">AI Speech Score for this answer: </span>
                            <span style="color: #4F8BF9; font-weight: bold; font-size: 1.1rem;">{score}/10</span>
                        </div>
                        """, unsafe_allow_html=True)

                    elif isinstance(enhancement, str) and enhancement:
                        # Fallback for old plain-string format
                        st.markdown(f"""
                        <div style="background-color: #0e4b25; padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 4px solid #2ecc71;">
                            <p style="margin: 0; font-weight: bold; color: #2ecc71;">🏆 10/10 Professional Version:</p>
                            <p style="margin: 5px 0 0 0; font-style: italic;">{enhancement}</p>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")



# Footer
st.markdown("---")
st.caption("AI English Evaluator | Archetype Assessment Powered by Gemini-Flash")
