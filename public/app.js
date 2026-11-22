let currentSecurityMode = 'vulnerable';
let currentLogsPage = 1;
let logsPerPage = 15;
let totalLogsPages = 1;

document.addEventListener('DOMContentLoaded', () => {
  updateCookieDisplay();
  loadComments();
  loadSecurityLogs();
});

function setSecurityMode(mode) {
  currentSecurityMode = mode;
  const vulnBtn = document.getElementById('modeVulnerableBtn');
  const secBtn = document.getElementById('modeSecureBtn');

  if (mode === 'vulnerable') {
    vulnBtn.classList.add('active');
    secBtn.classList.remove('active');
  } else {
    vulnBtn.classList.remove('active');
    secBtn.classList.add('active');
  }

  loadComments();
  updateCookieDisplay();
}

function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

  const targetPane = document.getElementById(`tab-${tabId}`);
  if (targetPane) targetPane.classList.add('active');

  const btns = document.querySelectorAll('.tab-btn');
  if (tabId === 'sqli' && btns[0]) btns[0].classList.add('active');
  if (tabId === 'xss' && btns[1]) btns[1].classList.add('active');
  if (tabId === 'logs' && btns[2]) {
    btns[2].classList.add('active');
    loadSecurityLogs();
  }
  if (tabId === 'docs' && btns[3]) btns[3].classList.add('active');
}

function updateCookieDisplay() {
  const display = document.getElementById('cookieDisplay');
  if (display) {
    display.textContent = document.cookie || '(Empty - No cookies accessible via JavaScript)';
  }
}

function fillLoginPayload(username, password) {
  document.getElementById('loginUsername').value = username;
  document.getElementById('loginPassword').value = password;
}

async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById('loginUsername').value;
  const password = document.getElementById('loginPassword').value;
  const resultBox = document.getElementById('loginResult');

  resultBox.className = 'result-box';
  resultBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting authentication request...';

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, securityMode: currentSecurityMode })
    });
    const data = await res.json();

    if (res.ok && data.success) {
      resultBox.classList.add('success');
      resultBox.innerHTML = `
        <strong><i class="fa-solid fa-circle-check"></i> ${data.message}</strong>
        ${data.user ? `<div>Authenticated User: <code>${data.user.username}</code> | Assigned Role: <code>${data.user.role}</code></div>` : ''}
        ${data.executedQuery ? `<div class="code-display"><strong>Executed Backend Query:</strong><br>${escapeHtml(data.executedQuery)}</div>` : ''}
        ${data.vulnerabilityTriggered ? '<div style="color:#ef4444; margin-top:6px;"><strong>SQL INJECTION EXPLOITED:</strong> Authentication bypassed via malicious payload.</div>' : ''}
      `;
    } else {
      resultBox.classList.add('danger');
      resultBox.innerHTML = `
        <strong><i class="fa-solid fa-triangle-exclamation"></i> ${data.message || 'Authentication failed.'}</strong>
        ${data.executedQuery ? `<div class="code-display"><strong>Executed Query:</strong><br>${escapeHtml(data.executedQuery)}</div>` : ''}
      `;
    }
  } catch (err) {
    resultBox.classList.add('danger');
    resultBox.innerHTML = `<strong>Network Error:</strong> ${err.message}`;
  }

  updateCookieDisplay();
  refreshLogCount();
}

function fillSearchPayload(keyword) {
  document.getElementById('searchKeyword').value = keyword;
}

