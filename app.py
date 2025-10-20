import streamlit as st

# Page config
st.set_page_config(
    page_title="Sports Matchup Analyzer",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Fixed for better readability
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Content container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    /* Title styling */
    .main h1 {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        text-align: center;
        background: linear-gradient(90deg, #1E3A8A 0%, #C9082A 50%, #FDB927 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        padding: 0;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #475569;
        font-size: 1.25rem;
        margin-top: 0.5rem;
        margin-bottom: 3rem;
    }
    
    /* Sport cards */
    .sport-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 3px solid transparent;
        margin-bottom: 2rem;
    }
    
    .sport-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
        border-color: #3B82F6;
    }
    
    .sport-icon {
        font-size: 5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sport-title {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        color: #1E293B;
    }
    
    .sport-description {
        color: #64748B;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    
    .feature-list {
        margin-top: 1.5rem;
        padding-left: 0;
        list-style: none;
    }
    
    .feature-item {
        padding: 0.5rem 0;
        color: #334155;
        font-size: 1rem;
        display: flex;
        align-items: center;
    }
    
    .feature-item:before {
        content: "✓";
        color: #10B981;
        font-weight: bold;
        font-size: 1.3rem;
        margin-right: 0.75rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    
    /* Sidebar title */
    .sidebar-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 1rem;
        padding: 1rem;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Selectbox styling */
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 2px solid #334155 !important;
        border-radius: 12px;
    }
    
    /* Getting started section */
    .getting-started {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        border-radius: 16px;
        margin-top: 2rem;
    }
    
    .getting-started h2 {
        color: #1E293B;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .getting-started p {
        color: #475569;
        font-size: 1.15rem;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #64748B;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 2px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("<div class='sidebar-title'>🏆 Sports Analyzer</div>", unsafe_allow_html=True)

sport = st.sidebar.selectbox(
    "Select Sport",
    ["Home", "🏈 NFL", "🏀 NBA"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem; color: #94A3B8;'>
    📊 Data updated daily<br>
    Built with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)

# Router logic
if sport == "Home":
    # HOME PAGE
    st.markdown("<h1>🏆 Sports Matchup Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Data-driven insights for smarter lineup decisions</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])

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
                <li class="feature-item">Defense positional weaknesses by position</li>
                <li class="feature-item">Week-by-week matchup analysis</li>
                <li class="feature-item">Player consistency ratings</li>
                <li class="feature-item">NextGen Stats integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # NBA Card
        st.markdown("""
        <div class="sport-card">
            <div class="sport-icon">🏀</div>
            <div class="sport-title">NBA Matchup Analyzer</div>
            <div class="sport-description">
                Analyze NBA matchups and find scoring opportunities
            </div>
            <ul class="feature-list">
                <li class="feature-item">Team defensive rankings by position</li>
                <li class="feature-item">Tonight's game analysis</li>
                <li class="feature-item">Player performance trends</li>
                <li class="feature-item">Pace and efficiency stats</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Getting Started Section
    st.markdown("""
    <div class='getting-started'>
        <h2>🚀 Getting Started</h2>
        <p>
            Select a sport from the dropdown in the sidebar to begin analyzing matchups 
            and making data-driven lineup decisions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class='footer'>
        <p><strong>Data Sources:</strong> nflverse (NFL) • NBA Stats API (NBA)</p>
        <p>Updated weekly during active seasons</p>
    </div>
    """, unsafe_allow_html=True)

elif sport == "🏈 NFL":
    # NFL APP
    try:
        import nfl_app
        nfl_app.run()
    except ImportError:
        st.error("""
        **NFL app not found!**
        
        Make sure you have a file called `nfl_app.py` in your repository with a `run()` function.
        """)
        st.code("""
# Create nfl_app.py with this structure:
import streamlit as st

def run():
    st.title("🏈 NFL Matchup Analyzer")
    # Your NFL code here
    pass
        """, language="python")
        
elif sport == "🏀 NBA":
    # NBA APP
    try:
        import nba_app
        nba_app.run()
    except ImportError:
        st.error("""
        **NBA app not found!**
        
        Make sure you have a file called `nba_app.py` in your repository with a `run()` function.
        """)
        st.code("""
# Create nba_app.py with this structure:
import streamlit as st

def run():
    st.title("🏀 NBA Matchup Analyzer")
    # Your NBA code here
    pass
        """, language="python")
