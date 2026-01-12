const API_BASE = 'http://localhost:8000';

window.addEventListener('page-loaded', (e) => {
    if (e.detail.page === 'whatsapp-numbers') {
        initDevicesPage();
    }
});

function initDevicesPage() {
    console.log('Linked Devices Page Initialized');
    loadUsers();

    const form = document.getElementById('connect-device-form');
    if (form) {
        form.removeEventListener('submit', handleConnectDevice);
        form.addEventListener('submit', handleConnectDevice);
    }
}

async function loadUsers() {
    const select = document.getElementById('user-select');
    if (!select) return;

    try {
        const response = await fetch(`${API_BASE}/business-users`);
        if (response.ok) {
            const users = await response.json();
            if (users.length === 0) {
                select.innerHTML = '<option value="">No Users Found</option>';
            } else {
                select.innerHTML = '<option value="">Select User</option>' +
                    users.map(u => `<option value="${u.user_id}">${u.profile.name}</option>`).join('');
            }
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Global scope
window.loadDevices = async function (userId) {
    const tbody = document.getElementById('devices-table-body');
    if (!tbody) return;

    if (!userId) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-secondary);">Select a user to view devices.</td></tr>';
        return;
    }

    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Loading...</td></tr>';

    try {
        const response = await fetch(`${API_BASE}/devices?user_id=${userId}`);
        const devices = await response.json();

        if (devices.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No devices connected.</td></tr>';
            return;
        }

        tbody.innerHTML = devices.map(d => `
            <tr>
                <td style="padding: 1rem; font-weight: 500;">${d.device_name}</td>
                <td style="padding: 1rem;">${d.device_type}</td>
                <td style="padding: 1rem;">
                    <span class="badge ${d.session_status === 'connected' ? 'badge-success' : 'badge-danger'}">
                        ${d.session_status}
                    </span>
                </td>
                <td style="padding: 1rem;">
                    <div id="session-${d.device_id}">
                        <span class="badge badge-gray" style="font-size: 0.75rem;">Checking...</span>
                    </div>
                </td>
                <td style="padding: 1rem;">${new Date(d.last_active).toLocaleString()}</td>
                <td style="padding: 1rem;">
                     <button class="btn btn-danger btn-sm" onclick="disconnectDevice('${d.device_id}')">Disconnect</button>
                     <button class="btn btn-secondary btn-sm" onclick="createSession('${d.device_id}')" style="margin-left: 0.5rem;">New Session</button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading devices:', error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: red;">Error loading devices.</td></tr>';
    }
};

window.refreshDevices = function () {
    const userId = document.getElementById('user-select').value;
    loadDevices(userId);
};

window.simulateScan = function () {
    // 1. Validate Form
    const userId = document.getElementById('user-select').value;
    const name = document.querySelector('input[name="device_name"]').value;

    if (!userId || !name) {
        alert('Please select a user and enter a device name.');
        return;
    }

    // 2. Show mock QR
    const btn = document.getElementById('scan-btn');
    const submitBtn = document.getElementById('submit-btn');
    const qr = document.getElementById('qr-container');

    btn.style.display = 'none';
    qr.style.display = 'block';

    // 3. Simulate processing
    setTimeout(() => {
        qr.innerHTML = `
            <div style="width: 200px; height: 200px; background: #dcfce7; margin: 0 auto; display: flex; align-items: center; justify-content: center; border-radius: 8px;">
                <span style="color: #15803d; font-weight: bold; font-size: 1.5rem;">✔ Scanned!</span>
            </div>
             <p style="margin-top: 1rem; font-weight: bold; color: #15803d;">Ready to connect</p>
        `;
        submitBtn.style.display = 'inline-flex';
    }, 2000);
};

async function handleConnectDevice(e) {
    e.preventDefault();
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.textContent = 'Connecting...';
    submitBtn.disabled = true;

    const formData = new FormData(e.target);
    const payload = {
        user_id: formData.get('user_id'),
        device_name: formData.get('device_name'),
        device_type: formData.get('device_type')
    };

    try {
        const response = await fetch(`${API_BASE}/devices/connect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert('Device connected successfully!');
            // Reset UI
            document.getElementById('qr-container').style.display = 'none';
            document.getElementById('scan-btn').style.display = 'inline-flex';
            submitBtn.style.display = 'none';
            e.target.reset();

            // Refresh list
            loadDevices(payload.user_id);
            // Re-select user (since reset cleared it)
            document.getElementById('user-select').value = payload.user_id;
        } else {
            const err = await response.json();
            alert(`Error: ${err.detail}`);
        }

    } catch (error) {
        console.error(error);
        alert('Connection failed.');
    } finally {
        submitBtn.textContent = 'Confirm Connection';
        submitBtn.disabled = false;
    }
}

window.disconnectDevice = async function (deviceId) {
    if (!confirm('Are you sure you want to disconnect this device?')) return;

    try {
        const response = await fetch(`${API_BASE}/devices/${deviceId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            refreshDevices();
        } else {
            alert('Failed to disconnect');
        }
    } catch (error) {
        console.error(error);
        alert('Error disconnecting');
    }
};

window.createSession = async function (deviceId) {
    try {
        const response = await fetch(`${API_BASE}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_id: deviceId })
        });

        if (response.ok) {
            const session = await response.json();
            const badge = document.getElementById(`session-${deviceId}`);
            if (badge) {
                badge.innerHTML = `<span class="badge badge-success" title="Token: ${session.session_token.substring(0, 10)}...">Active</span>`;
            }
            alert('New Session Token Generated!');
        } else {
            alert('Failed to create session');
        }
    } catch (e) {
        console.error(e);
        alert('Error creating session');
    }
};
