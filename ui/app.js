// ============================================================
// Config
// ============================================================
const API = '';  // same origin

// ============================================================
// State
// ============================================================
let currentView = { type: 'inbox', folder: 'INBOX' };
let currentEmailId = null;

// ============================================================
// Utilities
// ============================================================
function showToast(msg, type = 'info') {
  const toast = document.getElementById('toast');
  const inner = document.getElementById('toastInner');
  const colors = { info: 'bg-gray-900', success: 'bg-green-700', error: 'bg-red-600' };
  inner.className = `flex items-center gap-3 text-white text-sm px-5 py-3 rounded-full shadow-lg ${colors[type] || 'bg-gray-900'}`;
  inner.textContent = msg;
  toast.classList.remove('hidden');
  setTimeout(() => toast.classList.add('hidden'), 3500);
}

function setLoading(on) {
  const icon = document.getElementById('refreshIcon');
  if (on) icon.classList.add('spinner'); else icon.classList.remove('spinner');
}

async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function escapeHtml(str) {
  return String(str ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

function avatar(name) {
  const letter = (name || '?')[0].toUpperCase();
  const colors = ['bg-red-400','bg-orange-400','bg-amber-400','bg-green-400','bg-teal-400','bg-blue-400','bg-purple-400','bg-pink-400'];
  const c = colors[letter.charCodeAt(0) % colors.length];
  const div = document.createElement('div');
  div.className = `w-9 h-9 rounded-full ${c} flex items-center justify-center text-white font-semibold text-sm shrink-0`;
  div.textContent = letter;
  return div.outerHTML;
}

function formatDate(dateStr) {
  if (!dateStr || dateStr === 'Unknown') return '';
  try {
    const d = new Date(dateStr);
    const now = new Date();
    if (d.toDateString() === now.toDateString()) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  } catch { return dateStr.slice(0, 16); }
}

function senderName(from) {
  const m = from.match(/^"?([^"<]+)"?\s*</);
  return m ? m[1].trim() : from.split('@')[0];
}

// ============================================================
// Page switching
// ============================================================
function showPage(page) {
  document.getElementById('page-emails').classList.toggle('hidden', page !== 'emails');
  document.getElementById('page-tools').classList.toggle('hidden', page !== 'tools');
  if (page === 'tools') loadToolsPage();
}

// ============================================================
// Sidebar folder list
// ============================================================
async function loadFolders() {
  const el = document.getElementById('folderList');
  try {
    const data = await apiFetch('/api/folders');
    el.innerHTML = '';
    data.folders.slice(0, 20).forEach(f => {
      const btn = document.createElement('button');
      btn.className = 'sidebar-item w-full text-left flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs text-gray-600 truncate';
      btn.addEventListener('click', () => loadEmails(f, false));
      btn.innerHTML = `<svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7a1 1 0 0 1 1-1h6l2 2h8a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7z"/>
        </svg>`;
      const span = document.createElement('span');
      span.className = 'truncate';
      span.textContent = f;
      btn.appendChild(span);
      el.appendChild(btn);
    });
  } catch (e) {
    const p = document.createElement('p');
    p.className = 'px-3 text-xs text-red-400';
    p.textContent = e.message;
    el.innerHTML = '';
    el.appendChild(p);
  }
}

// ============================================================
// Status dot
// ============================================================
async function checkStatus() {
  try {
    const s = await apiFetch('/api/status');
    const dot = document.getElementById('statusDot');
    dot.className = `w-2 h-2 rounded-full ${s.connected ? 'bg-green-400' : 'bg-red-400'} ml-1`;
    dot.title = s.connected ? `Connected: ${s.email}` : 'Disconnected';
  } catch {}
}

// ============================================================
// Email list
// ============================================================
async function loadEmails(folder = 'INBOX', unreadOnly = false) {
  showPage('emails');
  currentView = { type: 'folder', folder, unreadOnly };
  currentEmailId = null;
  document.getElementById('emailDetailPanel').classList.add('hidden');
  document.getElementById('listTitle').textContent = folder;
  document.getElementById('listSubtitle').textContent = unreadOnly ? 'Unread only' : '';
  setLoading(true);
  try {
    const max = document.getElementById('maxResults').value;
    const data = await apiFetch(`/api/emails?folder=${encodeURIComponent(folder)}&max_results=${max}&unread_only=${unreadOnly}`);
    renderEmailList(data.emails, `${data.count} message${data.count !== 1 ? 's' : ''}`);
  } catch (e) {
    showToast(e.message, 'error');
    const errDiv = document.createElement('div');
    errDiv.className = 'p-6 text-sm text-red-500';
    errDiv.textContent = e.message;
    document.getElementById('emailList').replaceChildren(errDiv);
  } finally { setLoading(false); }
}

async function loadUnread() {
  showPage('emails');
  currentView = { type: 'unread' };
  document.getElementById('listTitle').textContent = 'Unread';
  document.getElementById('listSubtitle').textContent = '';
  setLoading(true);
  try {
    const max = document.getElementById('maxResults').value;
    const data = await apiFetch(`/api/emails/unread?max_results=${max}`);
    renderEmailList(data.emails, `${data.count} unread`);
  } catch (e) {
    showToast(e.message, 'error');
  } finally { setLoading(false); }
}

function refreshCurrentView() {
  const v = currentView;
  if (v.type === 'unread') loadUnread();
  else if (v.type === 'search') runSearch();
  else loadEmails(v.folder, v.unreadOnly);
}

function renderEmailList(emails, subtitle = '') {
  document.getElementById('listSubtitle').textContent = subtitle;
  const el = document.getElementById('emailList');
  if (!emails || emails.length === 0) {
    el.innerHTML = `<div class="flex flex-col items-center justify-center h-full text-gray-300 gap-2 py-16">
      <svg class="w-10 h-10" fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
      <p class="text-sm">No emails found</p></div>`;
    return;
  }
  el.innerHTML = emails.map(e => `
    <div class="email-row px-4 py-3 flex items-start gap-3" data-email-id="${escapeHtml(e.id)}">
      ${avatar(senderName(e.from || ''))}
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between">
          <span class="email-subject text-sm text-gray-800 truncate font-medium">${escapeHtml(senderName(e.from || 'Unknown'))}</span>
          <span class="text-xs text-gray-400 shrink-0 ml-2">${escapeHtml(formatDate(e.date))}</span>
        </div>
        <p class="text-sm text-gray-700 truncate">${escapeHtml(e.subject || '(no subject)')}</p>
        <p class="text-xs text-gray-400 truncate mt-0.5">${escapeHtml((e.body || '').slice(0, 80))}</p>
      </div>
    </div>
  `).join('');
  el.querySelectorAll('.email-row[data-email-id]').forEach(row => {
    row.addEventListener('click', () => openEmail(row.dataset.emailId));
  });
}

// ============================================================
// Email detail
// ============================================================
async function openEmail(id) {
  currentEmailId = id;
  const panel = document.getElementById('emailDetailPanel');
  const detail = document.getElementById('emailDetail');
  panel.classList.remove('hidden');
  detail.innerHTML = `<div class="flex items-center justify-center h-full"><div class="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full spinner"></div></div>`;
  try {
    const e = await apiFetch(`/api/emails/${id}`);
    detail.innerHTML = `
      <div class="px-6 py-5 border-b border-gray-100 sticky top-0 bg-white z-10">
        <h2 class="text-lg font-semibold text-gray-800 leading-tight"></h2>
        <div class="flex items-center gap-3 mt-3">
          ${avatar(senderName(e.from || ''))}
          <div>
            <p class="text-sm font-medium text-gray-700 sender-name"></p>
            <p class="text-xs text-gray-400 sender-email"></p>
          </div>
          <span class="ml-auto text-xs text-gray-400 email-date"></span>
        </div>
      </div>
      <div class="flex-1 overflow-auto email-body-container"></div>
      <div class="px-6 py-4 border-t border-gray-100 bg-gray-50">
        <button class="reply-btn text-sm text-blue-600 hover:underline flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 0 1 8 8v2M3 10l6 6m-6-6 6-6"/>
          </svg>
          Reply
        </button>
      </div>
    `;
    detail.querySelector('h2').textContent = e.subject || '(no subject)';
    detail.querySelector('.sender-name').textContent = senderName(e.from || 'Unknown');
    detail.querySelector('.sender-email').textContent = e.from || '';
    detail.querySelector('.email-date').textContent = formatDate(e.date);
    const body = e.body || '';
    const bodyContainer = detail.querySelector('.email-body-container');
    const isHtml = /<\s*(html|body|div|p|table|span|br|img)\b/i.test(body);
    if (isHtml) {
      const iframe = document.createElement('iframe');
      iframe.sandbox = 'allow-same-origin';
      iframe.style.cssText = 'width:100%;height:100%;border:none;min-height:400px;';
      bodyContainer.appendChild(iframe);
      iframe.contentDocument.open();
      iframe.contentDocument.write(body);
      iframe.contentDocument.close();
    } else {
      const pre = document.createElement('pre');
      pre.className = 'text-sm text-gray-700 leading-relaxed font-sans px-6 py-5';
      pre.textContent = body || '(empty)';
      bodyContainer.appendChild(pre);
    }
    detail.querySelector('.reply-btn').addEventListener('click', () => replyTo(e.from || '', e.subject || ''));
  } catch (e) {
    const errDiv = document.createElement('div');
    errDiv.className = 'p-6 text-sm text-red-500';
    errDiv.textContent = e.message;
    detail.replaceChildren(errDiv);
  }
}

function replyTo(from, subject) {
  document.getElementById('composeTo').value = from.match(/<(.+)>/) ? from.match(/<(.+)>/)[1] : from;
  document.getElementById('composeSubject').value = subject.startsWith('Re:') ? subject : `Re: ${subject}`;
  openCompose();
}

// ============================================================
// Search
// ============================================================
async function runSearch() {
  const q = document.getElementById('searchInput').value.trim();
  if (!q) return;
  const type = document.getElementById('searchType').value;
  showPage('emails');
  document.getElementById('listTitle').textContent = 'Search Results';
  document.getElementById('listSubtitle').textContent = `"${q}"`;
  currentView = { type: 'search', q, searchType: type };
  setLoading(true);
  try {
    const max = document.getElementById('maxResults').value;
    let url;
    if (type === 'sender') url = `/api/emails/from?sender=${encodeURIComponent(q)}&max_results=${max}`;
    else if (type === 'subject') url = `/api/emails/by-subject?subject=${encodeURIComponent(q)}&max_results=${max}`;
    else url = `/api/emails/search?query=${encodeURIComponent(q)}&max_results=${max}`;
    const data = await apiFetch(url);
    renderEmailList(data.emails, `${data.count} result${data.count !== 1 ? 's' : ''}`);
  } catch (e) {
    showToast(e.message, 'error');
  } finally { setLoading(false); }
}

document.getElementById('searchInput').addEventListener('keydown', e => { if (e.key === 'Enter') runSearch(); });

// ============================================================
// Compose
// ============================================================
function openCompose() {
  document.getElementById('composeModal').classList.remove('hidden');
  document.getElementById('composeTo').focus();
}
function closeCompose() {
  document.getElementById('composeModal').classList.add('hidden');
  document.getElementById('composeTo').value = '';
  document.getElementById('composeSubject').value = '';
  document.getElementById('composeBody').value = '';
  document.getElementById('composeHtml').checked = false;
}

async function sendEmail() {
  const to = document.getElementById('composeTo').value.trim();
  const subject = document.getElementById('composeSubject').value.trim();
  const body = document.getElementById('composeBody').value.trim();
  const html = document.getElementById('composeHtml').checked;
  if (!to || !subject || !body) { showToast('Fill in all fields', 'error'); return; }
  try {
    await apiFetch('/api/emails/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient: to, subject, body, html }),
    });
    showToast('Email sent!', 'success');
    closeCompose();
    document.getElementById('composeTo').value = '';
    document.getElementById('composeSubject').value = '';
    document.getElementById('composeBody').value = '';
  } catch (e) {
    showToast(e.message, 'error');
  }
}

