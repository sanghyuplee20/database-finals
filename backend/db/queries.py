import random

def fetch_all_items(conn):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM movie;")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching items: {e}")
        return []

def search_movies_by_title(conn, title_query):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("CALL GetTopMoviesByTitlePattern(%s)", (f"%{title_query}%",))
        result = cursor.fetchall()


        if result:
            return result
        else:
            print("No movies found")
            return []  
    except Exception as e:
        print(f"Error searching movies: {e}")
        return []

def get_top_rated_movies(conn, genre=None, min_ratings=100):
    try:
        cursor = conn.cursor(dictionary=True)
        genre_filter = "AND m.genres LIKE %s" if genre else ""
        params = [min_ratings]
        if genre:
            params.append(f"%{genre}%")
        
        cursor.execute(f"""
            SELECT m.movieId, m.title, m.genres, AVG(r.rating) as avg_rating, COUNT(r.rating) as rating_count
            FROM movie m
            JOIN rating r ON m.movieId = r.movieId
            GROUP BY m.movieId, m.title, m.genres
            HAVING rating_count >= %s
            {genre_filter}
            ORDER BY avg_rating DESC
            LIMIT 10;
        """, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting top rated movies: {e}")
        return []

def get_movie_tags(conn, movie_id):
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("CALL GetTopTagsByMovieId(%s)", (movie_id))
    
        return cursor.fetchall()
    
    except Exception as e:
        print(f"Error getting movie tags: {e}")
        return []

def get_year_movie(conn, start_year, end_year):
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("CALL GetMoviesByYearRange(%s, %s)", (start_year, end_year))
        return cursor.fetchall()


def get_similar_movies(conn, movie_title, user_rating):
   try:
       cursor = conn.cursor(dictionary=True)
      
       cursor.execute("""
           SELECT movieId, title, genres
           FROM movie
           WHERE LOWER(title) LIKE LOWER(%s)
           LIMIT 1
       """, (f"%{movie_title}%",))
      
       base_movie = cursor.fetchone()
       if not base_movie:
           print("No movie found with the given title.")
           return []


       cursor.execute("""
           SELECT gt.tag, gs.tagId, gs.relevance
           FROM genome_scores gs
           JOIN genome_tags gt ON gs.tagId = gt.tagId
           WHERE gs.movieId = %s AND gs.relevance > 0.5
           ORDER BY gs.relevance DESC
       """, (base_movie['movieId'],))
      
       base_movie_tags = cursor.fetchall()
       tag_ids = [row['tagId'] for row in base_movie_tags] if base_movie_tags else []


       if tag_ids:
           placeholder = ','.join(['%s'] * len(tag_ids)) 
       else:
           placeholder = 'NULL' 


       query = f"""
           WITH movie_tag_scores AS (
               SELECT m.movieId, m.title, m.genres, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count,
                   ( LENGTH(m.genres) -
                       LENGTH(REPLACE(m.genres, '|', '')) + 1 +
                       LENGTH(%s) -
                       LENGTH(REPLACE(%s, '|', '')) + 1 -
                       ABS(
                           LENGTH(m.genres) -
                           LENGTH(REPLACE(m.genres, '|', '')) + 1 -
                           LENGTH(%s) -
                           LENGTH(REPLACE(%s, '|', '')) + 1
                       )
                   ) / 2 AS genre_similarity,
                   COALESCE(
                       (
                           SELECT AVG(gs.relevance)
                           FROM genome_scores gs
                           WHERE gs.movieId = m.movieId
                           AND gs.tagId IN ({placeholder})
                           AND gs.relevance > 0.5
                       ), 0
                   ) AS tag_similarity
               FROM movie m
               JOIN rating r ON m.movieId = r.movieId
               WHERE m.movieId != %s AND m.genres REGEXP REPLACE(REPLACE(%s, '|', '|.*|'), '|', '')
               GROUP BY m.movieId, m.title, m.genres
               HAVING rating_count >= 100 AND (ABS(avg_rating - %s) <= 0.5 OR %s = 0)
           )
           SELECT *, (genre_similarity * 0.4 + tag_similarity * 0.6) AS total_similarity
           FROM movie_tag_scores
           ORDER BY total_similarity DESC, avg_rating DESC
           LIMIT 10
       """


       params = (
           base_movie['genres'], base_movie['genres'],  
           base_movie['genres'], base_movie['genres'],  
           *tag_ids,                                    
           base_movie['movieId'],                     
           base_movie['genres'],                      
           float(user_rating), float(user_rating)      
       )
       cursor.execute(query, params)
       similar_movies = cursor.fetchall()


       for movie in similar_movies:
           cursor.execute("""
                SELECT gt.tag, gs.relevance
                FROM genome_scores gs
                JOIN genome_tags gt ON gs.tagId = gt.tagId
                WHERE gs.movieId = %s AND gs.relevance > 0.5
                ORDER BY gs.relevance DESC
                LIMIT 5
           """, (movie['movieId'],))
           movie['tags'] = cursor.fetchall()
           movie['total_similarity'] = round(movie.get('total_similarity', 0) * 100, 2)
           movie['genre_similarity'] = round(movie.get('genre_similarity', 0), 2)
           movie['tag_similarity'] = round(movie.get('tag_similarity', 0) * 100, 2)
           movie['avg_rating'] = round(movie.get('avg_rating', 0), 2)
       return similar_movies


   except Exception as e:
       print(f"Error finding similar movies: {e}")
       return []
   
def get_movies_by_month(conn, month):
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("CALL GetTopMoviesByMonth(%s)", (month,))
        return cursor.fetchall()

def get_recommended_movies_by_genres(conn, genres):
    genre_pattern = '|'.join(genres)

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("CALL GetTopMoviesByGenre(%s)", (genre_pattern,))
        results = cursor.fetchall()

    random.shuffle(results)
    return results[:10] 
