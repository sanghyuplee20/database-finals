const showLoadingSpinner = () => {
    document.getElementById('loading-spinner').style.display = 'flex';
};

const hideLoadingSpinner = () => {
    document.getElementById('loading-spinner').style.display = 'none';
};

const createMovieCard = (movie) => {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.innerHTML = `
        <h3>${movie.title}</h3>
        <p>Genres: ${movie.genres}</p>
        ${movie.avg_rating ? `<p>Average Rating: ${Number(movie.avg_rating).toFixed(2)}</p>` : ''}
        ${movie.rating_count ? `<p>Number of Ratings: ${movie.rating_count}</p>` : ''}
        <button onclick="toggleMovieDetails(${movie.movieId}, this)">View Details</button>
        <div id="tags-${movie.movieId}" class="movie-tags" style="display: none;"></div>
    `;
    return card;
};

async function toggleMovieDetails(movieId, button) {
    const detailsContainer = document.getElementById(`tags-${movieId}`);

    if (detailsContainer.style.display === 'none') {
        try {
            const tagsResponse = await fetch(`http://localhost:5000/api/movies/${movieId}/tags`);
            const tags = await tagsResponse.json();

            detailsContainer.innerHTML = tags.map(tag => `<span class="tag">${tag.tag}</span>`).join('');
            detailsContainer.style.display = 'block';
            button.innerHTML = 'Hide Details'; // Change button text
        } catch (error) {
            console.error('Error fetching movie details:', error);
            detailsContainer.innerHTML = '<p>Error loading tags</p>';
        }
    } else {
        detailsContainer.style.display = 'none';
        button.innerHTML = 'View Details'; // Change button text back
    }
}

// Make toggleMovieDetails accessible globally so the inline onclick can find it
window.toggleMovieDetails = toggleMovieDetails;

const displayMovies = (movies, containerId) => {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (movies && movies.length > 0) {
        movies.forEach(movie => {
            container.appendChild(createMovieCard(movie));
        });
    } else {
        container.innerHTML = '<p>No movies found.</p>';
    }
};

// API calls
const searchMovies = async () => {
    showLoadingSpinner();

    const query = document.getElementById('movie-search').value.trim();
    if (!query) {
        alert('Please enter a search term');
        hideLoadingSpinner();
        return;
    }

    try {
        const response = await fetch(`http://localhost:5000/api/movies/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        displayMovies(data, 'search-results');
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('search-results').innerHTML = '<p>Error searching movies</p>';
    } finally {
        hideLoadingSpinner();
    }
};

const getTopRatedMovies = async () => {
    const genre = document.getElementById('genre-filter').value;
    const minRatings = document.getElementById('min-ratings').value;

    showLoadingSpinner();

    try {
        const response = await fetch(`http://localhost:5000/api/movies/top-rated?genre=${encodeURIComponent(genre)}&min_ratings=${minRatings}`);
        const data = await response.json();
        displayMovies(data, 'top-rated-results');
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('top-rated-results').innerHTML = '<p>Error fetching top rated movies</p>';
    } finally {
        hideLoadingSpinner();
    }
};

// Tab switching logic
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons and tabs
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));

        // Add active class to clicked button and corresponding tab
        button.classList.add('active');
        document.getElementById(`${button.dataset.tab}-tab`).classList.add('active');

        // Clear movie details when switching tabs
        document.getElementById('movie-details').innerHTML = '';
    });
});

const getTopMoviesByYearRange = async () => {
    const startYear = document.getElementById('start-year-filter').value.trim();
    const endYear = document.getElementById('end-year-filter').value.trim();

    if (!startYear || !endYear || isNaN(startYear) || isNaN(endYear)) {
        alert('Please enter valid start and end years.');
        return;
    }

    if (Number(startYear) > Number(endYear)) {
        alert('Start year cannot be greater than end year.');
        return;
    }

    showLoadingSpinner();

    try {
        const response = await fetch(
            `http://localhost:5000/api/movies/top-year-range?start_year=${encodeURIComponent(
                startYear
            )}&end_year=${encodeURIComponent(endYear)}`
        );
        const data = await response.json();
        displayMovies(data, 'top-year-results');
    } catch (error) {
        console.error('Error fetching top movies by year range:', error);
        document.getElementById('top-year-results').innerHTML =
            '<p>Error fetching top movies by year range</p>';
    } finally {
        hideLoadingSpinner();
    }
};

// Event listener for "Apply Filters" button in the Top-Year tab
document
    .getElementById('apply-year-range-filters')
    .addEventListener('click', getTopMoviesByYearRange);

