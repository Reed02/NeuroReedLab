/* ============================================================
   blog.js — Renders blog post cards on blog.html
   ============================================================
   HOW TO ADD A NEW BLOG POST:

   1. Copy blog/_template.html to a new file, e.g.
        blog/my-new-post.html
      and fill in your content. It already links to
      css/blog.css and the site navbar/footer, so it will
      match the rest of the site automatically.

   2. Open data/blog.json and add a new object to the array:

      {
        "title": "My New Post",
        "tag":   "EEG",
        "date":  "2025-03",
        "url":   "blog/my-new-post.html",
        "desc":  "A one or two sentence summary of the post.",
        "external": false
      }

      Set "external": true  → opens in a new tab (e.g. a post
                               hosted somewhere else)
      Set "external": false → opens in the same tab (local file)

   That's it — the new card appears on blog.html automatically,
   newest-first is up to you (order in the JSON = display order).
   ============================================================ */

(function () {

  const JSON_PATH = 'data/blog.json';

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length < 2) return dateStr;
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const monthIdx = parseInt(parts[1], 10) - 1;
    return `${months[monthIdx] || ''} ${parts[0]}`;
  }

  function buildCard(post) {
    const target = post.external ? 'target="_blank" rel="noopener noreferrer"' : '';
    return `
      <a href="${post.url}" ${target} class="blog-card">
        <div class="blog-card-top">
          <span class="tag tag-teal">${post.tag}</span>
          <span class="blog-card-date">${formatDate(post.date)}</span>
        </div>
        <h3>${post.title}</h3>
        <p>${post.desc}</p>
        <span class="blog-card-arrow">Read post →</span>
      </a>`;
  }

  const grid = document.getElementById('blog-grid');
  if (!grid) return; /* not on blog.html, nothing to do */

  fetch(JSON_PATH)
    .then(r => r.json())
    .then(posts => {
      const countEl = document.getElementById('blog-count');
      if (!posts.length) {
        grid.innerHTML = `<p class="blog-empty">No posts yet — check back soon.</p>`;
        if (countEl) countEl.textContent = '0 posts';
        return;
      }
      /* newest-looking first: reverse so most-recently-added shows first */
      const ordered = posts.slice().reverse();
      grid.innerHTML = ordered.map(buildCard).join('');
      if (countEl) {
        const n = posts.length;
        countEl.textContent = `${n} post${n !== 1 ? 's' : ''}`;
      }
    })
    .catch(err => {
      console.warn('blog.js: could not load data/blog.json', err);
      grid.innerHTML = `<p class="blog-empty">Could not load blog posts.</p>`;
    });

})();
