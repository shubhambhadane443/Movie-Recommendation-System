from src.app import MovieRecommendationSystem

def main():
    print("=" * 60)
    print("        Movie Recommendation System")
    print("=" * 60)
    print()

    system = MovieRecommendationSystem(
        movies_path="data/movies.csv",
        ratings_path="data/ratings.csv"
    )

    try:
        system.train()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure movies.csv and ratings.csv exist in the data/ folder.")
        return

    while True:
        print("\nOptions:")
        print("  1. Recommend by movie title (content-based)")
        print("  2. Recommend for user (collaborative filtering)")
        print("  3. Hybrid recommendation")
        print("  4. Popular movies")
        print("  5. Exit")
        print()

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            title = input("Enter movie title: ").strip()
            if not title:
                print("Title cannot be empty.")
                continue
            results = system.recommend_by_movie(title, top_n=10)
            if results.empty:
                print("No recommendations found.")
            else:
                print(f"\nRecommendations similar to '{title}':")
                for _, row in results.iterrows():
                    print(f"  {row['title']} ({row['genres']}) - Score: {row['score']:.3f}")

        elif choice == "2":
            try:
                user_id = int(input("Enter user ID: ").strip())
            except ValueError:
                print("Invalid user ID.")
                continue
            results = system.recommend_for_user(user_id, top_n=10)
            if results.empty:
                print("No recommendations found for this user.")
            else:
                print(f"\nRecommendations for user {user_id}:")
                for _, row in results.iterrows():
                    print(f"  {row['title']} ({row['genres']}) - Score: {row['score']:.3f}")

        elif choice == "3":
            try:
                user_id = int(input("Enter user ID (or 0 to skip): ").strip())
            except ValueError:
                print("Invalid user ID.")
                continue
            movie_title = input("Enter movie title (or leave blank): ").strip()
            user_id = user_id if user_id != 0 else None
            movie_title = movie_title if movie_title else None
            if not user_id and not movie_title:
                print("Provide at least one input.")
                continue
            results = system.recommend_hybrid(user_id, movie_title, top_n=10)
            if results.empty:
                print("No recommendations found.")
            else:
                print(f"\nHybrid Recommendations:")
                for _, row in results.iterrows():
                    print(f"  {row['title']} ({row['genres']}) - Score: {row['score']:.3f}")

        elif choice == "4":
            results = system.get_popular_movies(top_n=10)
            print("\nPopular Movies:")
            for _, row in results.iterrows():
                print(f"  {row['title']} ({row['genres']}) - Score: {row['score']:.3f}")

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