// ============================================================
// MCP Tools page
// ============================================================
const TOOL_CONFIGS = [
  {
    name: 'list_emails',
    icon: '📋',
    color: 'blue',
    description: 'List emails from any mailbox folder',
    fields: [
      { id: 'folder', label: 'Folder', type: 'text', default: 'INBOX' },
      { id: 'max_results', label: 'Max Results', type: 'number', default: '10' },
      { id: 'unread_only', label: 'Unread Only', type: 'checkbox', default: false },
    ],
    run: async (vals) => apiFetch(`/api/emails?folder=${encodeURIComponent(vals.folder||'INBOX')}&max_results=${vals.max_results||10}&unread_only=${vals.unread_only||false}`),
  },
  {
    name: 'get_unread_emails',
    icon: '📬',
    color: 'yellow',
    description: 'Fetch only unread emails from a folder',
    fields: [
      { id: 'folder', label: 'Folder', type: 'text', default: 'INBOX' },
      { id: 'max_results', label: 'Max Results', type: 'number', default: '10' },
    ],
    run: async (vals) => apiFetch(`/api/emails/unread?folder=${encodeURIComponent(vals.folder||'INBOX')}&max_results=${vals.max_results||10}`),
  },
  {
    name: 'get_emails_from_sender',
    icon: '👤',
    color: 'green',
    description: 'Retrieve all emails from a specific sender',
    fields: [
      { id: 'sender', label: 'Sender Email', type: 'email', placeholder: 'user@example.com' },
      { id: 'folder', label: 'Folder', type: 'text', default: 'INBOX' },
      { id: 'max_results', label: 'Max Results', type: 'number', default: '10' },
    ],
    run: async (vals) => apiFetch(`/api/emails/from?sender=${encodeURIComponent(vals.sender)}&folder=${encodeURIComponent(vals.folder||'INBOX')}&max_results=${vals.max_results||10}`),
  },
  {
    name: 'get_emails_by_subject',
    icon: '🔤',
    color: 'orange',
    description: 'Find emails matching a subject keyword',
    fields: [
      { id: 'subject', label: 'Subject Keyword', type: 'text', placeholder: 'e.g. invoice' },
      { id: 'folder', label: 'Folder', type: 'text', default: 'INBOX' },
      { id: 'max_results', label: 'Max Results', type: 'number', default: '10' },
    ],
    run: async (vals) => apiFetch(`/api/emails/by-subject?subject=${encodeURIComponent(vals.subject)}&folder=${encodeURIComponent(vals.folder||'INBOX')}&max_results=${vals.max_results||10}`),
  },
  {
    name: 'search_emails',
    icon: '🔍',
    color: 'purple',
    description: 'Search with raw IMAP criteria (UNSEEN, FROM "x@y", SUBJECT "z")',
    fields: [
      { id: 'query', label: 'IMAP Query', type: 'text', placeholder: 'e.g. UNSEEN or SUBJECT "invoice"' },
      { id: 'folder', label: 'Folder', type: 'text', default: 'INBOX' },
      { id: 'max_results', label: 'Max Results', type: 'number', default: '10' },
    ],
    run: async (vals) => apiFetch(`/api/emails/search?query=${encodeURIComponent(vals.query)}&folder=${encodeURIComponent(vals.folder||'INBOX')}&max_results=${vals.max_results||10}`),
  },
  {
    name: 'get_email_details',
    icon: '📄',
    color: 'teal',
    description: 'Get the full content of a single email by its IMAP ID',
    fields: [
      { id: 'message_id', label: 'Message ID', type: 'text', placeholder: 'e.g. 42' },
    ],
    run: async (vals) => apiFetch(`/api/emails/${encodeURIComponent(vals.message_id)}`),
  },
  {
    name: 'list_folders',
    icon: '📁',
    color: 'gray',
    description: 'List all available mailbox folders',
    fields: [],
    run: async () => apiFetch('/api/folders'),
  },
  {
    name: 'send_email',
    icon: '📤',
    color: 'red',
    description: 'Compose and send an email (plain-text or HTML)',
    fields: [
      { id: 'recipient', label: 'To', type: 'email', placeholder: 'recipient@example.com' },
      { id: 'subject', label: 'Subject', type: 'text' },
      { id: 'body', label: 'Body', type: 'textarea' },
      { id: 'html', label: 'HTML body', type: 'checkbox', default: false },
    ],
    run: async (vals) => apiFetch('/api/emails/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipient: vals.recipient, subject: vals.subject, body: vals.body, html: vals.html || false }),
    }),
  },
];

