import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import os

# ==============================
# Configuration
# ==============================
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Page configuration
st.set_page_config(
    page_title="App Review Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# Data Loading Functions
# ==============================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_transformer_data(version):
    """Load data for a specific transformer version"""
    try:
        # Handle special case for C1 (no suffix)
        if version == "1":
            apps_file = PROCESSED_DIR / "apps_catalog.csv"
            reviews_file = PROCESSED_DIR / "apps_reviews.csv"
            kpis_file = PROCESSED_DIR / "app_kpis.csv"
            daily_file = PROCESSED_DIR / "daily_metrics.csv"
        else:
            apps_file = PROCESSED_DIR / f"apps_catalog_{version}.csv"
            reviews_file = PROCESSED_DIR / f"apps_reviews_{version}.csv"
            kpis_file = PROCESSED_DIR / f"app_kpis_{version}.csv"
            daily_file = PROCESSED_DIR / f"daily_metrics_{version}.csv"
        
        # Load apps catalog
        apps_df = pd.read_csv(apps_file) if apps_file.exists() else pd.DataFrame()
        
        # Load reviews
        reviews_df = pd.read_csv(reviews_file) if reviews_file.exists() else pd.DataFrame()
        
        # Load KPIs if available
        kpis_df = pd.read_csv(kpis_file) if kpis_file.exists() else pd.DataFrame()
        
        # Load daily metrics if available
        daily_df = pd.read_csv(daily_file) if daily_file.exists() else pd.DataFrame()
        
        # Load sentiment-specific data for C5
        contradictions_df = pd.DataFrame()
        summary_df = pd.DataFrame()
        if version == "5":
            contradictions_file = PROCESSED_DIR / "sentiment_contradictions_5.csv"
            if contradictions_file.exists():
                contradictions_df = pd.read_csv(contradictions_file)
            
            summary_file = PROCESSED_DIR / "sentiment_summary_5.csv"
            if summary_file.exists():
                summary_df = pd.read_csv(summary_file)
        
        return apps_df, reviews_df, kpis_df, daily_df, contradictions_df, summary_df
    
    except Exception as e:
        st.error(f"Error loading data for version {version}: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)
def get_available_versions():
    """Get list of available transformer versions"""
    versions = []
    
    # Check for C1 (no suffix)
    if (PROCESSED_DIR / "apps_reviews.csv").exists():
        versions.append("1")
    
    # Check for other versions (with suffix)
    for file in PROCESSED_DIR.glob("apps_reviews_*.csv"):
        version = file.stem.split("_")[-1]
        if version != "1":  # Don't duplicate C1
            versions.append(version)
    
    return sorted(versions, key=lambda x: int(x) if x.isdigit() else float('inf'))

# ==============================
# Helper Functions
# ==============================
def format_number(num):
    """Format large numbers with commas"""
    if pd.isna(num):
        return "N/A"
    return f"{num:,.0f}"

def safe_divide(numerator, denominator):
    """Safe division with zero handling"""
    if denominator == 0 or pd.isna(denominator):
        return 0
    return numerator / denominator

# ==============================
# Main App
# ==============================
def main():
    st.title("📊 App Review Analytics Dashboard")
    st.markdown("---")
    
    # Sidebar for version selection
    with st.sidebar:
        st.header("🔧 Configuration")
        
        available_versions = get_available_versions()
        if not available_versions:
            st.error("No transformer data found! Please run transformer scripts first.")
            return
        
        selected_version = st.selectbox(
            "Select Transformer Version",
            available_versions,
            index=len(available_versions)-1,  # Select latest by default
            format_func=lambda x: f"C{x}" if x.isdigit() else x
        )
        
        st.markdown("---")
        st.markdown("### Version Info:")
        
        # Version descriptions
        version_info = {
            "1": "🔹 **C1**: Original clean data",
            "2": "🔹 **C2**: Schema drift handling", 
            "3": "🔹 **C3**: Dirty data processing",
            "4": "🔹 **C4**: Updated apps catalog",
            "5": "🔹 **C5**: Sentiment analysis + contradictions"
        }
        
        if selected_version in version_info:
            st.markdown(version_info[selected_version])
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Load selected data
    apps_df, reviews_df, kpis_df, daily_df, contradictions_df, summary_df = load_transformer_data(selected_version)
    
    if reviews_df.empty:
        st.error(f"No data available for version C{selected_version}")
        return
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", "📱 Apps Analysis", "📝 Reviews Analysis", 
        "📅 Time Trends", "🔍 Sentiment Analysis" if selected_version == "5" else "📊 Metrics"
    ])
    
    # ==============================
    # Tab 1: Overview
    # ==============================
    with tab1:
        st.header("📈 Data Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Apps", format_number(len(apps_df)))
        
        with col2:
            st.metric("Total Reviews", format_number(len(reviews_df)))
        
        with col3:
            if not reviews_df.empty and 'score' in reviews_df.columns:
                avg_rating = reviews_df['score'].mean()
                st.metric("Avg Rating", f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A")
        
        with col4:
            if not reviews_df.empty and 'app_name' in reviews_df.columns:
                unique_apps = reviews_df['app_name'].nunique()
                st.metric("Apps with Reviews", format_number(unique_apps))
        
        st.markdown("---")
        
        # Data quality indicators
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📱 Apps Data Quality")
            if not apps_df.empty:
                # Check for missing data
                missing_data = apps_df.isnull().sum()
                if missing_data.sum() > 0:
                    st.warning("⚠️ Missing data detected:")
                    for col, count in missing_data[missing_data > 0].items():
                        st.write(f"- {col}: {count} missing values")
                else:
                    st.success("✅ No missing data in apps catalog")
                
                # Show apps preview
                st.write("**Apps Preview:**")
                st.dataframe(apps_df.head(), use_container_width=True)
        
        with col2:
            st.subheader("📝 Reviews Data Quality")
            if not reviews_df.empty:
                # Check for missing data
                missing_reviews = reviews_df.isnull().sum()
                if missing_reviews.sum() > 0:
                    st.warning("⚠️ Missing data detected:")
                    for col, count in missing_reviews[missing_reviews > 0].items():
                        st.write(f"- {col}: {count} missing values")
                else:
                    st.success("✅ No missing data in reviews")
                
                # Show reviews preview
                st.write("**Reviews Preview:**")
                st.dataframe(reviews_df.head(), use_container_width=True)
    
    # ==============================
    # Tab 2: Apps Analysis
    # ==============================
    with tab2:
        st.header("📱 Apps Analysis")
        
        if not kpis_df.empty:
            # Apps KPIs table
            st.subheader("📊 Apps Performance Metrics")
            
            # Select columns to display
            display_cols = ['title', 'num_reviews', 'avg_rating']
            if 'pct_low_rating' in kpis_df.columns:
                display_cols.append('pct_low_rating')
            if 'avg_sentiment_score' in kpis_df.columns:
                display_cols.extend(['avg_sentiment_score', 'contradiction_rate'])
            
            # Filter columns that exist
            available_cols = [col for col in display_cols if col in kpis_df.columns]
            
            # Format the display
            display_df = kpis_df[available_cols].copy()
            if 'pct_low_rating' in display_df.columns:
                display_df['pct_low_rating'] = display_df['pct_low_rating'].round(1)
            if 'contradiction_rate' in display_df.columns:
                display_df['contradiction_rate'] = display_df['contradiction_rate'].round(1)
            
            st.dataframe(display_df, width="stretch")
            
            # Apps rating chart
            if 'title' in kpis_df.columns and 'avg_rating' in kpis_df.columns:
                st.subheader("⭐ Apps by Average Rating")
                
                fig = px.bar(
                    kpis_df.sort_values('avg_rating', ascending=True),
                    x='avg_rating',
                    y='title',
                    orientation='h',
                    title="Average Rating by App",
                    labels={'avg_rating': 'Average Rating', 'title': 'App Name'},
                    color='avg_rating',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, width="stretch")
            
            # Apps review count chart
            if 'title' in kpis_df.columns and 'num_reviews' in kpis_df.columns:
                st.subheader("📊 Apps by Review Count")
                
                fig = px.bar(
                    kpis_df.sort_values('num_reviews', ascending=False),
                    x='num_reviews',
                    y='title',
                    orientation='h',
                    title="Number of Reviews by App",
                    labels={'num_reviews': 'Number of Reviews', 'title': 'App Name'},
                    color='num_reviews',
                    color_continuous_scale='blues'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total descending'})
                st.plotly_chart(fig, width="stretch")
        
        else:
            st.info("No KPI data available for this version")
    
    # ==============================
    # Tab 3: Reviews Analysis
    # ==============================
    with tab3:
        st.header("📝 Reviews Analysis")
        
        if not reviews_df.empty:
            # Rating distribution
            if 'score' in reviews_df.columns:
                st.subheader("⭐ Rating Distribution")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Histogram
                    fig = px.histogram(
                        reviews_df, 
                        x='score',
                        nbins=5,
                        title="Rating Distribution",
                        labels={'score': 'Rating', 'count': 'Number of Reviews'},
                        color_discrete_sequence=['#1f77b4']
                    )
                    fig.update_layout(bargap=0.1)
                    st.plotly_chart(fig, width="stretch")
                
                with col2:
                    # Rating stats
                    rating_stats = reviews_df['score'].describe()
                    st.write("**Rating Statistics:**")
                    st.write(f"- Mean: {rating_stats['mean']:.2f}")
                    st.write(f"- Median: {rating_stats['50%']:.2f}")
                    st.write(f"- Std Dev: {rating_stats['std']:.2f}")
                    st.write(f"- Min: {rating_stats['min']:.2f}")
                    st.write(f"- Max: {rating_stats['max']:.2f}")
            
            # Reviews by app
            if 'app_name' in reviews_df.columns:
                st.subheader("📱 Reviews by App")
                
                app_review_counts = reviews_df['app_name'].value_counts()
                
                fig = px.pie(
                    values=app_review_counts.values,
                    names=app_review_counts.index,
                    title="Reviews Distribution by App"
                )
                st.plotly_chart(fig, width="stretch")
            
            # Sample reviews
            st.subheader("📄 Sample Reviews")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                if 'app_name' in reviews_df.columns:
                    selected_app = st.selectbox(
                        "Filter by App",
                        ["All"] + list(reviews_df['app_name'].unique())
                    )
                else:
                    selected_app = "All"
            
            with col2:
                if 'score' in reviews_df.columns:
                    rating_filter = st.selectbox(
                        "Filter by Rating",
                        ["All", "5 Stars", "4 Stars", "3 Stars", "2 Stars", "1 Star"]
                    )
                else:
                    rating_filter = "All"
            
            # Apply filters
            filtered_reviews = reviews_df.copy()
            if selected_app != "All" and 'app_name' in reviews_df.columns:
                filtered_reviews = filtered_reviews[filtered_reviews['app_name'] == selected_app]
            
            if rating_filter != "All" and 'score' in reviews_df.columns:
                rating_map = {
                    "5 Stars": 5, "4 Stars": 4, "3 Stars": 3,
                    "2 Stars": 2, "1 Star": 1
                }
                filtered_reviews = filtered_reviews[filtered_reviews['score'] == rating_map[rating_filter]]
            
            # Display reviews
            display_cols = ['app_name', 'score', 'content'] if 'content' in reviews_df.columns else ['app_name', 'score']
            if 'userName' in reviews_df.columns:
                display_cols.insert(0, 'userName')
            
            available_display_cols = [col for col in display_cols if col in filtered_reviews.columns]
            st.dataframe(
                filtered_reviews[available_display_cols].head(10),
                use_container_width=True
            )
        
        else:
            st.info("No reviews data available for this version")
    
    # ==============================
    # Tab 4: Time Trends
    # ==============================
    with tab4:
        st.header("📅 Time Trends Analysis")
        
        if not daily_df.empty:
            # Convert date column
            if 'date' in daily_df.columns:
                daily_df['date'] = pd.to_datetime(daily_df['date'])
                
                # Daily metrics over time
                st.subheader("📈 Daily Metrics Trends")
                
                # Create subplot
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=("Daily Review Count", "Daily Average Rating"),
                    vertical_spacing=0.15
                )
                
                # Review count
                fig.add_trace(
                    go.Scatter(
                        x=daily_df['date'],
                        y=daily_df['daily_num_reviews'],
                        mode='lines+markers',
                        name='Daily Reviews',
                        line=dict(color='blue')
                    ),
                    row=1, col=1
                )
                
                # Average rating
                if 'daily_avg_rating' in daily_df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=daily_df['date'],
                            y=daily_df['daily_avg_rating'],
                            mode='lines+markers',
                            name='Avg Rating',
                            line=dict(color='green')
                        ),
                        row=2, col=1
                    )
                
                fig.update_layout(
                    title="Daily Trends Over Time",
                    height=600,
                    showlegend=True
                )
                fig.update_xaxes(title_text="Date", row=2, col=1)
                fig.update_yaxes(title_text="Number of Reviews", row=1, col=1)
                fig.update_yaxes(title_text="Average Rating", row=2, col=1)
                
                st.plotly_chart(fig, width="stretch")
                
                # Sentiment trends for C5
                if selected_version == "5" and 'daily_avg_sentiment' in daily_df.columns:
                    st.subheader("💭 Daily Sentiment Trends")
                    
                    fig = go.Figure()
                    
                    # Add sentiment line
                    fig.add_trace(go.Scatter(
                        x=daily_df['date'],
                        y=daily_df['daily_avg_sentiment'],
                        mode='lines+markers',
                        name='Avg Sentiment',
                        line=dict(color='purple')
                    ))
                    
                    # Add contradiction rate
                    if 'daily_contradiction_rate' in daily_df.columns:
                        fig.add_trace(go.Scatter(
                            x=daily_df['date'],
                            y=daily_df['daily_contradiction_rate'],
                            mode='lines+markers',
                            name='Contradiction Rate (%)',
                            yaxis='y2',
                            line=dict(color='red')
                        ))
                    
                    fig.update_layout(
                        title="Daily Sentiment and Contradiction Trends",
                        xaxis_title="Date",
                        yaxis_title="Sentiment Score",
                        yaxis2=dict(
                            title="Contradiction Rate (%)",
                            overlaying='y',
                            side='right'
                        ),
                        height=400
                    )
                    
                    st.plotly_chart(fig, width="stretch")
        
        else:
            st.info("No daily metrics data available for this version")
    
    # ==============================
    # Tab 5: Sentiment Analysis (C5 only)
    # ==============================
    if selected_version == "5":
        with tab5:
            st.header("🔍 Sentiment Analysis & Contradictions")
            
            if not summary_df.empty:
                # Summary metrics
                st.subheader("📊 Sentiment Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Contradiction Rate",
                        f"{summary_df['contradiction_rate_pct'].iloc[0]:.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Avg Sentiment Score",
                        f"{summary_df['avg_sentiment_score'].iloc[0]:.2f}"
                    )
                
                with col3:
                    st.metric(
                        "Positive Reviews",
                        f"{summary_df['positive_reviews_pct'].iloc[0]:.1f}%"
                    )
                
                with col4:
                    st.metric(
                        "Sentiment Gap",
                        f"{summary_df['avg_sentiment_gap'].iloc[0]:.2f}"
                    )
            
            if not contradictions_df.empty:
                # Contradictions details
                st.subheader("⚠️ Sentiment-Rating Contradictions")
                
                # Contradiction types
                if 'contradiction_type' in contradictions_df.columns:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        contradiction_types = contradictions_df['contradiction_type'].value_counts()
                        
                        fig = px.pie(
                            values=contradiction_types.values,
                            names=contradiction_types.index,
                            title="Types of Contradictions"
                        )
                        st.plotly_chart(fig, width="stretch")
                    
                    with col2:
                        # Contradictions by app
                        if 'app_name' in contradictions_df.columns:
                            app_contradictions = contradictions_df['app_name'].value_counts()
                            
                            fig = px.bar(
                                x=app_contradictions.values,
                                y=app_contradictions.index,
                                orientation='h',
                                title="Contradictions by App",
                                labels={'x': 'Count', 'y': 'App'}
                            )
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, width="stretch")
                
                # Detailed contradictions table
                st.subheader("📋 Detailed Contradictions")
                
                display_cols = [
                    'app_name', 'content', 'score', 'text_sentiment_label',
                    'contradiction_type', 'sentiment_rating_gap'
                ]
                available_cols = [col for col in display_cols if col in contradictions_df.columns]
                
                # Format content for display
                display_df = contradictions_df[available_cols].copy()
                if 'content' in display_df.columns:
                    display_df['content'] = display_df['content'].str.slice(0, 100) + '...'
                
                st.dataframe(display_df, width="stretch")
            
            if not kpis_df.empty and 'contradiction_rate' in kpis_df.columns:
                # Apps with contradictions
                st.subheader("📱 Apps by Contradiction Rate")
                
                fig = px.scatter(
                    kpis_df,
                    x='avg_rating',
                    y='contradiction_rate',
                    size='num_reviews',
                    color='title',
                    title="Rating vs Contradiction Rate",
                    labels={
                        'avg_rating': 'Average Rating',
                        'contradiction_rate': 'Contradiction Rate (%)',
                        'title': 'App',
                        'num_reviews': 'Number of Reviews'
                    },
                    hover_name='title'
                )
                st.plotly_chart(fig, width="stretch")
    else:
        with tab5:
            st.header("📊 General Metrics")
            st.info("Sentiment analysis is only available for version C5. Select C5 to view sentiment-specific metrics.")
            
            # Show general metrics if available
            if not kpis_df.empty:
                st.subheader("📈 Apps Performance")
                st.dataframe(kpis_df, width="stretch")

# ==============================
# Footer
# ==============================
def footer():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        📊 App Review Analytics Dashboard | Built with Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
    footer()
