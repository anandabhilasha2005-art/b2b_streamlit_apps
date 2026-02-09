import streamlit as st
import pandas as pd
import re
import html
import time
from typing import List, Dict

# -------------------------------------------------------------------
# Global CSS Injection (aligned with data_engineer style)
# -------------------------------------------------------------------
def _get_global_css() -> str:
    """Returns the custom CSS for lead prioritization + logs."""
    return """
<style>

/* Progress bar for tasks (same visual as data_engineer) */
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

/* =======================
    Agentic log styling
    ======================= */
.agent-log-box {
    background: #faf4ff;  /* soft lavender */
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

/* Task Card Styling */
.task-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 20px;
    background-color: #ffffff;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.02);
    padding: 15px;
}
.task-card-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}
.task-name {
    font-weight: 600;
    font-size: 1.05rem;
    color: #1f2937;
    display: flex;
    align-items: center;
    gap: 6px;
}

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

/* Prioritization summary header */
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

/* Reuse same title + description classes as data_engineer */
.main-title {
    text-align: left !important;
    margin: 0 0 4px 0;
}
.panel-desc-left {
    text-align: left !important;
    margin: 0 0 14px 0;
    color: #555;
    font-size: 0.98rem;
    line-height: 1.45;
}


/* =======================
    Custom Table Styling for Lead Prioritization (NEW STYLES)
    ======================= */
.prioritization-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    line-height: 1.4;
    color: #374151; /* Dark text */
}

.prioritization-table thead th {
    background-color: #f9fafb; /* Light header background */
    color: #4b5563; /* Header text color */
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
    border-bottom: 2px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 10;
}

.prioritization-table tbody tr {
    border-bottom: 1px solid #f3f4f6; /* Subtle row separator */
    transition: background-color 0.15s ease;
}

.prioritization-table tbody tr:hover {
    background-color: #f9fafb; /* Light hover effect */
}

.prioritization-table tbody td {
    padding: 12px 16px;
    vertical-align: top;
}

/* Index Column */
.prioritization-table .col-idx {
    width: 20px;
    font-size: 12px;
    color: #9ca3af;
    padding-right: 0;
}

/* Priority Column */
.prioritization-table .col-priority {
    width: 80px;
}

/* The actual badge styling */
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

/* Priority Color Mapping */
.priority-high {
    background-color: #d1fae5; /* Light Green */
    color: #065f46; /* Dark Green */
    border: 1px solid #34d399;
}
.priority-medium {
    background-color: #fffbeb; /* Light Yellow */
    color: #92400e; /* Dark Yellow */
    border: 1px solid #fcd34d;
}
.priority-low {
    background-color: #fee2e2; /* Light Red/Pink */
    color: #991b1b; /* Dark Red */
    border: 1px solid #f87171;
}

/* Explicit minimum width for the Rationale column to ensure it is visible */
.prioritization-table .col-rationale {
    min-width: 300px; 
}


/* Add this class to your global CSS or ensure the table is wrapped */
.scrollable-table-wrapper {
    overflow-x: auto; /* Enables horizontal scrolling if content exceeds width */
    max-height: 500px; /* Optional: Adds vertical scrolling after 500px */
    overflow-y: auto;
    border: 1px solid #e5e7eb; /* Optional: Gives the wrapper a subtle border */
    border-radius: 8px;
    margin-top: 10px;
}

/* Ensure the prioritization-table uses its full width to enable scrolling */
.prioritization-table {
    /* Set a minimum width greater than the container to force scrolling */
    min-width: 1400px; 
    border-collapse: collapse;
    font-size: 14px;
    line-height: 1.4;
    color: #374151;
}

/* Remove the header styling for the 'Ix' column (it was removed in Python too, this is a guardrail) */
.prioritization-table thead th:last-child {
    /* display: none; */ 
    /* Removing this line because the last 'th' is now 'Priority Rationale' */
    /* The index 'th' is correctly the first child, so no need for this style */
}
</style>
"""

# -------------------------------------------------------------------
# Small helpers
# -------------------------------------------------------------------
def status_dot(color: str = "#ccc", size: int = 12) -> str:
    """Colored dot HTML used in headers."""
    return (
        f"<div style='width:{size}px; height:{size}px; border-radius:50%; "
        f"background:{color}; display:inline-block;'></div>"
    )

LEAD_TASKS: List[Dict] = [
    {"name": "Business Context Analyzer", "key": "business_context"},
    {"name": "AI-Driven Category Weights", "key": "category_weights"},
    {"name": "Prioritization Segment Classifier", "key": "prioritization_table"},
]

