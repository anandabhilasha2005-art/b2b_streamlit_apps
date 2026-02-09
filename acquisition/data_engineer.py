# data_engineer.py
# Agentic-flavoured pipeline with live background logs + enrichment details

import streamlit as st
import pandas as pd
import time
from typing import Dict, List
import html
import datetime
import re
import os

# --- IMPORTS FOR PAGE RENDERING ---
try:
    from lead_scoring import lead_scoring_page
except ImportError:
    def lead_scoring_page(df):
        st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
        st.warning("🚨 Lead Scoring page module not found. Displaying placeholder.")
        st.markdown("</div>", unsafe_allow_html=True)

try:
    from product_reco import product_recommendation_page
except ImportError:
    def product_recommendation_page(df):
        st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
        st.warning("🚨 Product Recommendation page module not found. Displaying placeholder.")
        st.markdown("</div>", unsafe_allow_html=True)

try:
    from insight_studio import insight_studio_page
except ImportError:
    def insight_studio_page():
        st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
        st.error("🚨 Insight Studio page module not found. Displaying placeholder.")
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# Small UI helpers & style
# ---------------------------
def status_dot(color: str = "#ccc", size: int = 12) -> str:
    """Returns HTML for a simple colored status dot."""
    return f"<div style='width:{size}px; height:{size}px; border-radius:50%; background:{color}; display:inline-block; margin-right:12px;'></div>"


# --- VIEW SWITCHER CALLBACKS ---
def _switch_to_insights():
    """Callback to set the main view to Insight Studio."""
    st.session_state.last_selected_company = st.session_state.get("company_input")
    st.session_state.main_view = "insight"


def _switch_to_lead():
    """Callback to set the main view back to Lead Management."""
    st.session_state.last_selected_company = st.session_state.get("company_input")
    st.session_state.main_view = "lead"


def _clear_right_side():
    """Callback to reset the main panel when the company changes."""

    keep = {
    # Core app
    "company_input",
    "last_selected_company",
    "placeholders",
    "scope",
    "logged_in",
    "role",
    "username",
    "uploaded_df",
    "main_view",

    # Insight Studio
    "insight_scope",
    "insight_content_type",

    # Lead Scoring (VERY IMPORTANT)
    "lead_placeholders",
    "lead_cached",
    "lead_run_id",
    "lead_stop_requested",
    "lead_ctx_text",
    "lead_list_name",
    "lead_prioritization_df",

    # Pipeline continuity
    "pipeline_company",
}

    # st.session_state["last_selected_company"] = st.session_state.get("company_input")
    if "company_input" in st.session_state and st.session_state.company_input:
        st.session_state["last_selected_company"] = st.session_state.company_input

    for k in list(st.session_state.keys()):
        if k not in keep:
            try:
                del st.session_state[k]
            except Exception:
                pass
    st.session_state["placeholders"] = {}
    st.session_state["stop_requested"] = False
    # reset run flags
    st.session_state["pipeline_has_run"] = False
    st.session_state["detailed_logs_list"] = []


# --- NEW FUNCTION FOR INSIGHT STUDIO SIDEBAR INPUTS ---
def _handle_insight_generation():
    """Sets a flag to tell insight_studio.py to generate content."""
    st.session_state.run_insight_generation = True


def _reset_company_on_content_change():
    st.session_state.company_input_insight = ""


