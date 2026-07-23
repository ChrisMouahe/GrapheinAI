/**
 * ThemeManager - Instant Client-Side Light / Dark Theme Controller for GrapheinAI
 */
(function () {
  const THEME_KEY = 'graphein_theme';

  function getStoredTheme() {
    return localStorage.getItem(THEME_KEY) || 'light';
  }

  function applyTheme(theme) {
    const htmlEl = document.documentElement;
    if (theme === 'dark') {
      htmlEl.classList.add('dark');
      htmlEl.classList.remove('light');
    } else {
      htmlEl.classList.remove('dark');
      htmlEl.classList.add('light');
    }
    localStorage.setItem(THEME_KEY, theme);
    updateThemeIcon(theme);
  }

  function updateThemeIcon(theme) {
    const iconEl = document.getElementById('theme-icon');
    if (iconEl) {
      if (theme === 'dark') {
        iconEl.setAttribute('data-lucide', 'sun');
      } else {
        iconEl.setAttribute('data-lucide', 'moon');
      }
      if (window.lucide && window.lucide.createIcons) {
        window.lucide.createIcons();
      }
    }
  }

  window.initTheme = function () {
    const currentTheme = getStoredTheme();
    applyTheme(currentTheme);
  };

  window.toggleTheme = function () {
    const currentTheme = getStoredTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
  };

  window.setTheme = function (themeName) {
    if (themeName === 'dark' || themeName === 'light') {
      applyTheme(themeName);
    }
  };

  // Run initial theme application immediately
  window.initTheme();
})();
