-- Table: genome_scores
CREATE TABLE genome_scores (
    movieId INT NOT NULL,         
    tagId INT NOT NULL,            
    relevance FLOAT NOT NULL,     
    PRIMARY KEY (movieId, tagId),  
    FOREIGN KEY (movieId) REFERENCES movie(movieId),  
    FOREIGN KEY (tagId) REFERENCES genome_tags(tagId) 
);

-- Table: genome_tags
CREATE TABLE genome_tags (
    tagId INT NOT NULL,            
    tag VARCHAR(255) NOT NULL,    
    PRIMARY KEY (tagId)
);

-- Table: link
CREATE TABLE link (
    movieId INT NOT NULL,         
    imdbId INT,                    
    tmdbId INT,                 
    PRIMARY KEY (movieId),
    FOREIGN KEY (movieId) REFERENCES movie(movieId) 
);

-- Table: movie
CREATE TABLE movie (
    movieId INT NOT NULL,          
    title VARCHAR(255) NOT NULL,   
    genres VARCHAR(500),          
    PRIMARY KEY (movieId)
);

-- Table: rating
CREATE TABLE rating (
    userId INT NOT NULL,          
    movieId INT NOT NULL,        
    rating FLOAT NOT NULL,        
    timestamp DATETIME NOT NULL,  
    PRIMARY KEY (userId, movieId, timestamp),
    FOREIGN KEY (movieId) REFERENCES movie(movieId)
);

-- Table: tag
CREATE TABLE tag (
    userId INT NOT NULL,         
    movieId INT NOT NULL,         
    tag VARCHAR(255) NOT NULL,    
    timestamp DATETIME NOT NULL,  
    PRIMARY KEY (userId, movieId, timestamp),
    FOREIGN KEY (movieId) REFERENCES movie(movieId)
);
