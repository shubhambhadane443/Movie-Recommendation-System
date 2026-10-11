import pandas as pd
import joblib
from sklearn.neighbors import NearestNeighbors


# ==========================================
# 1. LOAD DATA
# ==========================================

print("Loading datasets...")

movies = pd.read_csv("dataset/movies.csv")
ratings = pd.read_csv("dataset/ratings.csv")

print(f"Movies loaded: {len(movies)}")
print(f"Ratings loaded: {len(ratings)}")


# ==========================================
# 2. CREATE USER-MOVIE MATRIX
# ==========================================

print("\nCreating user-movie matrix...")

user_movie_matrix = ratings.pivot_table(
    index="movieId",
    columns="userId",
    values="rating"
).fillna(0)

print("Matrix created!")
print("Matrix shape:", user_movie_matrix.shape)


# ==========================================
# 3. TRAIN NEAREST NEIGHBORS MODEL
# ==========================================

print("\nTraining recommendation model...")

model = NearestNeighbors(
    metric="cosine",
    algorithm="brute",
    n_neighbors=11
)

model.fit(user_movie_matrix.values)

print("Model trained successfully!")


# ==========================================
# 4. CREATE MOVIE ID MAPPING
# ==========================================

movie_ids = user_movie_matrix.index.tolist()

movie_id_to_index = {
    movie_id: index
    for index, movie_id in enumerate(movie_ids)
}


# ==========================================
# 5. SAVE MODEL
# ==========================================

model_data = {
    "model": model,
    "movie_ids": movie_ids,
    "movie_id_to_index": movie_id_to_index,
    "movies": movies
}

joblib.dump(model_data, "model.pkl")

print("\nModel saved successfully!")
print("File created: model.pkl")


# ==========================================
# 6. TEST THE MODEL
# ==========================================

test_movie = 1  # Toy Story

if test_movie in movie_id_to_index:

    movie_index = movie_id_to_index[test_movie]

    distances, indices = model.kneighbors(
        user_movie_matrix.iloc[movie_index].values.reshape(1, -1),
        n_neighbors=11
    )

    print("\nTest Recommendation")
    print("=" * 50)

    selected_movie = movies[
        movies["movieId"] == test_movie
    ]["title"].iloc[0]

    print("Selected movie:", selected_movie)

    print("\nRecommended movies:")

    for i in range(1, len(indices[0])):

        recommended_index = indices[0][i]

        recommended_movie_id = movie_ids[recommended_index]

        recommended_movie = movies[
            movies["movieId"] == recommended_movie_id
        ]["title"].iloc[0]

        similarity = 1 - distances[0][i]

        print(
            f"{i}. {recommended_movie} "
            f"({similarity * 100:.2f}% similarity)"
        )


print("\n========================================")
print("MODEL TRAINING COMPLETED SUCCESSFULLY")
print("========================================")