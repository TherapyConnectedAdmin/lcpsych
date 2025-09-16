/**
 * Rewrite same-site hyperlinks copied from lcpsych.com to local paths/anchors.
 * - https://www.lcpsych.com/#section  -> #section
 * - https://www.lcpsych.com/           -> /
 * - https://www.lcpsych.com/foo/bar/   -> /foo/bar/
 * External links (therapyportal.com, tel:, mailto:, etc.) are left untouched.
 */
(function () {
  function rewriteAnchor(a) {
    try {
      const href = a.getAttribute('href');
      if (!href) return;
      // Skip non-http(s) schemes
      if (!/^https?:\/\//i.test(href)) return;
      const url = new URL(href);
      const host = url.hostname.replace(/^www\./, '').toLowerCase();
      if (host !== 'lcpsych.com') return; // only rewrite same-site links

      // Keep query/hash if present
      if ((url.pathname === '/' || url.pathname === '') && url.hash) {
        a.setAttribute('href', url.hash);
      } else if (url.pathname === '/' || url.pathname === '') {
        a.setAttribute('href', '/');
      } else {
        a.setAttribute('href', url.pathname + url.search + url.hash);
      }

      // Local links shouldn't force a new tab
      if (a.getAttribute('target') === '_blank') {
        a.removeAttribute('target');
        a.removeAttribute('rel');
      }
    } catch (e) {
      // no-op
    }
  }

  function run() {
    document.querySelectorAll('a[href]').forEach(rewriteAnchor);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
