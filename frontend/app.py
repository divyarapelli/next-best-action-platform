"""Streamlit frontend for the Next Best Action platform."""

from datetime import datetime
import json
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import threading

API_URL = "http://localhost:8000"

st.set_page_config(layout="wide", page_title="Next Best Action Platform")

# Custom CSS
st.markdown("""
<style>
    /* Dark gradient header */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Cards with box shadow and hover effect */
    .recommendation-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        margin: 10px 0;
    }
    .recommendation-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Risk badge colors */
    .risk-high {
        background-color: #ef4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .risk-medium {
        background-color: #f97316;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .risk-low {
        background-color: #22c55e;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* Confidence bar colors */
    .confidence-high {
        background-color: #22c55e;
    }
    .confidence-medium {
        background-color: #f97316;
    }
    .confidence-low {
        background-color: #ef4444;
    }
    
    /* Clean font */
    body {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Memory badge */
    .memory-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
for key, value in {"results": None, "decided": set(), "interaction": "", "domain": "Customer Success", "email_drafts": {}, "compare_results": None, "auto_analyze": False}.items():
    st.session_state.setdefault(key, value)

# Ensure domain is always set (defensive)
if "domain" not in st.session_state:
    st.session_state.domain = "Customer Success"

# Sidebar
with st.sidebar:
    st.markdown("## 🧠 Next Best Action")
    st.markdown("*AI-powered decision assistant*")
    
    st.divider()
    
    # Dashboard section
    st.markdown("### 📊 Dashboard")
    try:
        response = requests.get(f"{API_URL}/history", timeout=3)
        response.raise_for_status()
        history = response.json()
        
        if history:
            # Calculate today's stats
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            today_actions = [h for h in history if h.get("timestamp", "").startswith(today)]
            
            st.metric("Analyses Today", len(today_actions))
            approved = sum(1 for h in history if h.get("decision") == "approved")
            rejected = sum(1 for h in history if h.get("decision") == "rejected")
            st.metric("Total Approved", approved)
            st.metric("Total Rejected", rejected)
        else:
            st.info("No data yet")
    except Exception as exc:
        st.warning("Backend unavailable - dashboard data not loaded")
    
    st.divider()
    
    # Settings section
    st.markdown("### ⚙️ Settings")
    domain = st.selectbox(
        "Business Domain",
        ["Customer Success", "Sales", "Support"],
        index=["Customer Success", "Sales", "Support"].index(st.session_state.get("domain", "Customer Success"))
    )
    st.session_state.domain = domain
    
    st.divider()
    
    # Demo Mode section
    st.markdown("### 🎬 Demo Mode")
    st.markdown("*Quick demo scenarios*")
    
    demo_scenarios = {
        "😰 Churn Risk": "Customer has not logged in for 30 days. Support ticket unresolved for 2 weeks. Renewal due in 5 days. Team size reduced by 50%.",
        "💰 Upsell Opportunity": "Customer usage is at 95% of plan limit. Team expanded from 10 to 25 users. Mentioned needing advanced reporting features. Last QBR went very well.",
        "⚠️ Competitor Threat": "Customer said Salesforce offered 40% discount. They have a board meeting next week to decide on tools. Current contract ends in 45 days. Main champion just left the company."
    }
    
    for scenario_name, scenario_text in demo_scenarios.items():
        if st.button(scenario_name, key=f"demo_{scenario_name}", use_container_width=True):
            st.session_state.interaction = scenario_text
            st.session_state.auto_analyze = True
            st.rerun()

    st.divider()

    # Export Report section
    if st.session_state.get("results"):
        st.markdown("### 📤 Export Report")
        
        res = st.session_state.results
        recommendations = res.get("recommendations", [])[:3]
        
        report = f"""
╔══════════════════════════════════════╗
   NEXT BEST ACTION REPORT
   Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}
   Domain: {st.session_state.get('domain', 'Customer Success')}
╚══════════════════════════════════════╝

