import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

class ContentBasedRecommender:
    def __init__(self, movies_df: pd.DataFrame, tfidf_matrix):
        self.movies_df = movies_df.reset_index(drop=True)
        self.tfidf_matrix = tfidf_matrix
        self.similarity_matrix = None

    def compute_similarity(self):
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
        return self.similarity_matrix

    def recommend(self, movie_title: str, top_n: int = 10) -> pd.DataFrame:
        if self.similarity_matrix is None:
            self.compute_similarity()

        idx = self.movies_df[self.movies_df["title"].str.lower() == movie_title.lower()].index
        if len(idx) == 0:
            return pd.DataFrame()

        idx = idx[0]
        sim_scores = list(enumerate(self.similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]

        movie_indices = [i[0] for i in sim_scores]
        scores = [i[1] for i in sim_scores]

        results = self.movies_df.iloc[movie_indices].copy()
        results["score"] = scores
        return results[["movieId", "title", "genres", "score"]]

class CollaborativeFilteringRecommender:
    def __init__(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame):
        self.ratings_df = ratings_df
        self.movies_df = movies_df
        self.user_item_matrix = None
        self.similarity_matrix = None
        self.user_index_map = {}
        self.index_user_map = {}

    def build_matrix(self):
        self.user_item_matrix = self.ratings_df.pivot_table(
            index="userId", columns="movieId", values="rating"
        ).fillna(0)
        self.user_item_matrix_sparse = csr_matrix(self.user_item_matrix.values)
        self.user_index_map = {user: idx for idx, user in enumerate(self.user_item_matrix.index)}
        self.index_user_map = {idx: user for user, idx in self.user_index_map.items()}
        return self.user_item_matrix

    def compute_similarity(self):
        if self.user_item_matrix is None:
            self.build_matrix()
        self.similarity_matrix = cosine_similarity(self.user_item_matrix_sparse)
        return self.similarity_matrix

    def recommend(self, user_id: int, top_n: int = 10) -> pd.DataFrame:
        if self.user_item_matrix is None:
            self.build_matrix()
        if self.similarity_matrix is None:
            self.compute_similarity()

        if user_id not in self.user_index_map:
            return pd.DataFrame()

        user_idx = self.user_index_map[user_id]
        user_ratings = self.user_item_matrix.iloc[user_id].values
        rated_mask = user_ratings > 0

        sim_scores = self.similarity_matrix[user_idx]
        weighted_ratings = sim_scores @ self.user_item_matrix.values
        normalization = np.abs(sim_scores).sum()
        if normalization == 0:
            return pd.DataFrame()

        pred_ratings = weighted_ratings / normalization
        pred_ratings[rated_mask] = -np.inf
        top_indices = np.argsort(pred_ratings)[::-1][:top_n]
        top_scores = pred_ratings[top_indices]

        movie_ids = self.user_item_matrix.columns[top_indices]
        results = self.movies_df[self.movies_df["movieId"].isin(movie_ids)].copy()
        score_map = dict(zip(movie_ids, top_scores))
        results["score"] = results["movieId"].map(score_map)
        results = results.sort_values("score", ascending=False)
        return results[["movieId", "title", "genres", "score"]]

class PopularityRecommender:
    def __init__(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame):
        self.ratings_df = ratings_df
        self.movies_df = movies_df
        self.popular_movies = None

    def build(self):
        movie_stats = self.ratings_df.groupby("movieId").agg(
            avg_rating=("rating", "mean"), count=("rating", "count")
        ).reset_index()
        movie_stats["score"] = movie_stats["avg_rating"] * np.log1p(movie_stats["count"])
        self.popular_movies = movie_stats.sort_values("score", ascending=False)
        return self.popular_movies

    def recommend(self, top_n: int = 10) -> pd.DataFrame:
        if self.popular_movies is None:
            self.build()
        top = self.popular_movies.head(top_n)
        results = self.movies_df[self.movies_df["movieId"].isin(top["movieId"])].copy()
        score_map = dict(zip(top["movieId"], top["score"]))
        results["score"] = results["movieId"].map(score_map)
        results = results.sort_values("score", ascending=False)
        return results[["movieId", "title", "genres", "score"]]

class HybridRecommender:
    def __init__(self, content_rec: ContentBasedRecommender, collab_rec: CollaborativeFilteringRecommender, popularity_rec: PopularityRecommender, alpha: float = 0.6):
        self.content_rec = content_rec
        self.collab_rec = collab_rec
        self.popularity_rec = popularity_rec
        self.alpha = alpha

    def recommend(self, user_id: int = None, movie_title: str = None, top_n: int = 10) -> pd.DataFrame:
        content_results = pd.DataFrame()
        collab_results = pd.DataFrame()

        if movie_title:
            content_results = self.content_rec.recommend(movie_title, top_n=top_n * 2)
            if "score" in content_results.columns and content_results["score"].max() > 0:
                content_results["score"] = content_results["score"] / content_results["score"].max()

        if user_id:
            collab_results = self.collab_rec.recommend(user_id, top_n=top_n * 2)
            if "score" in collab_results.columns and collab_results["score"].max() > 0:
                collab_results["score"] = collab_results["score"] / collab_results["score"].max()

        if content_results.empty and collab_results.empty:
            return self.popularity_rec.recommend(top_n)

        if content_results.empty:
            return collab_results.head(top_n)

        if collab_results.empty:
            return content_results.head(top_n)

        combined = pd.concat([content_results, collab_results])
        combined = combined.groupby(["movieId", "title", "genres"], as_index=False).agg({"score": "max"})
        combined = combined.sort_values("score", ascending=False).head(top_n)
        return combined[["movieId", "title", "genres", "score"]]
