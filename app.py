import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(page_title="Publishing Analytics", page_icon="📚", layout="wide")

# ==========================================
# Data Loading & Preparation (UPDATED FOR KAGGLE DATASET)
# ==========================================
@st.cache_data
def load_data():
    # 1. Load the real CSV, skipping bad lines
    df = pd.read_csv('books.csv', on_bad_lines='skip')
    
    # 2. Fix the Kaggle column name typos
    df.columns = df.columns.str.strip() 
    df = df.rename(columns={'# num_pages': 'num_pages'})
    
    # 3. Convert data types safely
    df['average_rating'] = pd.to_numeric(df['average_rating'], errors='coerce')
    df['num_pages'] = pd.to_numeric(df['num_pages'], errors='coerce')
    df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    
    # 4. Extract publication year specifically for the Line Chart
    df['publication_year'] = df['publication_date'].dt.year
    
    # 5. Drop rows with missing critical data to keep the dashboard charts clean
    df = df.dropna(subset=['title', 'authors', 'average_rating', 'num_pages', 'publication_year'])
    
    return df

df = load_data()

# ==========================================
# Sidebar & Widgets (Navigation & Filters)
# ==========================================
st.sidebar.title("📚 Dashboard Filters")
st.sidebar.write("Explore the dataset dynamically.")

# Widget 1: Multiselect for Language
# (We take the top 10 most common languages so the dropdown isn't cluttered)
top_languages = df['language_code'].value_counts().head(10).index.tolist()
selected_langs = st.sidebar.multiselect("Select Language:", options=top_languages, default=['eng', 'en-US', 'en-GB'])

# Widget 2: Slider for Average Rating
min_rating, max_rating = st.sidebar.slider(
    "Select Rating Range:", 
    min_value=0.0, max_value=5.0, value=(3.5, 5.0), step=0.1
)

# Widget 3: Selectbox for Sorting
sort_by = st.sidebar.selectbox("Sort Data By:", ["average_rating", "num_pages", "ratings_count"])

# Apply Filters
filtered_df = df[
    (df['language_code'].isin(selected_langs)) & 
    (df['average_rating'] >= min_rating) & 
    (df['average_rating'] <= max_rating)
].sort_values(by=sort_by, ascending=False)

# ==========================================
# Main Layout: Tabs
# ==========================================
st.title("Literature & Publishing Analytics Dashboard")
tab1, tab2, tab3 = st.tabs(["📊 Dataset Overview", "📈 Visualizations", "💡 Insights"])

# ------------------------------------------
# Tab 1: Dataset Overview & KPIs
# ------------------------------------------
with tab1:
    st.header("Key Performance Indicators (KPIs)")
    
    # Columns for KPIs
    col1, col2, col3 = st.columns(3)
    
    # Calculate and Display KPIs
    with col1:
        st.metric(label="Total Books (Records)", value=len(filtered_df))
    with col2:
        avg_rating = round(filtered_df['average_rating'].mean(), 2) if not filtered_df.empty else 0
        st.metric(label="Average Rating", value=f"{avg_rating} ⭐")
    with col3:
        total_pages = int(filtered_df['num_pages'].sum())
        st.metric(label="Total Pages (Sum)", value=f"{total_pages:,}")

    # Display grouped data
    st.subheader("Category-Wise Record Counts")
    category_count = filtered_df.groupby('language_code').size().reset_index(name='Book Count')
    st.dataframe(category_count, use_container_width=True)

    # Container for raw data
    with st.container():
        st.subheader("Filtered Dataset (Top 500 Rows)")
        # We limit to 500 rows here so the browser doesn't lag displaying massive tables
        st.dataframe(filtered_df[['title', 'authors', 'language_code', 'average_rating', 'num_pages', 'publication_date']].head(500), use_container_width=True)

# ------------------------------------------
# Tab 2: Visualizations (Bar, Line, Scatter)
# ------------------------------------------
with tab2:
    st.header("Exploratory Data Analysis")
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Bar Chart (Top 15 Books by Rating/Sort)
        st.subheader(f"Top 15 Books by {sort_by.replace('_', ' ').title()}")
        st.bar_chart(data=filtered_df.head(15), x="title", y=sort_by, color="#ffaa00")
        
        # Line Chart (Filter for modern books to make the trend readable)
        st.subheader("Ratings Trend Over Publication Year (1950 - Present)")
        trend_df = filtered_df[filtered_df['publication_year'] >= 1950].groupby('publication_year')['average_rating'].mean().reset_index()
        st.line_chart(data=trend_df, x="publication_year", y="average_rating", color="#0055ff")
        
        # Scatter Plot
        st.subheader("Relationship: Page Count vs. Average Rating")
        st.scatter_chart(data=filtered_df, x="num_pages", y="average_rating", color="#00aa00")

# ------------------------------------------
# Tab 3: Insights & Expanders
# ------------------------------------------
with tab3:
    st.header("Analytical Insights")
    
    with st.expander("View Top Rated Books in Current Filter"):
        top_books = filtered_df.nlargest(5, 'average_rating')[['title', 'authors', 'average_rating']]
        st.table(top_books)
        
    with st.expander("Data Interpretations & Observations"):
        st.write("""
        * **Page Count vs Rating:** Based on the scatter plot, books with higher page counts do not necessarily guarantee higher ratings. 
        * **Rating Distribution:** The highest-rated books tend to cluster around the 300-450 page mark.
        * **Language Domination:** English variants ('eng', 'en-US', 'en-GB') heavily dominate the dataset volume.
        """)