const COLOR_MAP = {
  blue: 'bg-blue-50 border-blue-200 text-blue-700',
  yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
  green: 'bg-green-50 border-green-200 text-green-700',
  orange: 'bg-orange-50 border-orange-200 text-orange-700',
  purple: 'bg-purple-50 border-purple-200 text-purple-700',
  teal: 'bg-teal-50 border-teal-200 text-teal-700',
  gray: 'bg-gray-50 border-gray-200 text-gray-700',
  red: 'bg-red-50 border-red-200 text-red-700',
};

function loadToolsPage() {
  const grid = document.getElementById('toolsGrid');
  grid.innerHTML = TOOL_CONFIGS.map((t, i) => `
    <div class="tool-card bg-white rounded-2xl border ${COLOR_MAP[t.color].split(' ').slice(1).join(' ')} p-5 cursor-pointer" onclick="openTool(${i})">
      <div class="flex items-start gap-3">
        <span class="text-2xl">${t.icon}</span>
        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-gray-800 text-sm">${t.name}</h3>
          <p class="text-xs text-gray-500 mt-0.5 leading-relaxed">${t.description}</p>
        </div>
        <svg class="w-4 h-4 text-gray-300 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </div>
      ${t.fields.length > 0 ? `<div class="mt-3 flex flex-wrap gap-1">${t.fields.map(f => `<span class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">${f.id}</span>`).join('')}</div>` : '<div class="mt-3 text-xs text-gray-400">No parameters</div>'}
    </div>
  `).join('');

  // Load status
  apiFetch('/api/status').then(s => {
    document.getElementById('statusJson').textContent = JSON.stringify(s, null, 2);
  }).catch(e => {
    document.getElementById('statusJson').textContent = `Error: ${e.message}`;
  });
}

