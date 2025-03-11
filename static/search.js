// ==========================
// SEARCH FUNCTIONALITY
// ==========================

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchButton = document.querySelector('.search-button');
    const searchPopover = document.getElementById('search-box');
    const searchInput = document.getElementById('search-input');
    const searchForm = document.querySelector('.search-input-container');
    const searchResultsContainer = document.querySelector('.search-results-container');
    const closeSearchButton = document.querySelector('#search-box .close-btn');
    
    // Search Data - Replace with your actual content or fetch from an API
    const searchData = [
        {
            category: 'Blog',
            items: [
                {
                    title: 'Introduction to Quantum Computing',
                    url: '/blog/quantum-computing-intro',
                    date: 'March 5, 2025',
                    snippet: 'An in-depth look at the principles of quantum computing and how it's changing the landscape of modern technology.'
                },
                {
                    title: 'Machine Learning Fundamentals',
                    url: '/blog/machine-learning-fundamentals',
                    date: 'February 18, 2025',
                    snippet: 'Understanding the basic concepts and applications of machine learning in today\'s digital world.'
                }
                // Add more blog posts here
            ]
        },
        {
            category: 'Research',
            items: [
                {
                    title: 'Advancements in Neural Networks',
                    url: '/research/neural-networks',
                    date: 'January 30, 2025',
                    snippet: 'Exploring recent breakthroughs in neural network architectures and applications.'
                },
                {
                    title: 'Computational Biology Research',
                    url: '/research/computational-biology',
                    date: 'December 12, 2024',
                    snippet: 'How computational methods are revolutionizing biological research and medical discoveries.'
                }
                // Add more research items here
            ]
        }
        // Add more categories as needed
    ];

    // Open search popover
    function openSearch() {
        searchPopover.togglePopover(true);
        // Focus on search input after a brief delay to ensure the popover is visible
        setTimeout(() => {
            searchInput.focus();
        }, 100);
    }

    // Close search popover
    function closeSearch() {
        searchPopover.togglePopover(false);
        // Clear search input and results
        searchInput.value = '';
        clearSearchResults();
    }

    // Clear search results
    function clearSearchResults() {
        searchResultsContainer.classList.remove('visible');
        searchResultsContainer.innerHTML = '';
    }

    // Generate search results HTML
    function generateResultsHTML(results) {
        if (results.length === 0) {
            return `
                <div class="no-results">
                    <p>No results found. Try different keywords.</p>
                </div>
            `;
        }

        let html = '<div class="search-results">';
        
        // Group results by category
        const groupedResults = {};
        
        results.forEach(result => {
            if (!groupedResults[result.category]) {
                groupedResults[result.category] = [];
            }
            groupedResults[result.category].push(result);
        });
        
        // Generate HTML for each category
        for (const category in groupedResults) {
            html += `
                <div class="result-section">
                    <h3>${category}</h3>
                    <ul>
            `;
            
            groupedResults[category].forEach(item => {
                html += `
                    <li>
                        <a href="${item.url}" class="result-item">
                            <div class="result-title">${item.title}</div>
                            <div class="result-meta">
                                <span class="result-category">${category}</span>
                                <span class="result-date">${item.date}</span>
                            </div>
                            <div class="result-snippet">${highlightSearchTerms(item.snippet, searchInput.value)}</div>
                        </a>
                    </li>
                `;
            });
            
            html += `
                    </ul>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

    // Highlight search terms in snippet
    function highlightSearchTerms(snippet, searchTerm) {
        if (!searchTerm.trim()) return snippet;
        
        const terms = searchTerm.trim().split(/\s+/);
        let highlightedSnippet = snippet;
        
        terms.forEach(term => {
            if (term.length < 3) return; // Skip very short terms
            
            const regex = new RegExp(`(${escapeRegExp(term)})`, 'gi');
            highlightedSnippet = highlightedSnippet.replace(regex, '<mark>$1</mark>');
        });
        
        return highlightedSnippet;
    }

    // Escape special regex characters
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Perform search
    function performSearch(query) {
        clearSearchResults();
        
        if (!query.trim()) {
            return;
        }
        
        const results = [];
        const searchTerms = query.toLowerCase().trim().split(/\s+/);
        
        // Search through all items
        searchData.forEach(category => {
            category.items.forEach(item => {
                // Check if item matches search query
                const titleMatches = searchTerms.some(term => 
                    item.title.toLowerCase().includes(term)
                );
                
                const snippetMatches = searchTerms.some(term => 
                    item.snippet.toLowerCase().includes(term)
                );
                
                if (titleMatches || snippetMatches) {
                    results.push({
                        ...item,
                        category: category.category
                    });
                }
            });
        });
        
        // Display results
        if (results.length > 0 || query.trim()) {
            searchResultsContainer.innerHTML = generateResultsHTML(results);
            searchResultsContainer.classList.add('visible');
        }
    }

    // Event Listeners
    if (searchButton) {
        searchButton.addEventListener('click', (e) => {
            e.preventDefault();
            openSearch();
        });
    }

    if (closeSearchButton) {
        closeSearchButton.addEventListener('click', (e) => {
            e.preventDefault();
            closeSearch();
        });
    }

    // Close search when clicking outside
    document.addEventListener('click', (e) => {
        if (searchPopover.matches(':popover-open') && 
            !searchPopover.contains(e.target) && 
            e.target !== searchButton) {
            closeSearch();
        }
    });

    // Handle search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            performSearch(searchInput.value);
        });
    }

    // Handle input changes (live search)
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            // Debounced search for better performance
            clearTimeout(searchInput.searchTimeout);
            searchInput.searchTimeout = setTimeout(() => {
                performSearch(searchInput.value);
            }, 300);
        });

        // Handle keyboard navigation for the search popover
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeSearch();
            }
        });
    }

    // Initialize keyboard shortcut for search (Ctrl+K or Command+K)
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchPopover.matches(':popover-open')) {
                closeSearch();
            } else {
                openSearch();
            }
        }
    });

    // Handle popover API fallback for browsers that don't support it
    if (typeof HTMLElement.prototype.togglePopover !== 'function') {
        // Simple polyfill for the togglePopover method
        HTMLElement.prototype.togglePopover = function(force) {
            if (force === true || (force !== false && this.style.display !== 'flex')) {
                this.style.display = 'flex';
                this.setAttribute('popover-open', '');
            } else {
                this.style.display = 'none';
                this.removeAttribute('popover-open');
            }
        };
        
        // Initialize popover state
        if (searchPopover) {
            searchPopover.style.display = 'none';
        }
    }

    // Additional functionality for mobile devices
    // Add tap outside to close on mobile
    if ('ontouchstart' in window) {
        document.addEventListener('touchstart', (e) => {
            if (searchPopover.matches(':popover-open') && 
                !searchPopover.contains(e.target) && 
                e.target !== searchButton) {
                closeSearch();
            }
        });
    }
});

// ==========================
// SEARCH ANALYTICS TRACKING
// ==========================

// Track search queries (optional)
function trackSearchQuery(query) {
    // Replace with your analytics tracking code
    if (typeof gtag === 'function') {
        gtag('event', 'search', {
            search_term: query
        });
    } else if (typeof ga === 'function') {
        ga('send', 'event', 'Search', 'query', query);
    }
    
    // You can also implement custom tracking logic here
    console.log('Search query:', query);
}

// ==========================
// ADVANCED SEARCH FEATURES
// ==========================

// Function to get search suggestions (can be expanded based on your needs)
function getSearchSuggestions(query) {
    // This could be connected to an API endpoint for dynamic suggestions
    const commonSearches = [
        'machine learning',
        'artificial intelligence',
        'neural networks',
        'deep learning',
        'data science',
        'quantum computing',
        'blockchain'
    ];
    
    return commonSearches.filter(term => 
        term.toLowerCase().includes(query.toLowerCase())
    );
}

// Add recent searches functionality (using localStorage)
const recentSearches = {
    add: function(query) {
        if (!query.trim()) return;
        
        let searches = this.get();
        
        // Add the new search and remove duplicates
        searches = [query, ...searches.filter(item => item !== query)];
        
        // Keep only the 5 most recent searches
        searches = searches.slice(0, 5);
        
        localStorage.setItem('recentSearches', JSON.stringify(searches));
    },
    
    get: function() {
        const searches = localStorage.getItem('recentSearches');
        return searches ? JSON.parse(searches) : [];
    },
    
    clear: function() {
        localStorage.removeItem('recentSearches');
    }
};