SIMULATE_TIME_PER_STEP = 0.6  # seconds per log line

# -------------------------------------------------------------------
# Agentic steps for each task (logs)
# -------------------------------------------------------------------
def get_lead_scoring_steps(task_key: str) -> List[Dict[str, str]]:
    """Returns a list of agentic log steps for the given task."""
    if task_key == "business_context":
        steps = [
            {"cls": "title", "text": "STEP 2 — Business Context Analyzer"},
            {"cls": "info", "text": "🤖 Initializing Business Context Analyzer Agent…"},
            {"cls": "info", "text": "🧠 Analyzing narrative input to extract structured context dimensions…"},
            {"cls": "info", "text": "🎯 Identified business objective and strategic intent."},
            {"cls": "info", "text": "👥 Classified target segment and customer archetype."},
            {"cls": "info", "text": "🗺️ Recognized operational geography and market coverage."},
            {"cls": "info", "text": "🧩 Mapped key product focus areas (Connectivity, Internet, Communication, Security)."},
            {"cls": "info", "text": "⚠️ Highlighted business challenges impacting GTM execution."},
            {"cls": "info", "text": "📈 Derived success metrics aligned to revenue and penetration goals."},
            {"cls": "success", "text": "📌 Agent Summary: Business context translated into actionable signals for downstream weighting, logic design, and prioritization scoring."},
        ]

    elif task_key == "category_weights":
        steps = [
            {"cls": "title", "text": "STEP 3 — Category Weight Optimization"},
            {"cls": "info", "text": "⚖️ Initializing Category Weight Optimizer Agent…"},
            {"cls": "info", "text": "🔎 Evaluating signal families: Technographics, Growth Signals, Financial Strength, Firmographics, Company Profile…"},
            {"cls": "info", "text": "📐 Calibrating category weights to align with business objective, target segment, and GTM priorities."},
            {"cls": "info", "text": "🏷️ Generating importance hierarchy and relevance tags:"},
            {"cls": "info", "text": "   • Technology category relevance"},
            {"cls": "info", "text": "   • Industry prioritization"},
            {"cls": "info", "text": "   • Location classification"},
            {"cls": "info", "text": "   • All category relevance tags generated."},
            {"cls": "success", "text": "✓ Optimization complete — category weights finalized successfully."},
        ]

    elif task_key == "prioritization_table":
        steps = [
            {"cls": "title", "text": "STEP 4 — Priority Segment Logic & Scoring"},
            {"cls": "info", "text": "🏗️ Initializing Logic Architect Agent…"},
            {"cls": "info", "text": "🧮 Constructing prioritization logic based on inputs, weights, and relevance tags…"},
            {"cls": "info", "text": "🔧 Applying scoring framework…"},
            {"cls": "info", "text": "   • Extracting calibrated sub-weights…"},
            {"cls": "info", "text": "   ✓ Sub-weights extracted successfully."},
            {"cls": "info", "text": "   • Applying weighted scoring across all accounts…"},
            {"cls": "info", "text": "   ✓ Weighted scores computed."},
            {"cls": "info", "text": "   • Assigning priority segments (High / Medium / Low)…"},
            {"cls": "success", "text": "✓ Priority segments generated and applied."},
        ]
    else:
        steps = [
            {"cls": "title", "text": "Lead Scoring Agent"},
            {"cls": "info", "text": "Running scoring sub-graph..."},
            {"cls": "success", "text": "✓ Step completed."},
        ]
    return steps

