// Console page JS

// ─── Command descriptions ─────────────────────────────────────────────────────

const CLI_HELP = {
    decoderawtransaction: {
        desc: 'Decode a raw transaction hex into a readable JSON object.',
        usage: 'decoderawtransaction <hex>',
    },
    decodescript: {
        desc: 'Decode a hex-encoded script and return its type and addresses.',
        usage: 'decodescript <hex>',
    },
    estimaterawfee: {
        desc: 'Estimate fee rates (in BTCP/kB) for a given confirmation target.',
        usage: 'estimaterawfee <conf_target> [threshold]',
    },
    estimatesmartfee: {
        desc: 'Estimate the smart fee per kB for a target number of confirmations.',
        usage: 'estimatesmartfee <conf_target> ["ECONOMICAL"|"CONSERVATIVE"]',
    },
    getaddednodeinfo: {
        desc: 'Get info on nodes manually added via addnode.',
        usage: 'getaddednodeinfo [node]',
    },
    getaddressinfo: {
        desc: 'Get detailed information about a given address.',
        usage: 'getaddressinfo <address>',
    },
    getbestblockhash: {
        desc: 'Return the hash of the best (tip) block in the longest chain.',
        usage: 'getbestblockhash',
    },
    getblock: {
        desc: 'Return block data for a given hash. Verbosity 0=hex, 1=JSON, 2=JSON with tx detail.',
        usage: 'getblock <hash> [verbosity=1]',
    },
    getblockchaininfo: {
        desc: 'Return general state of the blockchain (height, chain, sync progress, etc.).',
        usage: 'getblockchaininfo',
    },
    getblockcount: {
        desc: 'Return the current block height (number of blocks in the best chain).',
        usage: 'getblockcount',
    },
    getblockfilter: {
        desc: 'Return the BIP 157 block filter for a given block hash.',
        usage: 'getblockfilter <blockhash> [filtertype="basic"]',
    },
    getblockhash: {
        desc: 'Return the block hash at a given height.',
        usage: 'getblockhash <height>',
    },
    getblockheader: {
        desc: 'Return block header data. Set verbose=false for raw hex.',
        usage: 'getblockheader <hash> [verbose=true]',
    },
    getblockstats: {
        desc: 'Compute per-block statistics (fees, size, tx count, etc.).',
        usage: 'getblockstats <hash_or_height> [stats=[...]]',
    },
    getblocksubsidy: {
        desc: 'Return the current block subsidy (miner reward) at the current height.',
        usage: 'getblocksubsidy [height]',
    },
    getchaintips: {
        desc: 'Return info about all known chain tips (active, valid-fork, invalid, etc.).',
        usage: 'getchaintips',
    },
    getchaintxstats: {
        desc: 'Compute statistics about the total number and rate of transactions.',
        usage: 'getchaintxstats [nblocks] [blockhash]',
    },
    getconnectioncount: {
        desc: 'Return the number of active peer connections.',
        usage: 'getconnectioncount',
    },
    getdifficulty: {
        desc: 'Return the current proof-of-work difficulty target.',
        usage: 'getdifficulty',
    },
    getindexinfo: {
        desc: 'Return status of active indexes (txindex, blockfilterindex, coinstatsindex).',
        usage: 'getindexinfo [index_name]',
    },
    getmempoolancestors: {
        desc: 'Return all in-mempool ancestors of a transaction.',
        usage: 'getmempoolancestors <txid> [verbose=false]',
    },
    getmempooldescendants: {
        desc: 'Return all in-mempool descendants of a transaction.',
        usage: 'getmempooldescendants <txid> [verbose=false]',
    },
    getmempoolentry: {
        desc: 'Return mempool data (fee, size, ancestors) for a specific transaction.',
        usage: 'getmempoolentry <txid>',
    },
    getmempoolinfo: {
        desc: 'Return the current mempool state (size, bytes, fees, min fee rate).',
        usage: 'getmempoolinfo',
    },
    getmininginfo: {
        desc: 'Return mining-related info: difficulty, network hashrate, block template size.',
        usage: 'getmininginfo',
    },
    getnettotals: {
        desc: 'Return total bytes sent and received by the node since startup.',
        usage: 'getnettotals',
    },
    getnetworkhashps: {
        desc: 'Estimate the network hashes per second based on recent blocks.',
        usage: 'getnetworkhashps [nblocks=120] [height=-1]',
    },
    getnetworkinfo: {
        desc: 'Return P2P network info: version, subversion, connections, services, reachability.',
        usage: 'getnetworkinfo',
    },
    getpeerinfo: {
        desc: 'Return data about each connected peer (address, version, ping, traffic).',
        usage: 'getpeerinfo',
    },
    getrawmempool: {
        desc: 'Return all transaction IDs currently in the mempool.',
        usage: 'getrawmempool [verbose=false]',
    },
    getrawtransaction: {
        desc: 'Return raw transaction data. Set verbose=true for decoded JSON.',
        usage: 'getrawtransaction <txid> [verbose=false] [blockhash]',
    },
    gettxout: {
        desc: 'Return details about an unspent transaction output (UTXO).',
        usage: 'gettxout <txid> <n> [include_mempool=true]',
    },
    gettxoutproof: {
        desc: 'Return a hex-encoded proof that a transaction was included in a block.',
        usage: 'gettxoutproof ["txid",...] [blockhash]',
    },
    gettxoutsetinfo: {
        desc: 'Return statistics about the UTXO set. Warning: this is slow.',
        usage: 'gettxoutsetinfo',
    },
    listbanned: {
        desc: 'List all banned IP addresses and subnets.',
        usage: 'listbanned',
    },
    logging: {
        desc: 'Return currently active logging categories.',
        usage: 'logging',
    },
    uptime: {
        desc: 'Return the node uptime in seconds since it was started.',
        usage: 'uptime',
    },
    validateaddress: {
        desc: 'Validate a BitcoinPurple address and return detailed info.',
        usage: 'validateaddress <address>',
    },
    verifymessage: {
        desc: 'Verify a message signed with a BitcoinPurple address.',
        usage: 'verifymessage <address> <signature> <message>',
    },
    verifytxoutproof: {
        desc: 'Verify a transaction inclusion proof returned by gettxoutproof.',
        usage: 'verifytxoutproof <proof_hex>',
    },
};