// ============================================================
// Tool Playground Modal
// ============================================================
let activeTool = null;

function openTool(index) {
  activeTool = TOOL_CONFIGS[index];
  document.getElementById('modalTitle').textContent = `${activeTool.icon} ${activeTool.name}`;
  document.getElementById('modalDesc').textContent = activeTool.description;

  const body = document.getElementById('modalBody');
  body.innerHTML = activeTool.fields.map(f => {
    if (f.type === 'checkbox') return `
      <label class="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
        <input type="checkbox" id="mf_${f.id}" ${f.default ? 'checked' : ''} class="rounded" />
        ${f.label}
      </label>`;
    if (f.type === 'textarea') return `
      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">${f.label}</label>
        <textarea id="mf_${f.id}" rows="4" placeholder="${f.placeholder||''}"
          class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-100 resize-none"></textarea>
      </div>`;
    return `
      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">${f.label}</label>
        <input type="${f.type}" id="mf_${f.id}" value="${f.default||''}" placeholder="${f.placeholder||f.default||''}"
          class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-100" />
      </div>`;
  }).join('');

  if (activeTool.fields.length === 0) {
    body.innerHTML = '<p class="text-sm text-gray-500">This tool requires no parameters.</p>';
  }

  // Result area
  body.innerHTML += `
    <div id="toolResult" class="hidden mt-2">
      <div class="flex items-center justify-between mb-1">
        <span class="text-xs font-medium text-gray-500">Result</span>
        <button onclick="document.getElementById('toolResult').classList.add('hidden')" class="text-xs text-gray-400 hover:text-gray-600">clear</button>
      </div>
      <pre id="toolResultPre" class="bg-gray-50 rounded-xl p-3 text-xs text-gray-700 overflow-auto max-h-52"></pre>
    </div>`;

  document.getElementById('modalRunBtn').onclick = runActiveTool;
  document.getElementById('toolModal').classList.remove('hidden');
}

