# Movie Recommendation System

A machine learning-powered movie recommendation system implementing multiple algorithms.

## Features

- **Content-Based Filtering**: Uses TF-IDF and cosine similarity on movie genres and overviews
- **Collaborative Filtering**: User-based CF using ratings matrix and cosine similarity
- **Popularity-Based**: Recommends popular movies as a fallback
- **Hybrid Recommendations**: Combines content-based and collaborative filtering

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the CLI application:

```bash
python main.py
```

Or use the system programmatically:

```python
from src.app import MovieRecommendationSystem

system = MovieRecommendationSystem()
system.train()

# Get recommendations based on a movie
system.recommend_by_movie("The Matrix", top_n=10)

# Get recommendations for a user
system.recommend_for_user(user_id=1, top_n=10)

# Hybrid recommendation
system.recommend_hybrid(user_id=1, movie_title="The Matrix", top_n=10)
```

## Data Format

### movies.csv
```
movieId,title,genres,overview
1,The Matrix,Action|Sci-Fi,A computer hacker learns about reality...
```

### ratings.csv
```
userId,movieId,rating,timestamp
1,1,5,964980000
```

## Algorithms

### Content-Based
- Uses TF-IDF vectorization on combined genre and overview text
- Computes cosine similarity between movie feature vectors
- Recommends movies similar to a given movie

### Collaborative Filtering
- Builds user-item rating matrix
- Computes user-user similarity
- Predicts ratings for unwatched movies using weighted average

### Hybrid
- Combines content-based and collaborative filtering scores
- Falls back to popularity-based recommendations when needed
