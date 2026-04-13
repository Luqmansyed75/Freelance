/* =====================================================
   FreelanceMatch — Main JavaScript
   Skill selector, AJAX job search, nav, utils
   ===================================================== */

// ── Config ──
const API_BASE = '/api/v1';

// ── DOM Ready ──
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  if (document.getElementById('skills-container'))   initSkillSelector();
  if (document.getElementById('jobs-grid'))           initJobSearch();
  if (document.getElementById('apps-table-body'))     initApplicationsCRM();
  initScrollAnimations();
});

/* =====================================================
   NAVBAR
   ===================================================== */
function initNavbar() {
  // Mobile toggle
  const toggle = document.getElementById('nav-toggle');
  const links  = document.getElementById('navbar-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', links.classList.contains('open'));
    });

    // Close on link click
    links.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => links.classList.remove('open'));
    });
  }

  // Active link highlighting
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link[data-path]').forEach(link => {
    if (link.dataset.path === path || (path.startsWith(link.dataset.path) && link.dataset.path !== '/')) {
      link.classList.add('active');
    }
  });
}

/* =====================================================
   SKILL SELECTOR (Dashboard)
   ===================================================== */
let selectedSkills = new Set();

function initSkillSelector() {
  const container    = document.getElementById('skills-container');
  const selectedBox  = document.getElementById('selected-skills');
  const searchInput  = document.getElementById('skill-search');
  const chips        = container ? container.querySelectorAll('.skill-chip') : [];

  // Chip click — toggle selection
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      const skill = chip.dataset.skill;
      if (selectedSkills.has(skill)) {
        selectedSkills.delete(skill);
        chip.classList.remove('selected');
      } else {
        selectedSkills.add(skill);
        chip.classList.add('selected');
      }
      updateSelectedBox(selectedBox);
    });
  });

  // Skill search filter
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase();
      chips.forEach(chip => {
        const visible = chip.dataset.skill.toLowerCase().includes(q);
        chip.style.display = visible ? '' : 'none';
      });
    });
  }

  // Add custom skill on Enter
  if (searchInput) {
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const val = searchInput.value.trim();
        if (val && !selectedSkills.has(val)) {
          selectedSkills.add(val);
          updateSelectedBox(selectedBox);
        }
      }
    });
  }

  // Clear all button
  const clearBtn = document.getElementById('clear-skills');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      selectedSkills.clear();
      chips.forEach(c => c.classList.remove('selected'));
      updateSelectedBox(selectedBox);
    });
  }

  // AI Resume Parsing handling
  const resumeUpload = document.getElementById('resume-upload');
  if (resumeUpload) {
    resumeUpload.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      
      const uploadText = document.getElementById('resume-upload-text');
      uploadText.textContent = 'Parsing...';
      
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const token = getCookie('access_token');
        const res = await fetch(`${API_BASE}/profile/parse-resume`, {
          method: 'POST',
          headers: token ? { 'Authorization': `Bearer ${token}` } : {},
          body: formData
        });
        
        if (!res.ok) {
          const errData = await res.json().catch(() => null);
          throw new Error(errData?.detail || 'Failed to parse resume. Check API key or server.');
        }
        
        const data = await res.json();
        const extractedSkills = data.skills || [];
        
        if (extractedSkills.length > 0) {
          // Clear current skills
          selectedSkills.clear();
          chips.forEach(c => c.classList.remove('selected'));
          
          // Add new skills
          extractedSkills.forEach(skill => {
            selectedSkills.add(skill);
            const chip = document.querySelector(`.skill-chip[data-skill="${CSS.escape(skill)}"]`);
            if (chip) chip.classList.add('selected');
          });
          
          updateSelectedBox(selectedBox);
          showToast(`Extracted ${extractedSkills.length} skills from resume!`, 'success');
          
          // Auto search
          if (typeof runJobSearch === 'function') {
            runJobSearch();
          }
        } else {
          showToast('No matching skills found in resume.', 'info');
        }
      } catch (err) {
        showToast(err.message, 'error');
      } finally {
        uploadText.textContent = 'Upload PDF';
        resumeUpload.value = ''; // Reset file input
      }
    });
  }
}

