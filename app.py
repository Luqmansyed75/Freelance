"""
Freelance Job Matcher — API Powered Streamlit UI
Search jobs and manage applications via the FastAPI backend.
"""
import streamlit as st
import requests
import html as html_lib
import time

API_BASE = "http://127.0.0.1:8000/api/v1"

# ─── Page Config ───
st.set_page_config(
    page_title="Freelance Job Matcher",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ══════ GLOBAL ══════ */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0a1a 0%, #0f1629 30%, #121a30 60%, #0d1117 100%); }
#MainMenu, footer, header {visibility: hidden;}

/* ══════ ANIMATED BACKGROUND ORB ══════ */
.orb-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; overflow: hidden; }
.orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.12; animation: orbFloat 20s ease-in-out infinite; }
.orb-1 { width: 500px; height: 500px; background: radial-gradient(circle, #667eea 0%, transparent 70%); top: -100px; left: -100px; animation-delay: 0s; }
.orb-2 { width: 400px; height: 400px; background: radial-gradient(circle, #764ba2 0%, transparent 70%); bottom: -80px; right: -80px; animation-delay: -7s; }
.orb-3 { width: 300px; height: 300px; background: radial-gradient(circle, #f093fb 0%, transparent 70%); top: 40%; left: 60%; animation-delay: -14s; }
@keyframes orbFloat { 0%, 100% { transform: translate(0, 0) scale(1); } 25% { transform: translate(40px, -30px) scale(1.1); } 50% { transform: translate(-20px, 40px) scale(0.95); } 75% { transform: translate(30px, 20px) scale(1.05); } }

/* ══════ HERO SECTION ══════ */
.hero-container { text-align: center; padding: 40px 20px 10px; position: relative; z-index: 1; }
.hero-title { font-size: 3.2rem; font-weight: 900; background: linear-gradient(135deg, #667eea 0%, #764ba2 35%, #f093fb 65%, #667eea 100%); background-size: 300% 300%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradientShift 6s ease-in-out infinite; margin-bottom: 8px; letter-spacing: -1px; line-height: 1.2; }
@keyframes gradientShift { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.hero-sub { text-align: center; color: #64748b; font-size: 1.1rem; font-weight: 400; margin-top: 0; margin-bottom: 6px; letter-spacing: 0.3px; }
.hero-divider { width: 80px; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); margin: 16px auto 30px; border-radius: 3px; }

/* ══════ STATS DASHBOARD ══════ */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; padding: 0 10px; }
.stat-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; text-align: center; backdrop-filter: blur(20px); position: relative; overflow: hidden; transition: all 0.3s ease; }
.stat-card:hover { border-color: rgba(102, 126, 234, 0.3); transform: translateY(-2px); box-shadow: 0 8px 30px rgba(102, 126, 234, 0.1); }
.stat-icon { font-size: 1.6rem; margin-bottom: 8px; display: block; }
.stat-num { font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #667eea, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2; }
.stat-label { color: #64748b; font-size: 0.75rem; margin-top: 4px; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }

/* ══════ HOW IT WORKS ══════ */
.how-it-works { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; max-width: 900px; margin: 40px auto; padding: 0 20px; }
.step-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 20px; padding: 32px 24px; text-align: center; backdrop-filter: blur(20px); }
.step-num { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; font-weight: 800; font-size: 1rem; margin-bottom: 16px; }
.step-icon { font-size: 2.5rem; margin-bottom: 12px; display: block; }
.step-title { color: #e2e8f0; font-weight: 700; font-size: 1.05rem; margin-bottom: 8px; }
.step-desc { color: #64748b; font-size: 0.85rem; line-height: 1.5; }
.hiw-heading { text-align: center; color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 3px; font-weight: 600; margin-top: 40px; margin-bottom: 4px; }
.hiw-title { text-align: center; color: #e2e8f0; font-size: 1.6rem; font-weight: 800; margin-bottom: 24px; }

/* ══════ EMPTY / NO-RESULTS ══════ */
.empty-state { text-align: center; padding: 60px 20px 40px; color: #64748b; }
.empty-state .icon { font-size: 4rem; margin-bottom: 20px; display: block; animation: emptyBounce 2s ease-in-out infinite; }
@keyframes emptyBounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
.empty-state h3 { color: #cbd5e1; font-weight: 700; font-size: 1.3rem; margin-bottom: 8px; }

/* ══════ SECTION HEADERS ══════ */
.section-header { display: flex; align-items: center; gap: 10px; margin: 28px 0 18px; padding-left: 4px; }
.section-header .label { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }
.section-header .line { flex: 1; height: 1px; background: linear-gradient(90deg, rgba(100,116,139,0.3), transparent); }

/* ══════ SIDEBAR ══════ */
[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(10, 10, 30, 0.98) 0%, rgba(15, 22, 41, 0.98) 100%); border-right: 1px solid rgba(255,255,255,0.04); }
.sidebar-brand { text-align: center; padding: 16px 0 20px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 20px; }
.sidebar-brand .logo { font-size: 2rem; display: block; margin-bottom: 6px; }
.sidebar-brand .name { font-size: 1rem; font-weight: 800; background: linear-gradient(135deg, #667eea, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.3px; }
.sidebar-brand .version { color: #475569; font-size: 0.7rem; margin-top: 2px; letter-spacing: 1px; }
.sidebar-section { font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 2px; margin: 22px 0 10px; display: flex; align-items: center; gap: 8px; }
.sidebar-section::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.06); }
.sidebar-hint { color: #475569; font-size: 0.78rem; margin-bottom: 12px; line-height: 1.4; }

/* ══════ FOOTER ══════ */
.app-footer { text-align: center; padding: 40px 20px 20px; border-top: 1px solid rgba(255,255,255,0.04); margin-top: 40px; }
.app-footer .brand { font-size: 0.85rem; font-weight: 700; background: linear-gradient(135deg, #667eea, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
.app-footer .tech-badge { padding: 3px 10px; border-radius: 6px; font-size: 0.68rem; font-weight: 600; background: rgba(255,255,255,0.04); color: #64748b; border: 1px solid rgba(255,255,255,0.06); }

/* Force Streamlit buttons under cards */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #38bdf8, #818cf8); color: white; border: none; border-radius: 8px; font-weight: 600; transition: all 0.3s;
}
div[data-testid="stButton"] button:hover { box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4); transform: translateY(-1px); }

/* Primary Dustbin Button */
div[data-testid="stButton"] button[kind="primary"] {
    background: #ea2b2b !important; border-radius: 50% !important; width: 58px !important; height: 58px !important; padding: 0 !important; border: none !important; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 6px 15px rgba(234, 43, 43, 0.3) !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative;
}
div[data-testid="stButton"] button[kind="primary"]:hover { transform: translateY(-2px) scale(1.05); box-shadow: 0 10px 25px rgba(234, 43, 43, 0.5) !important; }
div[data-testid="stButton"] button[kind="primary"] p { display: none !important; }
div[data-testid="stButton"] button[kind="primary"]::after { content: ''; width: 26px; height: 26px; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'/%3E%3C/svg%3E"); background-size: contain; background-repeat: no-repeat; background-position: center; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); display: block; }

/* Custom Radio Navigation */
div[data-testid="stRadio"] > div[role="radiogroup"] { gap: 12px; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); border-radius: 12px; padding: 14px 16px; cursor: pointer; transition: all 0.3s ease; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { background: rgba(255,255,255,0.12); border-color: rgba(102, 126, 234, 0.5); }
div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child { display: none; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label p { font-weight: 700; font-size: 0.95rem; color: #cbd5e1; margin: 0; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) { background: linear-gradient(135deg, #667eea, #764ba2); border-color: #a78bfa; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4); transform: scale(1.02); }
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p { color: #ffffff; font-size: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)


# ─── Auth State Management ───
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

def fetch_user_profile():
    if not st.session_state.token: return
    try:
        resp = requests.get(f"{API_BASE}/auth/me", headers=get_auth_headers(), timeout=5)
        if resp.status_code == 200:
            st.session_state.user = resp.json()
        else:
            st.session_state.token = None
            st.session_state.user = None
    except Exception:
        pass


# ─── API Helper Functions ───
@st.cache_data(ttl=60)
def fetch_jobs(page=1, per_page=20, source=None, skills=None):
    params = {"page": page, "per_page": per_page}
    if source and source != "All":
        params["source"] = source
    if skills:
        params["skills"] = ",".join(skills)
    
    try:
        r = requests.get(f"{API_BASE}/jobs", params=params, timeout=10)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        return None

def save_job_api(job_id):
    if not st.session_state.token: return False, "Not logged in"
    try:
        r = requests.post(f"{API_BASE}/applications", json={"job_id": job_id}, headers=get_auth_headers(), timeout=5)
        if r.status_code == 201: return True, "Saved!"
        if r.status_code == 409: return False, "Already saved!"
        return False, f"Error: {r.text}"
    except Exception as e:
        return False, str(e)

def delete_job_api(app_id):
    if not st.session_state.token: return False
    try:
        r = requests.delete(f"{API_BASE}/applications/{app_id}", headers=get_auth_headers(), timeout=5)
        return r.status_code == 204
    except:
        return False

def get_my_applications():
    if not st.session_state.token: return []
    try:
        r = requests.get(f"{API_BASE}/applications", headers=get_auth_headers(), timeout=5)
        return r.json() if r.status_code == 200 else []
    except:
        return []


# ─── HTML Generator ───
def generate_job_card_html(job, rank_idx=None, max_score=1):
    score = job.get('attention_score', 0)
    score_pct = min((score / max_score) * 100, 100) if max_score else 0
    job_skills = job.get('skills', [])
    source = job.get('source', '')
    salary = job.get('salary', {})

    rank_badge = ""
    if rank_idx == 0: rank_badge = '<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#fbbf24,#f59e0b);color:#000;font-weight:800;font-size:0.75rem;margin-right:10px;flex-shrink:0;">1</span>'
    elif rank_idx == 1: rank_badge = '<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#94a3b8,#cbd5e1);color:#000;font-weight:800;font-size:0.75rem;margin-right:10px;flex-shrink:0;">2</span>'
    elif rank_idx == 2: rank_badge = '<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,#d97706,#b45309);color:#fff;font-weight:800;font-size:0.75rem;margin-right:10px;flex-shrink:0;">3</span>'

    source_badge = '<span class="badge badge-wwr">💼 WWR</span>' if source == 'wwr' else '<span class="badge badge-nomad">🧳 Nomads</span>'
    
    # We don't have matched keyword logic strictly synced to UI search terms right now due to server scoring, so simple colors
    salary_badge = ""
    if salary.get('min') or salary.get('max'):
        s_min = f"${salary['min']:,.0f}" if salary.get('min') else ""
        s_max = f"${salary['max']:,.0f}" if salary.get('max') else ""
        salary_str = f"{s_min} – {s_max}" if s_min and s_max else (s_min or s_max)
        salary_badge = f'<span class="badge badge-salary">💰 {salary_str}</span>'

    safe_title = html_lib.escape(job.get('title', 'Untitled'))
    safe_company = html_lib.escape(job.get('company', 'Unknown'))
    apply_link = job.get('apply_link', '#')

    skills_html = ""
    if job_skills:
        tags = []
        for sk in job_skills:
            safe_sk = html_lib.escape(sk)
            tags.append(f'<span class="skill-tag skill-matched">{safe_sk}</span>')
        skills_html = '<div class="skills-wrap">' + "".join(tags) + '</div>'

    desc_items = job.get('description', [])
    desc_text = ""
    if desc_items:
        clean_desc = [html_lib.escape(d) for d in desc_items if d and d.lower() not in ('contract',)]
        if clean_desc: desc_text = f'<p class="desc-text">{" · ".join(clean_desc)}</p>'

    card = f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: transparent; font-family: 'Inter', -apple-system, sans-serif; }}
            .card {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 24px 28px; position: relative; overflow: hidden; }}
            .card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: linear-gradient(180deg, #667eea, #764ba2); border-radius: 4px 0 0 4px; }}
            .title-row {{ display: flex; align-items: center; margin-bottom: 4px; }}
            .title {{ font-size: 1.2rem; font-weight: 700; color: #e2e8f0; line-height: 1.3; }}
            .company {{ color: #64748b; font-size: 0.9rem; margin-bottom: 14px; font-weight: 500; }}
            .badge-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }}
            .badge {{ display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }}
            .badge-wwr {{ background: rgba(56, 178, 172, 0.12); color: #5eead4; border: 1px solid rgba(56, 178, 172, 0.25); }}
            .badge-nomad {{ background: rgba(251, 146, 60, 0.12); color: #fdba74; border: 1px solid rgba(251, 146, 60, 0.25); }}
            .badge-salary {{ background: rgba(34, 197, 94, 0.12); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.25); }}
            .skills-wrap {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; margin-top: 10px; }}
            .skill-tag {{ display: inline-block; padding: 3px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; }}
            .skill-matched {{ background: rgba(102, 126, 234, 0.15); color: #a5b4fc; border: 1px solid rgba(102, 126, 234, 0.3); }}
            .desc-text {{ color: #475569; font-size: 0.8rem; margin-top: 8px; font-style: italic; line-height: 1.4; }}
            .apply-btn {{ display: inline-flex; padding: 10px 24px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; text-decoration: none; border-radius: 10px; font-weight: 700; font-size: 0.85rem; margin-top: 16px; transition: all 0.3s; }}
            .apply-btn:hover {{ transform: translateY(-1px); box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4); }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="title-row">{rank_badge}<span class="title">{safe_title}</span></div>
            <div class="company">{safe_company}</div>
            <div class="badge-row">{source_badge}{salary_badge}</div>
            {skills_html}
            {desc_text}
            <a href="{apply_link}" target="_blank" class="apply-btn">Apply / Learn More&nbsp;→</a>
        </div>
    </body>
    </html>
    """
    return card


# ─── Sidebar ───
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><span class="logo">🎯</span><div class="name">Job Matcher</div><div class="version">API BACKEND • v3.0</div></div>', unsafe_allow_html=True)
    
    # ── User Account Section ──
    st.markdown('<div class="sidebar-section">👤 Account</div>', unsafe_allow_html=True)
    
    if st.session_state.token and not st.session_state.user:
        fetch_user_profile()
        
    if st.session_state.user:
        user = st.session_state.user
        st.success(f"Logged in as:\n**{user['email']}**")
        
        if user.get("is_admin"):
            if st.button("🚀 Trigger Scraper Pipeline"):
                v = requests.post(f"{API_BASE}/jobs/trigger-pipeline", headers=get_auth_headers())
                if v.status_code == 202:
                    st.toast("Pipeline started in background!", icon="🔥")
                else:
                    st.error("Action denied.")

        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()
    else:
        auth_mode = st.radio("Account Action", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
        with st.form("auth_form"):
            email = st.text_input("Email", placeholder="you@domain.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button(auth_mode)
            
            if submit and email and password:
                if auth_mode == "Login":
                    r = requests.post(f"{API_BASE}/auth/token", data={"username": email, "password": password})
                    if r.status_code == 200:
                        st.session_state.token = r.json().get("access_token")
                        st.success("Logged in!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                else:
                    r = requests.post(f"{API_BASE}/auth/register", json={"email": email, "password": password})
                    if r.status_code == 201:
                        st.success("Account created! Please log in.")
                    elif r.status_code == 409:
                        st.error("Email already registered.")
                    else:
                        st.error("Error creating account.")

    st.markdown('---')
    nav = st.radio("Navigation", ["🔍 Search Jobs", "📂 My Applications"], label_visibility="collapsed")
    st.markdown('---')

    st.markdown('<div class="sidebar-section">🎯 Your Skills</div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-hint">Enter skills to filter results</p>', unsafe_allow_html=True)
    skill_input = st.text_input("Enter skills", placeholder="python, react, remote", label_visibility="collapsed")
    
    st.markdown('<div class="sidebar-section">🔍 API Filters</div>', unsafe_allow_html=True)
    source_filter = st.selectbox("Source", options=["All", "working_nomads", "wwr"], format_func=lambda x: {"All": "🌐 All", "working_nomads": "🧳 Nomads", "wwr": "💼 WWR"}.get(x, x))
    top_n = st.slider("Max results per page", min_value=5, max_value=50, value=20, step=5)
    
    user_keywords = [s.strip() for s in skill_input.split(",")] if skill_input else []


# ─── Animated Background ───
st.markdown('<div class="orb-container"><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div></div>', unsafe_allow_html=True)

# ─── Main Content ───
if nav == "🔍 Search Jobs":
    st.markdown('<div class="hero-container"><h1 class="hero-title">Freelance Job Matcher</h1><p class="hero-sub">API-powered skill matching to find your perfect remote opportunity</p><div class="hero-divider"></div></div>', unsafe_allow_html=True)
    
    # Always fetch from API
    with st.spinner("Fetching jobs from API..."):
        resp_data = fetch_jobs(page=1, per_page=top_n, source=source_filter, skills=user_keywords)

    if not resp_data or not resp_data.get("jobs"):
        if not user_keywords and source_filter == "All":
            st.markdown('<div class="empty-state"><span class="icon">📡</span><h3>Cannot connect to API</h3><p>Ensure your FastAPI server is running on port 8000.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state"><span class="icon">😕</span><h3>No matching jobs found</h3><p>Try reducing your filter criteria.</p></div>', unsafe_allow_html=True)
    else:
        results = resp_data["jobs"]
        total = resp_data["total"]
        st.markdown(f'<div class="stats-grid"><div class="stat-card"><span class="stat-icon">📊</span><div class="stat-num">{len(results)}</div><div class="stat-label">Displayed</div></div><div class="stat-card"><span class="stat-icon">🗄️</span><div class="stat-num">{total}</div><div class="stat-label">Total in DB</div></div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-header"><span class="label">🏆 Latest Jobs</span><div class="line"></div></div>', unsafe_allow_html=True)
        for idx, job in enumerate(results):
            st.html(generate_job_card_html(job, rank_idx=idx))
            
            # Action Buttons
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("💾 Save", key=f"save_{job['id']}", help="Save to CRM"):
                    if st.session_state.token:
                        success, text = save_job_api(job['id'])
                        if success:
                            st.toast(f"Saved {job['company']}!", icon="✅")
                        else:
                            st.toast(text, icon="ℹ️")
                    else:
                        st.warning("Please log in via the sidebar to use the CRM.")


elif nav == "📂 My Applications":
    st.markdown('<div class="hero-container"><h1 class="hero-title">My Applications</h1><p class="hero-sub">Your personal CRM for saved job opportunities</p><div class="hero-divider"></div></div>', unsafe_allow_html=True)
    
    if not st.session_state.token:
        st.markdown('<div class="empty-state"><span class="icon">🔒</span><h3>Authentication Required</h3><p>Please log in via the sidebar to view your saved applications.</p></div>', unsafe_allow_html=True)
    else:
        with st.spinner("Loading your CRM data..."):
            saved_apps = get_my_applications()
        
        if not saved_apps:
            st.markdown('<div class="empty-state"><span class="icon">📂</span><h3>No saved jobs yet</h3><p>Go to your Job Search and click "Save" on jobs you like!</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f"**Total Saved Jobs:** {len(saved_apps)}")
            
            for app in saved_apps:
                job_data = app['job']
                if not job_data: continue
                # Render using the nested job dictionary
                st.html(generate_job_card_html(job_data, rank_idx=None))
                
                col1, col2 = st.columns([1, 10])
                with col1:
                    # Primary type makes it pick up our circular red dustbin CSS
                    if st.button("Delete", key=f"del_{app['id']}", type="primary", help="Delete from CRM"):
                        if delete_job_api(app['id']):
                            st.toast(f"Removed from your CRM.", icon="🗑️")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.toast("⚠️ Could not delete job.", icon="⚠️")

# ─── Footer ───
st.markdown('<div class="app-footer"><div class="brand">Freelance Job Matcher Platform</div><div class="tech-badge">FastAPI + Streamlit</div></div>', unsafe_allow_html=True)