def _render_insight_sidebar_inputs():
    """Renders the dynamic inputs for the Insight Studio view in the sidebar."""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='scope-title'>Insight Scope</div>", unsafe_allow_html=True)

    st.session_state.insight_scope = st.radio(
        "Select Scope",
        ["Chat", "Sales Intelligence Report"],
        index=0 if st.session_state.insight_scope == "Chat" else 1,
        key="insight_mode_radio",
        label_visibility="visible"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.session_state.pipeline_ran = True
    if st.session_state.insight_scope == "Sales Intelligence Report":
        company_name_for_insight = (
            st.session_state.get("company_input")
            or st.session_state.get("last_selected_company")
            or ""
        )
        st.text_input(
            "Target Company",
            key="company_input_insight",
            value=company_name_for_insight,
            disabled=False,
            help="To change the company, switch back to Lead Management."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='scope-title'>Content Type</div>", unsafe_allow_html=True)

        st.session_state.insight_content_type = st.radio(
            "Select Content Type",
            ["Scouting Report", "Seller Pitch", "Personalized Email"],
            index=["Scouting Report", "Seller Pitch", "Personalized Email"].index(
                st.session_state.insight_content_type
            )
            if st.session_state.insight_content_type in
               ["Scouting Report", "Seller Pitch", "Personalized Email"]
            else 0,
            key="insight_content_type_radio",
            on_change=_reset_company_on_content_change,
            label_visibility="collapsed"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.button(
        "Generate",
        key="generate_insight_button",
        type="primary",
        use_container_width=True,
        on_click=_handle_insight_generation,
    )


# --- FULL CSS (unchanged from your file) ---
_CSS = """
<style>

/* --- Make whole page white and tidy --- */
.stApp {
    background-color: #ffffff;
}

/* main block container adjustments */
.block-container {
    padding: 1.5rem 1.5rem 2rem 1.5rem !important;
}

/* main-panel wrapper (will contain the large white area) */
.main-panel {
    background: #ffffff;
    border-radius: 12px;
    padding: 18px;
    box-shadow: none;
    border: 1px solid transparent;
}

/* description paragraph inside main-panel (left aligned) */
.main-panel .panel-desc {
    text-align: left;
    color: #555;
    font-size: 1.02rem;
    line-height: 1.45;
    margin-top: 6px;
    margin-bottom: 14px;
}

/* Highlighted (expanded) task card gets subtle grey */
.task-card.highlighted {
    background: #f6f7f9 !important;
    border: 1px solid #e6e7ea !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

/* Default task card remains white with soft border */
.task-card {
    background:#ffffff;
    border:1px solid #eef0f2;
    border-radius:10px;
    padding:12px 16px;
    margin-bottom:12px;
    transition: all 120ms ease-in-out;
}
.task-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.03);
}

/* ================================
   Sidebar styling + header + user
   ================================ */

/* Sidebar container */
[data-testid="stSidebar"] {
    border-right: 1px solid #e6e6e6;
    width: 400px !important;
    min-width: 400px !important;
}

/* Full-height inner wrapper with light grey gradient */
[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 1.2rem 1rem 1rem 1rem;
    background: linear-gradient(
        to bottom,
        #f7f7f9 0%,
        #f7f7f9 60%,
        #f1f1f4 60%,
        #f1f1f4 100%
    );
}

.sidebar-spacer {
    flex-grow: 1;
}

/* Accenture logo + stacked title */
.sidebar-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
}

.sidebar-logo-img {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.sidebar-logo-img img {
    width: 32px;
    height: auto;
}

.sidebar-title-block {
    display: flex;
    flex-direction: column;
    font-weight: 800;
    color: #18181b;
    font-size: 1.02rem;
    line-height: 1.2;
}

/* tweak font size of stacked title */
.sidebar-title-block span {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: #18181b !important;
    line-height: 1.2;
    letter-spacing: -0.3px;
}

/* Small purple section label */
.scope-title {
    color: #6b00b8;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.01em;
}

/* Logged-in user inline row with avatar icon */
.sidebar-user-inline {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-top: 6px;
}

.sidebar-user-avatar-inline {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #f3ecff;
    border: 1px solid #d3c3ff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    color: #8b6cff;
}

.sidebar-user-text-inline {
    display: flex;
    flex-direction: column;
}

.sidebar-user-name-inline {
    font-weight: 600;
    color: #6b00b8;
    font-size: 0.9rem;
}

.sidebar-user-name-inline span {
    font-weight: 700;
}

.sidebar-user-role-inline {
    color: #666;
    font-size: 0.85rem;
    margin-top: 2px;
}

/* ========= LOGOUT BUTTON (CENTER) ========= */
.sidebar-logout-wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
    margin-top: 10px;
}
.sidebar-logout-wrapper button {
    min-width: 120px;
    display: inline-block;
    margin: 0 auto;
}

/* =======================
   Selectbox styling
   ======================= */

[data-testid="stSelectbox"] > div:first-child,
.stSelectbox > div,
div[role="combobox"],
div[aria-haspopup="listbox"] {
    background: #ffffff !important;
    border: 1px solid #f1dff6 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    box-shadow: 0 2px 8px rgba(107,0,184,0.04) !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}
[data-testid="stSelectbox"] > div:first-child span,
.stSelectbox > div span,
div[role="combobox"] span,
div[aria-haspopup="listbox"] span {
    color: #222 !important;
    font-weight: 600 !important;
}

/* =======================
   Purple Labels
   ======================= */

[data-testid="stSidebar"] div[data-testid="stTextInput"] > label {
    color: #6b00b8 !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

/* Text input styling */
div[data-testid="stTextInput"] input {
    background-color: #ffffff !important;
    border: 1px solid #dcdcdc !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
    color: #222 !important;
}

/* Purple Select Scope label */
[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    color: #6b00b8 !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

/* --- Sidebar: scope radio custom cards --- */
[data-testid="stSidebar"] [data-testid="stRadio"] {
    width: 100%;
    display: block;
    margin-top: 8px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
    display: flex !important;
    flex-direction: column;
    gap: 10px;
    margin-top: 6px;
}

/* white background + same width for all three options */
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label {
    display: flex !important;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 10px;
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    cursor: pointer;
    font-weight: 600;
    transition: 0.12s ease-in-out;
    color: #333 !important;
    width: 100%;
    box-sizing: border-box;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:hover {
    background: #f9fafb !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label[aria-checked="true"] {
    background: #ffffff !important;
    border: 1px solid rgba(107,0,184,0.6) !important;
    box-shadow: 0 0 0 1px rgba(107,0,184,0.25) !important;
    color: #4a0070 !important;
    transform: translateY(-1px);
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label[aria-checked="true"] input[type="radio"]::after {
    background: #4a0070 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] input[type="radio"] {
    margin-right: 8px !important;
}

/* =======================
   Expander header
   ======================= */

[data-testid="stExpander"] {
    border: none;
    margin-top: 10px;
}
[data-testid="stExpander"] > summary {
    background: #f5f7f9;
    padding: 8px 14px;
    border-radius: 8px;
    font-weight: 600;
    color: #333;
}
[data-testid="stExpander"] > summary:hover {
    background: #eef2f6;
}

/* =======================
   Output boxes
   ======================= */

.output-box {
    background: #ffffff;
    border: 1px solid #eef0f2;
    border-radius: 8px;
    padding:12px;
    font-size:14px;
    color:#111;
}
.kv {
    margin-bottom:10px;
    padding-bottom:10px;
    border-bottom: 1px solid #eee;
}
.kv:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}
.kv .label {
    display: block;
    font-weight: 600;
    margin-bottom: 5px;
    font-size: 14px;
    color: #222;
}
.kv a {
    color: #6b00b8;
    text-decoration: none;
}
.kv a:hover {
    text-decoration: underline;
}

/* header/title */
.header-title {
    color:#2e2e2e;
    font-weight:800;
    margin:0;
    font-size:28px;
}

/* Progress bar inline */
.progress-inline {
    width: 100%;
    height: 8px;
    border-radius: 4px;
    background: #e6e6e6;
}
.progress-inline::-webkit-progress-value {
    background: #6b00b8;
}

/* Minor typography */
h3 {
    font-weight:700;
    margin:0 0 8px 0;
    color:#6b00b8 !important;
}

/* =======================
   File Uploader styling
   ======================= */

div[data-testid="stFileUploader"] > label {
    color: #6b00b8 !important;
    font-weight: 600 !important;
}
div[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 1px solid #dcdcdc;
    border-radius: 10px;
    padding: 10px 12px 14px 12px;
}
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {
    padding: 6px !important;
}
div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] span {
    font-size: 0.9rem !important;
}
div[data-testid="stFileUploader"] button {
    background-color: #6b00b8 !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 6px 14px !important;
    border: none !important;
}
div[data-testid="stFileUploader"] button:hover {
    background-color: #54008f !important;
}

/* =======================
   Agentic log styling
   ======================= */

.agent-log-box {
    background: #faf4ff;
    border-radius: 8px;
    border: 1px dashed #d7c6ff;
    padding: 10px 12px;
    font-size: 13px;
    color: #3b2a6f;
    margin-bottom: 10px;
    max-height: none;
    overflow-y: visible;
}
.agent-log-line {
    margin-bottom: 4px;
}
.agent-log-line.title {
    font-weight: 700;
    color: #6b00b8;
    margin-bottom: 6px;
}
.agent-log-line.info {
    color: #4a3b8f;
}
.agent-log-line.success {
    color: #1b7f3b;
}
.agent-log-line.meta {
    color: #777;
    font-size: 12px;
}
.agent-log-empty {
    color: #999;
    font-style: italic;
}

.main-title {
    text-align: left !important;
    margin: 0 0 4px 0;
}
.panel-desc-left {
    text-align: left !important;
    margin: 0 0 14px 0;
}

/* =======================
   Top Tabs (Lead / Insight)
   ======================= */
.stTabs [role="tablist"] {
    gap: 22px;
    padding-left: 4px;
    border-bottom: 1px solid #e5e7eb;
}
.stTabs [role="tablist"] button {
    font-size: 0.95rem;
    font-weight: 500;
    color: #6b7280;
    padding: 0.4rem 0;
}
.stTabs [role="tablist"] button[aria-selected="true"] {
    color: #6b00b8 !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #6b00b8 !important;
    height: 3px;
    border-radius: 999px;
}

/* =======================
   Main buttons (Run / Stop)
   ======================= */
.stButton > button {
    border-radius: 8px !important;
    border: 1px solid transparent !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"] {
    background: #6b00b8 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 10px rgba(107, 0, 184, 0.18);
}
.stButton > button[kind="primary"]:hover {
    background: #54008f !important;
}
.stButton > button:focus-visible {
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(107, 0, 184, 0.45) !important;
}

/* Secondary (unselected) buttons = grey */
.stButton > button[kind="secondary"] {
    background: #f3f4f6 !important;
    color: #374151 !important;
    border-color: #d1d5db !important;
    box-shadow: none !important;
}

/* Optional: subtle hover for secondary */
.stButton > button[kind="secondary"]:hover {
    background: #e5e7eb !important;
}



/* === Compact File Uploader (Sidebar) === */
[data-testid="stFileUploader"] {
    padding: 6px 10px !important;
    border-radius: 8px !important;
    border: 1px solid #e2e2e2 !important;
    background: #ffffff !important;
    margin-top: 4px !important;
    margin-bottom: 8px !important;
}

/* Reduce padding inside the dropzone */
[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {
    padding: 4px !important;
    min-height: 85px !important;   /* default ~150px */
    border: none !important;
}

/* Reduce line spacing inside uploader */
[data-testid="stFileUploader"] div {
    line-height: 1.2rem !important;
}

/* Smaller Browse button */
[data-testid="stFileUploader"] button {
    padding: 4px 12px !important;
    font-size: 0.85rem !important;
    border-radius: 6px !important;
}

/* ================================
   Disable Product Recommendation
   ================================ */

/* Disable Product Recommendation */
.lead-scope-radio [role="radiogroup"] > label:nth-child(3) {
    flex-direction: column;
    align-items: flex-start;
    opacity: 0.45;
    cursor: not-allowed;
}

/* Disable clicking */
.lead-scope-radio [role="radiogroup"] > label:nth-child(3) input {
    pointer-events: none;
}

/* FIRST line: main label */
.lead-scope-radio [role="radiogroup"] > label:nth-child(3) p:first-child {
    font-weight: 600;
    color: #374151;
}

/* SECOND line: Coming Soon */
.lead-scope-radio [role="radiogroup"] > label:nth-child(3) p:last-child {
    font-size: 0.75rem;
    color: #9ca3af;
    font-style: italic;
    margin-top: 2px;
}


</style>
"""


# ---------------------------
# Log helpers
# ---------------------------
def _log_block_step(lines: list[str]) -> str:
    """Join a list of log lines into a block with a trailing blank line."""
    return "\n".join(lines) + "\n\n"


def _safe_filename_component(s: str) -> str:
    """Make a safe filename component (alphanumeric + underscore, short)."""
    if not s:
        return "unknown"
    s = re.sub(r"\s+", "_", str(s).strip())
    s = re.sub(r"[^A-Za-z0-9_\-\.]", "", s)
    return s[:120]

def normalize_company_name(name: str) -> str:
    """
    Normalize company names for fuzzy matching:
    - lowercase
    - remove spaces, hyphens, punctuation
    """
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]", "", name)
    return name


def generate_detailed_log(
    step_key: str,
    company_display: str,
    website_display: str = "",
    csafe: str = "",
    original_raw_log: str | None = None,
    run_ts: datetime.datetime | None = None,
) -> str:
    """
    Build the detailed download text according to the templates provided.
    step_key values: "website", "firmo", "techno", "financials", "growth"
    """
    # run timestamp (local with offset)
    if run_ts is None:
        run_ts = datetime.datetime.now(datetime.timezone.utc).astimezone()
    run_iso = run_ts.isoformat()

    # base header
    header = [
        "=== AGENTIC PIPELINE DETAILED LOG ===",
        f"Run Timestamp: {run_iso}",
        f"Company: {company_display or 'UNKNOWN'}",
        f"Task: {step_key}",
        "-" * 39,
        "",
    ]
    buf = "\n".join(header)


    # For convenience use a short ts string inside each template line
    ts = run_ts.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

    # Build the relevant step template
    if step_key == "website":
        lines = [
            f"{ts} - INFO - Starting Website Extraction Pipeline",
            f"{ts} - INFO - Input: Company Name = \"{company_display}\"",
            f"{ts} - INFO - Searching Google for official website (region = USA)",
            f"{ts} - INFO - Applying LLM-based ranking to find the most authoritative domain",
            f"{ts} - INFO - Extracted Website: {website_display}",
            f"{ts} - INFO - Performing entity resolution",
            f"{ts} - INFO - - Normalizing entity name variants",
            f"{ts} - INFO - - Deduping against existing entity registry (S3 master list)",
            f"{ts} - INFO - Canonical Company Profile created",
            f"{ts} - INFO - Storing extracted website record",
            f"{ts} - INFO - Saved to: s3://b2b-growth-agent/data_ingestion/Output/website/{csafe}.json",
            f"{ts} - INFO - Website extraction completed successfully",
        ]
        buf += _log_block_step(lines)

    elif step_key == "firmo":
        lines = [
            f"{ts} - INFO - Starting Firmographic Enrichment",
            f"{ts} - INFO - Reading input file from s3://b2b-growth-agent/data_ingestion/Output/website/{csafe}.json",
            f"{ts} - INFO - Input: Company = \"{company_display}\", Website = {website_display}",
            f"{ts} - INFO - [LAMBDA] Event received: {{\"Records\": [{{\"s3\": {{\"bucket\": {{\"name\": \"b2b-growth-agent\"}}, \"object\": {{\"key\": \"data_ingestion/Output/website/{csafe}.json\"}}}}}}], \"run_firmo_lambda\": true}}",
            f"{ts} - INFO - Pulling data from firmographic sources (LLM-enriched + multi-source lookup)",
            f"{ts} - INFO - Extracting legal name, HQ, founding year, addresses, and entity hierarchy",
            f"{ts} - INFO - Enriching revenue, employee range, industry classification",
            f"{ts} - INFO - Fetching social links (LinkedIn, Facebook, Instagram)",
            f"{ts} - INFO - Lambda completed successfully",
            f"{ts} - INFO - 🌐 Crawling company homepages and classifying links by theme...",
            f"{ts} - INFO - Scraping {csafe.lower()} - {website_display} ...",
            f"{ts} - INFO - 🤖 Extracting structured info using Gemini URL Context + Google Search fallback...",
            f"{ts} - INFO - 🔎 URL-context retrieved About Us / Company Info for {company_display}",
            f"{ts} - INFO - 🔎 URL-context retrieved Leadership & Governance for {company_display}",
            f"{ts} - INFO - 🔎 URL-context retrieved Products / Services / Solutions for {company_display}",
            f"{ts} - INFO - 🔎 URL-context retrieved Subsidiaries / Brands for {company_display}",
            f"{ts} - INFO - 🔎 URL-context retrieved Headquarters / Locations for {company_display}",
            f"{ts} - INFO - 🔎 URL-context retrieved Contact Us for {company_display}",
            f"{ts} - INFO - 🔎 URL-context retrieved Social Media for {company_display}",
            f"{ts} - INFO - Running website content extraction (About, Products, Contact, Newsroom)",
            f"{ts} - INFO - Generating company overview summary using LLM",
            f"{ts} - INFO - Performing final entity dedupe and consistency checks",
            f"{ts} - INFO - Writing enriched firmographic profile to S3",
            f"{ts} - INFO - Saved to: s3://b2b-growth-agent/data_ingestion/Output/firmo/{csafe}.json",
            f"{ts} - INFO - Firmographic enrichment completed successfully",
        ]
        buf += _log_block_step(lines)

    elif step_key == "techno":
        lines = [
            f"{ts} - INFO - Starting Technographic Profiling",
            f"{ts} - INFO - Input Entity = \"{company_display}\"",
            f"{ts} - INFO - [LAMBDA] Event received: {{\"Records\": [{{\"s3\": {{\"bucket\": {{\"name\": \"b2b-growth-agent\"}}, \"object\": {{\"key\": \"data_ingestion/Output/website/{csafe}.json\"}}}}}}], \"run_techno_lambda\": true}}",
            f"{ts} - INFO - Hitting technographic vendor APIs and public fingerprints for the detected domains",
            f"{ts} - INFO - Mapping identified products to normalized product categories (CRM, Marketing Automation, Cloud, Data, Security, etc.)",
            f"{ts} - INFO - Computing tech maturity level based on stack depth, cloud adoption and modern tool usage",
            f"{ts} - INFO - Writing technographic profile to S3",
            f"{ts} - INFO - Saved to: s3://b2b-growth-agent/data_ingestion/Output/techno/{csafe}.json",
            f"{ts} - INFO - Lambda completed successfully",
            f"{ts} - INFO - Technographic profiling completed successfully",
        ]
        buf += _log_block_step(lines)

    elif step_key == "financials":
        lines = [
            f"{ts} - INFO - Starting Financial Insights Pipeline",
            f"{ts} - INFO - Input Entity = \"{company_display}\"",
            f"{ts} - INFO - [LAMBDA] Event received: {{\"Records\": [{{\"s3\": {{\"bucket\": {{\"name\": \"b2b-growth-agent\"}}, \"object\": {{\"key\": \"data_ingestion/Output/website/{csafe}.json\"}}}}}}], \"run_finance_lambda\": true}}",
            f"{ts} - INFO - Gathering available financial data for \"{company_display}\"",
            f"{ts} - INFO - Extracting last 3 years (and latest quarters where available) of revenue, EBITDA, net income and operating cash flow",
            f"{ts} - INFO - Computing YoY and QoQ percentage changes",
            f"{ts} - INFO - Deriving financial health & momentum indicators (growth, profitability, leverage and liquidity)",
            f"{ts} - INFO - Preparing financial summary for downstream 360 view",
            f"{ts} - INFO - Saved to: s3://b2b-growth-agent/data_ingestion/Output/financials/{csafe}.json",
            f"{ts} - INFO - Lambda completed successfully",
            f"{ts} - INFO - Financial insights generated successfully",
        ]
        buf += _log_block_step(lines)

    elif step_key == "growth":
        lines = [
            f"{ts} - INFO - Starting Growth Signal Extraction",
            f"{ts} - INFO - Input Entity = \"{company_display}\"",
            f"{ts} - INFO - [LAMBDA] Event received: {{\"Records\": [{{\"s3\": {{\"bucket\": {{\"name\": \"b2b-growth-agent\"}}, \"object\": {{\"key\": \"data_ingestion/Output/website/{csafe}.json\"}}}}}}], \"run_growth_signals_lambda\": true}}",
            f"{ts} - INFO - Fetching last 12 months of news, blogs, and press releases for \"{company_display}\"",
            f"{ts} - INFO - Deduping articles and filtering high-quality signals",
            f"{ts} - INFO - Running LLM-based theme classification using the GTM taxonomy (Growth Signals, Financials, Risk, Strategic Outlook, Customer & Market, Competitor, ESG, Challenges)",
            f"{ts} - INFO - Highlighting Growth Signal sub-themes: Acquisition & Mergers, Awards & Industry Recognition, Business Expansion, Leadership Changes, New Product/Technology Launches, Fundings & Capital Raises.",
            f"{ts} - INFO - Capturing Risk-oriented themes: Regulatory/Legal/Compliance, ESG & Sustainability, Bankruptcy & Financial Distress.",
            f"{ts} - INFO - Enriching Financials-related news: Revenue & Earnings, Profitability & Dividends, Debt & Liquidity.",
            f"{ts} - INFO - Adding context from Strategic Outlook, Customer/Market focus, Competitor actions and Business Pain Points.",
            f"{ts} - INFO - Tagging sentiment, timestamps, and source URLs",
            f"{ts} - INFO - Exporting structured signal dataset",
            f"{ts} - INFO - Saved to: s3://b2b-growth-agent/data_ingestion/Output/growth/{csafe}.json",
            f"{ts} - INFO - Lambda completed successfully",
            f"{ts} - INFO - Growth signal extraction completed successfully",
        ]
        buf += _log_block_step(lines)

    else:
        # generic fallback
        lines = [
            f"{ts} - INFO - Starting {step_key}",
            f"{ts} - INFO - No specific template found; logging basic step info",
            f"{ts} - INFO - Completed {step_key}",
        ]
        buf += _log_block_step(lines)

    # add a tailing meta line
    buf += f"\n--- Generated by Agentic Lead Intelligence on {run_iso} ---\n"
    return buf


# ---------------------------
# tasks config
# ---------------------------
TASKS: List[Dict] = [
    {"name": "Website Extraction", "cols": ["Official Domain"], "icon": "🌐"},
    {
        "name": "Firmographic Enrichment",
        "cols": [
            "Company Overview",
            "Company Founding Year",
            "Headquarter Location",
            "Employee Range",
            "Company Revenue($)",
            "Company Industry",
            "Other Locations",
            "Facebook URL",
            "LinkedIn URL",
            "Instagram URL",
            "Company Board Line Number",
        ],
        "icon": "🏢",
    },
    {"name": "Technographic Profiling", "cols": ["Tech Install"], "icon": "🖥️"},
    {
        "name": "Financial Insights",
        "cols": [
            "Financial Summary",
            "Revenue Growth",
            "Net Income Change",
            "Operating Cash Flow Change",
            "CapEx Change",
            "EPS Change",
            "Funding Amount($)",
        ],
        "icon": "💰",
    },
    {
        "name": "Growth Signals",
        "cols": ["Signal Type", "Signal Details", "Signal Links"],
        "icon": "📈",
    },
]


# ---------------------------
# Static signal counts per company (for log simulation)
# ---------------------------
STATIC_SIGNAL_COUNTS: Dict[str, Dict[str, int]] = {
    "A-Mark Precious Metals": {
        "firmo_signals": 41,
        "web_signals": 7,
        "tech_signals": 3,
        "fin_signals": 12,
        "growth_signals": 5,
    },
    "VeriSign": {
        "firmo_signals": 42,
        "web_signals": 9,
        "tech_signals": 7,
        "fin_signals": 13,
        "growth_signals": 3,
    },
    "Allied Fire Protection": {
        "firmo_signals": 41,
        "web_signals": 8,
        "tech_signals": 7,
        "fin_signals": 0,
        "growth_signals": 3,
    },
    "Aroma360": {
        "firmo_signals": 42,
        "web_signals": 8,
        "tech_signals": 20,
        "fin_signals": 0,
        "growth_signals": 2,
    },
    "Sigmatron International": {
        "firmo_signals": 41,
        "web_signals": 7,
        "tech_signals": 1,
        "fin_signals": 2,
        "growth_signals": 3,
    },
    "Wolfspeed": {
        "firmo_signals": 41,
        "web_signals": 8,
        "tech_signals": 8,
        "fin_signals": 13,
        "growth_signals": 5,
    },
    "VF Corporation": {
        "firmo_signals": 42,
        "web_signals": 8,
        "tech_signals": 6,
        "fin_signals": 6,
        "growth_signals": 5,
    },
}


def get_static_counts(company: str) -> Dict[str, int] | None:
    """Case-insensitive lookup of static signal counts for a company."""
    if not company:
        return None
    c_lower = company.strip().lower()
    for name, counts in STATIC_SIGNAL_COUNTS.items():
        if name.lower() == c_lower:
            return counts
    return None


# ---------------------------
# Agentic log definitions (for UI streaming)
# ---------------------------
def get_agentic_steps(task_name: str, company: str) -> List[Dict[str, str]]:
    """
    Return a list of agentic log lines (with CSS classes) for each task.
    Includes static signal counts in the final success line per step.
    """
    c = company or "the selected company"
    name = task_name.strip().lower()
    counts = get_static_counts(company)

    def fmt_counts(keys_labels):
        """Helper: build '(X foo, Y bar)' style suffix from counts."""
        if not counts:
            return ""
        parts = []
        for key, label in keys_labels:
            val = counts.get(key)
            if isinstance(val, (int, float)) and val > 0:
                parts.append(f"{val} {label}")
        if not parts:
            return ""
        return " (" + ", ".join(parts) + ")."

    # 1) Website + entity resolution
    if name == "website extraction":
        suffix = fmt_counts([("web_signals", "web touchpoints")])
        steps = [
            {"cls": "title", "text": "STEP 1 — Website & Entity Resolution Phase"},
            {"cls": "info", "text": f"🧾 User input: \"{c}\""},
            {"cls": "info", "text": "🎯 Initializing Website Extraction Utility Agent."},
            {
                "cls": "info",
                "text": "🌐 Extracting company websites via Google Search Crawler and LLM ranking...",
            },
            {
                "cls": "info",
                "text": "🔗 Identifying official domain and key web properties (regional sites, subdomains, social handles).",
            },
            {
                "cls": "info",
                "text": "🧩 Performing entity resolution — UID generation, fuzzy matching variants, and deduplication across sources.",
            },
            {
                "cls": "info",
                "text": f"📌 Locking canonical entity record for \"{c}\" for downstream enrichment.",
            },
            {
                "cls": "success",
                "text": f"✅ Website set & canonical company ID created successfully{suffix}",
            },
        ]

    # 2) Firmographics + website signal enrichment
    elif name == "firmographic enrichment":
        suffix = fmt_counts(
            [
                ("firmo_signals", "firmographic attributes"),
                ("web_signals", "website-derived fields"),
            ]
        )
        steps = [
            {
                "cls": "title",
                "text": "STEP 2 — Firmographic & Website Signal Enrichment Phase",
            },
            {
                "cls": "info",
                "text": f"🚀 Initializing Firmographic Enrichment Agent for \"{c}\"...",
            },
            {
                "cls": "info",
                "text": "📞 Hitting vendor firmographic APIs with the canonical Company UID, Name and Domain.",
            },
            {
                "cls": "info",
                "text": "🏛️ Extracting legal name, founding year, HQ location, and global office footprint.",
            },
            {
                "cls": "info",
                "text": "👥 Reconciling employee range and revenue bands from multiple data providers.",
            },
            {
                "cls": "info",
                "text": f"🏭 Classifying industry, sub-industry, and key segments for \"{c}\".",
            },
            {
                "cls": "info",
                "text": "📰 Crawling company website sections — About Us, Newsroom, Product & Services, Contact Us.",
            },
            {
                "cls": "info",
                "text": "🧠 Converting unstructured page content into structured fields: company overview, solution areas, ICP hints, and positioning signals.",
            },
            {
                "cls": "success",
                "text": f"✅ Firmographic snapshot + website-derived signals enriched successfully{suffix}",
            },
        ]

    # 3) Technographic
    elif name == "technographic profiling":
        suffix = fmt_counts([("tech_signals", "technographic signals")])
        steps = [
            {"cls": "title", "text": "STEP 3 — Technographic Profiling Phase"},
            {
                "cls": "info",
                "text": f"🧪 Initializing Technographic Intelligence Agent for \"{c}\"...",
            },
            {
                "cls": "info",
                "text": "🔌 Hitting technographic vendor APIs and public fingerprints for the detected domains.",
            },
            {
                "cls": "info",
                "text": "🗂️ Mapping raw product names into normalized product categories (CRM, Marketing Automation, Cloud, Data, Security, etc.).",
            },
            {
                "cls": "info",
                "text": "📊 Estimating tech maturity level based on stack depth, cloud adoption and modern tool usage.",
            },
            {
                "cls": "success",
                "text": f"✅ Technographic profile and maturity score generated for \"{c}\"{suffix}",
            },
        ]

    # 4) Financials
    elif name == "financial insights":
        suffix = fmt_counts(
            [
                ("fin_signals", "financial metrics & growth indicators"),
            ]
        )
        steps = [
            {"cls": "title", "text": "STEP 4 — Financial Insights Phase"},
            {
                "cls": "info",
                "text": f"💹 Initializing Financials Enrichment Agent for \"{c}\"...",
            },
            {
                "cls": "info",
                "text": "🌍 Hitting public financial APIs / filings aggregators using the canonical legal entity.",
            },
            {
                "cls": "info",
                "text": "🧽 Filtering returned records to the focal company and most recent filings.",
            },
            {
                "cls": "info",
                "text": "📑 Extracting last 3 years (and latest quarters where available) of revenue, EBITDA, net income and operating cash flow.",
            },
            {
                "cls": "info",
                "text": "📈 Computing YoY and QoQ growth rates for revenue, profitability and cash flow.",
            },
            {
                "cls": "info",
                "text": "🧮 Deriving financial health & momentum indicators (growth, profitability, leverage and liquidity).",
            },
            {
                "cls": "success",
                "text": f"✅ Financial summary and growth metrics prepared for scoring engines{suffix}",
            },
        ]

    # 5) News & Growth/Risk signals
    elif name == "growth signals":
        suffix = fmt_counts([("growth_signals", "news-based growth & risk signals")])
        steps = [
            {
                "cls": "title",
                "text": "STEP 5 — News & Signal Detection Phase",
            },
            {
                "cls": "info",
                "text": f"🛰️ Initializing News & Signal Detection Agent for \"{c}\"...",
            },
            {
                "cls": "info",
                "text": f"📰 Fetching last 12 months of news, press releases, blogs and regulatory disclosures mentioning \"{c}\".",
            },
            {
                "cls": "info",
                "text": "🧽 Deduplicating articles and filtering for high-relevance company events.",
            },
            {
                "cls": "info",
                "text": "🧠 Running LLM-based theme classification using the GTM taxonomy (Growth Signals, Financials, Risk, Strategic Outlook, Customer & Market, Competitor, ESG, Challenges).",
            },
            {
                "cls": "info",
                "text": "📌 Highlighting Growth Signal sub-themes: Acquisition & Mergers, Awards & Industry Recognition, Business Expansion, Leadership Changes, New Product/Technology Launches, Fundings & Capital Raises.",
            },
            {
                "cls": "info",
                "text": "⚠️ Capturing Risk-oriented themes: Regulatory/Legal/Compliance, ESG & Sustainability, Bankruptcy & Financial Distress.",
            },
            {
                "cls": "info",
                "text": "💰 Enriching Financials-related news: Revenue & Earnings, Profitability & Dividends, Debt & Liquidity.",
            },
            {
                "cls": "info",
                "text": "📊 Adding context from Strategic Outlook, Customer/Market focus, Competitor actions and Business Pain Points.",
            },
            {
                "cls": "info",
                "text": "🔗 For each signal, attaching source URL, timestamp, sentiment and theme/sub-theme label.",
            },
            {
                "cls": "success",
                "text": f"✅ Prioritized growth & risk signal cards prepared for \"{c}\"{suffix}",
            },
        ]

    else:
        steps = [
            {"cls": "title", "text": f"Running Agentic Step for {task_name}"},
            {"cls": "info", "text": "Orchestrating specialized agents for this capability..."},
            {"cls": "success", "text": "✅ Step completed."},
        ]

    steps.append({"cls": "meta", "text": "Background execution completed just now."})
    return steps


# ---------------------------
# utility helpers
# ---------------------------
def pretty_label(col: str) -> str:
    """Cleans up a column name for display."""
    return col.replace("_", " ").title()


def format_tech_install(raw: str) -> str:
    if not raw:
        return "(no value)"

    s = str(raw).strip()

    # Case 1: list-like string → ["AWS","Azure"]
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return "(no value)"
        items = [x.strip(" '\"") for x in inner.split(",") if x.strip(" '\"")]
        return "<ul>" + "".join([f"<li>{i}</li>" for i in items]) + "</ul>"

    # Case 2: bullet style merged (• Cloud:..., • Security:...)
    if "•" in s:
        parts = [p.strip(" •\n") for p in s.split("•") if p.strip(" •\n")]
        formatted = []
        for p in parts:
            if ":" in p:
                label, rest = p.split(":", 1)
                formatted.append(f"<li><b>{label.strip()}:</b>{rest}</li>")
            else:
                formatted.append(f"<li>{p}</li>")
        return "<ul>" + "".join(formatted) + "</ul>"


    # Case 3: newline separated
    parts = [p.strip(" -•\n") for p in s.split("\n") if p.strip(" -•\n")]
    if len(parts) > 1:
        formatted = []
        for p in parts:
            if ":" in p:
                label, rest = p.split(":", 1)
                formatted.append(f"<li><b>{label.strip()}:</b>{rest}</li>")
            else:
                formatted.append(f"<li>{p}</li>")
        return "<ul>" + "".join(formatted) + "</ul>"



def format_growth_signals(details: str, links: str) -> str:
    """Splits bullet merged growth signals and pairs each with its URLs."""
    if not details:
        return "(no value)"

    parts = [p.strip(" •\n") for p in details.split("•") if p.strip(" •\n")]

    url_list = []
    if links:
        url_list = [u.strip() for u in links.split(",") if u.strip()]

    html_rows = ["<ul>"]
    for i, p in enumerate(parts):
        html_rows.append("<li>")
        if ":" in p:
            label, rest = p.split(":", 1)
            html_rows.append(f"<b>{label.strip()}:</b>{rest}")
        else:
            html_rows.append(p)

        if i < len(url_list):
            html_rows.append(f"<br><b>Source:</b> <a href='{url_list[i]}' target='_blank'>{url_list[i]}</a>")
        html_rows.append("</li>")
    html_rows.append("</ul>")

    return "".join(html_rows)


def format_locations_to_bullets(raw: str) -> str:
    """Formats a string of locations into an HTML bulleted list."""
    if not raw or raw in ("(not available)", "(no value)"):
        return raw

    s = str(raw).strip()

    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if inner == "":
            return "(no value)"
        items = [it.strip().strip("'\"") for it in inner.split(",") if it.strip().strip("'\"")]
        items = [it for it in items if it]
        if not items:
            return "(no value)"
        return "<br>".join([f"• {it}" for it in items])

    for delim in ["•", ";", "|"]:
        if delim in s:
            parts = [p.strip(" •\n\t\r") for p in s.split(delim) if p.strip(" •\n\t\r")]
            return "<br>".join([f"• {p}" for p in parts])

    if "," in s and len(s) > 90:
        parts = [p.strip() for p in s.split(",") if p.strip()]
        bullets = []
        for j in range(0, len(parts), 3):
            chunk = " ".join(parts[j:j + 3]).strip()
            if chunk:
                bullets.append(chunk)
        return "<br>".join([f"• {b}" for b in bullets])

    return s.replace("\n", "<br>")


# ---------------------------
# Mapping helper
# ---------------------------
def task_name_to_step_key(task_name: str) -> str:
    """Map the display task name to the short step key used by generate_detailed_log."""
    m = {
        "Website Extraction": "website",
        "Firmographic Enrichment": "firmo",
        "Technographic Profiling": "techno",
        "Financial Insights": "financials",
        "Growth Signals": "growth",
    }
    return m.get(task_name, task_name.lower().replace(" ", "_"))


# ---------------------------
# Main page
# ---------------------------
def data_engineer_page():
    try:
        st.set_page_config(
            page_title="Agentic Lead Intelligence — Admin Console", layout="wide"
        )
    except Exception:
        pass

    st.markdown(_CSS, unsafe_allow_html=True)
    
    # ------------------------------------
    # Read Excel path from environment
    # ------------------------------------

    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    excel_path = BASE_DIR / "files" / "b2b_agentic_streamlit_demo_data.xlsx"


    try:
        df = pd.read_excel(excel_path, sheet_name="Customer360")
    except Exception as e:
        st.error(f"Failed to load Excel file from path: {excel_path}")
        st.error(str(e))
        df = pd.DataFrame()


    if "uploaded_df" in st.session_state:
        df = st.session_state["uploaded_df"]

    simulate_time_per_step = 0.7  # seconds per log line

    # --- Session State Defaults ---
    if "placeholders" not in st.session_state or not isinstance(
        st.session_state.placeholders, dict
    ):
        st.session_state.placeholders = {}
    if "stop_requested" not in st.session_state:
        st.session_state.stop_requested = False
    if "scope" not in st.session_state:
        st.session_state.scope = "ingest"
    if "last_selected_company" not in st.session_state:
        st.session_state.last_selected_company = None
    if "main_view" not in st.session_state:
        st.session_state.main_view = "lead"
    if "insight_scope" not in st.session_state:
        st.session_state.insight_scope = "Chat"
    if "insight_content_type" not in st.session_state:
        st.session_state.insight_content_type = "Scouting Report"
    if "pipeline_has_run" not in st.session_state:
        st.session_state.pipeline_has_run = False
    if "detailed_logs_list" not in st.session_state:
        st.session_state.detailed_logs_list = []
    if "last_valid_scope" not in st.session_state:
        st.session_state.last_valid_scope = "ingest"

    # ----------------------------------------

    # ---------------------------
    # --- LEFT SIDEBAR (FIXED) ---
    # ---------------------------
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <div class="sidebar-logo-img">
                    <img src="https://cdn.brandfetch.io/idT9xYxvm0/theme/dark/logo.svg?c=1dxbfHSJFAPEGdCLU4o5B">
                </div>
                <div class="sidebar-title-block">
                    <span>Agentic Lead Intelligence</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='scope-title'>Enter Input</div>", unsafe_allow_html=True)

        input_area_ph = st.empty()
        with input_area_ph.container():
            if st.session_state.main_view == "lead":
                st.markdown("<br>", unsafe_allow_html=True)

                # radio_options = [
                #     "Data Ingestion & Enrichment",
                #     "Lead Scoring & Prioritization",
                #     "🚧 Product Recommendation (Coming Soon)",
                # ]
            #     radio_options = [
            #     "Data Ingestion & Enrichment",
            #     "Lead Scoring & Prioritization",
            #     "Product Recommendation (🚧Coming Soon)",
            # ]
                radio_options = [
                    "Data Ingestion & Enrichment",
                    "Lead Scoring & Prioritization",
                    "Product Recommendation\n(Coming Soon)",
                ]


                st.markdown("<div class='lead-scope-radio'>", unsafe_allow_html=True)
                if st.session_state.scope == "ingest":
                    default_index = 0
                elif st.session_state.scope == "score":
                    default_index = 1
                else:
                    default_index = 2

                # chosen = st.radio(
                #     "Select Scope",
                #     radio_options,
                #     index=default_index,
                #     key="scope_radio",
                #     label_visibility="visible",
                # )
                

                chosen = st.radio(
                    "Select Scope",
                    radio_options,
                    index=default_index,
                    key="scope_radio",
                    label_visibility="visible",
                )

                st.markdown("</div>", unsafe_allow_html=True)


                # if chosen == radio_options[0]:
                #     st.session_state.scope = "ingest"
                # elif chosen == radio_options[1]:
                #     st.session_state.scope = "score"
                # else:
                #     st.session_state.scope = "coming_soon"
                if chosen == radio_options[0]:
                    st.session_state.scope = "ingest"
                    st.session_state.last_valid_scope = "ingest"

                elif chosen == radio_options[1]:
                    st.session_state.scope = "score"
                    st.session_state.last_valid_scope = "score"

                else:
                    # Product Recommendation (Coming Soon)
                    st.warning("🚧 Product Recommendation is coming soon.")
                    st.session_state.scope = st.session_state.last_valid_scope
                    st.rerun()


                st.markdown("<br>", unsafe_allow_html=True)

                uploaded_file = st.file_uploader(
                    "Upload data file",
                    type=["xlsx", "xls", "csv"],
                    key="data_file_uploader"
                )

                if uploaded_file is not None:
                    try:
                        if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
                            st.session_state["uploaded_df"] = pd.read_excel(
                                uploaded_file, sheet_name="Customer360"
                            )
                        else:
                            st.session_state["uploaded_df"] = pd.read_csv(uploaded_file)
                    except Exception as e:
                        st.warning(f"Could not read uploaded file: {e}")

                st.markdown("<br>", unsafe_allow_html=True)

                if st.session_state.scope == "score":
                    lead_list_options = [
                        "Q4 2025 — Expansion Accounts",
                        "Q4 2025 — Strategic Accounts",
                        "Q4 2025 — High-Velocity Mid-Market",
                        "Q3 2025 — Renewal & Upsell Candidates",
                    ]

                    current_lead_list = st.session_state.get(
                        "lead_list_name", "Q4 2025 — Expansion Accounts"
                    )

                    if current_lead_list in lead_list_options:
                        default_idx = lead_list_options.index(current_lead_list)
                    else:
                        default_idx = 0

                    selected_lead_list = st.selectbox(
                        "Lead List",
                        lead_list_options,
                        index=default_idx,
                        key="lead_list_select",
                    )

                    st.session_state.lead_list_name = selected_lead_list
                    selected_company = None  # Not required for scoring

                else:
                    selected_company = st.text_input(
                        "Company Name",
                        key="company_input",
                        placeholder="Type company name",
                        on_change=_clear_right_side,
                    )

            else:
                _render_insight_sidebar_inputs()

        selected_company = st.session_state.get("company_input")
        # Preserve selected company across reruns (e.g., download button clicks)
        if not st.session_state.get("company_input") and st.session_state.get("last_selected_company"):
            st.session_state.company_input = st.session_state.last_selected_company

        st.markdown("<div class='sidebar-spacer'></div>", unsafe_allow_html=True)
        st.divider()

        if st.session_state.get("username"):
            st.markdown(
                """
                <div class="sidebar-user-inline">
                    <div class="sidebar-user-avatar-inline">
                        👤
                    </div>
                    <div class="sidebar-user-text-inline">
                        <div class="sidebar-user-name-inline">
                            Signed in as: <span>{username}</span>
                        </div>
                        <div class="sidebar-user-role-inline">
                            Role: {role}
                        </div>
                    </div>
                </div>
                """.format(
                    username=st.session_state.get("username"),
                    role=st.session_state.get("role"),
                ),
                unsafe_allow_html=True,
            )

            st.markdown("<div class='sidebar-logout-wrapper'>", unsafe_allow_html=True)
            if st.button("Logout", key="logout_button"):
                st.session_state.logged_in = False
                st.session_state.role = None
                st.session_state.username = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.divider()

    # --------------------------------
    # --- TOP NAVIGATION BAR (TAB STYLE) - NOW USING st.columns ---
    # --------------------------------
    st.markdown("<div class='top-nav-container'>", unsafe_allow_html=True)

    tab_cols = st.columns([0.15, 0.15, 0.7])

    lead_button_type = "primary" if st.session_state.main_view == "lead" else "secondary"
    insight_button_type = "primary" if st.session_state.main_view == "insight" else "secondary"

    with tab_cols[0]:
        st.button(
            "💼 Lead Management",
            key="nav_lead",
            type=lead_button_type,
            on_click=_switch_to_lead,
            use_container_width=True,
        )

    with tab_cols[1]:
        st.button(
            "💡 Insight Studio",
            key="nav_insight",
            type=insight_button_type,
            on_click=_switch_to_insights,
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)  # close top-nav-container

    # ---------------------------
    # --- MAIN PANEL (CONTENT ROUTING) ---
    # ---------------------------
    if st.session_state.main_view == "lead":

        if st.session_state.scope == "score":
            # print(df)
            try:
                lead_scoring_page(df)
            except Exception as e:
                st.error(f"Failed to load Lead Scoring page: {e}")
            return

        if st.session_state.scope == "coming_soon":
            st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
            st.markdown("## 🧪 Product Recommendation")
            st.info("🚧 Product Recommendation Studio is under development. Coming soon!")
            st.markdown("</div>", unsafe_allow_html=True)
            return


        st.markdown("<div class='main-panel'>", unsafe_allow_html=True)

        st.markdown(
            "<h3 class='main-title'>"
            "<span style='font-size: 1.1em;'>⚙️</span> "
            "Ingestion & Enrichment Console — Company 360° Pipeline"
            "</h3>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p class='panel-desc-left'>"
            "This console is designed to provide transparency into the enrichment pipeline by displaying agent execution status, "
            "extracted signals, and validation outcomes, ensuring accuracy and explainability before downstream prioritization."
            "</p>",
            unsafe_allow_html=True,
        )

        top_cols = st.columns([0.1, 0.1, 0.8])
        with top_cols[0]:
            launch_clicked = st.button(
                "Run Process", key="launch_pipeline", type="primary", use_container_width=True
            )
        with top_cols[1]:
            if st.button(
                "Stop Process", key="stop_pipeline",  type="secondary",  use_container_width=True
            ):
                st.session_state.stop_requested = True

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Tasks Container ---
        tasks_container = st.container()
        with tasks_container:
            for i, t in enumerate(TASKS):
                expander_key = f"exp_{i}"
                if expander_key not in st.session_state:
                    st.session_state[expander_key] = False

                highlighted_cls = (
                    " highlighted" if st.session_state.get(expander_key, False) else ""
                )
                st.markdown(
                    f"<div class='task-card{highlighted_cls}' id='task-{i}'>",
                    unsafe_allow_html=True,
                )

                header_ph = st.empty()
                dot_ph = st.empty()

                # NEW: render status based on session state
                if st.session_state.get(f"task_done_{i}", False):
                    # task completed in a previous run
                    status_html = (
                        f"{status_dot('#10b981')}"
                        f"<span style='color:#10b981;'>— Complete</span>"
                    )
                else:
                    # default = pending
                    status_html = (
                        f"{status_dot('#999999')}"
                        f"<span style='font-weight:600; color:#666;'>— Pending</span>"
                    )

                header_html = (
                    f"<div class='task-card-header'>"
                    f"<div class='task-name'>{t['icon']} {t['name']} {status_html}</div>"
                    f"</div>"
                )
                header_ph.markdown(header_html, unsafe_allow_html=True)

                # header_html = (
                #     f"<div class='task-card-header'>"
                #     f"<div class='task-name'>{t['icon']} {t['name']} "
                #     f"{status_dot('#999999')}<span style='font-weight:600; color:#666;'>— Pending</span></div>"
                #     f"</div>"
                # )
                # header_ph.markdown(header_html, unsafe_allow_html=True)

                st.markdown("<div class='task-card-body'>", unsafe_allow_html=True)
                progress_ph = st.empty()

                # Agentic log area
                log_ph = st.empty()
                if not st.session_state.get(f"log_{i}"):
                    log_ph.markdown(
                        "<div class='agent-log-box agent-log-empty'>Background agent pipeline will appear here once the process starts.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    # Re-render existing log (so UI persists even on rerun)
                    existing_log = st.session_state.get(f"log_{i}", "")

                    if existing_log:
                        # full HTML from stored classes
                        formatted_html = ""
                        for ln in existing_log.split("\n"):
                            # expected format: "{timestamp} - {CLS} - {text}"
                            try:
                                _, cls, text = ln.split(" - ", 2)
                                cls = cls.lower()
                            except:
                                cls = "info"
                                text = ln

                            formatted_html += f"<div class='agent-log-line {cls}'>{html.escape(text)}</div>"

                        log_ph.markdown(f"<div class='agent-log-box'>{formatted_html}</div>", unsafe_allow_html=True)

                    else:
                        log_ph.markdown(
                            "<div class='agent-log-box agent-log-empty'>Background agent pipeline will appear here once the process starts.</div>",
                            unsafe_allow_html=True,
                        )

                    log_html = "".join(
                        [f"<div class='agent-log-line'>{line}</div>" for line in existing_log.split("\n")]
                    )
                    log_ph.markdown(f"<div class='agent-log-box'>{log_html}</div>", unsafe_allow_html=True)


                # Enrichment details (collapsed until task finishes)
                exp = st.expander(
                    "Expand AI Enrichment Details",
                    expanded=st.session_state.get(expander_key, False),
                )
                with exp:
                    results_ph = st.empty()
                    cached_key = f"result_html_{i}"

                    # Show results only if this task has completed in this session run
                    if st.session_state.get(cached_key, None) and st.session_state.get(f"task_done_{i}", False):
                        results_ph.markdown(
                            st.session_state[cached_key], unsafe_allow_html=True
                        )
                    else:
                        # keep placeholder until real results are produced
                        results_ph.markdown(
                            "<div class='output-box'>(no results yet)</div>",
                            unsafe_allow_html=True,
                        )

                st.markdown("</div>", unsafe_allow_html=True)  # task-card-body
                st.markdown("</div>", unsafe_allow_html=True)  # task-card

                st.session_state.placeholders[i] = {
                    "dot_ph": dot_ph,
                    "header_ph": header_ph,
                    "progress_ph": progress_ph,
                    "log_ph": log_ph,
                    "results_ph": results_ph,
                    "expander_key": expander_key,
                    "cached_key": f"result_html_{i}",
                }


        # --- Pipeline Execution Logic ---
        if launch_clicked:
            st.session_state.stop_requested = False

            if not selected_company or not str(selected_company).strip():
                st.warning("Please enter a company name before launching.")
            else:
                name_str = str(selected_company).strip()

                # rows = (
                #     df[df["company_name"].astype(str).str.strip() == name_str]
                #     if "company_name" in df.columns
                #     else pd.DataFrame()
                # )
                if "company_name" in df.columns:
                    user_key = normalize_company_name(name_str)

                    df["_company_key"] = (
                        df["company_name"]
                        .astype(str)
                        .apply(normalize_company_name)
                    )

                    rows = df[df["_company_key"] == user_key]
                    if "_company_key" in df.columns:
                        df.drop(columns=["_company_key"], inplace=True)

                else:
                    rows = pd.DataFrame()


                if rows.empty:
                    st.error("Selected company not found in data source.")
                else:
                    row = rows.iloc[0]

                    # Reset run state
                    st.session_state.pipeline_has_run = False
                    st.session_state.detailed_logs_list = []

                    total_tasks = len(TASKS)
                    overall_progress = st.progress(0, text="Overall Pipeline Progress")

                    # Safe filename
                    csafe_run = _safe_filename_component(name_str)

                    # ----------- Execute each task -----------
                    for i, task in enumerate(TASKS):
                        if st.session_state.get("stop_requested", False):
                            break

                        ph = st.session_state.placeholders.get(i)
                        if ph is None:
                            continue

                        dot_ph = ph["dot_ph"]
                        header_ph = ph["header_ph"]
                        progress_ph = ph["progress_ph"]
                        log_ph = ph["log_ph"]
                        results_ph = ph["results_ph"]
                        expander_key = ph["expander_key"]
                        cached_key = ph["cached_key"]

                        # Clear previous logs/results
                        st.session_state.pop(cached_key, None)
                        st.session_state.pop(f"log_{i}", None)
                        st.session_state.pop(f"detailed_log_{i}", None)
                        st.session_state[f"task_done_{i}"] = False

                        # Mark task = running in header
                        header_ph.markdown(
                            f"<div class='task-card-header'><div class='task-name'>{task['icon']} {task['name']} "
                            f"{status_dot('#f0c040')} <span style='color:#888;'>— Running</span></div></div>",
                            unsafe_allow_html=True,
                        )

                        # -------- Agentic Step Streaming --------
                        agent_steps = get_agentic_steps(task["name"], name_str)

                        log_html = ""
                        plain_lines = []

                        total_lines = len(agent_steps)

                        for idx, step in enumerate(agent_steps, start=1):
                            if st.session_state.get("stop_requested", False):
                                break

                            cls = step.get("cls", "info")
                            text = step.get("text", "")
                            escaped_text = html.escape(text)

                            # Build HTML log stream
                            log_html += f"<div class='agent-log-line {cls}'>{escaped_text}</div>"

                            ts_line = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            plain_lines.append(f"{ts_line} - {cls} - {text}")
                            st.session_state[f"log_{i}"] = "\n".join(plain_lines)

                            log_ph.markdown(
                                f"<div class='agent-log-box'>{log_html}</div>",
                                unsafe_allow_html=True,
                            )

                            pct = int((idx / max(total_lines, 1)) * 100)
                            progress_ph.markdown(
                                f"<div style='width:100%'>"
                                f"<div style='margin-bottom:6px; font-weight:600; font-size: 13px; color: #333;'>Executing... {pct}%</div>"
                                f"<progress value='{pct}' max='100' class='progress-inline'></progress>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )

                            time.sleep(simulate_time_per_step)

                        if st.session_state.get("stop_requested", False):
                            progress_ph.markdown(
                                "<div style='padding:8px;'><strong>Task interrupted by user.</strong></div>",
                                unsafe_allow_html=True,
                            )
                            header_ph.markdown(
                                f"<div class='task-card-header'><div class='task-name'>{task['icon']} {task['name']} "
                                f"{status_dot('#999999')} <span style='color:#999;'>— Interrupted</span></div></div>",
                                unsafe_allow_html=True,
                            )
                            break

                        # Mark task as finished
                        progress_ph.markdown(
                            "<div style='padding:8px;'><strong>Task Finished.</strong></div>",
                            unsafe_allow_html=True,
                        )
                        header_ph.markdown(
                            f"<div class='task-card-header'><div class='task-name'>{task['icon']} {task['name']} "
                            f"{status_dot('#10b981')} <span style='color:#10b981;'>— Complete</span></div></div>",
                            unsafe_allow_html=True,
                        )

                        # -------- Result HTML for Expander --------
                        html_rows = []

                        if task["name"] == "Growth Signals":
                            details = row.get("Signal Details", "")
                            links = row.get("Signal Links", "")
                            formatted = format_growth_signals(details, links)
                            html_rows.append(
                                f"<div class='kv'><div class='label'>Growth Signals</div>{formatted}</div>"
                            )
                        else:
                            for col in task["cols"]:
                                raw_val = row.get(col, "(no value)")
                                if isinstance(raw_val, str):
                                    raw_val = raw_val.strip()

                                if col.lower() in ["other locations", "locations", "hq locations"]:
                                    raw_val = format_locations_to_bullets(raw_val)

                                if col == "Tech Install":
                                    raw_val = format_tech_install(raw_val)

                                html_rows.append(
                                    f"<div class='kv'><div class='label'>{pretty_label(col)}</div>{raw_val}</div>"
                                )

                        result_html = f"<div class='output-box'>{''.join(html_rows)}</div>"

                        st.session_state[cached_key] = result_html
                        st.session_state[f"task_done_{i}"] = True
                        results_ph.markdown(result_html, unsafe_allow_html=True)
                        st.session_state[expander_key] = False

                        # -------- Detailed Log (downloadable template) --------
                        step_key = task_name_to_step_key(task["name"])
                        original_raw = "\n".join([f"[{s['cls'].upper()}] {s['text']}" for s in agent_steps])

                        detailed_text = generate_detailed_log(
                            step_key,
                            name_str,
                            row.get("Official Domain", ""),
                            csafe_run,
                            original_raw,
                            datetime.datetime.now(),
                        )

                        st.session_state[f"detailed_log_{i}"] = detailed_text
                        st.session_state.detailed_logs_list.append(detailed_text)

                        # Update overall progress bar
                        overall_pct = int(((i + 1) / total_tasks) * 100)
                        overall_progress.progress(
                            overall_pct,
                            text=f"Overall Pipeline Progress — {i+1}/{total_tasks} tasks complete",
                        )

                    # -------- All tasks finished --------
                    if st.session_state.get("stop_requested", False):
                        st.warning("Pipeline stopped by user.")
                        overall_progress.empty()
                    else:
                        st.success("Pipeline finished successfully.")
                        overall_progress.empty()

                        # Prepare cleaned Customer360 output
                        csafe = re.sub(r"[^a-z0-9]+", "_", name_str.lower()).strip("_") or "company"

                        customer360_filtered = rows.copy()
                        customer360_filtered.rename(columns = {"company_name":"Company Name"}, inplace = True)
                        customer360_filtered.drop(
                            columns=["lead_priority_label"], errors="ignore", inplace=True
                        )

                        consolidated_log_text = "\n\n".join(st.session_state.detailed_logs_list or [])

                        st.session_state.pipeline_has_run = True
                        st.session_state.pipeline_company = name_str
                        st.session_state.pipeline_csafe = csafe
                        st.session_state.customer360_filtered = customer360_filtered
                        st.session_state.consolidated_log_text = consolidated_log_text


        # -------------------------------------------------
        # AFTER PIPELINE: show download + DB update controls
        # -------------------------------------------------
        if st.session_state.get("pipeline_has_run", False):
            # Only show if we're still on the same company
            last_company = st.session_state.get("pipeline_company")
            current_company = st.session_state.get("company_input")

            if last_company and current_company and last_company == current_company:
                csafe = st.session_state.get("pipeline_csafe", "company")
                customer360_filtered = st.session_state.get("customer360_filtered")
                consolidated_log_text = st.session_state.get("consolidated_log_text", "")

                if customer360_filtered is not None:
                    dl_col1, dl_col2 = st.columns(2)

                    with dl_col1:
                        st.download_button(
                            label="📥 Download Customer 360",
                            data=customer360_filtered.to_csv(index=False).encode("utf-8"),
                            file_name=f"{csafe}_customer360.csv",
                            mime="text/csv",
                            key="download_customer360",
                        )

                    with dl_col2:
                        st.download_button(
                            label="📄 Download Consolidated Logs",
                            data=consolidated_log_text,
                            file_name=f"{csafe}_agentic_pipeline_logs.txt",
                            mime="text/plain",
                            key="download_consolidated_logs",
                        )

                    # ------------------------------------
                    # DB UPDATE PROMPT (USER INPUT)
                    # ------------------------------------

                    customer360_filtered = customer360_filtered.drop(columns=["_company_key"], errors="ignore")
                    customer360_filtered = customer360_filtered.rename(columns={"unique_id": "Unique ID"})
                    customer360_filtered.reset_index(drop = True, inplace = True)

                    st.markdown("---")
                    st.subheader("Update Customer 360 table in your database?")

                    user_update_msg = st.text_input(
                        "Do you want to update the Customer 360 table? (Type 'yes' to confirm)",
                        key="update_prompt_input",
                        placeholder="e.g., yes / no / maybe later",
                    )

                    user_reply = (user_update_msg or "").strip().lower()

                    if user_reply == "yes":
                        db_name = "postgres"
                        table_name = "unified_customer_intelligence"

                        st.success(
                            f"Updating database...\n\n"
                            f"**DB Name:** {db_name}\n"
                            f"**Table Name:** {table_name}"
                        )

                        if st.button("🚀 Confirm Update", key="confirm_update_btn"):
                            # hook your real DB write here if needed
                            st.success(
                                f"Customer 360 updated successfully in `{db_name}.{table_name}`!"
                            )
                            st.markdown("#### Preview of updated records:")
                            st.dataframe(customer360_filtered)

                    elif user_reply:
                        st.info("Okay, the database will not be updated.")


        # close main-panel
        st.markdown("</div>", unsafe_allow_html=True)

            
    else:  # Insight Studio
        insight_studio_page()


if __name__ == "__main__":
    data_engineer_page()
