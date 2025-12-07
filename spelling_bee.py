import streamlit as st
import pandas as pd
import zipfile
import tempfile
import sqlite3
import os

st.title("Spelling Practice App – Numbers File Support (iPad Compatible)")
st.write("Upload a .numbers file containing: WORD, PRONUNCIATION, PART OF SPEECH, DEFINITION AND SENTENCE")


# --- Extract .numbers file ---
def read_numbers_file(numbers_file):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(numbers_file.read())
    tmp.close()

    with zipfile.ZipFile(tmp.name, 'r') as z:
        sqlite_path = None
        for name in z.namelist():
            if name.endswith("Index.zip"):
                z.extract(name, "/tmp")
                nested_zip = os.path.join("/tmp", name)

                with zipfile.ZipFile(nested_zip, 'r') as nested:
                    for n2 in nested.namelist():
                        if n2.endswith(".sqlite"):
                            sqlite_path = nested.extract(n2, "/tmp")
                break

    if not sqlite_path:
        raise Exception("Could not locate SQLite table inside .numbers file")

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_name = cursor.fetchall()[0][0]

    df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
    conn.close()
    return df


# --- Main App ---
uploaded = st.file_uploader("Upload .numbers file", type=["numbers"])

if uploaded:
    try:
        df = read_numbers_file(uploaded)

        required_cols = ["WORD", "PRONUNCIATION", "PART OF SPEECH", "DEFINITION AND SENTENCE"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Missing column: {col}")
                st.stop()

        st.success(f"Loaded {len(df)} words!")

        words = sorted(df["WORD"].dropna().unique())
        selected_word = st.selectbox("Choose a word:", words)

        row = df[df["WORD"] == selected_word].iloc[0]

        st.header(row["WORD"])
        st.write("### Pronunciation")
        st.write(row["PRONUNCIATION"])

        st.write("### Part of Speech")
        st.write(row["PART OF SPEECH"])

        st.write("### Definition & Sentence")
        st.write(row["DEFINITION AND SENTENCE"])

        # Browser-based TTS (works on iPad)
        speak_button = st.button("🔊 Pronounce")

        if speak_button:
            st.components.v1.html(
                f"""
                <script>
                    var utterance = new SpeechSynthesisUtterance("{selected_word}");
                    speechSynthesis.speak(utterance);
                </script>
                """,
                height=0,
            )

    except Exception as e:
        st.error(f"Error reading .numbers file: {e}")
