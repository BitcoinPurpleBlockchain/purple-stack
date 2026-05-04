// Electrum Active Servers Page JavaScript

function esc(value) {
    const el = document.createElement('span');
    el.textContent = (value == null ? '' : String(value));
    return el.innerHTML;
}

let _apiKeyPromise = null;
async function _getApiKey() {
    if (_apiKeyPromise === null) {
        _apiKeyPromise = fetch('/api/config')
            .then(r => r.ok ? r.json() : {})
            .then(d => (d.api_key || '').trim())
            .catch(() => '');
    }
    return _apiKeyPromise;
}

async function apiFetch(url) {
    const apiKey = await _getApiKey();
    const headers = apiKey ? { 'X-API-Key': apiKey } : {};
    return fetch(url, { headers });
}

function updateLastUpdateTime() {
    const now = new Date().toLocaleString();
    document.getElementById('lastUpdate').textContent = now;
}

async function updateElectrumServers() {
    try {
        const response = await apiFetch('/api/electrumx/servers');
        const data = await response.json();

        if (data.error) {
            console.error('Electrum servers error:', data.error);
            return;
        }

        const servers = Array.isArray(data.servers) ? data.servers : [];
        const tbody = document.getElementById('electrumServersTable');
        tbody.innerHTML = '';

        if (servers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No active servers found</td></tr>';
            document.getElementById('totalServers').textContent = '0';
            return;
        }

        servers.forEach(server => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="peer-addr">${esc(server.host || '--')}</td>
                <td>${esc(server.tcp_port || '--')}</td>
                <td>${esc(server.ssl_port || '--')}</td>
                <td>${server.tcp_reachable === true ? 'Yes' : 'No'}</td>
                <td>${server.ssl_reachable === true ? 'Yes' : 'No'}</td>
            `;
            tbody.appendChild(row);
        });

        document.getElementById('totalServers').textContent = String(servers.length);
    } catch (error) {
        console.error('Error fetching Electrum servers:', error);
        document.getElementById('electrumServersTable').innerHTML =
            '<tr><td colspan="5" class="loading">Error loading servers</td></tr>';
    }
}

async function updateAll() {
    updateLastUpdateTime();
    await updateElectrumServers();
}

document.addEventListener('DOMContentLoaded', async () => {
    await updateAll();
    setInterval(updateAll, 10000);
});
