from src.data_loader import DataLoader
from src.preprocessor import Preprocessor
from src.recommenders import (
    ContentBasedRecommender,
    CollaborativeFilteringRecommender,
    PopularityRecommender,
    HybridRecommender,
)

def test_preprocessor():
    pre = Preprocessor()
    assert pre.clean_text("Hello World!!!  ") == "hello world"
    assert pre.clean_text("") == ""
    assert pre.clean_text(None) == ""
    print("test_preprocessor passed")

def test_content_based():
    loader = DataLoader(movies_path="data/movies.csv")
    df = loader.load_movies()
    pre = Preprocessor()
    tfidf = pre.prepare_content_features(df)
    rec = ContentBasedRecommender(df, tfidf)
    sim = rec.compute_similarity()
    assert sim.shape[0] == len(df)
    assert sim.shape[1] == len(df)
    results = rec.recommend("The Matrix", top_n=5)
    assert not results.empty
    assert len(results) <= 5
    print("test_content_based passed")

def test_collaborative_filtering():
    loader = DataLoader(movies_path="data/movies.csv", ratings_path="data/ratings.csv")
    movies, ratings = loader.load_all()
    rec = CollaborativeFilteringRecommender(ratings, movies)
    rec.build_matrix()
    sim = rec.compute_similarity()
    assert sim.shape[0] == rec.user_item_matrix.shape[0]
    results = rec.recommend(1, top_n=5)
    assert not results.empty
    assert len(results) <= 5
    print("test_collaborative_filtering passed")

def test_popularity():
    loader = DataLoader(movies_path="data/movies.csv", ratings_path="data/ratings.csv")
    movies, ratings = loader.load_all()
    rec = PopularityRecommender(ratings, movies)
    rec.build()
    results = rec.recommend(5)
    assert not results.empty
    assert len(results) == 5
    print("test_popularity passed")

if __name__ == "__main__":
    test_preprocessor()
    test_content_based()
    test_collaborative_filtering()
    test_popularity()
    print("\nAll tests passed!")
