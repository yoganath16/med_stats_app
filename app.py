import streamlit as st
import pandas as pd
from agents.data_profiling import profile_dataset
from agents.data_cleaning import clean_dataset
from copy import deepcopy
from scipy import stats
import numpy as np
from core.stats_engine import execute_test
from agents.reporting import generate_results_text
from core.visuals import boxplot_by_group, distribution_plot
from core.apa_tables import format_group_table, format_test_table
from agents.citations import get_citations
from core.report_export import generate_word, generate_pdf
from agents.research_context import get_research_context

# ---------------------------
# Streamlit state init
# ---------------------------

for key in ["test_plan", "confirmed_schema", "results", "report_text", "df_clean"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ---------------------------
# Page config
# ---------------------------

st.set_page_config(page_title="Medical Statistical Analyzer", layout="wide", page_icon="🏥")

# ---------------------------
# Custom CSS for Medical Theme
# ---------------------------

st.markdown("""
<style>
    /* Medical Theme Colors */
    :root {
        --medical-blue: #1e88e5;
        --medical-teal: #00897b;
        --medical-light-blue: #e3f2fd;
        --medical-light-teal: #e0f2f1;
        --medical-accent: #1565c0;
    }
    
    /* Main Title Styling */
    h1 {
        color: #1565c0;
        font-weight: 600;
        border-bottom: 3px solid #1e88e5;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Tab Styling with Background */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 500;
        color: #424242;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e3f2fd;
        border-color: #1e88e5;
        color: #1565c0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1e88e5 !important;
        color: #ffffff !important;
        border-color: #1565c0 !important;
        font-weight: 600;
    }
    
    /* Banner Styling */
    .medical-banner {
        background: linear-gradient(135deg, #e3f2fd 0%, #e0f2f1 100%);
        padding: 15px 20px;
        border-radius: 8px;
        border-left: 5px solid #1e88e5;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Section Headers */
    h3 {
        color: #1565c0;
        font-weight: 600;
        margin-top: 25px;
        padding-left: 10px;
        border-left: 4px solid #1e88e5;
    }
    
    /* Info Boxes */
    .stInfo {
        background-color: #e3f2fd;
        border-left: 4px solid #1e88e5;
    }
    
    /* Success Boxes */
    .stSuccess {
        background-color: #e0f2f1;
        border-left: 4px solid #00897b;
    }
    
    /* Warning Boxes */
    .stWarning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #1e88e5;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1565c0;
        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.3);
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 2px dashed #1e88e5;
        border-radius: 8px;
        padding: 20px;
        background-color: #fafafa;
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 6px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Header with Medical Theme
# ---------------------------

st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: #1565c0; font-size: 2.5em; margin-bottom: 10px;">
        🏥 Statistical Analysis Platform for Medical Professionals
    </h1>
    <p style="color: #616161; font-size: 1.1em; font-style: italic;">
        AI Powered Advanced Analytics for Clinical Research & Evidence-Based Medicine
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# Tabs
# ---------------------------

tab1, tab2 = st.tabs(["🔬 Statistical Analysis", "📚 Research Context"])

# ==========================================================
# TAB 1 — STATISTICAL ANALYSIS
# ==========================================================

with tab1:
    
    st.markdown("""
    <div class="medical-banner">
        <h4 style="margin: 0; color: #1565c0;">📥 Data Upload & Preparation</h4>
        <p style="margin: 5px 0 0 0; color: #616161;">Upload your clinical dataset to begin statistical analysis</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "📁 Choose CSV or Excel file",
        type=["csv", "xlsx"],
        help="Upload your clinical research dataset (CSV or Excel format)"
    )

    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        df.columns = df.columns.astype(str).str.strip().str.replace("\u00a0", " ")

        st.markdown("""
        <div class="medical-banner">
            <h4 style="margin: 0; color: #1565c0;">📋 Dataset Preview</h4>
            <p style="margin: 5px 0 0 0; color: #616161;">First 5 rows of your uploaded dataset</p>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(df.head(), width="stretch")

        # ---------------------------
        # Cleaning
        # ---------------------------

        df_clean, audit_log = clean_dataset(df)
        st.session_state.df_clean = df_clean

        st.markdown("""
        <div class="medical-banner">
            <h4 style="margin: 0; color: #1565c0;">⚕️ Data Quality Assessment</h4>
            <p style="margin: 5px 0 0 0; color: #616161;">Automated data cleaning and validation results</p>
        </div>
        """, unsafe_allow_html=True)
        st.info(" ".join(audit_log))
        st.dataframe(df_clean.head(), width="stretch")

        # ---------------------------
        # Profiling
        # ---------------------------

        st.markdown("""
        <div class="medical-banner">
            <h4 style="margin: 0; color: #1565c0;">🔬 Automated Data Profiling</h4>
            <p style="margin: 5px 0 0 0; color: #616161;">AI-powered analysis of variable characteristics and distributions</p>
        </div>
        """, unsafe_allow_html=True)
        data_profile = profile_dataset(df_clean)

        # ---------------------------
        # Confirm datatypes
        # ---------------------------

        st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #e0f2f1 100%); padding: 8px 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #1e88e5; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h4 style="margin: 0; color: #1565c0; font-size: 1em;">✅ Variable Type Confirmation</h4>
            <p style="margin: 3px 0 0 0; color: #616161; font-size: 0.9em;">Review and confirm the data types for each variable in your dataset</p>
        </div>
        """, unsafe_allow_html=True)

        type_options = ["continuous", "categorical", "ordinal", "datetime"]

        confirm_df = pd.DataFrame([
            {"Feature": v, "Suggested Type": d.type, "Confirmed Type": d.type}
            for v, d in data_profile.variables.items()
        ])

        edited_df = st.data_editor(
            confirm_df,
            column_config={
                "Confirmed Type": st.column_config.SelectboxColumn(
                    "Confirmed Type", options=type_options
                )
            },
            hide_index=True,
            width="stretch"
        )

        if st.button("🔒 Confirm Data Types"):
            st.session_state.confirmed_schema = edited_df.copy()

        if st.session_state.confirmed_schema is not None:

            # ---------------------------
            # Reprofiling
            # ---------------------------

            final_profile = deepcopy(data_profile)

            for _, row in st.session_state.confirmed_schema.iterrows():
                var = row["Feature"]
                typ = row["Confirmed Type"]
                final_profile.variables[var].type = typ

                if typ == "continuous":
                    s = df_clean[var].dropna()
                    if len(s) >= 3:
                        p = stats.shapiro(s)[1]
                        final_profile.variables[var].normality_p = float(p)
                        final_profile.variables[var].normal = bool(p > 0.05)
                        z = np.abs(stats.zscore(s))
                        final_profile.variables[var].outliers_present = bool((z > 3).any())

            # ---------------------------
            # Agent 2 – Test suggestion
            # ---------------------------

            st.markdown("""
            <div class="medical-banner">
                <h4 style="margin: 0; color: #1565c0;">📊 Hypothesis Variables Selection</h4>
                <p style="margin: 5px 0 0 0; color: #616161;">Select your dependent (outcome) and independent (predictor) variables</p>
            </div>
            """, unsafe_allow_html=True)

            continuous_vars = [v for v, d in final_profile.variables.items() if d.type == "continuous"]
            all_vars = list(final_profile.variables.keys())

            col1, col2 = st.columns(2)
            with col1:
                dv = st.selectbox("🎯 Outcome Variable (Dependent)", continuous_vars, help="Select the continuous outcome variable you want to analyze")
            with col2:
                iv = st.selectbox("📈 Predictor Variable (Independent)", all_vars, help="Select the grouping or predictor variable")

            if st.button("🧠 Ask Comix for Recommendation", use_container_width=True):

                from agents.reasoning import select_statistical_test

                st.session_state.results = None
                st.session_state.report_text = None

                group_count = df_clean[iv].nunique() if final_profile.variables[iv].type == "categorical" else None

                payload = {
                    "dependent_variable": {
                        "name": dv,
                        "type": final_profile.variables[dv].type,
                        "normal": final_profile.variables[dv].normal
                    },
                    "independent_variable": {
                        "name": iv,
                        "type": final_profile.variables[iv].type,
                        "groups": group_count
                    }
                }

                st.session_state.test_plan = select_statistical_test(payload)

            # ---------------------------
            # Suggested test explanation
            # ---------------------------

            if st.session_state.test_plan:

                tp = st.session_state.test_plan

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">📌 Recommended Statistical Approach</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">AI-suggested test based on your data characteristics</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 6px; margin: 10px 0;">
                    <p style="margin: 5px 0;"><strong>Recommended Test:</strong> <span style="color: #1565c0; font-size: 1.1em;">{tp['selected_test']}</span></p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                **Rationale:**  
                {tp['justification']}
                """)

                st.markdown("**Statistical Assumptions Considered:**")
                for a in tp["assumptions"]:
                    st.markdown(f"• {a}")

                st.divider()

                # ---------------------------
                # Agent 3 – Run test
                # ---------------------------

                if st.button("🧪 Execute Statistical Test", use_container_width=True, type="primary"):
                    st.session_state.results = execute_test(
                        df_clean,
                        st.session_state.test_plan
                    )

            # ---------------------------
            # Summary output
            # ---------------------------

            if st.session_state.results:

                r = st.session_state.results

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">📊 Statistical Test Results</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Summary of statistical analysis findings</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Test", r['test'])
                with col2:
                    st.metric("Statistic", f"{r['statistic']:.3f}")
                with col3:
                    st.metric("p-value", f"{r['p_value']:.3f}")
                with col4:
                    st.metric("Effect Size", r.get('effect_size', 'N/A'))

                if r["p_value"] < 0.05:
                    st.success("✅ **Statistically Significant Result** (p < 0.05) - Clinical significance should be evaluated")
                else:
                    st.info("ℹ️ **Not Statistically Significant** (p ≥ 0.05) - No significant difference detected")

                # ---------------------------
                # Agent 4 – Academic output
                # ---------------------------

                if st.button("📄 Generate Publication-Ready Results", use_container_width=True):
                    st.session_state.report_text = generate_results_text(
                        st.session_state.test_plan,
                        st.session_state.results
                    )

            # ---------------------------
            # Academic display
            # ---------------------------

            if st.session_state.report_text:

                rt = st.session_state.report_text

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">✍ Publication-Style Results</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Formatted results ready for academic publication</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**Results:**")
                st.write(rt["results_text"])
                st.markdown("**Interpretation:**")
                st.write(rt["interpretation"])
                st.markdown("**Limitations:**")
                st.write(rt["limitations"])

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">📑 APA-Style Tables</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Publication-ready tables following APA guidelines</p>
                </div>
                """, unsafe_allow_html=True)

                group_stats = st.session_state.results.get("group_statistics")

                if group_stats:

                    group_df = format_group_table(group_stats)
                    st.dataframe(group_df, width="stretch")

                else:
                    st.info("Group-wise descriptive statistics are not applicable for correlation-based analyses.")

                test_df = format_test_table(st.session_state.results)
                st.dataframe(test_df, width="stretch")

                # Figures once (safe reuse)
                fig1 = distribution_plot(df_clean, dv)
                fig2 = boxplot_by_group(df_clean, dv, iv)

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">📊 Data Visualizations</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Clinical data distributions and group comparisons</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display figures side by side
                col_fig1, col_fig2 = st.columns(2)
                with col_fig1:
                    st.pyplot(fig1, use_container_width=True)
                with col_fig2:
                    st.pyplot(fig2, use_container_width=True)

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">📚 Academic References</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Key citations for the statistical methods used</p>
                </div>
                """, unsafe_allow_html=True)

                citation_data = get_citations(
                    st.session_state.test_plan["selected_test"]
                )

                for c in citation_data["citations"]:
                    st.write(c)

                # ---------------------------
                # Export
                # ---------------------------

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">💾 Export Reports</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Download your complete analysis report</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("📄 Download Word Report", use_container_width=True):
                        path = generate_word(
                            rt,
                            fig1,
                            fig2,
                            st.session_state.results,
                            st.session_state.confirmed_schema,
                            audit_log,
                            st.session_state.test_plan
                        )
                        with open(path, "rb") as f:
                            st.download_button("⬇ Download Word Document", f, "clinical_analysis_report.docx", use_container_width=True)

                with col2:
                    if st.button("📑 Download PDF Report", use_container_width=True):
                        path = generate_pdf(
                            rt,
                            fig1,
                            fig2,
                            st.session_state.results,
                            st.session_state.confirmed_schema,
                            audit_log,
                            st.session_state.test_plan
                        )
                        with open(path, "rb") as f:
                            st.download_button("⬇ Download PDF Document", f, "clinical_analysis_report.pdf", use_container_width=True)

# ==========================================================
# TAB 2 — RESEARCH CONTEXT
# ==========================================================

with tab2:

    st.markdown("""
    <div class="medical-banner">
        <h4 style="margin: 0; color: #1565c0;">📚 Research Context & Literature Insights</h4>
        <p style="margin: 5px 0 0 0; color: #616161;">Explore relevant clinical literature and research context for your study</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.df_clean is None or st.session_state.test_plan is None:
        st.warning("⚠️ Please complete the statistical analysis in the Statistical Analysis tab first to explore research context.")
    else:

        st.markdown("""
        <div class="medical-banner">
            <h4 style="margin: 0; color: #1565c0;">🎯 Research Objective</h4>
            <p style="margin: 5px 0 0 0; color: #616161;">Describe your clinical research question or hypothesis</p>
        </div>
        """, unsafe_allow_html=True)

        objective = st.text_area(
            "Describe your research objective",
            placeholder="Example: Compare reaction time between low vs high nutritional risk ICU patients",
            help="Provide a clear description of your research question or clinical hypothesis"
        )

        if objective:

            if st.button("🔍 Ask Comex for Relevant Clinical Literature", use_container_width=True, type="primary"):

                with st.spinner("🔬 I'm searching the clinical research landscape and identifying relevant literature for you..."):
                    context = get_research_context(
                        objective,
                        st.session_state.test_plan
                    )

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">📖 Research Theme</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Overview of the research domain and clinical context</p>
                </div>
                """, unsafe_allow_html=True)
                st.write(context["research_theme"])

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">📄 Key Clinical Papers & Findings</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Relevant published research in your field</p>
                </div>
                """, unsafe_allow_html=True)

                for paper in context["key_papers"]:
                    # Banner with citation only
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #e0f2f1 100%); padding: 12px 20px; border-radius: 6px; margin: 15px 0 5px 0; border-left: 5px solid #1e88e5; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-weight: 600; color: #1565c0; font-size: 1.05em;">{paper['citation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Summary displayed below the banner
                    st.markdown(f"""
                    <div style="background-color: #fafafa; padding: 15px; border-radius: 6px; margin: 0 0 20px 0; border: 1px solid #e0e0e0;">
                        <p style="margin: 0 0 10px 0;"><strong style="color: #1565c0;">Main Finding:</strong> {paper["main_finding"]}</p>
                        <p style="margin: 0;"><strong style="color: #1565c0;">Relation to Your Study:</strong> {paper["relation_to_current_study"]}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">🧪 Common Statistical Methods in Literature</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Frequently used analytical approaches in similar studies</p>
                </div>
                """, unsafe_allow_html=True)
                for m in context["common_methods_used"]:
                    st.markdown(f"• {m}")

                st.markdown("""
                <div class="medical-banner">
                    <h4 style="margin: 0; color: #1565c0;">📊 Typical Results Reported in Literature</h4>
                    <p style="margin: 5px 0 0 0; color: #616161;">Common findings and patterns in published research</p>
                </div>
                """, unsafe_allow_html=True)
                st.write(context["typical_results_in_literature"])