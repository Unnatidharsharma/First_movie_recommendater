from flask import Flask, request, jsonify, render_template
import requests
import pickle

app = Flask(__name__)  # Flask app initialization

# Your TMDB API key
TMDB_API_KEY = '612f88fa557aa8ff9277ef6b491b70cb'
TMDB_BASE_URL = 'https://api.themoviedb.org/3/movie/'
TMDB_SEARCH_URL = 'https://api.themoviedb.org/3/search/movie'

# Load your recommendation model
try:
    with open('movie_dict.pkl', 'rb') as file:
        movie_dict = pickle.load(file)
except FileNotFoundError:
    movie_dict = {}  # Handle the case where the file doesn't exist

@app.route('/')
def home():
    return render_template('index.html')  # Render your HTML page

@app.route('/get_movie_details', methods=['POST'])
def get_movie_details():
    """
    Endpoint to fetch detailed information about a movie by its ID.
    """
    try:
        data = request.json
        movie_ids = data.get('movie_ids', [])

        if not movie_ids or not isinstance(movie_ids, list):
            return jsonify({"error": "Invalid input. Please provide a list of movie IDs."}), 400

        movie_details = []

        for movie_id in movie_ids:
            url = f"{TMDB_BASE_URL}{movie_id}"
            params = {"api_key": TMDB_API_KEY}
            response = requests.get(url, params=params)

            if response.status_code == 200:
                movie_data = response.json()
                movie_details.append({
                    "id": movie_data.get("id"),
                    "title": movie_data.get("title"),
                    "overview": movie_data.get("overview"),
                    "release_date": movie_data.get("release_date"),
                    "vote_average": movie_data.get("vote_average"),
                    "poster_url": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path')}" if movie_data.get("poster_path") else None,
                })
            else:
                movie_details.append({
                    "id": movie_id,
                    "error": f"Failed to fetch details for movie ID {movie_id}",
                })

        return jsonify({"movies": movie_details})

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500


@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Endpoint to fetch recommended movie IDs based on a given movie title.
    """
    try:
        data = request.json
        movie_title = data.get('movie_title', '')

        if movie_title not in movie_dict:
            return jsonify({"error": "Movie not found in the database."}), 404

        recommended_ids = movie_dict[movie_title]
        return jsonify({"recommended_ids": recommended_ids})

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

@app.route('/search_movie', methods=['POST'])
def search_movie():
    """
    Endpoint to search for movies based on a query string.
    """
    try:
        data = request.json
        query = data.get('query', '')

        if not query:
            return jsonify({"error": "Query string cannot be empty."}), 400

        params = {
            "api_key": TMDB_API_KEY,
            "query": query
        }
        response = requests.get(TMDB_SEARCH_URL, params=params)

        if response.status_code == 200:
            results = response.json().get("results", [])
            movies = [
                {
                    "id": movie.get("id"),
                    "title": movie.get("title"),
                    "poster_url": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None,
                } for movie in results
            ]
            return jsonify({"movies": movies})
        else:
            return jsonify({"error": "Failed to fetch search results."}), response.status_code

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

@app.route('/get_movie_cast', methods=['POST'])
def get_movie_cast():
    """
    Endpoint to fetch cast information for a given movie by its ID.
    """
    try:
        data = request.json
        movie_id = data.get('movie_id')

        if not movie_id:
            return jsonify({"error": "Movie ID is required."}), 400

        # Fetch movie cast
        cast_url = f"{TMDB_BASE_URL}{movie_id}/credits"
        params = {"api_key": TMDB_API_KEY}
        response = requests.get(cast_url, params=params)

        if response.status_code == 200:
            cast_data = response.json()
            cast_list = cast_data.get("cast", [])

            cast_details = [
                {
                    "name": cast.get("name"),
                    "character": cast.get("character"),
                    "profile_path": f"https://image.tmdb.org/t/p/w500{cast.get('profile_path')}" if cast.get("profile_path") else None
                }
                for cast in cast_list
            ]
            return jsonify({"cast": cast_details})

        else:
            return jsonify({"error": "Failed to fetch cast details."}), response.status_code

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500


@app.route('/movie_cast')
def movie_cast_page():
    return render_template('movie_cast.html')  # Render the movie cast page

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
