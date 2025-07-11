import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Dark theme CSS
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: #E0E0E0;
    }
    .main-title {
        font-size: 30px;
        font-weight: bold;
        color: #81C784;
        padding-bottom: 5px;
        border-bottom: 2px solid #81C784;
        margin-bottom: 20px;
    }
    .metric-button {
        font-size: 16px !important;
        font-weight: 600 !important;
        border: 1px solid #81C784 !important;
        border-radius: 8px !important;
        background-color: #1E1E1E;
        color: #81C784;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        font-weight: 600;
        padding: 10px 16px;
        color: #81C784;
    }
    /* Reduced KPI metric text size */
    div[data-testid="metric-container"] {
        font-size: 13px !important;
    }
    div[data-testid="metric-container"] > label {
        font-size: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

def validate_format(df, required_columns, name=""):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"{name} file is missing columns: {', '.join(missing)}")
        return False
    return True

def render_ui(hr_df, access_df):
    st.markdown('<div class="main-title">\U0001F6E1️ ERP Role Access Intelligence</div>', unsafe_allow_html=True)

    hr_df.columns = hr_df.columns.str.strip()
    access_df.columns = access_df.columns.str.strip()
    access_df[['PS No', 'Name', 'Emp Job Code', 'Emp Job Description']] = access_df[
        ['PS No', 'Name', 'Emp Job Code', 'Emp Job Description']
    ].ffill()
    hr_df = hr_df.loc[:, ~hr_df.columns.str.contains('^Unnamed')]

    required_hr_cols = ["PS No", "Name", "Emp Job Code", "Emp Job Description", "Cluster", "SPG", "BU"]
    required_access_cols = ["PS No", "Name", "Emp Job Code", "Emp Job Description",
                            "Violation Job Code", "Violated Job Description"]

    if not (validate_format(hr_df, required_hr_cols, "HR Master Sheet") and
            validate_format(access_df, required_access_cols, "Access Data Sheet")):
        st.stop()

    hr_df["PS No"] = hr_df["PS No"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    access_df["PS No"] = access_df["PS No"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    access_df = access_df[access_df["Violation Job Code"] != access_df["Emp Job Code"]]

    hr_unique = hr_df.drop_duplicates(subset=["PS No"])
    access_df = pd.merge(
        access_df,
        hr_unique[["PS No", "Cluster", "SPG", "BU"]],
        on="PS No",
        how="left"
    )

    with st.sidebar:
        st.markdown("## \U0001F33B Filter Options")
        spg = st.multiselect("SPG", sorted(hr_df["SPG"].dropna().unique()))
        bu = st.multiselect("BU", sorted(hr_df["BU"].dropna().unique()))
        cluster = st.multiselect("Cluster", sorted(hr_df["Cluster"].dropna().unique()))

    filtered_access_df = access_df.copy()
    if spg:
        filtered_access_df = filtered_access_df[filtered_access_df["SPG"].isin(spg)]
    if bu:
        filtered_access_df = filtered_access_df[filtered_access_df["BU"].isin(bu)]
    if cluster:
        filtered_access_df = filtered_access_df[filtered_access_df["Cluster"].isin(cluster)]

    summary_columns = [
        "PS No", "Name", "Emp Job Code", "Emp Job Description",
        "SPG", "BU", "Cluster",
        "Violation Job Code", "Violated Job Description"
    ]

    summary_df = filtered_access_df.copy()
    if all(col in summary_df.columns for col in summary_columns):
        summary_df = summary_df[summary_columns].dropna(subset=["PS No"])
        employees_with_violations = len(summary_df)
    else:
        employees_with_violations = 0

    total_employees = hr_df["PS No"].nunique()

        # === KPI DASHBOARD ===
        # === KPI DASHBOARD ===
        # === KPI DASHBOARD ===
    st.markdown("### 📊 Key Metrics")

    # Custom styles for KPI
    st.markdown("""
        <style>
        .kpi-box {
            background-color: #1E1E1E;
            border: 1px solid #81C784;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .kpi-label {
            font-size: 15px;
            color: #A5D6A7;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 26px;
            font-weight: bold;
            color: #81C784;
            overflow-wrap: break-word;
        }
        </style>
    """, unsafe_allow_html=True)

    def render_kpi(label, value):
        return f"""
        <div class="kpi-box">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """

    # Prepare KPI values
    total_employees_val = total_employees
    employees_with_violations_val = summary_df['PS No'].nunique()
    total_violations_val = len(summary_df)
    if not summary_df.empty:
        most_violated_role = summary_df["Violated Job Description"].value_counts().idxmax()
        violation_count = summary_df["Violated Job Description"].value_counts().max()
        most_violated_val = f"{most_violated_role} ({violation_count})"
    else:
        most_violated_val = "N/A"

    # Render in 4 columns with spacing
    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        st.markdown(render_kpi("Total Employees", total_employees_val), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi("Employees with Violations", employees_with_violations_val), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi("Total Violations", total_violations_val), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi("Most Violated Role", most_violated_val), unsafe_allow_html=True)

        # Move buttons one line below KPIs
    with st.container():
        st.markdown("""<div style='margin-top: 20px;'></div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if "show_hr_view" not in st.session_state:
            st.session_state.show_hr_view = False
        if col1.button(f"\U0001F468‍\U0001F4BC Employees ({total_employees})"):
            st.session_state.show_hr_view = True
        if col2.button(f"\U0001F6A8 Violations ({employees_with_violations})"):
            st.session_state.show_hr_view = False


    tab1, tab2, tab3 = st.tabs([
        "\U0001F522 Sankey View",
        "\U0001F333 Treemap View",
        "\U0001F4CA Summary View"
    ])

    with tab1:
        st.subheader("\U0001F4A1 Violation Sankey View")
        sankey_df = filtered_access_df.dropna(subset=["PS No", "Emp Job Description", "Violated Job Description"])
        if not sankey_df.empty:
            unique_emp_access = sankey_df[["PS No", "Emp Job Description", "Violated Job Description"]].drop_duplicates()
            grouped_df = (
                unique_emp_access
                .groupby(["Emp Job Description", "Violated Job Description"])
                .agg(Employees=("PS No", "nunique"))
                .reset_index()
            )
            grouped_df["Emp Label"] = grouped_df["Emp Job Description"] + " (" + grouped_df["Employees"].astype(str) + ")"
            grouped_df["Violated Label"] = grouped_df["Violated Job Description"]

            all_labels = pd.unique(grouped_df["Emp Label"].tolist() + grouped_df["Violated Label"].tolist()).tolist()
            label_indices = {label: i for i, label in enumerate(all_labels)}

            sources = grouped_df["Emp Label"].map(label_indices)
            targets = grouped_df["Violated Label"].map(label_indices)
            values = grouped_df["Employees"]

            sankey_fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=all_labels,
                    color="#81C784"
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color="rgba(129,199,132,0.4)"
                )
            )])

            sankey_fig.update_layout(
                title_text="Violation Sankey View: Unique Employees per Access",
                font=dict(color="#E0E0E0", size=14),
                paper_bgcolor="#121212",
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(sankey_fig, use_container_width=True)
        else:
            st.info("No violations available to generate Sankey diagram.")

    with tab2:
        st.subheader("\U0001F333 Treemap of Violated Access")
        tree_df = filtered_access_df[["Emp Job Description", "Violated Job Description"]].dropna()
        if not tree_df.empty:
            fig = px.treemap(
                tree_df,
                path=["Emp Job Description", "Violated Job Description"],
                values=[1] * len(tree_df),
                color=[1] * len(tree_df),
                color_continuous_scale='Greens'
            )
            fig.update_layout(
                margin=dict(t=30, l=0, r=0, b=0),
                paper_bgcolor="#121212",
                font_color="#E0E0E0"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No access data available to display treemap.")

    with tab3:
        st.subheader("\U0001F4CA Summary View")
        if st.session_state.show_hr_view:
            filtered_hr_df = hr_df.copy()
            if spg:
                filtered_hr_df = filtered_hr_df[filtered_hr_df["SPG"].isin(spg)]
            if bu:
                filtered_hr_df = filtered_hr_df[filtered_hr_df["BU"].isin(bu)]
            if cluster:
                filtered_hr_df = filtered_hr_df[filtered_hr_df["Cluster"].isin(cluster)]
            st.dataframe(filtered_hr_df, use_container_width=True)
        else:
            if all(col in filtered_access_df.columns for col in summary_columns):
                summary_df = filtered_access_df[summary_columns].fillna("")
                display_df = summary_df.copy()
                display_df["row_num"] = display_df.groupby("PS No").cumcount()
                for col in ["PS No", "Name", "Emp Job Code", "Emp Job Description", "SPG", "BU", "Cluster"]:
                    display_df.loc[display_df["row_num"] > 0, col] = ""
                display_df.drop(columns="row_num", inplace=True)
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("Some required columns are missing in the violations data.")
