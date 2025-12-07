import streamlit as st
import pandas as pd
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

st.title("Spelling Practice App (CSV Version)")
st.write("Upload a CSV file containing: WORD, PRONUNCIATION, PART OF SPEECH, DEFINITION AND SENTENCE")

# Upload CSV
uploaded_file = st.file_uploader("Upload your vocabulary CSV", type=["csv"])

if uploaded_file:
    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Ensure required columns exist
    required_cols = ["WORD", "PRONUNCIATION", "PART OF SPEECH", "DEFINITION AND SENTENCE"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV must contain columns: {', '.join(required_cols)}")
    else:
        st.success(f"Loaded {len(df)} words!")

        # Dropdown list of words (unique & sorted)
        words = sorted(df["WORD"].dropna().unique())
        selected_word = st.selectbox("Select a word to practice:", words)

        # Get row for selected word
        row = df[df["WORD"] == selected_word].iloc[0]

        st.header(selected_word)

        st.write("### Pronunciation")
        st.write(row["PRONUNCIATION"])

        st.write("### Part of Speech")
        st.write(row["PART OF SPEECH"])

        st.write("### Definition and Sentence")
        st.write(row["DEFINITION AND SENTENCE"])

        # Pronounce button
        if st.button("🔊 Pronounce"):
            engine.say(selected_word)
            engine.runAndWait()