// ─── API helpers ──────────────────────────────────────────────────────────────

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

// ─── Input parsing ────────────────────────────────────────────────────────────

function parseCliTokens(raw) {
    const tokens = [];
    let current = '';
    let inQuote = null;
    for (const ch of raw) {
        if (inQuote) {
            if (ch === inQuote) inQuote = null;
            else current += ch;
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

// ─── Output helpers ───────────────────────────────────────────────────────────

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
        const msg = typeof rpcErr === 'object' ? (rpcErr.message || JSON.stringify(rpcErr)) : String(rpcErr);
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

// ─── Autocomplete ─────────────────────────────────────────────────────────────

function initAutocomplete(input, dropdown, allMethods) {
    let activeIdx = -1;

    function getItems() {
        return Array.from(dropdown.querySelectorAll('.console-ac-item'));
    }

    function setActive(idx) {
        const items = getItems();
        items.forEach((el, i) => el.classList.toggle('console-ac-item--active', i === idx));
        activeIdx = idx;
    }

    function close() {
        dropdown.style.display = 'none';
        dropdown.innerHTML = '';
        activeIdx = -1;
    }

    function open(matches) {
        dropdown.innerHTML = '';
        activeIdx = -1;
        if (!matches.length) { close(); return; }

        matches.forEach(m => {
            const li = document.createElement('li');
            li.className = 'console-ac-item';
            const name = document.createElement('span');
            name.className = 'console-ac-name';
            name.textContent = m;
            const desc = document.createElement('span');
            desc.className = 'console-ac-desc';
            desc.textContent = CLI_HELP[m] ? CLI_HELP[m].desc.split('.')[0] : '';
            li.appendChild(name);
            li.appendChild(desc);
            li.addEventListener('mousedown', e => {
                e.preventDefault();
                input.value = m + ' ';
                close();
                input.focus();
            });
            dropdown.appendChild(li);
        });
        dropdown.style.display = 'block';
    }

    input.addEventListener('input', () => {
        const val = input.value;
        // Only autocomplete the first token (method name)
        if (val.includes(' ') || !val) { close(); return; }
        const q = val.toLowerCase();
        const matches = allMethods.filter(m => m.startsWith(q) && m !== q);
        open(matches.slice(0, 8));
    });

    input.addEventListener('keydown', e => {
        const items = getItems();
        if (!items.length) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setActive(Math.min(activeIdx + 1, items.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setActive(Math.max(activeIdx - 1, 0));
        } else if ((e.key === 'Enter' || e.key === 'Tab') && activeIdx >= 0) {
            e.preventDefault();
            const chosen = items[activeIdx].querySelector('.console-ac-name').textContent;
            input.value = chosen + ' ';
            close();
        } else if (e.key === 'Escape') {
            close();
        }
    });

    document.addEventListener('click', e => {
        if (!dropdown.contains(e.target) && e.target !== input) close();
    });
}

// ─── Help panel ───────────────────────────────────────────────────────────────

function initHelp(helpBtn, helpPanel, helpBody, helpSearch) {
    const allEntries = Object.entries(CLI_HELP).sort((a, b) => a[0].localeCompare(b[0]));

    function renderRows(filter) {
        const q = (filter || '').toLowerCase();
        helpBody.innerHTML = '';
        allEntries
            .filter(([cmd, info]) => !q || cmd.includes(q) || info.desc.toLowerCase().includes(q))
            .forEach(([cmd, info]) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="help-cmd">${cmd}</td>
                    <td class="help-desc">${info.desc}</td>
                    <td class="help-usage">${info.usage}</td>
                `;
                tr.querySelector('.help-cmd').addEventListener('click', () => {
                    document.getElementById('consoleInput').value = cmd + ' ';
                    helpPanel.style.display = 'none';
                    helpBtn.textContent = '? Help';
                    document.getElementById('consoleInput').focus();
                });
                helpBody.appendChild(tr);
            });
    }

    renderRows('');

    helpBtn.addEventListener('click', () => {
        const open = helpPanel.style.display !== 'none';
        helpPanel.style.display = open ? 'none' : 'block';
        helpBtn.textContent = open ? '? Help' : '✕ Close Help';
        if (!open) { helpSearch.value = ''; renderRows(''); helpSearch.focus(); }
    });

    helpSearch.addEventListener('input', () => renderRows(helpSearch.value));
}

// ─── Init ─────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
    const form       = document.getElementById('consoleForm');
    const input      = document.getElementById('consoleInput');
    const output     = document.getElementById('consoleOutput');
    const runBtn     = form.querySelector('.console-run-btn');
    const clearBtn   = document.getElementById('consoleClearBtn');
    const dropdown   = document.getElementById('consoleAutocomplete');
    const helpBtn    = document.getElementById('consoleHelpBtn');
    const helpPanel  = document.getElementById('consoleHelpPanel');
    const helpBody   = document.getElementById('consoleHelpBody');
    const helpSearch = document.getElementById('consoleHelpSearch');

    const allMethods = Object.keys(CLI_HELP).sort();

    initAutocomplete(input, dropdown, allMethods);
    initHelp(helpBtn, helpPanel, helpBody, helpSearch);

    clearBtn.addEventListener('click', () => {
        output.innerHTML = '';
        input.focus();
    });

    form.addEventListener('submit', async e => {
        e.preventDefault();
        const raw = input.value.trim();
        if (!raw) return;
        input.value = '';
        runBtn.disabled = true;
        try { await runConsoleCommand(raw); }
        finally { runBtn.disabled = false; input.focus(); }
    });

    input.focus();
});
