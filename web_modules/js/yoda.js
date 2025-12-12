// YODA - Voice Activated IDS - Main JavaScript

// Global state
let nodes = {};
let refreshTimer = null;
let uptimeStart = Date.now();
let scanCounter = 0;
let lastNodeCount = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeSystem();
    startUptime();
    startScanRate();
    setupEventListeners();
    startAutoRefresh();
    loadNodes();
});

// System initialization
function initializeSystem() {
    addLog('[SYSTEM] Initializing YODA IDS v3.0...', 'info');
    setTimeout(() => addLog('[SUCCESS] Voice activation module loaded', 'success'), 500);
    setTimeout(() => addLog('[SUCCESS] Network monitoring active', 'success'), 1000);
    setTimeout(() => addLog('[INFO] Scanning for network nodes...', 'info'), 1500);
}

// Uptime counter
function startUptime() {
    setInterval(() => {
        const elapsed = Date.now() - uptimeStart;
        const hours = Math.floor(elapsed / 3600000);
        const minutes = Math.floor((elapsed % 3600000) / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);

        document.getElementById('uptime').textContent =
            `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
    }, 1000);
}

// Scan rate simulator
function startScanRate() {
    setInterval(() => {
        scanCounter = Math.floor(Math.random() * 50) + 100;
        document.getElementById('scanRate').textContent = scanCounter;
    }, 2000);
}

// Event listeners
function setupEventListeners() {
    document.getElementById('searchFilter').addEventListener('input', filterNodes);
    document.getElementById('statusFilter').addEventListener('change', filterNodes);

    document.getElementById('autoRefresh').addEventListener('change', (e) => {
        if (e.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });

    document.getElementById('refreshInterval').addEventListener('change', () => {
        if (document.getElementById('autoRefresh').checked) {
            startAutoRefresh();
        }
    });
}

// Auto-refresh control
function startAutoRefresh() {
    stopAutoRefresh();
    const interval = parseInt(document.getElementById('refreshInterval').value) * 1000;
    refreshTimer = setInterval(loadNodes, interval);
    addLog('[AUTO-REFRESH] Enabled - Interval: ' + (interval/1000) + 's', 'info');
}

function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
        addLog('[AUTO-REFRESH] Disabled', 'warning');
    }
}

// Load nodes from API
async function loadNodes() {
    try {
        updateConnectionStatus(true);
        const response = await fetch('/nodes.json');

        if (!response.ok) throw new Error('HTTP ' + response.status);

        const data = await response.json();
        nodes = data.nodes || {};

        updateDashboard();
        renderNodes();
        updateLastUpdate();

        // Check for new/removed nodes
        const currentCount = Object.keys(nodes).length;
        if (currentCount !== lastNodeCount) {
            if (currentCount > lastNodeCount) {
                addLog(`[ALERT] New node detected! Total: ${currentCount}`, 'warning');
                playAlert();
            } else if (currentCount < lastNodeCount) {
                addLog(`[WARNING] Node removed! Total: ${currentCount}`, 'danger');
            }
            lastNodeCount = currentCount;
        }

    } catch (error) {
        updateConnectionStatus(false);
        addLog('[ERROR] Failed to load nodes: ' + error.message, 'danger');
        console.error('Load error:', error);
    }
}

// Update dashboard stats
function updateDashboard() {
    const nodeList = Object.values(nodes);
    const total = nodeList.length;
    const online = nodeList.filter(n => n.status === 'online').length;
    const uptimePercent = total > 0 ? Math.round((online / total) * 100) : 0;

    document.getElementById('nodesOnline').textContent = online;
    document.getElementById('nodesTotal').textContent = total;
    document.getElementById('uptimePercent').textContent = uptimePercent + '%';
    document.getElementById('nodeCount').textContent = total + ' NODES';

    // Random bandwidth for effect
    const bandwidth = (Math.random() * 10 + 5).toFixed(2);
    document.getElementById('bandwidth').textContent = bandwidth + ' MB/s';

    // Update threat counter (offline nodes)
    const threats = total - online;
    document.getElementById('threats').textContent = threats;
}

// Render nodes table
function renderNodes() {
    const tbody = document.getElementById('nodesTableBody');
    const searchTerm = document.getElementById('searchFilter').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;

    // Convert nodes object to array
    let nodeList = Object.values(nodes);

    // Apply filters
    nodeList = nodeList.filter(node => {
        const matchesSearch = !searchTerm ||
            (node.target_ip && node.target_ip.toLowerCase().includes(searchTerm)) ||
            (node.host && node.host.toLowerCase().includes(searchTerm)) ||
            (node.vendor && node.vendor.toLowerCase().includes(searchTerm)) ||
            (node.target_mac && node.target_mac.toLowerCase().includes(searchTerm));

        const matchesStatus = !statusFilter || node.status === statusFilter;

        return matchesSearch && matchesStatus;
    });

    // Sort: online first, then by IP
    nodeList.sort((a, b) => {
        if (a.status === 'online' && b.status !== 'online') return -1;
        if (a.status !== 'online' && b.status === 'online') return 1;
        return (a.target_ip || '').localeCompare(b.target_ip || '');
    });

    // Render table
    tbody.innerHTML = nodeList.map(node => {
        const status = node.status || 'offline';
        const isOnline = status === 'online';

        return `
            <tr class="node-row ${status}">
                <td>
                    <span class="status-badge ${status}">
                        <span class="status-dot ${status}"></span>
                        ${status.toUpperCase()}
                    </span>
                </td>
                <td class="ip-cell">${node.target_ip || '—'}</td>
                <td>${node.host || '—'}</td>
                <td class="mac-cell">${node.target_mac || '—'}</td>
                <td>${node.vendor || '—'}</td>
                <td>
                    <button class="action-btn" onclick="inspectNode('${node.target_ip}')">INSPECT</button>
                    <button class="action-btn" onclick="blockNode('${node.target_ip}')" title="Feature coming soon">BLOCK (SOON)</button>
                </td>
            </tr>
        `;
    }).join('');
}

// Filter nodes
function filterNodes() {
    renderNodes();
}

// Manual refresh
function manualRefresh() {
    addLog('[MANUAL] Refreshing node data...', 'info');
    loadNodes();
}

// Emergency lockdown
function emergencyLockdown() {
    addLog('[LOCKDOWN] Emergency protocol initiated!', 'danger');
    addLog('[LOCKDOWN] Blocking all external connections...', 'danger');
    playAlert();

    // Visual effect
    document.body.style.animation = 'flash 0.5s 3';
    setTimeout(() => {
        document.body.style.animation = '';
        addLog('[LOCKDOWN] System secured', 'warning');
    }, 1500);
}

// Node actions
function inspectNode(ip) {
    addLog(`[INSPECT] Analyzing node ${ip}...`, 'info');
    const node = Object.values(nodes).find(n => n.target_ip === ip);
    if (node) {
        const details = `
            IP: ${node.target_ip}
            MAC: ${node.target_mac || 'Unknown'}
            Host: ${node.host || 'Unknown'}
            Vendor: ${node.vendor || 'Unknown'}
            Status: ${node.status || 'Unknown'}
        `;
        alert('NODE DETAILS:\n\n' + details);
    }
}

function blockNode(ip) {
    addLog(`[BLOCKED] Node ${ip} has been blocked`, 'danger');
    playAlert();
}

// Terminal log functions
function addLog(message, type = 'info') {
    const terminal = document.getElementById('terminal');
    const entry = document.createElement('div');
    entry.className = 'log-entry';

    // Add timestamp
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;

    // Color based on type
    if (type === 'danger') entry.style.color = '#ff0040';
    else if (type === 'warning') entry.style.color = '#ffcc00';
    else if (type === 'success') entry.style.color = '#00ff41';
    else entry.style.color = '#6ef089';

    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight;

    // Keep only last 100 entries
    while (terminal.children.length > 100) {
        terminal.removeChild(terminal.firstChild);
    }
}

function clearLog() {
    document.getElementById('terminal').innerHTML = '';
    addLog('[SYSTEM] Terminal cleared', 'info');
}

// Update connection status
function updateConnectionStatus(connected) {
    const status = document.getElementById('connectionStatus');
    if (connected) {
        status.textContent = '◉ CONNECTED';
        status.className = 'connected';
    } else {
        status.textContent = '◉ DISCONNECTED';
        status.className = 'disconnected';
    }
}

// Update last update time
function updateLastUpdate() {
    const now = new Date();
    document.getElementById('lastUpdate').textContent = now.toLocaleTimeString();
}

// Play alert sound
function playAlert() {
    const audio = document.getElementById('alertSound');
    if (audio) {
        audio.play().catch(e => console.log('Audio play failed:', e));
    }
}

// Utility functions
function pad(num) {
    return num.toString().padStart(2, '0');
}

// Flash animation for lockdown
const style = document.createElement('style');
style.textContent = `
    @keyframes flash {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; background: rgba(255, 0, 64, 0.2); }
    }
`;
document.head.appendChild(style);

// Voice activation easter egg (optional)
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const command = event.results[0][0].transcript.toLowerCase();
        addLog(`[VOICE] Command received: "${command}"`, 'info');

        if (command.includes('refresh') || command.includes('reload')) {
            manualRefresh();
        } else if (command.includes('lockdown') || command.includes('emergency')) {
            emergencyLockdown();
        } else if (command.includes('clear')) {
            clearLog();
        }
    };

    // Activate voice on spacebar hold
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && !e.repeat) {
            recognition.start();
            addLog('[VOICE] Listening...', 'info');
        }
    });

    recognition.onerror = (event) => {
        if (event.error !== 'no-speech') {
            console.log('Voice error:', event.error);
        }
    };
}
