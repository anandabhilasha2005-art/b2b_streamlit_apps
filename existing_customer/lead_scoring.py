import pandas as pd
import re, html, os, time
from typing import List, Dict
import streamlit as st
import streamlit.components.v1 as components
from data_ingestion import DataEngineerApp
import datetime

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "files"
ACCOUNT_SUMMARY_PATH   = FILES_DIR / "account_summary.xlsx"
RECOMMENDATIONS_PATH   = FILES_DIR / "recommendations.xlsx"


# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Prioritization & Product Recommendation Studio",
    layout="wide",
)

# --------------------------------------------------
# CSS (Combined from both files)
# --------------------------------------------------
st.markdown(
    """
<style>
/* ===== PAGE HEADER ===== */
.page-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 4px;
}
.page-desc {
    color: #555;
    font-size: 0.95rem;
    margin-bottom: 20px;
}

/* ===== AGENT LOG BOX ===== */
.agent-log-box {
    background: #faf4ff;
    border-radius: 8px;
    border: 1px dashed #d7c6ff;
    padding: 12px 14px;
    font-size: 13px;
    color: #3b2a6f;
    margin-bottom: 16px;
}
.agent-log-line { margin-bottom: 4px; }

.agent-log-line.title {
    font-weight: 700;
    color: #6b00b8;
    margin-bottom: 6px;
}

.step-label { color: #6b00b8; font-weight: 700; }
.agent-log-line.info { color: #4a3b8f; }
.agent-log-line.success { color: #1b7f3b; }
.agent-log-line.source-tag {
    display: inline-block;
    background: #ede9fe;
    border: 1px solid #c4b5fd;
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 11px;
    color: #6b21a8;
    margin-left: 6px;
    font-weight: 600;
}
.agent-log-empty { color: #999; font-style: italic; }

/* ===== TASK CARD ===== */
.task-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 20px;
    background-color: #ffffff;
    box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05);
    padding: 15px;
}
.task-card-header { display: flex; align-items: center; margin-bottom: 10px; }
.task-name {
    font-weight: 600;
    font-size: 1.05rem;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 6px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    border-right: 1px solid #e6e6e6;
    width: 400px !important;
    min-width: 400px !important;
}
[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 1.2rem 1rem 1rem 1rem;
    background: linear-gradient(to bottom, #f7f7f9 0%, #f7f7f9 60%, #f1f1f4 60%, #f1f1f4 100%);
}
.sidebar-header { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
.sidebar-logo-img {
    width: 44px; height: 44px; border-radius: 12px; background: #fff;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.sidebar-logo-img img { width: 32px; height: auto; }
.sidebar-title-block { display: flex; flex-direction: column; font-weight: 800; color: #18181b; }
.sidebar-title-block span { font-size: 1.5rem !important; font-weight: 800 !important; color: #18181b !important; line-height: 1.2; letter-spacing: -0.3px; }
.scope-title { color: #6b00b8; font-weight: 700; font-size: 0.9rem; }

.sidebar-user-inline { display: flex; align-items: center; gap: 8px; padding-top: 6px; }
.sidebar-user-avatar-inline {
    width: 32px; height: 32px; border-radius: 50%; background: #f3ecff;
    border: 1px solid #d3c3ff; display: flex; align-items: center; justify-content: center;
    font-size: 18px; color: #8b6cff;
}
.sidebar-user-name-inline { font-weight: 600; color: #6b00b8; font-size: 0.9rem; }
.sidebar-user-name-inline span { font-weight: 700; }
.sidebar-user-role-inline { color: #666; font-size: 0.85rem; margin-top: 2px; }

.sidebar-logout-wrapper { width: 100%; display: flex; justify-content: center; margin-top: 10px; }
.sidebar-logout-wrapper button { min-width: 120px; }
.stButton > button { white-space: nowrap !important; }

/* ===== FILE UPLOADER ===== */
div[data-testid="stFileUploader"] > label { color: #6b00b8 !important; font-weight: 600 !important; }
div[data-testid="stFileUploader"] { background: #fff; border: 1px solid #dcdcdc; border-radius: 10px; padding: 10px 12px 14px; }
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] { border: none !important; background: transparent !important; padding: 6px !important; }
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] span { font-size: 0.9rem !important; }
div[data-testid="stFileUploader"] button { background-color: #6b00b8 !important; color: white !important; border-radius: 8px !important; padding: 6px 14px !important; border: none !important; }
div[data-testid="stFileUploader"] button:hover { background-color: #54008f !important; }

/* Progress bar */
progress.progress-inline {
    width: 100%;
    height: 8px;
    border-radius: 4px;
    border: none;
    background: #f3f4f6;
}
progress.progress-inline::-webkit-progress-bar {
    background: #f3f4f6;
    border-radius: 4px;
}
progress.progress-inline::-webkit-progress-value {
    background: #6b00b8;
    border-radius: 4px;
}
progress.progress-inline::-moz-progress-bar {
    background: #6b00b8;
    border-radius: 4px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
/* Output Box Styling */
.output-box {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 12px;
    margin-top: 10px;
    border: 1px solid #eef0f2;
}
.output-box ul {
    margin-top: 5px;
    margin-bottom: 0;
    padding-left: 20px;
}
.output-box li {
    margin-bottom: 4px;
    font-size: 13px;
    color: #4b5563;
}

.kv .label {
    font-weight: 700;
    font-size: 1.05rem;
    color: #1f2937;
    display: block;
    margin-bottom: 5px;
}
.small-muted {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 10px;
}

/* ===== PRIORITIZATION TABLE ===== */
.prioritization-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    line-height: 1.4;
    color: #374151;
    min-width: 1400px;
}

.prioritization-table thead th {
    background-color: #f9fafb;
    color: #4b5563;
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 2px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 10;
}

.prioritization-table tbody tr {
    border-bottom: 1px solid #f3f4f6;
    transition: background-color 0.15s ease;
}

.prioritization-table tbody tr:hover {
    background-color: #f9fafb;
}

.prioritization-table tbody td {
    padding: 12px 16px;
    vertical-align: top;
}

.prioritization-table .col-idx {
    width: 20px;
    font-size: 12px;
    color: #9ca3af;
    padding-right: 0;
}

.prioritization-table .col-priority {
    width: 80px;
}

.priority-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1;
}

.priority-high {
    background-color: #d1fae5;
    color: #065f46;
    border: 1px solid #34d399;
}
.priority-medium {
    background-color: #fffbeb;
    color: #92400e;
    border: 1px solid #fcd34d;
}
.priority-low {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #f87171;
}

.prioritization-table .col-rationale {
    min-width: 300px;
}

.scrollable-table-wrapper {
    overflow-x: auto;
    max-height: 500px;
    overflow-y: auto;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-top: 10px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
/* ===== CAPABILITY CHIPS ===== */
.cap-chip {
    display: inline-block; padding: 4px 10px; border-radius: 999px;
    font-size: 11px; font-weight: 600;
    background: linear-gradient(135deg, #eef2ff, #e0e7ff);
    color: #4338ca; border: 1px solid #c7d2fe;
    margin: 3px 5px 3px 0; white-space: nowrap;
}

/* ===== PRODUCT CARDS ===== */
.product-card {
    border: 2px solid #e5e7eb; border-radius: 14px; padding: 16px;
    background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    height: 360px; min-height: 360px; max-height: 360px;
    display: flex; flex-direction: column;
    transition: all 0.3s ease; position: relative; overflow: hidden; margin-bottom: 18px;
}
.product-card::before {
    content:''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    transform: scaleX(0); transition: transform 0.3s ease;
}
.product-card:hover::before { transform: scaleX(1); }
.product-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(102,126,234,0.15); border-color: #667eea; }

.card-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }

.card-icon {
    width: 40px; height: 40px; border-radius: 10px;
    background: #f0f0f5;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
}
.card-title-section { flex: 1; min-width: 0; }
.product-title { font-weight: 700; font-size: 0.92rem; color: #111827; line-height: 1.3; margin-bottom: 6px; }
.product-meta { display: flex; gap: 6px; flex-wrap: wrap; }
.meta-line-compact {
    font-size: 10.5px;
    color: #6b7280;
    margin-bottom: 3px;
    line-height: 1.5;
}

.meta-line-compact strong {
    font-weight: 600;
    color: #374151;
    margin-right: 4px;
}
.product-desc { font-size: 0.8rem; color: #6b7280; line-height: 1.4; margin-bottom: 10px; font-style: italic; }
.product-benefits { font-size: 0.8rem; color: #4b5563; line-height: 1.5; margin-bottom: 10px; flex: 1; overflow-y: auto; }
.product-benefits ul { margin: 0; padding-left: 16px; }
.product-benefits li { margin-bottom: 4px; }
.product-link { display: inline-flex; align-items: center; gap: 5px; font-size: 0.75rem; color: #667eea; text-decoration: none; font-weight: 600; margin-bottom: 10px; transition: all 0.2s ease; }
.product-link:hover { color: #764ba2; gap: 7px; }
.product-footer { margin-top: auto; padding-top: 10px; border-top: 1px dashed #e5e7eb; display: flex; flex-wrap: wrap; gap: 5px; }

</style>
""",
    unsafe_allow_html=True,
)

st.markdown("""
<style>
/* ===== UNIFIED TABLE SYSTEM ===== */
:root {
  --table-font: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --table-bg: #ffffff;
  --table-border: #e2e8f0;
  --header-bg: #f9fafb;
  --header-text: #64748b;
  --row-alt: #f8fafc;
  --row-hover: #f5f3ff;
  --accent: #7c3aed;
  --text: #0f172a;
  --muted: #64748b;
}

/* Table Container */
.unified-table-card {
  background: var(--table-bg);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  overflow: hidden;
  border: 1px solid var(--table-border);
  font-family: var(--table-font);
}

.unified-table-wrap {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 600px;
}

/* Scrollbar Styling */
.unified-table-wrap::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}
.unified-table-wrap::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 10px;
}
.unified-table-wrap::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
  border: 2px solid #f1f5f9;
}
.unified-table-wrap::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Base Table */
.unified-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  background: white;
  min-width: 1200px;
}

/* Sticky Header */
.unified-table thead th {
  position: sticky;
  top: 0;
  background: var(--header-bg);
  padding: 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 800;
  color: var(--header-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #edf2f7;
  z-index: 10;
}

/* Table Rows */
.unified-table tbody tr {
  border-bottom: 1px solid #edf2f7;
  border-left: 4px solid transparent;
}
.unified-table tbody tr:nth-child(even) {
  background-color: var(--row-alt);
}
.unified-table tbody tr:hover {
  background-color: var(--row-hover) !important;
  border-left: 4px solid var(--accent);
}

/* Table Cells */
.unified-table td {
  padding: 18px 16px;
  vertical-align: middle;
  color: var(--text);
  font-size: 12px;
  line-height: 1.5;
}

/* Company Name - Consistent */
.company-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  display: block;
  margin-bottom: 6px;
  line-height: 1.3;
}

/* Priority Pills */
.priority-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 11px;
  border: 1px solid;
  white-space: nowrap;
}
.p-high { background: #dcfce7; color: #15803d; border-color: #86efac; }
.p-medium { background: #fef3c7; color: #d97706; border-color: #fbbf24; }
.p-low { background: #fee2e2; color: #dc2626; border-color: #fca5a5; }

/* Tags & Pills */
.tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  background: #dbeafe;
  color: #1e40af;
  white-space: nowrap;
  margin: 0 4px 4px 0;
}

.pill {
  display: inline-flex;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  border: 1px solid;
  white-space: nowrap;
  margin: 0 4px 4px 0;
}
.pill-amber { background: #fef3c7; color: #d97706; border-color: #fbbf24; }
.pill-green { background: #dcfce7; color: #15803d; border-color: #86efac; }

/* Text Styles */
.muted {
  font-size: 12px;
  color: var(--muted);
  line-height: 1.6;
}

.cell-score strong {
  font-weight: 700;
  color: #0f172a;
}

.cell-explain {
  margin-top: 4px;
  color: #475569;
  font-size: 12px;
}

/* Expandable Details */
.trigger-details {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  margin-top: 8px;
}
.trigger-summary {
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
}
.trigger-summary::-webkit-details-marker { display: none; }
.trigger-summary::before {
  content: '→';
  margin-right: 8px;
  color: #a855f7;
  transition: 0.2s;
}
.trigger-details[open] .trigger-summary::before {
  transform: rotate(90deg);
}
.trigger-details[open] .trigger-summary {
  border-bottom: 1px solid #f1f5f9;
}
.trigger-content {
  padding: 12px;
  font-size: 12px;
  color: #334155;
  line-height: 1.5;
  background: #fafafa;
  border-radius: 0 0 8px 8px;
}
</style>
""", unsafe_allow_html=True)

GLOBAL_IFRAME_TABLE_CSS = """
<style>
/* ===== UNIFIED TABLE SYSTEM (iframe-safe) ===== */
:root {
  --table-font: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --table-bg: #ffffff;
  --table-border: #e2e8f0;
  --header-bg: #f9fafb;
  --header-text: #64748b;
  --row-alt: #f8fafc;
  --row-hover: #f5f3ff;
  --accent: #7c3aed;
  --text: #0f172a;
  --muted: #64748b;
}

/* Container */
.unified-table-card {
  background: var(--table-bg);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--table-border);
  font-family: var(--table-font);
}

/* Scroll wrapper */
.unified-table-wrap {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 600px;
}

/* Base table */
.unified-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  background: white;
  min-width: 1200px;
}

/* Sticky header */
.unified-table thead th {
  position: sticky;
  top: 0;
  background: var(--header-bg);
  padding: 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 800;
  color: var(--header-text);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #edf2f7;
  z-index: 10;
}

/* Rows */
.unified-table tbody tr {
  border-bottom: 1px solid #edf2f7;
  border-left: 4px solid transparent;
}
.unified-table tbody tr:nth-child(even) { background-color: var(--row-alt); }
.unified-table tbody tr:hover {
  background-color: var(--row-hover) !important;
  border-left: 4px solid var(--accent);
}

/* Cells */
.unified-table td {
  padding: 18px 16px;
  vertical-align: middle;
  color: var(--text);
  font-size: 12px;
  line-height: 1.5;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

/* Text helpers */
.company-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  display: block;
  margin-bottom: 6px;
  line-height: 1.3;
}
.muted {
  font-size: 12px;
  color: var(--muted);
  line-height: 1.6;
}

/* Pills/tags used in Account Summary */
.tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  background: #dbeafe;
  color: #1e40af;
  white-space: nowrap;
  margin: 0 4px 4px 0;
}

.pill {
  display: inline-flex;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  border: 1px solid;
  white-space: nowrap;
  margin: 0 4px 4px 0;
}
.pill-amber { background: #fef3c7; color: #d97706; border-color: #fbbf24; }
.pill-green { background: #dcfce7; color: #15803d; border-color: #86efac; }
</style>
"""

