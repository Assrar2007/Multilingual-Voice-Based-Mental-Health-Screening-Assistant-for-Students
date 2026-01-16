import streamlit as st
import tempfile
import whisper
from gtts import gTTS
import langid
import os

# --------------------
# STREAMLIT CONFIG
# --------------------
st.set_page_config(page_title="MindCare AI", layout="centered")

st.title("🧠 MindCare AI")
st.write("AI-based multilingual mental health screening assistant for students.")

# --------------------
# LOAD WHISPER MODEL (CACHED + FAST)
# --------------------
@st.cache_resource
def load_whisper():
    return whisper.load_model("tiny")   # faster than base

with st.spinner("Loading AI Speech Model... Please wait"):
    whisper_model = load_whisper()

# --------------------
# LANGUAGE MAP
# --------------------
LANG_MAP = {
    'en': "English",
    'hi': "Hinglish",
    'ta': "Tamil"
}

# --------------------
# STRESS CLASSIFIER
# --------------------
def classify_stress(text):
    text = text.lower()
    score = 0
    if any(w in text for w in ["exam", "study", "marks", "score", "padikka"]):
        score += 1
    if any(w in text for w in ["sleep", "can't sleep", "thoongala", "sona nahi"]):
        score += 2
    if any(w in text for w in ["stress", "anxiety", "pressure", "tense", "bayama"]):
        score += 2

    if score <= 2:
        return "Low Stress"
    elif score <= 4:
        return "Medium Stress"
    else:
        return "High Stress"

# --------------------
# CRISIS DETECTION
# --------------------
def crisis_detect(text):
    crisis_words = ["suicide", "kill", "die", "give up", "end life", "varamudiyala"]
    return any(w in text.lower() for w in crisis_words)

# --------------------
# COPING STRATEGIES
# --------------------
STRATEGIES = {
    "en": [
        "Use Pomodoro for study (25m work + 5m break)",
        "Reduce caffeine after evening",
        "Experiment with sleep schedule",
        "Practice 10-min deep breathing"
    ],
    "hi": [
        "25 minute study + 5 minute break use karo",
        "Shaam ke baad caffeine kam karo",
        "Sona ek fix time pe try karo",
        "10 minute deep breathing helpful hota hai"
    ],
    "ta": [
        "25 nimisham padichu 5 nimisham break edunga",
        "Saayanga coffee avoid pannunga",
        "Daily same time la thoongunga",
        "10 nimisham deep breathing try panlaam"
    ]
}

# --------------------
# TEXT TO SPEECH
# --------------------
def speak(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp.name)
    return temp.name

# --------------------
# INPUT UI
# --------------------
audio_file = st.file_uploader("Upload audio note", type=["mp3", "wav", "m4a"])
typed_text = st.text_input("Or type your message here:")

# --------------------
# PROCESS INPUT
# --------------------
if audio_file or typed_text:

    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(audio_file.read())
            result = whisper_model.transcribe(temp.name)
            user_text = result['text']
            st.write("You said:", user_text)
    else:
        user_text = typed_text

    lang, _ = langid.classify(user_text)
    if lang not in LANG_MAP:
        lang = "en"

    st.write(f"Detected Language: **{LANG_MAP[lang]}**")

    # crisis handling
    if crisis_detect(user_text):
        st.error("⚠ Crisis Indicators Detected")
        msg = {
            "en": "You are not alone. Please reach out for help.",
            "hi": "Aap akelay nahi ho. Please help contact karo.",
            "ta": "Neenga thani illa. Please help thedu."
        }
        st.write(msg.get(lang, msg["en"]))

        st.write("📞 Tele-MANAS India: 14416")
        st.write("📞 NIMHANS: +91-80-46110007")
        speak_file = speak(msg.get(lang, msg["en"]), "en")
        st.audio(speak_file, format="audio/mp3")

    else:
        level = classify_stress(user_text)
        st.write(f"### Stress Level: **{level}**")

        st.write("### Suggested Strategies:")
        for s in STRATEGIES.get(lang, STRATEGIES["en"]):
            st.write(f"- {s}")

        speak_file = speak(user_text, "en")
        st.audio(speak_file, format="audio/mp3")
