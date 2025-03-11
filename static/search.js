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

  // Initialize MiniSearch with the search index
  function initializeSearch() {
    // Create a new MiniSearch instance
    miniSearch = new MiniSearch({
      fields: ["title", "content", "description"], // fields to index for full-text search
      storeFields: ["title", "url", "description", "type", "category", "date"], // fields to return with search results
      searchOptions: {
        boost: { title: 2, description: 1.5 }, // boost factors for fields
        fuzzy: 0.2, // fuzzy search with edit distance of 0.2
        prefix: true, // match by prefix
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
        // Add documents to the index
        miniSearch.addAll(documents);
        console.log(`Indexed ${documents.length} documents for search`);
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

    // Search the index
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
        const snippet = getSnippet(item, query);
        const category = item.category
          ? `<span class="result-category">${item.category}</span>`
          : "";
        const date = item.date
          ? `<span class="result-date">${item.date}</span>`
          : "";

        html += `
                    <li>
                        <a href="${item.url}" class="result-item">
                            <div class="result-title">${item.title}</div>
                            <div class="result-meta">
                                ${category}
                                ${date}
                            </div>
                            <div class="result-snippet">${highlightSearchTerms(snippet, query)}</div>
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

  // Get a relevant snippet from the content
  function getSnippet(item, query) {
    const description = item.description || "";
    const content = item.content || "";

    // If description exists and is not too long, use it
    if (description && description.length > 0 && description.length <= 200) {
      return description;
    }

    // Otherwise, find a relevant snippet from the content
    if (content && content.length > 0) {
      const lowerQuery = query.toLowerCase();
      const lowerContent = content.toLowerCase();

      // Find the position of the query in the content
      const position = lowerContent.indexOf(lowerQuery);

      if (position !== -1) {
        // Get a snippet around the query
        const start = Math.max(0, position - 60);
        const end = Math.min(content.length, position + query.length + 60);
        let snippet = content.substring(start, end);

        // Add ellipsis if needed
        if (start > 0) {
          snippet = "..." + snippet;
        }

        if (end < content.length) {
          snippet = snippet + "...";
        }

        return snippet;
      }
    }

    // Fallback to first 160 characters of content or description
    return (content || description).substring(0, 160) + "...";
  }

  // Highlight search terms in snippet
  function highlightSearchTerms(snippet, searchTerm) {
    if (!searchTerm.trim() || !snippet) return snippet;

    // Get all individual terms
    const terms = searchTerm.trim().split(/\s+/);
    let highlightedSnippet = snippet;

    terms.forEach((term) => {
      if (term.length < 3) return; // Skip very short terms

      const regex = new RegExp(`(${escapeRegExp(term)})`, "gi");
      highlightedSnippet = highlightedSnippet.replace(regex, "<mark>$1</mark>");
    });

    return highlightedSnippet;
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