# -------------------------------------------------------------------
# Format helpers for details
# -------------------------------------------------------------------
def _business_context_html_from_text(ctx_text: str) -> str:
    if not ctx_text or str(ctx_text).strip() == "":
        ctx_text = ""
    paragraphs = [p.strip() for p in re.split(r"\n{1,2}", ctx_text) if p.strip()]
    objective = html.escape(paragraphs[0]) if paragraphs else "(no objective provided)"
    
    key_products = ["Dedicated Fiber", "Internet", "Communication", "Security products"]
    key_challenges = [
        "Lack of granular insights to identify high-potential accounts",
        "Misalignment of sales execution with digital and connectivity demands in the mid-market space",
    ]
    success_metrics = [
        "Increased adoption of Dedicated Fiber, Internet, Communication, and Security products",
        "Improved market penetration in the mid-market segment",
        "Revenue growth in the mid-market segment",
        "Optimized GTM strategy with better customer targeting and segmentation",
    ]

    html_out = "<div class='output-box'>"
    html_out += (
        "<div style='margin-bottom:10px; font-weight:600;'>Business Objective:</div>"
        f"<div style='margin-bottom:8px;'>{objective}</div>"
    )
    html_out += (
        "<div style='margin-top:8px;'><strong>Target Segment:</strong><br>"
        "Mid-market businesses</div>"
    )
    html_out += "<div style='margin-top:8px;'><strong>Geography:</strong><br>US region</div>"
    html_out += (
        "<div style='margin-top:8px;'><strong>Primary Goal:</strong><br>"
        "Increase market penetration, drive revenue growth, and optimize Go-To-Market (GTM) strategy."
        "</div>"
    )
    html_out += "<div style='margin-top:8px;'><strong>Key products:</strong><ul>"
    for p in key_products:
        html_out += f"<li>{html.escape(p)}</li>"
    html_out += "</ul></div>"
    html_out += "<div style='margin-top:8px;'><strong>Key Challenges:</strong><ul>"
    for c in key_challenges:
        html_out += f"<li>{html.escape(c)}</li>"
    html_out += "</ul></div>"
    html_out += "<div style='margin-top:8px;'><strong>Success Metrics:</strong><ul>"
    for s in success_metrics:
        html_out += f"<li>{html.escape(s)}</li>"
    html_out += "</ul></div>"
    html_out += "</div>"
    return html_out

def _format_weights_to_html() -> str:
    """Card-based layout with weights & reasoning."""
    def md_to_html_bold(text: str) -> str:
        parts = text.split("**")
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                result.append(f"<strong>{part}</strong>")
            else:
                result.append(part)
        return "".join(result)

    categories = [
        {
            "title": "Growth Signals", "priority": "High", "weight": 35, 
            "sample": "Funding rounds, hiring spikes, expansions, acquisitions, new locations",
            "reasoning": "**Highest Weight**: Dynamic growth events are the **strongest leading indicators** of **near-term demand** for upgraded connectivity and security. They align directly with the objective of identifying **high-potential, high-urgency accounts**.",
            "value": "**Detects Near-Term Demand**: Surfaces accounts **actively expanding or transforming**—the most likely to require new or scaled **Dedicated Fiber, Internet, Communication, or Security solutions** in the short term.",
        },
        {
            "title": "Technographics", "priority": "High", "weight": 30, 
            "sample": "Current network stack, cloud usage (AWS/Azure), security tools, SD-WAN, digital maturity",
            "reasoning": "**High Weight**: Validates **technology readiness** and **product-market fit** for advanced offerings. Strong technical signals **reduce sales friction** and increase conversion for **premium connectivity/security**.",
            "value": "**Confirms Product-Market Fit**: Shows whether an account's **technical environment** can adopt and utilize premium connectivity and security products, **improving targeting quality**.",
        },
        {
            "title": "Firmographics", "priority": "Medium", "weight": 15, 
            "sample": "Employee count, revenue band, location count, industry (NAICS/SIC)",
            "reasoning": "**Medium Weight**: Provides **essential structural context** to ensure the account fits the **mid-market focus**. Useful for **segmentation** but **less predictive** of immediate purchase timing.",
            "value": "**Segmentation & Qualification**: Ensures accounts meet **mid-market criteria** and typically have the operational profile that requires **dedicated connectivity solutions**.",
        },
        {
            "title": "Financial Data", "priority": "Medium", "weight": 15, 
            "sample": "Credit rating, cash flow, funding stage, YoY revenue growth, YoY employee growth",
            "reasoning": "**Medium Weight**: Validates the account's **ability to commit** to multi-year contracts and **filters deal risk**. Used as **supporting evidence** rather than a primary intent signal.",
            "value": "**Validates Deal Quality**: Confirms **financial capacity** and **reduces credit/risk exposure** for long-term contracts.",
        },
        {
            "title": "Company Profile", "priority": "Low", "weight": 5, 
            "sample": "HQ location, years in business, business model, operational footprint",
            "reasoning": "**Lowest Weight**: Provides **contextual background** that aids GTM planning (e.g., multi-site potential), but has the **weakest correlation** with **short-term purchase intent**.",
            "value": "**GTM Context**: Adds **strategic depth** to account profiles to better plan **territory coverage** and multi-product approaches.",
        },
    ]

    html_out = "<div class='output-box'>"

    def render_card(c: Dict) -> str:
        badge_color = "#9ca3af"
        if c["priority"].lower() == "high":
            badge_color = "#06b6d4"
        elif c["priority"].lower() == "medium":
            badge_color = "#fb923c"
        
        card_html = (
            "<div style='background:#fff;border-radius:8px;padding:12px;border:1px solid #eee;'>"
        )
        card_html += (
            "<div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>"
            f"<div style='font-weight:700;font-size:15px'>{c['title']}</div>"
            "<div style='margin-left:auto;display:flex;gap:8px;align-items:center;'>"
            f"<div style='background:{badge_color};color:#fff;padding:6px 8px;"
            "border-radius:999px;font-weight:700;font-size:12px'>"
            f"{c['priority']}</div>"
            f"<div style='font-weight:700;color:#374151'>{c['weight']}%</div>"
            "</div></div>"
        )
        card_html += (
            f"<div style='color:#4b5563;font-size:13px;margin-bottom:8px;'><strong>Attributes:"
            f"</strong><br>{c['sample']}</div>"
        )
        card_html += (
            "<div style='font-size:13px;color:#374151;margin-bottom:8px;'>"
            f"<strong>Why this weight:</strong><br>{md_to_html_bold(c['reasoning'])}</div>"
        )
        card_html += (
            "<div style='font-size:13px;color:#111827;'>"
            f"<strong>Value in prioritization:</strong><br>{md_to_html_bold(c['value'])}</div>"
        )
        card_html += "<div style='margin-top:10px;'>"
        card_html += (
            "<div style='height:8px;background:#f3f4f6;border-radius:999px;overflow:hidden;'>"
            f"<div style='height:100%;width:{int(c['weight'])}%;"
            "background:linear-gradient(90deg,#60a5fa,#3b82f6);'></div>"
            "</div></div>"
        )
        card_html += "</div>"
        return card_html

    # Row 1 (3 cards)
    html_out += (
        "<div style='display:grid; grid-template-columns:repeat(3, 1fr); "
        "gap:12px; margin-bottom: 12px;'>"
    )
    for c in categories[:3]:
        html_out += render_card(c)
    html_out += "</div>"

    # Row 2 (2 cards + empty cell)
    html_out += (
        "<div style='display:grid; grid-template-columns:repeat(3, 1fr); "
        "gap:12px;'>"
    )
    for c in categories[3:]:
        html_out += render_card(c)
    html_out += "<div></div>"  # third column empty
    html_out += "</div>"
    html_out += "</div>"
    return html_out

