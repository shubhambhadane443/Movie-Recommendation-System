import pandas as pd
import numpy as np
from src.data_loader import DataLoader
from src.preprocessor import Preprocessor
from src.recommenders import ContentBasedRecommender, CollaborativeFilteringRecommender, PopularityRecommender, HybridRecommender

class MovieRecommendationSystem:
    def __init__(self, movies_path: str = "data/movies.csv", ratings_path: str = "data/ratings.csv"):
        self.data_loader = DataLoader(movies_path, ratings_path)
        self.preprocessor = Preprocessor()
        self.content_rec = None
        self.collab_rec = None
        self.popularity_rec = None
        self.hybrid_rec = None
        self.is_trained = False

    def train(self):
        print("Loading data...")
        movies_df, ratings_df = self.data_loader.load_all()
        print(f"Loaded {len(movies_df)} movies and {len(ratings_df)} ratings.")

        print("Preprocessing...")
        tfidf_matrix = self.preprocessor.prepare_content_features(movies_df)

        print("Training content-based recommender...")
        self.content_rec = ContentBasedRecommender(movies_df, tfidf_matrix)
        self.content_rec.compute_similarity()

        print("Training collaborative filtering recommender...")
        self.collab_rec = CollaborativeFilteringRecommender(ratings_df, movies_df)
        self.collab_rec.build_matrix()
        self.collab_rec.compute_similarity()

        print("Training popularity recommender...")
        self.popularity_rec = PopularityRecommender(ratings_df, movies_df)
        self.popularity_rec.build()

        print("Initializing hybrid recommender...")
        self.hybrid_rec = HybridRecommender(self.content_rec, self.collab_rec, self.popularity_rec)

        self.is_trained = True
        print("Training complete!\n")

    def recommend_by_movie(self, movie_title: str, top_n: int = 10) -> pd.DataFrame:
        if not self.is_trained:
            raise RuntimeError("System not trained. Call train() first.")
        return self.content_rec.recommend(movie_title, top_n)

    def recommend_for_user(self, user_id: int, top_n: int = 10) -> pd.DataFrame:
        if not self.is_trained:
            raise RuntimeError("System not trained. Call train() first.")
        return self.collab_rec.recommend(user_id, top_n)

    def recommend_hybrid(self, user_id: int = None, movie_title: str = None, top_n: int = 10) -> pd.DataFrame:
        if not self.is_trained:
            raise RuntimeError("System not trained. Call train() first.")
        return self.hybrid_rec.recommend(user_id, movie_title, top_n)

    def get_popular_movies(self, top_n: int = 10) -> pd.DataFrame:
        if not self.is_trained:
            raise RuntimeError("System not trained. Call train() first.")
        return self.popularity_rec.recommend(top_n)