function updateSelectedBox(box) {
  if (!box) return;
  box.innerHTML = '';
  selectedSkills.forEach(skill => {
    const pill = document.createElement('span');
    pill.className = 'selected-pill';
    pill.textContent = skill;
    pill.title = 'Click to remove';
    pill.addEventListener('click', () => {
      selectedSkills.delete(skill);
      updateSelectedBox(box);
      // Also deselect the chip in the list
      const chip = document.querySelector(`.skill-chip[data-skill="${CSS.escape(skill)}"]`);
      if (chip) chip.classList.remove('selected');
    });
    box.appendChild(pill);
  });
}

/* =====================================================
   JOB SEARCH (Dashboard)
   ===================================================== */
function initJobSearch() {
  const searchBtn  = document.getElementById('search-btn');
  const sourceFilter = document.getElementById('source-filter');
  const sortFilter   = document.getElementById('sort-filter');

  if (searchBtn) {
    searchBtn.addEventListener('click', runJobSearch);
  }

  // Allow re-filtering without reload
  [sourceFilter, sortFilter].forEach(el => {
    if (el) el.addEventListener('change', () => {
      if (cachedJobs.length > 0) renderJobs(cachedJobs);
    });
  });

  // Initial load — show all jobs
  runJobSearch(true);
}

let cachedJobs = [];

