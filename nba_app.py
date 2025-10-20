import streamlit as st
import pandas as pd
from datetime import datetime

def run():
    """Main NBA app function"""
    
    # Custom CSS
    st.markdown("""
    <style>
        .main h1 {
            color: #C9082A;
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
    st.sidebar.header("⚙️ NBA Settings")
    season = st.sidebar.selectbox("Season", ["2024-25", "2023-24", "2022-23"], index=0)
    
    # Position groups
    positions = {
        'PG': 'Point Guard',
        'SG': 'Shooting Guard',
        'SF': 'Small Forward',
        'PF': 'Power Forward',
        'C': 'Center'
    }
    
    # Info banner
    st.info("📊 **Coming Soon!** NBA data integration is currently being developed. Connect your NBA API credentials in the sidebar to get started.")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🛡️ Worst Defenses", 
        "🏀 Tonight's Games", 
        "🏆 Top Performers",
        "📊 Consistency"
    ])
    
    # TAB 1: WORST DEFENSES
    with tab1:
        st.header("Which Teams Give Up The Most?")
        st.markdown("Find defensive weaknesses to exploit")
        
        stat_category = st.selectbox(
            "Stat Category",
            ["Points", "3-Pointers", "Rebounds", "Assists", "Steals", "Blocks"]
        )
        
        position = st.selectbox("Position", list(positions.keys()), format_func=lambda x: f"{x} - {positions[x]}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔴 Worst Defenses")
            st.caption("These teams allow the most production")
            
            # Sample data
            sample_data = pd.DataFrame({
                'Team': ['LAL', 'GSW', 'BOS', 'MIA', 'PHX'],
                stat_category: [125.3, 122.8, 120.5, 119.2, 118.7]
            })
            st.dataframe(sample_data, use_container_width=True, hide_index=True)
            st.caption("*Sample data - Connect NBA API for live data*")
        
        with col2:
            st.subheader("🟢 Best Defenses")
            st.caption("These teams shut down opponents")
            
            sample_data_best = pd.DataFrame({
                'Team': ['MEM', 'CLE', 'NYK', 'DEN', 'MIL'],
                stat_category: [105.2, 106.5, 107.8, 108.9, 109.3]
            })
            st.dataframe(sample_data_best, use_container_width=True, hide_index=True)
            st.caption("*Sample data - Connect NBA API for live data*")
    
    # TAB 2: TONIGHT'S GAMES
    with tab2:
        st.header("🏀 Tonight's NBA Games")
        st.markdown("Find favorable matchups for your lineup")
        
        current_date = datetime.now().strftime("%B %d, %Y")
        st.subheader(f"📅 Games for {current_date}")
        
        # Sample games
        sample_games = [
            {"away": "LAL", "home": "GSW", "time": "10:00 PM ET"},
            {"away": "BOS", "home": "MIA", "time": "7:30 PM ET"},
            {"away": "PHX", "home": "DEN", "time": "9:00 PM ET"},
        ]
        
        for game in sample_games:
            with st.expander(f"{game['away']} @ {game['home']} - {game['time']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{game['away']} Offense**")
                    st.success("✅ PG: Good matchup vs weak perimeter D")
                    st.success("✅ C: Good matchup vs weak interior D")
                    st.caption("*Sample analysis - Connect NBA API for live data*")
                
                with col2:
                    st.markdown(f"**{game['home']} Offense**")
                    st.success("✅ SG: Good matchup vs weak 3PT D")
                    st.success("✅ PF: Good matchup vs weak rebounding D")
                    st.caption("*Sample analysis - Connect NBA API for live data*")
        
        st.info("Connect NBA API to see real-time matchup analysis")
    
    # TAB 3: TOP PERFORMERS
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
            sample_guards = pd.DataFrame({
                'Player': ['Luka Doncic', 'Damian Lillard', 'Trae Young', 'Ja Morant', 'Tyrese Maxey'],
                'Team': ['DAL', 'MIL', 'ATL', 'MEM', 'PHI'],
                sort_option: [32.5, 30.2, 29.8, 28.5, 27.9]
            })
            st.dataframe(sample_guards, use_container_width=True, hide_index=True)
            st.caption("*Sample data - Connect NBA API for live data*")
            
            st.subheader("💪 Forwards")
            sample_forwards = pd.DataFrame({
                'Player': ['Giannis', 'Kevin Durant', 'Jayson Tatum', 'LeBron James', 'Kawhi Leonard'],
                'Team': ['MIL', 'PHX', 'BOS', 'LAL', 'LAC'],
                sort_option: [31.2, 29.5, 28.7, 26.8, 25.3]
            })
            st.dataframe(sample_forwards, use_container_width=True, hide_index=True)
            st.caption("*Sample data - Connect NBA API for live data*")
        
        with col2:
            st.subheader("🏔️ Centers")
            sample_centers = pd.DataFrame({
                'Player': ['Joel Embiid', 'Nikola Jokic', 'Anthony Davis', 'Bam Adebayo', 'Domantas Sabonis'],
                'Team': ['PHI', 'DEN', 'LAL', 'MIA', 'SAC'],
                sort_option: [33.8, 32.1, 28.9, 22.5, 21.8]
            })
            st.dataframe(sample_centers, use_container_width=True, hide_index=True)
            st.caption("*Sample data - Connect NBA API for live data*")
    
    # TAB 4: CONSISTENCY
    with tab4:
        st.header("📊 Player Consistency Ratings")
        st.markdown("Find reliable players who perform night after night")
        
        consistency_position = st.selectbox(
            "Position", 
            list(positions.keys()),
            format_func=lambda x: f"{x} - {positions[x]}",
            key="consistency_pos"
        )
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Most Consistent", "Sample Player", "95.2/100")
        with col2:
            st.metric("Highest Average", "Sample Player", "28.5 PPG")
        with col3:
            st.metric("Highest Floor", "Sample Player", "18.2 PPG")
        with col4:
            st.metric("Highest Ceiling", "Sample Player", "45.8 PPG")
        
        st.caption("*Sample metrics - Connect NBA API for live data*")
        
        # Sample consistency data
        st.subheader(f"🎯 {consistency_position} Consistency Rankings")
        sample_consistency = pd.DataFrame({
            'Player': ['Player A', 'Player B', 'Player C', 'Player D', 'Player E'],
            'Team': ['LAL', 'GSW', 'BOS', 'MIA', 'PHX'],
            'Avg': [28.5, 26.8, 25.3, 24.7, 23.9],
            'Consistency': [92.5, 89.3, 87.8, 85.2, 83.6],
            'Floor': [18.2, 16.5, 15.8, 14.3, 13.9],
            'Ceiling': [42.5, 41.8, 39.2, 38.5, 37.8],
            'Games': [25, 28, 26, 30, 24]
        })
        st.dataframe(sample_consistency, use_container_width=True, hide_index=True)
        st.caption("*Sample data - Connect NBA API for live data*")
        
        with st.expander("ℹ️ How Consistency is Calculated"):
            st.markdown("""
            **Consistency Rating (0-100):**
            - Higher score = more reliable night-to-night performance
            - Based on variance in scoring/stats
            - Accounts for minutes played and game situation
            
            **Floor:** Lowest performance this season
            
            **Ceiling:** Best performance this season
            
            **Range:** Difference between ceiling and floor (lower = more consistent)
            
            **Why it matters:** Consistent players reduce risk in DFS lineups, while high-ceiling players offer upside potential.
            """)
    
    # Setup instructions sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔌 Connect NBA API")
    
    with st.sidebar.expander("Setup Instructions"):
        st.markdown("""
        **To enable live NBA data:**
        
        1. Install NBA API:
        ```bash
        pip install nba_api
        ```
        
        2. Add API integration to this file
        
        3. Available data sources:
        - Player game logs
        - Team statistics
        - Live game data
        - Injury reports
        - Vegas lines
        
        4. See documentation:
        [NBA API Docs](https://github.com/swar/nba_api)
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #6B7280;'>
            📊 Data: NBA Stats API | Updated daily during NBA season<br>
            <small>Currently showing sample data - Connect API for live statistics</small>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run()
