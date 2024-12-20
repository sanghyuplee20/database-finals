
DELIMITER \\
CREATE PROCEDURE GetTopMoviesByTitlePattern (
    IN title_pattern VARCHAR(255)
)
BEGIN
    SELECT m.*, AVG(r.rating) AS avg_rating
    FROM movie m
    LEFT JOIN rating r ON m.movieId = r.movieId
    WHERE LOWER(m.title) LIKE LOWER(title_pattern)
    GROUP BY m.movieId
    ORDER BY avg_rating DESC
    LIMIT 10;
END\\
DELIMITER ;

DELIMITER \\
CREATE PROCEDURE GetTopTagsByMovieId (
    IN movie_id INT
)
BEGIN
    SELECT gt.tag, gs.relevance
    FROM genome_scores gs
    JOIN genome_tags gt ON gs.tagId = gt.tagId
    WHERE gs.movieId = movie_id
    ORDER BY gs.relevance DESC
    LIMIT 10;
END\\
DELIMITER ;


DELIMITER \\
CREATE PROCEDURE GetMoviesByYearRange (
    IN start_year INT,
    IN end_year INT
)
BEGIN
    SELECT m.movieId, 
           m.title, 
           m.genres, 
           AVG(r.rating) AS avg_rating, 
           COUNT(r.rating) AS rating_count
    FROM movie m
    JOIN rating r ON m.movieId = r.movieId
    WHERE YEAR(r.timestamp) BETWEEN start_year AND end_year
    GROUP BY m.movieId, m.title, m.genres
    HAVING COUNT(r.rating) > 100
    ORDER BY avg_rating DESC, rating_count DESC
    LIMIT 5;
END\\
DELIMITER ;


DELIMITER \\
DROP PROCEDURE IF EXISTS GetTopMoviesByMonth$$
CREATE PROCEDURE GetTopMoviesByMonth (
    IN month INT
)
BEGIN
    SELECT m.movieId, m.title, m.genres, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count
    FROM movie m
    JOIN rating r 
    ON m.movieId = r.movieId
    WHERE  MONTH(r.timestamp) = month
    GROUP BY m.movieId, m.title, m.genres
    HAVING COUNT(r.rating) > 100
    ORDER BY avg_rating DESC, rating_count DESC
    LIMIT 10;
END\\
DELIMITER ;

DELIMITER \\
DROP PROCEDURE IF EXISTS GetTopMoviesByGenre$$
CREATE PROCEDURE GetTopMoviesByGenre (
    IN genre_pattern VARCHAR(255)
)
BEGIN
    SELECT m.movieId, m.title, m.genres, AVG(r.rating) AS avg_rating, COUNT(r.rating) AS rating_count
    FROM  movie m
    JOIN rating r 
    ON m.movieId = r.movieId
    WHERE m.genres REGEXP genre_pattern
    GROUP BY m.movieId, m.title, m.genres
    HAVING COUNT(r.rating) > 100
    ORDER BY avg_rating DESC, rating_count DESC
    LIMIT 100;
END\\
DELIMITER ;

