import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------- CONFIG ----------------------
st.set_page_config(
    page_title="Indian Wedding Dashboard",
    layout="wide",
    page_icon="💍"
)

# ---------------------- STYLE ----------------------
st.markdown("""
<style>
.big-font {
    font-size:18px !important;
}
.metric-card {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("💍 Indian Wedding Cost Analysis")

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Indian_Weddings_.csv")

    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)

    df.columns = df.columns.str.replace('/', '')
    df = df.rename(columns={'Gifts(perpiece)': 'Gifts'})

    df['WeddingType'] = df['WeddingType'].replace('[////]', '', regex=True)
    df['Place'] = df['Place'].replace('[/xc2]', '', regex=True)
    df['DecorCategory'] = df['DecorCategory'].replace('/519830', '', regex=True)

    return df

df = load_data()

# ---------------------- SIDEBAR ----------------------
st.sidebar.header("🔍 Filters")

# Theme
color_theme = st.sidebar.selectbox(
    "🎨 Select Color Theme",
    ["viridis", "plasma", "inferno", "magma", "cividis"]
)

# Filters
wedding_type = st.sidebar.multiselect("Wedding Type", df['WeddingType'].unique(), default=df['WeddingType'].unique())
place = st.sidebar.multiselect("Place", df['Place'].unique(), default=df['Place'].unique())
decor = st.sidebar.multiselect("Decor", df['DecorCategory'].unique(), default=df['DecorCategory'].unique())
ent = st.sidebar.multiselect("Entertainment", df['EntertainmentCategory'].unique(), default=df['EntertainmentCategory'].unique())

# Budget filter
if 'TotalCost' in df.columns:
    min_cost, max_cost = st.sidebar.slider(
        "💰 Budget Range",
        int(df['TotalCost'].min()),
        int(df['TotalCost'].max()),
        (int(df['TotalCost'].min()), int(df['TotalCost'].max()))
    )
else:
    min_cost, max_cost = None, None

# Top N
top_n = st.sidebar.slider("📊 Top N Categories", 3, 20, 10)

# ---------------------- FILTER ----------------------
filtered_df = df[
    (df['WeddingType'].isin(wedding_type)) &
    (df['Place'].isin(place)) &
    (df['DecorCategory'].isin(decor)) &
    (df['EntertainmentCategory'].isin(ent))
]

if 'TotalCost' in df.columns:
    filtered_df = filtered_df[
        (filtered_df['TotalCost'] >= min_cost) &
        (filtered_df['TotalCost'] <= max_cost)
    ]

# ---------------------- KPIs ----------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Weddings", len(filtered_df))
col2.metric("Avg Cost", f"₹ {int(filtered_df['TotalCost'].mean())}" if 'TotalCost' in filtered_df else "N/A")
col3.metric("Max Cost", f"₹ {int(filtered_df['TotalCost'].max())}" if 'TotalCost' in filtered_df else "N/A")
col4.metric("Min Cost", f"₹ {int(filtered_df['TotalCost'].min())}" if 'TotalCost' in filtered_df else "N/A")

st.markdown("---")

# ---------------------- TABS ----------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Distribution", "💰 Cost", "📈 Trends", "📥 Export"])

# ---------------------- TAB 1 ----------------------
with tab1:
    st.subheader("Category Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.histogram(filtered_df, x="WeddingType",
                            color="WeddingType",
                            color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig1, use_container_width=True)

        top_places = filtered_df['Place'].value_counts().nlargest(top_n).reset_index()
        fig2 = px.bar(top_places, x='index', y='Place',
                      color='index',
                      color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        fig3 = px.histogram(filtered_df, x="DecorCategory",
                            color="DecorCategory",
                            color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.histogram(filtered_df, x="EntertainmentCategory",
                            color="EntertainmentCategory",
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

        avg_cost_place = filtered_df.groupby('Place')['TotalCost'].mean().nlargest(top_n).reset_index()

        fig6 = px.bar(avg_cost_place, x='Place', y='TotalCost',
                      color='Place',
                      color_discrete_sequence=px.colors.sequential.__dict__[color_theme])
        st.plotly_chart(fig6, use_container_width=True)

# ---------------------- TAB 3 ----------------------
with tab3:
    st.subheader("Insights")

    st.markdown("### 📌 Auto Insights")

    if 'TotalCost' in filtered_df.columns:

        highest = filtered_df.groupby('WeddingType')['TotalCost'].mean().idxmax()
        lowest = filtered_df.groupby('WeddingType')['TotalCost'].mean().idxmin()

        st.write(f"🔴 Most Expensive Wedding Type: **{highest}**")
        st.write(f"🟢 Most Budget Friendly: **{lowest}**")

        decor_popular = filtered_df['DecorCategory'].mode()[0]
        st.write(f"🎨 Most Popular Decor: **{decor_popular}**")

        place_popular = filtered_df['Place'].mode()[0]
        st.write(f"📍 Most Common Place: **{place_popular}**")

    st.markdown("""
    ### 💡 Strategy Tips:
    - Choose Resorts/Hotels for budget weddings  
    - Avoid Palace/Heritage if budget constrained  
    - Floral decor increases cost significantly  
    - Entertainment drives luxury perception  
    """)

# ---------------------- TAB 4 ----------------------
with tab4:
    st.subheader("Download Filtered Data")

    csv = filtered_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="filtered_wedding_data.csv",
        mime='text/csv'
    )

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.caption("🚀 Built with Streamlit | Advanced Interactive Dashboard")