async function handleProductSearch(e) {
  e.preventDefault();
  const q = document.getElementById('searchKeyword').value;
  const resultBox = document.getElementById('searchResult');

  resultBox.className = 'result-box';
  resultBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Querying products...';

  try {
    const res = await fetch(`/api/products/search?q=${encodeURIComponent(q)}&securityMode=${currentSecurityMode}`);
    const data = await res.json();

    if (res.ok && data.success) {
      resultBox.classList.add(data.vulnerabilityTriggered ? 'danger' : 'success');

      let html = `<strong>Returned ${data.count} records:</strong>`;
      if (data.executedQuery) {
        html += `<div class="code-display"><strong>SQL Query:</strong><br>${escapeHtml(data.executedQuery)}</div>`;
      }

      if (data.data && data.data.length > 0) {
        html += '<ul style="margin-top:10px; padding-left:18px;">';
        data.data.forEach(item => {
          html += `<li><strong>${escapeHtml(item.name || item.username || '')}</strong> - ${escapeHtml(item.category || item.password || '')} (${item.price || item.role || ''})</li>`;
        });
        html += '</ul>';
      }

      if (data.vulnerabilityTriggered) {
        html += '<div style="color:#ef4444; margin-top:8px;"><strong>UNION SQL INJECTION SUCCESSFUL:</strong> Database user records and credentials exfiltrated.</div>';
      }

      resultBox.innerHTML = html;
    } else {
      resultBox.classList.add('danger');
      resultBox.innerHTML = `<strong>${data.message || 'Search failed.'}</strong>`;
    }
  } catch (err) {
    resultBox.classList.add('danger');
    resultBox.innerHTML = `<strong>Network Error:</strong> ${err.message}`;
  }

  refreshLogCount();
}

function fillCommentPayload(author, content) {
  document.getElementById('commentAuthor').value = author;
  document.getElementById('commentContent').value = content;
}

async function handlePostComment(e) {
  e.preventDefault();
  const author = document.getElementById('commentAuthor').value;
  const content = document.getElementById('commentContent').value;

  try {
    const res = await fetch('/api/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ author, content, securityMode: currentSecurityMode })
    });
    const data = await res.json();
    alert(data.message);
    document.getElementById('commentContent').value = '';
    loadComments();
    refreshLogCount();
  } catch (err) {
    alert('Error: ' + err.message);
  }
}

async function loadComments() {
  const container = document.getElementById('commentsList');
  if (!container) return;

  try {
    const res = await fetch(`/api/comments?securityMode=${currentSecurityMode}`);
    const data = await res.json();

    if (data.success && data.data) {
      if (data.data.length === 0) {
        container.innerHTML = '<em>No comments available.</em>';
        return;
      }

      container.innerHTML = '';
      data.data.forEach(item => {
        const div = document.createElement('div');
        div.className = 'comment-item';

        if (currentSecurityMode === 'vulnerable') {
          div.innerHTML = `
            <div class="comment-author">
              <span>${item.author}</span>
              <span class="comment-time">${item.created_at || ''}</span>
            </div>
            <div class="comment-content">${item.content}</div>
          `;
        } else {
          const authorSpan = document.createElement('span');
          authorSpan.textContent = item.author;

          const timeSpan = document.createElement('span');
          timeSpan.className = 'comment-time';
          timeSpan.textContent = item.created_at || '';

          const authorDiv = document.createElement('div');
          authorDiv.className = 'comment-author';
          authorDiv.appendChild(authorSpan);
          authorDiv.appendChild(timeSpan);

          const contentDiv = document.createElement('div');
          contentDiv.className = 'comment-content';
          contentDiv.textContent = item.content;

          div.appendChild(authorDiv);
          div.appendChild(contentDiv);
        }

        container.appendChild(div);
      });
    }
  } catch (err) {
    container.innerHTML = `<span style="color:red">Failed to load comments: ${err.message}</span>`;
  }
}

async function resetComments() {
  if (confirm('Reset sample comments to initial state?')) {
    await fetch('/api/comments/reset', { method: 'POST' });
    loadComments();
  }
}

function fillReflectedPayload(payload) {
  document.getElementById('reflectedQuery').value = payload;
}

async function handleReflectedSearch(e) {
  e.preventDefault();
  const q = document.getElementById('reflectedQuery').value;
  const resultBox = document.getElementById('reflectedResult');

  resultBox.className = 'result-box';
  resultBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Loading reflected response...';

  try {
    const res = await fetch(`/api/search/reflected?q=${encodeURIComponent(q)}&securityMode=${currentSecurityMode}`);
    const data = await res.json();

    if (currentSecurityMode === 'vulnerable') {
      resultBox.classList.add('danger');
      resultBox.innerHTML = data.htmlSnippet;
      executeInjectedScripts(resultBox);
    } else {
      resultBox.classList.add('success');
      resultBox.innerHTML = data.htmlSnippet;
    }
  } catch (err) {
    resultBox.classList.add('danger');
    resultBox.innerHTML = 'Error: ' + err.message;
  }

  updateCookieDisplay();
  refreshLogCount();
}

