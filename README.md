# Movie Recommendation System

## Overview

This project is a Movie Recommendation System built using a Flask backend and a database populated with the MovieLens 20M dataset. It features advanced recommendation algorithms and an intuitive web interface that allows users to search for movies, explore top-rated films, and view similar recommendations.

---

## Setup Guide

### Prerequisites

Ensure you have the following installed:
- Python 3.8 or later
- Flask
- Pandas
- MatPlot
- MySQL or a compatible database system
- Required Python libraries (listed in `requirements.txt`)

### Downloading the Dataset

Before running the application, you need to download the dataset from Kaggle:

1. Visit the [MovieLens 20M dataset](https://www.kaggle.com/grouplens/movielens-20m-dataset).
2. Download and extract the dataset.
3. Place the following CSV files into the `db/data` directory:
   - `genome_scores.csv`
   - `genome_tags.csv`
   - `link.csv`
   - `movie.csv`
   - `rating.csv`
   - `tag.csv`
4. Update .env file accordance to the database you have in your system.

### Initializing the Database

1. Ensure the database connection details in `connection.py` are correctly configured.
2. Run the `populate.py` script to create and populate the tables:
   ```bash
   python populate.py
   ```
   
   This script will:
   - Create the required tables in your database.
   - Load the data from the CSV files into the database.

---

## Running the Application

1. Navigate to the `backend` folder.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Flask server:
   ```bash
   python app.py
   or
   flask run
   ```
4. The application backend will start on [http://127.0.0.1:5000/](http://127.0.0.1:5000/) by default. Open the html file location in your directory and run.

---

## Web Interface Features

- **Search**: Use the search bar to find movies by title.
- **Top-Rated**: View a list of the top-rated movies.
- **Similar Movies**: Explore movies similar to your selected movie.
- **Expandable Details**: Click on a movie card to see additional metadata.
- **Recommendation Movies**: View recommendations accordance to genre input

---

## Notes

- Make sure the database server is running and accessible before starting the Flask application.
- The default configuration assumes a local database setup. Update the connection details in `connection.py` if using a remote database.
- If you encounter issues during the setup, ensure all required Python libraries are installed and the dataset is correctly placed in the `db/data` directory.

---
