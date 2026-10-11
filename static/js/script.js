let searchTimeout;

document.getElementById("movieSearch").addEventListener("input", function (e) {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();

    const resultsContainer = document.getElementById("searchResults");

    if (query.length < 2) {
        resultsContainer.classList.add("hidden");
        return;
    }

    searchTimeout = setTimeout(() => {
        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.results.length > 0) {
                    resultsContainer.innerHTML = data.results.map(movie => `
                        <div class="search-result-item" onclick="selectMovie('${movie.title.replace(/'/g, "\\'")}')">
                            <div class="search-result-title">${movie.title}</div>
                            <div class="search-result-genres">${movie.genres.replace(/\|/g, ' • ')}</div>
                        </div>
                    `).join("");
                    resultsContainer.classList.remove("hidden");
                } else {
                    resultsContainer.innerHTML = `
                        <div class="search-result-item">
                            <div class="search-result-title" style="color: var(--text-muted)">No movies found</div>
                        </div>
                    `;
                    resultsContainer.classList.remove("hidden");
                }
            })
            .catch(() => {
                resultsContainer.classList.add("hidden");
            });
    }, 300);
});

document.getElementById("movieSearch").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        getRecommendations();
    }
});

document.addEventListener("click", function (e) {
    const searchContainer = document.querySelector(".search-container");
    const resultsContainer = document.getElementById("searchResults");
    if (!searchContainer.contains(e.target)) {
        resultsContainer.classList.add("hidden");
    }
});

function selectMovie(title) {
    document.getElementById("movieSearch").value = title;
    document.getElementById("searchResults").classList.add("hidden");
    getRecommendations();
}

async function getRecommendations() {
    const movie = document.getElementById("movieSearch").value.trim();
    const results = document.getElementById("recommendations");
    const loading = document.getElementById("loading");
    const resultTitle = document.getElementById("resultTitle");
    const resultsSection = document.getElementById("results");

    if (!movie) {
        alert("Please select a movie.");
        return;
    }

    loading.classList.remove("hidden");
    results.innerHTML = "";
    resultTitle.innerText = "Recommended Movies";
    resultsSection.classList.add("hidden");

    try {
        const response = await fetch("/api/recommend", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ movie: movie, number: 10 })
        });

        const data = await response.json();
        loading.classList.add("hidden");

        if (data.error) {
            results.innerHTML = `
                <div class="error-message">
                    ${data.error}
                </div>
            `;
            resultsSection.classList.remove("hidden");
            return;
        }

        resultTitle.innerText = `Movies Similar to ${data.selected_movie}`;

        if (!data.recommendations || data.recommendations.length === 0) {
            results.innerHTML = `
                <div class="error-message">
                    No recommendations found.
                </div>
            `;
            resultsSection.classList.remove("hidden");
            return;
        }

        data.recommendations.forEach((movie, index) => {
            const card = document.createElement("div");
            card.className = "movie-card";
            card.onclick = () => {
                window.location.href = `/movie/${movie.movieId}`;
            };

            const genres = movie.genres.replaceAll("|", " • ");
            const posterHtml = movie.poster_url
                ? `<img src="${movie.poster_url}" alt="${movie.title} poster" class="poster" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">` +
                  `<div class="poster-placeholder" style="display:none;"><span>No Poster</span></div>`
                : `<div class="poster-placeholder"><span>No Poster</span></div>`;

            card.innerHTML = `
                ${posterHtml}
                <div class="card-content">
                    <div class="rank">#${index + 1}</div>
                    <h3>${movie.title}</h3>
                    <p class="genres">${genres}</p>
                    <div class="movie-info">
                        <span>⭐ ${movie.rating}/5</span>
                        <span>👥 ${movie.rating_count}</span>
                    </div>
                    <div class="match">
                        <span>🎯 ${movie.similarity}% Match</span>
                    </div>
                    <div class="card-footer">
                        <span class="view-btn">View Details →</span>
                    </div>
                </div>
            `;

            results.appendChild(card);
        });

        const relatedSection = document.getElementById("relatedSection");
        const relatedMovies = document.getElementById("relatedMovies");
        const relatedTitle = document.getElementById("relatedTitle");

        relatedTitle.innerText = `Related to ${data.selected_movie}`;
        relatedMovies.innerHTML = "";

        data.recommendations.forEach((movie, index) => {
            const card = document.createElement("div");
            card.className = "related-movie-card";
            card.onclick = () => {
                window.location.href = `/movie/${movie.movieId}`;
            };

            const genres = movie.genres.replaceAll("|", " • ");
            const posterHtml = movie.poster_url
                ? `<img src="${movie.poster_url}" alt="${movie.title} poster" class="poster" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">` +
                  `<div class="poster-placeholder" style="display:none;"><span>No Poster</span></div>`
                : `<div class="poster-placeholder"><span>No Poster</span></div>`;

            card.innerHTML = `
                ${posterHtml}
                <div class="card-content">
                    <div class="related-rank">#${index + 1}</div>
                    <h4>${movie.title}</h4>
                    <p class="related-genres">${genres}</p>
                    <div class="related-movie-info">
                        <span>⭐ ${movie.rating}/5</span>
                    </div>
                    <div class="related-match">
                        <span>🎯 ${movie.similarity}% Match</span>
                    </div>
                </div>
            `;

            relatedMovies.appendChild(card);
        });

        relatedSection.classList.remove("hidden");
        relatedSection.scrollIntoView({ behavior: "smooth", block: "nearest" });

    } catch (error) {
        console.error("Recommendation error:", error);
        loading.classList.add("hidden");
        results.innerHTML = `
            <div class="error-message">
                Something went wrong. Please try again.
            </div>
        `;
        resultsSection.classList.remove("hidden");
    }
}
