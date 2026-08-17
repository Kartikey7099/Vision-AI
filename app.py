import io
import os
import json
import time
import platform
import zipfile
from datetime import datetime

import streamlit as st
from PIL import Image

from styles import CSS, accent_override_css
from components import stat_card, capability_card_html, section_header, divider, render_html, pill, esc
from florence_utils import TASK_REGISTRY, execute_task, NATIVE_MODEL_ID, load_model, backend_label

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_DIR = os.path.join(APP_DIR, "assets", "demo_images")

# --------------------------------------------------------------------------------------
# PAGE CONFIG + STYLES
# --------------------------------------------------------------------------------------
st.set_page_config(page_title="Vision AI Studio Pro", page_icon="👁️", layout="wide",
                    initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# CAPABILITY DEFINITIONS (grouped)
# --------------------------------------------------------------------------------------
CAPABILITIES = [
    {"key": "od", "title": "Object Detection", "desc": "Detect objects and return bounding boxes.",
     "tag": "<OD>", "icon": "🎯", "accent": "#8b5cf6", "group": "Detection"},
    {"key": "caption", "title": "Image Captioning", "desc": "Generate a short caption describing the image.",
     "tag": "<CAPTION>", "icon": "📄", "accent": "#22c55e", "group": "Captioning"},
    {"key": "detailed_caption", "title": "Detailed Caption", "desc": "Generate a detailed image description.",
     "tag": "<DETAILED_CAPTION>", "icon": "📘", "accent": "#3b82f6", "group": "Captioning"},
    {"key": "more_detailed_caption", "title": "More Detailed Caption", "desc": "Generate a paragraph-level image description.",
     "tag": "<MORE_DETAILED_CAPTION>", "icon": "📝", "accent": "#f59e0b", "group": "Captioning"},
    {"key": "dense_region_caption", "title": "Dense Region Caption", "desc": "Describe multiple regions in detail.",
     "tag": "<DENSE_REGION_CAPTION>", "icon": "🧩", "accent": "#ec4899", "group": "Detection"},
    {"key": "ocr", "title": "OCR", "desc": "Extract text from the image.",
     "tag": "<OCR>", "icon": "🅰️", "accent": "#14b8a6", "group": "OCR"},
    {"key": "region_proposal", "title": "Region Proposal", "desc": "Generate region proposals in the image.",
     "tag": "<REGION_PROPOSAL>", "icon": "▦", "accent": "#f97316", "group": "Detection"},
    {"key": "ocr_region", "title": "OCR with Region", "desc": "Extract text and localize it with polygons.",
     "tag": "<OCR_WITH_REGION>", "icon": "🔎", "accent": "#38bdf8", "group": "OCR", "new": True},
    {"key": "phrase_grounding", "title": "Phrase Grounding", "desc": "Localize objects described by a caption you provide.",
     "tag": "<CAPTION_TO_PHRASE_GROUNDING>", "icon": "🔗", "accent": "#a3e635", "group": "Detection", "new": True},
    {"key": "open_vocab", "title": "Open Vocabulary Detection", "desc": "Detect arbitrary objects you name, not just fixed classes.",
     "tag": "<OPEN_VOCABULARY_DETECTION>", "icon": "🧭", "accent": "#f43f5e", "group": "Detection", "new": True},
    {"key": "combo", "title": "More Powerful Together", "desc": "Chain multiple capabilities for a full visual analysis report.",
     "tag": "COMBINE", "icon": "✨", "accent": "#a855f7", "group": "Advanced"},
]
CAP_BY_KEY = {c["key"]: c for c in CAPABILITIES}

# --------------------------------------------------------------------------------------
# SESSION STATE
# --------------------------------------------------------------------------------------
DEFAULTS = {
    "page": "Dashboard",
    "selected_task": "caption",
    "history": [],
    "images_processed": set(),
    "uploaded_image_bytes": None,
    "uploaded_image_name": None,
    "favorites": set(),
    "gen_max_tokens": 512,
    "gen_num_beams": 3,
    "batch_results": [],
    "accent_1": "#7c3aed",
    "accent_2": "#a855f7",
    "cap_search": "",
}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# Apply any custom accent color chosen in the sidebar (must run every render)
st.markdown(accent_override_css(st.session_state.accent_1, st.session_state.accent_2), unsafe_allow_html=True)


def log_history(task_title, image_name, summary, elapsed):
    st.session_state.history.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": task_title,
        "image": image_name,
        "summary": summary,
        "elapsed_s": round(elapsed, 2),
    })
    st.session_state.images_processed.add(image_name)