function executeInjectedScripts(container) {
  const scripts = container.querySelectorAll('script');
  scripts.forEach(s => {
    const newScript = document.createElement('script');
    newScript.text = s.innerText;
    document.body.appendChild(newScript);
  });
}

function changeLogsPage(delta) {
  const targetPage = currentLogsPage + delta;
  if (targetPage >= 1 && targetPage <= totalLogsPages) {
    currentLogsPage = targetPage;
    loadSecurityLogs();
  }
}

function changeLogsLimit(newLimit) {
  logsPerPage = parseInt(newLimit, 10) || 15;
  currentLogsPage = 1;
  loadSecurityLogs();
}

async function loadSecurityLogs() {
  const tableBody = document.getElementById('logsTableBody');
  if (!tableBody) return;

  try {
    const statsRes = await fetch('/api/logs/stats');
    const statsData = await statsRes.json();
    if (statsData.success) {
      document.getElementById('metricTotal').textContent = statsData.data.total;
      document.getElementById('metricSQLi').textContent = statsData.data.sqliCount;
      document.getElementById('metricXSS').textContent = statsData.data.xssCount;
      document.getElementById('metricCritical').textContent = statsData.data.criticalCount;
      document.getElementById('badgeLogCount').textContent = statsData.data.total;
    }

    const logsRes = await fetch(`/api/logs?page=${currentLogsPage}&limit=${logsPerPage}`);
    const logsData = await logsRes.json();

    if (logsData.success) {
      const logs = logsData.data || [];
      const pagination = logsData.pagination || { total: 0, page: 1, limit: logsPerPage, totalPages: 1 };
      
      totalLogsPages = pagination.totalPages;
      currentLogsPage = pagination.page;

      const pageIndicator = document.getElementById('pageIndicator');
      const paginationInfo = document.getElementById('paginationInfo');
      const prevBtn = document.getElementById('prevPageBtn');
      const nextBtn = document.getElementById('nextPageBtn');

      if (pageIndicator) pageIndicator.textContent = `Page ${pagination.page} of ${pagination.totalPages}`;
      
      const startEntry = pagination.total === 0 ? 0 : (pagination.page - 1) * pagination.limit + 1;
      const endEntry = Math.min(pagination.page * pagination.limit, pagination.total);
      if (paginationInfo) paginationInfo.textContent = `Showing ${startEntry} to ${endEntry} of ${pagination.total} logs`;

      if (prevBtn) prevBtn.disabled = pagination.page <= 1;
      if (nextBtn) nextBtn.disabled = pagination.page >= pagination.totalPages;

      if (logs.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No security incidents recorded.</td></tr>';
        return;
      }

      tableBody.innerHTML = '';
      logs.forEach(log => {
        const tr = document.createElement('tr');
        const badgeClass = log.severity === 'CRITICAL' ? 'badge-critical' : 
                           log.severity === 'HIGH' ? 'badge-high' : 
                           log.severity === 'MEDIUM' ? 'badge-medium' : 'badge-low';

        tr.innerHTML = `
          <td><code>${log.timestamp}</code></td>
          <td><code>${escapeHtml(log.ip)}</code></td>
          <td><span class="badge ${badgeClass}">${log.severity}</span></td>
          <td><strong>${escapeHtml(log.event_type)}</strong></td>
          <td><code>${escapeHtml(log.endpoint)}</code></td>
          <td>${escapeHtml(log.action_taken)}</td>
          <td><code style="word-break:break-all;">${escapeHtml(log.payload)}</code></td>
        `;
        tableBody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error('Failed to load logs:', err);
  }
}

async function refreshLogCount() {
  try {
    const statsRes = await fetch('/api/logs/stats');
    const statsData = await statsRes.json();
    if (statsData.success) {
      document.getElementById('badgeLogCount').textContent = statsData.data.total;
    }
  } catch (err) {}
}

async function clearSecurityLogs() {
  if (confirm('Are you sure you want to clear all security incident logs?')) {
    await fetch('/api/logs', { method: 'DELETE' });
    loadSecurityLogs();
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