st.markdown("""
<style>
/* ===== ENHANCED TABS - REDUCED TOP SPACING ===== */
.stTabs {
    margin-top: -20px;  /* Pull tabs up closer to sidebar */
}

.stTabs [data-baseweb="tab-list"] {
    gap: 16px;
    padding: 0;
    margin-bottom: 16px;
    border-bottom: 2px solid #e5e7eb;
}

.stTabs [data-baseweb="tab"] {
    height: 42px;
    padding: 0 20px;
    background-color: transparent;
    border-radius: 6px 6px 0 0;
    font-size: 14.5px;
    font-weight: 600;
    color: #6b7280;
    border: none;
    border-bottom: 3px solid transparent;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #374151;
    background-color: #f9fafb;
    border-bottom: 3px solid #d1d5db;
}

.stTabs [aria-selected="true"] {
    color: #1f2937 !important;
    background-color: #fafafa !important;
    border-bottom: 3px solid #6b00b8 !important;
    font-weight: 700;
}

/* ===== PAGE HEADER - TIGHTER SPACING ===== */
.page-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 8px;
    margin-top: 8px;  /* Reduced even more */
    color: #1f2937;
}
.page-desc {
    color: #6b7280;
    font-size: 0.9rem;
    margin-bottom: 14px;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== REMOVE TOP WHITESPACE ABOVE TABS ===== */

/* Main app container */
.block-container {
    padding-top: 0.5rem !important;
}

/* Tabs wrapper */
.stTabs {
    margin-top: -30px !important;
}

/* Extra spacer div Streamlit injects */
.stTabs > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Tab list itself */
.stTabs [data-baseweb="tab-list"] {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-logo-img">
                <img src="https://cdn.brandfetch.io/idT9xYxvm0/theme/dark/logo.svg?c=1dxbfHSJFAPEGdCLU4o5B">
            </div>
            <div class="sidebar-title-block"><span>Agentic Lead Intelligence</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='scope-title'>Enter Input</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload data file", type=["xlsx","xls","csv"], key="data_file_uploader")
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith((".xlsx",".xls")):
                st.session_state["uploaded_df"] = pd.read_excel(uploaded_file, sheet_name="Customer360")
            else:
                st.session_state["uploaded_df"] = pd.read_csv(uploaded_file)
        except Exception as e:
            st.warning(f"Could not read uploaded file: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.text_input("Company Name", key="company_input",  value="IronBuild Infrastructure", placeholder="Type company name")

    st.markdown("<div style='flex:1 1 auto; min-height:40px;'></div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("""
        <div class="sidebar-user-inline">
            <div class="sidebar-user-avatar-inline">👤</div>
            <div class="sidebar-user-text-inline">
                <div class="sidebar-user-name-inline">Signed in as: <span>Sarah Jones</span></div>
                <div class="sidebar-user-role-inline">Role: Data Science Team</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-logout-wrapper'>", unsafe_allow_html=True)
    if st.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)




# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def status_dot(color="#ccc", size=12):
    return (f"<span style='display:inline-block;width:{size}px;height:{size}px;"
            f"border-radius:50%;background:{color};margin-right:8px;'></span>")

SIMULATE_TIME_PER_STEP = 0.55


# --------------------------------------------------
# STATE INITIALIZATION
# --------------------------------------------------
st.session_state.setdefault("run_process", False)
st.session_state.setdefault("stop_process", False)
st.session_state.setdefault("step_done", {})
st.session_state.setdefault("log_html", {})

# Business context default
default_context = (
    "We aim to strengthen our mid-market presence across the U.S. for Dedicated Fiber, Internet, "
    "Communication, and Security offerings. While coverage is strong, identifying accounts with the highest "
    "growth potential or urgent connectivity needs remains a challenge.\n\n"
    "As a result, sales teams lack actionable insights to prioritize and position the right products.\n\n"
    "Our goal is to enhance targeting, segmentation, and sales intelligence to deepen market penetration, "
    "accelerate revenue growth, and align execution with rising digital and connectivity demands."
)
if "business_context_text" not in st.session_state:
    st.session_state.business_context_text = default_context

# Mock prioritization dataframe
if "lead_prioritization_df" not in st.session_state:
    
    mock_data = {
    "Account ID": ['ACC001', 'ACC002', 'ACC003', 'ACC004', 'ACC005', 'ACC006', 'ACC007', 'ACC008', 'ACC009', 'ACC010'],
    "Company Name": [
        "IronBuild Infrastructure Pty Ltd",
        "BlueHarbor Logistics",
        "SouthernGrid Energy Services",
        "ApexHealth Clinics Group",
        "HorizonAgri Advisory",
        "NovaTech Industrial Manufacturing",
        "CoastalBuild Projects",
        "MetroServe Financial Advisory",
        "TerraLink Mining Services",
        "EduCore Learning Services",
    ],
    "Priority": ["🟢 High", "🟡 Medium", "🟢 High", "🟡 Medium", "🔴 Low", "🟢 High", "🟡 Medium", "🟡 Medium", "🟢 High", "🔴 Low"],
    "Growth Signals": [
        "⭐ High — Infra expansion + partnerships; 12% YoY growth",
        "🟡 Medium — Stable ops; 4% YoY growth",
        "⭐ Very High — Acquisition-led APAC expansion; 16% YoY",
        "🟡 Medium — Healthcare expansion; 8% YoY growth",
        "⚪ Low — Flat growth (2%); cost pressures",
        "⭐ Very High — M&A + automation; 19% YoY growth",
        "🟡 Medium — Project-driven growth; 6% YoY",
        "🟡 Medium — Steady services growth; 5% YoY",
        "⭐ High — Fleet expansion + IoT; 11% YoY growth",
        "⚪ Low — Minimal growth; 1% YoY",
    ],
    "Tech Maturity": [
        "⭐ High — Enterprise networking, cloud (AWS/Azure), security & analytics",
        "🟡 Developing — SaaS-first with basic cloud & SMB networking",
        "⭐ Advanced — Enterprise systems, private cloud, SIEM, carrier-grade connectivity",
        "⭐ High — Healthcare tech with collaboration & compliance focus",
        "⚪ Basic — Productivity tools with standard broadband",
        "⭐ Advanced — Global multi-cloud, ERP, data/AI, DevOps automation",
        "🟡 Developing — Project SaaS with temporary site connectivity",
        "🟡 Developing — Client SaaS with moderate infra complexity",
        "⭐ High — IoT, analytics, wireless backhaul for operations",
        "⚪ Low — Basic digital tools for online delivery",
    ],
    "Tech Relevancy": [
        "🟡 Medium — Upsell via Ethernet, security, bandwidth scaling",
        "🟡 Medium — SD-WAN, secure internet, scalable connectivity",
        "🟡 Medium — Security & network optimization upsell",
        "🟡 Medium — Backup links, traffic prioritization, security",
        "⚪ Low — Basic connectivity relevance only",
        "🟡 Medium — Global interconnect & managed services",
        "🟡 Medium — Rapid deployment & flexible bandwidth",
        "🟡 Medium — QoS, performance, secure access",
        "🟡 Medium — IoT scale-out & coverage expansion",
        "⚪ Low — Entry-level connectivity only",
    ],
    "Product History & Usage": [
        "⭐ High — Long tenure, multi-product, strong renewal growth",
        "🟡 Medium — Limited products, stable TCV, selective upsell",
        "⭐ High — Deep adoption, strong TCV, multiple renewals",
        "🟡 Medium — Multi-product, healthy TCV, moderate expansion",
        "⚪ Low — Single product, flat TCV, minimal expansion",
        "⭐ High — Strategic account, broad adoption, strong renewal growth",
        "🟡 Medium — Growing usage, improving TCV, limited renewal depth",
        "🟡 Medium — Stable tenure, selective adoption, modest growth",
        "⭐ High — Diversified products, strong TCV, frequent renewals",
        "⚪ Low — New account, low usage, no expansion",
    ],
    "Est. Potential Spend": [
        "Very High — Large infra player; high network & service expansion potential",
        "Medium — Stable regional; moderate connectivity & SD-WAN growth",
        "Very High — Critical utility; strategic long-term telco & security account",
        "High — Multi-site healthcare; strong fit for UCaaS & managed services",
        "Low — Small advisory; minimal ICT demand, low-touch sales",
        "Very High — Global manufacturing; flagship enterprise transformation account",
        "Medium — Project-driven; short-term connectivity & service needs",
        "Medium — Professional services; stable collaboration & connectivity needs",
        "High — Mining services; IoT, resilient networks & managed services opportunity",
        "Very Low — Small education; limited ICT budget, digital-only sales",
    ],
    "Intent Signals": [
        "⭐ Very High — Strong focus on networking, SD-WAN, IoT & security",
        "⚪ No intent — Minimal research in last 90 days",
        "⭐ Very High — Active research in digital infrastructure & security",
        "🟡 High — Clear interest in collaboration & UCaaS with network optimization",
        "⚪ No intent — Minimal research in last 90 days",
        "⭐ Very High — Enterprise-wide digital transformation & cloud connectivity",
        "🟡 Medium — Project-driven temporary connectivity for construction",
        "⚪ No intent — Minimal research in last 90 days",
        "🟡 High — IoT-driven fleet & telemetry infrastructure scaling",
        "⚪ No intent — Minimal research in last 90 days",
    ],
    "GTM Fit": [
        "⭐ High — Multi-site construction, strong network & expansion needs",
        "🟡 Medium — Regional logistics, stable connectivity, moderate services",
        "⭐ Very High — Critical utility, regulated ops, complex national footprint",
        "🟡 High — Multi-site healthcare, secure & compliant collaboration",
        "⚪ Low — Small advisory, limited ICT, low-touch sales",
        "⭐ Very High — Global manufacturing, mission-critical networks & cloud",
        "🟡 Medium — Project-driven developer, short-term ICT needs",
        "🟡 Medium — Professional services, collaboration & secure access priority",
        "⭐ High — Mining services, remote ops & IoT connectivity requirements",
        "⚪ Low — Small education, simple connectivity, limited IT spend",
    ],
    "Priority Rationale": [
        # ACC001 IronBuild
        "<strong>Rapid national expansion with immediate network scale requirements.</strong>"
        "<ul>"
        "<li><strong>High Growth Momentum:</strong> ~12% YoY growth driven by major infrastructure projects</li>"
        "<li><strong>Active Site Expansion:</strong> 8 → 10 construction sites requiring rapid connectivity rollout</li>"
        "<li><strong>Strong Network Readiness:</strong> Existing SD-WAN and mobility enable fast Ethernet upsell</li>"
        "</ul>",

        # ACC002 BlueHarbor
        "<strong>Stable regional operations with limited near-term expansion.</strong>"
        "<ul>"
        "<li><strong>Moderate ICT Spend:</strong> SaaS-first stack with basic connectivity needs</li>"
        "<li><strong>Low Growth Urgency:</strong> Minimal expansion or acquisition activity</li>"
        "<li><strong>Selective Upsell:</strong> Best suited for monitoring and opportunistic engagement</li>"
        "</ul>",

        # ACC003 SouthernGrid
        "<strong>Strategic, long-term infrastructure and security account.</strong>"
        "<ul>"
        "<li><strong>Expansion-led Growth:</strong> Acquisition-driven scaling and multi-site complexity</li>"
        "<li><strong>High Tech Maturity:</strong> Enterprise systems + SIEM + carrier-grade connectivity readiness</li>"
        "<li><strong>Strong Upsell Path:</strong> Network resilience and security optimization opportunities</li>"
        "</ul>",

        # ACC004 ApexHealth
        "<strong>Regulated healthcare provider with growing collaboration and security needs.</strong>"
        "<ul>"
        "<li><strong>Multi-Site Operations:</strong> Performance-sensitive clinical locations</li>"
        "<li><strong>UC & Security Intent:</strong> Collaboration + network optimization signals are strong</li>"
        "<li><strong>Clear Upsell:</strong> Backup connectivity, traffic prioritization, managed security</li>"
        "</ul>",

        # ACC005 HorizonAgri
        "<strong>Low-growth organization with basic connectivity requirements.</strong>"
        "<ul>"
        "<li><strong>Limited ICT Footprint:</strong> Standard broadband and productivity tools only</li>"
        "<li><strong>Low Spend Capacity:</strong> Minimal discretionary ICT investment</li>"
        "<li><strong>Low Priority:</strong> Better handled via digital/low-touch motions</li>"
        "</ul>",

        # ACC006 NovaTech
        "<strong>Global manufacturing enterprise with selective, high-value expansion potential.</strong>"
        "<ul>"
        "<li><strong>Very High Growth:</strong> M&A + automation driving transformation programs</li>"
        "<li><strong>Advanced Tech Stack:</strong> Multi-cloud + ERP + DevOps automation readiness</li>"
        "<li><strong>High-Value Plays:</strong> Managed services, global interconnect, security uplift</li>"
        "</ul>",

        # ACC007 CoastalBuild
        "<strong>Project-driven construction firm with fluctuating connectivity needs.</strong>"
        "<ul>"
        "<li><strong>Moderate Growth:</strong> Demand tied to project pipeline and site ramp-ups</li>"
        "<li><strong>Deployment Needs:</strong> Rapid rollout and flexible bandwidth for temporary sites</li>"
        "<li><strong>Tactical Opportunities:</strong> Engage when new projects trigger connectivity spikes</li>"
        "</ul>",

        # ACC008 MetroServe
        "<strong>Professional services firm with stable collaboration-centric operations.</strong>"
        "<ul>"
        "<li><strong>Steady Growth:</strong> Consistent services expansion without major disruption signals</li>"
        "<li><strong>Moderate Tech Complexity:</strong> QoS, secure access, and performance improvements fit well</li>"
        "<li><strong>Selective Upsell:</strong> Monitor for collaboration/security upgrade triggers</li>"
        "</ul>",

        # ACC009 TerraLink
        "<strong>Mining services organization scaling IoT and remote operations.</strong>"
        "<ul>"
        "<li><strong>Growth + IoT Expansion:</strong> Fleet monitoring and telemetry scaling across sites</li>"
        "<li><strong>Strong Fit:</strong> IoT, wireless backhaul, resilient connectivity requirements</li>"
        "<li><strong>Clear Upsell:</strong> IoT connectivity + managed resilience/security services</li>"
        "</ul>",

        # ACC010 EduCore
        "<strong>Small education provider with early-stage digital adoption.</strong>"
        "<ul>"
        "<li><strong>Minimal Growth:</strong> Low YoY growth and limited modernization activity</li>"
        "<li><strong>Low Spend:</strong> Entry-level connectivity needs only</li>"
        "<li><strong>Low Priority:</strong> Maintain coverage with lightweight sales motion</li>"
        "</ul>",
    ],
}
    st.session_state["lead_prioritization_df"] = pd.DataFrame(mock_data)
    df_for_status = st.session_state["lead_prioritization_df"].copy()

