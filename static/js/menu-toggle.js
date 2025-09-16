// Hamburger menu toggle for mobile nav
// Looks for .elementor-menu-toggle and toggles .elementor-active on click

document.addEventListener('DOMContentLoaded', function () {
  // For each nav menu with a burger toggle
  document.querySelectorAll('.elementor-menu-toggle').forEach(function(toggle) {
    // Find the closest nav menu widget
    var navMenuWidget = toggle.closest('.elementor-widget-nav-menu');
    if (!navMenuWidget) return;
    // Find the dropdown nav (not the horizontal one)
    var dropdownNav = navMenuWidget.querySelector('.elementor-nav-menu--dropdown');
    if (!dropdownNav) return;

    function setOpen(isOpen) {
      if (isOpen) {
        toggle.classList.add('elementor-active');
        toggle.setAttribute('aria-expanded', 'true');
        dropdownNav.style.display = 'block';
        dropdownNav.setAttribute('aria-hidden', 'false');
        dropdownNav.classList.add('elementor-dropdown-active');
      } else {
        toggle.classList.remove('elementor-active');
        toggle.setAttribute('aria-expanded', 'false');
        dropdownNav.style.display = 'none';
        dropdownNav.setAttribute('aria-hidden', 'true');
        dropdownNav.classList.remove('elementor-dropdown-active');
      }
    }

    toggle.addEventListener('click', function() {
      // Toggle active class on toggle
      var willOpen = !toggle.classList.contains('elementor-active');
      setOpen(willOpen);
    });

    // Close dropdown when a nav anchor is clicked (so the page can scroll to target)
    dropdownNav.addEventListener('click', function(e) {
      var a = e.target.closest('a[href^="#"]');
      if (!a) return;
      // Only act on in-page anchors and not the off-canvas opener
      var href = a.getAttribute('href');
      if (href === '#open-off-canvas') return; // handled elsewhere
      setOpen(false);
    });
  });
});
