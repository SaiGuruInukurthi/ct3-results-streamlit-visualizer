"""
TCD Technical Scorecard - Streamlit App
Interactive dashboard for viewing and exporting student scores.
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="TCD Technical Scorecard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 TCD Technical Scorecard")
st.markdown("**GITAM - 20 Dec 2025 to 6 Jan 2026**")
st.markdown("---")

# File paths
APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = APP_DIR / "data.json"


@st.cache_data
def load_data_from_json():
    """Load data from pre-extracted JSON file."""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
        df = pd.DataFrame(records)
        df = df[['Rank', 'Name', 'RollNo', 'Campus', 'OverallPseudocode', 'OverallCoding', 'OverallDailyTest', 'Total']]
        return df
    except Exception as e:
        return pd.DataFrame()


@st.cache_data
def load_data_from_html(file_content: str):
    """Load data from uploaded HTML file content."""
    from parser import parse_html_file_content
    try:
        records = parse_html_file_content(file_content)
        df = pd.DataFrame(records)
        df = df[['Rank', 'Name', 'RollNo', 'Campus', 'OverallPseudocode', 'OverallCoding', 'OverallDailyTest', 'Total']]
        return df
    except Exception as e:
        st.error(f"Error parsing HTML: {e}")
        return pd.DataFrame()


# Try to load default data
df = load_data_from_json()

# If no default data, show upload option
if df.empty:
    st.info("📁 No default data found. Please upload your TCD Technical HTML report.")
    uploaded_file = st.file_uploader("Upload HTML Report", type=['html', 'htm'])
    
    if uploaded_file is not None:
        content = uploaded_file.read().decode('utf-8')
        df = load_data_from_html(content)
    else:
        st.stop()

if df.empty:
    st.warning("No data loaded. Please check the file format.")
    st.stop()

# Sidebar - Filters and Options
st.sidebar.header("🔧 Options")

# Campus filter
st.sidebar.subheader("🏫 Campus Filter")
campuses = ['All Campuses'] + sorted(df['Campus'].unique().tolist())
selected_campus = st.sidebar.selectbox("Select Campus", campuses)

# Search
search_term = st.sidebar.text_input("🔍 Search by Name or Roll No", "")

# Sorting options
st.sidebar.subheader("📈 Sorting")
sort_column = st.sidebar.selectbox(
    "Sort by",
    options=['Rank', 'Name', 'RollNo', 'OverallPseudocode', 'OverallCoding', 'OverallDailyTest', 'Total'],
    index=0
)
sort_order = st.sidebar.radio("Order", ["Ascending", "Descending"], index=0 if sort_column == 'Rank' else 1)

# Score filters
st.sidebar.subheader("📊 Score Filters")
min_total = st.sidebar.slider(
    "Minimum Total Score",
    min_value=0.0,
    max_value=float(df['Total'].max()) if not df.empty else 300.0,
    value=0.0,
    step=1.0
)

# Apply filters
filtered_df = df.copy()

# Campus filter
if selected_campus != 'All Campuses':
    filtered_df = filtered_df[filtered_df['Campus'] == selected_campus]
    # Recalculate ranks for the selected campus
    filtered_df = filtered_df.sort_values('Total', ascending=False).reset_index(drop=True)
    filtered_df['Rank'] = filtered_df.groupby('Total', sort=False).ngroup(ascending=False) + 1
    # Handle ties properly with min rank method
    rank_map = {}
    current_rank = 1
    for i, (idx, row) in enumerate(filtered_df.iterrows()):
        total = row['Total']
        if total not in rank_map:
            rank_map[total] = current_rank
            current_rank = i + 2
        filtered_df.at[idx, 'Rank'] = rank_map[total]

# Search filter
if search_term:
    search_term_lower = search_term.lower()
    filtered_df = filtered_df[
        filtered_df['Name'].str.lower().str.contains(search_term_lower, na=False) |
        filtered_df['RollNo'].astype(str).str.contains(search_term, na=False)
    ]

# Score filter
filtered_df = filtered_df[filtered_df['Total'] >= min_total]

# Apply sorting
ascending = sort_order == "Ascending"
filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending)

# Main content area
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📚 Total Students", len(df))
with col2:
    st.metric("🔍 Filtered Results", len(filtered_df))
with col3:
    st.metric("🏆 Highest Total", f"{df['Total'].max():.1f}")
with col4:
    st.metric("📈 Average Total", f"{df['Total'].mean():.1f}")

st.markdown("---")

# Campus breakdown
st.subheader("🏫 Campus-wise Student Count")
campus_counts = df['Campus'].value_counts().sort_index()

# Display campus counts in columns
num_campuses = len(campus_counts)
cols_per_row = 4
num_rows = (num_campuses + cols_per_row - 1) // cols_per_row

for row in range(num_rows):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        campus_idx = row * cols_per_row + col_idx
        if campus_idx < num_campuses:
            campus = campus_counts.index[campus_idx]
            count = campus_counts.iloc[campus_idx]
            with cols[col_idx]:
                st.metric(f"📍 {campus}", count)

st.markdown("---")

# Display the dataframe
st.subheader(f"📋 Student Scores ({len(filtered_df)} records)")

# Format the dataframe for display
display_df = filtered_df.copy()
display_df['OverallPseudocode'] = display_df['OverallPseudocode'].round(1)
display_df['OverallCoding'] = display_df['OverallCoding'].round(1)
display_df['OverallDailyTest'] = display_df['OverallDailyTest'].round(1)
display_df['Total'] = display_df['Total'].round(1)

# Rename columns for better display
display_df = display_df.rename(columns={
    'RollNo': 'Roll No',
    'OverallPseudocode': 'Pseudocode',
    'OverallCoding': 'Coding',
    'OverallDailyTest': 'Daily Test'
})

# Reorder columns to put Campus after Roll No
column_order = ['Rank', 'Name', 'Roll No', 'Campus', 'Pseudocode', 'Coding', 'Daily Test', 'Total']
display_df = display_df[column_order]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn("Rank", format="%d"),
        "Pseudocode": st.column_config.NumberColumn("Pseudocode", format="%.1f"),
        "Coding": st.column_config.NumberColumn("Coding", format="%.1f"),
        "Daily Test": st.column_config.NumberColumn("Daily Test", format="%.1f"),
        "Total": st.column_config.NumberColumn("Total", format="%.1f"),
    }
)

st.markdown("---")

# Export section
st.subheader("📥 Export Data")

col1, col2 = st.columns(2)

with col1:
    # Export filtered data
    csv_filtered = filtered_df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Filtered Data (CSV)",
        data=csv_filtered,
        file_name="tcd_scores_filtered.csv",
        mime="text/csv",
        help="Download the currently filtered and sorted data"
    )

with col2:
    # Export all data
    csv_all = df.to_csv(index=False)
    st.download_button(
        label="⬇️ Download All Data (CSV)",
        data=csv_all,
        file_name="tcd_scores_all.csv",
        mime="text/csv",
        help="Download all student data"
    )

# Statistics section
st.markdown("---")
st.subheader("📊 Score Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Pseudocode Scores**")
    st.write(f"- Mean: {df['OverallPseudocode'].mean():.1f}")
    st.write(f"- Median: {df['OverallPseudocode'].median():.1f}")
    st.write(f"- Max: {df['OverallPseudocode'].max():.1f}")
    st.write(f"- Min: {df['OverallPseudocode'].min():.1f}")

with col2:
    st.markdown("**Coding Scores**")
    st.write(f"- Mean: {df['OverallCoding'].mean():.1f}")
    st.write(f"- Median: {df['OverallCoding'].median():.1f}")
    st.write(f"- Max: {df['OverallCoding'].max():.1f}")
    st.write(f"- Min: {df['OverallCoding'].min():.1f}")

with col3:
    st.markdown("**Daily Test Scores**")
    st.write(f"- Mean: {df['OverallDailyTest'].mean():.1f}")
    st.write(f"- Median: {df['OverallDailyTest'].median():.1f}")
    st.write(f"- Max: {df['OverallDailyTest'].max():.1f}")
    st.write(f"- Min: {df['OverallDailyTest'].min():.1f}")

# Footer
st.markdown("---")
st.caption("TCD Technical Scorecard | Built with Streamlit & Pandas")
