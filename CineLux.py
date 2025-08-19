import streamlit as st
import requests

# ==========================
# TMDB API CONFIG
# ==========================
API_KEY = "b4702e67e60600e85714edaf0b3308e5"  # replace with your TMDB API key
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# ==========================
# SESSION
# ==========================
session = requests.Session()
session.params = {"api_key": API_KEY}

# ==========================
# HELPER FUNCTIONS
# ==========================
def search_movies(query):
    """Search for movies or TV shows by name/keyword"""
    url = f"{BASE_URL}/search/multi"
    response = session.get(url, params={"query": query})
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


def get_genres():
    """Get genres for both movies and TV"""
    movie_genres = session.get(f"{BASE_URL}/genre/movie/list").json().get("genres", [])
    tv_genres = session.get(f"{BASE_URL}/genre/tv/list").json().get("genres", [])
    return {g["name"].lower(): g["id"] for g in movie_genres + tv_genres}


def discover_by_genre(genre_id, media_type="movie"):
    """Discover top 5 items in a genre"""
    url = f"{BASE_URL}/discover/{media_type}"
    response = session.get(url, params={"with_genres": genre_id, "sort_by": "popularity.desc", "page": 1})
    if response.status_code == 200:
        return response.json().get("results", [])[:5]
    return []


def get_providers(item_id, media_type="movie"):
    """Fetch OTT providers for both movies and TV shows"""
    url = f"{BASE_URL}/{media_type}/{item_id}/watch/providers"
    try:
        response = session.get(url)
        response.raise_for_status()
        providers = response.json().get("results", {}).get("IN", {})  # India region
        flatrate = providers.get("flatrate", [])
        return [p["provider_name"] for p in flatrate]
    except:
        return []


# ==========================
# STREAMLIT UI
# ==========================
st.set_page_config(page_title="Cinelux OTT Explorer", layout="wide")
st.title("🎬 Cinelux OTT Explorer")
st.write("Type a movie/series name OR type a genre to see top 5 results.")

# Search box
query = st.text_input("🔍 Enter movie/series name OR genre:")

# Load genres
genres = get_genres()

results = []
mode = "search"

if query:
    q_lower = query.lower()

    # If user typed a genre
    if q_lower in genres:
        st.subheader(f"Top 5 in {query.title()}")
        results = discover_by_genre(genres[q_lower], "movie") + discover_by_genre(genres[q_lower], "tv")
        mode = "genre"
    else:
        # Otherwise treat as a name search
        results = search_movies(query)

# ==========================
# DISPLAY RESULTS
# ==========================
if results:
    for item in results:
        title = item.get("title") or item.get("name")
        overview = item.get("overview", "No description available.")
        poster = item.get("poster_path")
        release_date = item.get("release_date") or item.get("first_air_date", "N/A")
        rating = item.get("vote_average", "N/A")
        media_type = item.get("media_type", "movie")  # movie or tv

        # Providers
        providers = get_providers(item["id"], media_type)

        # Display
        col1, col2 = st.columns([1, 3])
        with col1:
            if poster:
                st.image(IMAGE_BASE + poster, use_container_width=True)
        with col2:
            st.subheader(title)
            st.markdown(f"**Release Date:** {release_date}")
            st.markdown(f"**Rating:** ⭐ {rating}")
            st.markdown(f"**Overview:** {overview}")

            if providers:
                st.success("Available on: " + ", ".join(providers))
            else:
                st.error("❌ Not available on OTT")

        st.markdown("---")
