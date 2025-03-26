// ==========================
// SEARCH FUNCTIONALITY
// ==========================

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const searchButton = document.querySelector(".search-button");
  const searchPopover = document.getElementById("search-box");
  const searchInput = document.getElementById("search-input");
  const searchForm = document.getElementById("search-form");
  const searchResultsContainer = document.getElementById(
    "search-results-container",
  );
  const searchResults = document.getElementById("search-results");
  const closeSearchButton = document.querySelector("#search-box .close-btn");

  // MiniSearch instance
  let miniSearch = null;
  let searchDocuments = []; // Store the full documents for context extraction

  // Determine current page depth for URL correction
  function getPathDepth() {
    const path = window.location.pathname;
    // Count the number of directory levels (slashes) from the root
    const pathParts = path.split("/").filter((part) => part.length > 0);
    return (
      pathParts.length - (path.endsWith("/") || path.endsWith(".html") ? 1 : 0)
    );
  }

  // Correct URL based on current page depth
  function correctUrl(url) {
    // If url is already absolute (starts with / or http), return as is
    if (url.startsWith("/") || url.startsWith("http")) {
      return url;
    }

    const pathDepth = getPathDepth();
    // If we're in a subdirectory, we need to prefix with ../ for each level
    if (pathDepth > 0) {
      return "../".repeat(pathDepth) + url;
    }

    return url;
  }

  // Initialize MiniSearch with the search index
  function initializeSearch() {
    // Create a new MiniSearch instance
    miniSearch = new MiniSearch({
      fields: ["title", "content", "description"], // fields to index for full-text search
      storeFields: [
        "title",
        "url",
        "content",
        "description",
        "type",
        "category",
        "date",
      ], // Store full content for snippets
      searchOptions: {
        boost: { title: 2, description: 1.5, content: 1 }, // boost factors for fields
        fuzzy: 0.2, // fuzzy search with edit distance of 0.2
        prefix: true, // match by prefix
        combineWith: "AND", // require all terms to match
      },
    });

    // Load the search index
    fetch("/static/search-index.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((documents) => {
        // Store documents for context extraction
        searchDocuments = documents;

        // Add documents to the index
        miniSearch.addAll(documents);
      })
      .catch((error) => {
        console.error("Error loading search index:", error);
      });
  }

  // Initialize search on page load
  initializeSearch();

  // Open search popover
  function openSearch() {
    if (typeof searchPopover.showPopover === "function") {
      searchPopover.showPopover();
    } else {
      togglePopover(searchPopover, true);
    }

    // Focus on search input after a brief delay
    setTimeout(() => {
      searchInput.focus();
    }, 100);
  }

  // Close search popover
  function closeSearch() {
    if (typeof searchPopover.hidePopover === "function") {
      searchPopover.hidePopover();
    } else {
      togglePopover(searchPopover, false);
    }

    // Clear search input and results
    searchInput.value = "";
    clearSearchResults();
  }

  // Clear search results
  function clearSearchResults() {
    searchResultsContainer.classList.remove("visible");
    searchResults.innerHTML = "";
  }

  // Format type name for display
  function formatTypeForDisplay(type) {
    if (!type) return "Other";

    return type
      .replace(/-/g, " ")
      .split(" ")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  // Perform search
  function performSearch(query) {
    if (!miniSearch || !query.trim()) {
      clearSearchResults();
      return;
    }

    // Save recent search
    recentSearches.add(query);

    // Search the index - get raw results from MiniSearch
    const results = miniSearch.search(query);

    if (results.length > 0) {
      displayResults(results, query);
    } else {
      displayNoResults();
    }
  }

  // Display search results
  function displayResults(results, query) {
    // Group results by type
    const groupedResults = {};

    results.forEach((result) => {
      const type = result.type || "other";
      if (!groupedResults[type]) {
        groupedResults[type] = [];
      }
      groupedResults[type].push(result);
    });

    let html = "";

    // Generate HTML for each type
    for (const type in groupedResults) {
      const displayType = formatTypeForDisplay(type);

      html += `
                <div class="result-section">
                    <h3>${displayType}</h3>
                    <ul>
            `;

      groupedResults[type].forEach((item) => {
        // Get context snippets - multiple snippets showing the search term in context
        const snippets = findMatchingSnippets(item, query);
        const category = item.category
          ? `<span class="result-category">${item.category}</span>`
          : "";
        const date = item.date
          ? `<span class="result-date">${item.date}</span>`
          : "";

        // Apply URL correction based on current page depth
        const correctedUrl = correctUrl(item.url);

        html += `
                    <li>
                        <a href="${correctedUrl}" class="result-item">
                            <div class="result-title">${highlightSearchTerms(item.title, query)}</div>
                            <div class="result-meta">
                                ${category}
                                ${date}
                            </div>
                `;

        // Add snippets if available
        if (snippets.length > 0) {
          html += `<div class="result-snippet">`;
          // Add each snippet with appropriate highlighting
          snippets.forEach((snippet, index) => {
            if (index > 0) {
              html += `<span class="snippet-separator">...</span>`;
            }
            html += `${snippet}`;
          });
          html += `</div>`;
        } else {
          // Fallback to description if no snippets
          html += `<div class="result-snippet">${highlightSearchTerms(item.description || "", query)}</div>`;
        }

        html += `
                        </a>
                    </li>
                `;
      });

      html += `
                    </ul>
                </div>
            `;
    }

    searchResults.innerHTML = html;
    searchResultsContainer.classList.add("visible");
  }

  // Display no results message
  function displayNoResults() {
    searchResults.innerHTML = `
            <div class="no-results">
                <p>No results found. Try different keywords.</p>
            </div>
        `;
    searchResultsContainer.classList.add("visible");
  }

  // Find multiple matching snippets in content
  function findMatchingSnippets(item, query) {
    const content = item.content || "";
    if (!content || content.length === 0) {
      return [];
    }

    const queryTerms = query
      .toLowerCase()
      .split(/\s+/)
      .filter((term) => term.length > 2);
    if (queryTerms.length === 0) {
      return [];
    }

    const snippets = [];
    const snippetLength = 100; // Characters before and after the match

    // Find snippets for each search term
    queryTerms.forEach((term) => {
      let startPos = 0;
      const maxSnippets = 2; // Max snippets per term
      let snippetCount = 0;

      while (startPos < content.length && snippetCount < maxSnippets) {
        const termPos = content.toLowerCase().indexOf(term, startPos);
        if (termPos === -1) break;

        const snippetStart = Math.max(0, termPos - snippetLength);
        const snippetEnd = Math.min(
          content.length,
          termPos + term.length + snippetLength,
        );

        // Extract the snippet
        let snippet = content.substring(snippetStart, snippetEnd);

        // Add ellipsis if needed
        if (snippetStart > 0) {
          snippet = "..." + snippet;
        }

        if (snippetEnd < content.length) {
          snippet = snippet + "...";
        }

        // Highlight the term in the snippet
        snippet = highlightSearchTerms(snippet, term);

        // Add to snippets if not a duplicate
        if (!snippets.includes(snippet)) {
          snippets.push(snippet);
          snippetCount++;
        }

        // Move start position for next search
        startPos = termPos + term.length;
      }
    });

    return snippets.slice(0, 3); // Limit to 3 snippets max per result
  }

  // Highlight search terms in text
  function highlightSearchTerms(text, searchTerm) {
    if (!searchTerm || !text) return text;

    // Get all individual terms
    const terms =
      typeof searchTerm === "string"
        ? searchTerm
            .toLowerCase()
            .split(/\s+/)
            .filter((term) => term.length > 2)
        : [searchTerm.toLowerCase()];

    if (terms.length === 0) return text;

    let highlightedText = text;

    // Highlight each term
    terms.forEach((term) => {
      // Create a regex that matches the whole word containing the term
      const regex = new RegExp(
        `(\\b\\w*${escapeRegExp(term)}\\w*\\b|${escapeRegExp(term)})`,
        "gi",
      );
      highlightedText = highlightedText.replace(regex, "<mark>$1</mark>");
    });

    return highlightedText;
  }

  // Escape special regex characters
  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  // Polyfill for popover API if not supported
  function togglePopover(element, force) {
    if (
      force === true ||
      (force !== false && !element.hasAttribute("popover-open"))
    ) {
      element.setAttribute("popover-open", "");
      element.style.display = "flex";
    } else {
      element.removeAttribute("popover-open");
      element.style.display = "none";
    }
  }

  // Event Listeners
  if (searchButton) {
    document.querySelectorAll(".search-button").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        openSearch();
      });
    });
  }

  if (closeSearchButton) {
    closeSearchButton.addEventListener("click", (e) => {
      e.preventDefault();
      closeSearch();
    });
  }

  // Handle search form submission
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      performSearch(searchInput.value);
    });
  }

  // Handle input changes for live search
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      // Debounced search for better performance
      clearTimeout(searchInput.searchTimeout);
      searchInput.searchTimeout = setTimeout(() => {
        performSearch(searchInput.value);
      }, 300);
    });

    // Handle keyboard shortcut to close search
    searchInput.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeSearch();
      }
    });
  }

  // Initialize keyboard shortcut for search (Ctrl+K or Command+K)
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "k") {
      e.preventDefault();
      if (searchPopover.hasAttribute("popover-open")) {
        closeSearch();
      } else {
        openSearch();
      }
    }
  });

  // Close search on click outside
  document.addEventListener("click", (e) => {
    if (
      searchPopover.hasAttribute("popover-open") &&
      !searchPopover.contains(e.target) &&
      !Array.from(document.querySelectorAll(".search-button")).some((btn) =>
        btn.contains(e.target),
      )
    ) {
      closeSearch();
    }
  });

  // Update CSS variables on root to fix missing colors
  const root = document.documentElement;
  if (!getComputedStyle(root).getPropertyValue("--background-color")) {
    root.style.setProperty("--background-color", "#ffffff");
    root.style.setProperty("--text-color", "#1c1c1c");
    root.style.setProperty("--border-color", "#e0e0e0");
    root.style.setProperty("--hover-color", "rgba(127, 62, 152, 0.1)");
    root.style.setProperty("--accent-color", "#7f3e98");
    root.style.setProperty("--text-color-light", "#4a4a4a");
    root.style.setProperty("--primary-color-rgb", "127, 62, 152");
    root.style.setProperty("--primary-color-dark", "#662d80");
  }
});

