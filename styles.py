CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --accent-1: #7c3aed;
    --accent-2: #a855f7;
}

* { font-family: 'Inter', -apple-system, sans-serif; }
code, .mono { font-family: 'JetBrains Mono', monospace !important; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---------------- Background ---------------- */
.stApp {
    background:
        radial-gradient(ellipse 60% 40% at 85% -5%, rgba(139,92,246,0.22), transparent 60%),
        radial-gradient(ellipse 50% 35% at -5% 10%, rgba(59,130,246,0.14), transparent 55%),
        radial-gradient(ellipse 40% 30% at 60% 100%, rgba(236,72,153,0.08), transparent 60%),
        #08070f;
    color: #e5e7eb;
}
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1360px; }

/* ---------------- Sidebar ---------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0b18 0%, #0a0812 100%);
    border-right: 1px solid #211d33;
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.1rem; }

/* ---------------- Scrollbar ---------------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0d0b18; }
::-webkit-scrollbar-thumb { background: #2e2848; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent-1); }

/* ---------------- Entrance animation ---------------- */
@keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeInUp .45s cubic-bezier(.16,1,.3,1) both; }

/* ---------------- Hero ---------------- */
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.35);
    color: #c4b5fd; padding: 5px 14px; border-radius: 20px;
    font-size: 0.78rem; font-weight: 600; margin-bottom: 0.9rem;
}
.hero-eyebrow { color: #a78bfa; font-weight: 700; font-size: 1.35rem; margin-bottom: 0.1rem; }
.hero-title {
    font-size: 3.1rem; font-weight: 900; line-height: 1.08; margin: 0 0 0.9rem 0;
    background: linear-gradient(100deg, #ffffff 0%, #d8c9ff 45%, #93c5fd 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-size: 200% auto;
    animation: shine 6s linear infinite;
}
@keyframes shine { to { background-position: 200% center; } }
.hero-sub { color: #9ca3af; font-size: 1.05rem; max-width: 620px; line-height: 1.65; }

.floaty { animation: floaty 5s ease-in-out infinite; }
@keyframes floaty { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-14px); } }

/* ---------------- Sidebar shell ---------------- */
.sb-brand {
    display: flex; align-items: center; gap: 10px; margin-bottom: 1rem; position: relative;
}
.sb-version {
    margin-left: auto; font-size: 0.62rem; font-weight: 700; color: #a78bfa;
    background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.3);
    padding: 2px 7px; border-radius: 20px; letter-spacing: 0.03em;
}
.sb-snapshot {
    display: flex; align-items: center; justify-content: space-between;
    background: linear-gradient(160deg, rgba(23,20,38,0.9), rgba(15,13,26,0.9));
    border: 1px solid #241f38; border-radius: 12px; padding: 0.7rem 0.5rem;
    margin-bottom: 1.1rem;
}
.sb-snap-item { flex: 1; text-align: center; }
.sb-snap-value { font-size: 1.15rem; font-weight: 800; color: #f9fafb; line-height: 1.1; }
.sb-snap-label { font-size: 0.65rem; color: #7c7a8c; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }
.sb-snap-divider { width: 1px; height: 26px; background: #241f38; }

.sb-heading {
    display: flex; align-items: center; gap: 6px;
    color: #7c7a8c; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.09em;
    margin: 0.2rem 0 0.5rem 2px;
}

.sb-thumb-wrap {
    border: 1px solid #241f38; border-radius: 12px; overflow: hidden;
    background: #0f0d1c; margin-bottom: 0.5rem;
}
.sb-thumb-wrap img { display: block; }
.sb-thumb-name {
    font-size: 0.72rem; color: #9ca3af; padding: 6px 10px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    border-top: 1px solid #1c1830;
}

.sb-footer {
    margin-top: 1.4rem; text-align: center; color: #4b5065;
    font-size: 0.68rem; line-height: 1.6; padding-bottom: 0.5rem;
}

/* Sidebar nav buttons: left-align icon + label, gentle default state */
section[data-testid="stSidebar"] div.stButton > button {
    text-align: left; justify-content: flex-start; display: flex;
}
section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
    background: transparent; border: 1px solid transparent;
}
section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
    background: #14121f; border-color: #241f38;
}


.vcard {
    background: linear-gradient(160deg, rgba(23,20,38,0.9) 0%, rgba(15,13,26,0.9) 100%);
    border: 1px solid #241f38;
    border-radius: 16px;
    padding: 1.15rem 1.3rem;
    height: 100%;
    backdrop-filter: blur(6px);
    transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
}
.vcard:hover { border-color: #4c3a8a; box-shadow: 0 8px 28px rgba(124,58,237,0.14); }

.stat-icon {
    width: 40px; height: 40px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; margin-bottom: 0.65rem;
}
.stat-label { color: #9ca3af; font-size: 0.7rem; letter-spacing: 0.08em; font-weight: 700; text-transform: uppercase; }
.stat-value { font-size: 1.65rem; font-weight: 800; color: #f9fafb; margin-top: 0.1rem; }
.stat-sub { color: #6b7280; font-size: 0.78rem; margin-top: 0.15rem; display:flex; align-items:center; gap:4px;}
.trend-up { color: #34d399; font-weight: 700; }
.trend-flat { color: #6b7280; font-weight: 700; }

/* ---------------- Capability cards ---------------- */
.cap-card {
    position: relative; overflow: hidden; cursor: default;
    background: linear-gradient(160deg, rgba(23,20,38,0.95) 0%, rgba(14,12,24,0.95) 100%);
    border: 1px solid #241f38; border-radius: 16px;
    padding: 1.25rem 1.35rem; height: 205px;
    display: flex; flex-direction: column;
    transition: all .22s ease;
}
.cap-card::before {
    content:''; position:absolute; inset:0; opacity:0; transition: opacity .25s ease;
    background: radial-gradient(120px 80px at 20% 0%, var(--glow, rgba(139,92,246,0.25)), transparent 70%);
}
.cap-card:hover { border-color: var(--accent, #7c3aed); transform: translateY(-4px); box-shadow: 0 14px 32px rgba(0,0,0,0.35); }
.cap-card:hover::before { opacity: 1; }
.cap-icon {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; margin-bottom: 0.7rem;
}
.cap-title { font-weight: 700; color: #f3f4f6; font-size: 1.03rem; }
.cap-desc { color: #9ca3af; font-size: 0.82rem; margin-top: 0.35rem; flex-grow: 1; line-height: 1.45; }
.cap-tag {
    display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    color: #34d399; background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.25);
    padding: 2px 8px; border-radius: 6px; width: fit-content;
}
.new-badge {
    position: absolute; top: 10px; right: 10px;
    background: linear-gradient(90deg,#f97316,#ec4899); color: white;
    font-size: 0.62rem; font-weight: 800; padding: 2px 7px; border-radius: 20px;
    letter-spacing: 0.04em;
}

/* ---------------- Model card / badges ---------------- */
.model-card {
    background: linear-gradient(160deg, rgba(23,20,38,0.95), rgba(14,12,24,0.95));
    border: 1px solid #241f38; border-radius: 14px; padding: 0.95rem;
}
.badge-ready { display: inline-flex; align-items: center; gap: 5px; color: #34d399; font-size: 0.78rem; font-weight: 600; }
.badge-dot { width: 7px; height: 7px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px #34d399; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

.pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: #1c1830; border: 1px solid #322a52; color: #c4b5fd;
    padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 600;
}

/* ---------------- Buttons ---------------- */
div.stButton > button {
    background: #17142a; border: 1px solid #2a2545; color: #d1d5db;
    border-radius: 10px; font-weight: 600; width: 100%;
    transition: all .18s ease;
}
div.stButton > button:hover { border-color: var(--accent-1); color: #fff; background: #1c1830; transform: translateY(-1px); }
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
    border: none; color: white; box-shadow: 0 6px 18px rgba(124,58,237,0.35);
}
div.stButton > button[kind="primary"]:hover { box-shadow: 0 8px 24px rgba(124,58,237,0.5); transform: translateY(-2px); }
.nav-active > button {
    background: linear-gradient(90deg, var(--accent-1), var(--accent-2)) !important;
    color: white !important; border: none !important;
    box-shadow: 0 4px 14px rgba(124,58,237,0.35);
}

/* ---------------- Task chooser chips ---------------- */
.task-chip {
    border: 1px solid #241f38; border-radius: 12px; padding: 0.6rem 0.8rem;
    background: rgba(23,20,38,0.7); transition: all .18s ease; height: 100%;
}
.task-chip:hover { border-color: var(--accent-1); }
.task-chip.selected { border-color: var(--accent-2); background: rgba(124,58,237,0.14); box-shadow: 0 0 0 1px var(--accent-2) inset; }

/* ---------------- Section headers ---------------- */
.section-title { font-size: 1.35rem; font-weight: 800; color: #f9fafb; display:flex; align-items:center; gap:8px;}
.section-sub { color: #9ca3af; font-size: 0.9rem; margin-top: 2px; margin-bottom: 1rem;}

/* ---------------- Misc ---------------- */
.divider-fade { height:1px; background: linear-gradient(90deg, transparent, #2a2545, transparent); margin: 1.2rem 0; }
.gh-card { background: linear-gradient(135deg,#1e1b3a,#161229); border:1px solid #2a2545; border-radius:14px; padding:0.85rem; }

.history-row { border-bottom: 1px solid #1c1830; padding: 10px 4px; }
.history-row:hover { background: rgba(124,58,237,0.06); border-radius: 8px; }

.tag-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }

[data-testid="stMetricValue"] { color: #f9fafb; }

.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: #14121f; border-radius: 10px 10px 0 0; color:#9ca3af; padding: 8px 16px;
}
.stTabs [aria-selected="true"] { background: #1c1830 !important; color: #fff !important; }

.stProgress > div > div { background: linear-gradient(90deg, var(--accent-1), var(--accent-2)); }

/* ---------------- Skeleton loader ---------------- */
.skeleton {
    background: linear-gradient(90deg, #17142a 25%, #201c38 37%, #17142a 63%);
    background-size: 400% 100%;
    animation: skeleton-loading 1.4s ease infinite;
    border-radius: 10px;
}
@keyframes skeleton-loading { 0% { background-position: 100% 50%; } 100% { background-position: 0 50%; } }

/* ---------------- Command bar ---------------- */
div[data-testid="stTextInput"] input {
    background: #14121f !important; border: 1px solid #241f38 !important;
    border-radius: 10px !important; color: #e5e7eb !important;
}
div[data-testid="stTextInput"] input:focus { border-color: var(--accent-1) !important; box-shadow: 0 0 0 2px rgba(124,58,237,0.25) !important; }

/* Selectbox / radio styling */
div[data-baseweb="select"] > div { background: #14121f !important; border-color: #241f38 !important; }
</style>
"""


def accent_override_css(accent_1: str, accent_2: str) -> str:
    """A tiny stylesheet that overrides the CSS accent variables at runtime,
    letting the user pick a custom theme color from the sidebar."""
    return f"""
    <style>
        :root {{ --accent-1: {accent_1}; --accent-2: {accent_2}; }}
    </style>
    """
