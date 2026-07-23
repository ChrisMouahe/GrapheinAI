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
    const isDark = theme === 'dark';

    // Topbar header icons
    const sunIcon = document.getElementById('theme-icon-sun');
    const moonIcon = document.getElementById('theme-icon-moon');
    if (sunIcon) sunIcon.style.display = isDark ? 'inline-block' : 'none';
    if (moonIcon) moonIcon.style.display = isDark ? 'none' : 'inline-block';

    // Landing navbar icons
    const landingSun = document.getElementById('landing-theme-icon-sun');
    const landingMoon = document.getElementById('landing-theme-icon-moon');
    if (landingSun) landingSun.style.display = isDark ? 'inline-block' : 'none';
    if (landingMoon) landingMoon.style.display = isDark ? 'none' : 'inline-block';
  }

  const initTheme = function () {
    const currentTheme = getStoredTheme();
    applyTheme(currentTheme);
  };

  const toggleTheme = function () {
    const currentTheme = getStoredTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
  };

  const setTheme = function (themeName) {
    if (themeName === 'dark' || themeName === 'light') {
      applyTheme(themeName);
    }
  };

  // Register on window object
  window.initTheme = initTheme;
  window.toggleTheme = toggleTheme;
  window.setTheme = setTheme;
  window.ThemeManager = {
    initTheme,
    toggleTheme,
    setTheme,
    applyTheme,
  };

  // Run initial theme application immediately
  initTheme();
})();
