import streamlit as st

# Page config
st.set_page_config(
    page_title="Sports Matchup Analyzer",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main h1 {
        font-size: 4rem !important;
        font-weight: 900 !important;
        text-align: center;
        background: linear-gradient(90deg, #1E3A8A 0%, #C9082A 50%, #FDB927 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    .subtitle {
        text-align: center;
        color: #6B7280;
        font-size: 1.5rem;
        margin-bottom: 3rem;
    }
    
    .sport-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .sport-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
        border-color: #1E3A8A;
    }
    
    .sport-icon {
        font-size: 5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sport-title {
        font-size: 2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sport-description {
        color: #6B7280;
        text-align: center;
        font-size: 1.1rem;
    }
    
    .feature-list {
        margin-top: 1.5rem;
        padding-left: 0;
        list-style: none;
    }
    
    .feature-item {
        padding: 0.5rem 0;
        color: #374151;
        font-size: 1rem;
    }
    
    .feature-item:before {
        content: "✓ ";
        color: #10B981;
        font-weight: bold;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar sport selector
st.sidebar.title("🏆 Sports Analyzer")
sport = st.sidebar.selectbox(
    "Select Sport",
    ["Home", "🏈 NFL", "🏀 NBA"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Router logic
if sport == "Home":
    # Landing page
    st.markdown("<h1>🏆 Sports Matchup Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Data-driven insights for smarter lineup decisions</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # NFL Card
        st.markdown("""
        <div class="sport-card">
            <div class="sport-icon">🏈</div>
            <div class="sport-title">NFL Matchup Analyzer</div>
            <div class="sport-description">
                Find the best NFL matchups and identify defensive weaknesses
            </div>
            <ul class="feature-list">
                <li class="feature-item">Defense positional weaknesses</li>
                <li class="feature-item">Week-by-week matchup analysis</li>
                <li class="feature-item">Player consistency ratings</li>
                <li class="feature-item">NextGen Stats integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # NBA Card
        st.markdown("""
        <div class="sport-card">
            <div class="sport-icon">🏀</div>
            <div class="sport-title">NBA Matchup Analyzer</div>
            <div class="sport-description">
                Analyze NBA matchups and find scoring opportunities
            </div>
            <ul class="feature-list">
                <li class="feature-item">Team defensive rankings</li>
                <li class="feature-item">Tonight's game analysis</li>
                <li class="feature-item">Player performance trends</li>
                <li class="feature-item">Pace and efficiency stats</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h2>🚀 Getting Started</h2>
        <p style='font-size: 1.2rem; color: #6B7280;'>
            Select a sport from the dropdown above to begin your analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

elif sport == "🏈 NFL":
    # NFL App - Import from nfl_app.py module
    try:
        import nfl_app
    except ImportError:
        st.error("NFL app module not found. Make sure nfl_app.py exists in your repository.")
        
elif sport == "🏀 NBA":
    # NBA App - Import from nba_app.py module
    try:
        import nba_app
    except ImportError:
        st.error("NBA app module not found. Make sure nba_app.py exists in your repository.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #6B7280; font-size: 0.8rem;'>
    📊 Data updated daily<br>
    Built with Streamlit
</div>
""", unsafe_allow_html=True)
