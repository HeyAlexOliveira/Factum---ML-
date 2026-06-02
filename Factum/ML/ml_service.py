
import re
import nltk
import joblib
from nltk.corpus import stopwords

nltk.download('stopwords')

model = joblib.load("factum_model.joblib")
vectorizer = joblib.load("vectorizer.joblib")

stop_words = set(stopwords.words('portuguese'))

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-ZÀ-ÿ0-9 ]', '', text)

    words = [
        word for word in text.split()
        if word not in stop_words
    ]

    return " ".join(words)

def predict_news(text):
    processed = preprocess(text)
    try:
        if hasattr(model, 'named_steps') and 'vect' in model.named_steps:
            prediction = model.predict([processed])[0]
        else:
            vector = vectorizer.transform([processed])
            prediction = model.predict(vector)[0]
    except Exception:
        raise

    return prediction
