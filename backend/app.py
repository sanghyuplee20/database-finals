from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from db.connection import get_db_connection
from db.queries import search_movies_by_title, get_top_rated_movies, get_movie_tags, get_year_movie, get_similar_movies, get_movies_by_month, get_recommended_movies_by_genres
from io import BytesIO
import pandas as pd

import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/')
def serve_frontend():
    return send_file('../frontend/index.html')

@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        movies = search_movies_by_title(conn, query)
        return jsonify(movies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/movies/top-rated', methods=['GET'])
def get_top_movies():
    genre = request.args.get('genre', None)
    min_ratings = request.args.get('min_ratings', 100, type=int)

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        top_movies = get_top_rated_movies(conn, genre, min_ratings)
        return jsonify(top_movies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/movies/<movie_id>/tags', methods=['GET'])
def get_tags(movie_id):
    if not movie_id:
        return jsonify({'error': 'Movie ID is required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        tags = get_movie_tags(conn, movie_id)
        return jsonify(tags), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/movies/top-year-range', methods=['GET'])
def get_top_movies_by_year_range():
    start_year = request.args.get('start_year', None)
    end_year = request.args.get('end_year', None)

    if not start_year or not end_year or not start_year.isdigit() or not end_year.isdigit():
        return jsonify({'error': 'Valid start and end years are required'}), 400

    if int(start_year) > int(end_year):
        return jsonify({'error': 'Start year cannot be greater than end year'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        top_movies = get_year_movie(conn, start_year, end_year)
        return jsonify(top_movies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/movies/similar', methods=['GET'])
def find_similar_movies():
   movie_title = request.args.get('movie', '')
   rating = request.args.get('rating', 0, type=int)
  
   if not movie_title:
       return jsonify({'error': 'Movie title is required'}), 400


   conn = get_db_connection()
   if conn is None:
       return jsonify({'error': 'Database connection failed'}), 500


   try:
       similar_movies = get_similar_movies(conn, movie_title, rating)
       return jsonify(similar_movies), 200
   except Exception as e:
       return jsonify({'error': str(e)}), 500
   finally:
       conn.close()

@app.route('/api/movies/top-month', methods=['GET'])
def get_top_movies_by_month():
    month = request.args.get('month', None)

    if not month or not month.isdigit() or int(month) < 1 or int(month) > 12:
        return jsonify({'error': 'Valid month (1-12) is required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        # Replace `get_top_movies_by_month` with your actual database query implementation
        top_movies = get_movies_by_month(conn, int(month))
        return jsonify(top_movies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/movies/recommend', methods=['GET'])
def recommend_movies_by_genres():
    genres = request.args.get('genres', '')
    if not genres:
        return jsonify({'error': 'At least one genre is required'}), 400

    genre_list = genres.split(',')
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        recommended_movies = get_recommended_movies_by_genres(conn, genre_list)
        return jsonify(recommended_movies), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/movies/<movie_id>/review-graph', methods=['GET'])
def get_review_graph(movie_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        query = """
            SELECT DATE_FORMAT(timestamp, '%Y') AS review_year
            FROM rating
            WHERE movieId = %s
        """

        df = pd.read_sql(query, conn, params=(movie_id,))

        # Count reviews per year
        review_counts = df['review_year'].value_counts().sort_index()

        # Create the plot
        plt.figure(figsize=(10, 6))
        review_counts.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Number of Reviews Per Year', fontsize=16)
        plt.xlabel('Year', fontsize=14)
        plt.ylabel('Number of Reviews', fontsize=14)
        plt.xticks(rotation=45, fontsize=12)
        plt.tight_layout()

        # Save plot to a BytesIO object
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        # Return the image as a response
        return send_file(img, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()



if __name__ == '__main__':
    app.run(debug=True)