CUSTOMER SITUATION:
{st.session_state.get('interaction', '')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RISK ASSESSMENT:
- Risk Level: {res.get('risk_level', 'N/A')}
- Health Score: {res.get('health_score', 0)}/100 ({res.get('health_label', 'N/A')})
- AI Model: {res.get('planner_mode', 'N/A')}
- RAG Knowledge Hits: {res.get('rag_hits', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RECOMMENDED ACTIONS:
"""
        
        for i, rec in enumerate(recommendations, 1):
            report += f"""
{i}. {rec.get('action_title', 'N/A')}
   Confidence: {rec.get('confidence', 0)}%
   Reason: {rec.get('reason', 'N/A')}
   Evidence: {rec.get('evidence', 'N/A')}
"""
        
        report += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Powered by Intelligent Next Best Action Platform
XLVentures.AI Hackathon 2026
"""
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"NBA_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

# Main area
st.markdown("# 🧠 Next Best Action Platform")
st.markdown(f"*Domain: {st.session_state.get('domain', 'Customer Success')}*")

# Input section
st.divider()
interaction = st.text_area(
    "Paste Customer Interaction",
    placeholder="Paste meeting notes, email, CRM update...",
    height=200,
    value=st.session_state.get("interaction", "")
)

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔍 Analyze", use_container_width=True, type="primary") and interaction.strip():
        with st.spinner("AI agents are analyzing..."):
            try:
                response = requests.post(
                    f"{API_URL}/analyze",
                    json={"interaction": interaction, "domain": st.session_state.get("domain", "Customer Success")},
                    timeout=120
                )
                response.raise_for_status()
                st.session_state.results = response.json()
                st.session_state.decided = set()
                st.session_state.interaction = interaction
                st.session_state.auto_analyze = False
            except Exception as exc:
                st.error(f"Backend error: {exc}")

with col2:
    if st.button("📋 Load Sample Scenario", use_container_width=True):
        st.session_state.interaction = "Customer has low product usage. Renewal due in 20 days. Mentioned evaluating Salesforce. Last meeting was 3 months ago."
        st.rerun()

# Auto-analyze if demo scenario was selected
if st.session_state.get("auto_analyze", False) and interaction.strip():
    with st.spinner("AI agents are analyzing..."):
        try:
            response = requests.post(
                f"{API_URL}/analyze",
                json={"interaction": interaction, "domain": st.session_state.get("domain", "Customer Success")},
                timeout=120
            )
            response.raise_for_status()
            st.session_state.results = response.json()
            st.session_state.decided = set()
            st.session_state.interaction = interaction
            st.session_state.auto_analyze = False
        except Exception as exc:
            st.error(f"Backend error: {exc}")

# Results section
res = st.session_state.get("results")
if res:
    st.divider()
    st.markdown("## 📊 Analysis Results")
    
    # Health Score Gauge
    health_score = res.get("health_score", 75)
    health_label = res.get("health_label", "Healthy")
    
    # Color based on health
    if health_score < 30:
        health_color = "#ef4444"  # red
        health_emoji = "🔴"
    elif health_score <= 60:
        health_color = "#f97316"  # orange
        health_emoji = "🟡"
    else:
        health_color = "#22c55e"  # green
        health_emoji = "🟢"
    
    # Calculate delta from industry average
    delta = health_score - 75
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(
            label="Customer Health Score",
            value=f"{health_score}",
            delta=f"{delta:+.0f} vs industry avg",
            delta_color="normal" if delta >= 0 else "inverse"
        )
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; border: 2px solid {health_color};">
            <h2 style="margin: 0; color: {health_color}; font-size: 48px;">{health_emoji} {health_label}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Risk badge
    risk = res.get("risk_level", "LOW")
    risk_class = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}.get(risk, "risk-low")
    st.markdown(f'<span class="{risk_class}">RISK: {risk}</span>', unsafe_allow_html=True)
    
    # 3-column layout for recommendations
    recommendations = res.get("recommendations", [])[:3]
    cols = st.columns(3)
    
    for i, rec in enumerate(recommendations):
        with cols[i]:
            confidence = float(rec.get("confidence", 50))
            
            # Confidence color
            if confidence > 80:
                conf_color = "#22c55e"
                conf_class = "confidence-high"
            elif confidence > 60:
                conf_color = "#f97316"
                conf_class = "confidence-medium"
            else:
                conf_color = "#ef4444"
                conf_class = "confidence-low"
            
            # Card styling
            st.markdown(f"""
            <div class="recommendation-card" style="border-top: 4px solid {conf_color};">
                <h3 style="margin-top: 0;">{rec.get('action_title', 'N/A')}</h3>
                <div style="text-align: center; margin: 15px 0;">
                    <div style="font-size: 48px; font-weight: bold; color: {conf_color};">{confidence}%</div>
                    <div style="color: #666;">Confidence</div>
                </div>
                <p><strong>Reason:</strong> {rec.get('reason', 'N/A')}</p>
                <p style="color: #888; font-style: italic;"><em>Evidence: {rec.get('evidence', 'N/A')}</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Memory badge
            if rec.get("memory_influenced"):
                st.markdown('<span class="memory-badge">🧠 Memory Influenced</span>', unsafe_allow_html=True)
            
            # Approve/Reject buttons
            action_id = f"{rec['action_title']}_{i}"
            if action_id not in st.session_state.get("decided", set()):
                c1, c2 = st.columns(2)
                payload = {
                    "action_title": rec["action_title"],
                    "situation": st.session_state.get("interaction", "")[:100],
                    "confidence": confidence,
                    "decision": "approved",
                    "domain": st.session_state.get("domain", "Customer Success")
                }
                with c1:
                    if st.button("✅ Approve", key=f"a_{action_id}", use_container_width=True):
                        requests.post(f"{API_URL}/feedback", json=payload, timeout=30)
                        decided_set = st.session_state.get("decided", set())
                        decided_set.add(action_id)
                        st.session_state.decided = decided_set
                        st.session_state[f"approved_{action_id}"] = True
                        st.rerun()
                with c2:
                    if st.button("❌ Reject", key=f"r_{action_id}", use_container_width=True):
                        payload["decision"] = "rejected"
                        requests.post(f"{API_URL}/feedback", json=payload, timeout=30)
                        decided_set = st.session_state.get("decided", set())
                        decided_set.add(action_id)
                        st.session_state.decided = decided_set
                        st.rerun()
            else:
                st.success("✓ Decision recorded")
                
                # Show email generation section for approved actions
                if st.session_state.get(f"approved_{action_id}", False):
                    st.markdown("---")
                    st.markdown("### 📧 Generate Email Draft")
                    
                    if action_id not in st.session_state.get("email_drafts", {}):
                        if st.button("Generate Email for this Action", key=f"gen_{action_id}", use_container_width=True):
                            with st.spinner("Generating email..."):
                                try:
                                    email_payload = {
                                        "action_title": rec["action_title"],
                                        "situation": st.session_state.get("interaction", ""),
                                        "customer_context": json.dumps(res.get("context", {}))
                                    }
                                    response = requests.post(f"{API_URL}/generate-email", json=email_payload, timeout=60)
                                    response.raise_for_status()
                                    email_data = response.json()
                                    st.session_state.setdefault("email_drafts", {})[action_id] = email_data
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"Email generation failed: {exc}")
                    else:
                        email_data = st.session_state.get("email_drafts", {}).get(action_id)
                        
                        # Show subject and body
                        st.markdown(f"**Subject:** {email_data.get('subject', 'N/A')}")
                        
                        email_text = st.text_area(
                            "Email Body",
                            value=email_data.get('body', ''),
                            height=150,
                            key=f"email_text_{action_id}"
                        )
                        
                        # Copy button
                        if st.button("📋 Copy Email", key=f"copy_{action_id}", use_container_width=True):
                            full_email = f"{email_data.get('subject', '')}\n\n{email_text}"
                            st.code(full_email, language=None)
                            st.success("Email ready to copy above!")
    
    # Action Priority Matrix
    if res and res.get("recommendations"):
        st.divider()
        st.markdown("### 📊 Action Priority Matrix")
        
        recommendations = res.get("recommendations", [])[:3]
        
        # Prepare data for scatter plot
        matrix_data = []
        for rec in recommendations:
            confidence = float(rec.get("confidence", 50))
            
            # X axis: Effort Required (high confidence = low effort)
            effort = 100 - confidence  # Invert: high confidence = low effort
            
            # Y axis: Expected Impact (use confidence directly)
            impact = confidence
            
            # Color based on impact
            if impact > 80:
                color = "green"
            elif impact > 60:
                color = "orange"
            else:
                color = "red"
            
            matrix_data.append({
                "action_title": rec.get("action_title", "Unknown"),
                "effort_required": effort,
                "expected_impact": impact,
                "confidence": confidence,
                "color": color
            })
        
        if matrix_data:
            df_matrix = pd.DataFrame(matrix_data)
            
            # Create scatter plot
            fig = px.scatter(
                df_matrix,
                x="effort_required",
                y="expected_impact",
                size="confidence",
                color="color",
                color_discrete_map={"green": "#22c55e", "orange": "#f97316", "red": "#ef4444"},
                text="action_title",
                size_max=50,
                labels={
                    "effort_required": "Effort Required (Low → High)",
                    "expected_impact": "Expected Impact (Low → High)",
                    "confidence": "Confidence"
                },
                title="Action Priority Matrix"
            )
            
            # Add quadrant lines
            fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
            fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
            
            # Add quadrant labels
            fig.add_annotation(x=25, y=75, text="Quick Wins", showarrow=False, font=dict(size=14, color="gray"))
            fig.add_annotation(x=75, y=75, text="Strategic", showarrow=False, font=dict(size=14, color="gray"))
            fig.add_annotation(x=25, y=25, text="Low Priority", showarrow=False, font=dict(size=14, color="gray"))
            fig.add_annotation(x=75, y=25, text="Avoid", showarrow=False, font=dict(size=14, color="gray"))
            
            # Update layout
            fig.update_traces(textposition="top center")
            fig.update_layout(
                xaxis=dict(range=[0, 100]),
                yaxis=dict(range=[0, 100]),
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption("Quadrants: Quick Wins (Low Effort, High Impact) | Strategic (High Effort, High Impact) | Low Priority (Low Effort, Low Impact) | Avoid (High Effort, Low Impact)")

# Bottom tabs section
st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["📋 History", "📈 Analytics", "🔍 Pipeline", "🔄 Compare Scenarios"])

with tab1:
    st.markdown("### Recent Actions History")
    try:
        response = requests.get(f"{API_URL}/history", timeout=10)
        response.raise_for_status()
        history = response.json()
        if history:
            df = pd.DataFrame(history)[["timestamp", "situation", "action", "confidence", "decision"]]
            # Color code decisions
            def color_decision(val):
                if val == "approved":
                    return "background-color: #d1fae5"
                elif val == "rejected":
                    return "background-color: #fee2e2"
                return ""
            styled_df = df.style.applymap(color_decision, subset=["decision"])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.info("No action history recorded yet.")
    except Exception as exc:
        st.error(f"Could not load history: {exc}")

with tab2:
    st.markdown("### Analytics")
    try:
        response = requests.get(f"{API_URL}/history", timeout=3)
        response.raise_for_status()
        history = response.json()
        if history:
            approved = sum(1 for h in history if h.get("decision") == "approved")
            rejected = sum(1 for h in history if h.get("decision") == "rejected")
            
            # Bar chart
            chart_data = pd.DataFrame({
                "Decision": ["Approved", "Rejected"],
                "Count": [approved, rejected]
            })
            st.bar_chart(chart_data.set_index("Decision"))
        else:
            st.info("No data for analytics yet.")
    except Exception as exc:
        st.warning("Backend unavailable - analytics data not loaded")
    
    st.divider()
    
    # Confidence Trend Chart
    st.markdown("### 📈 Confidence Trend Over Time")
    try:
        response = requests.get(f"{API_URL}/confidence-trend", timeout=3)
        response.raise_for_status()
        trend_data = response.json()
        if trend_data:
            # Convert to DataFrame for plotting
            trend_df = pd.DataFrame(trend_data)
            trend_df['timestamp'] = pd.to_datetime(trend_df['timestamp'])
            trend_df = trend_df.set_index('timestamp')
            
            # Plot line chart
            st.line_chart(trend_df['confidence'])
            
            st.caption("Higher confidence over time shows the AI is learning from your decisions")
        else:
            st.info("No approved actions yet to show confidence trend.")
    except Exception as exc:
        st.warning("Backend unavailable - confidence trend not loaded")

with tab3:
    st.markdown("### AI Pipeline Details")
    if res:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("AI Mode", res.get("planner_mode", "unknown"))
        with col2:
            st.metric("RAG Hits", res.get("rag_hits", 0))
        with col3:
            st.metric("Memory Hits", res.get("memory_hits", 0))
    else:
        st.info("Run an analysis to see pipeline details.")

with tab4:
    st.markdown("### 🔄 Compare Scenarios")
    st.markdown("Analyze two customer scenarios side by side to compare recommendations.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        scenario_a = st.text_area("Scenario A", placeholder="Enter first customer scenario...", height=150)
    with col_b:
        scenario_b = st.text_area("Scenario B", placeholder="Enter second customer scenario...", height=150)
    
    if st.button("Compare Both →", use_container_width=True, type="primary"):
        if scenario_a.strip() and scenario_b.strip():
            with st.spinner("Analyzing both scenarios..."):
                try:
                    # Function to analyze scenario
                    def analyze_scenario(scenario, result_key):
                        try:
                            response = requests.post(
                                f"{API_URL}/analyze",
                                json={"interaction": scenario, "domain": st.session_state.get("domain", "Customer Success")},
                                timeout=120
                            )
                            response.raise_for_status()
                            return result_key, response.json()
                        except Exception as exc:
                            return result_key, {"error": str(exc)}
                    
                    # Run both analyses in parallel using threads
                    results = {}
                    threads = []
                    
                    thread_a = threading.Thread(target=lambda: results.update([analyze_scenario(scenario_a, "scenario_a")]))
                    thread_b = threading.Thread(target=lambda: results.update([analyze_scenario(scenario_b, "scenario_b")]))
                    
                    threads.extend([thread_a, thread_b])
                    thread_a.start()
                    thread_b.start()
                    
                    for thread in threads:
                        thread.join()
                    
                    st.session_state.compare_results = results
                except Exception as exc:
                    st.error(f"Comparison failed: {exc}")
        else:
            st.warning("Please enter both scenarios to compare.")
    
    # Display comparison results
    if st.session_state.get("compare_results"):
        results = st.session_state.get("compare_results", {})
        
        st.divider()
        st.markdown("## Comparison Results")
        
        col_left, col_right = st.columns(2)
        
        # Scenario A results
        with col_left:
            st.markdown("### Scenario A")
            res_a = results.get("scenario_a", {})
            if "error" in res_a:
                st.error(f"Error: {res_a['error']}")
            else:
                # Health score
                health_a = res_a.get("health_score", 75)
                health_label_a = res_a.get("health_label", "Healthy")
                st.metric("Health Score", f"{health_a}", health_label_a)
                
                # Risk badge
                risk_a = res_a.get("risk_level", "LOW")
                st.markdown(f"**Risk Level:** {risk_a}")
                
                # Recommendations
                st.markdown("**Recommendations:**")
                for i, rec in enumerate(res_a.get("recommendations", [])[:3], 1):
                    st.markdown(f"{i}. **{rec.get('action_title')}** (Confidence: {rec.get('confidence')}%)")
                    st.caption(rec.get('reason', '')[:100] + "...")
        
        # Scenario B results
        with col_right:
            st.markdown("### Scenario B")
            res_b = results.get("scenario_b", {})
            if "error" in res_b:
                st.error(f"Error: {res_b['error']}")
            else:
                # Health score
                health_b = res_b.get("health_score", 75)
                health_label_b = res_b.get("health_label", "Healthy")
                st.metric("Health Score", f"{health_b}", health_label_b)
                
                # Risk badge
                risk_b = res_b.get("risk_level", "LOW")
                st.markdown(f"**Risk Level:** {risk_b}")
                
                # Recommendations
                st.markdown("**Recommendations:**")
                for i, rec in enumerate(res_b.get("recommendations", [])[:3], 1):
                    st.markdown(f"{i}. **{rec.get('action_title')}** (Confidence: {rec.get('confidence')}%)")
                    st.caption(rec.get('reason', '')[:100] + "...")
        
        # Key differences section
        st.divider()
        st.markdown("## 🔑 Key Differences")
        
        if "error" not in res_a and "error" not in res_b:
            recs_a = [r.get("action_title") for r in res_a.get("recommendations", [])]
            recs_b = [r.get("action_title") for r in res_b.get("recommendations", [])]
            
            # Find differences
            only_in_a = set(recs_a) - set(recs_b)
            only_in_b = set(recs_b) - set(recs_a)
            common = set(recs_a) & set(recs_b)
            
            col_diff1, col_diff2, col_diff3 = st.columns(3)
            
            with col_diff1:
                st.markdown("**Only in Scenario A:**")
                if only_in_a:
                    for action in only_in_a:
                        st.markdown(f"- {action}")
                else:
                    st.info("None")
            
            with col_diff2:
                st.markdown("**Only in Scenario B:**")
                if only_in_b:
                    for action in only_in_b:
                        st.markdown(f"- {action}")
                else:
                    st.info("None")
            
            with col_diff3:
                st.markdown("**Common Actions:**")
                if common:
                    for action in common:
                        st.markdown(f"- {action}")
                else:
                    st.info("None")
            
            # Health score comparison
            st.divider()
            health_diff = health_a - health_b
            if health_diff > 0:
                st.success(f"Scenario A is healthier by {health_diff} points")
            elif health_diff < 0:
                st.warning(f"Scenario B is healthier by {-health_diff} points")
            else:
                st.info("Both scenarios have the same health score")
