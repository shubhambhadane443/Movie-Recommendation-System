import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer

class Preprocessor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self.mlb = MultiLabelBinarizer()
        self.tfidf_matrix = None
        self.genre_matrix = None

    def clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def prepare_content_features(self, movies_df: pd.DataFrame) -> np.ndarray:
        movies_df = movies_df.copy()
        movies_df["clean_genres"] = movies_df["genres"].apply(lambda x: " ".join(x.split("|")) if pd.notna(x) else "")
        movies_df["clean_overview"] = movies_df["overview"].apply(self.clean_text) if "overview" in movies_df.columns else ""
        movies_df["content"] = movies_df["clean_genres"] + " " + movies_df["clean_overview"]

        self.tfidf_matrix = self.vectorizer.fit_transform(movies_df["content"])
        return self.tfidf_matrix

    def get_tfidf_matrix(self) -> np.ndarray:
        return self.tfidf_matrix