// ==========================
// RECENT SEARCHES
// ==========================

// Manage recent searches with localStorage
const recentSearches = {
  add: function (query) {
    if (!query.trim()) return;

    let searches = this.get();

    // Add new search to the beginning and remove duplicates
    searches = [query, ...searches.filter((item) => item !== query)];

    // Keep only the 5 most recent searches
    searches = searches.slice(0, 5);

    localStorage.setItem("recentSearches", JSON.stringify(searches));
  },

  get: function () {
    const searches = localStorage.getItem("recentSearches");
    return searches ? JSON.parse(searches) : [];
  },

  clear: function () {
    localStorage.removeItem("recentSearches");
  },
};

// Add CSS for snippet separators
document.addEventListener("DOMContentLoaded", () => {
  const style = document.createElement("style");
  style.textContent = `
        .snippet-separator {
            display: inline-block;
            margin: 0 4px;
            color: var(--text-muted);
            font-weight: bold;
        }
        
        mark {
            background-color: rgba(127, 62, 152, 0.2);
            color: inherit;
            font-weight: bold;
            padding: 0 2px;
            border-radius: 2px;
        }
        
        .result-snippet {
            font-size: 0.9rem;
            color: var(--text-muted);
            line-height: 1.4;
            margin-top: 4px;
        }
    `;
  document.head.appendChild(style);
});