function closeToolModal() {
  document.getElementById('toolModal').classList.add('hidden');
  activeTool = null;
}

async function runActiveTool() {
  if (!activeTool) return;
  const btn = document.getElementById('modalRunBtn');
  btn.textContent = 'Running…';
  btn.disabled = true;

  const vals = {};
  activeTool.fields.forEach(f => {
    const el = document.getElementById(`mf_${f.id}`);
    if (!el) return;
    if (f.type === 'checkbox') vals[f.id] = el.checked;
    else vals[f.id] = el.value;
  });

  try {
    const result = await activeTool.run(vals);
    const resultEl = document.getElementById('toolResult');
    const pre = document.getElementById('toolResultPre');
    pre.textContent = JSON.stringify(result, null, 2);
    resultEl.classList.remove('hidden');
    showToast('Tool executed successfully', 'success');
  } catch (e) {
    const resultEl = document.getElementById('toolResult');
    const pre = document.getElementById('toolResultPre');
    pre.textContent = `Error: ${e.message}`;
    resultEl.classList.remove('hidden');
    showToast(e.message, 'error');
  } finally {
    btn.textContent = 'Run';
    btn.disabled = false;
  }
}

// ============================================================
// AI Chat
// ============================================================
let chatSessionId = null;
let chatBusy = false;

