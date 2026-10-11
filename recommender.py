import joblib
import pandas as pd


# ==========================================
# LOAD TRAINED MODEL
# ==========================================

model_data = joblib.load("model.pkl")

model = model_data["model"]
movie_ids = model_data["movie_ids"]
movie_id_to_index = model_data["movie_id_to_index"]
movies = model_data["movies"]


# ==========================================
# LOAD RATINGS
# ==========================================

ratings = pd.read_csv("dataset/ratings.csv")


# ==========================================
# CALCULATE MOVIE STATISTICS
# ==========================================

movie_statistics = ratings.groupby("movieId").agg(
    average_rating=("rating", "mean"),
    rating_count=("rating", "count")
).reset_index()


# ==========================================
# RECOMMEND MOVIES
# ==========================================

def recommend_movies(movie_title, number_of_recommendations=10):

    # Find the selected movie
    movie_match = movies[
        movies["title"].str.lower() == movie_title.lower()
    ]

    # Movie not found
    if movie_match.empty:
        return []

    # Get movie ID
    movie_id = movie_match.iloc[0]["movieId"]

    # Check whether movie has ratings
    if movie_id not in movie_id_to_index:
        return []

    # Get movie position
    movie_index = movie_id_to_index[movie_id]

    # Find similar movies
    distances, indices = model.kneighbors(
        model._fit_X[movie_index].reshape(1, -1),
        n_neighbors=number_of_recommendations + 1
    )

    recommendations = []

    # Skip first result because it is the selected movie
    for i in range(1, len(indices[0])):

        recommended_index = indices[0][i]

        recommended_movie_id = movie_ids[recommended_index]

        recommended_movie = movies[
            movies["movieId"] == recommended_movie_id
        ]

        if recommended_movie.empty:
            continue

        # Movie information
        title = recommended_movie.iloc[0]["title"]
        genres = recommended_movie.iloc[0]["genres"]

        # Calculate similarity
        similarity = (1 - distances[0][i]) * 100

        # Get rating statistics
        stats = movie_statistics[
            movie_statistics["movieId"] == recommended_movie_id
        ]

        if not stats.empty:

            average_rating = round(
                stats.iloc[0]["average_rating"],
                1
            )

            rating_count = int(
                stats.iloc[0]["rating_count"]
            )

        else:

            average_rating = 0
            rating_count = 0

        # Add recommendation
        recommendations.append({
            "movieId": int(recommended_movie_id),
            "title": title,
            "genres": genres,
            "similarity": round(similarity, 2),
            "rating": average_rating,
            "rating_count": rating_count
        })

    return recommendations


# ==========================================
# TEST RECOMMENDATION SYSTEM
# ==========================================

if __name__ == "__main__":

    movie = "Toy Story (1995)"

    print("=" * 60)
    print("MOVIE RECOMMENDATION SYSTEM")
    print("=" * 60)

    print(f"\nSelected Movie: {movie}")

    recommendations = recommend_movies(movie, 10)

    print("\nRecommended Movies:")
    print("-" * 60)

    if recommendations:

        for i, recommendation in enumerate(
            recommendations,
            start=1
        ):

            print(
                f"{i}. {recommendation['title']}"
            )

            print(
                f"   Genre: {recommendation['genres']}"
            )

            print(
                f"   Rating: "
                f"{recommendation['rating']}/5"
            )

            print(
                f"   Number of ratings: "
                f"{recommendation['rating_count']}"
            )

            print(
                f"   Similarity: "
                f"{recommendation['similarity']}%"
            )

            print()

    else:

        print(
            "Movie not found or no recommendations available."
        )