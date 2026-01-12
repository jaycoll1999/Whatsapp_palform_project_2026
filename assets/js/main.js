// Main App Logic

document.addEventListener('DOMContentLoaded', async () => {
    console.log('App Initializing...');

    // 1. Load Layout Components
    await loadComponent('sidebar-container', 'components/sidebar.html');
    await loadComponent('header-container', 'components/header.html');
    await loadComponent('modal-wrapper', 'components/modal.html');

    // 2. Initialize Sidebar Logic (from sidebar.js)
    if (typeof initSidebar === 'function') {
        initSidebar();
    }

    // 3. Load Default Page (Dashboard) or from URL Hash
    const page = getPageFromHash() || 'dashboard';
    await loadPage(page);
});

// Helper: Load HTML component
async function loadComponent(elementId, path) {
    try {
        const response = await fetch(path);
        if (!response.ok) throw new Error(`Failed to load ${path}`);
        const html = await response.text();
        document.getElementById(elementId).innerHTML = html;
    } catch (error) {
        console.error(error);
    }
}

// Global: Load Page Content
async function loadPage(pageName, event = null) {
    if (event) event.preventDefault();

    const mainContent = document.getElementById('main-content');

    // Show Loading
    // mainContent.innerHTML = '<div class="spinner"...></div>'; // Optional

    try {
        // Update URL Hash
        window.location.hash = pageName;

        // Update Sidebar Active State
        updateActiveLink(pageName);

        // Fetch Page
        const response = await fetch(`pages/${pageName}.html`);
        if (!response.ok) throw new Error(`Page ${pageName} not found`);
        const html = await response.text();

        mainContent.innerHTML = html;

        // Update Header Title (Simple heuristic)
        const titleMap = {
            'dashboard': 'Dashboard',
            'users': 'User Management',
            'whatsapp-numbers': 'WhatsApp Numbers',
            'templates': 'Message Templates',
            'webhooks': 'Webhook Configuration',
            'send-message': 'Send Message',
            'settings': 'Settings',
            'resellers': 'Reseller Management'
        };
        const pageTitle = document.getElementById('page-title');
        if (pageTitle) pageTitle.textContent = titleMap[pageName] || 'Dashboard';

        // Re-attach sidebar toggle listener if header was reloaded (not needed since header is static, but good practice)
        if (typeof initSidebar === 'function') initSidebar();

        // Dispatch Page Loaded Event for specific page scripts
        window.dispatchEvent(new CustomEvent('page-loaded', { detail: { page: pageName } }));

    } catch (error) {
        console.error(error);
        mainContent.innerHTML = `<div class="card"><h3 class="text-danger">Error</h3><p>Could not load page: ${pageName}</p></div>`;
    }
}

function updateActiveLink(pageName) {
    const links = document.querySelectorAll('.sidebar-menu a');
    links.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === pageName) {
            link.classList.add('active');
        }
    });
}

function getPageFromHash() {
    return window.location.hash.replace('#', '');
}

// Handle Browser Back/Forward
window.addEventListener('popstate', () => {
    const page = getPageFromHash() || 'dashboard';
    loadPage(page);
});
