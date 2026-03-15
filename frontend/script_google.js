// Google-style Search Engine JavaScript

// ===== BACKGROUND IMAGE ROTATION =====
const backgroundImages = ['moteur2.jpg'];
let currentImageIndex = 0;

function rotateBackground() {
    currentImageIndex = (currentImageIndex + 1) % backgroundImages.length;
    document.documentElement.style.backgroundImage = `url('./${backgroundImages[currentImageIndex]}')`;
}

// Change background every 10 seconds (10000 milliseconds)
setInterval(rotateBackground, 10000);
// =====================================

const API_BASE = 'http://localhost:5000/api';
let currentPage = 1;
let currentQuery = '';
let currentCategory = ''; // web / images / videos / news etc
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
    const category = params.get('categorie') || '';
    currentCategory = category;
    
    if (query) {
        showResultsPage(query, category);
    } else {
        showHomePage();
    }
}

// Show home page (search hero)
function showHomePage() {

    document.querySelector('.google-container').innerHTML = `
        <div class="google-header">
            <div class="logo" translate="no">
                <span class="letter a" style="color: #EA4335;">A</span><span class="letter x" style="color: #FBBC05;">X</span><span class="letter o" style="color: #34A853;">O</span><span class="letter r" style="color: #4285F4;">R</span><span class="letter a2" style="color: #EA4335;">A</span>
            </div>
            <div class="google-nav">
                <a href="about.html">À propos</a>
                <a href="advanced.html">Recherche avancée</a>
                <a href="settings.html">Paramètres</a>
                <button class="login-btn" id="loginBtn" type="button">Se connecter</button>
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
                            placeholder="Rechercher sur le web"
                            autocomplete="off"
                        >
                        <button type="button" class="voice-search-btn" id="voiceSearchBtn" title="Search by voice">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 1a4 4 0 0 0-4 4v6a4 4 0 0 0 8 0V5a4 4 0 0 0-4-4z"/>
                                <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
                                <line x1="12" y1="19" x2="12" y2="23"/>
                                <line x1="8" y1="23" x2="16" y2="23"/>
                            </svg>
                        </button>
                        <button type="button" class="image-search-btn" id="imageSearchBtn" title="Search by image">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                <circle cx="9" cy="9" r="2"/>
                                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
                            </svg>
                        </button>
                        <input type="file" id="imageUpload" accept="image/*" style="display: none;">
                    </div>
                    <div id="homeAutocomplete" class="autocomplete-list"></div>
                </div>
                <div class="search-buttons">
                    <button type="submit" class="btn-search">Rechercher</button>
                    <button type="button" class="btn-lucky">J'ai de la chance</button>
                </div>
            </form>
            
        </div>
    `;

    // Set up login button
    const isLoggedIn = localStorage.getItem('loggedIn') === 'true';
    const loginBtn = document.getElementById('loginBtn');
    if (isLoggedIn) {
        loginBtn.textContent = 'Se déconnecter';
        loginBtn.addEventListener('click', () => {
            localStorage.removeItem('loggedIn');
            location.reload();
        });
    } else {
        loginBtn.textContent = 'Se connecter';
        loginBtn.addEventListener('click', () => {
            window.location.href = 'login.html';
        });
    }

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

    // Initialize voice and image search
    initVoiceSearch();
    initImageSearch();
}

// ===== VOICE SEARCH FUNCTIONALITY =====
function initVoiceSearch() {
    const voiceBtn = document.getElementById('voiceSearchBtn');
    const searchInput = document.getElementById('homeSearchInput');
    
    if (!voiceBtn) return;
    
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        voiceBtn.style.display = 'none';
        return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'fr-FR'; // French language
    
    let isListening = false;
    
    voiceBtn.addEventListener('click', () => {
        if (isListening) {
            recognition.stop();
            return;
        }
        
        recognition.start();
        isListening = true;
        voiceBtn.classList.add('listening');
        voiceBtn.title = 'Cliquez pour arrêter';
    });
    
    recognition.onstart = () => {
        console.log('Voice recognition started');
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        searchInput.value = transcript;
        searchInput.focus();
    };
    
    recognition.onend = () => {
        isListening = false;
        voiceBtn.classList.remove('listening');
        voiceBtn.title = 'Recherche vocale';
    };
    
    recognition.onerror = (event) => {
        console.error('Voice recognition error:', event.error);
        isListening = false;
        voiceBtn.classList.remove('listening');
    };
}

