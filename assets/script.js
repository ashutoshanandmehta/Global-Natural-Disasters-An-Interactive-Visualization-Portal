function initializeDashboardUI(retries = 10) {
  const layout = document.getElementById('app-container');
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const themeToggle = document.getElementById('theme-toggle');
  const tabs = document.querySelectorAll('.sidebar-tab');
  const sections = document.querySelectorAll('.content-section');

  if (!layout || !sidebar || !sidebarToggle || !themeToggle || tabs.length === 0 || sections.length === 0) {
    if (retries > 0) {
      setTimeout(() => initializeDashboardUI(retries - 1), 300); // wait 300ms and try again
    } else {
      console.warn("Dashboard UI initialization failed: elements still not found.");
    }
    return;
  }

  // === Sidebar Toggle ===
  sidebarToggle.addEventListener('click', () => {
    const isCollapsed = sidebar.classList.toggle('sidebar--collapsed');
    layout.classList.toggle('layout--sidebar-collapsed', isCollapsed);
    tabs.forEach(tab => {
      tab.classList.toggle('sidebar-tab--icon-only', isCollapsed);
    });
  });

  // === Theme Toggle ===
  themeToggle.addEventListener('click', () => {
    const isLight = layout.classList.contains('light');
    layout.classList.toggle('light', !isLight);
    layout.classList.toggle('dark', isLight);
    themeToggle.classList.toggle('theme-toggle--light', !isLight);
    themeToggle.classList.toggle('theme-toggle--dark', isLight);
  });

  // === Tab Switching ===
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('sidebar-tab--active'));
      tab.classList.add('sidebar-tab--active');

      const target = tab.dataset.tab;
      sections.forEach(section => {
        if (section.id === `content-${target}`) {
          section.classList.add('active');
        } else {
          section.classList.remove('active');
        }
      });
    });
  });

  console.log("Dashboard UI initialized successfully.");
}

// Start it after load
window.addEventListener("load", () => {
  initializeDashboardUI();
});
