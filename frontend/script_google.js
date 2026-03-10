// Google-style Search Engine JavaScript

const API_BASE = 'http://localhost:5000/api';
let currentPage = 1;
let currentQuery = '';
let allResults = [];

// Elements
const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const clearBtn = document.getElementById('clearBtn');
const autocompleteList = document.getElementById('autocompleteList');
const resultsContainer = document.getElementById('resultsContainer');
const statsBar = document.getElementById('statsBar');
const paginationContainer = document.getElementById('paginationContainer');
const pageTitle = document.getElementById('pageTitle');

// Initialize
function init() {
    // Check if we're on results page
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q');
    
    if (query) {
        showResultsPage(query);
    } else {
        showHomePage();
    }
}

// Show home page (search hero)
function showHomePage() {
    document.querySelector('.google-container').innerHTML = `
        <div class="google-header">
            <div class="logo">
                <span class="letter s">S</span><span class="letter e">e</span><span class="letter a">a</span>
                <span class="letter r">r</span><span class="letter c">c</span><span class="letter h">h</span>
                <span class="letter m">M</span><span class="letter i">i</span><span class="letter n">n</span>
                <span class="letter e">e</span>
            </div>
            <div class="google-nav">
                <a href="#about">About</a>
                <a href="#advanced">Advanced Search</a>
                <a href="#settings">Settings</a>
            </div>
        </div>
        <div class="search-hero">
            <form id="homeSearchForm" class="search-form">
                <div class="search-box-wrapper">
                    <div class="search-box">
                        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.35-4.35"></path>
                        </svg>
                        <input 
                            type="text" 
                            id="homeSearchInput" 
                            placeholder="Search the web"
                            autocomplete="off"
                        >
                    </div>
                    <div id="homeAutocomplete" class="autocomplete-list"></div>
                </div>
                <div class="search-buttons">
                    <button type="submit" class="btn-search">Search</button>
                    <button type="button" class="btn-lucky">I'm Feeling Lucky</button>
                </div>
            </form>
        </div>
    `;

    const homeSearchForm = document.getElementById('homeSearchForm');
    const homeSearchInput = document.getElementById('homeSearchInput');
    const homeAutocomplete = document.getElementById('homeAutocomplete');
    const luckButton = homeSearchForm.querySelector('.btn-lucky');

    // Search form submission
    homeSearchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = homeSearchInput.value.trim();
        if (query) {
            window.location.href = `?q=${encodeURIComponent(query)}`;
        }
    });

    // Lucky button
    luckButton.addEventListener('click', (e) => {
        e.preventDefault();
        const query = homeSearchInput.value.trim();
        if (query) {
            performLuckySearch(query);
        }
    });

    // Autocomplete
    homeSearchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        if (query.length > 1) {
            loadAutocompleteSuggestions(query, homeAutocomplete, () => {
                window.location.href = `?q=${encodeURIComponent(query)}`;
            });
        } else {
            homeAutocomplete.classList.remove('show');
        }
    });
}

// Show results page
function showResultsPage(query) {
    currentQuery = query;
    document.querySelector('.google-container').innerHTML = `
        <div class="results-page">
            <!-- Header -->
            <div class="results-header">
                <div class="results-logo">SearchMine</div>
                <div class="results-search-box">
                    <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                    </svg>
                    <input 
                        type="text" 
                        id="resultsSearchInput" 
                        value="${escapeHtml(query)}"
                        placeholder="Search"
                    >
                    <button type="button" id="resultsSearchBtn">Search</button>
                </div>
                <div class="results-nav">
                    <a href="#tools">Tools</a>
                </div>
            </div>

            <!-- Results Container -->
            <div class="results-container">
                <div id="statsBar" class="stats-bar"></div>
                <div id="featuredSnippet" class="featured-snippet" style="display: none;">
                    <div class="featured-label">Featured Snippet</div>
                    <h2 id="snippetTitle"></h2>
                    <p id="snippetContent"></p>
                    <a id="snippetUrl" class="snippet-url" target="_blank"></a>
                </div>
                <div id="resultsContainer" class="google-results"></div>
                <div id="paginationContainer" class="pagination"></div>
            </div>

            <!-- Footer -->
            <div class="google-footer">
                <div class="footer-content">
                    <div>
                        <a href="#privacy">Privacy</a>
                        <a href="#terms">Terms</a>
                        <a href="#settings">Settings</a>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Set up results page events
    const resultsSearchInput = document.getElementById('resultsSearchInput');
    const resultsSearchBtn = document.getElementById('resultsSearchBtn');

    resultsSearchBtn.addEventListener('click', () => {
        const newQuery = resultsSearchInput.value.trim();
        if (newQuery) {
            window.location.href = `?q=${encodeURIComponent(newQuery)}`;
        }
    });

    resultsSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            resultsSearchBtn.click();
        }
    });

    // Load search results
    loadSearchResults(query, 1);
}

// Load search results from API
async function loadSearchResults(query, page = 1) {
    currentPage = page;
    const resultsContainer = document.getElementById('resultsContainer');
    const statsBar = document.getElementById('statsBar');
    const featuredSnippetDiv = document.getElementById('featuredSnippet');

    resultsContainer.innerHTML = '<div class="loading"></div> Searching...';
    statsBar.textContent = '';

    try {
        // Main search
        const offset = (page - 1) * 10;
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}&limit=10`);

        if (!response.ok) throw new Error('Search failed');
        const data = await response.json();

        allResults = data.results || [];
        const totalResults = data.total_results || 0;
        const searchTime = data.search_time || 0;

        statsBar.textContent = `About ${totalResults} results (${searchTime.toFixed(3)}s)`;

        // Try to get featured snippet
        try {
            const snippetResponse = await fetch(`${API_BASE}/features/featured-snippet`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, documents: allResults.slice(0, 3) })
            });

            if (snippetResponse.ok) {
                const snippetData = await snippetResponse.json();
                if (snippetData.snippet) {
                    displayFeaturedSnippet(snippetData.snippet, query);
                }
            }
        } catch (e) {
            console.log('Featured snippet fetch failed:', e);
        }

        // Display results
        if (allResults.length === 0) {
            resultsContainer.innerHTML = `
                <p style="color: var(--text-secondary); text-align: center; padding: 2rem;">
                    No results found for "<strong>${escapeHtml(query)}</strong>"
                </p>
            `;
        } else {
            displayResults(allResults);
        }

        // Pagination
        displayPagination(totalResults, page);

    } catch (error) {
        console.error('Error:', error);
        resultsContainer.innerHTML = `
            <p style="color: var(--text-secondary);">
                Error loading results: ${error.message}
            </p>
        `;
    }
}