def _format_prioritization_html_summary() -> str:
    """Returns the header for the prioritization step."""
    return """
<div class="output-box">
    <div class="kv">
        <span class="label">Lead Prioritization — Explanatory Data</span>
        <div class="small-muted">
            The weighted scoring framework has generated final priority segments and scores.
        </div>
    </div>
</div>
"""

# -------------------------------------------------------------------
# Final Updated Format helper for the table (with Priority Rationale fix)
# -------------------------------------------------------------------
def _format_prioritization_table_html(df: pd.DataFrame) -> str:
    """Generates the custom, styled HTML table, ensuring all desired columns are displayed."""
    
    # Define ALL column headers and classes
    # NOTE: The order here defines the order in the final rendered table (after index and priority)
    DISPLAY_COLUMNS = [
        "Growth Signals", 
        "Tech Maturity", 
        "Financial Strength", 
        "Intent Signals",
        "GTM Fit",
        "Priority Rationale" # <--- ENSURING IT IS IN THE LIST
    ]
    
    # Mapping for CSS classes (mostly for consistency, but not strictly needed for every column)
    COL_MAPPING = {
        "Company Name": "col-company",
        "Priority": "col-priority",
        "Growth Signals": "col-signals",
        "Tech Maturity": "col-tech",
        "Financial Strength": "col-financial",
        "Intent Signals": "col-intent",
        "GTM Fit": "col-gtm",
        "Priority Rationale": "col-rationale",
    }
    
    # List of unicode characters to remove
    ICON_CHARS = "⭐🟡⚪🟢🔴" 

    def format_cell_content(content: str) -> str:
        # Improved formatting: remove icon, bold the score/status, keep explanation.
        parts = content.split("—", 1)
        if len(parts) == 2:
            score_text = parts[0].strip()
            score_text_clean = score_text.lstrip(ICON_CHARS).strip()

            bold_part = html.escape(score_text_clean)
            explanation = html.escape(parts[1].strip())
            
            return f"<strong>{bold_part}</strong> — {explanation}"
        
        # Priority Rationale content does not use the '—' separator, so we just bold the whole thing.
        return f"<strong>{html.escape(content)}</strong>"


    # Start the scrollable wrapper and the table HTML
    html_out = "<div class='scrollable-table-wrapper'>"
    html_out += "<table class='prioritization-table'>"
    
    # --- Table Header ---
    html_out += "<thead><tr>"
    html_out += "<th class='col-idx'></th>" # Index column header
    html_out += f"<th>{html.escape('Company Name')}</th>"
    html_out += f"<th>{html.escape('Priority')}</th>"
    
    # Iterate through the specific display columns for the header
    for name in DISPLAY_COLUMNS:
        html_out += f"<th>{html.escape(name)}</th>"

    html_out += "</tr></thead>"
    
    # --- Table Body ---
    html_out += "<tbody>"
    
    # Iterate over the DataFrame rows
    for index, row in df.iterrows():
        
        priority_data = row["Priority"].split(" ")
        priority_raw = priority_data[-1].lower() if len(priority_data) > 1 else 'low'
        priority_text = priority_data[-1] if len(priority_data) > 1 else 'Low'
        priority_class = f"priority-{priority_raw}"
        
        html_out += "<tr>"
        
        # 1. Index Column
        html_out += f"<td class='col-idx'>{index}</td>"
        
        # 2. Company Name
        html_out += f"<td class='col-company'><strong>{html.escape(row['Company Name'])}</strong></td>"
        
        # 3. Priority Badge (Centered)
        html_out += f"<td class='col-priority'><div style='text-align: center;'><div class='priority-badge {priority_class}'>{priority_text}</div></div></td>"
        
        # 4-9. Data columns (using the defined DISPLAY_COLUMNS list)
        for col in DISPLAY_COLUMNS:
            cell_content = row.get(col, "N/A")
            
            # Apply formatting
            styled_content = format_cell_content(str(cell_content))
            
            # Apply vertical alignment to the top
            html_out += (
                f"<td class='{COL_MAPPING.get(col, '')}' "
                f"style='vertical-align: top;'>{styled_content}</td>"
            )
            
        html_out += "</tr>"
        
    html_out += "</tbody>"
    html_out += "</table>"
    html_out += "</div>" # Close the scrollable wrapper div
    
    return html_out
