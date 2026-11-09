import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(page_title="Publishing Analytics", page_icon="📚", layout="wide")

# ==========================================
# Data Loading & Preparation
# ==========================================
@st.cache_data
def load_data():
    # Fallback mock dataset based on the Goodreads format for immediate testing
    data = {
        'title': ['1984', 'Dune', 'The Great Gatsby', 'Fahrenheit 451', 'Moby Dick', 'Brave New World', 'The Hobbit', 'Catch-22', 'Neuromancer', 'Foundation'],
        'authors': ['George Orwell', 'Frank Herbert', 'F. Scott Fitzgerald', 'Ray Bradbury', 'Herman Melville', 'Aldous Huxley', 'J.R.R. Tolkien', 'Joseph Heller', 'William Gibson', 'Isaac Asimov'],
        'language_code': ['eng', 'eng', 'eng', 'eng', 'eng', 'eng', 'eng', 'eng', 'eng', 'eng'],
        'average_rating': [4.19, 4.23, 3.93, 3.99, 3.51, 3.99, 4.28, 3.98, 3.90, 4.16],
        'num_pages': [328, 412, 180, 194, 378, 268, 310, 453, 261, 244],
        'ratings_count': [3140442, 701235, 3778214, 1729000, 498300, 1500000, 2900000, 750000, 280000, 390000],
        'publication_year': [1949, 1965, 1925, 1953, 1851, 1932, 1937, 1961, 1984, 1951]
    }
    return pd.DataFrame(data)

df = load_data()

# ==========================================
# 3a. Sidebar & Widgets (Navigation & Filters)
# ==========================================
st.sidebar.title("📚 Dashboard Filters")
st.sidebar.write("Explore the dataset dynamically.")

# Widget 1: Multiselect for Language
languages = df['language_code'].unique()
selected_langs = st.sidebar.multiselect("Select Language:", options=languages, default=languages)

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
# Main Layout: 3d. Tabs
# ==========================================
st.title("Literature & Publishing Analytics Dashboard")
tab1, tab2, tab3 = st.tabs(["📊 Dataset Overview", "📈 Visualizations", "💡 Insights"])

# ------------------------------------------
# Tab 1: Dataset Overview & KPIs
# ------------------------------------------
with tab1:
    st.header("Key Performance Indicators (KPIs)")
    
    # 3b. Columns for KPIs
    col1, col2, col3 = st.columns(3)
    
    # 1a. Calculate and Display KPIs
    with col1:
        st.metric(label="Total Books (Records)", value=len(filtered_df))
    with col2:
        avg_rating = round(filtered_df['average_rating'].mean(), 2) if not filtered_df.empty else 0
        st.metric(label="Average Rating", value=f"{avg_rating} ⭐")
    with col3:
        total_pages = filtered_df['num_pages'].sum()
        st.metric(label="Total Pages (Sum)", value=f"{total_pages:,}")

    # Display grouped data
    st.subheader("Category-Wise Record Counts")
    category_count = filtered_df.groupby('language_code').size().reset_index(name='Book Count')
    st.dataframe(category_count, use_container_width=True)

    # 3c. Container for raw data
    with st.container():
        st.subheader("Filtered Dataset")
        st.dataframe(filtered_df, use_container_width=True)

# ------------------------------------------
# Tab 2: Visualizations (Bar, Line, Scatter)
# ------------------------------------------
with tab2:
    st.header("Exploratory Data Analysis")
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        # 2a. Bar Chart
        st.subheader("Distribution of Average Ratings")
        st.bar_chart(data=filtered_df, x="title", y="average_rating", color="#ffaa00")
        
        # 2b. Line Chart
        st.subheader("Ratings Trend Over Publication Year")
        trend_df = filtered_df.groupby('publication_year')['average_rating'].mean().reset_index()
        st.line_chart(data=trend_df, x="publication_year", y="average_rating", color="#0055ff")
        
        # 2c. Scatter Plot
        st.subheader("Relationship: Page Count vs. Average Rating")
        st.scatter_chart(data=filtered_df, x="num_pages", y="average_rating", color="#00aa00")

# ------------------------------------------
# Tab 3: Insights & Expanders
# ------------------------------------------
with tab3:
    st.header("Analytical Insights")
    
    # 3c. Expanders for details
    with st.expander("View Top Rated Books in Current Filter"):
        top_books = filtered_df.nlargest(3, 'average_rating')[['title', 'authors', 'average_rating']]
        st.table(top_books)
        
    with st.expander("Data Interpretations & Observations"):
        st.write("""
        * **Page Count vs Rating:** Based on the scatter plot, books with higher page counts do not necessarily guarantee higher ratings. The highest-rated books tend to cluster around the 300-450 page mark.
        * **Rating Distribution:** The bar chart indicates a competitive spread, with most classic literature comfortably sitting above the 3.9 average rating threshold.
        * **Trends over Time:** The line chart reveals how historical publication years correlate with modern reader ratings.
        """)