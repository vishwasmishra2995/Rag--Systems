/* ─────────────────────────────────────────────
   Multilingual RAG — app.js
   API base: https://razashaikh9921-main-dev.hf.space
───────────────────────────────────────────── */

const API = 'https://razashaikh9921-main-dev.hf.space';

let authToken = null;
let currentUsername = '';
let selectedFile = null;

/* ══════════════════════════════════════════
   INIT
══════════════════════════════════════════ */
window.addEventListener('DOMContentLoaded', () => {
  // Restore session
  const saved = localStorage.getItem('rag_token');
  const savedUser = localStorage.getItem('rag_user');
  if (saved && savedUser) {
    authToken = saved;
    currentUsername = savedUser;
    enterApp();
  }
});

/* ══════════════════════════════════════════
   AUTH
══════════════════════════════════════════ */
async function handleLogin() {
  const input = document.getElementById('username-input');
  const btn = document.getElementById('login-btn');
  const errEl = document.getElementById('auth-error');
  const username = input.value.trim();

  if (!username) {
    showAuthError('Please enter a username.');
    return;
  }

  btn.disabled = true;
  btn.querySelector('.btn-text').textContent = 'Signing in…';
  errEl.classList.add('hidden');

  try {
    const res = await fetch(`${API}/login?username=${encodeURIComponent(username)}`, {
      method: 'POST'
    });
    const data = await res.json();

    if (!res.ok || !data.token) throw new Error(data.detail || 'Login failed');

    authToken = data.token;
    currentUsername = username;
    localStorage.setItem('rag_token', authToken);
    localStorage.setItem('rag_user', username);
    enterApp();

  } catch (err) {
    showAuthError(err.message || 'Could not connect to server.');
    btn.disabled = false;
    btn.querySelector('.btn-text').textContent = 'Continue';
  }
}

function showAuthError(msg) {
  const el = document.getElementById('auth-error');
  el.textContent = msg;
  el.classList.remove('hidden');
}

function enterApp() {
  document.getElementById('auth-screen').classList.remove('active');
  document.getElementById('app-screen').classList.add('active');

  const initials = currentUsername.charAt(0).toUpperCase();
  document.getElementById('user-avatar').textContent = initials;
  document.getElementById('user-name-display').textContent = currentUsername;
}

function handleLogout() {
  authToken = null;
  currentUsername = '';
  localStorage.removeItem('rag_token');
  localStorage.removeItem('rag_user');
  document.getElementById('app-screen').classList.remove('active');
  document.getElementById('auth-screen').classList.add('active');
  document.getElementById('username-input').value = '';
  document.getElementById('chat-messages').innerHTML = `
    <div class="chat-welcome">
      <div class="welcome-icon">✦</div>
      <p>Upload a document first, then ask questions about it.</p>
    </div>`;
  switchTab('chat');
}

/* ══════════════════════════════════════════
   TAB NAVIGATION
══════════════════════════════════════════ */
function switchTab(name) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(`tab-${name}`).classList.add('active');
  document.getElementById(`nav-${name}`).classList.add('active');
  if (name === 'eval') renderEvalHistory();
}

/* ══════════════════════════════════════════
   CHAT — ASK
══════════════════════════════════════════ */
async function sendQuestion() {
  const input = document.getElementById('question-input');
  const btn = document.getElementById('send-btn');
  const question = input.value.trim();
  if (!question || btn.disabled) return;

  input.value = '';
  btn.disabled = true;

  appendMessage('user', question);
  const typingId = appendTyping();

  try {
    const res = await fetch(`${API}/ask?question=${encodeURIComponent(question)}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${authToken}` }
    });

    if (!res.ok) {
      // Try to parse error detail from JSON
      let errMsg = 'Request failed';
      try {
        const errData = await res.json();
        errMsg = errData.detail || errMsg;
      } catch {}
      throw new Error(errMsg);
    }

    removeTyping(typingId);

    // Create an empty assistant message bubble for streaming
    const { bubble } = appendMessageStreaming();

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value, { stream: true });
      bubble.textContent += text;
      // Auto-scroll as tokens arrive
      const container = document.getElementById('chat-messages');
      container.scrollTop = container.scrollHeight;
    }

  } catch (err) {
    removeTyping(typingId);
    appendMessage('assistant', `⚠ ${err.message}`);
  } finally {
    btn.disabled = false;
    input.focus();
  }
}

