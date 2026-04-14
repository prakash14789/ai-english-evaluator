# AI English Evaluator — Project Brief

## 👤 Author

Prakash Mishra
GitHub: https://github.com/prakash14789/ai-english-evaluator

---

## 📌 Project Overview

This project aims to build an **AI-powered spoken English evaluation system**.
The system takes user speech as input, analyzes it for grammar and fluency, assigns a score (0–10), and provides learning feedback over a 7-day improvement cycle.

---

## 🎯 Current Progress (Completed)

### ✅ 1. Project Setup

* Created structured repository
* Initialized Git and pushed to GitHub
* Set up virtual environment (venv)
* Installed required libraries

### ✅ 2. Folder Structure

```
ai-english-evaluator/
│
├── src/
│   ├── stt/         # Speech-to-text module
│   ├── nlp/         # Grammar analysis (in progress)
│   ├── scoring/     # Scoring logic (planned)
│   ├── utils/
│
├── api/             # Backend (planned)
├── data/            # Datasets (ignored in git)
├── models/          # Trained models (ignored in git)
├── notebooks/       # Experiments
├── tests/
├── README.md
├── requirements.txt
└── .gitignore
```

---

### ✅ 3. Speech-to-Text Module (Working)

* Implemented using **OpenAI Whisper (local model)**
* Successfully transcribes `.wav` audio into text
* FFmpeg installed and configured for audio processing

#### File:

```
src/stt/whisper_stt.py
```

#### Function:

* Input: Audio file (`sample.wav`)
* Output: Transcribed text

---

## ⚙️ Current Pipeline (Working + Planned)

```
User Speech
   ↓
Speech-to-Text (Whisper) ✅
   ↓
Text Output
   ↓
Grammar Analysis 🔄 (next step)
   ↓
Fluency Analysis 🔄
   ↓
Scoring Model (0–10) 🔄
   ↓
Level Classification (Beginner / Intermediate / Advanced) 🔄
   ↓
Lesson Recommendation System 🔄
   ↓
Daily Quiz + Final Evaluation 🔄
```

---

## 🚀 Next Steps (Immediate)

### 🔥 1. Grammar Evaluation Module

* Use transformer model (e.g., T5 / BERT)
* Detect and correct grammatical errors
* Compare original vs corrected text

### 🔥 2. Fluency Analysis

* Extract speech features:

  * Words per minute
  * Pauses
  * Fillers (uh, umm)
* Use simple ML model for scoring

### 🔥 3. Scoring System

* Combine:

  * Grammar score
  * Fluency score
  * Vocabulary quality
* Output score (0–10)

---

## 🧠 Long-Term Plan

* Personalized learning system (7-day cycle)
* Adaptive quizzes
* Performance tracking
* Backend API (FastAPI)
* Frontend (Web/App interface)

---

## 🛠 Tech Stack

* Python
* Whisper (Speech-to-Text)
* Transformers (Grammar models)
* Librosa (audio feature extraction)
* Scikit-learn / XGBoost (scoring)
* FastAPI (backend)

---

## ⚠️ Notes

* Virtual environment (`venv`) is used
* Large files (data, models, audio) are excluded via `.gitignore`
* System currently runs locally (no deployment yet)

---

## 📌 Status Summary

| Component          | Status    |
| ------------------ | --------- |
| Project Setup      | ✅ Done    |
| GitHub Integration | ✅ Done    |
| Speech-to-Text     | ✅ Working |
| Grammar Analysis   | 🔄 Next   |
| Fluency Detection  | ⏳ Pending |
| Scoring System     | ⏳ Pending |
| API / Deployment   | ⏳ Pending |

---

## 🎯 Goal

To build a **fully automated AI tutor for spoken English**, capable of:

* Evaluating user speech
* Providing feedback
* Improving skills over time
* Replacing manual assessment systems

---
