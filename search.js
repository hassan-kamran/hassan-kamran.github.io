// Initialize MiniSearch when the document is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const searchInput = document.getElementById("search-input");
  const searchResults = document.getElementById("search-results");
  const searchForm = document.getElementById("search-form");
  const searchResultsContainer = document.getElementById(
    "search-results-container",
  );

  // Initialize variables
  let searchIndex;
  let miniSearch;

  // Initialize MiniSearch instance with configuration
  const initMiniSearch = (documents) => {
    return new MiniSearch({
      fields: ["title", "content", "category"], // fields to index for full-text search
      storeFields: ["title", "content", "url", "category", "date", "type"], // fields to return with search results
      searchOptions: {
        boost: { title: 2, category: 1.5 }, // boost these fields
        fuzzy: 0.2, // fuzzy search with edit distance = 2
        prefix: true, // match by prefix (e.g. "eng" matches "engineer")
      },
    });
  };

  // Fetch and load search index
  const loadSearchIndex = async () => {
    try {
      const response = await fetch("/static/search-index.json");
      if (!response.ok) {
        throw new Error("Failed to load search index");
      }

      searchIndex = await response.json();
      miniSearch = initMiniSearch();
      miniSearch.addAll(searchIndex);

      console.log("Search index loaded successfully");
    } catch (error) {
      console.error("Error loading search index:", error);
    }
  };

  // Perform search and display results
  const performSearch = (query) => {
    // Don't search if query is empty or search index hasn't loaded
    if (!query.trim() || !miniSearch) {
      hideSearchResults();
      return;
    }

    // Get search results
    const results = miniSearch.search(query, {
      boost: { title: 2 },
      fuzzy: 0.2,
    });

    // Display results
    displaySearchResults(results, query);
  };

  // Display search results
  const displaySearchResults = (results, query) => {
    if (!searchResults) return;

    // Clear previous results
    searchResults.innerHTML = "";

    if (results.length === 0) {
      // No results found
      searchResults.innerHTML = `
        <div class="no-results">
          <p>No results found for "${query}"</p>
        </div>
      `;
    } else {
      // Group results by type
      const groupedResults = {
        page: [],
        blog: [],
      };

      results.forEach((result) => {
        const type = result.type || "other";
        if (!groupedResults[type]) {
          groupedResults[type] = [];
        }
        groupedResults[type].push(result);
      });

      // Create results HTML
      if (groupedResults.page.length > 0) {
        const pagesSection = document.createElement("div");
        pagesSection.className = "result-section";
        pagesSection.innerHTML = `<h3>Pages</h3>`;

        const pageList = document.createElement("ul");
        groupedResults.page.forEach((result) => {
          const item = document.createElement("li");
          item.innerHTML = `
            <a href="/${result.url}" class="result-item">
              <div class="result-title">${result.title}</div>
              <div class="result-snippet">${getResultSnippet(result.content, query)}</div>
            </a>
          `;
          pageList.appendChild(item);
        });

        pagesSection.appendChild(pageList);
        searchResults.appendChild(pagesSection);
      }

      if (groupedResults.blog.length > 0) {
        const blogsSection = document.createElement("div");
        blogsSection.className = "result-section";
        blogsSection.innerHTML = `<h3>Blog Posts</h3>`;

        const blogList = document.createElement("ul");
        groupedResults.blog.forEach((result) => {
          const item = document.createElement("li");
          item.innerHTML = `
            <a href="/${result.url}" class="result-item">
              <div class="result-title">${result.title}</div>
              <div class="result-meta">
                <span class="result-category">${result.category}</span>
                <span class="result-date">${result.date || ""}</span>
              </div>
              <div class="result-snippet">${getResultSnippet(result.content, query)}</div>
            </a>
          `;
          blogList.appendChild(item);
        });

        blogsSection.appendChild(blogList);
        searchResults.appendChild(blogsSection);
      }
    }

    // Show results container
    showSearchResults();
  };

  // Get a snippet of content around the search query
  const getResultSnippet = (content, query) => {
    if (!content) return "";

    const maxSnippetLength = 150;
    const lowerContent = content.toLowerCase();
    const lowerQuery = query.toLowerCase();

    const index = lowerContent.indexOf(lowerQuery);
    if (index === -1) {
      // If query not found, return beginning of content
      return content.substring(0, maxSnippetLength) + "...";
    }

    // Calculate snippet start and end
    let start = Math.max(0, index - 50);
    let end = Math.min(content.length, index + query.length + 100);

    // Adjust to not break words
    if (start > 0) {
      // Find previous space
      const prevSpace = content.lastIndexOf(" ", start);
      if (prevSpace !== -1) {
        start = prevSpace + 1;
      }
    }

    if (end < content.length) {
      // Find next space
      const nextSpace = content.indexOf(" ", end);
      if (nextSpace !== -1) {
        end = nextSpace;
      }
    }

    // Create snippet with ellipses if needed
    let snippet = content.substring(start, end);
    if (start > 0) snippet = "..." + snippet;
    if (end < content.length) snippet = snippet + "...";

    // Highlight the query in the snippet (simple approach)
    const regex = new RegExp(`(${escapeRegExp(query)})`, "gi");
    snippet = snippet.replace(regex, "<mark>$1</mark>");

    return snippet;
  };

  // Helper to escape special characters for regex
  const escapeRegExp = (string) => {
    return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  };

  // Show search results container
  const showSearchResults = () => {
    if (searchResultsContainer) {
      searchResultsContainer.classList.add("visible");
    }
  };

  // Hide search results container
  const hideSearchResults = () => {
    if (searchResultsContainer) {
      searchResultsContainer.classList.remove("visible");
    }
  };

  // Event listeners
  if (searchInput) {
    // Input event for real-time search
    searchInput.addEventListener("input", (event) => {
      const query = event.target.value;
      performSearch(query);
    });

    // Focus event to show results if input has value
    searchInput.addEventListener("focus", () => {
      if (searchInput.value.trim()) {
        performSearch(searchInput.value);
      }
    });
  }

  // Handle form submission
  if (searchForm) {
    searchForm.addEventListener("submit", (event) => {
      event.preventDefault();
      performSearch(searchInput.value);
    });
  }

  // Close search results when clicking outside
  document.addEventListener("click", (event) => {
    const isClickInside =
      searchResultsContainer?.contains(event.target) ||
      searchInput?.contains(event.target);

    if (
      !isClickInside &&
      searchResultsContainer?.classList.contains("visible")
    ) {
      hideSearchResults();
    }
  });

  // Close search results with escape key
  document.addEventListener("keydown", (event) => {
    if (
      event.key === "Escape" &&
      searchResultsContainer?.classList.contains("visible")
    ) {
      hideSearchResults();
    }
  });

  // Load search index on page load
  loadSearchIndex();
});