async function initChatSession() {
  try {
    const res = await apiFetch('/api/chat/session', { method: 'POST' });
    chatSessionId = res.session_id;
  } catch (e) {
    console.warn('Chat session init failed:', e.message);
  }
}

function toggleChat() {
  const panel = document.getElementById('chatPanel');
  panel.classList.toggle('open');
}

const CHAT_DEFAULT = { width: 380, height: 560 };
let chatExpanded = false;

function toggleExpandChat() {
  const panel = document.getElementById('chatPanel');
  const btn = document.getElementById('chatExpandBtn');
  chatExpanded = !chatExpanded;
  if (chatExpanded) {
    panel.style.width  = Math.min(720, window.innerWidth  - 48) + 'px';
    panel.style.height = Math.min(800, window.innerHeight - 100) + 'px';
    // Re-clamp position so panel stays on screen
    const rect = panel.getBoundingClientRect();
    if (rect.right  > window.innerWidth)  panel.style.left = Math.max(0, window.innerWidth  - panel.offsetWidth  - 24) + 'px';
    if (rect.bottom > window.innerHeight) panel.style.top  = Math.max(0, window.innerHeight - panel.offsetHeight - 24) + 'px';
    panel.style.right = 'auto';
    btn.title = 'Restore';
    btn.querySelector('path').setAttribute('d', 'M9 9L15 3M15 3h-4m4 0v4M3 15l6-6M3 15h4m-4 0v-4');
  } else {
    panel.style.width  = CHAT_DEFAULT.width  + 'px';
    panel.style.height = CHAT_DEFAULT.height + 'px';
    btn.title = 'Expand';
    btn.querySelector('path').setAttribute('d', 'M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5');
  }
}

