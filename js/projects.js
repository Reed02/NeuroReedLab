/* ============================================================
   projects.js — Renders project cards & nav dropdown
   ============================================================
   HOW TO ADD A NEW PROJECT:
   Open data/projects.json and add a new object to the array:

   {
     "title":    "My New Project",
     "tag":      "Machine Learning",
     "url":      "https://my-project-site.com",
     "desc":     "A short description of what this project does.",
     "external": true
   }

   Set "external": true  → opens in a new tab (external site)
   Set "external": false → opens in the same tab (local HTML file)

   That's it! The card on projects.html, the dropdown in the
   navbar, and the featured card on index.html all update
   automatically.
   ============================================================ */

(function () {

  const JSON_PATH = 'data/projects.json';

  /* SVG icons — add more as needed, keyed by tag name (lowercase) */
  const ICONS = {
    default: `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="3" y1="9" x2="21" y2="9"/>
        <line x1="3" y1="15" x2="21" y2="15"/>
        <line x1="9" y1="9" x2="9" y2="21"/>
      </svg>`,
    'machine learning': `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
      </svg>`,
    'eeg': `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <polyline points="2 12 5 12 7 6 9 18 11 10 13 14 15 12 22 12"/>
      </svg>`,
    'data prep': `
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="3" y1="9" x2="21" y2="9"/>
        <line x1="3" y1="15" x2="21" y2="15"/>
        <line x1="9" y1="9" x2="9" y2="21"/>
      </svg>`,
  };

  const ARROW_SVG = `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <line x1="7" y1="17" x2="17" y2="7"/>
      <polyline points="7 7 17 7 17 17"/>
    </svg>`;

  function getIcon(tag) {
    return ICONS[tag.toLowerCase()] || ICONS.default;
  }

  function buildCard(project) {
    const target = project.external ? 'target="_blank" rel="noopener noreferrer"' : '';
    return `
      <a href="${project.url}" ${target} class="project-card">
        <div class="card-header">
          <div class="card-icon">${getIcon(project.tag)}</div>
          <div class="card-arrow">${ARROW_SVG}</div>
        </div>
        <span class="card-tag">${project.tag}</span>
        <div class="card-title">${project.title}</div>
        <div class="card-desc">${project.desc}</div>
      </a>`;
  }

  function buildDropdownLink(project) {
    const target = project.external ? 'target="_blank" rel="noopener noreferrer"' : '';
    return `<a href="${project.url}" ${target}>${project.title}</a>`;
  }

  function buildFeaturedCard(project) {
    const target = project.external ? 'target="_blank" rel="noopener noreferrer"' : '';
    return `
      <a href="${project.url}" ${target} class="featured-card">
        <div class="featured-icon">${getIcon(project.tag)}</div>
        <div class="featured-body">
          <span class="featured-tag">${project.tag}</span>
          <div class="featured-title">${project.title}</div>
          <div class="featured-desc">${project.desc}</div>
        </div>
        <div class="featured-arrow">↗</div>
      </a>`;
  }

  fetch(JSON_PATH)
    .then(r => r.json())
    .then(projects => {

      /* ── PROJECT GRID (projects.html) ── */
      const grid = document.getElementById('projects-grid');
      const countEl = document.getElementById('project-count');
      if (grid) {
        grid.innerHTML = projects.map(buildCard).join('');
        if (countEl) {
          const n = projects.length;
          countEl.textContent = `${n} project${n !== 1 ? 's' : ''}`;
        }
      }

      /* ── NAV DROPDOWN ── */
      const dropdown = document.getElementById('nav-projects-dropdown');
      if (dropdown) {
        dropdown.innerHTML = projects.map(buildDropdownLink).join('');
      }

      /* ── FEATURED CARD (index.html) ── */
      const featured = document.getElementById('featured-project');
      if (featured && projects.length > 0) {
        /* Shows the most recently added project (last in the JSON array) */
        featured.innerHTML = buildFeaturedCard(projects[projects.length - 1]);
      }

    })
    .catch(err => {
      console.warn('projects.js: could not load data/projects.json', err);

      const grid = document.getElementById('projects-grid');
      if (grid) grid.innerHTML = `<p style="color:var(--text-muted);font-size:14px;">Could not load projects.</p>`;
    });

})();