# --------------------------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------------------------
with st.sidebar:
    # ---- Brand header ---------------------------------------------------------
    render_html("""
        <div class="sb-brand">
            <div style="font-size:2rem;" class="floaty">👁️</div>
            <div>
                <div style="font-weight:800;font-size:1.1rem;color:#fff;line-height:1.2;">Vision AI Studio</div>
                <div style="font-size:0.72rem;color:#a78bfa;">Pro · Powered by Florence-2</div>
            </div>
            <div class="sb-version">v2.0</div>
        </div>
    """)

    # ---- Session snapshot -------------------------------------------------------
    total_runs = len(st.session_state.history)
    fav_count = len(st.session_state.favorites)
    imgs_done = len(st.session_state.images_processed)
    render_html(f"""
        <div class="sb-snapshot">
            <div class="sb-snap-item">
                <div class="sb-snap-value">{total_runs}</div>
                <div class="sb-snap-label">Runs</div>
            </div>
            <div class="sb-snap-divider"></div>
            <div class="sb-snap-item">
                <div class="sb-snap-value">{imgs_done}</div>
                <div class="sb-snap-label">Images</div>
            </div>
            <div class="sb-snap-divider"></div>
            <div class="sb-snap-item">
                <div class="sb-snap-value">{fav_count}</div>
                <div class="sb-snap-label">Favorites</div>
            </div>
        </div>
    """)

    # ---- Navigation -------------------------------------------------------------
    render_html('<div class="sb-heading"><span>🧭</span> NAVIGATION</div>')
    nav_badges = {
        "History": str(total_runs) if total_runs else None,
        "Batch Studio": str(len(st.session_state.batch_results)) if st.session_state.batch_results else None,
    }
    nav_items = [
        ("Dashboard", "🏠"), ("Vision Lab", "🔬"), ("Batch Studio", "📦"),
        ("Analytics", "📊"), ("History", "🕐"), ("System", "⚙️"),
    ]
    for label, icon in nav_items:
        is_active = st.session_state.page == label
        badge = nav_badges.get(label)
        btn_label = f"{icon}  {label}" + (f"   ·  {badge}" if badge else "")
        if st.button(btn_label, key=f"nav_{label}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = label
            st.rerun()

    divider()

    # ---- Current image preview ---------------------------------------------------
    if st.session_state.uploaded_image_bytes:
        render_html('<div class="sb-heading"><span>🖼️</span> CURRENT IMAGE</div>')
        render_html('<div class="sb-thumb-wrap">')
        st.image(st.session_state.uploaded_image_bytes, use_container_width=True)
        render_html(f'<div class="sb-thumb-name">{esc(st.session_state.uploaded_image_name)}</div>')
        render_html("</div>")
        if st.button("✕ Clear image", use_container_width=True, key="clear_img_sidebar"):
            st.session_state.uploaded_image_bytes = None
            st.session_state.uploaded_image_name = None
            st.rerun()
        divider()

    # ---- Model status -------------------------------------------------------------
    render_html('<div class="sb-heading"><span>🧠</span> MODEL</div>')
    render_html("""
        <div class="model-card">
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="font-size:1.3rem;">🟣</div>
                <div>
                    <div style="font-weight:700;color:#f3f4f6;font-size:0.9rem;">Florence-2-base</div>
                    <span class="badge-ready"><span class="badge-dot"></span> Ready</span>
                </div>
            </div>
            <div style="color:#9ca3af;font-size:0.75rem;margin-top:0.5rem;">Florence-2 Vision-Language Model</div>
        </div>
    """)

    with st.expander("⚡ Generation settings"):
        st.session_state.gen_max_tokens = st.slider("Max new tokens", 128, 1024, st.session_state.gen_max_tokens, 64)
        st.session_state.gen_num_beams = st.slider("Beam search width", 1, 6, st.session_state.gen_num_beams)
        st.caption("Higher beams = higher quality, slower inference.")

    with st.expander("🎨 Appearance"):
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.accent_1 = st.color_picker("Accent A", st.session_state.accent_1)
        with c2:
            st.session_state.accent_2 = st.color_picker("Accent B", st.session_state.accent_2)
        st.caption("Customize the studio's gradient accent color.")
        if st.button("↺ Reset to default", use_container_width=True, key="reset_accent"):
            st.session_state.accent_1 = DEFAULTS["accent_1"]
            st.session_state.accent_2 = DEFAULTS["accent_2"]
            st.rerun()

    divider()

    # ---- Quick actions --------------------------------------------------------
    render_html('<div class="sb-heading"><span>⚡</span> QUICK ACTIONS</div>')
    if st.button("⬆️  Upload Image", use_container_width=True):
        st.session_state.page = "Vision Lab"; st.rerun()
    if st.button("📦  Batch Studio", use_container_width=True):
        st.session_state.page = "Batch Studio"; st.rerun()
    if st.button("📖  Documentation", use_container_width=True):
        st.session_state.page = "System"; st.rerun()

    render_html("""
        <div class="gh-card" style="margin-top:1.2rem;">
            <div style="color:#facc15;font-size:0.85rem;font-weight:700;">⭐ Star this repo on GitHub</div>
            <div style="color:#9ca3af;font-size:0.75rem;margin-top:2px;">If you find this project useful!</div>
        </div>
    """)

    render_html('<div class="sb-footer">Vision AI Studio Pro · v2.0<br/>Session data only · resets on restart</div>')

# --------------------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------------------
def load_demo_gallery():
    items = []
    if os.path.isdir(DEMO_DIR):
        for fname in sorted(os.listdir(DEMO_DIR)):
            path = os.path.join(DEMO_DIR, fname)
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                items.append((fname, path))
    return items


def render_result(res, container):
    with container:
        if res["kind"] == "text":
            # Model-generated text can itself contain '<'/'&' (e.g. OCR reading a
            # literal "<STOP>" sign), so it must be escaped before going into HTML.
            render_html(f"""<div class="vcard" style="min-height:120px;">
                <div style="color:#e5e7eb;line-height:1.6;">{esc(res['text'])}</div></div>""")
        elif res["kind"] in ("boxes", "quad"):
            st.image(res["annotated_image"], use_container_width=True)
            n = len(res.get("bboxes", res.get("quad_boxes", [])))
            st.caption(f"{n} region(s) detected")


def skeleton_block(height=180):
    render_html(f'<div class="skeleton" style="height:{height}px;width:100%;"></div>')


# --------------------------------------------------------------------------------------
# PAGE: DASHBOARD
# --------------------------------------------------------------------------------------
def page_dashboard():
    col1, col2 = st.columns([3, 1])
    with col1:
        render_html('<div class="hero-badge">✨ Now with grounding, open-vocab detection &amp; batch mode</div>')
        render_html('<div class="hero-eyebrow">Welcome to</div>')
        render_html('<div class="hero-title">Vision AI Studio Pro</div>')
        render_html(
            '<div class="hero-sub">A multimodal computer vision laboratory powered by Florence-2. '
            "Explore, analyze, and extract insights from images using state-of-the-art AI — "
            "now with richer detection, grounding, batch processing, and analytics.</div>"
        )
        st.write("")
        b1, b2, _ = st.columns([1, 1, 2])
        with b1:
            if st.button("🚀 Launch Vision Lab", type="primary", use_container_width=True):
                st.session_state.page = "Vision Lab"; st.rerun()
        with b2:
            if st.button("📦 Try Batch Studio", use_container_width=True):
                st.session_state.page = "Batch Studio"; st.rerun()
    with col2:
        render_html('<div style="font-size:6rem;text-align:right;" class="floaty">👁️</div>')

    st.write("")
    total_analyses = len(st.session_state.history)
    images_processed = len(st.session_state.images_processed)
    avg_time = (sum(h["elapsed_s"] for h in st.session_state.history) / total_analyses) if total_analyses else 0

    import torch
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: stat_card("🟣", "#8b5cf6", "MODEL", "Florence-2-base", "Vision-Language Model")
    with c2: stat_card("🖥️", "#22c55e", "DEVICE", "GPU" if torch.cuda.is_available() else "CPU", "Inference Device")
    with c3: stat_card("📈", "#3b82f6", "TOTAL ANALYSES", str(total_analyses), "All Time",
                        trend=f"+{total_analyses}" if total_analyses else None)
    with c4: stat_card("🖼️", "#f97316", "IMAGES PROCESSED", str(images_processed), "All Time")
    with c5: stat_card("⏱️", "#14b8a6", "AVG. RUN TIME", f"{avg_time:.1f}s" if total_analyses else "—", "Per analysis")

    st.write(""); st.write("")
    h1, h2 = st.columns([5, 1])
    with h1:
        section_header("✨ Explore Vision Capabilities")
    with h2:
        render_html(f'<div style="text-align:right;padding-top:6px;">{pill(str(len(CAPABILITIES)) + " Capabilities")}</div>')

    st.session_state.cap_search = st.text_input(
        "🔎 Quick search", value=st.session_state.cap_search,
        placeholder="Search capabilities… e.g. 'ocr', 'grounding', 'caption'",
        label_visibility="collapsed",
    )

    def matches_search(cap):
        if not st.session_state.cap_search:
            return True
        q = st.session_state.cap_search.lower()
        return q in cap["title"].lower() or q in cap["desc"].lower() or q in cap["tag"].lower()

    tabs = st.tabs(["All", "⭐ Favorites", "Captioning", "Detection", "OCR", "Advanced"])
    groups = ["All", "Favorites", "Captioning", "Detection", "OCR", "Advanced"]
    for tab, group in zip(tabs, groups):
        with tab:
            if group == "All":
                caps = CAPABILITIES
            elif group == "Favorites":
                caps = [c for c in CAPABILITIES if c["key"] in st.session_state.favorites]
            else:
                caps = [c for c in CAPABILITIES if c["group"] == group]
            caps = [c for c in caps if matches_search(c)]

            if not caps:
                st.caption("No capabilities match yet — try a different search, or star a few as favorites." if group == "Favorites"
                            else "No capabilities match your search.")

            rows = [caps[i:i + 4] for i in range(0, len(caps), 4)]
            for row in rows:
                cols = st.columns(4)
                for col, cap in zip(cols, row):
                    with col:
                        capability_card_html(cap, is_new=cap.get("new", False),
                                              is_favorite=cap["key"] in st.session_state.favorites)
                        bc1, bc2 = st.columns([3, 1])
                        with bc1:
                            if st.button("Try it →", key=f"try_{group}_{cap['key']}", use_container_width=True):
                                st.session_state.selected_task = cap["key"]
                                st.session_state.page = "Vision Lab"
                                st.rerun()
                        with bc2:
                            starred = cap["key"] in st.session_state.favorites
                            if st.button("⭐" if not starred else "✩", key=f"fav_{group}_{cap['key']}", use_container_width=True):
                                if starred:
                                    st.session_state.favorites.discard(cap["key"])
                                else:
                                    st.session_state.favorites.add(cap["key"])
                                st.rerun()
                st.write("")

    divider()
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        render_html("""
            <div class="vcard">
                <div style="display:flex;gap:12px;align-items:flex-start;">
                    <div style="font-size:1.4rem;">🛡️</div>
                    <div>
                        <div style="font-weight:700;color:#f3f4f6;">Built for Experimentation &amp; Innovation</div>
                        <div style="color:#9ca3af;font-size:0.85rem;margin-top:2px;">
                            Vision AI Studio Pro is designed for researchers, developers, and AI enthusiasts
                            to experiment, learn, and build the future of computer vision.
                        </div>
                    </div>
                </div>
            </div>
        """)
    with fc2:
        recent = st.session_state.history[-1] if st.session_state.history else None
        activity_html = (f"Ran <b>{esc(recent['task'])}</b> on <i>{esc(recent['image'])}</i>" if recent
                          else "No analyses yet — try a capability above.")
        render_html(f"""
            <div class="vcard">
                <div style="font-weight:700;color:#f3f4f6;margin-bottom:6px;">🕐 Latest activity</div>
                <div style="color:#9ca3af;font-size:0.85rem;">{activity_html}</div>
            </div>
        """)


# --------------------------------------------------------------------------------------
# PAGE: VISION LAB
# --------------------------------------------------------------------------------------
def page_vision_lab():
    section_header("🔬 Vision Lab", "Upload an image, choose a capability, and run real Florence-2 inference.")

    left, right = st.columns([1, 1.35])

    with left:
        src_tab1, src_tab2 = st.tabs(["⬆️ Upload", "🖼️ Demo Gallery"])
        image = None
        with src_tab1:
            uploaded = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp", "bmp"], label_visibility="collapsed")
            if uploaded is not None:
                st.session_state.uploaded_image_bytes = uploaded.getvalue()
                st.session_state.uploaded_image_name = uploaded.name
        with src_tab2:
            demo_items = load_demo_gallery()
            if demo_items:
                cols = st.columns(len(demo_items))
                for col, (name, path) in zip(cols, demo_items):
                    with col:
                        st.image(path, use_container_width=True, caption=name.replace("_", " ").replace(".png", ""))
                        if st.button("Use", key=f"demo_{name}", use_container_width=True):
                            with open(path, "rb") as f:
                                st.session_state.uploaded_image_bytes = f.read()
                            st.session_state.uploaded_image_name = name
                            st.rerun()
            else:
                st.caption("No demo images bundled.")

        if st.session_state.uploaded_image_bytes:
            image = Image.open(io.BytesIO(st.session_state.uploaded_image_bytes)).convert("RGB")
            st.image(image, caption=st.session_state.uploaded_image_name, use_container_width=True)
        else:
            st.info("Upload an image or pick a demo image to get started.")

        render_html('<div style="font-weight:700;color:#f3f4f6;margin:0.8rem 0 0.5rem;">Choose a capability</div>')
        group_filter = st.radio("Filter", ["All", "Captioning", "Detection", "OCR", "Advanced"],
                                 horizontal=True, label_visibility="collapsed")
        visible_caps = CAPABILITIES if group_filter == "All" else [c for c in CAPABILITIES if c["group"] == group_filter]

        chip_cols = st.columns(3)
        for i, cap in enumerate(visible_caps):
            with chip_cols[i % 3]:
                selected = st.session_state.selected_task == cap["key"]
                label = f"{'✅ ' if selected else cap['icon'] + ' '}{cap['title']}"
                if st.button(label, key=f"chip_{cap['key']}", use_container_width=True):
                    st.session_state.selected_task = cap["key"]
                    st.rerun()

        chosen_cap = CAP_BY_KEY[st.session_state.selected_task]
        text_input = None
        needs_text = chosen_cap["key"] in ("phrase_grounding", "open_vocab")
        if needs_text:
            placeholder = "e.g. a red car and a stop sign" if chosen_cap["key"] == "open_vocab" else "e.g. a man riding a bicycle"
            text_input = st.text_input("Describe what to locate", placeholder=placeholder)

        run_clicked = st.button("▶ Run Analysis", type="primary", use_container_width=True,
                                 disabled=(image is None) or (needs_text and not text_input))

    with right:
        render_html('<div class="vcard" style="min-height:460px;">')
        render_html(f'<div style="font-weight:700;color:#f3f4f6;margin-bottom:0.8rem;">Results — {esc(chosen_cap["title"])}</div>')

        if run_clicked and image is not None:
            try:
                if chosen_cap["key"] != "combo":
                    placeholder = st.empty()
                    with placeholder.container():
                        st.caption(f"Running {chosen_cap['title']} with Florence-2…")
                        skeleton_block(220)
                    t0 = time.time()
                    res = execute_task(image, chosen_cap["key"], text_input=text_input,
                                        max_new_tokens=st.session_state.gen_max_tokens,
                                        num_beams=st.session_state.gen_num_beams)
                    elapsed = time.time() - t0
                    placeholder.empty()

                    tab_visual, tab_raw = st.tabs(["🖼️ Visual", "🧾 Raw JSON"])
                    with tab_visual:
                        render_result(res, st.container())
                        st.caption(f"⏱️ {elapsed:.1f}s · beams={st.session_state.gen_num_beams} · max_tokens={st.session_state.gen_max_tokens}")
                    with tab_raw:
                        st.json(res["raw"])

                    dl1, dl2 = st.columns(2)
                    with dl1:
                        st.download_button("⬇️ Download result (JSON)",
                                            data=json.dumps(res["raw"], indent=2),
                                            file_name=f"{chosen_cap['key']}_result.json",
                                            mime="application/json", use_container_width=True)
                    with dl2:
                        if res["kind"] in ("boxes", "quad"):
                            buf = io.BytesIO()
                            res["annotated_image"].save(buf, format="PNG")
                            st.download_button("⬇️ Download annotated image", data=buf.getvalue(),
                                                file_name=f"{chosen_cap['key']}_annotated.png",
                                                mime="image/png", use_container_width=True)

                    summary = res["text"][:120] + "…" if res["kind"] == "text" and len(res["text"]) > 120 else (
                        f"{len(res.get('bboxes', res.get('quad_boxes', [])))} regions" if res["kind"] != "text" else res["text"])
                    log_history(chosen_cap["title"], st.session_state.uploaded_image_name, summary, elapsed)
                    st.toast(f"{chosen_cap['title']} complete in {elapsed:.1f}s", icon="✅")

                else:
                    combo_keys = ["caption", "od", "ocr", "dense_region_caption"]
                    t0 = time.time()
                    prog = st.progress(0, text="Starting combined analysis…")
                    for i, key in enumerate(combo_keys):
                        cap = CAP_BY_KEY[key]
                        prog.progress(i / len(combo_keys), text=f"Running {cap['title']}…")
                        res = execute_task(image, key, max_new_tokens=st.session_state.gen_max_tokens,
                                            num_beams=st.session_state.gen_num_beams)
                        render_html(f"<b>{cap['icon']} {cap['title']}</b>")
                        render_result(res, st.container())
                        divider()
                    prog.progress(1.0, text="Done")
                    elapsed = time.time() - t0
                    log_history("Combined Analysis", st.session_state.uploaded_image_name,
                                f"Ran {len(combo_keys)} capabilities", elapsed)
                    st.toast("Combined analysis complete", icon="✨")
                    st.caption(f"Total time: {elapsed:.1f}s")

            except Exception as e:
                st.error(
                    "Inference failed — usually means Florence-2 couldn't be downloaded/loaded "
                    "(no internet, or missing `torch`/`transformers`/`timm`/`einops`).\n\n"
                    f"`{type(e).__name__}: {e}`"
                )
        else:
            render_html('<div style="color:#6b7280;padding:3rem 0;text-align:center;">'
                         "Results will appear here after you run an analysis.</div>")
        render_html("</div>")


# --------------------------------------------------------------------------------------
# PAGE: BATCH STUDIO
# --------------------------------------------------------------------------------------
def page_batch_studio():
    section_header("📦 Batch Studio", "Run one capability across many images at once.")

    files = st.file_uploader("Upload multiple images", type=["png", "jpg", "jpeg", "webp", "bmp"],
                              accept_multiple_files=True)
    text_caps = [c for c in CAPABILITIES if c["key"] != "combo"]
    label_to_key = {c["title"]: c["key"] for c in text_caps}
    chosen_label = st.selectbox("Capability to run on all images", list(label_to_key.keys()))
    chosen_key = label_to_key[chosen_label]
    needs_text = chosen_key in ("phrase_grounding", "open_vocab")
    text_input = st.text_input("Text prompt (required for grounding / open-vocab tasks)") if needs_text else None

    run_batch = st.button("▶ Run batch", type="primary", disabled=not files or (needs_text and not text_input))

    if run_batch and files:
        st.session_state.batch_results = []
        prog = st.progress(0, text="Starting batch…")
        for i, f in enumerate(files):
            img = Image.open(io.BytesIO(f.getvalue())).convert("RGB")
            prog.progress(i / len(files), text=f"Processing {f.name}…")
            try:
                t0 = time.time()
                res = execute_task(img, chosen_key, text_input=text_input,
                                    max_new_tokens=st.session_state.gen_max_tokens,
                                    num_beams=st.session_state.gen_num_beams)
                elapsed = time.time() - t0
                st.session_state.batch_results.append({"name": f.name, "image": img, "result": res, "elapsed": elapsed})
                log_history(CAP_BY_KEY[chosen_key]["title"], f.name,
                            res.get("text", f"{len(res.get('bboxes', []))} regions")[:100], elapsed)
            except Exception as e:
                st.session_state.batch_results.append({"name": f.name, "image": img, "error": str(e)})
        prog.progress(1.0, text="Batch complete")
        st.toast(f"Processed {len(files)} images", icon="✅")

    if st.session_state.batch_results:
        st.write("")
        render_html(f'<div style="font-weight:700;color:#f3f4f6;margin-bottom:0.6rem;">Results ({len(st.session_state.batch_results)})</div>')
        cols = st.columns(3)
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for i, item in enumerate(st.session_state.batch_results):
                with cols[i % 3]:
                    render_html('<div class="vcard">')
                    st.markdown(f"**{item['name']}**")
                    if "error" in item:
                        st.error(item["error"])
                    else:
                        res = item["result"]
                        if res["kind"] == "text":
                            st.image(item["image"], use_container_width=True)
                            st.caption(res["text"][:150])
                            zf.writestr(f"{item['name']}_result.json", json.dumps(res["raw"], indent=2))
                        else:
                            st.image(res["annotated_image"], use_container_width=True)
                            buf = io.BytesIO()
                            res["annotated_image"].save(buf, format="PNG")
                            zf.writestr(f"{item['name']}_annotated.png", buf.getvalue())
                        st.caption(f"⏱️ {item['elapsed']:.1f}s")
                    render_html("</div>")
        st.write("")
        st.download_button("⬇️ Download all results (.zip)", data=zip_buf.getvalue(),
                            file_name="batch_results.zip", mime="application/zip")


# --------------------------------------------------------------------------------------
# PAGE: ANALYTICS
# --------------------------------------------------------------------------------------
def page_analytics():
    section_header("📊 Analytics", "Usage insights from this session's runs.")
    if not st.session_state.history:
        st.info("No analyses yet. Run something in Vision Lab or Batch Studio to see analytics here.")
        return

    import pandas as pd
    df = pd.DataFrame(st.session_state.history)
    df["time"] = pd.to_datetime(df["time"])

    c1, c2, c3, c4 = st.columns(4)
    with c1: stat_card("📈", "#3b82f6", "TOTAL RUNS", str(len(df)), "All Time")
    with c2: stat_card("🖼️", "#f97316", "UNIQUE IMAGES", str(df["image"].nunique()), "All Time")
    with c3: stat_card("🏆", "#8b5cf6", "TOP CAPABILITY", df["task"].mode()[0], "Most used")
    with c4: stat_card("⏱️", "#14b8a6", "AVG. TIME", f"{df['elapsed_s'].mean():.1f}s", "Per run")

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        render_html('<div style="font-weight:700;color:#f3f4f6;margin-bottom:0.4rem;">Runs per capability</div>')
        st.bar_chart(df["task"].value_counts())
    with col2:
        render_html('<div style="font-weight:700;color:#f3f4f6;margin-bottom:0.4rem;">Runs over time</div>')
        timeline = df.set_index("time").resample("1min").size()
        st.line_chart(timeline if len(timeline) > 1 else df["task"].value_counts())

    st.write("")
    render_html('<div style="font-weight:700;color:#f3f4f6;margin-bottom:0.4rem;">Processing time per run</div>')
    st.area_chart(df["elapsed_s"])


# --------------------------------------------------------------------------------------
# PAGE: HISTORY
# --------------------------------------------------------------------------------------
def page_history():
    section_header("🕐 History", "Every analysis run in this session.")
    if not st.session_state.history:
        st.info("No analyses yet.")
        return

    import pandas as pd
    df = pd.DataFrame(st.session_state.history).iloc[::-1].reset_index(drop=True)

    search = st.text_input("🔎 Search by task or image name")
    if search:
        mask = df["task"].str.contains(search, case=False) | df["image"].str.contains(search, case=False, na=False)
        df = df[mask]

    st.dataframe(df, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Export history (CSV)", data=df.to_csv(index=False),
                            file_name="history.csv", mime="text/csv", use_container_width=True)
    with c2:
        if st.button("🗑️ Clear history", use_container_width=True):
            st.session_state.history = []
            st.session_state.images_processed = set()
            st.rerun()


# --------------------------------------------------------------------------------------
# PAGE: SYSTEM
# --------------------------------------------------------------------------------------
def page_system():
    section_header("⚙️ System", "Environment diagnostics and capability reference.")

    import torch, transformers
    c1, c2 = st.columns(2)
    with c1:
        render_html('<div class="vcard">')
        st.markdown("**Model**")
        st.write(f"- Native model id: `{NATIVE_MODEL_ID}`")
        st.write(f"- Device: `{'cuda' if torch.cuda.is_available() else 'cpu'}`")
        st.write(f"- Torch: `{torch.__version__}`")
        st.write(f"- Transformers: `{transformers.__version__}`")
        render_html("</div>")
    with c2:
        render_html('<div class="vcard">')
        st.markdown("**Environment**")
        st.write(f"- Python: `{platform.python_version()}`")
        st.write(f"- Platform: `{platform.system()} {platform.release()}`")
        st.write(f"- Streamlit: `{st.__version__}`")
        render_html("</div>")

    st.write("")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔌 Test model load"):
            with st.spinner("Loading Florence-2… this downloads the model on first run."):
                try:
                    load_model()
                    st.success(f"Model loaded successfully via **{backend_label()}** backend.")
                except Exception as e:
                    st.error(f"Failed to load model: {type(e).__name__}: {e}")
    with b2:
        if st.button("🧹 Clear model cache (force reload)"):
            st.cache_resource.clear()
            st.success("Cache cleared. The model will reload on the next inference call.")

    st.write("")
    st.markdown("**📖 Capability reference**")
    for cap in CAPABILITIES:
        if cap["key"] == "combo":
            continue
        st.markdown(f"- **{cap['title']}** `{cap['tag']}` — {cap['desc']}")
    st.markdown(
        f"""
> The first run of any capability downloads `{NATIVE_MODEL_ID}` (~460MB) from
> Hugging Face and caches it locally. Subsequent runs are fast. GPU is used automatically
> if `torch.cuda.is_available()`. If the installed `transformers` version is too old for
> the native Florence-2 integration, the app automatically falls back to the legacy
> `microsoft/Florence-2-base` + `trust_remote_code=True` path.
"""
    )


# --------------------------------------------------------------------------------------
# ROUTER
# --------------------------------------------------------------------------------------
PAGES = {
    "Dashboard": page_dashboard,
    "Vision Lab": page_vision_lab,
    "Batch Studio": page_batch_studio,
    "Analytics": page_analytics,
    "History": page_history,
    "System": page_system,
}
PAGES[st.session_state.page]()
