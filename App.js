/**
 * Pavani Bot Creator V10 - Frontend Application
 * Real-time dashboard with WebSocket support
 */

// Global state
let currentFilter = 'all';
let bots = [];
let activeBotId = null;
let activeWebSocket = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    setupFileInputs();
});

// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

async function initDashboard() {
    await loadStats();
    await loadBots();
    startAutoRefresh();
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('totalBots').textContent = stats.total || 0;
        document.getElementById('runningBots').textContent = stats.running || 0;
        document.getElementById('stoppedBots').textContent = stats.stopped || 0;
        document.getElementById('errorBots').textContent = stats.error || 0;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

async function loadBots() {
    try {
        const response = await fetch('/api/bots');
        bots = await response.json();
        
        renderBots();
        await loadStats(); // Update stats after loading bots
    } catch (error) {
        console.error('Failed to load bots:', error);
        showToast('Failed to load bots', 'error');
    }
}

function renderBots() {
    const grid = document.getElementById('botsGrid');
    const empty = document.getElementById('emptyState');
    
    // Filter bots
    const filtered = bots.filter(bot => {
        if (currentFilter === 'all') return true;
        return bot.status === currentFilter;
    });
    
    if (filtered.length === 0) {
        grid.innerHTML = '';
        empty.style.display = 'block';
        return;
    }
    
    empty.style.display = 'none';
    
    grid.innerHTML = filtered.map(bot => `
        <div class="bot-card" onclick="openBotModal('${bot.bot_id}')">
            <div class="bot-header">
                <div>
                    <div class="bot-name">🤖 ${bot.name}</div>
                    <div class="bot-id">#${bot.bot_id}</div>
                </div>
                <div class="bot-status status-${bot.status}">
                    ${getStatusIcon(bot.status)} ${bot.status.toUpperCase()}
                </div>
            </div>
            
            <div class="bot-metrics">
                <div class="metric">
                    <div class="metric-value">${bot.uptime || '00:00:00'}</div>
                    <div class="metric-label">Uptime</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${bot.metrics.messages_total || 0}</div>
                    <div class="metric-label">Messages</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${bot.metrics.errors_total || 0}</div>
                    <div class="metric-label">Errors</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${bot.metrics.restarts_total || 0}</div>
                    <div class="metric-label">Restarts</div>
                </div>
            </div>
            
            <div class="bot-actions" onclick="event.stopPropagation()">
                <button class="btn btn-secondary" onclick="restartBot('${bot.bot_id}')">
                    🔄 Restart
                </button>
                <button class="btn btn-secondary" onclick="stopBot('${bot.bot_id}')">
                    ⏹️ Stop
                </button>
                <button class="btn btn-secondary" onclick="deleteBot('${bot.bot_id}')">
                    🗑️ Delete
                </button>
            </div>
        </div>
    `).join('');
}

function getStatusIcon(status) {
    const icons = {
        'running': '🟢',
        'stopped': '⚪',
        'error': '🔴',
        'initializing': '🟡',
        'crashed': '💀'
    };
    return icons[status] || '⚪';
}

function filterBots() {
    currentFilter = document.getElementById('statusFilter').value;
    renderBots();
}

function startAutoRefresh() {
    setInterval(async () => {
        if (!document.getElementById('botModal').classList.contains('active')) {
            await loadBots();
        }
    }, 5000); // Refresh every 5 seconds
}

// ═══════════════════════════════════════════════════════════════════════════
// BOT ACTIONS
// ═══════════════════════════════════════════════════════════════════════════

async function restartBot(botId) {
    try {
        const response = await fetch(`/api/bots/${botId}/restart`, { method: 'POST' });
        if (response.ok) {
            showToast('Bot restarting...', 'success');
            setTimeout(() => loadBots(), 2000);
        }
    } catch (error) {
        showToast('Failed to restart bot', 'error');
    }
}

async function stopBot(botId) {
    try {
        const response = await fetch(`/api/bots/${botId}/stop`, { method: 'POST' });
        if (response.ok) {
            showToast('Bot stopped', 'success');
            setTimeout(() => loadBots(), 1000);
        }
    } catch (error) {
        showToast('Failed to stop bot', 'error');
    }
}

async function deleteBot(botId) {
    if (!confirm('Are you sure you want to delete this bot? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/bots/${botId}`, { method: 'DELETE' });
        if (response.ok) {
            showToast('Bot deleted', 'success');
            await loadBots();
        }
    } catch (error) {
        showToast('Failed to delete bot', 'error');
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// DEPLOY MODAL
// ═══════════════════════════════════════════════════════════════════════════

function openDeployModal() {
    document.getElementById('deployModal').classList.add('active');
    document.getElementById('deployForm').reset();
    resetFileInputs();
}

function closeDeployModal() {
    document.getElementById('deployModal').classList.remove('active');
}

function setupFileInputs() {
    const botFile = document.getElementById('botFile');
    const reqFile = document.getElementById('reqFile');
    
    botFile.addEventListener('change', (e) => {
        updateFileInput('botFileUpload', e.target.files[0]);
    });
    
    reqFile.addEventListener('change', (e) => {
        updateFileInput('reqFileUpload', e.target.files[0]);
    });
}

function updateFileInput(uploadId, file) {
    const upload = document.getElementById(uploadId);
    if (file) {
        upload.classList.add('has-file');
        upload.querySelector('.file-text').textContent = `✅ ${file.name}`;
    }
}

function resetFileInputs() {
    document.getElementById('botFileUpload').classList.remove('has-file');
    document.getElementById('reqFileUpload').classList.remove('has-file');
    document.getElementById('botFileUpload').querySelector('.file-text').textContent = 'Click to select bot.py file';
    document.getElementById('reqFileUpload').querySelector('.file-text').textContent = 'Click to select requirements.txt';
}

document.getElementById('deployForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = e.target.querySelector('button[type="submit"]');
    const btnText = document.getElementById('deployBtnText');
    const originalText = btnText.innerHTML;
    
    btn.disabled = true;
    btnText.innerHTML = '<span class="spinner"></span> Deploying...';
    
    try {
        const formData = new FormData(e.target);
        
        const response = await fetch('/api/bots', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('Bot deployed successfully!', 'success');
            closeDeployModal();
            await loadBots();
        } else {
            throw new Error(result.error || 'Deployment failed');
        }
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.disabled = false;
        btnText.innerHTML = originalText;
    }
});

// ═══════════════════════════════════════════════════════════════════════════
// BOT MODAL (Console View)
// ═══════════════════════════════════════════════════════════════════════════

async function openBotModal(botId) {
    activeBotId = botId;
    const bot = bots.find(b => b.bot_id === botId);
    
    if (!bot) return;
    
    document.getElementById('botModalTitle').textContent = `🤖 ${bot.name}`;
    document.getElementById('botModal').classList.add('active');
    
    // Load logs
    await loadBotLogs(botId);
    
    // Connect WebSocket
    connectWebSocket(botId);
}

function closeBotModal() {
    document.getElementById('botModal').classList.remove('active');
    
    if (activeWebSocket) {
        activeWebSocket.close();
        activeWebSocket = null;
    }
    
    activeBotId = null;
}

async function loadBotLogs(botId) {
    const console = document.getElementById('telegramConsole');
    console.innerHTML = '<div class="console-loading"><div class="spinner"></div><span>Loading logs...</span></div>';
    
    try {
        const response = await fetch(`/api/bots/${botId}/logs?limit=100`);
        const data = await response.json();
        
        renderLogs(data.logs || []);
    } catch (error) {
        console.innerHTML = '<div class="log-error">Failed to load logs</div>';
    }
}

function renderLogs(logs) {
    const console = document.getElementById('telegramConsole');
    
    if (logs.length === 0) {
        console.innerHTML = '<div class="log-info">No logs yet...</div>';
        return;
    }
    
    console.innerHTML = logs.map(log => {
        const time = new Date(log.ts).toLocaleTimeString();
        return `
            <div class="log-entry log-${log.level}">
                <span class="log-timestamp">[${time}]</span>
                <span>${escapeHtml(log.msg)}</span>
            </div>
        `;
    }).join('');
    
    console.scrollTop = console.scrollHeight;
}

function connectWebSocket(botId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${botId}`);
    
    activeWebSocket = ws;
    
    ws.onopen = () => {
        updateConsoleStatus('connected');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'init') {
            renderLogs(data.logs);
        } else if (data.type === 'log') {
            appendLog(data.data);
        }
    };
    
    ws.onclose = () => {
        updateConsoleStatus('disconnected');
    };
    
    ws.onerror = () => {
        updateConsoleStatus('error');
    };
}

function appendLog(log) {
    const console = document.getElementById('telegramConsole');
    const time = new Date(log.ts).toLocaleTimeString();
    
    const entry = document.createElement('div');
    entry.className = `log-entry log-${log.level}`;
    entry.innerHTML = `
        <span class="log-timestamp">[${time}]</span>
        <span>${escapeHtml(log.msg)}</span>
    `;
    
    console.appendChild(entry);
    console.scrollTop = console.scrollHeight;
}

function updateConsoleStatus(status) {
    const statusEl = document.getElementById('consoleStatus');
    const dot = statusEl.querySelector('.status-dot');
    const text = statusEl.querySelector('.status-text');
    
    const states = {
        'connected': { color: 'var(--success)', text: 'Connected' },
        'disconnected': { color: 'var(--text-muted)', text: 'Disconnected' },
        'error': { color: 'var(--error)', text: 'Connection Error' }
    };
    
    const state = states[status] || states.disconnected;
    dot.style.background = state.color;
    text.textContent = state.text;
}

function clearConsole() {
    document.getElementById('telegramConsole').innerHTML = '';
}

function downloadLogs() {
    const console = document.getElementById('telegramConsole');
    const logs = console.innerText;
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bot-${activeBotId}-logs.txt`;
    a.click();
}

// ═══════════════════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function refreshDashboard() {
    await loadBots();
    showToast('Dashboard refreshed', 'success');
}

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        window.location.href = '/login';
    }
}

// PWA Installation
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
});

// Register service worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
}
