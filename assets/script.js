function initializeDashboardUI(retries = 10) {
  const layout = document.getElementById('app-container');
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const themeToggle = document.getElementById('theme-toggle');
  const tabs = document.querySelectorAll('.sidebar-tab');
  const sections = document.querySelectorAll('.content-section');

  if (!layout || !sidebar || !sidebarToggle || !themeToggle || tabs.length === 0 || sections.length === 0) {
    if (retries > 0) {
      setTimeout(() => initializeDashboardUI(retries - 1), 300);
    } else {
      console.warn('Dashboard UI initialization failed: elements still not found.');
    }
    return;
  }

  // Helper: treat Enter/Space on a role="button" element like a click
  const clickable = (el, fn) => {
    el.addEventListener('click', fn);
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fn();
      }
    });
  };

  // === Sidebar toggle ===
  clickable(sidebarToggle, () => {
    const isCollapsed = sidebar.classList.toggle('sidebar--collapsed');
    layout.classList.toggle('layout--sidebar-collapsed', isCollapsed);
    window.dispatchEvent(new Event('resize'));
  });

  // === Theme toggle ===
  clickable(themeToggle, () => {
    const isLight = layout.classList.contains('light');
    layout.classList.toggle('light', !isLight);
    layout.classList.toggle('dark', isLight);
    themeToggle.classList.toggle('theme-toggle--light', !isLight);
    themeToggle.classList.toggle('theme-toggle--dark', isLight);
  });

  // === Tab switching ===
  tabs.forEach((tab) => {
    clickable(tab, () => {
      tabs.forEach((t) => t.classList.remove('sidebar-tab--active'));
      tab.classList.add('sidebar-tab--active');

      const target = tab.dataset.tab;
      sections.forEach((section) => {
        section.classList.toggle('active', section.id === `content-${target}`);
      });

      // Plotly figures rendered while hidden have zero width — let them
      // re-measure once their section becomes visible.
      requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
    });
  });

  console.log('Dashboard UI initialized successfully.');
}

window.addEventListener('load', () => {
  initializeDashboardUI();
});