function initDraggable() {
  const panel = document.getElementById('chatPanel');
  const handle = panel.querySelector('.chat-drag-handle');
  const resizeGrip = document.getElementById('chatResizeHandle');

  // ── Drag ──
  let dragging = false, ox = 0, oy = 0;
  handle.addEventListener('mousedown', e => {
    if (e.target.closest('button')) return;
    dragging = true;
    const rect = panel.getBoundingClientRect();
    ox = e.clientX - rect.left;
    oy = e.clientY - rect.top;
    panel.style.transition = 'none';
    e.preventDefault();
  });

  // ── Resize ──
  let resizing = false, startX = 0, startY = 0, startW = 0, startH = 0;
  resizeGrip.addEventListener('mousedown', e => {
    resizing = true;
    startX = e.clientX; startY = e.clientY;
    startW = panel.offsetWidth; startH = panel.offsetHeight;
    panel.style.transition = 'none';
    e.preventDefault();
  });

  document.addEventListener('mousemove', e => {
    if (dragging) {
      let x = e.clientX - ox;
      let y = e.clientY - oy;
      x = Math.max(0, Math.min(window.innerWidth  - panel.offsetWidth,  x));
      y = Math.max(0, Math.min(window.innerHeight - panel.offsetHeight, y));
      panel.style.left  = x + 'px';
      panel.style.top   = y + 'px';
      panel.style.right = 'auto';
    }
    if (resizing) {
      const w = Math.max(320, Math.min(window.innerWidth  - panel.offsetLeft - 8, startW + e.clientX - startX));
      const h = Math.max(300, Math.min(window.innerHeight - panel.offsetTop  - 8, startH + e.clientY - startY));
      panel.style.width  = w + 'px';
      panel.style.height = h + 'px';
    }
  });

  document.addEventListener('mouseup', () => {
    if (dragging || resizing) {
      dragging = resizing = false;
      panel.style.transition = '';
    }
  });
}

function clearChat() {
  document.getElementById('chatMessages').innerHTML = '';
  rebuildWelcome();
  initChatSession();
}

function rebuildWelcome() {
  const msgs = document.getElementById('chatMessages');
  msgs.innerHTML = `
    <div id="chatWelcome" class="chat-welcome flex flex-col">
      <div class="w-14 h-14 rounded-full bg-purple-100 flex items-center justify-center mx-auto">
        <svg class="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 0 1-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
      </div>
      <p class="text-sm font-semibold text-gray-700 mt-3">Ask me anything about your emails</p>
      <p class="text-xs text-gray-400 mt-1">I can read, search, and send emails for you.</p>
      <div class="mt-4 flex flex-col gap-2 w-full">
        <button onclick="quickPrompt('Show my unread emails')" class="text-left text-xs bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl px-3 py-2 text-gray-600 transition">📬 Show my unread emails</button>
        <button onclick="quickPrompt('List emails from the last week')" class="text-left text-xs bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl px-3 py-2 text-gray-600 transition">📅 List emails from the last week</button>
        <button onclick="quickPrompt('What folders do I have?')" class="text-left text-xs bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl px-3 py-2 text-gray-600 transition">📁 What folders do I have?</button>
        <button onclick="quickPrompt('Search for emails about invoice')" class="text-left text-xs bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl px-3 py-2 text-gray-600 transition">🔍 Search for emails about invoice</button>
      </div>
    </div>`;
}