# --------------------------------------------------
# PRODUCT CATALOG DATA
# --------------------------------------------------

PRODUCT_CATALOG = [
    # ===== NETWORKS =====
    {"category":"Networks","sub":"Software Defined Networks","url":"https://example.com/products/networks/software-defined-networks","desc":"Centralized, programmable networking that automates policy, segmentation, and traffic optimization across sites and clouds","benefits":["Programmable infrastructure for business agility","Optimized routing and application performance","Elastic scalability for new sites and regions","Lower operational overhead via automation"],"segments":"Mid-Market, Enterprise","industries":"Retail, Finance, Healthcare, Manufacturing, Government","flags":{"multi_site":True,"resilience":True,"zero_trust":True,"real_time":True,"edge_compute":False,"cost_opt":False},"complexity":"Medium","flexibility":"Flexible"},
    {"category":"Networks","sub":"Adaptive Networks","url":"https://example.com/products/networks/adaptive-networks","desc":"Modular connectivity that flexes across access types (wired/wireless) with optional security and rapid site enablement","benefits":["Flexible access options (private WAN, internet, wireless)","Integrated security controls for branches","Fast setup for temporary or new sites","Commercial flexibility to support change"],"segments":"Small, Mid-Market, Enterprise","industries":"Retail, Logistics, Construction, Events, Agriculture","flags":{"multi_site":True,"resilience":True,"zero_trust":True,"real_time":False,"edge_compute":False,"cost_opt":True},"complexity":"Low","flexibility":"Flexible"},
    {"category":"Networks","sub":"Satellite Services","url":"https://example.com/products/networks/satellite-services","desc":"Connectivity for remote and hard-to-reach locations using satellite links for primary or backup network access","benefits":["Coverage for remote locations beyond terrestrial reach","Secure access options and resilient routing","Supports global and regional operations","Improves business continuity during outages"],"segments":"Mid-Market, Enterprise","industries":"Mining, Oil & Gas, Agriculture, Government, Defense","flags":{"multi_site":True,"resilience":True,"zero_trust":False,"real_time":False,"edge_compute":True,"cost_opt":False},"complexity":"High","flexibility":"Standard"},
    {"category":"Networks","sub":"Business Broadband","url":"https://example.com/products/networks/business-broadband","desc":"Business-grade broadband with performance options, enhanced support, and failover for operational resilience","benefits":["Business-grade performance and SLAs (where available)","Enhanced assurance and support","Backup connectivity options during outages","Static IP and flexible speed tiers"],"segments":"SOHO, Small, Mid-Market","industries":"Professional Services, Education, Retail, Hospitality","flags":{"multi_site":False,"resilience":True,"zero_trust":False,"real_time":False,"edge_compute":False,"cost_opt":True},"complexity":"Low","flexibility":"Flexible"},

    # ===== CLOUD =====
    {"category":"Cloud","sub":"Cloud Solutions","url":"https://example.com/products/cloud/cloud-solutions","desc":"Cloud strategy, migration, and managed services spanning architecture, landing zones, and modernization","benefits":["Reduces IT complexity across transformation programs","Connects workloads to networks and ecosystems","Scales to meet changing business demand","Supports major public cloud platforms"],"segments":"Mid-Market, Enterprise","industries":"Finance, Healthcare, Government, Retail, Technology","flags":{"multi_site":True,"resilience":True,"zero_trust":True,"real_time":False,"edge_compute":False,"cost_opt":False},"complexity":"High","flexibility":"Standard"},
    {"category":"Cloud","sub":"Cloud Connectivity","url":"https://example.com/products/cloud/cloud-connectivity","desc":"Private, high-performance connectivity to public clouds to improve security, latency, and reliability for critical workloads","benefits":["Reliable and secure cloud access","Improved performance for cloud applications","Cost-efficient hybrid cloud operations","Supports multi-cloud connectivity patterns"],"segments":"Mid-Market, Enterprise","industries":"Technology, Finance, Healthcare, E-commerce, Media","flags":{"multi_site":False,"resilience":True,"zero_trust":True,"real_time":True,"edge_compute":False,"cost_opt":True},"complexity":"Medium","flexibility":"Standard"},
    {"category":"Cloud","sub":"Cloud Advisory","url":"https://example.com/products/cloud/cloud-advisory","desc":"Guidance to define cloud operating models, governance, security, and modernization roadmaps","benefits":["Cloud roadmap planning and target architecture","Accelerates app modernization priorities","Cloud cost and operations optimization","Security best practices and guardrails"],"segments":"Small, Mid-Market, Enterprise","industries":"All Industries","flags":{"multi_site":False,"resilience":False,"zero_trust":True,"real_time":False,"edge_compute":False,"cost_opt":True},"complexity":"Low","flexibility":"Flexible"},

    # ===== SECURITY =====
    {"category":"Security","sub":"SASE Assessment","url":"https://example.com/products/security/sase-assessment","desc":"Assessment and blueprint to evolve secure access and edge security using SASE-aligned architectures","benefits":["Identifies target-state SASE architecture","Evaluates vendor and platform options","Delivers conceptual design and rollout plan","Aligns with zero-trust principles"],"segments":"Mid-Market, Enterprise","industries":"Finance, Healthcare, Government, Technology","flags":{"multi_site":False,"resilience":False,"zero_trust":True,"real_time":False,"edge_compute":False,"cost_opt":False},"complexity":"Low","flexibility":"Flexible"},
    {"category":"Security","sub":"Incident Response Readiness","url":"https://example.com/products/security/incident-response-readiness","desc":"Independent review of incident response preparedness, processes, and technical readiness across people, process, and tools","benefits":["Assesses current response posture","Identifies gaps and remediation priorities","Pragmatic, actionable improvement plan","Improves stakeholder readiness and governance"],"segments":"Mid-Market, Enterprise","industries":"Finance, Healthcare, Critical Infrastructure, Government","flags":{"multi_site":False,"resilience":True,"zero_trust":True,"real_time":False,"edge_compute":False,"cost_opt":True},"complexity":"Low","flexibility":"Flexible"},
    {"category":"Security","sub":"Cyber Detection & Response","url":"https://example.com/products/security/cyber-detection-and-response","desc":"24/7 managed detection and response for continuous monitoring, threat hunting, and rapid incident containment","benefits":["Continuous threat detection and response","Expert incident handling and escalation","Managed service to reduce security workload","Improves time-to-detect and time-to-respond"],"segments":"Small, Mid-Market, Enterprise","industries":"Finance, Healthcare, Retail, Government, Critical Infrastructure","flags":{"multi_site":False,"resilience":True,"zero_trust":True,"real_time":True,"edge_compute":False,"cost_opt":False},"complexity":"Medium","flexibility":"Standard"},

    # ===== MOBILITY =====
    {"category":"Mobility Solutions","sub":"Business Apps","url":"https://example.com/products/mobility/business-apps","desc":"Mobile application development and integration to digitize field workflows and improve workforce productivity","benefits":["Custom apps to streamline operations","Supports BYOD and managed mobility patterns","Automates manual tasks and approvals","Integrates with existing enterprise systems"],"segments":"Small, Mid-Market, Enterprise","industries":"Retail, Field Services, Logistics, Healthcare, Construction","flags":{"multi_site":True,"resilience":False,"zero_trust":False,"real_time":False,"edge_compute":False,"cost_opt":True},"complexity":"Medium","flexibility":"Flexible"},
    {"category":"Mobility Solutions","sub":"Satellite Messaging","url":"https://example.com/products/mobility/satellite-messaging","desc":"Two-way satellite messaging for remote environments where cellular coverage is limited or unavailable","benefits":["Communication beyond cellular coverage","Operational continuity in remote locations","Emergency backup communication","Keeps teams informed in the field"],"segments":"Mid-Market, Enterprise","industries":"Mining, Agriculture, Emergency Services, Defense, Construction","flags":{"multi_site":True,"resilience":True,"zero_trust":False,"real_time":False,"edge_compute":True,"cost_opt":False},"complexity":"Low","flexibility":"Flexible"},
    {"category":"Mobility Solutions","sub":"Enterprise Mobility Plans","url":"https://example.com/products/mobility/enterprise-mobility-plans","desc":"Business mobility plans and device management to support secure, scalable connectivity for hybrid and field workforces","benefits":["Supports hybrid working models","High-speed mobile connectivity options (where available)","Device and policy management support","Device lifecycle and fleet management"],"segments":"Small, Mid-Market, Enterprise","industries":"All Industries","flags":{"multi_site":False,"resilience":False,"zero_trust":False,"real_time":False,"edge_compute":False,"cost_opt":True},"complexity":"Low","flexibility":"Flexible"},

    # ===== IoT =====
    {"category":"Internet of Things","sub":"IoT Solutions","url":"https://example.com/products/iot/iot-solutions","desc":"End-to-end IoT implementation covering connectivity, devices, edge, analytics, and operational integration","benefits":["Improves process efficiency and visibility","Enhances customer and operational experience","Reduces operational costs through automation","Enables data-driven decision making"],"segments":"Mid-Market, Enterprise","industries":"Manufacturing, Logistics, Agriculture, Smart Cities, Healthcare","flags":{"multi_site":False,"resilience":False,"zero_trust":True,"real_time":True,"edge_compute":True,"cost_opt":False},"complexity":"High","flexibility":"Standard"},
    {"category":"Internet of Things","sub":"IoT Platform","url":"https://example.com/products/iot/iot-platform","desc":"IoT platform for device onboarding, management, connectivity orchestration, and secure device-to-cloud integration","benefits":["Scalable architecture for IoT growth","Device-to-cloud integration patterns","Lifecycle management and monitoring","Supports ecosystem integrations and APIs"],"segments":"Mid-Market, Enterprise","industries":"Utilities, Transport, Agriculture, Manufacturing, Mining","flags":{"multi_site":False,"resilience":True,"zero_trust":True,"real_time":True,"edge_compute":True,"cost_opt":False},"complexity":"High","flexibility":"Long-term"},

    # ===== UNIFIED COMMUNICATIONS =====
    {"category":"Unified Communications","sub":"Contact Center Solutions","url":"https://example.com/products/unified-communications/contact-center-solutions","desc":"Cloud contact center capabilities for omnichannel engagement integrated with CRM and workforce tools","benefits":["Improves customer experience through integration","Omnichannel engagement and routing","Cloud scalability and faster rollout","Can reduce costs while improving CX"],"segments":"Mid-Market, Enterprise","industries":"Retail, Finance, Healthcare, Utilities, Government","flags":{"multi_site":True,"resilience":True,"zero_trust":False,"real_time":True,"edge_compute":False,"cost_opt":True},"complexity":"Medium","flexibility":"Standard"},
    {"category":"Unified Communications","sub":"UC Consulting","url":"https://example.com/products/unified-communications/uc-consulting","desc":"Advisory to optimize collaboration, voice, and CX—roadmaps, adoption, and operating model improvements","benefits":["CX and collaboration strategy support","Improves teamwork and communications","Adoption planning and change enablement","Roadmaps and governance guidance"],"segments":"Mid-Market, Enterprise","industries":"All Industries","flags":{"multi_site":False,"resilience":False,"zero_trust":False,"real_time":False,"edge_compute":False,"cost_opt":True},"complexity":"Low","flexibility":"Flexible"},
    {"category":"Unified Communications","sub":"Calling & Collaboration","url":"https://example.com/products/unified-communications/calling-and-collaboration","desc":"Cloud calling and collaboration to enable secure communication for remote and on-site teams","benefits":["Boosts productivity with modern collaboration tools","Supports remote and hybrid work","Integrates with common productivity suites","Simplifies deployment and management"],"segments":"SOHO, Small, Mid-Market, Enterprise","industries":"All Industries","flags":{"multi_site":True,"resilience":False,"zero_trust":False,"real_time":True,"edge_compute":False,"cost_opt":False},"complexity":"Low","flexibility":"Flexible"},
]


CATEGORY_ICONS = {"Cloud":"☁️","Security":"🔒","Networks":"🌐","Mobility Solutions":"📱","Internet of Things":"🔗","Unified Communications":"💬"}

