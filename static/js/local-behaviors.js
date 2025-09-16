// Local behaviors to emulate essential Elementor interactions without external deps
(function () {
  'use strict';

  function onReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  // Sticky header width + spacer sync
  function fixStickyLayout() {
    var stickies = document.querySelectorAll('.elementor-sticky.elementor-sticky--active');
    for (var i = 0; i < stickies.length; i++) {
      var el = stickies[i];
      // Ensure full-width and pinned to viewport
      el.style.left = '0px';
      el.style.right = '0px';
      el.style.width = '100%';
  // Prevent clipping of dropdowns inside sticky bars
  el.style.overflow = 'visible';
      // Sync spacer height for layout flow
      var id = el.getAttribute('data-id');
      if (id) {
        var spacers = document.querySelectorAll('.elementor-sticky__spacer[data-id="' + id + '"]');
        for (var s = 0; s < spacers.length; s++) {
          var sp = spacers[s];
          sp.style.height = el.offsetHeight + 'px';
          sp.style.display = 'block';
          sp.style.visibility = 'hidden';
        }
      }
    }
  }

  // Utility: parse data-settings JSON from Elementor containers
  function getDataSettings(el) {
    var raw = el.getAttribute('data-settings');
    if (!raw) return {};
    try {
      return JSON.parse(raw);
    } catch (e) {
      try {
        // Some HTML exporters double-encode quotes; try to normalize
        return JSON.parse(raw.replace(/&quot;/g, '"'));
      } catch (_) {
        return {};
      }
    }
  }

  // Determine current device for Elementor breakpoints
  function currentDevice() {
    var w = window.innerWidth || document.documentElement.clientWidth;
    if (w <= 767) return 'mobile';
    if (w <= 1024) return 'tablet';
    return 'desktop';
  }

  function deviceAllowed(settings) {
    var on = settings && settings.sticky_on;
    if (!on || !on.length) return true; // if not specified, assume all
    var dev = currentDevice();
    return on.indexOf(dev) !== -1;
  }

  function getStickyOffset(settings) {
    var dev = currentDevice();
    if (dev === 'mobile' && typeof settings.sticky_offset_mobile === 'number') return settings.sticky_offset_mobile;
    if (dev === 'tablet' && typeof settings.sticky_offset_tablet === 'number') return settings.sticky_offset_tablet;
    if (typeof settings.sticky_offset === 'number') return settings.sticky_offset;
    return 0;
  }

  function isVisible(el) {
    // Basic visibility check
    return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  }

  function getDocumentTop(el) {
    var rect = el.getBoundingClientRect();
    return rect.top + (window.pageYOffset || document.documentElement.scrollTop);
  }

  // Mobile nav menus (Elementor Nav Menu widget)
  function setupMobileNavMenus() {
    var widgets = document.querySelectorAll('.elementor-widget-nav-menu.elementor-nav-menu--toggle');

  function closeWidget(w) {
      var toggle = w.querySelector('.elementor-menu-toggle');
      var dropdown = w.querySelector('.elementor-nav-menu--dropdown.elementor-nav-menu__container');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
      if (dropdown) dropdown.setAttribute('aria-hidden', 'true');
      w.classList.remove('elementor-active');
      // Also remove Elementor's expected active state on the toggle button
      if (toggle) toggle.classList.remove('elementor-active');
      // Inline styles to ensure it's hidden even without Elementor CSS
      if (dropdown) {
        dropdown.style.display = 'none';
        dropdown.style.maxHeight = '0px';
        dropdown.style.overflow = 'hidden';
        dropdown.style.visibility = 'hidden';
        dropdown.style.width = '';
        dropdown.style.zIndex = '';
        dropdown.style.opacity = '';
        dropdown.style.transform = '';
        dropdown.style.position = '';
        dropdown.style.left = '';
        dropdown.style.right = '';
        dropdown.style.top = '';
  dropdown.style.margin = '';
  dropdown.style.height = '';
      }
      // Toggle icons
      var iconOpen = w.querySelector('.elementor-menu-toggle__icon--open');
      var iconClose = w.querySelector('.elementor-menu-toggle__icon--close');
      if (iconOpen) iconOpen.style.display = '';
      if (iconClose) iconClose.style.display = 'none';
      // Restore overflow on nearest sticky ancestor if we changed it
      if (w.__stickyAncestor) {
        try {
          w.__stickyAncestor.style.overflow = w.__stickyAncestorPrevOverflow || '';
        } catch (_) {}
        w.__stickyAncestor = null;
        w.__stickyAncestorPrevOverflow = null;
      }
      // Restore widget/container flow styles
      if (w.__widgetPrevOverflow !== undefined) {
        w.style.overflow = w.__widgetPrevOverflow;
        w.__widgetPrevOverflow = undefined;
      }
      var wc = w.querySelector('.elementor-widget-container');
      if (wc) {
        if (w.__widgetContainerPrevOverflow !== undefined) wc.style.overflow = w.__widgetContainerPrevOverflow;
        if (w.__widgetContainerPrevPosition !== undefined) wc.style.position = w.__widgetContainerPrevPosition;
        if (w.__widgetContainerPrevZIndex !== undefined) wc.style.zIndex = w.__widgetContainerPrevZIndex;
        w.__widgetContainerPrevOverflow = undefined;
        w.__widgetContainerPrevPosition = undefined;
        w.__widgetContainerPrevZIndex = undefined;
      }
      // Remove stretch follow handlers if present
      if (w.__followScroll) {
        try {
          window.removeEventListener('scroll', w.__followScroll);
          window.removeEventListener('resize', w.__followScroll);
        } catch (_) {}
        w.__followScroll = null;
      }
      // Restore any ancestor overflow tweaks
      if (w.__overflowTweaks && Array.isArray(w.__overflowTweaks)) {
        try {
          for (var k = 0; k < w.__overflowTweaks.length; k++) {
            var rec = w.__overflowTweaks[k];
            if (!rec || !rec.el) continue;
            if (rec.prev !== undefined) rec.el.style.overflow = rec.prev;
            if (rec.prevY !== undefined) rec.el.style.overflowY = rec.prevY;
            if (rec.prevPos !== undefined) rec.el.style.position = rec.prevPos;
            if (rec.prevZ !== undefined) rec.el.style.zIndex = rec.prevZ;
          }
        } catch (_) {}
      }
      w.__overflowTweaks = [];
      // Make dropdown links not tabbable again
      if (dropdown) {
        var dLinks = dropdown.querySelectorAll('a[href]');
        for (var j = 0; j < dLinks.length; j++) dLinks[j].setAttribute('tabindex', '-1');
      }
    }

  function openWidget(w) {
      var toggle = w.querySelector('.elementor-menu-toggle');
      var dropdown = w.querySelector('.elementor-nav-menu--dropdown.elementor-nav-menu__container');
      if (toggle) toggle.setAttribute('aria-expanded', 'true');
      if (dropdown) dropdown.setAttribute('aria-hidden', 'false');
      w.classList.add('elementor-active');
      // Match Elementor's active selector behavior
      if (toggle) toggle.classList.add('elementor-active');
      // Inline styles to ensure it's visible even without Elementor CSS
      if (dropdown) {
        dropdown.style.display = 'block';
        dropdown.style.visibility = 'visible';
        dropdown.style.overflow = 'auto';
        // Expand to content height
        dropdown.style.maxHeight = dropdown.scrollHeight + 'px';
        // Make sure it spans full widget width and layers above if needed
        dropdown.style.width = '100%';
        dropdown.style.zIndex = '1002';
        // Force visibility over Elementor's transform-based hide
        dropdown.style.opacity = '1';
        dropdown.style.transform = 'none';
        // Position safeguard: anchor to widget container so it overlays content
        dropdown.style.position = 'absolute';
        dropdown.style.left = '0';
        dropdown.style.right = '0';
        // If widget is set to stretch, expand dropdown to full viewport width on non-desktop
        if (w.classList.contains('elementor-nav-menu--stretch') && currentDevice() !== 'desktop') {
          var anchorEl = toggle || w;
          var rect = anchorEl.getBoundingClientRect();
          var top = Math.max(0, Math.round(rect.bottom));
          dropdown.style.position = 'fixed';
          dropdown.style.left = '0';
          dropdown.style.right = '0';
          dropdown.style.top = top + 'px';
          dropdown.style.margin = '0';
          dropdown.style.width = '100vw';
          dropdown.style.maxHeight = 'calc(100vh - ' + top + 'px)';
          // Follow scroll/resize to keep aligned to the toggle
          w.__followScroll = function () {
            var r = (toggle || w).getBoundingClientRect();
            var t = Math.max(0, Math.round(r.bottom));
            dropdown.style.top = t + 'px';
            dropdown.style.maxHeight = 'calc(100vh - ' + t + 'px)';
          };
          window.addEventListener('scroll', w.__followScroll, { passive: true });
          window.addEventListener('resize', w.__followScroll);
        }
        // Let CSS place it below; avoid hard-coding top when not stretched
      }
      // Toggle icons
      var iconOpen = w.querySelector('.elementor-menu-toggle__icon--open');
      var iconClose = w.querySelector('.elementor-menu-toggle__icon--close');
      if (iconOpen) iconOpen.style.display = 'none';
      if (iconClose) iconClose.style.display = '';
      // Ensure the dropdown isn't clipped by a sticky ancestor
      var ancestor = w.closest('.elementor-sticky');
      if (ancestor) {
        w.__stickyAncestor = ancestor;
        w.__stickyAncestorPrevOverflow = ancestor.style.overflow;
        ancestor.style.overflow = 'visible';
      }
      // Ensure widget/container allow overflow and stack above
      if (w.__widgetPrevOverflow === undefined) w.__widgetPrevOverflow = w.style.overflow;
      w.style.overflow = 'visible';
      var wc = w.querySelector('.elementor-widget-container');
      if (wc) {
        if (w.__widgetContainerPrevOverflow === undefined) w.__widgetContainerPrevOverflow = wc.style.overflow;
        if (w.__widgetContainerPrevPosition === undefined) w.__widgetContainerPrevPosition = wc.style.position;
        if (w.__widgetContainerPrevZIndex === undefined) w.__widgetContainerPrevZIndex = wc.style.zIndex;
        wc.style.overflow = 'visible';
        wc.style.position = 'relative';
        wc.style.zIndex = '1000';
      }
      // If any ancestor containers clip overflow, temporarily relax them
      try {
        var tweaks = [];
        var node = w.parentElement;
        var steps = 0;
        while (node && node !== document.body && steps < 6) {
          var cs = window.getComputedStyle(node);
          var ovY = cs.overflowY || cs.overflow;
          if (ovY && ovY !== 'visible') {
            tweaks.push({
              el: node,
              prev: node.style.overflow,
              prevY: node.style.overflowY,
              prevPos: node.style.position,
              prevZ: node.style.zIndex
            });
            node.style.overflow = 'visible';
            node.style.overflowY = 'visible';
            if (cs.position === 'static') node.style.position = 'relative';
            node.style.zIndex = '1000';
          }
          node = node.parentElement;
          steps++;
        }
        w.__overflowTweaks = tweaks;
      } catch (_) {
        w.__overflowTweaks = [];
      }
      // Make dropdown links tabbable
      if (dropdown) {
        var dLinks = dropdown.querySelectorAll('a[href]');
        for (var j = 0; j < dLinks.length; j++) dLinks[j].removeAttribute('tabindex');
        // Ensure visibility overrides any residual CSS
        dropdown.style.opacity = '1';
        dropdown.style.transform = 'none';
      }
    }

    function isOpen(w) {
      return w.classList.contains('elementor-active');
    }

    function bindWidget(w) {
      if (w.__menuBound) return;
      var toggle = w.querySelector('.elementor-menu-toggle');
      var dropdown = w.querySelector('.elementor-nav-menu--dropdown.elementor-nav-menu__container');
      if (!toggle || !dropdown) return;

      // Ensure initial ARIA state
      toggle.setAttribute('aria-expanded', 'false');
      dropdown.setAttribute('aria-hidden', 'true');

      function toggleMenu(e) {
        if (e) e.preventDefault();
        if (isOpen(w)) {
          closeWidget(w);
        } else {
          // Close any other open menus first
          for (var i = 0; i < widgets.length; i++) {
            if (widgets[i] !== w && isOpen(widgets[i])) closeWidget(widgets[i]);
          }
          openWidget(w);
        }
      }

      toggle.addEventListener('click', toggleMenu);
      toggle.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ' || e.keyCode === 13 || e.keyCode === 32) {
          e.preventDefault();
          toggleMenu();
        }
      });

      // Close on outside click
      document.addEventListener('click', function (e) {
        if (!isOpen(w)) return;
        if (!w.contains(e.target)) closeWidget(w);
      });

      // Close on Escape
      document.addEventListener('keydown', function (e) {
        if (!isOpen(w)) return;
        if (e.key === 'Escape' || e.keyCode === 27) closeWidget(w);
      });

      // Close after selecting a link
      var links = dropdown.querySelectorAll('a[href]');
      for (var i = 0; i < links.length; i++) {
        links[i].addEventListener('click', function () { closeWidget(w); });
      }

      // On resize to desktop, ensure closed and clean inline styles
      window.addEventListener('resize', function () {
        if (currentDevice() === 'desktop') {
          closeWidget(w);
          var dropdown = w.querySelector('.elementor-nav-menu--dropdown.elementor-nav-menu__container');
          if (dropdown) {
            dropdown.style.display = '';
            dropdown.style.maxHeight = '';
            dropdown.style.overflow = '';
            dropdown.style.visibility = '';
            dropdown.style.width = '';
            dropdown.style.zIndex = '';
            dropdown.style.opacity = '';
            dropdown.style.transform = '';
            dropdown.style.position = '';
            dropdown.style.left = '';
            dropdown.style.right = '';
            dropdown.style.top = '';
            dropdown.style.margin = '';
            dropdown.style.height = '';
          }
        }
      });

      w.__menuBound = true;
    }

    // Initialize all widgets: clone links if needed and bind
    for (var i = 0; i < widgets.length; i++) {
      var w = widgets[i];
      try {
        var dropdown = w.querySelector('.elementor-nav-menu--dropdown.elementor-nav-menu__container');
        var main = w.querySelector('.elementor-nav-menu--main.elementor-nav-menu__container');
        if (dropdown && main) {
          var dUL = dropdown.querySelector('ul');
          var mUL = main.querySelector('ul');
          if (dUL && mUL && !dUL.querySelector('li')) {
            dUL.innerHTML = mUL.innerHTML;
          }
        }
      } catch (e) { /* no-op */ }
      bindWidget(w);
    }
  }

  // Sticky manager: emulate Elementor sticky for containers
  function setupSticky() {
    var candidates = Array.prototype.slice.call(document.querySelectorAll('[data-settings]'));
    var managed = [];

    candidates.forEach(function (el) {
      var settings = getDataSettings(el);
      if (!settings || settings.sticky !== 'top') return;

      // Create spacer if needed
      var spacer = document.createElement('div');
      spacer.className = 'elementor-sticky__spacer';
      spacer.setAttribute('data-id', el.getAttribute('data-id') || '');
      spacer.style.display = 'none';
      spacer.style.height = '0px';
      spacer.style.visibility = 'hidden';
      // Insert immediately after element
      if (el.parentNode) {
        el.parentNode.insertBefore(spacer, el.nextSibling);
      }

      managed.push({ el: el, spacer: spacer, settings: settings, topOrigin: getDocumentTop(el) });
    });

    function applyStickyState(item) {
      var el = item.el;
      var spacer = item.spacer;
      var settings = item.settings;
      var allow = deviceAllowed(settings) && isVisible(el);
      var offset = getStickyOffset(settings);
      var topOrigin = item.topOrigin;
      // Update origin in case layout changed (e.g., fonts loaded, window resized)
      // Use spacer height when currently sticky to compute original flow position
      if (!el.classList.contains('elementor-sticky--active')) {
        topOrigin = getDocumentTop(el);
        item.topOrigin = topOrigin;
      } else if (spacer && spacer.offsetParent) {
        // The spacer occupies the original place; use its top
        topOrigin = getDocumentTop(spacer);
        item.topOrigin = topOrigin;
      }

      // Determine activation threshold
      var shouldStick = allow && (window.pageYOffset || document.documentElement.scrollTop) >= Math.max(0, topOrigin - offset);

      if (shouldStick) {
        if (!el.classList.contains('elementor-sticky')) el.classList.add('elementor-sticky');
        if (!el.classList.contains('elementor-sticky--active')) {
          // set spacer height before fixing to avoid jump
          if (spacer) {
            spacer.style.height = el.offsetHeight + 'px';
            spacer.style.display = 'block';
          }
          el.classList.add('elementor-sticky--active');
          // Fixed positioning
          el.style.position = 'fixed';
          el.style.top = offset + 'px';
          el.style.left = '0px';
          el.style.right = '0px';
          el.style.width = '100%';
          // Allow sub-nav to layer above header by DOM order (same zIndex)
          el.style.zIndex = '999';
        } else {
          // keep top updated if offset changes with breakpoint
          el.style.top = offset + 'px';
        }
      } else {
        if (el.classList.contains('elementor-sticky--active')) {
          el.classList.remove('elementor-sticky--active');
          // Restore positioning
          el.style.position = '';
          el.style.top = '';
          el.style.left = '';
          el.style.right = '';
          el.style.width = '';
          el.style.zIndex = '';
          if (spacer) {
            spacer.style.height = '0px';
            spacer.style.display = 'none';
          }
        }
      }
    }

    function tick() {
      for (var i = 0; i < managed.length; i++) applyStickyState(managed[i]);
      // Secondary layout sync
      fixStickyLayout();
    }

    // Initial and listeners
    tick();
    window.addEventListener('scroll', tick, { passive: true });
    window.addEventListener('resize', tick);

    // Expose for other logic (e.g., anchor scrolling)
    return {
      refresh: tick,
      getStickyHeightSum: function () {
        var sum = 0;
        for (var i = 0; i < managed.length; i++) {
          var el = managed[i].el;
          if (el.classList.contains('elementor-sticky--active')) sum += el.offsetHeight;
        }
        return sum;
      }
    };
  }

  // Focus trap helpers for dialogs
  function getFocusable(root) {
    return root.querySelectorAll(
      'a[href], area[href], input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex]:not([tabindex="-1"]), [contenteditable="true"]'
    );
  }

  function trapFocus(dialog) {
    var focusables = Array.prototype.slice.call(getFocusable(dialog));
    if (!focusables.length) return function () {};
    function handle(e) {
      if (e.key !== 'Tab') return;
      var first = focusables[0];
      var last = focusables[focusables.length - 1];
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
    dialog.addEventListener('keydown', handle);
    return function () { dialog.removeEventListener('keydown', handle); };
  }

  // Off-canvas open/close
  function openOffCanvas(el) {
    if (!el || el.classList.contains('elementor-offcanvas--open')) return;
    el.classList.add('elementor-offcanvas--open');
    el.setAttribute('aria-hidden', 'false');
    el.removeAttribute('inert');
    document.documentElement.classList.add('has-offcanvas-open');
    var overlay = el.querySelector('.e-off-canvas__overlay');
    if (overlay && !overlay.__ocBound) {
      overlay.addEventListener('click', function () { closeOffCanvas(el); });
      overlay.__ocBound = true;
    }
    function onEsc(e) { if (e.key === 'Escape') { closeOffCanvas(el); } }
    el.__esc = onEsc;
    document.addEventListener('keydown', onEsc);
    // Focus management
    var cleanupTrap = trapFocus(el);
    el.__trapCleanup = cleanupTrap;
    // Move focus inside dialog
    var focusables = getFocusable(el);
    if (focusables.length) {
      setTimeout(function(){ focusables[0].focus(); }, 0);
    } else {
      setTimeout(function(){ el.focus && el.focus(); }, 0);
    }
  }

  function closeOffCanvas(el) {
    if (!el || !el.classList.contains('elementor-offcanvas--open')) return;
    el.classList.remove('elementor-offcanvas--open');
    el.setAttribute('aria-hidden', 'true');
    el.setAttribute('inert', '');
    if (el.__esc) {
      document.removeEventListener('keydown', el.__esc);
      delete el.__esc;
    }
    if (el.__trapCleanup) {
      try { el.__trapCleanup(); } catch (_) {}
      delete el.__trapCleanup;
    }
    // Restore focus to opener if known
    if (el.__opener && el.__opener.focus) {
      try { el.__opener.focus(); } catch (_) {}
      delete el.__opener;
    }
    // If no other offcanvas is open, clear helper class
    if (!document.querySelector('.e-off-canvas.elementor-offcanvas--open')) {
      document.documentElement.classList.remove('has-offcanvas-open');
    }
  }

  function parseOffCanvasAction(href) {
    try {
      var isOpen = /off_canvas(?::|%3A)open/.test(href);
      var isClose = /off_canvas(?::|%3A)close/.test(href);
      var m = href.match(/settings(?:=|%3D)([^&]+)/);
      if (!m) return null;
      var enc = decodeURIComponent(m[1]);
      var json = enc;
      try { json = atob(enc); } catch (_) {}
      var settings = JSON.parse(json);
      if (!settings || !settings.id) return null;
      return { id: settings.id, action: isOpen ? 'open' : (isClose ? 'close' : null) };
    } catch (_) { return null; }
  }

  function bindOffCanvasActionLinks() {
    var links = document.querySelectorAll('a[href^="#elementor-action"], a[href*="off_canvas%3Aopen"], a[href*="off_canvas%3Aclose"], a[href*="off_canvas:open"], a[href*="off_canvas:close"]');
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      if (a.__ocBound) continue;
      a.addEventListener('click', function (e) {
        var info = parseOffCanvasAction(this.getAttribute('href'));
        if (!info || !info.action) return;
        e.preventDefault();
        var target = document.getElementById('off-canvas-' + info.id);
        if (!target) return;
        // track opener to restore focus on close
        target.__opener = this;
        if (info.action === 'open') openOffCanvas(target); else closeOffCanvas(target);
      });
      a.__ocBound = true;
    }
  }

  function bindOffCanvasCloseButtons() {
    // Any element with data-close or .e-off-canvas__toggle inside open offcanvas should close
    document.addEventListener('click', function (e) {
      var t = e.target;
      if (!t) return;
      if (t.closest && t.closest('.e-off-canvas .e-off-canvas__toggle')) {
        var oc = t.closest('.e-off-canvas');
        if (oc) closeOffCanvas(oc);
      }
    });
  }

  // FAQ accordion toggles
  function setupFAQToggles() {
    var titles = document.querySelectorAll('#FAQ .elementor-widget-toggle .elementor-tab-title');
    function toggle(title) {
      var cid = title.getAttribute('aria-controls');
      var content = cid ? document.getElementById(cid) : null;
      var isExpanded = title.getAttribute('aria-expanded') === 'true';
      var next = !isExpanded;
      title.setAttribute('aria-expanded', String(next));
      title.classList.toggle('elementor-active', next);
      if (content) {
        content.style.display = next ? 'block' : 'none';
        content.setAttribute('aria-hidden', String(!next));
      }
    }
    for (var i = 0; i < titles.length; i++) {
      var t = titles[i];
      if (t.__faqBound) continue;
      t.setAttribute('tabindex', '0');
      t.addEventListener('click', function () { toggle(this); });
      t.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(this); }
      });
      // ensure initial aria-hidden state matches display
      var cid = t.getAttribute('aria-controls');
      var c = cid ? document.getElementById(cid) : null;
      if (c && !c.hasAttribute('aria-hidden')) {
        var expanded = t.getAttribute('aria-expanded') === 'true';
        c.setAttribute('aria-hidden', String(!expanded));
        if (!expanded) c.style.display = 'none';
      }
      t.__faqBound = true;
    }
  }

  // Init
  onReady(function () {
  var sticky = setupSticky();
  fixStickyLayout();
  setupMobileNavMenus();
    bindOffCanvasActionLinks();
    bindOffCanvasCloseButtons();
    setupFAQToggles();
    // Support the site-specific "Join Our Team" trigger links
    (function bindJoinOurTeam() {
      var joinLinks = document.querySelectorAll('a[href="#open-off-canvas"], .open-off-canvas a[href="#open-off-canvas"], li.open-off-canvas > a');
      var offCanvas = document.getElementById('off-canvas-cf32857');
      if (!offCanvas || !joinLinks.length) return;
      for (var i = 0; i < joinLinks.length; i++) {
        var link = joinLinks[i];
        if (link.__joinBound) continue;
        link.addEventListener('click', function (e) {
          e.preventDefault();
          // remember opener
          offCanvas.__opener = this;
          openOffCanvas(offCanvas);
        });
        link.__joinBound = true;
      }
    })();

    // Anchor links: scroll accounting for sticky header(s)
    (function bindAnchors() {
      var links = document.querySelectorAll('a.elementor-item-anchor[href^="#"], a[href^="#ourteam"], a[href^="#aboutus"], a[href^="#services"]');
      function scrollToId(id) {
        var target = document.getElementById(id);
        if (!target) return;
        // Ensure sticky state is up to date before measuring
        if (sticky && typeof sticky.refresh === 'function') sticky.refresh();
        var rect = target.getBoundingClientRect();
        var y = rect.top + (window.pageYOffset || document.documentElement.scrollTop);
        var offset = 0;
        // Sum of sticky heights
        if (sticky && typeof sticky.getStickyHeightSum === 'function') {
          offset = sticky.getStickyHeightSum();
        }
        // Scroll so that section starts below sticky bars
        window.scrollTo({ top: Math.max(0, y - offset - 8), behavior: 'smooth' });
      }
      for (var i = 0; i < links.length; i++) {
        var a = links[i];
        if (a.__anchorBound) continue;
        a.addEventListener('click', function (e) {
          var href = this.getAttribute('href') || '';
          if (href.charAt(0) !== '#') return;
          var id = href.slice(1);
          if (!id) return;
          var target = document.getElementById(id);
          if (!target) return;
          e.preventDefault();
          scrollToId(id);
        });
        a.__anchorBound = true;
      }
      // If loaded with a hash, adjust position once
      if (window.location.hash) {
        var initialId = window.location.hash.replace('#', '');
        setTimeout(function(){ scrollToId(initialId); }, 0);
      }
    })();
  });
  window.addEventListener('resize', fixStickyLayout);
  window.addEventListener('load', fixStickyLayout);
})();
