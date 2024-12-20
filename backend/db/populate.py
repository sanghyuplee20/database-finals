import os
import csv
from datetime import datetime
from connection import get_db_connection

# Configure intervals
PROGRESS_INTERVAL = 1000  # Print progress every 1,000 inserts
COMMIT_INTERVAL = 5000    # Commit every 5,000 inserts to reduce memory load

def create_tables(cursor):
    # Create tables if they don't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genome_scores (
            movieId INT NOT NULL,
            tagId INT NOT NULL,
            relevance FLOAT NOT NULL,
            PRIMARY KEY (movieId, tagId)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genome_tags (
            tagId INT NOT NULL,
            tag VARCHAR(255),
            PRIMARY KEY (tagId)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS link (
            movieId INT NOT NULL,
            imdbId INT,
            tmdbId INT,
            PRIMARY KEY (movieId)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movie (
            movieId INT NOT NULL,
            title VARCHAR(255),
            genres VARCHAR(500),
            PRIMARY KEY (movieId)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rating (
            userId INT NOT NULL,
            movieId INT NOT NULL,
            rating FLOAT NOT NULL,
            timestamp DATETIME NOT NULL,
            PRIMARY KEY (userId, movieId, timestamp)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tag (
            userId INT NOT NULL,
            movieId INT NOT NULL,
            tag VARCHAR(255),
            timestamp DATETIME NOT NULL
        )
    """)


def import_csv(cursor, conn, filename, tablename):
    filepath = os.path.join("data", filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, quotechar='"', skipinitialspace=True)
        header = next(reader, None)
        if header is None:
            print(f"No header found in {filename}, skipping.")
            return
        
        # Clean header column names by stripping surrounding quotes
        columns = [col.strip('"') for col in header]
        placeholders = ', '.join(['%s'] * len(columns))
        col_names = ', '.join(columns)
        insert_query = f"INSERT INTO {tablename} ({col_names}) VALUES ({placeholders})"

        row_count = 0
        for row in reader:
            # Handle timestamp columns for 'rating' and 'tag' tables
            if tablename in ('rating', 'tag'):
                # The last column is timestamp
                timestamp_str = row[-1]
                # Attempt to parse timestamp
                try:
                    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    row[-1] = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError as ve:
                    print(f"Error parsing timestamp '{timestamp_str}' in file {filename}: {ve}")
                    continue  # Skip this row

            # Insert the row
            try:
                cursor.execute(insert_query, row)
            except Exception as ex:
                print(f"Error inserting row {row} into {tablename}: {ex}")
                # Decide whether to break or continue:
                # break  # If you want to stop on error
                continue  # If you want to skip bad rows

            row_count += 1
            # Print progress every PROGRESS_INTERVAL rows
            if row_count % PROGRESS_INTERVAL == 0:
                print(f"{row_count} rows inserted into {tablename}...")

            # Commit every COMMIT_INTERVAL rows
            if row_count % COMMIT_INTERVAL == 0:
                conn.commit()
                print(f"Committed {row_count} rows into {tablename} so far.")

        # Final commit after finishing this file
        conn.commit()
        print(f"Finished importing {row_count} rows into {tablename}.")


def populate_database():
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database.")
        return

    try:
        cursor = conn.cursor()
        #create_tables(cursor)
        conn.commit()

        files_to_tables = {
            'genome_scores.csv': 'genome_scores',
            'genome_tags.csv': 'genome_tags',
            'link.csv': 'link',
            'movie.csv': 'movie',
            'rating.csv': 'rating',
            'tag.csv': 'tag'
        }

        # Optionally clear tables before insert
        for filename, tablename in files_to_tables.items():
            print(f"Clearing table {tablename}...")
            cursor.execute(f"DELETE FROM {tablename}")
        conn.commit()

        # Populate each table
        for filename, tablename in files_to_tables.items():
            print(f"Importing {filename} into {tablename}...")
            import_csv(cursor, conn, filename, tablename)

        print("All data imported successfully!")

    except Exception as e:
        print(f"Error while populating the database: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    populate_database()