CAP_FLAG_MAP = {
    "multi_site": "Multi-Site",
    "resilience": "Business Resilience",
    "zero_trust": "Zero Trust",
    "real_time": "Real-Time",
    "edge_compute": "Edge Computing",
    "cost_opt": "Cost Optimized"
}

# --------------------------------------------------
# STATE INITIALIZATION
# --------------------------------------------------
st.session_state.setdefault("run_process", False)
st.session_state.setdefault("stop_process", False)
st.session_state.setdefault("step_done", {})
st.session_state.setdefault("log_html", {})
st.session_state.setdefault("current_step", 0)
if "task_running" not in st.session_state:
    st.session_state.task_running = {}


# Business context default
default_context = (
    "We aim to strengthen our mid-market presence across the U.S. for Dedicated Fiber, Internet, "
    "Communication, and Security offerings. While coverage is strong, identifying accounts with the highest "
    "growth potential or urgent connectivity needs remains a challenge.\n\n"
    "As a result, sales teams lack actionable insights to prioritize and position the right products.\n\n"
    "Our goal is to enhance targeting, segmentation, and sales intelligence to deepen market penetration, "
    "accelerate revenue growth, and align execution with rising digital and connectivity demands."
)
if "business_context_text" not in st.session_state:
    st.session_state.business_context_text = default_context



# --------------------------------------------------
# TASK DEFINITIONS
# --------------------------------------------------
ALL_TASKS = [
    {"name": "Loading Customer 360° Data", "key": "load_data", "step_num": 1, "tab": "tab1"},
    {"name": "Business Context Analyzer", "key": "business_context", "step_num": 2, "tab": "tab1"},
    {"name": "AI-Driven Category Weights", "key": "category_weights", "step_num": 3, "tab": "tab1"},
    {"name": "Prioritization Segment Classifier", "key": "prioritization_table", "step_num": 4, "tab": "tab1"},
    {"name": "Product Catalogue Analyzer", "key": "product_catalog", "step_num": 5, "tab": "tab2"},
    {"name": "AI Recommender Agent", "key": "recommender_agent", "step_num": 6, "tab": "tab2"},
]

# --------------------------------------------------
# STEP LOGS
# --------------------------------------------------
STEP_LOGS = {

    "load_data": [
    "<strong>⚙️ Initializing Customer 360° Context Assembly Agent…</strong>",
    "📥 Retrieving consolidated Customer 360° profiles from the ingestion & enrichment phase.",
    "🧩 Validating presence of all core intelligence dimensions:",
    "     • 🏢 Firmographics & organizational footprint",
    "     • 📦 Active product portfolio & contract context",
    "     • 📈 Growth indicators",
    "     • 💰 Financial and Est. Potential Spend",
    "     • 🎯 Intent signals and priority badges",
    "     • 💻 Technographic maturity & competitor context",
    "🗂️ Normalizing account-level attributes for downstream reasoning.",
    "📊 Preparing unified Customer 360° view for scoring and recommendation agents.",
    "✅ <span style='color:#1b7f3b;font-weight:700;'>Customer 360° context ready — handing off to Business Context Analyzer.</span>",
    ],

    
    "business_context": [
        "<strong>⚙️ Initializing Business Context Analyzer Agent…</strong>",
        "🧠 Analyzing narrative input to extract structured context dimensions…",
        "🎯 Identified business objective and strategic intent.",
        "👥 Classified target segment and customer archetype.",
        "🗺️ Recognized operational geography and market coverage.",
        "🧩 Mapped key product focus areas (Connectivity, Internet, Communication, Security).",
        "⚠️ Highlighted business challenges impacting GTM execution.",
        "📈 Derived success metrics aligned to revenue and penetration goals.",
        "🔗 Passing calibrated strategic context to Category Weight Optimizer for relevance weighting.",
        "✅ <span style='color:#1b7f3b;font-weight:700;'>Business context translated into actionable signals for downstream weighting and prioritization.</span>",
    ],
    
    "category_weights": [
    "<strong>⚙️ Initializing Category & Signal Weighting Agent…</strong>",
    "🧠 Consuming business context to understand GTM priorities, target segments, and product focus.",
    "🧩 Decomposing Customer 360° intelligence into primary signal categories:",
    "🔍 Evaluating sub-signals within each category for strategic relevance:",
    "   📈 Growth Signals: Expansion and acquisition flags, Hiring momentum, YoY revenue and TCV growth trends etc..",
    "   🎯 Intent Intelligence: Explicit vs peer-led intent classification, Domain relevance to priority products, Intent strength and recency etc..",
    "   💻 Technographics: Network, cloud, and security maturity, complexity vs solution readiness etc..",
    "   💰 Financial Indicators: Spend potential tier, Share of wallet and contract trajectory etc..",
    "⚖️ Assigning context-aware weights at category and sub-signal level",
    "📐 Producing calibrated scoring framework aligned to business objectives.",
    "🔗 Passing weighted signal model to Prioritization Segment Classifier for account-level scoring.",
    "✅ <span style='color:#1b7f3b;font-weight:700;'>Category and sub-signal weighting complete — scoring logic contextually optimized.</span>",
    ],

    "prioritization_table": [
    "<strong>⚙️ Initializing Prioritization & Segmentation Agent…</strong>",
    "🧠 Receiving calibrated category and sub-signal weights from Strategic Weighting Agent.",
    "🔗 Aggregating weighted signals for each account across Customer 360° dimensions:",
    "📊 Computing composite priority scores per account using context-aware weighting model.",
    "🧩 Normalizing scores to account for signal overlap and correlated indicators.",
    "🏷️ Translating composite scores into actionable priority segments:",
    "    • High — immediate GTM focus",
    "    • Medium — nurture and monitor",
    "    • Low — deprioritize or long-term watch",
    "🔍 Attaching explainability metadata to each account:",
    "    • Dominant contributing signal categories",
    "    • Key drivers influencing priority assignment",
    "📋 Generating ranked prioritization table with transparent rationale.",
    "✅ <span style='color:#1b7f3b;font-weight:700;'>Account prioritization complete — sales-ready priority segments generated.</span>",
    ],

    "product_catalog": [
        "<strong>⚙️ Initializing Product Catalogue Analyzer Agent…</strong>",
        "📦 Loading product catalogue source — <strong>18 Enterprise products</strong> across 6 L1 categories… <span class='source-tag'>Catalog Source</span>",
        "🔍 <strong>L1 Category Scan</strong> — Networks · Cloud · Security · Mobility Solutions · IoT · Unified Communications… <span class='source-tag'>L1 Taxonomy</span>",
        "🏷️ <strong>L2 Sub-Category Extraction</strong> — SDN, Adaptive Networks, Satellite, Broadband, Cloud Solutions, Cloud Connectivity, Cloud Advisory, SASE, Incident Response, Cyber Detection, Business Apps, Satellite Messaging, Enterprise Mobility, IoT Solutions, IoT Platform, Contact Center, UC Consulting, Calling & Collaboration… <span class='source-tag'>L2 Taxonomy</span>",
        "📝 Parsing <strong>product descriptions</strong> and mapping to enterprise use-case archetypes… <span class='source-tag'>NLP Engine</span>",
        "✨ Extracting <strong>key benefits</strong> — 3–4 value propositions per product, ranked by GTM relevance… <span class='source-tag'>Benefit Extraction</span>",
        "🏢 Tagging <strong>target segments</strong> — SOHO / Small / Mid-Market / Enterprise per product… <span class='source-tag'>Segment Classifier</span>",
        "🏭 Mapping <strong>priority industries</strong> — Construction, Mining, Energy, Healthcare, Logistics, Finance, Education, Manufacturing… <span class='source-tag'>Industry Mapper</span>",
        "🎨 Evaluating <strong>capability flags</strong> — Multi-site, Business Resilience, Zero Trust, Real-Time, Edge Computing, Cost Optimized… <span class='source-tag'>Capability Engine</span>",
        "📊 Scoring <strong>deployment complexity</strong> (Low / Medium / High) and <strong>contract flexibility</strong> per product… <span class='source-tag'>Risk Scorer</span>",
        "🔗 Building <strong>product-to-customer fit matrix</strong> — capability × industry × segment cross-reference… <span class='source-tag'>Fit Matrix</span>",
        "✅ <span style='color:#1b7f3b;font-weight:700;'>Product catalogue analysis complete — 18 products indexed, tagged, and fit-mapped.</span>",
    ],


    "recommender_agent": [
    "<strong>⚙️ Initializing AI Recommendation & Decisioning Agent…</strong>",
    "🤖 Activating multi-dimensional decision engine using enriched Customer 360° profiles and product capability intelligence.",
    "🔗 Ingesting upstream intelligence: - Account priority segments and composite scores, Growth and market momentum signals, Intent domains, Technographic maturity and existing product footprint",
    "🎯 Evaluating intent-to-capability alignment for each account, Mapping dominant intent themes to relevant product use-cases",
    "🏭 Applying industry and operating-model context.",
    "    • Construction → site connectivity, IoT, adaptive networks",
    "    • Mining → remote connectivity, satellite, IoT platforms",
    "    • Healthcare → collaboration, secure connectivity, compliance-ready solutions",
    "    • Manufacturing → cloud, security, global network resilience",
    "💻 Assessing expansion feasibility - Existing product footprint and adjacency potential, Contract posture and renewal windows, Spend tier and share-of-wallet headroom",
    "📊 Computing recommendation fit scores per product such as Capability overlap score, Intent relevance score, Industry affinity score etc.. ",
    "🧩 Ranking top 1–3 recommendations per account based on composite fit score.",
    "📝 Generating explainability layer for each recommendation:",
    "   • Primary trigger signals",
    "   • Supporting context and rationale",
    "   • Confidence indicators for sales engagement",
    "📋 Assembling final recommendation matrix with product, fit score, and rationale.",
    "✅ <span style='color:#1b7f3b;font-weight:700;'>Recommendations generated — explainable, prioritized, and ready for GTM execution.</span>",
    ]

}


# --------------------------------------------------
# OUTPUT FORMATTING HELPERS
# --------------------------------------------------

