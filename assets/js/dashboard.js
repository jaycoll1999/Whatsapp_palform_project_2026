const API_BASE = 'http://localhost:8000';

window.addEventListener('page-loaded', (e) => {
    if (e.detail.page === 'dashboard') {
        initDashboard();
    }
});

function initDashboard() {
    console.log('Dashboard Initialized');
    populateAnalyticResellers();
}

async function populateAnalyticResellers() {
    const select = document.getElementById('analytics-reseller-select');
    if (!select) return;

    try {
        const response = await fetch(`${API_BASE}/resellers`);
        if (response.ok) {
            const resellers = await response.json();
            if (resellers.length > 0) {
                select.innerHTML = '<option value="">Select Reseller</option>' +
                    resellers.map(r => `<option value="${r.user_id}">${r.profile.name} (${r.business.business_name || 'No Biz'})</option>`).join('');

                // Auto-select first one for convenience
                if (resellers.length > 0) {
                    select.value = resellers[0].user_id;
                    loadAnalytics(resellers[0].user_id);
                }
            } else {
                select.innerHTML = '<option value="">No Resellers Found</option>';
            }
        }
    } catch (error) {
        console.error(error);
    }
}

window.loadAnalytics = async function (resellerId) {
    if (!resellerId) return;

    // Reset UI
    document.getElementById('stat-purchased').textContent = '...';
    document.getElementById('stat-distributed').textContent = '...';
    document.getElementById('stat-balance').textContent = '...';
    document.getElementById('stat-users').textContent = '...';

    const tbody = document.getElementById('analytics-table-body');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Loading...</td></tr>';

    try {
        const response = await fetch(`${API_BASE}/analytics/reseller/${resellerId}`);
        if (!response.ok) throw new Error('Failed to fetch analytics');

        const data = await response.json();

        // Update Cards
        animateValue('stat-purchased', data.total_credits_purchased);
        animateValue('stat-distributed', data.total_credits_distributed);
        animateValue('stat-balance', data.remaining_credits);
        animateValue('stat-users', data.active_business_users);

        // Update Table
        if (data.business_user_stats.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No business users found.</td></tr>';
        } else {
            tbody.innerHTML = data.business_user_stats.map(u => {
                const percent = u.credits_allocated > 0 ? Math.round((u.credits_used / u.credits_allocated) * 100) : 0;
                return `
                <tr>
                    <td style="padding: 1rem; font-weight: 500;">${u.name}</td>
                    <td style="padding: 1rem;">${u.credits_allocated}</td>
                    <td style="padding: 1rem;">${u.credits_used}</td>
                    <td style="padding: 1rem;">${u.credits_remaining}</td>
                    <td style="padding: 1rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="flex: 1; height: 6px; background: #eee; border-radius: 3px; overflow: hidden;">
                                <div style="width: ${percent}%; height: 100%; background: var(--primary);"></div>
                            </div>
                            <span style="font-size: 0.8rem;">${percent}%</span>
                        </div>
                    </td>
                </tr>
                `;
            }).join('');
        }

    } catch (error) {
        console.error(error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">Error loading analytics.</td></tr>';
    }
};

function animateValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
    // Animation logic can be added here if desired
}
