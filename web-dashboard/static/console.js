// Console page JS

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

async function apiFetch(url, options = {}) {
    const apiKey = await _getApiKey();
    const headers = { ...(options.headers || {}) };
    if (apiKey) headers['X-API-Key'] = apiKey;
    return fetch(url, { ...options, headers });
}

function parseCliTokens(raw) {
    const tokens = [];
    let current = '';
    let inQuote = null;
    for (let i = 0; i < raw.length; i++) {
        const ch = raw[i];
        if (inQuote) {
            if (ch === inQuote) { inQuote = null; }
            else { current += ch; }
        } else if (ch === '"' || ch === "'") {
            inQuote = ch;
        } else if (ch === ' ' || ch === '\t') {
            if (current !== '') { tokens.push(current); current = ''; }
        } else {
            current += ch;
        }
    }
    if (current !== '') tokens.push(current);
    return tokens;
}

function coerceParam(s) {
    try { return JSON.parse(s); } catch { return s; }
}

function consoleAppend(output, text, cls) {
    if (cls === 'sep') {
        const hr = document.createElement('div');
        hr.className = 'console-line console-line--sep';
        output.appendChild(hr);
        return;
    }
    const el = document.createElement('div');
    el.className = 'console-line console-line--' + cls;
    el.textContent = text;
    output.appendChild(el);
    output.scrollTop = output.scrollHeight;
}

async function runConsoleCommand(raw) {
    const output = document.getElementById('consoleOutput');
    const tokens = parseCliTokens(raw.trim());
    if (!tokens.length) return;

    const method = tokens[0].toLowerCase();
    const params = tokens.slice(1).map(coerceParam);

    consoleAppend(output, '$ ' + raw.trim(), 'cmd');

    let data;
    try {
        const res = await apiFetch('/api/cli', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ method, params }),
        });
        data = await res.json();
    } catch (e) {
        consoleAppend(output, 'Network error: ' + e.message, 'error');
        consoleAppend(output, '', 'sep');
        return;
    }

    if (data.error) {
        consoleAppend(output, 'Error: ' + (typeof data.error === 'object' ? JSON.stringify(data.error) : data.error), 'error');
    } else if (data.rpc_error) {
        const rpcErr = data.rpc_error;
        const msg = typeof rpcErr === 'object'
            ? (rpcErr.message || JSON.stringify(rpcErr))
            : String(rpcErr);
        consoleAppend(output, 'RPC error: ' + msg, 'error');
    } else {
        const result = data.result;
        const text = result === null ? 'null'
            : typeof result === 'object' ? JSON.stringify(result, null, 2)
            : String(result);
        consoleAppend(output, text, 'result');
    }
    consoleAppend(output, '', 'sep');
}

document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('consoleForm');
    const input = document.getElementById('consoleInput');
    const output = document.getElementById('consoleOutput');
    const btn = form.querySelector('.console-run-btn');
    const clearBtn = document.getElementById('consoleClearBtn');
    const toggle = document.getElementById('consoleMethodsToggle');
    const methodsList = document.getElementById('consoleMethodsList');

    // Load allowed methods
    try {
        const res = await apiFetch('/api/cli/methods');
        const data = await res.json();
        if (data.methods) {
            data.methods.forEach(m => {
                const tag = document.createElement('span');
                tag.className = 'console-method-tag';
                tag.textContent = m;
                tag.addEventListener('click', () => {
                    input.value = m + ' ';
                    input.focus();
                });
                methodsList.appendChild(tag);
            });
        }
    } catch { /* ignore */ }

    toggle.addEventListener('click', e => {
        e.preventDefault();
        const visible = methodsList.style.display !== 'none';
        methodsList.style.display = visible ? 'none' : 'flex';
        toggle.textContent = visible ? 'show allowed commands' : 'hide allowed commands';
    });

    clearBtn.addEventListener('click', () => {
        output.innerHTML = '';
        input.focus();
    });

    form.addEventListener('submit', async e => {
        e.preventDefault();
        const raw = input.value.trim();
        if (!raw) return;
        input.value = '';
        btn.disabled = true;
        try { await runConsoleCommand(raw); }
        finally { btn.disabled = false; input.focus(); }
    });

    input.focus();
});
