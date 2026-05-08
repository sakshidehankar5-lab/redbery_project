"""
IDEP — Streamlit Frontend
Document Upload & Extraction Preview
"""
import json
import os
import time

import requests
import streamlit as st
from pathlib import Path

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1 = f"{API_BASE}/api/v1"

# ─────────────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IDEP — Intelligent Document Extraction",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3 { font-family: 'Space Mono', monospace; }

    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .main-header h1 { font-size: 1.8rem; margin: 0; color: #fff; }
    .main-header p  { color: #ccc; margin: 0.3rem 0 0; font-size: 0.9rem; }

    .field-card {
        background: #1e1e2e;
        border: 1px solid #3a3a5c;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.4rem 0;
        display: flex;
        justify-content: space-between;
    }
    .field-name  { color: #a6adc8; font-size: 0.8rem; font-family: 'Space Mono'; }
    .field-value { color: #cdd6f4; font-size: 0.95rem; font-weight: 500; }

    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'Space Mono', monospace;
    }
    .status-completed { background: #1e4d2b; color: #69ff85; }
    .status-failed    { background: #4d1e1e; color: #ff6969; }
    .status-pending   { background: #3b3b1e; color: #ffee69; }

    .metric-box {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-label { color: #585b70; font-size: 0.75rem; font-family: 'Space Mono'; }
    .metric-value { color: #cba6f7; font-size: 1.5rem; font-weight: 700; margin-top: 4px; }

    [data-testid="stSidebar"] { background: #181825; }
    .stButton > button {
        background: linear-gradient(135deg, #cba6f7, #89b4fa);
        color: #1e1e2e;
        border: none;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        width: 100%;
    }
    .stButton > button:hover { opacity: 0.88; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def fetch_templates():
    try:
        r = requests.get(f"{API_V1}/templates", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def upload_document(file_bytes, filename, content_type, doc_type, custom_fields):
    try:
        files = {"file": (filename, file_bytes, content_type)}
        data = {"document_type": doc_type}
        if custom_fields:
            data["custom_fields"] = ",".join(custom_fields)
        r = requests.post(f"{API_V1}/documents/upload", files=files, data=data, timeout=120)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error_code": "CONNECTION_ERROR", "message": "Cannot connect to API. Is the server running?"}, 503
    except Exception as e:
        return {"error_code": "CLIENT_ERROR", "message": str(e)}, 500


def fetch_documents():
    try:
        r = requests.get(f"{API_V1}/documents", timeout=5)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def status_badge(status: str) -> str:
    css = f"status-{status}"
    return f'<span class="status-badge {css}">{status.upper()}</span>'


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Settings")

    templates = fetch_templates()
    type_options = ["auto"] + [t["document_type"] for t in templates]
    type_labels = {"auto": "🔍 Auto-detect"} | {
        t["document_type"]: f"📋 {t['display_name']}" for t in templates
    }

    selected_type = st.selectbox(
        "Document Type",
        options=type_options,
        format_func=lambda x: type_labels.get(x, x),
        help="'Auto-detect' uses OCR + heuristics to determine document type.",
    )

    custom_fields = []
    if selected_type != "auto":
        selected_template = next((t for t in templates if t["document_type"] == selected_type), None)
        if selected_template:
            all_fields = [f["name"] for f in selected_template["fields"]]
            custom_fields = st.multiselect(
                "Fields to Extract",
                options=all_fields,
                default=all_fields,
                help="Deselect fields you don't need.",
            )

    st.divider()
    st.markdown("**API Status**")
    try:
        health = requests.get(f"{API_BASE}/api/v1/health", timeout=3).json()
        st.success(f"✅ API Online — v{health.get('version', '?')}")
    except Exception:
        st.error("❌ API Offline")

    st.divider()
    st.caption("IDEP · Intelligent Document Extraction Platform")


# ─────────────────────────────────────────────────────────────────────────────
# Main Layout
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
  <h1>📄 Intelligent Document Extraction Platform</h1>
  <p>Upload Aadhaar · Driving Licence · Passport · Invoice — get structured data instantly</p>
</div>
""", unsafe_allow_html=True)

tab_upload, tab_history, tab_templates = st.tabs(["📤 Upload & Extract", "📜 History", "🗂 Templates"])


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Upload
# ─────────────────────────────────────────────────────────────────────────────

with tab_upload:
    col_upload, col_result = st.columns([1, 1.4], gap="large")

    with col_upload:
        st.markdown("### Upload Document")
        uploaded = st.file_uploader(
            "Drag & drop or click to upload",
            type=["pdf", "png", "jpg", "jpeg", "tiff"],
            help="Max 10MB. Supported: PDF, PNG, JPG, JPEG, TIFF",
        )

        if uploaded:
            if uploaded.type.startswith("image"):
                st.image(uploaded, caption=uploaded.name, use_column_width=True)
            else:
                st.info(f"📁 {uploaded.name} ({uploaded.size / 1024:.1f} KB)")

        extract_btn = st.button("🔍 Extract Data", disabled=uploaded is None)

    with col_result:
        st.markdown("### Extraction Result")

        if "result" not in st.session_state:
            st.info("Upload a document and click **Extract Data** to see results here.")

        if extract_btn and uploaded:
            with st.spinner("Running OCR + LLM extraction..."):
                t0 = time.time()
                result, status_code = upload_document(
                    file_bytes=uploaded.read(),
                    filename=uploaded.name,
                    content_type=uploaded.type,
                    doc_type=selected_type,
                    custom_fields=custom_fields if custom_fields else None,
                )
                elapsed = time.time() - t0

            st.session_state.result = result
            st.session_state.status_code = status_code

        if "result" in st.session_state:
            result = st.session_state.result
            sc = st.session_state.status_code

            if sc >= 400:
                st.error(f"❌ {result.get('message', 'Extraction failed')}")
                if result.get("details"):
                    st.json(result["details"])
            else:
                # Metrics row
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f"""
                    <div class="metric-box">
                      <div class="metric-label">DOC TYPE</div>
                      <div class="metric-value" style="font-size:1rem;">{result.get('document_type','?').replace('_',' ').title()}</div>
                    </div>""", unsafe_allow_html=True)
                with m2:
                    conf = result.get('classification_confidence', 0)
                    st.markdown(f"""
                    <div class="metric-box">
                      <div class="metric-label">CONFIDENCE</div>
                      <div class="metric-value">{conf:.0%}</div>
                    </div>""", unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""
                    <div class="metric-box">
                      <div class="metric-label">PAGES</div>
                      <div class="metric-value">{result.get('ocr_pages', 1)}</div>
                    </div>""", unsafe_allow_html=True)
                with m4:
                    ms = result.get('processing_time_ms', 0)
                    st.markdown(f"""
                    <div class="metric-box">
                      <div class="metric-label">TIME</div>
                      <div class="metric-value">{ms/1000:.1f}s</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <p style="margin:0.8rem 0 0.2rem;">
                  Status: {status_badge(result.get('status','?'))} &nbsp;|&nbsp;
                  Model: <code>{result.get('llm_model','?')}</code>
                </p>
                """, unsafe_allow_html=True)

                st.divider()

                # Extracted fields
                fields = result.get("extracted_fields") or {}
                if fields:
                    st.markdown("**Extracted Fields**")
                    for key, val in fields.items():
                        if val is None:
                            continue
                        display_val = json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else str(val)
                        st.markdown(f"""
                        <div class="field-card">
                          <span class="field-name">{key.replace('_',' ').upper()}</span>
                          <span class="field-value">{display_val}</span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.warning("No fields extracted.")

                # Raw JSON toggle
                with st.expander("🔧 Raw JSON Response"):
                    st.json(result)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — History
# ─────────────────────────────────────────────────────────────────────────────

with tab_history:
    st.markdown("### Processed Documents")
    if st.button("🔄 Refresh"):
        st.rerun()

    docs = fetch_documents()
    if not docs:
        st.info("No documents processed yet.")
    else:
        for doc in docs:
            with st.expander(f"📄 {doc['original_filename']}  —  {doc['document_type'].replace('_',' ').title()}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Doc Type", doc['document_type'].replace('_', ' ').title())
                c2.metric("File Size", f"{doc['file_size_bytes']/1024:.1f} KB")
                c3.metric("ID", str(doc['id'])[:8] + "...")
                st.caption(f"Uploaded: {doc['created_at']}")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 — Templates
# ─────────────────────────────────────────────────────────────────────────────

with tab_templates:
    st.markdown("### Extraction Templates")
    if not templates:
        st.warning("Could not load templates from API.")
    else:
        for tmpl in templates:
            with st.expander(f"📋 {tmpl['display_name']}"):
                req_fields = [f for f in tmpl["fields"] if f["required"]]
                opt_fields = [f for f in tmpl["fields"] if not f["required"]]

                st.markdown("**Required Fields**")
                for f in req_fields:
                    st.markdown(f"- `{f['name']}` — {f['description']}" + (f" *(e.g. {f['example']})*" if f.get("example") else ""))

                if opt_fields:
                    st.markdown("**Optional Fields**")
                    for f in opt_fields:
                        st.markdown(f"- `{f['name']}` — {f['description']}" + (f" *(e.g. {f['example']})*" if f.get("example") else ""))
