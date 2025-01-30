import streamlit as st
import pickle
import pandas as pd
import requests


# Streamlit caching to speed up API responses
import time

@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=658584cf766cac07436e673ecdead48e"

    for _ in range(3):  # Retry up to 3 times
        try:
            response = requests.get(url, timeout=5)  # Increased timeout
            response.raise_for_status()
            data = response.json()

            poster_path = data.get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500/{poster_path}"
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"

        except requests.exceptions.RequestException as e:
            print(f"Error fetching poster (Retrying...): {e}")
            time.sleep(2)  # Wait before retrying

    return "https://via.placeholder.com/500x750?text=No+Image"



# Function to recommend movies
def recommend(moviename):
    movie_index = movies[movies['title'] == moviename].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id  # Get TMDb movie ID
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))  # Fetch poster

    return recommended_movies, recommended_movies_posters


# Load movie data
movies_dict = pickle.load(open("movie.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

# Load similarity matrix
similarity = pickle.load(open("similarity.pkl", "rb"))

# Streamlit UI
st.title("🎬 Movie Recommender System")

# Movie selection dropdown
selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)

# Recommendation button
if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)  # Create 5 columns for displaying movies
    for i in range(5):
        with cols[i]:
            st.text(names[i])  # Display movie name
            st.image(posters[i], use_container_width=True)  # Display poster with proper width