// Handle Similar Movies API Call
document.getElementById('find-similar').addEventListener('click', async () => {
    const movieTitle = document.getElementById('base-movie-search').value.trim();
    const rating = [...document.querySelectorAll('.star')]
        .filter(star => star.style.color === 'rgb(255, 215, 0)')
        .length;


    if (!movieTitle) {
        alert('Please enter a base movie title.');
        return;
    }


    showLoadingSpinner();


    try {
        const response = await fetch(`http://localhost:5000/api/movies/similar?movie=${encodeURIComponent(movieTitle)}&rating=${rating}`);
        const data = await response.json();
        displayMovies(data, 'similar-results');
    } catch (error) {
        console.error('Error fetching similar movies:', error);
        document.getElementById('similar-results').innerHTML = '<p>Error fetching similar movies.</p>';
    } finally {
        hideLoadingSpinner();
    }
});


const getTopMoviesByMonth = async () => {
    const month = document.getElementById('month-filter').value;

    if (!month) {
        alert('Please select a month.');
        return;
    }

    showLoadingSpinner();

    try {
        const response = await fetch(`http://localhost:5000/api/movies/top-month?month=${encodeURIComponent(month)}`);
        const data = await response.json();
        displayMovies(data, 'month-top-results');
    } catch (error) {
        console.error('Error fetching top movies by month:', error);
        document.getElementById('month-top-results').innerHTML =
            '<p>Error fetching top movies for the selected month</p>';
    } finally {
        hideLoadingSpinner();
    }
};

// Event listener for "Apply Filters" button in the Top Movies Per Month tab
document.getElementById('apply-month-filters').addEventListener('click', getTopMoviesByMonth);


const getRecommendationsByGenres = async () => {
    // Get all selected genres
    const selectedGenres = Array.from(document.querySelectorAll('#genres-container input:checked'))
        .map(input => input.value);

    if (selectedGenres.length === 0) {
        alert('Please select at least one genre.');
        return;
    }

    showLoadingSpinner();

    try {
        const response = await fetch(`http://localhost:5000/api/movies/recommend?genres=${encodeURIComponent(selectedGenres.join(','))}`);
        const data = await response.json();
        displayMovies(data, 'recommend-genres-results');
    } catch (error) {
        console.error('Error fetching recommendations by genres:', error);
        document.getElementById('recommend-genres-results').innerHTML =
            '<p>Error fetching recommendations for selected genres</p>';
    } finally {
        hideLoadingSpinner();
    }
};

// Event listener for "Get Recommendations" button in the Recommend by Genres tab
document
    .getElementById('recommend-genres-button')
    .addEventListener('click', getRecommendationsByGenres);


// Highlight Stars on Click
document.querySelectorAll('.star').forEach(star => {
    star.addEventListener('click', function () {
        const rating = parseInt(this.dataset.rating, 10);
        document.querySelectorAll('.star').forEach(s => {
            s.style.color = parseInt(s.dataset.rating, 10) <= rating ? '#ffd700' : '#564d4d';
        });
    });
});

async function toggleMovieDetails(movieId, button) {
    const detailsContainer = document.getElementById(`tags-${movieId}`);
    
    if (detailsContainer.style.display === 'none') {
        try {
            // Fetch tags
            const tagsResponse = await fetch(`http://localhost:5000/api/movies/${movieId}/tags`);
            const tags = await tagsResponse.json();

            // Fetch review graph
            const graphResponse = await fetch(`http://localhost:5000/api/movies/${movieId}/review-graph`);
            const graphUrl = graphResponse.url; // URL to the graph image

            // Populate details container
            detailsContainer.innerHTML = `
                ${tags.map(tag => `<span class="tag">${tag.tag}</span>`).join('')}
                <h3>Reviews Per Year</h3>
                <img src="${graphUrl}" alt="Number of Reviews Per Year" style="width: 100%; max-height: 400px;"/>
            `;
            detailsContainer.style.display = 'block';
            button.innerHTML = 'Hide Details'; // Change button text
        } catch (error) {
            console.error('Error fetching movie details:', error);
            detailsContainer.innerHTML = '<p>Error loading details</p>';
        }
    } else {
        detailsContainer.style.display = 'none';
        button.innerHTML = 'View Details'; // Change button text back
    }
}

// Event listeners
document.getElementById('search-button').addEventListener('click', searchMovies);
document.getElementById('movie-search').addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        searchMovies();
    }
});
document.getElementById('apply-filters').addEventListener('click', getTopRatedMovies);