// ===== IMAGE SEARCH FUNCTIONALITY =====
function initImageSearch() {
    const imageBtn = document.getElementById('imageSearchBtn');
    const imageUpload = document.getElementById('imageUpload');
    const searchInput = document.getElementById('homeSearchInput');
    
    if (!imageBtn || !imageUpload) return;
    
    imageBtn.addEventListener('click', () => {
        imageUpload.click();
    });
    
    imageUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            // For now, just show the filename in the search box
            // In a real implementation, you would upload the image and get search results
            searchInput.value = `Recherche par image: ${file.name}`;
            searchInput.focus();
            
            // Here you would typically:
            // 1. Upload the image to your server
            // 2. Process it with image recognition
            // 3. Get search results based on the image content
            console.log('Image selected for search:', file.name);
        }
    });
}

// Initialize all new features when DOM is loaded
// document.addEventListener('DOMContentLoaded', () => {
//     initVoiceSearch();
//     initImageSearch();
// });

// Show results page
function showResultsPage(query, category = '') {
    currentQuery = query;
    currentCategory = category || '';
    document.querySelector('.google-container').innerHTML = `
        <div class="results-page">
            <!-- Header -->
            <div class="results-header">
                <div class="results-logo" translate="no">
                    <span class="letter a" style="color: #EA4335;">A</span><span class="letter x" style="color: #FBBC05;">X</span><span class="letter o" style="color: #34A853;">O</span><span class="letter r" style="color: #4285F4;">R</span><span class="letter a2" style="color: #EA4335;">A</span>
                </div>
                <div class="google-nav">
                    <a href="about.html">À propos</a>
                    <a href="advanced.html">Recherche avancée</a>
                    <a href="settings.html">Paramètres</a>
                    <button class="login-btn" id="resultsLoginBtn" type="button">Se connecter</button>
                </div>
                <div class="results-search-box">
                    <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                    </svg>
                    <input 
                        type="text" 
                        id="resultsSearchInput" 
                        value="${escapeHtml(query)}"
                        placeholder="Recherche"
                    >
                    <button type="button" id="resultsSearchBtn">Rechercher</button>
                </div>
            </div>

            <!-- Category tabs -->
            <div class="results-categories">
                <a href="?q=${encodeURIComponent(query)}" class="${currentCategory === '' ? 'active' : ''}">Web</a>
                <a href="?q=${encodeURIComponent(query)}&categorie=Images" class="${currentCategory.toLowerCase() === 'images' ? 'active' : ''}">Images</a>
                <a href="?q=${encodeURIComponent(query)}&categorie=Videos" class="${currentCategory.toLowerCase() === 'videos' ? 'active' : ''}">Videos</a>
                <a href="?q=${encodeURIComponent(query)}&categorie=PDF" class="${currentCategory.toLowerCase() === 'pdf' ? 'active' : ''}">PDF</a>
                <a href="?q=${encodeURIComponent(query)}&categorie=News" class="${currentCategory.toLowerCase() === 'news' ? 'active' : ''}">News</a>
            </div>
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

    // Set up login button on results page
    const isLoggedIn = localStorage.getItem('loggedIn') === 'true';
    const resultsLoginBtn = document.getElementById('resultsLoginBtn');
    if (isLoggedIn) {
        resultsLoginBtn.textContent = 'Se déconnecter';
        resultsLoginBtn.addEventListener('click', () => {
            localStorage.removeItem('loggedIn');
            location.reload();
        });
    } else {
        resultsLoginBtn.textContent = 'Se connecter';
        resultsLoginBtn.addEventListener('click', () => {
            window.location.href = 'login.html';
        });
    }

    // Set up results page events
    const resultsSearchInput = document.getElementById('resultsSearchInput');
    const resultsSearchBtn = document.getElementById('resultsSearchBtn');
    // adjust search input placeholder when category filter is active
    if (currentCategory) {
        resultsSearchInput.placeholder = `Search ${currentCategory}`;
    }

    resultsSearchBtn.addEventListener('click', () => {
        const newQuery = resultsSearchInput.value.trim();
        if (newQuery) {
            let url = `?q=${encodeURIComponent(newQuery)}`;
            if (currentCategory) {
                url += `&categorie=${encodeURIComponent(currentCategory)}`;
            }
            window.location.href = url;
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
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}&limit=50`);

        if (!response.ok) throw new Error('Search failed');
        const data = await response.json();

        allResults = data.results || [];
        const totalResults = data.total_results || 0;
        const searchTime = data.search_time || 0;

        // Filter results based on category
        if (currentCategory) {
            const cat = currentCategory.toLowerCase();
            if (cat === 'images') {
                allResults = allResults.filter(r => r.categorie && r.categorie.toLowerCase().includes('image'));
            } else if (cat === 'videos') {
                allResults = allResults.filter(r => r.categorie && r.categorie.toLowerCase().includes('video'));
            } else if (cat === 'pdf') {
                allResults = allResults.filter(r => r.categorie && r.categorie.toLowerCase() === 'pdf');
            } else if (cat === 'news') {
                allResults = allResults.filter(r => r.categorie && r.categorie.toLowerCase().includes('news'));
            }
            // For 'web' or empty, show all
        }

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

        // media preview for image/video/pdf categories
        let mediaHtml = '';
        if (result.categorie) {
            const cat = result.categorie.toLowerCase();
            if (cat === 'image' || cat === 'images') {
                mediaHtml = `<div class="result-media"><img src="${escapeHtml(result.url)}" alt="${escapeHtml(result.titre || '')}" class="result-image" /></div>`;
            } else if (cat === 'video' || cat === 'videos') {
                mediaHtml = `<div class="result-media"><video controls width="320" src="${escapeHtml(result.url)}" class="result-video"></video></div>`;
            } else if (cat === 'pdf') {
                mediaHtml = `<div class="result-media"><iframe src="${escapeHtml(result.url)}" width="320" height="240" class="result-pdf"></iframe></div>`;
            }
        }

        // show category label
        let categoryLabel = '';
        if (result.categorie) {
            categoryLabel = `<div class="result-category">${escapeHtml(result.categorie)}</div>`;
        }

        resultEl.innerHTML = `
            ${mediaHtml}
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
                ${categoryLabel}
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
        // Fallback to predefined suggestions
        loadFallbackSuggestions(query, container, onSelect);
    }
}

// Fallback suggestions from indexed elements
async function loadFallbackSuggestions(query, container, onSelect) {
    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}&limit=5`);
        if (response.ok) {
            const data = await response.json();
            const suggestions = data.results ? data.results.map(r => r.titre || r.title || r.url).slice(0, 5) : [];
            if (suggestions.length > 0) {
                container.innerHTML = '';
                suggestions.forEach(suggestion => {
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
        } else {
            // If search API also fails, use predefined
            const words = ["google", "github", "javascript", "python", "machine learning"];
            const filtered = words.filter(word => word.toLowerCase().includes(query.toLowerCase()) && query !== "");
            if (filtered.length > 0) {
                container.innerHTML = '';
                filtered.forEach(word => {
                    const item = document.createElement('div');
                    item.className = 'autocomplete-item';
                    item.innerHTML = `
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.35-4.35"></path>
                        </svg>
                        <span>${escapeHtml(word)}</span>
                    `;
                    item.addEventListener('click', () => {
                        document.getElementById('homeSearchInput').value = word;
                        onSelect(word);
                    });
                    container.appendChild(item);
                });
                container.classList.add('show');
            } else {
                container.classList.remove('show');
            }
        }
    } catch (e) {
        console.error('Fallback autocomplete error:', e);
        container.classList.remove('show');
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
