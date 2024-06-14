import pickle
import streamlit as st
import requests
import pandas as pd

try:
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading pickle files: {e}")

if not isinstance(movies, pd.DataFrame):
    st.error("The 'movies' variable is not a DataFrame.")
elif 'title' not in movies.columns:
    st.error("The 'movies' DataFrame does not contain a 'title' column.")

try:
    movie_data = pd.read_csv('moviedata.csv')
except Exception as e:
    st.error(f"Error loading moviedata.csv: {e}")

if not isinstance(movie_data, pd.DataFrame):
    st.error("The 'movie_data' variable is not a DataFrame.")
elif not all(col in movie_data.columns for col in ['title', 'overview', 'cast', 'crew']):
    st.error("The 'movie_data' DataFrame does not contain necessary columns ('title', 'overview', 'cast', 'crew').")

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "https://via.placeholder.com/500x750.png?text=No+Image"
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:11]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

def display_movie_info(movie_title):
    movie_info = movie_data[movie_data['title'] == movie_title].iloc[0]
    st.sidebar.subheader("Overview")
    st.sidebar.write(movie_info['overview'])
    st.sidebar.subheader("Cast")
    cast_list = eval(movie_info['cast']) 
    st.sidebar.write(', '.join(cast_list))
    st.sidebar.subheader("DIrector")
    crew_list = eval(movie_info['crew']) 
    st.sidebar.write(', '.join(crew_list))

st.sidebar.header('Search Movies')
if isinstance(movies, pd.DataFrame) and 'title' in movies.columns:
    movie_list = movies['title'].values
    search_movie = st.sidebar.selectbox(
        "Search the Movie",
        movie_list,
        key="search_movie_selectbox"
    )

    if st.sidebar.button('Search', key="search_button", help="Click to search a movie"):
        movie_id = movies[movies['title'] == search_movie].iloc[0].movie_id
        poster = fetch_poster(movie_id)
        st.sidebar.image(poster, caption=search_movie)
        display_movie_info(search_movie)
else:
    st.error("Movies data is not loaded correctly.")

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5em;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 20px;
    }
    .recommend-button {
        background-color: #ff4b4b;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 1.2em;
        border: none;
        cursor: pointer;
    }
    .recommend-button:hover {
        background-color: #ff1a1a;
    }
    .footer-text {
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-size: 1em;
        color: #ff4b4b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-header">MovieMatch</div>', unsafe_allow_html=True)

if isinstance(movies, pd.DataFrame) and 'title' in movies.columns:
    selected_movie = st.selectbox(
        "Select a Movie",
        movie_list,
        key="recommend_movie_selectbox"
    )

    if st.button('Show Recommendation', key="recommend_button", help="Click to get movie recommendations"):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
        for i in range(0, len(recommended_movie_names), 5):
            cols = st.columns(5)
            for col, name, poster in zip(cols, recommended_movie_names[i:i+5], recommended_movie_posters[i:i+5]):
                with col:
                    st.text(name)
                    st.image(poster)
else:
    st.error("Movies data is not loaded correctly.")

st.markdown('<div class="footer-text">Made by Vedant💖</div>', unsafe_allow_html=True)
