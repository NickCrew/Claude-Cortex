(() => {
  const searchIndexUrl = window.__SEARCH_INDEX_URL__ || '/search.json';
  const headerWrapper = document.querySelector('.site-header .wrapper');
  if (!headerWrapper) {
    return;
  }

  const searchContainer = document.createElement('div');
  searchContainer.className = 'site-search';
  searchContainer.innerHTML = `
    <label class="site-search__label" for="site-search-input">Search documentation</label>
    <input
      id="site-search-input"
      class="site-search__input"
      type="search"
      placeholder="Search docs"
      autocomplete="off"
      spellcheck="false"
    />
    <div class="site-search__results" role="listbox" aria-live="polite"></div>
  `;

  const nav = headerWrapper.querySelector('.site-nav');
  if (nav && nav.nextSibling) {
    headerWrapper.insertBefore(searchContainer, nav.nextSibling);
  } else {
    headerWrapper.appendChild(searchContainer);
  }

  const input = searchContainer.querySelector('.site-search__input');
  const results = searchContainer.querySelector('.site-search__results');

  let index = [];
  let indexLoaded = false;
  let indexLoading = false;

  const escapeHtml = (value) =>
    value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');

  const getSnippet = (content, tokens) => {
    const normalized = content.toLowerCase();
    let indexPos = -1;
    for (const token of tokens) {
      indexPos = normalized.indexOf(token);
      if (indexPos >= 0) break;
    }
    if (indexPos < 0) {
      return content.slice(0, 180);
    }
    const start = Math.max(0, indexPos - 60);
    const end = Math.min(content.length, indexPos + 120);
    let snippet = content.slice(start, end).trim();
    if (start > 0) snippet = `…${snippet}`;
    if (end < content.length) snippet = `${snippet}…`;
    return snippet;
  };

  const renderResults = (items, tokens) => {
    if (!items.length) {
      results.classList.remove('is-active');
      results.innerHTML = '';
      return;
    }

    results.innerHTML = items
      .map((item) => {
        const snippet = getSnippet(item.content || '', tokens);
        return `
          <a class="site-search__result" href="${item.url}" role="option">
            <div class="site-search__title">${escapeHtml(item.title || 'Untitled')}</div>
            <div class="site-search__snippet">${escapeHtml(snippet)}</div>
          </a>
        `;
      })
      .join('');

    results.classList.add('is-active');
  };

  const loadIndex = async () => {
    if (indexLoaded || indexLoading) return;
    indexLoading = true;
    try {
      const response = await fetch(searchIndexUrl, { cache: 'no-store' });
      if (!response.ok) throw new Error('Failed to load search index');
      index = await response.json();
      indexLoaded = true;
    } catch (error) {
      index = [];
      indexLoaded = true;
    } finally {
      indexLoading = false;
    }
  };

  const runSearch = (query) => {
    const tokens = query
      .toLowerCase()
      .split(/\s+/)
      .filter(Boolean);

    if (!tokens.length) {
      renderResults([], tokens);
      return;
    }

    const scored = [];
    for (const page of index) {
      const title = (page.title || '').toLowerCase();
      const content = (page.content || '').toLowerCase();
      const haystack = `${title} ${content}`;
      let score = 0;
      let matches = true;

      for (const token of tokens) {
        const inTitle = title.includes(token);
        const inContent = content.includes(token);
        if (!inTitle && !inContent) {
          matches = false;
          break;
        }
        if (inTitle) score += 12;
        if (inContent) score += 3;
      }

      if (matches) {
        scored.push({ page, score });
      }
    }

    scored.sort((a, b) => b.score - a.score);
    const resultsList = scored.slice(0, 8).map((entry) => entry.page);
    renderResults(resultsList, tokens);
  };

  input.addEventListener('focus', loadIndex);
  input.addEventListener('input', (event) => {
    const value = event.target.value.trim();
    if (!indexLoaded) {
      loadIndex().then(() => runSearch(value));
      return;
    }
    runSearch(value);
  });

  document.addEventListener('click', (event) => {
    if (!searchContainer.contains(event.target)) {
      results.classList.remove('is-active');
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      results.classList.remove('is-active');
      input.blur();
    }
  });
})();