async function runJobSearch(initial = false) {
  const grid     = document.getElementById('jobs-grid');
  const countEl  = document.getElementById('results-count');
  const searchBtn = document.getElementById('search-btn');

  if (!grid) return;

  // Build query
  const params = new URLSearchParams();
  params.set('per_page', '60');
  if (selectedSkills.size > 0) {
    params.set('skills', Array.from(selectedSkills).join(','));
  }

  // Show loading
  grid.innerHTML = skeletonCards(6);
  if (searchBtn) { searchBtn.disabled = true; searchBtn.textContent = 'Searching…'; }
  if (countEl) countEl.textContent = '';

  try {
    const token = getCookie('access_token');
    const res = await fetch(`${API_BASE}/jobs?${params}`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    cachedJobs = data.jobs || [];
    renderJobs(cachedJobs);
    if (countEl) {
      countEl.innerHTML = `Found <strong>${data.total || cachedJobs.length}</strong> matched roles`;
    }
  } catch (err) {
    console.error('Job search failed:', err);
    grid.innerHTML = errorState(err.message);
  } finally {
    if (searchBtn) { searchBtn.disabled = false; searchBtn.textContent = '🔍 Find Jobs'; }
  }
}

function renderJobs(jobs) {
  const grid       = document.getElementById('jobs-grid');
  const sourceFilter = document.getElementById('source-filter');
  const sortFilter   = document.getElementById('sort-filter');

  if (!grid) return;

  let filtered = [...jobs];

  // Filter by source
  const source = sourceFilter ? sourceFilter.value : '';
  if (source) {
    filtered = filtered.filter(j => (j.source || '').toLowerCase().includes(source));
  }

  // Sort
  const sort = sortFilter ? sortFilter.value : 'score';
  if (sort === 'score') {
    filtered.sort((a, b) => (b.attention_score || 0) - (a.attention_score || 0));
  } else if (sort === 'title') {
    filtered.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
  }

  if (filtered.length === 0) {
    grid.innerHTML = emptyState();
    return;
  }

  grid.innerHTML = filtered.map((job, i) => jobCardHTML(job, i)).join('');

  // Wire up Save buttons
  grid.querySelectorAll('.save-job-btn').forEach(btn => {
    btn.addEventListener('click', () => saveJob(btn.dataset.jobId, btn));
  });
}

function jobCardHTML(job, index) {
  const score   = job.attention_score ? Math.round(job.attention_score * 100) : null;
  const skills  = job.skills || [];
  const source  = job.source || 'unknown';

  const sourceBadge = source.includes('wwr') || source.includes('remote')
    ? 'badge-teal'
    : source.includes('nomads')
    ? 'badge-pink'
    : 'badge-muted';

  const sourceLabel = source.includes('wwr') || source.includes('remote')
    ? 'We Work Remotely'
    : source.includes('nomads')
    ? 'Working Nomads'
    : source;

  const scoreClass = score >= 70 ? 'score-high' : score >= 40 ? 'score-mid' : 'score-low';
  // description may be an array, join it
  const descText = Array.isArray(job.description) ? job.description.join(' ') : (job.description || '');

  const skillTags = skills.slice(0, 6).map(s => {
    const isMatched = selectedSkills.size > 0 &&
      Array.from(selectedSkills).some(sel => s.toLowerCase().includes(sel.toLowerCase()) || sel.toLowerCase().includes(s.toLowerCase()));
    return `<span class="job-skill-tag ${isMatched ? 'matched' : ''}">${escape(s)}</span>`;
  }).join('');

  const moreSkills = skills.length > 6 ? `<span class="job-skill-tag">+${skills.length - 6} more</span>` : '';

  return `
    <div class="job-card" style="animation-delay: ${index * 0.05}s">
      <div class="job-card-header">
        <div style="flex:1; min-width:0">
          <div class="job-title">${escapeHTML(job.title || 'Untitled Job')}</div>
          <div class="job-company">
            🏢 ${escapeHTML(job.company || 'Company not listed')}
          </div>
        </div>
        ${score !== null ? `<div class="job-score ${scoreClass}"><span>${score}</span><span style="font-size:0.6rem;font-weight:500">pts</span></div>` : ''}
      </div>

      <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center">
        <span class="badge ${sourceBadge}">📡 ${escapeHTML(sourceLabel)}</span>
        ${job.location ? `<span class="badge badge-muted">📍 ${escapeHTML(job.location)}</span>` : ''}
        ${job.job_type ? `<span class="badge badge-muted">⏱ ${escapeHTML(job.job_type)}</span>` : ''}
      </div>

      ${skills.length > 0 ? `<div class="job-skills">${skillTags}${moreSkills}</div>` : ''}

      ${descText ? `<p style="font-size:0.83rem;color:var(--text-secondary);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">${escapeHTML(descText)}</p>` : ''}

      <div class="job-footer">
        <a href="${escapeHTML(job.apply_link || '#')}"
           target="_blank" rel="noopener noreferrer"
           class="btn btn-primary btn-sm" onclick="this.textContent='Opening…'">
          🚀 Apply Now
        </a>
        <button class="btn btn-ghost btn-sm save-job-btn" data-job-id="${escapeHTML(job.id || '')}">
          🔖 Save
        </button>
      </div>
    </div>`;
}

async function saveJob(jobId, btn) {
  if (!jobId) return;
  const token = getCookie('access_token');
  if (!token) {
    showToast('Please log in to save jobs', 'error');
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Saving…';
  try {
    const res = await fetch(`${API_BASE}/applications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ job_id: jobId, status: 'saved' }),
    });
    if (res.ok) {
      btn.textContent = '✅ Saved';
      btn.classList.add('btn-teal');
      showToast('Job saved to your applications!', 'success');
    } else if (res.status === 409) {
      btn.textContent = '✅ Saved';
      showToast('Already in your saved list', 'info');
    } else {
      throw new Error(`Error ${res.status}`);
    }
  } catch (e) {
    btn.disabled = false;
    btn.textContent = '🔖 Save';
    showToast('Failed to save job', 'error');
  }
}

/* =====================================================
   APPLICATIONS CRM
   ===================================================== */
function initApplicationsCRM() {
  document.querySelectorAll('.status-select').forEach(sel => {
    sel.addEventListener('change', async () => {
      const appId  = sel.dataset.appId;
      const status = sel.value;
      const token  = getCookie('access_token');
      try {
        await fetch(`${API_BASE}/applications/${appId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ status }),
        });
        showToast('Status updated', 'success');
      } catch {
        showToast('Failed to update status', 'error');
      }
    });
  });

  document.querySelectorAll('.delete-app-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (!confirm('Remove this application?')) return;
      const appId = btn.dataset.appId;
      const token = getCookie('access_token');
      try {
        const res = await fetch(`${API_BASE}/applications/${appId}`, {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (res.ok || res.status === 204) {
          const row = btn.closest('tr');
          if (row) {
            row.style.animation = 'fadeIn 0.3s ease reverse both';
            setTimeout(() => row.remove(), 300);
          }
          showToast('Application removed', 'success');
        }
      } catch {
        showToast('Failed to remove', 'error');
      }
    });
  });
}

