import pandas as pd
import numpy as np
from typing import Optional

class DataLoader:
    def __init__(self, movies_path: str = "data/movies.csv", ratings_path: Optional[str] = None):
        self.movies_path = movies_path
        self.ratings_path = ratings_path
        self.movies_df = None
        self.ratings_df = None

    def load_movies(self) -> pd.DataFrame:
        self.movies_df = pd.read_csv(self.movies_path)
        return self.movies_df

    def load_ratings(self) -> Optional[pd.DataFrame]:
        if self.ratings_path:
            self.ratings_df = pd.read_csv(self.ratings_path)
            return self.ratings_df
        return None

    def load_all(self):
        self.load_movies()
        self.load_ratings()
        return self.movies_df, self.ratings_df
