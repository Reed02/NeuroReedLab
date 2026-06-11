/* main.js — shared site logic */

async function loadPartial(selector, url) {
  try {
    const res = await fetch(url);
    const html = await res.text();
    document.querySelector(selector).outerHTML = html;
  } catch (e) {
    console.warn('Could not load partial:', url);
  }
}

function setActiveNav() {
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === page || (page === '' && href === 'index.html')) {
      a.classList.add('active');
    }
  });
}

function initScrollReveal() {
  const els = document.querySelectorAll('[data-reveal]');
  if (!els.length) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('revealed');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  els.forEach(el => obs.observe(el));
}

function initCountUp() {
  const els = document.querySelectorAll('[data-countup]');
  if (!els.length) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target;
      const target = parseFloat(el.dataset.countup);
      const suffix = el.dataset.suffix || '';
      const prefix = el.dataset.prefix || '';
      const decimals = el.dataset.decimals ? parseInt(el.dataset.decimals) : 0;
      const duration = 1400;
      const start = performance.now();
      function tick(now) {
        const t = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - t, 3);
        const val = target * ease;
        el.textContent = prefix + val.toFixed(decimals) + suffix;
        if (t < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
      obs.unobserve(el);
    });
  }, { threshold: 0.5 });
  els.forEach(el => obs.observe(el));
}

/* ── Scroll-reveal CSS helper (injected once) ── */
function injectRevealStyles() {
  if (document.getElementById('reveal-style')) return;
  const s = document.createElement('style');
  s.id = 'reveal-style';
  s.textContent = `
    [data-reveal] { opacity: 0; transform: translateY(22px); transition: opacity 0.55s ease, transform 0.55s ease; }
    [data-reveal].revealed { opacity: 1; transform: none; }
    [data-reveal][data-delay="1"] { transition-delay: 0.1s; }
    [data-reveal][data-delay="2"] { transition-delay: 0.2s; }
    [data-reveal][data-delay="3"] { transition-delay: 0.3s; }
  `;
  document.head.appendChild(s);
}

document.addEventListener('DOMContentLoaded', async () => {
  injectRevealStyles();

  /* load header and footer if placeholder elements exist */
  const headerSlot = document.getElementById('header-slot');
  const footerSlot = document.getElementById('footer-slot');
  if (headerSlot) await loadPartial('#header-slot', 'header.html');
  if (footerSlot) await loadPartial('#footer-slot', 'footer.html');

  setActiveNav();
  initScrollReveal();
  initCountUp();
});
