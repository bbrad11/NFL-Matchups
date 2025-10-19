import streamlit as st
import pandas as pd
from nba_api.stats.endpoints import leaguegamefinder, playergamelog, teamgamelog
from nba_api.stats.static import players, teams

# Page config
st.set_page_config(
    page_title="NBA Matchup Analyzer", 
    page_icon="🏀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main h1 {
        color: #1D428A;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 0 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #C9082A;
        color: white;
    }
    
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0;'>🏀 NBA Matchup Analyzer</h1>
    <p style='text-align: center; color: #6B7280; font-size: 1.2rem; margin-top: 0;'>
        Find the best NBA matchups and player props
    </p>
""", unsafe_allow_html=True)

st.markdown("---")

# Sidebar controls
st.sidebar.header("⚙️ Settings")
season = st.sidebar.selectbox("Season", ["2024-25", "2023-24", "2022-23"], index=0)

# Position groups
positions = {
    'PG': ['PG', 'Point Guard'],
    'SG': ['SG', 'Shooting Guard'],
    'SF': ['SF', 'Small Forward'],
    'PF': ['PF', 'Power Forward'],
    'C': ['C', 'Center']
}

# Cache data loading
@st.cache_data
def load_nba_teams():
    """Load all NBA teams"""
    return teams.get_teams()

@st.cache_data
def load_nba_players():
    """Load all NBA players"""
    return players.get_active_players()

# Placeholder functions - you'll need to implement these with NBA API
def get_team_defense_stats():
    """Get defensive stats for each team"""
    # TODO: Implement using NBA API
    st.info("Connect to NBA API to load team defense data")
    return pd.DataFrame()

def get_player_stats():
    """Get player stats"""
    # TODO: Implement using NBA API
    st.info("Connect to NBA API to load player data")
    return pd.DataFrame()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🛡️ Worst Defenses", 
    "🔥 Tonight's Games", 
    "🏆 Top Performers",
    "📊 Consistency"
])

# ============================================================
# TAB 1: WORST DEFENSES
# ============================================================

with tab1:
    st.header("Which Teams Give Up The Most?")
    st.markdown("Find defensive weaknesses to exploit")
    
    stat_category = st.selectbox(
        "Stat Category",
        ["Points", "3-Pointers", "Rebounds", "Assists", "Steals", "Blocks"]
    )
    
    position = st.selectbox("Position", list(positions.keys()))
    
    st.info("📊 Defense rankings will appear here once NBA API is connected")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Worst Defenses")
        st.caption("These teams allow the most production")
        # Display worst defenses here
        
    with col2:
        st.subheader("🟢 Best Defenses")
        st.caption("These teams shut down opponents")
        # Display best defenses here

# ============================================================
# TAB 2: TONIGHT'S GAMES
# ============================================================

with tab2:
    st.header("🏀 Tonight's NBA Games")
    st.markdown("Find favorable matchups for your lineup")
    
    st.info("📅 Tonight's games and matchup analysis will appear here")
    
    # Sample game display
    with st.expander("LAL @ GSW - 10:00 PM ET"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**LAL Offense**")
            st.success("✅ LeBron James: Good matchup vs weak perimeter D")
            st.success("✅ Anthony Davis: Good matchup vs weak interior D")
        
        with col2:
            st.markdown("**GSW Offense**")
            st.success("✅ Stephen Curry: Good matchup vs weak 3PT D")

# ============================================================
# TAB 3: TOP PERFORMERS
# ============================================================

with tab3:
    st.header("Season Leaders")
    
    sort_option = st.radio(
        "Show leaders by:",
        ["Points", "Rebounds", "Assists", "Fantasy Points"],
        horizontal=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Guards")
        st.info("Guard leaders will appear here")
        
        st.subheader("💪 Forwards")
        st.info("Forward leaders will appear here")
    
    with col2:
        st.subheader("🏔️ Centers")
        st.info("Center leaders will appear here")

# ============================================================
# TAB 4: CONSISTENCY RATINGS
# ============================================================

with tab4:
    st.header("📊 Player Consistency Ratings")
    st.markdown("Find reliable players who perform night after night")
    
    consistency_position = st.selectbox(
        "Position", 
        list(positions.keys()), 
        key="consistency_pos"
    )
    
    st.info("Consistency ratings will appear here once data is loaded")
    
    # Metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Most Consistent", "Player Name", "95.2/100")
    with col2:
        st.metric("Highest Average", "Player Name", "28.5 PPG")
    with col3:
        st.metric("Highest Floor", "Player Name", "18.2 PPG")
    with col4:
        st.metric("Highest Ceiling", "Player Name", "45.8 PPG")
    
    with st.expander("ℹ️ How Consistency is Calculated"):
        st.markdown("""
        **Consistency Rating (0-100):**
        - Higher score = more reliable night-to-night performance
        - Based on variance in scoring/stats
        - Accounts for minutes played and game situation
        
        **Floor:** Lowest performance this season
        **Ceiling:** Best performance this season
        **Range:** Difference between ceiling and floor
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #6B7280;'>
        📊 Data: NBA Stats API | Updated daily during NBA season
    </div>
""", unsafe_allow_html=True)

# Setup instructions
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Setup Instructions")
st.sidebar.markdown("""
To complete this app, install:
```bash
pip install nba_api
```

Then implement:
1. Team defense stats
2. Player game logs
3. Live game data
4. Injury reports
5. Vegas lines integration
""")
