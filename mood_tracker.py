import streamlit as st
import sqlite3
from datetime import date
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import matplotlib.pyplot as plt
import random

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# --- Database ---
conn = sqlite3.connect('moods.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS moods (date TEXT, mood TEXT, note TEXT, sentiment REAL)
''')
conn.commit()

# --- Title ---
st.title("🧘 Mental Health Mood Tracker")

# --- Input ---
st.write("How are you feeling today?")
mood = st.radio("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad"])
note = st.text_area("Add a short note (optional)")
if st.button("Save Entry"):
    sentiment = sia.polarity_scores(note)["compound"]
    c.execute("INSERT INTO moods (date, mood, note, sentiment) VALUES (?, ?, ?, ?)",
              (str(date.today()), mood, note, sentiment))
    conn.commit()
    st.success("Your mood has been saved! 💚")

# --- Show Chart ---
if st.checkbox("Show mood chart"):
    c.execute("SELECT date, sentiment FROM moods")
    data = c.fetchall()
    if data:
        dates = [x[0] for x in data]
        scores = [x[1] for x in data]
        plt.figure(figsize=(10,5))
        plt.plot(dates, scores, marker='o')
        plt.xticks(rotation=45)
        plt.title("Mood Sentiment Over Time")
        plt.xlabel("Date")
        plt.ylabel("Sentiment Score")
        st.pyplot(plt)
    else:
        st.info("No data yet. Add a mood entry!")

# --- Load Quotes ---
def get_random_quote():
    try:
        with open("quotes.txt", "r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
            if quotes:
                return random.choice(quotes)
            else:
                return "Your mind is powerful — take care of it! 💚"
    except FileNotFoundError:
        return "No quotes file found. Please add a quotes.txt."

# --- Show Quote ---
if st.button("Get Positive Quote"):
    quote = get_random_quote()
    st.info(quote)

conn.close()