# --- End of _format_prioritization_table_html ---

# -------------------------------------------------------------------
# Main page
# -------------------------------------------------------------------
def lead_scoring_page(df=None):
    # --- CSS ---
    st.markdown(_get_global_css(), unsafe_allow_html=True)

    # --- ALWAYS use mock DataFrame (ignore df passed from data_engineer) ---
    mock_data = {
        "Company Name": [
            "A-Mark Precious Metals",
            "VeriSign",
            "Allied Fire Protection",
            "Aroma360",
            "SigmaTron International",
            "Wolfspeed",
            "VF Corporation",
        ],
        "Priority": [
            "🟢 High",
            "🟢 High",
            "🔴 Low",
            "🟡 Medium",
            "🔴 Low",
            "🟡 Medium",
            "🟢 High",
        ],
        "Growth Signals": [
            "⭐ High — strategic acquisitions, Gold.com rebrand, and +13% YoY FY25 revenue growth.",
            "🟡 Medium — steady 4–6% YoY revenue growth.",
            "⚪ Low — limited organic growth; single regional acquisition.",
            "⭐ High — retail footprint expansion + new product lines.",
            "⚪ Low — no organic growth; privatized via acquisition.",
            "🟡 Medium — restructuring with long-term sector tailwinds.",
            "⭐ High — $600M divestiture and portfolio optimization.",
        ],
        "Tech Maturity": [
            "⭐ High — AWS-based cloud stack with strong security supporting regulated financial operations.",
            "⭐ High — advanced multi-cloud, IAM and networking stack.",
            "⚪ Low — minimal modern tech (Interactio only).",
            "🟡 Medium — AWS, Azure, Zoho, MuleSoft.",
            "⚪ Low — no clear evidence of modern cloud / security stack.",
            "⭐ High — deep cloud, security and data/AI stack.",
            "⭐ High — large enterprise stack in cloud, security, AI, CRM/ERP.",
        ],
        "Financial Strength": [
            "⭐ High — solid revenue and cash flow growth; short-term margin and EPS pressure from acquisition-led expansion.",
            "⭐ High — strong cash flow and shareholder returns.",
            "🟡 Medium — healthy but modest mid-market revenue.",
            "🟡 Medium — mid-market consumer / retail profile.",
            "🟡 Medium — meaningful revenue but unclear trajectory.",
            "⚪ Low — revenue decline, losses and recent Chapter 11.",
            "⭐ High — scale, brand portfolio and balance sheet resilience.",
        ],
        "Intent Signals": [
            "⭐ High — acquisitions, consumer rebrand, new market entry, and continued digital investment.",
            "🟡 Medium — strong ops; some regulatory/antitrust scrutiny.",
            "⚪ Low — few digital or GTM transformation signals.",
            "⭐ High — expansion + launches indicate active GTM motion.",
            "⚪ Low — few positive strategic or digital signals.",
            "⭐ High — restructuring plus new CFO and transformation focus.",
            "⭐ High — divestiture + expansion and real-estate optimization.",
        ],
        "GTM Fit": [
            "⭐ High — mission-critical trading and consumer platforms needing secure, low-latency, always-on connectivity.",
            "⭐ High — mission-critical DNS and internet infrastructure.",
            "⚪ Low — connectivity is supportive, not strategic.",
            "🟡 Medium — omni-channel & experiential retail need reliable connectivity.",
            "⚪ Low — limited proof of high-bandwidth or digital use cases.",
            "⭐ High — fab & R&D ops need high-reliability connectivity.",
            "⭐ High — global omni-channel + complex supply chain footprint.",
        ],
        "Priority Rationale": [
            "Acquisition-driven financial platform with expanding consumer footprint and high security, connectivity, and scale needs.",
            "Highly digital, global, real-time workloads.",
            "Low tech readiness and limited growth / digital signals.",
            "Strong momentum and digital operations but smaller scale.",
            "Weak growth and unclear digital strategy during transition.",
            "Excellent tech and GTM fit but short-term financial risk.",
            "Large, highly digital enterprise with complex global footprint.",
        ],
    }
    st.session_state["lead_prioritization_df"] = pd.DataFrame(mock_data)
    df_for_status = st.session_state["lead_prioritization_df"].copy()

    # -------------------- header --------------------
    lead_list_name = st.session_state.get(
        "lead_list_name",
        "November Lead List — Expansion Accounts",
    )

    st.markdown(
        """<h3 class='main-title'><span style='font-size: 1.1em;'>🎯</span>
        Lead Scoring &amp; Prioritization Console</h3>""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """<p class='panel-desc-left'>
        This console converts Customer 360° signals into explainable lead scores and
        priority segments, aligned to your GTM objective.</p>""",
        unsafe_allow_html=True,
    )

    # -------------------- business context text area --------------------
    default_context = (
        "We aim to strengthen our mid-market presence across the U.S. for Dedicated Fiber, Internet, "
        "Communication, and Security offerings. While coverage is strong, identifying accounts with the highest "
        "growth potential or urgent connectivity needs remains a challenge.\n\n"
        "As a result, sales teams lack actionable insights to prioritize and position the right products.\n\n"
        "Our goal is to enhance targeting, segmentation, and sales intelligence to deepen market penetration, "
        "accelerate revenue growth, and align execution with rising digital and connectivity demands."
    )
    if "lead_ctx_text" not in st.session_state:
        st.session_state.lead_ctx_text = default_context

    ctx = st.text_area(
        "Business Context",
        value=st.session_state.lead_ctx_text,
        key="lead_ctx_text_area",
        height=140,
    )
    st.session_state.lead_ctx_text = ctx

    # session defaults
    if "lead_placeholders" not in st.session_state: st.session_state.lead_placeholders = {}
    if "lead_cached" not in st.session_state: st.session_state.lead_cached = {}
    if "lead_run_id" not in st.session_state: st.session_state.lead_run_id = 0
    if "lead_stop_requested" not in st.session_state: st.session_state.lead_stop_requested = False

    cols = st.columns([1, 1, 8])
    with cols[0]:
        run_clicked = st.button("Run Process", key="lead_run", use_container_width=True)
    with cols[1]:
        stop_clicked = st.button("Stop Process", key="lead_stop", use_container_width=True)

    if stop_clicked:
        st.session_state.lead_stop_requested = True
        run_clicked = False

    # global STEP 1 log placeholder
    step1_log_ph = st.empty()
    if "lead_step1_log_html" in st.session_state:
        step1_log_ph.markdown(st.session_state["lead_step1_log_html"], unsafe_allow_html=True)

    # -------------------- task scaffolding --------------------
    st.markdown("<hr>", unsafe_allow_html=True)
    task_container = st.container()
    with task_container:
        for t in LEAD_TASKS:
            key = t["key"]
            st.markdown(f"<div class='task-card' id='lead-task-{key}'>", unsafe_allow_html=True)
            header_ph = st.empty()
            progress_ph = st.empty()

            # default header: pending
            header_ph.markdown(
                f"<div class='task-card-header'><div class='task-name'>{html.escape(t['name'])} "
                f"{status_dot('#999999', 12)}<span style='color:#888;'>— Pending</span></div></div>",
                unsafe_allow_html=True,
            )

            # agent log placeholder
            log_ph = st.empty()
            if f"lead_log_html_{key}" in st.session_state:
                log_ph.markdown(st.session_state[f"lead_log_html_{key}"], unsafe_allow_html=True)
            else:
                log_ph.markdown(
                    "<div class='agent-log-box agent-log-empty'>Background agent pipeline will appear here once the run starts.</div>",
                    unsafe_allow_html=True,
                )

            # expander with details
            exp = st.expander("Expand AI Enrichment Details", expanded=False)
            with exp:
                results_ph = st.empty()
                cached_html = st.session_state.lead_cached.get(key)
                if cached_html:
                    with results_ph.container():
                        # The summary HTML is cached first
                        if key == "prioritization_table" and "lead_prioritization_df" in st.session_state:
                            # Split the cached HTML back into header and table/download part
                            header_html = _format_prioritization_html_summary()
                            st.markdown(header_html, unsafe_allow_html=True)
                            
                            display_df = st.session_state["lead_prioritization_df"]
                            # REPLACEMENT A: Use custom HTML table instead of st.dataframe
                            st.markdown(_format_prioritization_table_html(display_df), unsafe_allow_html=True) 
                            
                            csv = display_df.to_csv(index=False).encode("utf-8")
                            st.download_button(
                                "Download Prioritization CSV",
                                data=csv,
                                file_name=f"prioritization_cached_{st.session_state.lead_run_id}.csv",
                                mime="text/csv",
                                key=f"lead_download_cached_{key}_{st.session_state.lead_run_id}",
                            )
                        else: # For Business Context and Weights
                            st.markdown(cached_html, unsafe_allow_html=True)
                else:
                    results_ph.markdown("<div class='output-box'>(no results yet)</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            st.session_state.lead_placeholders[key] = {
                "header_ph": header_ph,
                "log_ph": log_ph,
                "results_ph": results_ph,
                "progress_ph": progress_ph,
            }

    overall_progress_ph = st.empty()

    # -------------------- active run --------------------
    if run_clicked:
        st.session_state.lead_stop_requested = False
        st.session_state.lead_run_id += 1
        run_id = st.session_state.lead_run_id

        # reset cache
        st.session_state.lead_cached = {}

        # --- STEP 1 global log (uses mock df metrics) ---
        row_count = len(df_for_status.index)
        metadata_fields = len(df_for_status.columns)
        unique_ids = row_count  # simple = number of rows
        lead_list_label = st.session_state.get("lead_list_name", "Selected Lead List")

        step1_steps = [
            {
                "cls": "title",
                "text": "STEP 1 — Lead Scoring Phase",
            },
            {
                "cls": "info",
                "text": f"Initializing Lead Scoring Super Agent to prioritize leads for \"{lead_list_label}\"…",
            },
            {
                "cls": "info",
                "text": "📥 Reading Customer 360° signals in-memory…",
            },
            {
                "cls": "info",
                "text": f"🔍 Extracted {unique_ids} unique account IDs.",
            },
            {
                "cls": "info",
                "text": "🚀 Invoking Prioritization Super Agent...",
            },

            {
                "cls": "info",
                "text": f"✓ C360 data loaded: {row_count} companies.",
            },
            {
                "cls": "success",
                "text": "✓ Passing enriched dataset to Business Context Analyzer Agent…",
            },
        ]

        log_html = "<div class='agent-log-box' style='margin-top: 15px;'>"

        for step in step1_steps:
            if st.session_state.lead_stop_requested:
                break

            cls = step.get("cls", "info")
            text = html.escape(step.get("text", ""))
            log_html += f"<div class='agent-log-line {cls}'>{text}</div>"

            box_html = log_html + "</div>"
            step1_log_ph.markdown(box_html, unsafe_allow_html=True)
            st.session_state["lead_step1_log_html"] = box_html

            time.sleep(SIMULATE_TIME_PER_STEP)


        # --- normal pipeline ---
        total = len(LEAD_TASKS)
        overall_progress_ph.progress(0, text="Overall Pipeline Progress")


        for idx, task in enumerate(LEAD_TASKS):
            if st.session_state.lead_stop_requested:
                st.warning("Lead scoring pipeline stopped by user.")
                break

            key = task["key"]
            ph = st.session_state.lead_placeholders.get(key, {})
            header_ph = ph.get("header_ph")
            log_ph = ph.get("log_ph")
            results_ph = ph.get("results_ph")
            progress_ph = ph.get("progress_ph")

            # header -> running
            if header_ph is not None:
                header_ph.markdown(
                    f"<div class='task-card-header'><div class='task-name'>"
                    f"{html.escape(task['name'])} "
                    f"{status_dot('#f0c040', 12)}"
                    f"<span style='color:#888;'>— Running</span></div></div>",
                    unsafe_allow_html=True,
                )

            # --- Agentic log streaming + per-task progress ---
            agent_steps = get_lead_scoring_steps(key)
            log_html = ""
            total_lines = len(agent_steps)

            for s_idx, step in enumerate(agent_steps, start=1):
                if st.session_state.lead_stop_requested:
                    break

                cls = step.get("cls", "info")
                text = html.escape(step.get("text", ""))
                log_html += f"<div class='agent-log-line {cls}'>{text}</div>"

                box_html = f"<div class='agent-log-box'>{log_html}</div>"
                log_ph.markdown(box_html, unsafe_allow_html=True)
                st.session_state[f"lead_log_html_{key}"] = box_html

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

            if st.session_state.lead_stop_requested:
                if progress_ph is not None:
                    progress_ph.markdown(
                        "<div style='padding:8px;'><strong>Task interrupted by user.</strong></div>",
                        unsafe_allow_html=True,
                    )
                if header_ph is not None:
                    header_ph.markdown(
                        f"<div class='task-card-header'><div class='task-name'>"
                        f"{html.escape(task['name'])} "
                        f"{status_dot('#999999', 12)}"
                        f"<span style='color:#999;'>— Interrupted</span></div></div>",
                        unsafe_allow_html=True,
                    )
                break

            # build outputs
            if key == "business_context":
                out_html = _business_context_html_from_text(st.session_state.lead_ctx_text)
            elif key == "category_weights":
                out_html = _format_weights_to_html()
            elif key == "prioritization_table":
                # The summary header HTML
                header_html = _format_prioritization_html_summary()
                # The main table HTML
                table_html = _format_prioritization_table_html(st.session_state["lead_prioritization_df"])
                # Combine them
                out_html = header_html + table_html # Combine them for caching
            else:
                out_html = "<div class='output-box'>(no output)</div>"

            # cache & render
            st.session_state.lead_cached[key] = out_html

            if header_ph is not None:
                header_ph.markdown(
                    f"<div class='task-card-header'><div class='task-name'>"
                    f"{html.escape(task['name'])} "
                    f"{status_dot('#2db24a', 12)}"
                    f"<span style='color:#2db24a;'>— Done</span></div></div>",
                    unsafe_allow_html=True,
                )

            if progress_ph is not None:
                progress_ph.empty()

            if results_ph is not None:
                with results_ph.container():
                    # Handle prioritization_table output rendering (header and table/download separately)
                    if key == "prioritization_table" and "lead_prioritization_df" in st.session_state:
                        
                        # 1. Render Summary Header
                        header_html = _format_prioritization_html_summary()
                        st.markdown(header_html, unsafe_allow_html=True)

                        # 2. Render Custom Table HTML
                        display_df = st.session_state["lead_prioritization_df"]
                        st.markdown(_format_prioritization_table_html(display_df), unsafe_allow_html=True)
                        
                        # 3. Render Download Button
                        csv = display_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "Download Prioritization CSV",
                            data=csv,
                            file_name=f"prioritization_run{run_id}.csv",
                            mime="text/csv",
                            key=f"lead_download_{key}_{run_id}",
                        )
                    else:
                        # Render other outputs (Business Context, Weights) directly from cached HTML
                        st.markdown(out_html, unsafe_allow_html=True)

            overall_progress_ph.progress(
                int(((idx + 1) / total) * 100),
                text="Overall Pipeline Progress",
            )

        overall_progress_ph.empty()
        if not st.session_state.lead_stop_requested:
            st.success("Lead scoring & prioritization run finished.")