// Display featured snippet
function displayFeaturedSnippet(snippet, query) {
    const div = document.getElementById('featuredSnippet');
    if (snippet && snippet.text) {
        document.getElementById('snippetTitle').textContent = snippet.title || query;
        document.getElementById('snippetContent').textContent = snippet.text;
        if (snippet.source_url) {
            const urlElem = document.getElementById('snippetUrl');
            urlElem.href = snippet.source_url;
            urlElem.textContent = new URL(snippet.source_url).hostname;
        }
        div.style.display = 'block';
    }
}

// Display results
function displayResults(results) {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = '';

    results.forEach(result => {
        const resultEl = document.createElement('div');
        resultEl.className = 'result-item';
        
        const urlObj = new URL(result.url || 'https://example.com');
        const displayUrl = urlObj.host + (urlObj.pathname !== '/' ? urlObj.pathname : '');
        
        resultEl.innerHTML = `
            <div class="result-url">
                <span class="result-url-display">${escapeHtml(displayUrl)}</span>
            </div>
            <a href="${escapeHtml(result.url || '#')}" class="result-title" target="_blank">
                ${escapeHtml(result.titre || result.title || 'Sans titre')}
            </a>
            <div class="result-snippet">
                ${escapeHtml((result.snippet || result.description || result.contenu || '').substring(0, 160))}...
            </div>
            <div class="result-meta">
                Relevance: ${result.relevance_score ? result.relevance_score.toFixed(2) : 'N/A'}
            </div>
        `;

        resultsContainer.appendChild(resultEl);
    });
}

// Display pagination
function displayPagination(totalResults, currentPage) {
    const paginationContainer = document.getElementById('paginationContainer');
    paginationContainer.innerHTML = '';

    const totalPages = Math.ceil(totalResults / 10);
    const maxButtons = 10;

    if (totalPages <= 1) return;

    // Previous button
    if (currentPage > 1) {
        const prevBtn = createPaginationBtn('← Previous', currentPage - 1);
        paginationContainer.appendChild(prevBtn);
    }

    // Page numbers
    let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);

    if (endPage - startPage < maxButtons - 1) {
        startPage = Math.max(1, endPage - maxButtons + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        const btn = createPaginationBtn(i, i);
        if (i === currentPage) {
            btn.classList.add('active');
        }
        paginationContainer.appendChild(btn);
    }

    // Next button
    if (currentPage < totalPages) {
        const nextBtn = createPaginationBtn('Next →', currentPage + 1);
        paginationContainer.appendChild(nextBtn);
    }
}

function createPaginationBtn(text, page) {
    const btn = document.createElement('button');
    btn.className = 'pagination-item';
    btn.textContent = text;
    btn.addEventListener('click', () => {
        loadSearchResults(currentQuery, page);
        window.scrollTo(0, 0);
    });
    return btn;
}

// Autocomplete suggestions
async function loadAutocompleteSuggestions(query, container, onSelect) {
    try {
        // Try to get suggestions from API
        const response = await fetch(`${API_BASE}/features/suggestions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        if (!response.ok) throw new Error('Suggestions failed');
        const data = await response.json();
        const suggestions = data.suggestions || [];

        if (suggestions.length > 0) {
            container.innerHTML = '';
            suggestions.slice(0, 5).forEach(suggestion => {
                const item = document.createElement('div');
                item.className = 'autocomplete-item';
                item.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                    </svg>
                    <span>${escapeHtml(suggestion)}</span>
                `;
                item.addEventListener('click', () => {
                    document.getElementById('homeSearchInput').value = suggestion;
                    onSelect(suggestion);
                });
                container.appendChild(item);
            });
            container.classList.add('show');
        } else {
            container.classList.remove('show');
        }
    } catch (e) {
        console.error('Autocomplete error:', e);
    }
}

// Lucky search
async function performLuckySearch(query) {
    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}&limit=1`);

        if (!response.ok) throw new Error('Search failed');
        const data = await response.json();

        if (data.results && data.results.length > 0) {
            window.location.href = data.results[0].url;
        } else {
            window.location.href = `?q=${encodeURIComponent(query)}`;
        }
    } catch (error) {
        console.error('Lucky search error:', error);
        window.location.href = `?q=${encodeURIComponent(query)}`;
    }
}

// Utility functions
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