def _format_weights_to_html() -> str:
    """MWC-ready Category Weights with icons + High/Medium/Low Impact pill + circular weight ring"""

    categories = [
        {
            "title": "Growth Signals",
            "icon": "📈",
            "priority": "High",
            "weight": 30,
            "value": "Surfaces upsell timing by detecting business expansion events that typically trigger connectivity upgrades and managed services demand.",
            "chips": ["Triggers: New sites, M&A, partnerships", "Best for: “why now?”"],
            "rationale": [
                "Prioritizes accounts with near-term change (expansion / acquisition)",
                "Signals demand for SD-WAN expansion, bandwidth uplift, multi-site rollout",
                "Improves conversion by aligning outreach to “moment of need”",
            ],
            "breakdown": [
                {"name": "Business Expansion", "pct": "30%"},
                {"name": "Acquisition / Merger", "pct": "25%"},
                {"name": "Partnerships", "pct": "20%"},
                {"name": "Hiring Trends", "pct": "10%"},
                {"name": "Risk / Disruption Flags", "pct": "15%"},
            ],
        },
        {
            "title": "Account Products & Usage",
            "icon": "📦",
            "priority": "High",
            "weight": 20,
            "value": "Reduces commercial risk by prioritizing accounts with proven product adoption and renewal momentum.",
            "chips": ["Triggers: renewals, upsell history", "Best for: retention + expansion"],
            "rationale": [
                "Account loyalty signals expansion likelihood",
                "Renewal cycles reveal cross-sell timing",
                "Historical upsell success predicts receptiveness",
            ],
            "breakdown": [
                {"name": "Active Products", "pct": "20%"},
                {"name": "Tenure", "pct": "15%"},
                {"name": "Renewals", "pct": "15%"},
                {"name": "Won Opps (3yr)", "pct": "15%"},
                {"name": "TCV Growth", "pct": "10%"},
                {"name": "Other", "pct": "25%"},
            ],
        },
        {
            "title": "Technographics",
            "icon": "💻",
            "priority": "High",
            "weight": 20,
            "value": "Maps current technology footprint to solution readiness and expansion paths.",
            "chips": ["Triggers: cloud, security stack", "Best for: solution fit"],
            "rationale": [
                "Complex stacks correlate with higher adoption",
                "Reveals logical adjacency opportunities",
                "Improves recommendation relevance",
            ],
            "breakdown": [
                {"name": "Network", "pct": "35%"},
                {"name": "Cloud", "pct": "25%"},
                {"name": "Collaboration", "pct": "20%"},
                {"name": "Security & IoT", "pct": "15%"},
                {"name": "Other", "pct": "5%"},
            ],
        },
        {
            "title": "Estimated Spend Potential",
            "icon": "💰",
            "priority": "Medium",
            "weight": 15,
            "value": "Focuses sales effort on accounts with meaningful wallet size.",
            "chips": ["Triggers: spend tier, headroom", "Best for: wallet expansion"],
            "rationale": [
                "Defines commercial headroom",
                "Guides AE capacity allocation",
                "Avoids low-value pursuits",
            ],
            "breakdown": [
                {"name": "ICT Spend", "pct": "30%"},
                {"name": "Telco Spend", "pct": "30%"},
                {"name": "Hardware & Software", "pct": "20%"},
                {"name": "IT Services", "pct": "20%"},
            ],
        },
        {
            "title": "Intent Signals",
            "icon": "🎯",
            "priority": "Medium",
            "weight": 10,
            "value": "Captures in-market behavior before CRM opportunity creation.",
            "chips": ["Triggers: search + content signals", "Best for: early pipeline"],
            "rationale": [
                "Flags active research behavior",
                "Improves outreach timing",
            ],
            "breakdown": [
                {"name": "Active Research", "pct": "70%"},
                {"name": "Baseline Interest", "pct": "30%"},
            ],
        },
        {
            "title": "Firmographics",
            "icon": "🏢",
            "priority": "Low",
            "weight": 5,
            "value": "Baseline segmentation filter, not a near-term trigger.",
            "chips": ["Triggers: ICP match", "Best for: segmentation"],
            "rationale": [
                "Ensures ICP alignment",
                "Supports benchmarking",
                "Not a “why now” signal",
            ],
            "breakdown": [
                {"name": "Employee Size", "pct": "20%"},
                {"name": "Revenue", "pct": "20%"},
                {"name": "Footprint", "pct": "15%"},
                {"name": "Industry", "pct": "15%"},
                {"name": "Other", "pct": "30%"},
            ],
        },
    ]

    COLOR = {"High": "#16a34a", "Medium": "#f59e0b", "Low": "#94a3b8"}
    BG = {"High": "#dcfce7", "Medium": "#fef3c7", "Low": "#f1f5f9"}

    html_out = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body{
  font-family: Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  background:#f6f7fb;
  padding:16px;
}
.wrap{max-width:1100px;margin:0 auto;display:flex;flex-direction:column;gap:14px;}
.card{
  background:#fff;border:1px solid #e5e7eb;border-radius:16px;
  box-shadow:0 10px 30px rgba(15,23,42,.08);overflow:hidden;
}
summary{list-style:none;cursor:pointer;padding:18px 18px 14px;display:flex;gap:16px;align-items:flex-start;}
summary::-webkit-details-marker{display:none;}
.hdr-left{flex:1;min-width:0;}
.hdr-top{display:flex;align-items:center;gap:10px;justify-content:space-between;}
.title-row{display:flex;align-items:center;gap:10px;min-width:0;}
.icon{
  width:28px;height:28px;border-radius:10px;background:#f3f4f6;
  display:grid;place-items:center;font-size:16px;flex:0 0 auto;
}
.title{font-weight:900;font-size:14px;color:#0f172a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.pill{
  display:inline-flex;align-items:center;gap:8px;
  padding:6px 10px;border-radius:999px;font-weight:900;font-size:11px;
  border:1px solid; white-space:nowrap;
}
.dot{width:8px;height:8px;border-radius:50%;}
.desc{margin-top:8px;font-size:12.5px;color:#64748b;line-height:1.5;}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;}
.chip{
  display:inline-flex;align-items:center;
  padding:6px 10px;border-radius:999px;
  background:#f8fafc;border:1px solid #e2e8f0;
  font-size:11px;font-weight:700;color:#334155;
}
.hdr-right{width:98px;display:flex;justify-content:flex-end;}
.circle{
  width:64px;height:64px;border-radius:50%;
  display:grid;place-items:center;font-weight:900;font-size:13px;color:#0f172a;
  background:conic-gradient(var(--clr) calc(var(--pct)*1%), #e5e7eb 0);
}
.circle span{
  width:48px;height:48px;background:#fff;border-radius:50%;
  display:grid;place-items:center;border:1px solid #e5e7eb;
}
.content{
  padding:14px 18px 18px;border-top:1px solid #f1f5f9;
  display:grid;grid-template-columns:1fr 1fr;gap:16px;
}
.panel{background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:14px;}
.panel h4{font-size:11px;text-transform:uppercase;color:#64748b;margin:0 0 10px;letter-spacing:.4px;}
.panel ul{padding-left:18px;margin:0;font-size:12.5px;line-height:1.6;color:#334155;}
.panel li{margin:0 0 8px;}
.row{
  display:flex;justify-content:space-between;gap:10px;
  font-size:12.5px;padding:10px 12px;border:1px solid #e2e8f0;border-radius:12px;
  background:#fff;margin-bottom:8px;
}
.row strong{color:#0f172a;}
</style>
</head>
<body>
<div class="wrap">
"""

    for c in categories:
        clr = COLOR[c["priority"]]
        bg = BG[c["priority"]]
        icon = c.get("icon", "✨")
        chips = c.get("chips", [])
        chip_html = "".join([f"<span class='chip'>{html.escape(ch)}</span>" for ch in chips])

        html_out += f"""
<details class="card" {"open" if c["title"] == "Growth Signals" else ""}>
  <summary>
    <div class="hdr-left">
      <div class="hdr-top">
        <div class="title-row">
          <div class="icon">{html.escape(icon)}</div>
          <div class="title">{html.escape(c["title"])}</div>
          <span class="pill" style="background:{bg};border-color:{clr};color:{clr};">
            <span class="dot" style="background:{clr};"></span>
            {c["priority"]} Impact
          </span>
        </div>
      </div>

      <div class="desc">{html.escape(c["value"])}</div>

      <div class="chips">{chip_html}</div>
    </div>

    <div class="hdr-right">
      <div class="circle" style="--pct:{c['weight']}; --clr:{clr};">
        <span>{c['weight']}%</span>
      </div>
    </div>
  </summary>

  <div class="content">
    <div class="panel">
      <h4>What it drives</h4>
      <ul>
"""
        for r in c["rationale"]:
            html_out += f"<li>{html.escape(r)}</li>"
        html_out += """
      </ul>
    </div>

    <div class="panel">
      <h4>Signals used</h4>
"""
        for b in c["breakdown"]:
            html_out += f"""
      <div class="row">
        <span>{html.escape(b['name'])}</span>
        <strong>{b['pct']}</strong>
      </div>
"""
        html_out += """
    </div>
  </div>
</details>
"""

    html_out += """
</div>
</body>
</html>
"""
    return html_out

def _business_context_html_from_text(ctx_text: str) -> str:
    import re, html

    if not ctx_text or str(ctx_text).strip() == "":
        ctx_text = ""

    paragraphs = [p.strip() for p in re.split(r"\n{1,2}", str(ctx_text)) if p.strip()]
    objective = html.escape(paragraphs[0]) if paragraphs else "(no objective provided)"

    # AU / Cross-sell + Upsell (as requested)
    target_segment = "Mid-Market Businesses"
    geography = "Australia"
    primary_goal = "Cross-sell + Upsell across existing accounts"

    key_products = [
        "Connectivity services (Fixed, Broadband, Ethernet)",
        "Unified Communications & Collaboration",
        "Network & Cloud Security solutions",
        "IoT / Edge Solutions",
    ]

    key_challenges = [
        "Limited visibility into existing customers’ upgrade and expansion readiness",
        "Difficulty identifying cross-sell and upsell opportunities across large account bases",
        "Lack of actionable signals to time sales outreach effectively",
    ]

    success_metrics = [
        "Increased wallet share across existing mid-market customers",
        "Higher adoption of additional connectivity and security services",
        "Improved upsell and cross-sell conversion rates",
        "Accelerated revenue growth from existing accounts",
    ]

    # NOTE: Header removed as requested (no purple top bar)
    html_out = f"""
<div style="font-family: Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#f6f7fb; padding:16px;">
  <div style="max-width:1050px; margin:0 auto;">

    <!-- Card -->
    <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:16px; box-shadow:0 10px 30px rgba(15,23,42,.08); overflow:hidden;">

      <!-- Body -->
      <div style="padding:18px 20px; background:#ffffff;">

        <!-- Objective -->
        <div style="border:1px solid #e2e8f0; background:#f8fafc; border-radius:14px; padding:14px 14px 12px; margin-bottom:14px;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
            <div style="width:26px; height:26px; border-radius:10px; background:#ede9fe; border:1px solid #ddd6fe; display:grid; place-items:center; color:#6b21a8;">🎯</div>
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:.5px; font-weight:900; color:#64748b;">Business Objective</div>
          </div>

          <div style="font-size:13px; line-height:1.6; color:#0f172a; font-weight:650;">
            {objective}
          </div>

          <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
            <span style="display:inline-flex; padding:6px 10px; border-radius:999px; background:#ffffff; border:1px solid #e2e8f0; font-size:11px; font-weight:800; color:#334155;">
              Primary Goal: Increase wallet share
            </span>
            <span style="display:inline-flex; padding:6px 10px; border-radius:999px; background:#ffffff; border:1px solid #e2e8f0; font-size:11px; font-weight:800; color:#334155;">
              Discovery: Identify “why now” signals
            </span>
            <span style="display:inline-flex; padding:6px 10px; border-radius:999px; background:#ffffff; border:1px solid #e2e8f0; font-size:11px; font-weight:800; color:#334155;">
              Execution: Prioritize outreach timing
            </span>
          </div>
        </div>

        <!-- Highlights row -->
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-bottom:14px;">
          <div style="border:1px solid #e2e8f0; border-radius:14px; padding:12px; background:#ffffff;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
              <div style="width:24px; height:24px; border-radius:10px; background:#dcfce7; border:1px solid #bbf7d0; display:grid; place-items:center;">👥</div>
              <div style="font-size:11px; text-transform:uppercase; letter-spacing:.5px; font-weight:900; color:#64748b;">Target Segment</div>
            </div>
            <div style="font-weight:900; color:#0f172a; font-size:13px;">{html.escape(target_segment)}</div>
            <div style="font-size:12px; color:#64748b; margin-top:4px; line-height:1.5;">Existing customer base; focus on expansion propensity.</div>
          </div>

          <div style="border:1px solid #e2e8f0; border-radius:14px; padding:12px; background:#ffffff;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
              <div style="width:24px; height:24px; border-radius:10px; background:#dbeafe; border:1px solid #bfdbfe; display:grid; place-items:center;">📍</div>
              <div style="font-size:11px; text-transform:uppercase; letter-spacing:.5px; font-weight:900; color:#64748b;">Geography</div>
            </div>
            <div style="font-weight:900; color:#0f172a; font-size:13px;">{html.escape(geography)}</div>
            <div style="font-size:12px; color:#64748b; margin-top:4px; line-height:1.5;">Prioritize footprint & multi-site coverage opportunities.</div>
          </div>

          <div style="border:1px solid #e2e8f0; border-radius:14px; padding:12px; background:#ffffff;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
              <div style="width:24px; height:24px; border-radius:10px; background:#fef3c7; border:1px solid #fde68a; display:grid; place-items:center;">⚡</div>
              <div style="font-size:11px; text-transform:uppercase; letter-spacing:.5px; font-weight:900; color:#64748b;">Primary Goal</div>
            </div>
            <div style="font-weight:900; color:#0f172a; font-size:13px;">{html.escape(primary_goal)}</div>
            <div style="font-size:12px; color:#64748b; margin-top:4px; line-height:1.5;">Increase adoption of adjacent products with explainability.</div>
          </div>
        </div>

        <!-- Two panels -->
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">

          <!-- Key Products -->
          <div style="border:1px solid #e2e8f0; border-radius:14px; padding:14px; background:#ffffff;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
              <div style="width:26px; height:26px; border-radius:10px; background:#ede9fe; border:1px solid #ddd6fe; display:grid; place-items:center;">🧩</div>
              <div style="font-size:11px; text-transform:uppercase; letter-spacing:.5px; font-weight:900; color:#64748b;">Key Products</div>
            </div>

            <div style="display:flex; flex-wrap:wrap; gap:8px;">
              <span style="display:inline-flex; padding:7px 10px; border-radius:999px; background:#f8fafc; border:1px solid #e2e8f0; font-size:11px; font-weight:900; color:#0f172a;">🌐 Connectivity (Fixed/Broadband/Ethernet)</span>
              <span style="display:inline-flex; padding:7px 10px; border-radius:999px; background:#f8fafc; border:1px solid #e2e8f0; font-size:11px; font-weight:900; color:#0f172a;">💬 UC & Collaboration</span>
              <span style="display:inline-flex; padding:7px 10px; border-radius:999px; background:#f8fafc; border:1px solid #e2e8f0; font-size:11px; font-weight:900; color:#0f172a;">🔒 Network & Cloud Security</span>
              <span style="display:inline-flex; padding:7px 10px; border-radius:999px; background:#f8fafc; border:1px solid #e2e8f0; font-size:11px; font-weight:900; color:#0f172a;">🔗 IoT / Edge</span>
            </div>

            <div style="margin-top:10px; font-size:12px; color:#64748b; line-height:1.6;">
              Focus areas mapped to intent + technographics for account-level fit scoring.
            </div>
          </div>

          <!-- Key Challenges -->
          <div style="border:1px solid #e2e8f0; border-radius:14px; padding:14px; background:#ffffff;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
              <div style="width:26px; height:26px; border-radius:10px; background:#fee2e2; border:1px solid #fecaca; display:grid; place-items:center;">⚠️</div>
              <div style="font-size:11px; text-transform:uppercase; letter-spacing:.5px; font-weight:900; color:#64748b;">Key Challenges</div>
            </div>

            <ul style="margin:0; padding-left:18px; color:#0f172a; font-size:12.5px; line-height:1.7;">
              <li style="margin-bottom:8px;">{html.escape(key_challenges[0])}</li>
              <li style="margin-bottom:8px;">{html.escape(key_challenges[1])}</li>
              <li style="margin-bottom:0;">{html.escape(key_challenges[2])}</li>
            </ul>

            <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
              <span style="display:inline-flex; padding:6px 10px; border-radius:999px; background:#fff7ed; border:1px solid #fed7aa; font-size:11px; font-weight:900; color:#9a3412;">Need: signals</span>
              <span style="display:inline-flex; padding:6px 10px; border-radius:999px; background:#fff7ed; border:1px solid #fed7aa; font-size:11px; font-weight:900; color:#9a3412;">Need: prioritization</span>
              <span style="display:inline-flex; padding:6px 10px; border-radius:999px; background:#fff7ed; border:1px solid #fed7aa; font-size:11px; font-weight:900; color:#9a3412;">Need: timing</span>
            </div>
          </div>
        </div>

        <!-- Success metrics -->
        <div style="border:1px solid #e2e8f0; border-radius:14px; padding:14px; background:#ffffff;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
            <div style="width:26px; height:26px; border-radius:10px; background:#dcfce7; border:1px solid #bbf7d0; display:grid; place-items:center;">✅</div>
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:.5px; font-weight:900; color:#64748b;">Success Metrics</div>
          </div>

          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
            <div style="border:1px solid #e2e8f0; border-radius:12px; padding:10px 12px; background:#f8fafc;">
              <div style="font-weight:900; color:#0f172a; font-size:12.5px;">📈 Increased wallet share</div>
              <div style="font-size:12px; color:#64748b; margin-top:4px; line-height:1.5;">More services per customer across mid-market base.</div>
            </div>

            <div style="border:1px solid #e2e8f0; border-radius:12px; padding:10px 12px; background:#f8fafc;">
              <div style="font-weight:900; color:#0f172a; font-size:12.5px;">🧠 Higher adoption of adjacent services</div>
              <div style="font-size:12px; color:#64748b; margin-top:4px; line-height:1.5;">Connectivity + security expansion via fit scoring.</div>
            </div>

            <div style="border:1px solid #e2e8f0; border-radius:12px; padding:10px 12px; background:#f8fafc;">
              <div style="font-weight:900; color:#0f172a; font-size:12.5px;">🎯 Better conversion (upsell/cross-sell)</div>
              <div style="font-size:12px; color:#64748b; margin-top:4px; line-height:1.5;">Explainable “why now” drivers improve outreach.</div>
            </div>

            <div style="border:1px solid #e2e8f0; border-radius:12px; padding:10px 12px; background:#f8fafc;">
              <div style="font-weight:900; color:#0f172a; font-size:12.5px;">⚡ Accelerated revenue growth</div>
              <div style="font-size:12px; color:#64748b; margin-top:4px; line-height:1.5;">Faster pipeline progression from existing accounts.</div>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</div>
"""
    return html_out

def _format_account_summary_table_html() -> str:
    """Account Summary Table - Complete HTML for iframe with top alignment and intent keywords"""
    try:
        df = pd.read_excel(ACCOUNT_SUMMARY_PATH, sheet_name="Complete")
    except Exception as e:
        return f"<div style='padding:20px; color:#dc2626;'>Error: {e}</div>"
    
    if df.empty:
        return "<div style='padding:20px; color:#64748b;'>No data available.</div>"
    
    html_out = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      padding: 20px;
      background: #f1f5f9;
    }
    .table-card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.05);
      overflow: hidden;
      border: 1px solid #e2e8f0;
    }
    .table-wrap {
      overflow-x: auto;
      overflow-y: auto;
      max-height: 580px;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      background: white;
      min-width: 1200px;
    }
    .data-table thead th {
      position: sticky;
      top: 0;
      background: #f9fafb;
      padding: 16px;
      text-align: left;
      font-size: 11px;
      font-weight: 800;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 2px solid #edf2f7;
      z-index: 10;
    }
    .data-table tbody tr {
      border-bottom: 1px solid #edf2f7;
      border-left: 4px solid transparent;
    }
    .data-table tbody tr:nth-child(even) {
      background-color: #f8fafc;
    }
    .data-table tbody tr:hover {
      background-color: #f5f3ff !important;
      border-left: 4px solid #7c3aed;
    }
    .data-table td {
      padding: 18px 16px;
      vertical-align: top;  /* TOP ALIGNED */
      color: #0f172a;
      font-size: 12px;
      line-height: 1.5;
    }
    .company-name {
      font-weight: 600;
      font-size: 14px;
      color: #0f172a;
      display: block;
      margin-bottom: 6px;
      line-height: 1.3;
    }
    .tag {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      background: #dbeafe;
      color: #1e40af;
      white-space: nowrap;
      margin: 0 4px 4px 0;
    }
    .pill {
      display: inline-flex;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      border: 1px solid;
      white-space: nowrap;
      margin: 0 4px 4px 0;
    }
    .pill-amber { background: #fef3c7; color: #d97706; border-color: #fbbf24; }
    .pill-green { background: #dcfce7; color: #15803d; border-color: #86efac; }
    .muted {
      font-size: 12px;
      color: #64748b;
      line-height: 1.6;
    }
    /* Intent styling */
    .intent-item {
      font-size: 12px;
      color: #334155;
      line-height: 1.5;
      padding-left: 10px;
      border-left: 2px solid #e9d5ff;
      margin-bottom: 8px;
    }
    .intent-domain {
      font-weight: 700;
      color: #0f172a;
    }
    .intent-score {
      color: #6b21a8;
      font-weight: 700;
      margin-left: 6px;
    }
    .intent-keyword {
      display: block;
      font-size: 11px;
      color: #7c3aed;
      font-style: italic;
      margin-top: 2px;
    }
    .table-wrap::-webkit-scrollbar {
      width: 12px;
      height: 12px;
    }
    .table-wrap::-webkit-scrollbar-track {
      background: #f1f5f9;
      border-radius: 10px;
    }
    .table-wrap::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 10px;
      border: 2px solid #f1f5f9;
    }
    .table-wrap::-webkit-scrollbar-thumb:hover {
      background: #94a3b8;
    }
    </style>
    </head>
    <body>
    <div class="table-card">
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 80px;">ID</th>
              <th style="width: 220px;">Account</th>
              <th style="width: 200px;">Active Products</th>
              <th style="width: 200px;">Growth & Signals</th>
              <th style="width: 380px;">Intent</th>
            </tr>
          </thead>
          <tbody>
    """
    
    for idx, r in df.iterrows():
        acc_id = str(r.get("Account ID", "") or "").strip()
        acc_name = str(r.get("Account Name", "") or "")
        industry = str(r.get("Industry", "") or "")
        fte = str(r.get("FTE Size", "") or "")
        revenue = str(r.get("Revenue Range", "") or "")
        location = str(r.get("City / State", "") or "")
        
        # Products
        renewal = r.get("Renewal_Due_Next_180Days")
        renewal_products = []
        if pd.notna(renewal) and str(renewal).strip() not in ["—", "nan", ""]:
            renewal_products = [p.strip() for p in str(renewal).split(",") if p.strip()]
        
        products = str(r.get("Active Products", "") or "")
        products_html = ""
        if products and products not in ["nan", "—"]:
            tags = []
            for p in products.split(","):
                p_clean = p.strip()
                if not p_clean:
                    continue
                if p_clean in renewal_products:
                    tags.append(f"<span class='pill pill-amber'>* {html.escape(p_clean)}</span>")
                else:
                    tags.append(f"<span class='tag'>{html.escape(p_clean)}</span>")
            products_html = "<div>" + "".join(tags) + "</div>"
        else:
            products_html = "<div class='muted'>—</div>"
        
        # Growth
        tcv_growth = str(r.get("TCV Growth (3Yr)", "") or "")
        yoy_growth = str(r.get("YoY Growth", "") or "")
        signal_tags = []
        if r.get("Acquisition") == "✓ Yes":
            signal_tags.append("<span class='pill pill-green'>✓ Acquisition</span>")
        if r.get("Expansion") == "✓ Yes":
            signal_tags.append("<span class='pill pill-green'>✓ Expansion</span>")
        if r.get("Partnership") == "✓ Yes":
            signal_tags.append("<span class='pill pill-green'>✓ Partnership</span>")
        if r.get("Hiring") == "✓ Yes":
            signal_tags.append("<span class='pill pill-green'>✓ Hiring</span>")
        
        growth_lines = []
        if tcv_growth and tcv_growth not in ["nan", "—", "0%"]:
            growth_lines.append(f"<div class='muted'><strong>TCV:</strong> {html.escape(tcv_growth)}</div>")
        if yoy_growth and yoy_growth not in ["nan", "—", ""]:
            growth_lines.append(f"<div class='muted'><strong>YoY:</strong> {html.escape(yoy_growth)}</div>")
        
        growth_text = "".join(growth_lines) if growth_lines else "<div class='muted'>—</div>"
        signal_text = "".join(signal_tags) if signal_tags else "<span class='muted'>—</span>"
        growth_html = f"{growth_text}<div style='margin-top:6px;'>{signal_text}</div>"
        
        # Intent WITH KEYWORDS
        intent_items = []
        for i in (1, 2, 3):
            dom = r.get(f"Intent Domain {i}")
            score = r.get(f"Score {i}")
            keyword = r.get(f"Keyword {i}")
            
            if pd.notna(dom) and pd.notna(score) and str(dom) not in ["—", "nan", ""]:
                try:
                    score_val = int(float(score))
                except Exception:
                    continue
                
                # Add keyword if available
                kw_html = ""
                if pd.notna(keyword) and str(keyword) not in ["nan", "", "—"]:
                    kw_html = f"<span class='intent-keyword'>→ {html.escape(str(keyword))}</span>"
                
                intent_items.append(
                    f"""
                    <div class="intent-item">
                      <span class="intent-domain">{html.escape(str(dom))}</span>
                      <span class="intent-score">({score_val})</span>
                      {kw_html}
                    </div>
                    """
                )
        
        intent_html = "".join(intent_items) if intent_items else "<div class='muted'>—</div>"
        
        html_out += f"""
          <tr>
            <td>#{html.escape(acc_id)}</td>
            <td>
              <span class="company-name">{html.escape(acc_name)}</span>
              <div class="muted">
                📍 {html.escape(location)}<br>
                👥 {html.escape(fte)}<br>
                🏢 {html.escape(industry)}
              </div>
            </td>
            <td>{products_html}</td>
            <td>{growth_html}</td>
            <td>{intent_html}</td>
          </tr>
        """
    
    html_out += """
          </tbody>
        </table>
      </div>
    </div>
    </body>
    </html>
    """
    return html_out

def _format_prioritization_table_html(df: pd.DataFrame) -> str:
    """Prioritization Table - Self-contained HTML for iframe"""
    if df is None or df.empty:
        return "<!DOCTYPE html><html><body style='padding:20px; color:#64748b; font-family:sans-serif;'>No data available.</body></html>"
    
    DISPLAY_COLS = ["Growth Signals", "Tech Maturity", "Tech Relevancy", 
                    "Product History & Usage", "Est. Potential Spend", 
                    "Intent Signals", "GTM Fit", "Priority Rationale"]
    
    ICON_CHARS = "⭐🟡⚪🟢🔴"
    
   
    def format_cell(content, allow_html=False):
        if not content or str(content).strip() in ["", "nan", "—"]:
            return "<span style='color:#64748b;'>—</span>"

        s = str(content).strip()

        # If this column is allowed to render HTML, return as-is
        if allow_html:
            return s

        ICON_CHARS = "⭐🟡⚪🟢🔴"
        parts = s.split("—", 1)
        if len(parts) == 2:
            score = parts[0].strip().lstrip(ICON_CHARS).strip()
            explain = html.escape(parts[1].strip())
            return (
                f"<div><strong>{html.escape(score)}</strong></div>"
                f"<div style='margin-top:4px; color:#475569; font-size:12px;'>{explain}</div>"
            )

        return f"<strong>{html.escape(s)}</strong>"

    
    html_out = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { 
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #f1f5f9;
  padding: 20px;
}
.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}
.table-scroll {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 580px;
}
.prio-table {
  width: 100%;
  min-width: 1700px;
  border-collapse: collapse;
  background: white;
}
.prio-table thead th {
  position: sticky;
  top: 0;
  background: #f9fafb;
  padding: 16px;
  text-align: left;
  font-size: 11px;
  font-weight: 800;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #edf2f7;
  z-index: 10;
}
.prio-table tbody tr {
  border-bottom: 1px solid #edf2f7;
  border-left: 4px solid transparent;
  transition: all 0.15s;
}
.prio-table tbody tr:nth-child(even) { background-color: #f8fafc; }
.prio-table tbody tr:hover {
  background-color: #f5f3ff !important;
  border-left-color: #7c3aed;
}
.prio-table td {
  padding: 18px 16px;
  vertical-align: top;
  font-size: 12px;
  line-height: 1.55;
  color: #0f172a;
  word-wrap: break-word;
}
.company-name {
  font-weight: 600;
  font-size: 14px;
  color: #0f172a;
  line-height: 1.3;
}
.priority-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 11px;
  border: 1px solid;
  white-space: nowrap;
}
.p-high { background: #dcfce7; color: #15803d; border-color: #86efac; }
.p-medium { background: #fef3c7; color: #d97706; border-color: #fbbf24; }
.p-low { background: #fee2e2; color: #dc2626; border-color: #fca5a5; }
.table-scroll::-webkit-scrollbar { width: 12px; height: 12px; }
.table-scroll::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; }
.table-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; border: 2px solid #f1f5f9; }
.table-scroll::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
</head>
<body>
<div class="table-container">
  <div class="table-scroll">
    <table class="prio-table">
      <thead>
        <tr>
          <th style="width: 70px;">ID</th>
          <th style="width: 200px;">Account Name</th>
          <th style="width: 100px; text-align: center;">Priority</th>
"""
    
    for name in DISPLAY_COLS:
        width = "400px" if name == "Priority Rationale" else "200px"
        html_out += f"          <th style='width: {width};'>{html.escape(name)}</th>\n"
    
    html_out += "        </tr>\n      </thead>\n      <tbody>\n"
    
    for idx, row in df.iterrows():
        pri_raw = str(row.get("Priority", "")).strip()
        pri_text = pri_raw.split()[-1].capitalize() if pri_raw else "Low"
        pill_cls = f"p-{pri_text.lower()}"
        
        acc_id = html.escape(str(row.get("Account ID", "") or "").strip())
        company = html.escape(str(row.get("Company Name", "") or "").strip())
        
        html_out += f"""        <tr>
          <td>{acc_id}</td>
          <td><span class="company-name">{company}</span></td>
          <td style="text-align: center;"><span class="priority-pill {pill_cls}">{pri_text}</span></td>
"""
        
        
        for col in DISPLAY_COLS:
            allow_html = (col == "Priority Rationale")
            html_out += f"          <td>{format_cell(row.get(col, ''), allow_html=allow_html)}</td>\n"

        
        html_out += "        </tr>\n"
    
    html_out += """      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    return html_out

def _format_product_catalog_html() -> str:
    """Format high-density, collapsible product catalog with horizontal metadata"""
    
    # 1. Group products by category (L1)
    catalog_by_cat = {}
    for p in PRODUCT_CATALOG:
        cat = p.get("category", "Uncategorized")
        if cat not in catalog_by_cat:
            catalog_by_cat[cat] = []
        catalog_by_cat[cat].append(p)
    
    styles = """
    <style>
        .cat-container { 
        font-family: 'Inter',-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
        padding: 0px; background: #f8fafc; 
        }

        .shelf { margin-bottom: 8px; }
        
        /* Collapsible Shelf */
        .shelf { 
            margin-bottom: 8px; border: 1px solid #e2e8f0; 
            border-radius: 8px; background: white; overflow: hidden; 
        }
        .shelf-summary { 
            list-style: none; padding: 8px 16px; background: #f8fafc; 
            cursor: pointer; display: flex; justify-content: space-between; 
            align-items: center; border-bottom: 1px solid transparent;
        }
        .shelf[open] .shelf-summary { border-bottom: 1px solid #e2e8f0; }
        .shelf-summary::-webkit-details-marker { display: none; }
        
        .shelf-title { 
            font-size: 11px; font-weight: 800; color: #6b00b8; 
            text-transform: uppercase; letter-spacing: 0.05em; 
            display: flex; align-items: center; gap: 8px;
        }
        
        /* Product Grid */
        .prod-grid { 
            display: grid; grid-template-columns: repeat(4, 1fr); 
            gap: 10px; padding: 12px; background: #fff; 
        }
        
        /* Compact Card Design */
        .prod-card { 
            border: 1px solid #f1f5f9; border-radius: 6px; padding: 10px; 
            display: flex; flex-direction: column; background: #fff; 
            min-height: 140px; transition: border-color 0.2s;
            overflow: hidden; /* Prevent wide content from breaking grid */
        }
        .prod-card:hover { border-color: #6b00b8; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        
        .prod-name { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 3px; }
        
        .prod-desc { 
            font-size: 10px; color: #64748b; line-height: 1.3; 
            margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; 
            -webkit-box-orient: vertical; overflow: hidden; height: 26px;
        }
        .card-link-row{
        margin-top: 6px;
        }
        .p-link{
        color:#0d00ff;
        font-weight:700;
        text-decoration: none;
        }
        .p-link:hover{
        text-decoration: underline;
        }

        
        /* Metadata Horizontal Layout */
        .meta-stack { display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px; }
        .meta-item { font-size: 9px; display: flex; align-items: flex-start; }
        .meta-label { 
            font-weight: 700; color: #94a3b8; text-transform: uppercase; 
            width: 50px; flex-shrink: 0; font-size: 8px; margin-top: 1px;
        }
        .meta-val { 
            color: #475569; 
            text-transform: capitalize; 
            line-height: 1.2; 
            display: inline-block; /* Allow wrapping for long industry lists */
        }
        
        /* Footer row */
        .card-ft { 
            display: flex; justify-content: space-between; align-items: center; 
            margin-top: auto; padding-top: 6px; border-top: 1px solid #f8fafc; 
        }
        .tag-wrap { display: flex; gap: 4px; flex-wrap: wrap; }
        .p-tag { 
            font-size: 8px; background: #f5f3ff; color: #6b00b8; 
            padding: 1px 5px; border-radius: 3px; font-weight: 700; border: 1px solid #ddd6fe;
        }
        .p-link { font-size: 9px; color: #0d00ff; text-decoration: none; font-weight: 700; }
        
        .empty-box { 
            display: flex; align-items: center; justify-content: center; 
            border: 1px dashed #e2e8f0; border-radius: 6px; color: #cbd5e1; 
        }
    </style>
    """

    html_out = f"{styles}<div class='cat-container'>"

    for cat_name, products in catalog_by_cat.items():
        icon = CATEGORY_ICONS.get(cat_name, "📦")
        # Keep first category open by default
        is_open = "open" if cat_name == list(catalog_by_cat.keys())[0] else ""
        
        html_out += f"""
        <details class="shelf" {is_open}>
            <summary class="shelf-summary">
                <div class="shelf-title">{icon} {html.escape(cat_name)}</div>
                <span style="font-size: 10px; color: #94a3b8;">{len(products)} Products</span>
            </summary>
            <div class="prod-grid">
        """

        for i in range(max(len(products), 4)):
            if i < len(products):
                p = products[i]
                chips = "".join([
                    f"<span class='p-tag'>{label}</span>"
                    for flag, label in CAP_FLAG_MAP.items() if p["flags"].get(flag)
                ])
                
                # Use .title() for proper casing of industries/segments
                html_out += f"""
                <div class="prod-card">
                    <div class="prod-name">{html.escape(p['sub'])}</div>
                    <div class="prod-desc">{html.escape(p['desc'])}</div>
                    
                    <div class="meta-stack">
                        <div class="meta-item">
                            <span class="meta-label">Segment:</span>
                            <span class="meta-val">{html.escape(p['segments'].title())}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Industry:</span>
                            <span class="meta-val">{html.escape(p['industries'].title())}</span>
                        </div>
                    </div>

                    <div class="card-ft">
                        <div class="tag-wrap">{chips}</div>
                        </div>
                        <div class="card-link-row">
                        <a href="{p['url']}" target="_blank" class="p-link">Details →</a>
                    </div>

                </div>
                """
            else:
                html_out += "<div class='prod-card empty-box'>—</div>"
        
        html_out += "</div></details>"

    html_out += "</div>"
    return html_out

def _format_recommendations_table_html() -> str:
    """Recommendations Table - Complete HTML for iframe with proper HTML rendering"""
    try:
        reco_df = pd.read_excel(RECOMMENDATIONS_PATH, sheet_name="Recommendations", header=3)
    except Exception as e:
        return f"<div style='padding:20px; color:#dc2626;'>Error: {e}</div>"
    
    if reco_df.empty:
        return "<div style='padding:20px; color:#64748b;'>No data available.</div>"
    
    account_ids = reco_df["Account ID"].unique()
    
    html_out = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      margin: 0;
      padding: 20px;
      background: #f1f5f9;
    }
    .table-card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.05);
      overflow: hidden;
      border: 1px solid #e2e8f0;
    }
    .table-wrap {
      overflow-x: auto;
      overflow-y: auto;
      max-height: 580px;
    }
    .reco-table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      background: white;
      min-width: 1400px;
    }
    .reco-table thead th {
      position: sticky;
      top: 0;
      background: #f9fafb;
      padding: 16px;
      text-align: left;
      font-size: 11px;
      font-weight: 800;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 2px solid #edf2f7;
      z-index: 10;
    }
    .reco-table tbody tr {
      border-bottom: 1px solid #edf2f7;
      border-left: 4px solid transparent;
    }
    .reco-table tbody tr:nth-child(even) {
      background-color: #f8fafc;
    }
    .reco-table tbody tr:hover {
      background-color: #f5f3ff !important;
      border-left: 4px solid #7c3aed;
    }
    .reco-table td {
      padding: 20px 16px;
      vertical-align: top;
      color: #0f172a;
      font-size: 12px;
      line-height: 1.5;
    }
    .company-name {
      font-weight: 600;
      color: #0f172a;
      font-size: 14px;
      display: block;
      margin-bottom: 6px;
      line-height: 1.3;
    }
    .priority-pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 6px 12px;
      border-radius: 999px;
      font-weight: 800;
      font-size: 11px;
      border: 1px solid;
      white-space: nowrap;
    }
    .p-high { background: #dcfce7; color: #15803d; border-color: #86efac; }
    .p-medium { background: #fef3c7; color: #d97706; border-color: #fbbf24; }
    .p-low { background: #fee2e2; color: #dc2626; border-color: #fca5a5; }
    .muted {
      font-size: 12px;
      color: #64748b;
      line-height: 1.6;
    }
    .trigger-details {
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      background: white;
      margin-top: 8px;
    }
    .trigger-summary {
      padding: 8px 12px;
      font-size: 12px;
      font-weight: 600;
      color: #475569;
      cursor: pointer;
      list-style: none;
      display: flex;
      align-items: center;
    }
    .trigger-summary::-webkit-details-marker { display: none; }
    .trigger-summary::before {
      content: '→';
      margin-right: 8px;
      color: #a855f7;
      transition: 0.2s;
    }
    .trigger-details[open] .trigger-summary::before {
      transform: rotate(90deg);
    }
    .trigger-details[open] .trigger-summary {
      border-bottom: 1px solid #f1f5f9;
    }
    .trigger-content {
      padding: 12px;
      font-size: 11px;
      color: #334155;
      line-height: 1.6;
      background: #fafafa;
      border-radius: 0 0 8px 8px;
    }
    /* Render HTML lists properly */
    .trigger-content ul {
      margin: 8px 0;
      padding-left: 20px;
    }
    .trigger-content li {
      margin-bottom: 6px;
      line-height: 1.5;
    }
    .table-wrap::-webkit-scrollbar {
      width: 12px;
      height: 12px;
    }
    .table-wrap::-webkit-scrollbar-track {
      background: #f1f5f9;
      border-radius: 10px;
    }
    .table-wrap::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 10px;
      border: 2px solid #f1f5f9;
    }
    .table-wrap::-webkit-scrollbar-thumb:hover {
      background: #94a3b8;
    }
    </style>
    </head>
    <body>
    <div class="table-card">
      <div class="table-wrap">
        <table class="reco-table">
          <thead>
            <tr>
              <th style="width: 70px;">ID</th>
              <th style="width: 180px;">Account</th>
              <th style="width: 90px; text-align: center;">Priority</th>
              <th style="min-width: 280px;">Recommendation 1</th>
              <th style="min-width: 280px;">Recommendation 2</th>
              <th style="min-width: 280px;">Recommendation 3</th>
            </tr>
          </thead>
          <tbody>
    """
    
    for acc_id in account_ids:
        rows = reco_df[reco_df["Account ID"] == acc_id].reset_index(drop=True)
        main = rows.iloc[0]
        
        pri_raw = str(main.get("Priority", "")).strip()
        pri_text = pri_raw.split()[-1].capitalize() if pri_raw else "Low"
        pill_cls = f"p-{pri_text.lower()}"
        
        html_out += f"""
        <tr>
          <td>#{acc_id}</td>
          <td>
            <span class="company-name">{html.escape(str(main.get('Account Name', '')))}</span>
            <div class="muted">
              📍 {html.escape(str(main.get('City / State', '')))}<br>
              👥 {html.escape(str(main.get('FTE Size', '')))}<br>
              🏢 {html.escape(str(main.get('Industry', '')))}
            </div>
          </td>
          <td style="text-align: center;">
            <span class="priority-pill {pill_cls}">{pri_text}</span>
          </td>
        """
        
        for i in range(3):
            if i < len(rows):
                r = rows.iloc[i]
                # DON'T escape the rationale - it contains HTML that should render
                rationale_raw = str(r.get('Insight & Rationale', ''))
                
                html_out += f"""
                <td>
                  <div style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;">
                    {html.escape(str(r.get('Category', '')))}
                  </div>
                  <div style="font-weight: 700; color: #6b21a8; font-size: 14px; margin-bottom: 6px;">
                    {html.escape(str(r.get('Product', '')))}
                  </div>
                  <div style="font-size: 11px; background: #f3e8ff; color: #6b21a8; padding: 3px 8px; border-radius: 50px; display: inline-block; margin-bottom: 8px; font-weight: 700;">
                    {html.escape(str(r.get('Fit Score', '')))} Fit
                  </div>
                  <details class="trigger-details">
                    <summary class="trigger-summary">Why this reco?</summary>
                    <div class="trigger-content">{rationale_raw}</div>
                  </details>
                </td>
                """
            else:
                html_out += "<td style='color: #cbd5e1; text-align: center;'>—</td>"
        
        html_out += "</tr>"
    
    html_out += """
          </tbody>
        </table>
      </div>
    </div>
    </body>
    </html>
    """
    return html_out

# --------------------------------------------------
# TABS AT THE TOP (BEFORE TITLE)
# --------------------------------------------------
tab1, tab2 = st.tabs(["📊 Data Ingestion & Enrichment", "🎯 Scoring & Recommendation"])

# --------------------------------------------------
# TAB 1: DATA INGESTION & ENRICHMENT - WIP PLACEHOLDER
# --------------------------------------------------
with tab1:

    # DataEngineerApp().run()
    # DataEngineerApp(render_sidebar=False, render_top_nav=False, key_prefix="ingest").run()

    st.markdown("""
    <div class="page-title">⚙️ Ingestion & Enrichment Studio</div>
    <div class="page-desc">   
    This console is designed to provide transparency into the enrichment pipeline by displaying agent execution status, extracted signals, and validation outcomes, ensuring accuracy and explainability before downstream prioritization.
    </div>
    """, unsafe_allow_html=True)


    # RUN/STOP BUTTONS
    ctrl = st.columns([1, 1, 8])
    with ctrl[0]:
        run_clicked = st.button("Run Process", key="run_btn_main_data", type="primary", use_container_width=True)
    with ctrl[1]:
        stop_clicked = st.button("Stop Process", key="stop_btn_main_data", use_container_width=True)

    if stop_clicked:
        st.session_state.stop_process = True
        run_clicked = False

    if run_clicked:
        st.session_state.run_process = True
        st.session_state.stop_process = False
        st.session_state.step_done = {}
        st.session_state.log_html = {}
        st.session_state.task_running = {}
        if "task_running" not in st.session_state:
            st.session_state.task_running = {}

        st.session_state.current_step = 1

    st.markdown("---")

    DataEngineerApp().run()


# --------------------------------------------------
# TAB 2: SCORING & RECOMMENDATION - MAIN CONTENT
# --------------------------------------------------
with tab2:
    # PAGE TITLE (inside tab2)
    st.markdown("""
    <div class="page-title">🎯 Lead Prioritization & Product Recommendation Studio</div>
    <div class="page-desc">
    Using agentic reasoning, the platform evaluates growth signals, intent patterns, 
    technographic fit, and industry context to assign priority tiers and generate explainable, 
    account-specific product recommendations aligned to GTM objectives.           
    </div>
    """, unsafe_allow_html=True)
    
    # RUN/STOP BUTTONS
    ctrl = st.columns([1, 1, 8])
    with ctrl[0]:
        run_clicked = st.button("Run Process", key="run_btn_main", type="primary", use_container_width=True)
    with ctrl[1]:
        stop_clicked = st.button("Stop Process", key="stop_btn_main", use_container_width=True)

    if stop_clicked:
        st.session_state.stop_process = True
        run_clicked = False

    if run_clicked:
        st.session_state.run_process = True
        st.session_state.stop_process = False
        st.session_state.step_done = {}
        st.session_state.log_html = {}
        st.session_state.current_step = 1

    st.markdown("---")
    
    # Overall Progress Bar Placeholder
    # overall_progress_ph = st.empty()
    
    # ALL 6 TASK CARDS (Steps 1-6)
    for t in ALL_TASKS:
        key = t["key"]
        step_num = t["step_num"]
        done_key = f"step_{step_num}_done"
        
        # Check if done
        done = st.session_state.step_done.get(done_key, False)
        prev_done = st.session_state.step_done.get(f"step_{step_num - 1}_done", False) if step_num > 1 else True
        should_run = (
            st.session_state.get("run_process")
            and not st.session_state.get("stop_process")
            and not done
            and prev_done
        )
        
        # status_text = "Complete" if done else ("Running" if should_run else "Pending")
        # status_color = "#2db24a" if done else ("#f0c040" if should_run else "#999999")


        if done:
            status_text = "Complete"
            status_color = "#2db24a"
        elif st.session_state.task_running.get(key, False):
            status_text = "Running"
            status_color = "#f0c040"
        else:
            status_text = "Pending"
            status_color = "#999999"

        
        # Card open
        st.markdown(f"<div class='task-card' id='task-{key}'>", unsafe_allow_html=True)
        
        # Header
        header_ph = st.empty()
        step_prefix = f"<span class='step-label'>STEP {step_num} — </span>"


        header_ph.markdown(
        f"<div class='task-card-header'><div class='task-name'>"
        f"{html.escape(t['name'])} "
        f"{status_dot(status_color,12)}"
        f"<span style='color:{status_color};'>— {status_text}</span>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

        
        # Progress bar placeholder
        progress_ph = st.empty()
        
        # Log placeholder
        log_ph = st.empty()
        if f"log_{key}" in st.session_state.log_html:
            log_ph.markdown(st.session_state.log_html[f"log_{key}"], unsafe_allow_html=True)
        else:
            log_ph.markdown("<div class='agent-log-box agent-log-empty'>Background agent pipeline will appear here once the run starts.</div>", unsafe_allow_html=True)
        
        # Expander for results
        exp_labels = {
            "load_data": "📊 View Account Summary",
            "business_context": "📋 View Business Context Analysis",
            "category_weights": "⚖️ View Category Weights",
            "prioritization_table": "🎯 View Prioritization Results",
            "product_catalog": "📦 View Product Catalogue",
            "recommender_agent": "🎯 View Recommendations"
        }
        exp_label = exp_labels.get(key, "View Details")
        
        exp = st.expander(exp_label, expanded=False)
        with exp:
            results_ph = st.empty()
            
            # Show cached results if available
            if done and f"output_{key}" in st.session_state:
                with results_ph.container():
                    if key == "load_data":
                        st.markdown("""<div style="
                        margin-bottom:12px;
                        padding:10px 14px;
                        border-radius:10px;
                        background:#fff7ed;
                        border:1px solid #fed7aa;
                        font-size:12.5px;
                        color:#9a3412;
                        font-weight:600;
                    ">
                        🔔 <strong>Renewal Insight:</strong>
                        Accounts with renewals due in the next <strong>180 days</strong> are highlighted — 
                        these represent <strong>high-confidence retention and upsell opportunities</strong>.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                        components.html(st.session_state[f"output_{key}"], height=700, scrolling=True)
                        
                    elif key == "business_context":
                        components.html(st.session_state[f"output_{key}"], height=800, scrolling=True)
                        
                    elif key == "category_weights":
                        components.html(st.session_state[f"output_{key}"],height=900, scrolling=True)

                        
                    elif key == "prioritization_table":
                        import streamlit.components.v1 as components
                        components.html(_format_prioritization_table_html(st.session_state["lead_prioritization_df"]), height=700, scrolling=True)
                        
                        csv = st.session_state["lead_prioritization_df"].to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "Download Prioritization CSV",
                            data=csv,
                            file_name="prioritization_results.csv",
                            mime="text/csv",
                            key=f"download_{key}_cached",
                        )
                        
                    elif key == "product_catalog":
                        components.html(st.session_state[f"output_{key}"], height=800, scrolling=True)

                        
                    elif key == "recommender_agent":
                        st.markdown("""<div style="
                            margin-bottom:12px;
                            padding:10px 14px;
                            border-radius:10px;
                            background:#eef2ff;
                            border:1px solid #c7d2fe;
                            font-size:12.5px;
                            color:#1e3a8a;
                            font-weight:600;
                        ">
                            🔎 <strong>Recommendation Confidence:</strong>
                            All recommended products meet a minimum <strong>LLM confidence threshold</strong> to ensure relevance and actionability.
                        </div>""", unsafe_allow_html=True)
                        components.html(st.session_state[f"output_{key}"], height=700, scrolling=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        with open(RECOMMENDATIONS_PATH, "rb") as f:
                            rec_bytes = f.read()
                        st.download_button(
                            label="⬇️  Download Recommendations (Excel)",
                            data=rec_bytes,
                            file_name="recommendations.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"dl_recommendations_cached",
                        )
            else:
                results_ph.markdown("<div class='output-box'>(no results yet)</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Store placeholders for animation
        if "placeholders" not in st.session_state:
            st.session_state.placeholders = {}
        st.session_state.placeholders[key] = {
            "header_ph": header_ph,
            "log_ph": log_ph,
            "results_ph": results_ph,
            "progress_ph": progress_ph,
        }


# --------------------------------------------------
# MAIN EXECUTION LOGIC
# --------------------------------------------------

# Check if run button was clicked
if run_clicked:
    
    # Run ALL tasks (steps 1-6)
    tasks_to_run = ALL_TASKS
    total_tasks = len(tasks_to_run)
    
    # Update overall progress
    # overall_progress_ph.progress(0, text="Overall Pipeline Progress")
    
    # Execute each task
    for idx, task in enumerate(tasks_to_run):
        if st.session_state.get("stop_process"):
            st.warning("Pipeline stopped by user.")
            st.session_state.task_running[task["key"]] = False
            break
        
        key = task["key"]
        step_num = task["step_num"]
        done_key = f"step_{step_num}_done"
        st.session_state.current_step = step_num
        st.session_state.task_running[key] = True


        # Skip if already done
        if st.session_state.step_done.get(done_key, False):
            continue
        
        # Check if previous step is done
        if step_num > 1:
            prev_done_key = f"step_{step_num - 1}_done"
            if not st.session_state.step_done.get(prev_done_key, False):
                continue
        
        # Get placeholders
        ph = st.session_state.placeholders.get(key, {})
        header_ph = ph.get("header_ph")
        log_ph = ph.get("log_ph")
        results_ph = ph.get("results_ph")
        progress_ph = ph.get("progress_ph")
        
        # Update header to "Running"
        if header_ph is not None:
            step_prefix = f"<span class='step-label'>STEP {step_num} — </span>"
            # Update header to "Running" (yellow)
            header_ph.markdown(
                f"<div class='task-card-header'><div class='task-name'>{step_prefix}{html.escape(task['name'])} "
                f"{status_dot('#f0c040', 12)}<span style='color:#f0c040;'>— Running</span></div></div>",
                unsafe_allow_html=True,
            )


        # Animate logs
        agent_steps = STEP_LOGS.get(key, [])

        # STEP header line
        ts0 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_html = (
            f"<div class='agent-log-line title'>"
            f"{ts0} — STEP {step_num} — {html.escape(task['name'])}"
            f"</div>"
        )

        total_lines = len(agent_steps)

        for s_idx, step_text in enumerate(agent_steps, start=1):
            if st.session_state.get("stop_process"):
                break

            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_html += (
                f"<div class='agent-log-line info'>"
                f"<span class='source-tag'>{ts}</span> {step_text}"
                f"</div>"
            )

            box_html = f"<div class='agent-log-box'>{log_html}</div>"

            if log_ph is not None:
                log_ph.markdown(box_html, unsafe_allow_html=True)

            st.session_state.log_html[f"log_{key}"] = box_html

            # progress update stays same...
            pct = int((s_idx / max(total_lines, 1)) * 100)
            if progress_ph is not None:
                progress_ph.markdown(
                    f"<div style='width:100%'>"
                    f"<div style='margin-bottom:6px; font-weight:600; font-size: 13px; color: #333;'>"
                    f"Executing... {pct}%"
                    f"</div>"
                    f"<progress value='{pct}' max='100' class='progress-inline'></progress>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            time.sleep(SIMULATE_TIME_PER_STEP)


        
        if st.session_state.get("stop_process"):
            if progress_ph is not None:
                progress_ph.markdown(
                    "<div style='padding:8px;'><strong>Task interrupted by user.</strong></div>",
                    unsafe_allow_html=True,
                )
            if header_ph is not None:
                step_prefix = f"<span class='step-label'>STEP {step_num} — </span>"
                header_ph.markdown(
                    f"<div class='task-card-header'><div class='task-name'>{step_prefix}{html.escape(task['name'])} "
                    f"{status_dot('#999999', 12)}<span style='color:#999;'>— Interrupted</span></div></div>",
                    unsafe_allow_html=True,
                )
            break
        
        # Generate outputs based on task key
        if key == "load_data":
            out_html = _format_account_summary_table_html()
            
        elif key == "business_context":
            out_html = _business_context_html_from_text(st.session_state.business_context_text)
            
        elif key == "category_weights":
            out_html = _format_weights_to_html()
            
        elif key == "prioritization_table":
            header_html = """
<div class="output-box">
    <div class="kv">
        <span class="label">Lead Prioritization — Explanatory Data</span>
        <div class="small-muted">
            The weighted scoring framework has generated final priority segments and scores.
        </div>
    </div>
</div>
"""
            table_html = _format_prioritization_table_html(st.session_state["lead_prioritization_df"])
            out_html = header_html + table_html
            
        elif key == "product_catalog":
            out_html = _format_product_catalog_html()
            
        elif key == "recommender_agent":
            out_html = _format_recommendations_table_html()
            
        else:
            out_html = "<div class='output-box'>(no output)</div>"
        
        # Cache output
        st.session_state[f"output_{key}"] = out_html
        
        # Mark as done
        st.session_state.step_done[done_key] = True
        st.session_state.task_running[key] = False
        st.session_state.current_step = step_num + 1
        # Update header to "Done"
        if header_ph is not None:
            step_prefix = f"<span class='step-label'>STEP {step_num} — </span>"
            header_ph.markdown(
                f"<div class='task-card-header'><div class='task-name'>{step_prefix}{html.escape(task['name'])} "
                f"{status_dot('#2db24a', 12)}<span style='color:#2db24a;'>— Complete</span></div></div>",
                unsafe_allow_html=True,
            )
        
        # Clear progress bar
        if progress_ph is not None:
            progress_ph.empty()
        
        # Render results in expander
        if results_ph is not None:
            with results_ph.container():
                if key == "load_data":
                    st.markdown("""<div style="
                    margin-bottom:12px;
                    padding:10px 14px;
                    border-radius:10px;
                    background:#fff7ed;
                    border:1px solid #fed7aa;
                    font-size:12.5px;
                    color:#9a3412;
                    font-weight:600;
                ">
                    🔔 <strong>Renewal Insight:</strong>
                    Accounts with renewals due in the next <strong>180 days</strong> are highlighted — 
                    these represent <strong>high-confidence retention and upsell opportunities</strong>.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                    components.html(_format_account_summary_table_html(), height=700, scrolling=True)
                    
                elif key == "business_context":
                    components.html(out_html, height=600, scrolling=True)
                    
                elif key == "category_weights":
                    # st.markdown(out_html, unsafe_allow_html=True)
                    components.html(out_html, height=900, scrolling=True)
                    
                elif key == "prioritization_table":
                    components.html(_format_prioritization_table_html(st.session_state["lead_prioritization_df"]), height=700, scrolling=True)

                    
                    csv = st.session_state["lead_prioritization_df"].to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download Prioritization CSV",
                        data=csv,
                        file_name="prioritization_results.csv",
                        mime="text/csv",
                        key=f"download_{key}_exec",
                    )
                    
                elif key == "product_catalog":
                    out_html = _format_product_catalog_html()
                    components.html(out_html, height=800, scrolling=True)
                    
                elif key == "recommender_agent":
                    st.markdown("""<div style="
                            margin-bottom:12px;
                            padding:10px 14px;
                            border-radius:10px;
                            background:#eef2ff;
                            border:1px solid #c7d2fe;
                            font-size:12.5px;
                            color:#1e3a8a;
                            font-weight:600;
                        ">
                            🔎 <strong>Recommendation Confidence:</strong>
                            All recommended products meet a minimum <strong>LLM confidence threshold</strong> to ensure relevance and actionability.
                        </div>""", unsafe_allow_html=True)
                    components.html(_format_recommendations_table_html(), height=700, scrolling=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    with open(RECOMMENDATIONS_PATH, "rb") as f:
                        rec_bytes = f.read()
                    st.download_button(
                        label="⬇️  Download Recommendations (Excel)",
                        data=rec_bytes,
                        file_name="recommendations.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_recommendations_exec",
                    )
        
        # Update overall progress
        # progress_value = int(((idx + 1) / total_tasks) * 100)
        # overall_progress_ph.progress(progress_value, text="Overall Pipeline Progress")
    
    # Clear overall progress when done
    # overall_progress_ph.empty()
    
    # Show success message if not stopped
    if not st.session_state.get("stop_process"):
        st.success("✅ Lead prioritization and product recommendation pipeline completed successfully!")