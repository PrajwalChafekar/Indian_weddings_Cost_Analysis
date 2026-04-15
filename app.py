import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Indian Wedding Cost Analysis", layout="wide")

st.title("💍 Indian Wedding Cost Analysis Dashboard")

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Indian_Weddings_.csv")

    # Cleaning
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)

    df.columns = df.columns.str.replace('/', '')

    df = df.rename(columns={'Gifts(perpiece)': 'Gifts'})

    df['WeddingType'] = df['WeddingType'].replace('[////]', '', regex=True)
    df['Place'] = df['Place'].replace('[/xc2]', '', regex=True)
    df['DecorCategory'] = df['DecorCategory'].replace('/519830', '', regex=True)

    return df

df = load_data()

# ---------------------- SIDEBAR FILTERS ----------------------
st.sidebar.header("🔍 Filters")

color_theme = st.sidebar.selectbox(
    "Select Color Theme",
    ["viridis", "plasma", "inferno", "magma", "cividis"]
)

wedding_type = st.sidebar.multiselect(
    "Wedding Type",
    df['WeddingType'].unique(),
    default=df['WeddingType'].unique()
)

place = st.sidebar.multiselect(
    "Place",
    df['Place'].unique(),
    default=df['Place'].unique()
)

decor = st.sidebar.multiselect(
    "Decor Category",
    df['DecorCategory'].unique(),
    default=df['DecorCategory'].unique()
)

entertainment = st.sidebar.multiselect(
    "Entertainment Category",
    df['EntertainmentCategory'].unique(),
    default=df['EntertainmentCategory'].unique()
)

# ---------------------- FILTER DATA ----------------------
filtered_df = df[
    (df['WeddingType'].isin(wedding_type)) &
    (df['Place'].isin(place)) &
    (df['DecorCategory'].isin(decor)) &
    (df['EntertainmentCategory'].isin(entertainment))
]

# ---------------------- KPIs ----------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Weddings", len(filtered_df))
col2.metric("Unique Places", filtered_df['Place'].nunique())
col3.metric("Decor Types", filtered_df['DecorCategory'].nunique())
col4.metric("Entertainment Types", filtered_df['EntertainmentCategory'].nunique())

st.markdown("---")

# ---------------------- TABS ----------------------
tab1, tab2, tab3 = st.tabs(["📊 Distribution", "💰 Cost Analysis", "📌 Insights"])

# ---------------------- TAB 1 ----------------------
with tab1:
    st.subheader("Category Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.histogram(filtered_df, x="WeddingType", color="WeddingType",
                            color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.histogram(filtered_df, x="DecorCategory", color="DecorCategory",
                            color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        fig3 = px.histogram(filtered_df, x="Place", color="Place",
                            color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.histogram(filtered_df, x="EntertainmentCategory", color="EntertainmentCategory",
                            color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig4, use_container_width=True)

# ---------------------- TAB 2 ----------------------
with tab2:
    st.subheader("Cost Analysis")

    if 'TotalCost' in filtered_df.columns:

        fig5 = px.box(filtered_df, x="WeddingType", y="TotalCost",
                      color="WeddingType",
                      color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig5, use_container_width=True)

        fig6 = px.bar(filtered_df.groupby('Place')['TotalCost'].mean().reset_index(),
                      x='Place', y='TotalCost',
                      color='Place',
                      color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig6, use_container_width=True)

    else:
        st.warning("TotalCost column not found in dataset.")

# ---------------------- TAB 3 ----------------------
with tab3:
    st.subheader("Key Insights")

    st.markdown("""
    ### 📌 Observations:

    - Wedding Types and Places are fairly distributed across the dataset  
    - Luxury and Floral Decor dominate most weddings  
    - Celebrity entertainment is more frequent than professional performers  
    - Heritage, Palace, and Cruise weddings are high-cost categories  
    - Destination, Beach, and Farmhouse weddings are more budget-friendly  
    - Resorts and Hotels offer cost-effective options  

    ### 💡 Recommendations:

    - Use filters to compare budget vs luxury weddings  
    - Analyze decor impact on total cost  
    - Explore location-based cost variations  
    """)

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.caption("Interactive Dashboard by Streamlit 🚀")