function autoResizeChatInput(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

function quickPrompt(text) {
  document.getElementById('chatInput').value = text;
  sendChatMessage();
}

function appendUserBubble(text) {
  const welcome = document.getElementById('chatWelcome');
  if (welcome) welcome.remove();
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'chat-bubble-user';
  div.textContent = text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

function createAiBubble() {
  const msgs = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'chat-bubble-ai streaming';
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

// Minimal safe markdown renderer — escapes HTML first, then applies transforms
function renderMarkdown(raw) {
  const e = raw
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

  return e
    // Code blocks (``` ... ```)
    .replace(/```[\w]*\n?([\s\S]*?)```/g, (_, c) =>
      `<pre style="background:#f1f3f4;border-radius:6px;padding:8px 10px;font-size:12px;overflow-x:auto;margin:4px 0"><code>${c.trimEnd()}</code></pre>`)
    // Inline code
    .replace(/`([^`\n]+)`/g, '<code style="background:#f1f3f4;padding:1px 5px;border-radius:3px;font-size:0.88em;font-family:monospace">$1</code>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*([^*\n]+)\*/g, '<em>$1</em>')
    // Headings (## / ###)
    .replace(/^#{1,3} (.+)$/gm, '<p style="font-weight:600;margin:6px 0 2px">$1</p>')
    // Bullet list items
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    // Numbered list items
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> blocks in <ul>
    .replace(/(<li>[\s\S]*?<\/li>)(\n<li>[\s\S]*?<\/li>)*/g, m =>
      `<ul style="margin:4px 0;padding-left:18px;list-style:disc">${m}</ul>`)
    // Paragraph breaks
    .replace(/\n{2,}/g, '<br><br>')
    // Single line breaks
    .replace(/\n/g, '<br>');
}

function appendToolChip(name, done = false) {
  const msgs = document.getElementById('chatMessages');
  const chip = document.createElement('div');
  chip.className = `tool-chip ${done ? 'done' : ''}`;
  chip.id = `chip-${name}-${Date.now()}`;
  chip.innerHTML = done
    ? `<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> ${name}`
    : `<svg class="w-3 h-3 spinner" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 0 0 4.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 0 1-15.357-2m15.357 2H15"/></svg> Calling ${name}…`;
  msgs.appendChild(chip);
  msgs.scrollTop = msgs.scrollHeight;
  return chip;
}

async function sendChatMessage() {
  if (chatBusy) return;
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  if (!chatSessionId) {
    showToast('Chat session not ready. Retrying…', 'error');
    await initChatSession();
    if (!chatSessionId) return;
  }

  input.value = '';
  input.style.height = 'auto';
  chatBusy = true;
  document.getElementById('chatSendBtn').disabled = true;

  appendUserBubble(text);
  const aiBubble = createAiBubble();

  // Open panel if closed
  document.getElementById('chatPanel').classList.add('open');

  let activeToolChips = {};

  try {
    const res = await fetch(`/api/chat/${chatSessionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    const msgs = document.getElementById('chatMessages');
    let buf = '';
    let rawText = '';  // accumulate full AI text for markdown rendering

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });

      const lines = buf.split('\n');
      buf = lines.pop();   // keep incomplete line

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        let evt;
        try { evt = JSON.parse(line.slice(6)); } catch { continue; }

        if (evt.type === 'text') {
          rawText += evt.text;
          aiBubble.textContent = rawText;  // plain text while streaming
          msgs.scrollTop = msgs.scrollHeight;
        } else if (evt.type === 'tool_call') {
          const chip = appendToolChip(evt.name, false);
          activeToolChips[evt.name] = chip;
        } else if (evt.type === 'tool_result') {
          const chip = activeToolChips[evt.name];
          if (chip) {
            chip.className = 'tool-chip done';
            chip.innerHTML = `<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg> ${escapeHtml(evt.name)}`;
          }
        } else if (evt.type === 'error') {
          aiBubble.textContent = `Error: ${evt.text}`;
          aiBubble.style.background = '#fce8e6';
          aiBubble.style.color = '#c5221f';
        } else if (evt.type === 'done') {
          // Render markdown now that the full response is received
          aiBubble.innerHTML = renderMarkdown(rawText);
          aiBubble.classList.remove('streaming');
          msgs.scrollTop = msgs.scrollHeight;
        }
      }
    }
  } catch (e) {
    aiBubble.textContent = `Error: ${e.message}`;
    aiBubble.classList.remove('streaming');
    aiBubble.style.background = '#fce8e6';
    aiBubble.style.color = '#c5221f';
    showToast(e.message, 'error');
  } finally {
    aiBubble.classList.remove('streaming');
    chatBusy = false;
    document.getElementById('chatSendBtn').disabled = false;
    document.getElementById('chatInput').focus();
  }
}

// ============================================================
// Init
// ============================================================
async function init() {
  await checkStatus();
  // loadFolders removed — only Inbox shown in sidebar
  loadEmails('INBOX', false);
  initChatSession();
  initDraggable();
}

init();