/* =====================================================
   SCROLL ANIMATIONS (Intersection Observer)
   ===================================================== */
function initScrollAnimations() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.feature-card, .step-card, .card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    obs.observe(el);
  });
}

/* =====================================================
   TOAST NOTIFICATIONS
   ===================================================== */
let toastContainer;

function showToast(message, type = 'info') {
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.style.cssText = `
      position: fixed; bottom: 24px; right: 24px;
      display: flex; flex-direction: column; gap: 10px;
      z-index: 9999; pointer-events: none;
    `;
    document.body.appendChild(toastContainer);
  }

  const colors = {
    success: { bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.4)', text: '#6ee7b7', icon: '✅' },
    error:   { bg: 'rgba(239,68,68,0.15)',  border: 'rgba(239,68,68,0.4)',  text: '#fca5a5', icon: '❌' },
    info:    { bg: 'rgba(99,102,241,0.15)', border: 'rgba(99,102,241,0.4)', text: '#a5b4fc', icon: 'ℹ️' },
  };
  const c = colors[type] || colors.info;

  const toast = document.createElement('div');
  toast.style.cssText = `
    display: flex; align-items: center; gap: 10px;
    padding: 12px 18px;
    background: ${c.bg};
    border: 1px solid ${c.border};
    border-radius: 10px;
    color: ${c.text};
    font-size: 0.875rem;
    font-weight: 500;
    font-family: var(--font-sans);
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    pointer-events: all;
    animation: fadeSlideUp 0.3s ease both;
    max-width: 320px;
  `;
  toast.innerHTML = `<span>${c.icon}</span><span>${escapeHTML(message)}</span>`;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'fadeIn 0.3s ease reverse both';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* =====================================================
   SKELETON / STATE HTML
   ===================================================== */
function skeletonCards(n) {
  return Array.from({ length: n }, () => `
    <div class="skeleton-card">
      <div class="flex" style="gap:12px">
        <div style="flex:1">
          <div class="skeleton" style="height:20px;width:70%;margin-bottom:10px"></div>
          <div class="skeleton" style="height:14px;width:45%"></div>
        </div>
        <div class="skeleton" style="width:44px;height:44px;border-radius:10px"></div>
      </div>
      <div class="flex gap-8">
        <div class="skeleton" style="height:22px;width:110px;border-radius:99px"></div>
        <div class="skeleton" style="height:22px;width:80px;border-radius:99px"></div>
      </div>
      <div class="flex gap-8">
        ${[60,80,70,55].map(w=>`<div class="skeleton" style="height:22px;width:${w}px;border-radius:99px"></div>`).join('')}
      </div>
      <div class="skeleton" style="height:14px;margin-bottom:6px"></div>
      <div class="skeleton" style="height:14px;width:80%"></div>
      <div class="flex gap-8" style="margin-top:8px">
        <div class="skeleton" style="height:34px;width:110px;border-radius:99px"></div>
        <div class="skeleton" style="height:34px;width:90px;border-radius:99px"></div>
      </div>
    </div>`).join('');
}

function emptyState() {
  return `
    <div class="state-message" style="grid-column:1/-1">
      <div class="state-icon">🔍</div>
      <div class="state-title">No jobs found</div>
      <div class="state-desc">Try different skills or remove some filters.</div>
    </div>`;
}

function errorState(msg) {
  return `
    <div class="state-message" style="grid-column:1/-1">
      <div class="state-icon">⚠️</div>
      <div class="state-title">Something went wrong</div>
      <div class="state-desc">${escapeHTML(msg || 'Failed to load jobs. Make sure the API server is running.')}</div>
    </div>`;
}

/* =====================================================
   UTILITIES
   ===================================================== */
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

function escapeHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escape(str) { return escapeHTML(str); }
