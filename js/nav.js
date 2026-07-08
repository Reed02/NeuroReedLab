/* ============================================================
   nav.js — Shared navbar & footer injector
   ============================================================
   HOW IT WORKS:
   Each HTML page has:
     <div id="navbar"></div>   ← navbar goes here
     <div id="footer"></div>   ← footer goes here
     <script src="js/nav.js"></script>

   To update the navbar or footer across ALL pages, edit this
   file only. No need to touch individual HTML files.

   PAGES IN SUBFOLDERS (e.g. blog/my-post.html):
   Add this ONE line BEFORE the nav.js <script> tag so the nav
   links point back to the site root correctly:
     <script>window.SITE_BASE = "../";</script>
   Root-level pages (index.html, blog.html, etc.) don't need it.
   ============================================================ */

(function () {

  /* ── BASE PATH (for pages inside subfolders like /blog/) ── */
  const base = window.SITE_BASE || '';

  /* ── ACTIVE LINK DETECTION ── */
  const page = window.location.pathname.split('/').pop() || 'index.html';

  function isActive(href) {
    return page === href ? 'class="active"' : '';
  }

  /* ── NAVBAR HTML ── */
  /* To add a new nav link: add a new <li> below.
     To add a new dropdown item: add a new <a> inside .dropdown-menu. */
  const navHTML = `
    <nav class="navbar" id="site-navbar">
      <a href="${base}index.html" class="logo">Neuro<em>Reed</em>Lab</a>
      <ul class="nav-links">
        <li><a href="${base}index.html" ${isActive('index.html')}>Home</a></li>
        <li><a href="${base}about.html" ${isActive('about.html')}>About</a></li>
        <li class="dropdown">
          <a href="${base}projects.html" ${isActive('projects.html')}>Projects ▾</a>
          <div class="dropdown-menu" id="nav-projects-dropdown">
            <!-- Project dropdown links are injected by projects.js -->
          </div>
        </li>
        <li><a href="${base}blog.html" ${isActive('blog.html')}>Blog</a></li>
        <li><a href="${base}testimonials.html" ${isActive('testimonials.html')}>Testimonials</a></li>
        <li><a href="${base}leave_testimonial.html" ${isActive('leave_testimonial.html')}>Leave a Testimonial</a></li>
        <li><a href="${base}contact.html" ${isActive('contact.html')}>Contact</a></li>
      </ul>
    </nav>
  `;

  /* ── FOOTER HTML ── */
  /* To update the footer across all pages, edit the HTML below. */
  const footerHTML = `
    <footer class="footer">
      <div class="footer-logo">Neuro<em>Reed</em>Lab</div>
      <div class="footer-copy">&copy; ${new Date().getFullYear()} NeuroReedLab</div>
    </footer>
  `;

  /* ── INJECT ── */
  const navEl = document.getElementById('navbar');
  const footerEl = document.getElementById('footer');

  if (navEl)    navEl.outerHTML    = navHTML;
  if (footerEl) footerEl.outerHTML = footerHTML;

  /* ── TRANSPARENT NAVBAR (index.html only) ── */
  if (page === 'index.html' || page === '') {
    const nb = document.getElementById('site-navbar');
    if (nb) nb.classList.add('navbar--transparent');
  }

})();
