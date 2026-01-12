function initSidebar() {
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar-container');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn) {
        // Remove old listener to avoid duplicates if re-init
        toggleBtn.onclick = toggleSidebar;
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar-container');
    const overlay = document.querySelector('.sidebar-overlay');

    if (sidebar) {
        sidebar.classList.toggle('active');
    }
    if (overlay) {
        overlay.classList.toggle('active');
    }
}