function appendMessage(role, text) {
  const container = document.getElementById('chat-messages');

  const welcome = container.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  const div = document.createElement('div');
  div.className = `chat-message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = role === 'user'
    ? currentUsername.charAt(0).toUpperCase()
    : '✦';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.textContent = text;

  div.appendChild(avatar);
  div.appendChild(bubble);
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function appendMessageStreaming() {
  const container = document.getElementById('chat-messages');

  const welcome = container.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  const div = document.createElement('div');
  div.className = 'chat-message assistant';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = '✦';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.textContent = '';

  div.appendChild(avatar);
  div.appendChild(bubble);
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return { bubble };
}

function appendTyping() {
  const container = document.getElementById('chat-messages');
  const id = 'typing-' + Date.now();

  const div = document.createElement('div');
  div.className = 'chat-message assistant';
  div.id = id;

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = '✦';

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  bubble.innerHTML = `<div class="typing-indicator">
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  </div>`;

  div.appendChild(avatar);
  div.appendChild(bubble);
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

/* ══════════════════════════════════════════
   INLINE UPLOAD (chat bar paperclip)
══════════════════════════════════════════ */
async function handleInlineUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const allowed = ['pdf', 'csv', 'docx', 'txt'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showChatToast(`Unsupported file type: .${ext}. Use PDF, CSV, DOCX or TXT.`, 'error-status');
    return;
  }

  const attachBtn = document.getElementById('attach-btn');
  attachBtn.classList.add('uploading');
  attachBtn.disabled = true;
  showChatToast(`⏳ Uploading "${file.name}"…`, 'loading');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API}/inject/file`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${authToken}` },
      body: formData
    });
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || data.detail || 'Upload failed');
    showChatToast(`✓ "${file.name}" uploaded — you can now ask questions about it!`, 'success');
    setTimeout(() => hideChatToast(), 4000);
  } catch (err) {
    showChatToast(`✗ ${err.message}`, 'error-status');
    setTimeout(() => hideChatToast(), 5000);
  } finally {
    attachBtn.classList.remove('uploading');
    attachBtn.disabled = false;
    e.target.value = '';
  }
}

function showChatToast(msg, cls) {
  const el = document.getElementById('chat-upload-toast');
  el.textContent = msg;
  el.className = `chat-upload-toast ${cls}`;
  el.classList.remove('hidden');
}
function hideChatToast() {
  document.getElementById('chat-upload-toast').classList.add('hidden');
}

/* ══════════════════════════════════════════
   EVALUATION — with localStorage history
══════════════════════════════════════════ */
const EVAL_HISTORY_KEY = 'rag_eval_history';

function loadEvalHistory() {
  try {
    return JSON.parse(localStorage.getItem(EVAL_HISTORY_KEY) || '[]');
  } catch { return []; }
}

function saveEvalRun(data) {
  const history = loadEvalHistory();
  history.unshift({ // newest first
    timestamp: new Date().toISOString(),
    data
  });
  // Keep last 20 runs max
  localStorage.setItem(EVAL_HISTORY_KEY, JSON.stringify(history.slice(0, 20)));
}

function clearEvalHistory() {
  if (!confirm('Clear all saved evaluation history?')) return;
  localStorage.removeItem(EVAL_HISTORY_KEY);
  document.getElementById('eval-history').innerHTML = '';
}

async function runEvaluation() {
  const btn = document.getElementById('eval-btn');
  const loadingEl = document.getElementById('eval-loading');

  btn.disabled = true;
  loadingEl.classList.remove('hidden');

  try {
    const res = await fetch(`${API}/evaluation/run`, {
      headers: { Authorization: `Bearer ${authToken}` }
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Evaluation failed');

    saveEvalRun(data);
    await renderEvalHistory();
  } catch (err) {
    // 404 = no new interactions — not a real error
    const msg = err.message || '';
    if (msg.toLowerCase().includes('no new') || msg.includes('404')) {
      const historyEl = document.getElementById('eval-history');
      const note = document.createElement('div');
      note.style.cssText = 'padding:12px 16px;border-radius:10px;font-size:13px;background:rgba(129,140,248,0.08);border:1px solid rgba(129,140,248,0.2);color:var(--primary);margin-top:12px';
      note.textContent = 'ℹ No new interactions since last evaluation. Ask more questions first.';
      historyEl.prepend(note);
      setTimeout(() => note.remove(), 5000);
    } else {
      const historyEl = document.getElementById('eval-history');
      const errDiv = document.createElement('div');
      errDiv.className = 'error-msg';
      errDiv.style.marginTop = '16px';
      errDiv.textContent = `⚠ ${err.message}`;
      historyEl.prepend(errDiv);
      setTimeout(() => errDiv.remove(), 6000);
    }
  } finally {
    btn.disabled = false;
    loadingEl.classList.add('hidden');
  }
}

async function renderEvalHistory() {
  const container = document.getElementById('eval-history');
  try {
    const res = await fetch(`${API}/evaluation/history`);
    const data = await res.json();
    const history = data.runs || [];
    if (!history.length) {
      container.innerHTML = '<p style="color:var(--text-muted);font-size:14px;padding:20px 0">No evaluation runs yet. Ask some questions then click Run Now.</p>';
      return;
    }
    container.innerHTML = history.map((run, ri) =>
      buildRunHTML(run, run.evaluated_at || run.run_dir || '', ri)
    ).join('');
    setTimeout(() => {
      container.querySelectorAll('.metric-bar-fill').forEach(bar => {
        bar.style.transition = 'width 0.9s cubic-bezier(.4,0,.2,1)';
      });
    }, 50);
  } catch {
    // fallback: show nothing silently
  }
}

function buildRunHTML(data, timestamp, runIndex) {
  const rows = data.metrics || [];
  const ts = new Date(timestamp);
  const label = ts.toLocaleString();

  const metrics = [
    { label: 'Answer Relevancy', key: 'answer_relevancy' },
    { label: 'Faithfulness',     key: 'faithfulness' },
    { label: 'Context Precision',key: 'context_precision' },
  ];

  const avg = (key) => {
    const vals = rows.map(r => r[key]).filter(v => v !== null && v !== undefined && !isNaN(v));
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
  };

  const summaryHTML = metrics.map(m => {
    const val = avg(m.key);
    const pct = val !== null ? Math.round(val * 100) : 0;
    return `
      <div class="metric-card">
        <div class="metric-label">${m.label}</div>
        <div class="metric-value">${val !== null ? val.toFixed(2) : '—'}</div>
        <div class="metric-bar"><div class="metric-bar-fill" style="width:${pct}%"></div></div>
      </div>`;
  }).join('');

  const rowsHTML = rows.map((r, i) => {
    const scores = metrics.map(m => {
      const v = r[m.key];
      if (v === null || v === undefined || isNaN(v))
        return `<span class="score-badge null-score">${m.label}: —</span>`;
      const cls = v >= 0.8 ? 'good' : v >= 0.5 ? 'mid' : 'bad';
      return `<span class="score-badge ${cls}">${m.label}: ${v.toFixed(2)}</span>`;
    }).join('');

    const contexts = r.retrieved_contexts || r.contexts || [];
    const contextHTML = contexts.length
      ? contexts.map((c, ci) => `
          <div class="ctx-chunk">
            <span class="ctx-idx">#${ci + 1}</span>
            <pre class="ctx-text">${escapeHtml(c)}</pre>
          </div>`).join('')
      : '<p class="ctx-empty">No context retrieved (fallback answer)</p>';

    return `
      <div class="eval-row" style="animation-delay:${i * 0.07}s">
        <div class="eval-field">
          <span class="eval-field-label">
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="8" r="6"/><path d="M8 5v3l2 2"/></svg>
            User Input
          </span>
          <p class="eval-field-value">${escapeHtml(r.user_input || r.question || '—')}</p>
        </div>
        <div class="eval-field">
          <span class="eval-field-label">
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H2v12l3-3h9V2z"/></svg>
            Answer
          </span>
          <p class="eval-field-value answer-text">${escapeHtml(r.response || r.answer || '—')}</p>
        </div>
        <div class="eval-field">
          <span class="eval-field-label">
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="12" height="12" rx="1"/><path d="M5 6h6M5 9h4"/></svg>
            Retrieved Context
          </span>
          <div class="ctx-list">${contextHTML}</div>
        </div>
        <div class="eval-row-scores">${scores}</div>
      </div>`;
  }).join('');

  return `
    <div class="eval-run ${runIndex === 0 ? 'eval-run-latest' : ''}">
      <div class="eval-run-header" onclick="toggleRun(${runIndex})">
        <div class="eval-run-meta">
          ${runIndex === 0 ? '<span class="run-badge">Latest</span>' : ''}
          <span class="run-time">${label}</span>
          <span class="run-count">${rows.length} interaction${rows.length !== 1 ? 's' : ''}</span>
        </div>
        <svg class="run-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
      </div>
      <div class="eval-run-body" id="eval-run-body-${runIndex}" style="${runIndex === 0 ? '' : 'display:none'}">
        <div class="eval-summary">${summaryHTML}</div>
        <div class="eval-rows">${rowsHTML}</div>
        <p class="eval-meta">Sample count: ${data.sample_count} · Run dir: ${data.run_dir || '—'}</p>
      </div>
    </div>`;
}

function toggleRun(index) {
  const body = document.getElementById(`eval-run-body-${index}`);
  const isOpen = body.style.display !== 'none';
  body.style.display = isOpen ? 'none' : 'block';
}



function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
