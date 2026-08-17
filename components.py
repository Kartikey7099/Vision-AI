import re
import html as html_lib
import streamlit as st


def render_html(raw: str):
    """Safely render a (possibly indented / multi-line) HTML template."""
    collapsed = re.sub(r">\s+<", "><", raw.strip())
    collapsed = re.sub(r"\s+", " ", collapsed)  # also flatten whitespace inside tags/attrs
    st.markdown(collapsed, unsafe_allow_html=True)


def esc(text) -> str:
    """HTML-escape user/data text before interpolating it into a template.

    Critical for anything that can contain literal angle brackets — e.g. task
    tags like '<OD>' or '<CAPTION>'. Without this, the browser tries to parse
    '<OD>' as a real (unknown) tag and can swallow everything after it until
    it finds a non-existent closing '</OD>', silently breaking the rest of
    the page — this was the second bug behind the earlier broken UI.
    """
    return html_lib.escape(str(text), quote=True)


def stat_card(icon, color, label, value, sub, trend=None):
    trend_html = ""
    if trend:
        cls = "trend-up" if trend.startswith("+") else "trend-flat"
        trend_html = f'<span class="{cls}">{esc(trend)}</span>'
    render_html(f"""
        <div class="vcard fade-in">
            <div class="stat-icon" style="background:{color}22;color:{color};">{icon}</div>
            <div class="stat-label">{esc(label)}</div>
            <div class="stat-value">{esc(value)}</div>
            <div class="stat-sub">{esc(sub)} {trend_html}</div>
        </div>
    """)


def capability_card_html(cap, is_new=False, is_favorite=False):
    new_badge = '<div class="new-badge">NEW</div>' if is_new else ""
    fav_icon = "⭐" if is_favorite else ""
    # NOTE: cap['tag'] looks like "<OD>" — it MUST be escaped, or the browser
    # tries to parse it as a real HTML tag and can swallow the rest of the page.
    render_html(f"""
        <div class="cap-card fade-in" style="--accent:{cap['accent']}; --glow:{cap['accent']}33;" title="{esc(cap['desc'])}">
            {new_badge}
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div class="cap-icon" style="background:{cap['accent']}22;color:{cap['accent']};">{cap['icon']}</div>
                <div style="font-size:0.9rem;">{fav_icon}</div>
            </div>
            <div class="cap-title">{esc(cap['title'])}</div>
            <div class="cap-desc">{esc(cap['desc'])}</div>
            <span class="cap-tag">{esc(cap['tag'])}</span>
        </div>
    """)


def section_header(title, sub=None):
    render_html(f'<div class="section-title">{title}</div>')
    if sub:
        render_html(f'<div class="section-sub">{sub}</div>')


def pill(text, color="#a855f7"):
    return f'<span class="pill" style="color:{color};border-color:{color}55;">{text}</span>'


def divider():
    render_html('<div class="divider-fade"></div>')


def glass_panel(inner_html: str, extra_style: str = ""):
    render_html(f'<div class="vcard fade-in" style="{extra_style}">{inner_html}</div>')
